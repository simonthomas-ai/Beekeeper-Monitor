"""Bounded, authenticated local HTTP ingestion for validated metadata events.

Default binding is loopback. For remote use, put this behind an authenticated
TLS VPN/reverse proxy; never expose the plain-HTTP listener to the public net.
"""
import hmac
import json
import os
import re
import threading
import time
from collections import defaultdict, deque
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, unquote, urlsplit

from integrations.event_contracts import HiveEvent
from integrations.event_store import SQLiteEventStore
from pathlib import Path

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


def make_handler(token, sink, rate_limit=RATE_LIMIT_REQUESTS, rate_window=RATE_LIMIT_WINDOW_SECONDS, web_root=None):
    if not token or len(token) < 24:
        raise ValueError("Set a random ingestion token of at least 24 characters")
    if not callable(sink) or rate_limit < 1 or rate_window < 1:
        raise ValueError("Invalid sink or rate-limit configuration")

    requests = defaultdict(deque)
    requests_lock = threading.Lock()
    public_root = Path(web_root or Path(__file__).resolve().parents[1]).resolve()
    public_files = {"index.html", "app.js", "integrations-ui.js", "live-media.js",
                    "style.css", "manifest.webmanifest", "icon.svg", "sw.js"}
    public_dirs = {"review", "sources"}
    public_extensions = {".html", ".js", ".css", ".json", ".csv", ".svg",
                         ".png", ".jpg", ".jpeg", ".webp", ".avif", ".ico"}

    class Handler(SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "BeeKeeperIngest"
        sys_version = ""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(public_root), **kwargs)

        def translate_path(self, path):
            raw = unquote(urlsplit(path).path)
            if "\\\\" in raw or "\x00" in raw:
                return str(public_root / "__not_found__")
            parts = raw.split("/")
            if any(part in (".", "..") or part.startswith(".") for part in parts if part):
                return str(public_root / "__not_found__")
            parts = [part for part in parts if part]
            if not parts:
                return str(public_root / "index.html")
            if len(parts) == 1 and parts[0] in public_files:
                return str(public_root / parts[0])
            if parts[0] not in public_dirs:
                return str(public_root / "__not_found__")
            candidate = public_root.joinpath(*parts)
            try:
                resolved = candidate.resolve()
                allowed_base = (public_root / parts[0]).resolve()
                resolved.relative_to(allowed_base)
            except (OSError, ValueError):
                return str(public_root / "__not_found__")
            if resolved.suffix.lower() not in public_extensions or not resolved.is_file():
                return str(public_root / "__not_found__")
            return str(resolved)

        def list_directory(self, path):
            self.send_error(404)
            return None

        def end_headers(self):
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            request_path = urlsplit(getattr(self, "path", "")).path
            script_policy = "'self' 'unsafe-inline'" if request_path.startswith("/review/") else "'self'"
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; script-src " + script_policy + "; object-src 'none'; "
                             "base-uri 'self'; frame-ancestors 'none'; "
                             "img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; "
                             "connect-src 'self' https:; media-src 'self' blob:; "
                             "form-action 'self'")
            self.send_header("Permissions-Policy",
                             "camera=(self), microphone=(self), geolocation=(self)")
            super().end_headers()

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
                q = requests.get(key)
                if q is None:
                    if len(requests) >= 1024:
                        for old_key, old_queue in list(requests.items()):
                            while old_queue and now - old_queue[0] > rate_window:
                                old_queue.popleft()
                            if not old_queue:
                                requests.pop(old_key, None)
                    if len(requests) >= 1024:
                        return False
                    q = requests.setdefault(key, deque())
                while q and now - q[0] > rate_window:
                    q.popleft()
                if len(q) >= rate_limit:
                    return False
                q.append(now)
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
            if self.headers.get("Transfer-Encoding") is not None or self.headers.get("Content-Encoding") is not None:
                self._json(400, {"error": "unsupported_transfer_or_content_encoding"})
                return
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) != 1:
                self._json(400, {"error": "invalid_content_length"})
                return
            raw_length = lengths[0]
            if not raw_length.isascii() or not raw_length.isdigit():
                self._json(400, {"error": "invalid_content_length"})
                return
            # Reject absurd decimal headers before int() to avoid conversion exceptions.
            if len(raw_length) > len(str(MAX_BODY)):
                self._json(413, {"error": "body_too_large"})
                return
            length = int(raw_length)
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
            except TimeoutError:
                self._json(408, {"error": "request_body_timeout"})
                return
            except OSError:
                self.close_connection = True
                return
            except Exception:
                self._json(503, {"error": "storage_unavailable"})
                return
            self._json(202, {"accepted": True})

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path != "/api/v1/events":
                return super().do_GET()
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
            if not re.fullmatch(r"[a-f0-9]{64}", event_id) or parsed.query:
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


def retention_maintenance(store, stop_event, interval_seconds=3600):
    """Periodically purge expired metadata without logging event content."""
    if not 300 <= interval_seconds <= 86400:
        raise ValueError("retention interval must be between 300 and 86400 seconds")
    while not stop_event.wait(interval_seconds):
        try:
            removed = store.purge_expired()
            if removed:
                print(f"Retention maintenance removed {removed} expired event(s).", flush=True)
        except Exception:
            # Keep the service alive; never log event payloads or identifiers.
            print("Retention maintenance failed; inspect local service diagnostics.", flush=True)


def run():
    token = os.environ.get("VESPAGUARD_INGEST_TOKEN", "")
    db_path = os.environ.get(
        "VESPAGUARD_INGEST_DB",
        os.path.join(os.path.dirname(__file__), "data", "events.sqlite3"),
    )
    retention_days = int(os.environ.get("VESPAGUARD_RETENTION_DAYS", "90"))
    max_rows = int(os.environ.get("VESPAGUARD_MAX_EVENTS", "100000"))
    retention_interval = int(os.environ.get("VESPAGUARD_RETENTION_INTERVAL_SECONDS", "3600"))
    if not 300 <= retention_interval <= 86400:
        raise ValueError("VESPAGUARD_RETENTION_INTERVAL_SECONDS must be between 300 and 86400")
    store = SQLiteEventStore(db_path, retention_days=retention_days, max_rows=max_rows)
    removed = store.purge_expired()
    if removed:
        print(f"Startup retention removed {removed} expired event(s).", flush=True)
    server = make_server(token, store)
    stop_event = threading.Event()
    maintenance = threading.Thread(
        target=retention_maintenance,
        args=(store, stop_event, retention_interval),
        name="beekeeper-retention",
        daemon=True,
    )
    maintenance.start()
    print("BeeKeeper local PWA and ingestion API: http://127.0.0.1:8765/ (localhost only)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        maintenance.join(timeout=5)
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run()
