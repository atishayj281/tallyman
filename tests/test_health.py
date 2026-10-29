import json
import threading
from http.server import HTTPServer
from urllib.request import urlopen

from wa.health import Handler


def test_health_endpoint():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    with urlopen(f"http://127.0.0.1:{port}/health") as r:  # noqa: S310
        assert r.status == 200
        assert json.loads(r.read())["status"] == "ok"
    server.shutdown()
