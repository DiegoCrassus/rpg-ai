#!/usr/bin/env python3
"""Minimal stdlib dashboard for SDLC observability (legacy port 7700)."""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.infra.sdlc_obs.collector import Collector  # noqa: E402


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        collector = Collector()
        if parsed.path in ("/", "/index.html"):
            self._json({"message": "Use Studio at /studio/obs or /api/kpis"})
            return
        if parsed.path == "/api/kpis":
            self._json(collector.get_kpis())
            return
        if parsed.path == "/api/summary":
            self._json(collector.get_summary())
            return
        if parsed.path == "/api/runs":
            qs = parse_qs(parsed.query)
            limit = int((qs.get("limit") or ["20"])[0])
            stage = (qs.get("stage") or [None])[0]
            runs = collector.get_runs(limit=limit, stage=stage)
            self._json({"runs": runs, "count": len(runs)})
            return
        self._json({"error": "not found"}, status=404)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7700
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"[obs] dashboard http://127.0.0.1:{port}/api/kpis")
    server.serve_forever()


if __name__ == "__main__":
    main()
