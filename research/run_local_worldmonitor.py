"""Local World Monitor application server for authorized security assessment.

Serves the cloned repository (research/worldmonitor) on port 3000 adhering to
the repository's documented development configuration.
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
WM_DIR = ROOT_DIR / "research" / "worldmonitor"
PUBLIC_DIR = WM_DIR / "public"


class WorldMonitorLocalHandler(SimpleHTTPRequestHandler):
    """HTTP Request Handler serving local World Monitor web application and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WM_DIR), **kwargs)

    def do_OPTIONS(self):
        """Handle CORS preflight requests safely."""
        origin = self.headers.get("Origin", "")
        self.send_response(200)
        
        # Dev CORS policy according to server/cors.ts: allow localhost / 127.0.0.1
        if "localhost" in origin or "127.0.0.1" in origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        elif "worldmonitor.app" in origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-WorldMonitor-Key, X-Api-Key")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for static pages and local API endpoints."""
        url_path = self.path.split("?")[0]
        origin = self.headers.get("Origin", "")

        # Local API Endpoints
        if url_path == "/api/version":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._apply_cors_headers(origin)
            self.end_headers()
            self.wfile.write(json.dumps({"version": "2.10.0", "tag": "v2.10.0", "environment": "local"}).encode())
            return

        if url_path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._apply_cors_headers(origin)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "environment": "local", "checks": {"database": "unconfigured"}}).encode())
            return

        if url_path == "/api/product-catalog":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._apply_cors_headers(origin)
            self.end_headers()
            self.wfile.write(json.dumps({"catalog": "world-monitor-public", "status": "active"}).encode())
            return

        # Check public directory
        public_file = PUBLIC_DIR / url_path.lstrip("/")
        if public_file.is_file():
            self.send_response(200)
            if url_path.endswith(".txt") or url_path.endswith(".md"):
                self.send_header("Content-Type", "text/plain; charset=utf-8")
            elif url_path.endswith(".json"):
                self.send_header("Content-Type", "application/json")
            self._apply_cors_headers(origin)
            self.end_headers()
            self.wfile.write(public_file.read_bytes())
            return

        # Serve index.html for root or client routes
        if url_path in ("/", "/dashboard", "/welcome", "/index.html"):
            index_path = WM_DIR / "index.html"
            if index_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self._apply_cors_headers(origin)
                self.end_headers()
                self.wfile.write(index_path.read_bytes())
                return

        super().do_GET()

    def do_HEAD(self):
        """Handle HEAD requests."""
        self.do_GET()

    def _apply_cors_headers(self, origin: str):
        if "localhost" in origin or "127.0.0.1" in origin or "worldmonitor.app" in origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")

    def log_message(self, format, *args):
        """Suppress standard HTTP request logging noise."""
        pass


def run_server(port: int = 3000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, WorldMonitorLocalHandler)
    print(f"[*] World Monitor local test server listening on http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopping...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port)
