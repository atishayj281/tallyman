"""Tiny stdlib health server so the Compose skeleton has something real to run.

Replaced by the FastAPI service in WA-21; kept until then so `docker compose up`
and the container healthcheck can be verified on day one.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from wa import __version__


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self.send_error(404)
            return
        body = json.dumps({"status": "ok", "version": __version__}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


def main() -> None:
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()  # noqa: S104


if __name__ == "__main__":
    main()
