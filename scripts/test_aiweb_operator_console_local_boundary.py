#!/usr/bin/env python3
"""Functional boundary checks for Forge's local operator-console server."""

from __future__ import annotations

import http.client
from pathlib import Path
import socketserver
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main


def _request(port: int, method: str, headers: dict[str, str]) -> tuple[int, dict[str, str]]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    connection.putrequest(method, "/api/status", skip_host=True)
    for name, value in headers.items():
        connection.putheader(name, value)
    connection.endheaders()
    response = connection.getresponse()
    response.read()
    result = response.status, {name.lower(): value for name, value in response.getheaders()}
    connection.close()
    return result


def main_test() -> int:
    handler = main._p201_make_handler()
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    checks = 0
    try:
        status, headers = _request(
            port,
            "GET",
            {"Host": "localhost:7477", "Origin": "http://localhost:7477"},
        )
        assert status == 200
        assert headers.get("access-control-allow-origin") == "http://localhost:7477"
        assert headers.get("access-control-allow-origin") != "*"
        checks += 3

        status, headers = _request(
            port,
            "GET",
            {"Host": "localhost:7477", "Origin": "https://untrusted.example"},
        )
        assert status == 403
        assert "access-control-allow-origin" not in headers
        checks += 2

        status, _ = _request(port, "GET", {"Host": "operator.example"})
        assert status == 403
        checks += 1

        status, _ = _request(
            port,
            "GET",
            {"Host": "localhost:7477", "Sec-Fetch-Site": "cross-site"},
        )
        assert status == 403
        checks += 1

        status, headers = _request(
            port,
            "OPTIONS",
            {"Host": "127.0.0.1:7477", "Origin": "http://127.0.0.1:7477"},
        )
        assert status == 200
        assert headers.get("access-control-allow-origin") == "http://127.0.0.1:7477"
        assert headers.get("access-control-allow-origin") != "*"
        checks += 3
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    print(f"Operator console local boundary: {checks} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_test())
