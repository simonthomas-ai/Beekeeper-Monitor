"""Local, authenticated HTTP ingestion for real device event JSON.

Uses only Python standard library. Intended for LAN/reverse-proxy deployment;
never expose this plain-HTTP listener to the public internet.
"""
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from integrations.event_contracts import HiveEvent

MAX_BODY = 32768

def make_handler(token, sink):
    if not token or len(token) < 24:
        raise ValueError("Set a random ingestion token of at least 24 characters")
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/api/v1/events":
                self.send_error(404)
                return
            supplied = self.headers.get("Authorization", "")
            if not hmac.compare_digest(supplied, "Bearer " + token):
                self.send_error(401)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_BODY:
                    self.send_error(413)
                    return
                event = HiveEvent.from_json(self.rfile.read(length).decode("utf-8"))
                sink(event)
            except (ValueError, UnicodeError, json.JSONDecodeError):
                self.send_error(400)
                return
            except Exception:
                self.send_error(503)
                return
            response = b'{"accepted":true}'
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def do_GET(self):
            self.send_error(404)

    return Handler

def run():
    token = os.environ.get("VESPAGUARD_INGEST_TOKEN", "")
    def log_event(event):
        # Metadata only: never print camera/audio payloads or secret token.
        print(json.dumps({"kind": event.kind, "device_id": event.device_id,
                          "timestamp": event.timestamp}), flush=True)
    server = ThreadingHTTPServer(("127.0.0.1", 8765), make_handler(token, log_event))
    print("VespaGuard ingestion listening on 127.0.0.1:8765 (localhost only)", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    run()
