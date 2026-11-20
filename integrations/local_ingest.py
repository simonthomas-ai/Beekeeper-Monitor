"""Bounded, authenticated local HTTP ingestion for validated metadata events.

Default binding is loopback. For remote use, put this behind an authenticated
TLS VPN/reverse proxy; never expose the plain-HTTP listener to the public net.
"""
import hmac
import json
import os
import threading
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, urlsplit

from integrations.event_contracts import HiveEvent
from integrations.event_store import SQLiteEventStore

MAX_BODY = 32768
READ_TIMEOUT_SECONDS = 5
MAX_WORKERS = 16
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60


class BoundedThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded server with a hard cap on active request workers."""
    daemon_threads = True
    block_on_close = False
    request_queue_size = 32

    def __init__(self, *args, max_workers=MAX_WORKERS, **kwargs):
        if not 1 <= max_workers <= 128:
            raise ValueError("max_workers must be between 1 and 128")
        self._slots = threading.BoundedSemaphore(max_workers)
        super().__init__(*args, **kwargs)

    def process_request(self, request, client_address):
        if not self._slots.acquire(timeout=0.25):
            try:
                request.sendall(
                    b"HTTP/1.1 503 Service Unavailable\r\n"
                    b"Connection: close\r\nContent-Length: 0\r\n\r\n"
                )
            except OSError:
                pass
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self._slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()

    def get_request(self):
        request, address = super().get_request()
        request.settimeout(READ_TIMEOUT_SECONDS)
        return request, address


def make_handler(token, sink, rate_limit=RATE_LIMIT_REQUESTS, rate_window=RATE_LIMIT_WINDOW_SECONDS):
    if not token or len(token) < 24:
        raise ValueError("Set a random ingestion token of at least 24 characters")
    if not callable(sink) or rate_limit < 1 or rate_window < 1:
        raise ValueError("Invalid sink or rate-limit configuration")

    requests = defaultdict(deque)
    requests_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "BeeKeeperIngest"
        sys_version = ""

        def log_message(self, fmt, *args):
            # Avoid writing client-controlled strings, payloads or headers to logs.
            return

        def _json(self, status, body):
            raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Connection", "close")
            self.end_headers()
            try:
                self.wfile.write(raw)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            self.close_connection = True

        def _authorized(self):
            supplied = self.headers.get("Authorization", "")
            return hmac.compare_digest(supplied, "Bearer " + token)

        def _rate_allowed(self):
            now = time.monotonic()
            key = self.client_address[0]
            with requests_lock:
                q = requests[key]
                while q and now - q[0] > rate_window:
                    q.popleft()
                if len(q) >= rate_limit:
                    return False
                q.append(now)
                if len(requests) > 1024:
                    for old_key in list(requests)[:256]:
                        if old_key != key and not requests[old_key]:
                            requests.pop(old_key, None)
                return True

        def do_POST(self):
            if self.path != "/api/v1/events":
                self._json(404, {"error": "not_found"})
                return
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            if not self._rate_allowed():
                self._json(429, {"error": "rate_limited"})
                return
            if self.headers.get("Transfer-Encoding") is not None:
                self._json(400, {"error": "transfer_encoding_not_supported"})
                return
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) != 1 or not lengths[0].isdigit():
                self._json(400, {"error": "invalid_content_length"})
                return
            length = int(lengths[0])
            if not 0 < length <= MAX_BODY:
                self._json(413, {"error": "body_too_large_or_empty"})
                return
            if self.headers.get_content_type() != "application/json":
                self._json(415, {"error": "application_json_required"})
                return
            try:
                chunks = bytearray()
                remaining = length
                while remaining:
                    chunk = self.rfile.read(min(remaining, 8192))
                    if not chunk:
                        raise ValueError("incomplete_body")
                    chunks.extend(chunk)
                    remaining -= len(chunk)
                event = HiveEvent.from_json(chunks.decode("utf-8"))
                sink(event)
            except (ValueError, UnicodeError, json.JSONDecodeError):
                self._json(400, {"error": "invalid_event"})
                return
            except (TimeoutError, OSError):
                self.close_connection = True
                return
            except Exception:
                self._json(503, {"error": "storage_unavailable"})
                return
            self._json(202, {"accepted": True})

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path != "/api/v1/events":
                self._json(404, {"error": "not_found"})
                return
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            if not self._rate_allowed():
                self._json(429, {"error": "rate_limited"})
                return
            try:
                query = parse_qs(parsed.query, strict_parsing=False)
                if set(query) - {"limit"} or any(len(values) != 1 for values in query.values()):
                    raise ValueError("invalid query")
                limit = int(query.get("limit", ["100"])[0])
                events = sink.list_events(limit)
                self._json(200, {"events": events, "count": len(events)})
            except (ValueError, AttributeError):
                self._json(400, {"error": "invalid_query_or_read_unavailable"})
            except Exception:
                self._json(503, {"error": "storage_unavailable"})

        def do_PUT(self):
            self._json(405, {"error": "method_not_allowed"})

        def do_DELETE(self):
            parsed = urlsplit(self.path)
            prefix = "/api/v1/events/"
            event_id = parsed.path[len(prefix):] if parsed.path.startswith(prefix) else ""
            if not event_id or "/" in event_id or parsed.query:
                self._json(404, {"error": "not_found"})
                return
            if not self._authorized():
                self._json(401, {"error": "unauthorized"})
                return
            if not self._rate_allowed():
                self._json(429, {"error": "rate_limited"})
                return
            try:
                deleted = sink.delete(event_id)
                self._json(200 if deleted else 404, {"deleted": deleted})
            except (ValueError, AttributeError):
                self._json(400, {"error": "invalid_event_id"})
            except Exception:
                self._json(503, {"error": "storage_unavailable"})

    return Handler


def make_server(token, sink, host="127.0.0.1", port=8765, max_workers=MAX_WORKERS):
    return BoundedThreadingHTTPServer(
        (host, port), make_handler(token, sink), max_workers=max_workers
    )


def run():
    token = os.environ.get("VESPAGUARD_INGEST_TOKEN", "")
    db_path = os.environ.get(
        "VESPAGUARD_INGEST_DB",
        os.path.join(os.path.dirname(__file__), "data", "events.sqlite3"),
    )
    retention_days = int(os.environ.get("VESPAGUARD_RETENTION_DAYS", "90"))
    max_rows = int(os.environ.get("VESPAGUARD_MAX_EVENTS", "100000"))
    store = SQLiteEventStore(db_path, retention_days=retention_days, max_rows=max_rows)
    server = make_server(token, store)
    print("BeeKeeper ingestion listening on 127.0.0.1:8765 (localhost only)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run()
