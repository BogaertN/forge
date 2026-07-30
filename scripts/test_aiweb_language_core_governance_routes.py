#!/usr/bin/env python3
"""Fail-closed HTTP proof for governed Language Core RMC routes.

This verifier intentionally exercises the real Forge handler and repository.
It may call the response-only Prepare stage, but it never submits a usable
approval or promotion nonce and therefore must not create receipts or stable
memory records.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import os
from pathlib import Path
import socketserver
import stat
import sys
import threading
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main as forge_main  # noqa: E402


STATUS_PATH = "/api/rmc/language-core/charter/status"
PREPARE_PATH = "/api/rmc/language-core/memory/prepare"
APPROVE_PATH = "/api/rmc/language-core/memory/approve"
PROMOTE_PATH = "/api/rmc/language-core/memory/promote"
ASK_FORGE_PATH = "/api/operator/ask-forge/language-core-preview"
MANIFEST_PATH = "/api/rmc/route-manifest"
MAX_GOVERNED_BODY_BYTES = 16 * 1024

EXPECTED_ROUTES: Mapping[str, Mapping[str, object]] = {
    "language_core_charter_status": {
        "method": "GET",
        "path": STATUS_PATH,
        "requires_approval": False,
        "approval_token": None,
    },
    "language_core_memory_prepare": {
        "method": "POST",
        "path": PREPARE_PATH,
        "requires_approval": False,
        "approval_token": None,
    },
    "language_core_memory_approve": {
        "method": "POST",
        "path": APPROVE_PATH,
        "requires_approval": True,
        "approval_token": "APPROVE_LANGUAGE_MEMORY",
    },
    "language_core_memory_promote": {
        "method": "POST",
        "path": PROMOTE_PATH,
        "requires_approval": True,
        "approval_token": "PROMOTE_LANGUAGE_MEMORY",
    },
}

MUTATION_PATHS = (PREPARE_PATH, APPROVE_PATH, PROMOTE_PATH)
MEMORY_ROOTS = (
    ROOT / "memory" / "rmc_language_core_v1",
    ROOT / "memory" / "rmc_language_core_governance_v1",
)


checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    if not condition:
        raise AssertionError(message)
    checks += 1


def _browser_headers(*, content_type: str | None = None) -> dict[str, str]:
    headers = {
        "Host": "localhost:7477",
        "Origin": "http://localhost:7477",
        "Referer": "http://localhost:7477/operator-console/",
        "Sec-Fetch-Site": "same-origin",
        "Accept": "application/json",
    }
    if content_type is not None:
        headers["Content-Type"] = content_type
    return headers


def _request(
    port: int,
    method: str,
    path: str,
    *,
    payload: object | None = None,
    raw_body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    extra_headers: Sequence[tuple[str, str]] = (),
    include_content_length: bool = True,
) -> tuple[int, dict[str, str], bytes]:
    if raw_body is not None and payload is not None:
        raise AssertionError("test request cannot specify payload and raw_body")
    body = (
        raw_body
        if raw_body is not None
        else json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        if payload is not None
        else b""
    )
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    connection.putrequest(method, path, skip_host=True)
    sent_headers = dict(headers or _browser_headers())
    for name, value in sent_headers.items():
        connection.putheader(name, value)
    for name, value in extra_headers:
        connection.putheader(name, value)
    if include_content_length and (body or method == "POST"):
        connection.putheader("Content-Length", str(len(body)))
    connection.endheaders(body)
    response = connection.getresponse()
    response_body = response.read()
    response_headers = {
        name.lower(): value for name, value in response.getheaders()
    }
    status = response.status
    connection.close()
    return status, response_headers, response_body


def _json(body: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(body)
    except Exception as error:
        raise AssertionError(f"{label} did not return JSON: {error}") from error
    if type(value) is not dict:
        raise AssertionError(f"{label} did not return a JSON object")
    return value


def _boundary(payload: Mapping[str, object]) -> Mapping[str, object]:
    value = payload.get("boundary")
    if type(value) is dict:
        return value
    for key in ("preview", "result"):
        nested = payload.get(key)
        if type(nested) is dict and type(nested.get("boundary")) is dict:
            return nested["boundary"]
    return {}


def _snapshot_path(root: Path) -> tuple[tuple[object, ...], ...]:
    """Content snapshot without following symlinks or changing metadata."""

    if not os.path.lexists(root):
        return ((".", "MISSING"),)
    rows: list[tuple[object, ...]] = []
    pending = [root]
    while pending:
        path = pending.pop()
        relative = "." if path == root else path.relative_to(root).as_posix()
        details = path.lstat()
        mode = stat.S_IFMT(details.st_mode)
        if stat.S_ISLNK(details.st_mode):
            rows.append((relative, "SYMLINK", os.readlink(path)))
        elif stat.S_ISDIR(details.st_mode):
            rows.append((relative, "DIRECTORY", stat.S_IMODE(details.st_mode)))
            pending.extend(sorted(path.iterdir(), reverse=True))
        elif stat.S_ISREG(details.st_mode):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(
                (
                    relative,
                    "FILE",
                    stat.S_IMODE(details.st_mode),
                    details.st_size,
                    digest,
                )
            )
        else:
            rows.append((relative, "OTHER", mode))
    return tuple(sorted(rows))


def _memory_snapshot() -> tuple[tuple[str, tuple[tuple[object, ...], ...]], ...]:
    return tuple((str(root), _snapshot_path(root)) for root in MEMORY_ROOTS)


def _assert_no_store(headers: Mapping[str, str], label: str) -> None:
    cache_control = headers.get("cache-control", "").lower()
    check("no-store" in cache_control, f"{label} response must be no-store")


def _assert_refusal(
    status: int,
    headers: Mapping[str, str],
    body: bytes,
    *,
    expected_status: int,
    label: str,
) -> dict[str, object]:
    check(status == expected_status, f"{label} HTTP status must be {expected_status}")
    payload = _json(body, label)
    check(
        payload.get("status") in {"FORBIDDEN", "INVALID", "REJECTED", "ERROR"},
        f"{label} must return a typed refusal",
    )
    check(
        isinstance(payload.get("reason_code"), str)
        and bool(payload.get("reason_code")),
        f"{label} refusal must expose a reason code",
    )
    if "writes_performed" in payload:
        check(payload.get("writes_performed") is False, f"{label} cannot write")
    _assert_no_store(headers, label)
    return payload


def test_manifest(port: int) -> None:
    status, headers, body = _request(port, "GET", MANIFEST_PATH)
    check(status == 200, "route manifest must be available")
    manifest = _json(body, "route manifest")
    routes = manifest.get("routes")
    check(type(routes) is list, "route manifest routes must be a list")
    for route_key, expected in EXPECTED_ROUTES.items():
        matches = [
            route
            for route in routes
            if type(route) is dict and route.get("route_key") == route_key
        ]
        check(len(matches) == 1, f"manifest must contain one {route_key} route")
        route = matches[0]
        for field, value in expected.items():
            check(
                route.get(field) == value,
                f"{route_key} manifest {field} must be exact",
            )
        check(
            route.get("group") == "language_core_governance",
            f"{route_key} must stay in its isolated governance group",
        )
        check(route.get("aliases") == [], f"{route_key} cannot have aliases")
        lookup = manifest.get("lookup")
        check(
            type(lookup) is dict and lookup.get(route_key) == expected["path"],
            f"manifest lookup must bind {route_key} exactly",
        )
    governed_paths = [
        route.get("path")
        for route in routes
        if type(route) is dict
        and route.get("route_key") in EXPECTED_ROUTES
    ]
    check(len(set(governed_paths)) == 4, "governed route paths must be unique")
    check(
        manifest.get("boundary", {}).get("writes_rmc_memory") is False,
        "route discovery cannot write RMC memory",
    )
    # The legacy discovery endpoint predates governed mutation caching rules.
    # The frontend explicitly fetches it with ``cache: no-store``; the four
    # Language Core route responses themselves must set no-store below.


def test_status_and_prepare(port: int) -> tuple[str, dict[str, object]]:
    before = _memory_snapshot()
    status, headers, body = _request(port, "GET", STATUS_PATH)
    check(status == 200, "charter status GET must succeed")
    charter = _json(body, "charter status")
    check(charter.get("status") == "OK", "charter status must pass closed validation")
    check(charter.get("entry_count") == 8, "status must expose only eight fixtures")
    entries = charter.get("entries")
    check(type(entries) is list and len(entries) == 8, "status entries must be exact")
    check(charter.get("writes_performed") is False, "status cannot write")
    check(
        _boundary(charter).get("memory_write_performed") is False,
        "status boundary cannot write memory",
    )
    _assert_no_store(headers, "charter status")
    fixture_id = entries[0].get("fixture_id") if type(entries[0]) is dict else None
    check(isinstance(fixture_id, str) and bool(fixture_id), "fixture ID must be present")
    check(_memory_snapshot() == before, "status GET cannot change governed memory")

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload={"fixture_id": fixture_id},
        headers=_browser_headers(content_type="application/json"),
    )
    check(status == 200, "valid Prepare must succeed")
    prepared = _json(body, "Prepare")
    check(prepared.get("status") == "PREPARED", "Prepare response must be typed")
    check(prepared.get("fixture_id") == fixture_id, "Prepare must bind chosen fixture")
    check(prepared.get("writes_performed") is False, "Prepare cannot write")
    check(prepared.get("written_refs") == [], "Prepare cannot report written refs")
    check(
        prepared.get("approval_token") == "APPROVE_LANGUAGE_MEMORY",
        "Prepare must disclose only the exact approval token",
    )
    check(
        isinstance(prepared.get("approval_action_nonce"), str)
        and bool(prepared.get("approval_action_nonce")),
        "Prepare must issue an approval nonce",
    )
    record = prepared.get("record_preview")
    check(type(record) is dict, "Prepare must return an exact record preview")
    for field in (
        "raw_text_present",
        "token_stream_present",
        "embedding_present",
        "vector_present",
    ):
        check(record.get(field) is False, f"prepared record {field} must be false")
    prepare_boundary = _boundary(prepared)
    check(
        prepare_boundary.get("memory_write_performed") is False,
        "Prepare boundary cannot write memory",
    )
    check(prepare_boundary.get("model_called") is False, "Prepare cannot call a model")
    check(prepare_boundary.get("vector_used") is False, "Prepare cannot use vectors")
    _assert_no_store(headers, "Prepare")
    check(_memory_snapshot() == before, "Prepare cannot change governed memory")
    return fixture_id, prepared


def test_strict_request_boundary(port: int, fixture_id: str) -> None:
    before = _memory_snapshot()
    valid_body = {"fixture_id": fixture_id}

    for path in MUTATION_PATHS:
        missing_origin = _browser_headers(content_type="application/json")
        del missing_origin["Origin"]
        status, headers, body = _request(
            port, "POST", path, payload=valid_body, headers=missing_origin
        )
        _assert_refusal(
            status,
            headers,
            body,
            expected_status=403,
            label=f"{path} missing Origin",
        )

    cases = []
    missing_host = _browser_headers(content_type="application/json")
    del missing_host["Host"]
    cases.append((missing_host, 403, "missing Host"))
    missing_referer = _browser_headers(content_type="application/json")
    del missing_referer["Referer"]
    cases.append((missing_referer, 403, "missing Referer"))
    missing_fetch_site = _browser_headers(content_type="application/json")
    del missing_fetch_site["Sec-Fetch-Site"]
    cases.append((missing_fetch_site, 403, "missing Sec-Fetch-Site"))
    cross_origin = _browser_headers(content_type="application/json")
    cross_origin["Origin"] = "http://attacker.invalid"
    cases.append((cross_origin, 403, "cross-site Origin"))
    cross_referer = _browser_headers(content_type="application/json")
    cross_referer["Referer"] = "http://attacker.invalid/operator-console/"
    cases.append((cross_referer, 403, "cross-site Referer"))
    cross_fetch = _browser_headers(content_type="application/json")
    cross_fetch["Sec-Fetch-Site"] = "cross-site"
    cases.append((cross_fetch, 403, "cross-site fetch metadata"))
    wrong_host = _browser_headers(content_type="application/json")
    wrong_host["Host"] = "attacker.invalid:7477"
    cases.append((wrong_host, 403, "untrusted Host"))
    wrong_content_type = _browser_headers(content_type="text/plain")
    cases.append((wrong_content_type, 415, "wrong Content-Type"))
    for headers_case, expected_status, label in cases:
        status, response_headers, body = _request(
            port,
            "POST",
            PREPARE_PATH,
            payload=valid_body,
            headers=headers_case,
        )
        _assert_refusal(
            status,
            response_headers,
            body,
            expected_status=expected_status,
            label=f"Prepare {label}",
        )

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=valid_body,
        headers=_browser_headers(),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=415,
        label="Prepare missing Content-Type",
    )

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=valid_body,
        headers=_browser_headers(content_type="application/json"),
        include_content_length=False,
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=411,
        label="Prepare missing Content-Length",
    )

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=valid_body,
        headers=_browser_headers(content_type="application/json"),
        extra_headers=(("Origin", "http://localhost:7477"),),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=400,
        label="Prepare duplicate required header",
    )

    oversized = b'{' + (b'"padding":"' + b'x' * MAX_GOVERNED_BODY_BYTES + b'"}')
    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        raw_body=oversized,
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=413,
        label="oversized Prepare",
    )

    duplicate = (
        '{"fixture_id":'
        + json.dumps(fixture_id)
        + ',"fixture_id":'
        + json.dumps(fixture_id)
        + "}"
    ).encode("utf-8")
    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        raw_body=duplicate,
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=400,
        label="duplicate-key Prepare",
    )
    check(_memory_snapshot() == before, "request-boundary refusals cannot write")


def test_nonce_refusal_and_method_lock(port: int) -> None:
    before = _memory_snapshot()
    impossible_approval = {
        "proposal_id": "language_memory_proposal:" + "0" * 64,
        "record_id": "rmc_exact_language_record:" + "0" * 64,
        "approval_token": "APPROVE_LANGUAGE_MEMORY",
        "approval_confirmation_phrase": "not an issued confirmation phrase",
    }
    status, headers, body = _request(
        port,
        "POST",
        APPROVE_PATH,
        payload=impossible_approval,
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        label="missing approval nonce",
    )
    approval_headers = _browser_headers(content_type="application/json")
    approval_headers["X-Forge-Action-Nonce"] = "nonexistent-approval-nonce"
    status, headers, body = _request(
        port,
        "POST",
        APPROVE_PATH,
        payload=impossible_approval,
        headers=approval_headers,
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        label="nonexistent approval nonce",
    )

    impossible_promotion = {
        "proposal_id": "language_memory_proposal:" + "0" * 64,
        "record_id": "rmc_exact_language_record:" + "0" * 64,
        "approval_receipt_id": "operator_approval_receipt:" + "0" * 64,
        "promotion_token": "PROMOTE_LANGUAGE_MEMORY",
        "promotion_confirmation_phrase": "not an issued confirmation phrase",
    }
    promotion_headers = _browser_headers(content_type="application/json")
    promotion_headers["X-Forge-Action-Nonce"] = "nonexistent-promotion-nonce"
    status, headers, body = _request(
        port,
        "POST",
        PROMOTE_PATH,
        payload=impossible_promotion,
        headers=promotion_headers,
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        label="nonexistent promotion nonce",
    )

    for path in MUTATION_PATHS:
        status, _, _ = _request(port, "GET", path)
        check(status == 404, f"GET {path} must remain unavailable")
    check(_memory_snapshot() == before, "nonce and method refusals cannot write")


def test_ask_forge_cannot_promote(port: int, prepared: Mapping[str, object]) -> None:
    before = _memory_snapshot()
    smuggled = {
        "source_text": "Forge uses RMC memory.",
        "fixture_id": prepared.get("fixture_id"),
        "proposal_id": prepared.get("proposal_id"),
        "record_id": prepared.get("record_id"),
        "approval_token": "APPROVE_LANGUAGE_MEMORY",
        "promotion_token": "PROMOTE_LANGUAGE_MEMORY",
    }
    status, _, body = _request(
        port,
        "POST",
        ASK_FORGE_PATH,
        payload=smuggled,
        headers=_browser_headers(content_type="application/json"),
    )
    check(status in {200, 400, 403, 409, 422}, "Ask Forge refusal must be bounded")
    response = _json(body, "Ask Forge promotion smuggling")
    check(
        response.get("status")
        in {"INVALID", "ERROR", "REJECTED", "HELD", "UNSUPPORTED"},
        "Ask Forge must refuse governance fields",
    )
    check(
        response.get("reason_code") == "request_contains_unsupported_fields",
        "Ask Forge refusal must identify unsupported fields",
    )
    boundary = _boundary(response)
    check(
        boundary.get("rmc_memory_write_performed") is False,
        "Ask Forge cannot write RMC memory",
    )
    check(boundary.get("filesystem_write_performed") is False, "Ask Forge cannot write files")
    check(boundary.get("action_performed") is False, "Ask Forge cannot perform actions")
    check(_memory_snapshot() == before, "Ask Forge cannot promote or write receipts")


def main() -> int:
    before = _memory_snapshot()
    server = socketserver.TCPServer(("127.0.0.1", 0), forge_main._p201_make_handler())
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        test_manifest(port)
        fixture_id, prepared = test_status_and_prepare(port)
        test_strict_request_boundary(port, fixture_id)
        test_nonce_refusal_and_method_lock(port)
        test_ask_forge_cannot_promote(port, prepared)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    check(_memory_snapshot() == before, "entire HTTP verifier must leave memory unchanged")
    print(f"Governed Language Core HTTP routes: {checks} checks passed")
    print("successful_approval_calls=0")
    print("successful_promotion_calls=0")
    print("governed_memory_changes=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
