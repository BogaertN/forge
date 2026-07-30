#!/usr/bin/env python3
"""HTTP integration proof for the live local Language Core stack."""

from __future__ import annotations

import http.client
import json
from pathlib import Path
import socketserver
import sys
import threading


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main  # noqa: E402


def _request(
    port: int,
    method: str,
    path: str,
    payload: object | None = None,
) -> tuple[int, dict[str, str], bytes]:
    body = (
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if payload is not None
        else b""
    )
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    connection.putrequest(method, path, skip_host=True)
    connection.putheader("Host", "localhost:7477")
    connection.putheader("Origin", "http://localhost:7477")
    if body:
        connection.putheader("Content-Type", "application/json")
        connection.putheader("Content-Length", str(len(body)))
    connection.endheaders(body)
    response = connection.getresponse()
    response_body = response.read()
    headers = {name.lower(): value for name, value in response.getheaders()}
    status = response.status
    connection.close()
    return status, headers, response_body


def _field() -> dict[str, object]:
    return {
        "identity_refs": ["identity:http-integration"],
        "phase_index": 4,
        "recursion_depth": 2,
        "drift_micro": 200_000,
        "resonance_micro": 800_000,
        "memory_charge_micro": 500_000,
        "entropy_micro": 300_000,
        "loop_ref": "loop:http-integration",
        "echo_ancestry_refs": ["ancestry:origin"],
        "lineage_refs": ["lineage:http-integration"],
        "locked": False,
        "archived": False,
        "grace_used": False,
        "revision": 0,
    }


def main_test() -> int:
    checks = 0
    server = socketserver.TCPServer(("127.0.0.1", 0), main._p201_make_handler())
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, _, body = _request(
            port,
            "POST",
            "/api/operator/ask-forge",
            {"source_text": "Can Forge report status?", "allow_network": False},
        )
        operator = json.loads(body)
        assert status == 200
        assert operator["status"] == "ANSWERED"
        assert operator["answer_kind"] == "typed_capability"
        assert operator["route"] == "typed_forge_status_capability"
        assert operator["source_text"] == "Can Forge report status?"
        assert operator["candidate_retention"] is None
        assert operator["boundary"]["calls_llm"] is False
        assert operator["boundary"]["conventional_token_stream_created"] is False
        assert operator["boundary"]["automatic_canonicalization_allowed"] is False
        checks += 9

        status, headers, body = _request(
            port,
            "POST",
            "/api/operator/ask-forge/language-core-preview",
            {"source_text": "Please inspect the manifest."},
        )
        language = json.loads(body)
        assert status == 200
        assert headers.get("access-control-allow-origin") == "http://localhost:7477"
        assert language["status"] == "PREVIEW_READY"
        provider = language["trusted_rmc_provider"]
        assert provider["load_status"] in {"TRUSTED_EMPTY", "TRUSTED_STRUCTURED"}
        assert language["boundary"]["filesystem_read_performed"] is provider["filesystem_read_performed"]
        assert language["boundary"]["memory_read_performed"] is provider["memory_read_performed"]
        if provider["load_status"] == "TRUSTED_STRUCTURED":
            assert provider["stable_record_count"] + provider["live_record_count"] > 0
            assert provider["filesystem_read_performed"] is True
            assert provider["memory_read_performed"] is True
        else:
            assert provider["stable_record_count"] == 0
            assert provider["live_record_count"] == 0
            assert provider["memory_read_performed"] is False
        selected_ref = language["selected_meaning"]["meaning_candidate_id"]
        exact_support = [
            item
            for item in language["rmc_exact_identity_resonances"]
            if item["meaning_candidate_ref"] == selected_ref
            and item["exact_semantic_contract_refs"]
        ]
        council = language["operator_council"]
        if exact_support:
            assert provider["load_status"] == "TRUSTED_STRUCTURED"
            assert council["status"] == "RECOMMEND_FOR_OPERATOR_REVIEW"
            assert council["result"]["evidence"]["selected_meaning_support_status"] == "EXACT_SUPPORT"
        else:
            assert council["status"] == "HOLD_FOR_EVIDENCE"
            assert (
                council["result"]["evidence"]["selected_meaning_support_status"]
                == "NO_ADEQUATE_EXACT_SUPPORT"
            )
        assert council["recommendation_only"] is True
        assert council["result"]["recommendation"]["executable"] is False
        assert language["boundary"]["tokenization_performed"] is False
        assert language["boundary"]["vector_used"] is False
        assert language["boundary"]["rmc_memory_write_performed"] is False
        assert language["boundary"]["delivery_performed"] is False
        checks += 17

        status, _, body = _request(
            port,
            "POST",
            "/api/operator/ask-forge/language-core-preview",
            {"source_text": "What does core mean?"},
        )
        core = json.loads(body)
        assert status == 200
        if core["status"] == "PREVIEW_READY":
            assert provider["load_status"] == "TRUSTED_STRUCTURED"
            assert core["reason_code"] == "unique_exact_rmc_resonance"
            selected_ref = core["selected_meaning"]["meaning_candidate_id"]
            selection_resonances = [
                item
                for item in core["rmc_context"]["resonances"]
                if item["meaning_candidate_ref"] == selected_ref
                and item["used_for_selection"] is True
                and item["exact_semantic_contract_refs"]
            ]
            assert core["rmc_context"]["context_used_for_selection"] is True
            assert core["rmc_context"]["memory_write_performed"] is False
            assert len(selection_resonances) == 1
            exact_support = [
                item
                for item in core["rmc_exact_identity_resonances"]
                if item["meaning_candidate_ref"] == selected_ref
                and item["exact_semantic_contract_refs"]
            ]
            assert exact_support
            assert all(item["approximate_match_used"] is False for item in exact_support)
            council = core["operator_council"]
            recommendation = council["result"]["recommendation"]
            assert council["status"] == "RECOMMEND_FOR_OPERATOR_REVIEW"
            assert council["recommendation_only"] is True
            assert recommendation["executable"] is False
            assert recommendation["authoritative"] is False
            checks += 14
        else:
            assert core["status"] == "HELD"
            assert core["selected_meaning"] is None
            assert core["rmc_context"]["context_used_for_selection"] is False
            checks += 4

        status, _, body = _request(
            port,
            "POST",
            "/api/rmc/rsoc-law-lab/preview",
            {"glyph": "Ĉ", "operands": [_field()]},
        )
        law = json.loads(body)
        assert status == 200
        assert law["status"] == "PREVIEW_READY"
        assert law["output_fields"][0]["archived"] is True
        assert law["boundary"]["persistence_performed"] is False
        assert law["boundary"]["operator_runtime_invoked"] is False
        checks += 5

        status, _, body = _request(port, "GET", "/api/rmc/route-manifest")
        manifest = json.loads(body)
        assert status == 200
        assert manifest["lookup"]["rsoc_law_lab_preview"] == "/api/rmc/rsoc-law-lab/preview"
        assert manifest["lookup"]["ask_forge_symbolic_operator"] == "/api/operator/ask-forge"
        assert manifest["lookup"]["ask_forge_language_core_preview"] == "/api/operator/ask-forge/language-core-preview"
        checks += 4

        status, _, body = _request(port, "GET", "/operator-console/")
        assert status == 200
        assert b'<div id="root"></div>' in body
        checks += 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    print(f"Live local Language Core stack: {checks} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_test())
