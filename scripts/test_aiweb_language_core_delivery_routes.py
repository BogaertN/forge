#!/usr/bin/env python3
"""HTTP proof for exact, operator-approved Language Core output delivery.

The verifier starts Forge's real standard-library HTTP handler on an ephemeral
listener and addresses it with the canonical localhost:7477 browser envelope.
It exercises the live route manifest, fail-closed request boundary, exact
evidence binding, one-time approval nonce, and the definition-only delivery
rule.  Delivery is response-only: the governed RMC stores are content-snapshotted
before and after the complete run.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import http.client
import json
import os
from pathlib import Path
import socketserver
import stat
import sys
import threading


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main as forge_main  # noqa: E402


MANIFEST_PATH = "/api/rmc/route-manifest"
PREVIEW_PATH = "/api/operator/ask-forge/language-core-preview"
PREPARE_PATH = "/api/operator/ask-forge/language-core-delivery/prepare"
APPROVE_PATH = "/api/operator/ask-forge/language-core-delivery/approve"
APPROVAL_TOKEN = "APPROVE_LANGUAGE_OUTPUT"
DEFINITION_SOURCE = "What does language core mean?"
RESTATEMENT_SOURCE = "Please inspect the manifest."

EXPECTED_ROUTES: Mapping[str, Mapping[str, object]] = {
    "language_core_delivery_prepare": {
        "method": "POST",
        "path": PREPARE_PATH,
        "group": "language_core_delivery",
        "stage": "exact_language_output_delivery_prepare",
        "requires_approval": False,
        "approval_token": None,
        "aliases": [],
    },
    "language_core_delivery_approve": {
        "method": "POST",
        "path": APPROVE_PATH,
        "group": "language_core_delivery",
        "stage": "exact_language_output_operator_delivery",
        "requires_approval": True,
        "approval_token": APPROVAL_TOKEN,
        "aliases": [],
    },
}

# These are the only existing or prospective stores the isolated Language Core
# delivery layer could reasonably target.  The runtime contract additionally
# asserts no filesystem or memory write on every response and receipt.
MEMORY_ROOTS = (
    ROOT / "memory" / "rmc_language_core_v1",
    ROOT / "memory" / "rmc_language_core_governance_v1",
    ROOT / "memory" / "rmc_language_output_delivery_v1",
    ROOT / "memory" / "language_output_delivery_v1",
)

checks = 0


def check(condition: object, message: str) -> None:
    global checks
    if condition is not True:
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
    if payload is not None and raw_body is not None:
        raise AssertionError("request cannot specify both payload and raw_body")
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
    for name, value in dict(headers or _browser_headers()).items():
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


def _mapping(value: object, label: str) -> dict[str, object]:
    if type(value) is not dict:
        raise AssertionError(f"{label} must be a JSON object")
    return value


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value:
        raise AssertionError(f"{label} must be non-empty text")
    return value


def _assert_no_store(headers: Mapping[str, str], label: str) -> None:
    check(
        "no-store" in headers.get("cache-control", "").lower(),
        f"{label} response must be no-store",
    )


def _assert_no_write_response(payload: Mapping[str, object], label: str) -> None:
    check(payload.get("writes_performed") is False, f"{label} cannot write")
    check(payload.get("written_refs") == [], f"{label} written refs must be empty")
    boundary = _mapping(payload.get("boundary"), f"{label} boundary")
    for field in (
        "filesystem_write_performed",
        "memory_write_performed",
        "identity_write_performed",
        "contribution_economy_write_performed",
        "tool_routing_performed",
        "action_performed",
    ):
        check(boundary.get(field) is False, f"{label} boundary {field} must be false")


def _assert_refusal(
    status: int,
    headers: Mapping[str, str],
    body: bytes,
    *,
    expected_status: int,
    label: str,
    expected_reason: str | None = None,
) -> dict[str, object]:
    check(status == expected_status, f"{label} HTTP status must be {expected_status}")
    response = _json(body, label)
    check(response.get("status") == "REJECTED", f"{label} must reject")
    reason = response.get("reason_code")
    check(type(reason) is str and bool(reason), f"{label} must expose a reason code")
    if expected_reason is not None:
        check(reason == expected_reason, f"{label} reason code must be exact")
    check(response.get("delivery_performed") is False, f"{label} cannot deliver")
    check(
        response.get("answer_delivery_performed") is False,
        f"{label} cannot deliver an answer",
    )
    if "writes_performed" in response:
        check(response.get("writes_performed") is False, f"{label} cannot write")
    _assert_no_store(headers, label)
    return response


def _snapshot_path(root: Path) -> tuple[tuple[object, ...], ...]:
    if not os.path.lexists(root):
        return ((".", "MISSING"),)
    rows: list[tuple[object, ...]] = []
    pending = [root]
    while pending:
        path = pending.pop()
        relative = "." if path == root else path.relative_to(root).as_posix()
        details = path.lstat()
        if stat.S_ISLNK(details.st_mode):
            rows.append((relative, "SYMLINK", os.readlink(path)))
        elif stat.S_ISDIR(details.st_mode):
            rows.append((relative, "DIRECTORY", stat.S_IMODE(details.st_mode)))
            pending.extend(sorted(path.iterdir(), reverse=True))
        elif stat.S_ISREG(details.st_mode):
            rows.append(
                (
                    relative,
                    "FILE",
                    stat.S_IMODE(details.st_mode),
                    details.st_size,
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
            )
        else:
            rows.append((relative, "OTHER", stat.S_IFMT(details.st_mode)))
    return tuple(sorted(rows))


def _memory_snapshot() -> tuple[tuple[str, tuple[tuple[object, ...], ...]], ...]:
    return tuple((str(root), _snapshot_path(root)) for root in MEMORY_ROOTS)


def test_manifest(port: int) -> None:
    status, _, body = _request(port, "GET", MANIFEST_PATH)
    check(status == 200, "live route manifest must be available")
    manifest = _json(body, "route manifest")
    routes = manifest.get("routes")
    check(type(routes) is list, "route manifest routes must be a list")
    lookup = _mapping(manifest.get("lookup"), "route manifest lookup")
    for route_key, expected in EXPECTED_ROUTES.items():
        matches = [
            route
            for route in routes
            if type(route) is dict and route.get("route_key") == route_key
        ]
        check(len(matches) == 1, f"manifest must contain one {route_key}")
        route = matches[0]
        for field, expected_value in expected.items():
            check(
                route.get(field) == expected_value,
                f"{route_key} manifest field {field} must be exact",
            )
        check(
            lookup.get(route_key) == expected["path"],
            f"manifest lookup must bind {route_key} exactly",
        )


def _preview(port: int, source_text: str) -> dict[str, object]:
    status, _, body = _request(
        port,
        "POST",
        PREVIEW_PATH,
        payload={"source_text": source_text},
        headers=_browser_headers(content_type="application/json"),
    )
    check(status == 200, f"preview for {source_text!r} must return HTTP 200")
    preview = _json(body, f"preview for {source_text!r}")
    check(preview.get("status") == "PREVIEW_READY", "preview must be ready")
    check(preview.get("source_text") == source_text, "preview must preserve source")
    check(preview.get("clarification_request") is None, "test source cannot clarify")
    return preview


def _delivery_request(
    preview: Mapping[str, object], source_text: str
) -> dict[str, object]:
    receipt = _mapping(preview.get("receipt"), "integrated receipt")
    compiler_receipt = _mapping(preview.get("compiler_receipt"), "compiler receipt")
    governed = _mapping(preview.get("governed_output"), "governed output")
    manifest = _mapping(governed.get("manifest"), "output manifest")
    rendered = _mapping(governed.get("rendered_output"), "rendered output")
    exact_echo = _mapping(governed.get("exact_echo"), "exact output Echo")
    council = _mapping(preview.get("operator_council"), "Operator Council")
    council_result = _mapping(council.get("result"), "Operator Council result")
    return {
        "preview_request": {"source_text": source_text},
        "integrated_result_id": _text(preview.get("result_id"), "integrated result ID"),
        "integrated_receipt_id": _text(receipt.get("receipt_id"), "integrated receipt ID"),
        "compiler_result_id": _text(preview.get("compiler_result_id"), "compiler result ID"),
        "compiler_receipt_id": _text(compiler_receipt.get("receipt_id"), "compiler receipt ID"),
        "manifest_id": _text(manifest.get("manifest_id"), "manifest ID"),
        "rendered_output_id": _text(
            rendered.get("rendered_output_id"), "rendered output ID"
        ),
        "exact_echo_id": _text(
            exact_echo.get("echo_id", exact_echo.get("echo_validation_id")),
            "exact Echo ID",
        ),
        "operator_council_result_id": _text(
            council_result.get("result_id"), "Operator Council result ID"
        ),
    }


def test_same_origin_and_strict_json(
    port: int, valid_request: Mapping[str, object]
) -> None:
    before = _memory_snapshot()

    missing_origin = _browser_headers(content_type="application/json")
    del missing_origin["Origin"]
    status, headers, body = _request(
        port, "POST", PREPARE_PATH, payload=valid_request, headers=missing_origin
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        label="Prepare missing Origin",
    )

    cross_origin = _browser_headers(content_type="application/json")
    cross_origin["Origin"] = "http://attacker.invalid"
    status, headers, body = _request(
        port, "POST", PREPARE_PATH, payload=valid_request, headers=cross_origin
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        label="Prepare cross-origin request",
    )

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=valid_request,
        headers=_browser_headers(content_type="text/plain"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=415,
        label="Prepare wrong Content-Type",
    )

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH + "?invented=true",
        payload=valid_request,
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=400,
        label="Prepare query-string route invention",
    )

    duplicate_body = (
        '{"preview_request":'
        + json.dumps(valid_request["preview_request"], separators=(",", ":"))
        + ',"preview_request":'
        + json.dumps(valid_request["preview_request"], separators=(",", ":"))
        + "}"
    ).encode("utf-8")
    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        raw_body=duplicate_body,
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=400,
        label="Prepare duplicate-key JSON",
    )

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        raw_body=b"{not-json",
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=400,
        label="Prepare malformed JSON",
    )

    extra_field_request = dict(valid_request)
    extra_field_request["caller_supplied_answer_text"] = "smuggled"
    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=extra_field_request,
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=400,
        expected_reason="delivery_request_fields_not_exact",
        label="Prepare extra caller-authored field",
    )

    unexpected_nonce_headers = _browser_headers(content_type="application/json")
    unexpected_nonce_headers["X-Forge-Action-Nonce"] = "not-admitted-on-prepare"
    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=valid_request,
        headers=unexpected_nonce_headers,
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=400,
        label="Prepare unexpected action nonce",
    )

    impossible_approve = {
        **valid_request,
        "delivery_proposal_id": "language_output_delivery_proposal:" + "0" * 64,
        "approval_token": APPROVAL_TOKEN,
        "approval_confirmation_phrase": "not an issued confirmation phrase",
    }
    status, headers, body = _request(
        port,
        "POST",
        APPROVE_PATH,
        payload=impossible_approve,
        headers=_browser_headers(content_type="application/json"),
    )
    _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        label="Approve missing action nonce",
    )
    check(_memory_snapshot() == before, "security refusals cannot change RMC memory")


def test_restatement_refusal(
    port: int, preview: Mapping[str, object], request: Mapping[str, object]
) -> None:
    before = _memory_snapshot()
    governed = _mapping(preview.get("governed_output"), "restatement governed output")
    check(
        governed.get("output_purpose") == "controlled_restatement_preview",
        "non-definition output must be a controlled restatement preview",
    )
    check(
        governed.get("answer_delivery_eligible") is False,
        "controlled restatement cannot be answer-delivery eligible",
    )
    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=request,
        headers=_browser_headers(content_type="application/json"),
    )
    response = _assert_refusal(
        status,
        headers,
        body,
        expected_status=409,
        expected_reason="output_not_answer_delivery_eligible",
        label="controlled restatement delivery",
    )
    _assert_no_write_response(response, "controlled restatement delivery")
    check(
        "delivery_action_nonce" not in response,
        "controlled restatement refusal cannot issue a delivery nonce",
    )
    check(
        _memory_snapshot() == before,
        "controlled restatement delivery refusal cannot change RMC memory",
    )


def test_definition_prepare_approve_and_replay(
    port: int, preview: Mapping[str, object], request: Mapping[str, object]
) -> None:
    before = _memory_snapshot()
    governed = _mapping(preview.get("governed_output"), "definition governed output")
    rendered = _mapping(governed.get("rendered_output"), "definition rendered output")
    exact_echo = _mapping(governed.get("exact_echo"), "definition exact Echo")
    expected_text = _text(rendered.get("text"), "definition rendered text")
    check(governed.get("output_purpose") == "definition_answer", "purpose must be definition")
    check(governed.get("answer_delivery_eligible") is True, "definition must be eligible")
    check(exact_echo.get("status") == "PASS", "definition exact Echo must pass")
    check(preview.get("candidate_wording") == expected_text, "renderer must preserve wording")

    status, headers, body = _request(
        port,
        "POST",
        PREPARE_PATH,
        payload=request,
        headers=_browser_headers(content_type="application/json"),
    )
    check(status == 200, "definition Prepare must succeed")
    prepared = _json(body, "definition Prepare")
    check(prepared.get("status") == "PREPARED", "Prepare must be typed")
    check(prepared.get("approval_token") == APPROVAL_TOKEN, "approval token must be exact")
    proposal_id = _text(prepared.get("delivery_proposal_id"), "delivery proposal ID")
    phrase = _text(
        prepared.get("approval_confirmation_phrase"), "delivery approval phrase"
    )
    nonce = _text(prepared.get("delivery_action_nonce"), "delivery action nonce")
    for key, value in request.items():
        if key != "preview_request":
            check(prepared.get(key) == value, f"Prepare must bind {key} exactly")
    check(prepared.get("delivery_performed") is False, "Prepare cannot deliver")
    check(prepared.get("answer_delivery_performed") is False, "Prepare cannot answer")
    _assert_no_write_response(prepared, "definition Prepare")
    _assert_no_store(headers, "definition Prepare")

    approval_request = {
        **request,
        "delivery_proposal_id": proposal_id,
        "approval_token": APPROVAL_TOKEN,
        "approval_confirmation_phrase": phrase,
    }
    tampered = dict(approval_request)
    tampered["manifest_id"] = "governed_output_manifest:" + "0" * 64
    approval_headers = _browser_headers(content_type="application/json")
    approval_headers["X-Forge-Action-Nonce"] = nonce
    status, headers, body = _request(
        port,
        "POST",
        APPROVE_PATH,
        payload=tampered,
        headers=approval_headers,
    )
    tampered_response = _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        expected_reason="delivery_evidence_binding_mismatch",
        label="tampered definition binding",
    )
    _assert_no_write_response(tampered_response, "tampered definition binding")

    # A failed binding check must not secretly deliver or consume authority.
    status, headers, body = _request(
        port,
        "POST",
        APPROVE_PATH,
        payload=approval_request,
        headers=approval_headers,
    )
    check(status == 200, "untampered operator approval must succeed")
    delivered = _json(body, "definition delivery")
    check(delivered.get("status") == "DELIVERED", "delivery must be typed")
    check(delivered.get("delivered_text") == expected_text, "delivered text must be bound")
    check(delivered.get("delivery_performed") is True, "delivery flag must be true")
    check(
        delivered.get("answer_delivery_performed") is True,
        "answer delivery flag must be true",
    )
    check(delivered.get("writes_performed") is False, "delivery cannot write")
    check(delivered.get("written_refs") == [], "delivery written refs must be empty")
    delivery_boundary = _mapping(delivered.get("boundary"), "delivery boundary")
    check(delivery_boundary.get("delivery_performed") is True, "boundary must record delivery")
    check(
        delivery_boundary.get("answer_delivery_performed") is True,
        "boundary must record answer delivery",
    )
    for field in (
        "filesystem_write_performed",
        "memory_write_performed",
        "identity_write_performed",
        "contribution_economy_write_performed",
        "tool_routing_performed",
        "action_performed",
    ):
        check(delivery_boundary.get(field) is False, f"delivery boundary {field} must be false")
    receipt = _mapping(delivered.get("delivery_receipt"), "delivery receipt")
    check(receipt.get("delivery_proposal_ref") == proposal_id, "receipt binds proposal")
    check(receipt.get("manifest_ref") == request["manifest_id"], "receipt binds manifest")
    check(
        receipt.get("rendered_output_ref") == request["rendered_output_id"],
        "receipt binds rendered output",
    )
    check(receipt.get("exact_echo_ref") == request["exact_echo_id"], "receipt binds Echo")
    check(receipt.get("exact_echo_passed") is True, "receipt records exact Echo pass")
    check(receipt.get("operator_identity_authenticated") is False, "identity is not invented")
    check(receipt.get("memory_write_performed") is False, "receipt records no memory write")
    check(receipt.get("filesystem_write_performed") is False, "receipt records no file write")
    check(
        receipt.get("rendered_text_sha256")
        == hashlib.sha256(expected_text.encode("utf-8")).hexdigest(),
        "receipt binds the exact delivered bytes",
    )
    _assert_no_store(headers, "definition delivery")

    status, headers, body = _request(
        port,
        "POST",
        APPROVE_PATH,
        payload=approval_request,
        headers=approval_headers,
    )
    replay = _assert_refusal(
        status,
        headers,
        body,
        expected_status=403,
        expected_reason="delivery_action_nonce_invalid",
        label="delivery nonce replay",
    )
    _assert_no_write_response(replay, "delivery nonce replay")
    check(_memory_snapshot() == before, "complete delivery flow cannot change RMC memory")


def main() -> int:
    before = _memory_snapshot()
    server = socketserver.TCPServer(("127.0.0.1", 0), forge_main._p201_make_handler())
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        test_manifest(port)
        definition_preview = _preview(port, DEFINITION_SOURCE)
        restatement_preview = _preview(port, RESTATEMENT_SOURCE)
        definition_request = _delivery_request(definition_preview, DEFINITION_SOURCE)
        restatement_request = _delivery_request(restatement_preview, RESTATEMENT_SOURCE)
        test_same_origin_and_strict_json(port, definition_request)
        test_restatement_refusal(port, restatement_preview, restatement_request)
        test_definition_prepare_approve_and_replay(
            port, definition_preview, definition_request
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    check(_memory_snapshot() == before, "HTTP delivery verifier must leave RMC memory unchanged")
    print(f"Exact Language Core delivery routes: {checks} checks passed")
    print("definition_deliveries=1")
    print("controlled_restatement_deliveries=0")
    print("nonce_replays_accepted=0")
    print("governed_memory_changes=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
