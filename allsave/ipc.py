"""Lightweight local IPC HTTP server for Ayeraa Save Downloader."""
from __future__ import annotations

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger("allsave.ipc")


class IPCServer:
    """Provides a local loopback server for cross-process communication."""

    def __init__(
        self,
        on_grab_url: Callable[[str], None],
        port: int = 48231,
        host: str = "127.0.0.1",
    ) -> None:
        self.on_grab_url = on_grab_url
        self.host = host
        self.requested_port = port
        self.server: ThreadingHTTPServer | None = None
        self.port: int = 0
        self._thread: threading.Thread | None = None

    def start(self) -> int:
        server_inst = self

        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                pass  # Suppress default console clutter

            def _send_cors_headers(self, content_type: str = "application/json") -> None:
                self.send_header("Content-Type", content_type)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

            def do_OPTIONS(self) -> None:
                self.send_response(204)
                self._send_cors_headers()
                self.end_headers()

            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path == "/ping":
                    self.send_response(200)
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(b'{"status":"ok","app":"Ayeraa Save Downloader"}')
                    return

                if parsed.path == "/grab":
                    params = parse_qs(parsed.query)
                    url_vals = params.get("url") or []
                    url = url_vals[0].strip() if url_vals else ""
                    if url:
                        server_inst.on_grab_url(url)
                    self.send_response(200)
                    self._send_cors_headers()
                    self.end_headers()
                    payload = json.dumps({"status": "ok", "url": url}).encode("utf-8")
                    self.wfile.write(payload)
                    return

                self.send_response(404)
                self.end_headers()

            def do_POST(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path == "/grab":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length) if length > 0 else b""
                    url = ""
                    try:
                        data = json.loads(body.decode("utf-8"))
                        url = str(data.get("url", "")).strip()
                    except Exception:
                        pass
                    if url:
                        server_inst.on_grab_url(url)
                    self.send_response(200)
                    self._send_cors_headers()
                    self.end_headers()
                    payload = json.dumps({"status": "ok", "url": url}).encode("utf-8")
                    self.wfile.write(payload)
                    return

                self.send_response(404)
                self.end_headers()

        # Try desired port first; fallback to ephemeral port if occupied
        try:
            self.server = ThreadingHTTPServer((self.host, self.requested_port), RequestHandler)
            self.port = self.requested_port
        except OSError:
            self.server = ThreadingHTTPServer((self.host, 0), RequestHandler)
            self.port = self.server.server_port

        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        return self.port

    def stop(self) -> None:
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
