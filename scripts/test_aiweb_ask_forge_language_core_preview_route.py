#!/usr/bin/env python3
"""Adapter and static route tests for Ask Forge Language Core Preview."""

from __future__ import annotations

import argparse
import builtins
from contextlib import ExitStack
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request
from unittest.mock import patch


ENDPOINT_EXPECTED = "/api/operator/ask-forge/language-core-preview"


class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str, detail: object = "") -> None:
        self.checks += 1
        if condition is not True:
            message = label + ((": " + repr(detail)[:1200]) if detail not in (None, "") else "")
            self.failures.append(message)
            print("FAIL - " + message)


def _forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("forbidden external side effect attempted")


def _boundary(response: dict[str, object]) -> dict[str, object]:
    value = response.get("boundary")
    if isinstance(value, dict):
        return value
    preview = response.get("preview")
    if isinstance(preview, dict) and isinstance(preview.get("boundary"), dict):
        return preview["boundary"]
    result = response.get("result")
    if isinstance(result, dict) and isinstance(result.get("boundary"), dict):
        return result["boundary"]
    return {}


def _source_text(response: dict[str, object]) -> object:
    if "source_text" in response:
        return response.get("source_text")
    source = response.get("source")
    if isinstance(source, dict):
        return source.get("exact_text", source.get("source_text"))
    for key in ("preview", "result"):
        nested = response.get(key)
        if isinstance(nested, dict):
            if "source_text" in nested:
                return nested.get("source_text")
            nested_source = nested.get("source")
            if isinstance(nested_source, dict):
                return nested_source.get("exact_text", nested_source.get("source_text"))
    return None


def _handler_segment(main_source: str) -> str:
    marker = f'_p281_req_path == "{ENDPOINT_EXPECTED}"'
    start = main_source.find(marker)
    if start < 0:
        return ""
    next_branch = main_source.find("\n            elif ", start + len(marker))
    return main_source[start : next_branch if next_branch >= 0 else start + 3000]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    sys.path.insert(0, str(repo))
    ledger = Ledger()

    from rmc_engine_v1.meaning_compiler_preview import (
        ENDPOINT,
        build_language_core_preview_response,
    )

    ledger.check(ENDPOINT == ENDPOINT_EXPECTED, "adapter endpoint exact", ENDPOINT)

    source = "Please inspect the manifest."
    first = build_language_core_preview_response({"source_text": source})
    second = build_language_core_preview_response({"source_text": source})
    ledger.check(isinstance(first, dict), "adapter returns JSON object")
    ledger.check(first == second, "adapter response deterministic")
    ledger.check(first.get("status") == "PREVIEW_READY", "ready request reaches preview", first)
    ledger.check(first.get("endpoint") == ENDPOINT_EXPECTED, "response endpoint exact", first)
    ledger.check(_source_text(first) == source, "response preserves exact source", first)
    round_trip = json.loads(json.dumps(first, ensure_ascii=False))
    ledger.check(isinstance(round_trip, dict), "response is JSON safe")
    ledger.check(_source_text(round_trip) == source, "JSON round trip preserves exact Unicode source")
    ledger.check(bool(first.get("result_id") or first.get("preview_result_id") or (first.get("preview") or {}).get("result_id")), "response exposes preview identity", first)

    ambiguous = build_language_core_preview_response({"source_text": "What does core mean?"})
    ledger.check(ambiguous.get("status") == "HELD", "ambiguity held at adapter", ambiguous)
    ledger.check(ambiguous.get("endpoint") == ENDPOINT_EXPECTED, "held response endpoint exact")

    unknown = build_language_core_preview_response({"source_text": "What does bank mean?"})
    ledger.check(unknown.get("status") in {"HELD", "UNSUPPORTED"}, "unknown source fails closed", unknown)

    injected_context = build_language_core_preview_response({
        "source_text": "What does core mean?",
        "rmc_snapshot": {"records": []},
    })
    ledger.check(injected_context.get("status") == "ERROR", "public API rejects caller-supplied RMC context", injected_context)
    ledger.check(injected_context.get("reason_code") == "request_contains_unsupported_fields", "RMC injection rejection is typed")

    invalid_requests = (
        None,
        [],
        "not-an-object",
        {},
        {"source_text": 7},
        {"source_text": source, "extra": True},
    )
    for request in invalid_requests:
        response = build_language_core_preview_response(request)
        ledger.check(response.get("status") in {"INVALID", "ERROR"}, f"invalid request rejected: {request!r}", response)
        ledger.check(response.get("endpoint") == ENDPOINT_EXPECTED, f"invalid request endpoint: {request!r}")
        ledger.check(isinstance(response.get("reason_code"), str) and bool(response.get("reason_code")), f"invalid request typed reason: {request!r}", response)
        boundary = _boundary(response)
        ledger.check(boundary.get("preview_only") is True, f"invalid request remains preview only: {request!r}", boundary)
        for name in (
            "model_called",
            "embedding_used",
            "vector_used",
            "similarity_scoring_used",
            "filesystem_write_performed",
            "network_access_performed",
            "memory_write_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
        ):
            ledger.check(boundary.get(name) is False, f"invalid request boundary false {name}: {request!r}", boundary)

    empty = build_language_core_preview_response({"source_text": ""})
    oversized = build_language_core_preview_response({"source_text": "a" * 20_000})
    ledger.check(empty.get("status") in {"HELD", "UNSUPPORTED", "INVALID", "ERROR"}, "empty source fails closed", empty)
    ledger.check(oversized.get("status") in {"HELD", "UNSUPPORTED", "INVALID", "ERROR"}, "oversized source fails closed", oversized)
    ledger.check(_source_text(oversized) in {None, "a" * 20_000}, "oversized source is not silently rewritten")

    boundary = _boundary(first)
    ledger.check(boundary.get("preview_only") is True, "ready response preview only", boundary)
    for name in (
        "normalization_performed",
        "tokenization_performed",
        "model_token_stream_created",
        "subword_token_stream_created",
        "numeric_token_ids_created",
        "model_called",
        "embedding_used",
        "vector_used",
        "similarity_scoring_used",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
    ):
        ledger.check(boundary.get(name) is False, "ready response boundary false " + name, boundary)

    # After import, the adapter must remain usable with every external effect trapped.
    with ExitStack() as stack:
        stack.enter_context(patch.object(builtins, "open", _forbidden))
        stack.enter_context(patch.object(Path, "open", _forbidden))
        stack.enter_context(patch.object(Path, "read_text", _forbidden))
        stack.enter_context(patch.object(Path, "read_bytes", _forbidden))
        stack.enter_context(patch.object(Path, "write_text", _forbidden))
        stack.enter_context(patch.object(Path, "write_bytes", _forbidden))
        stack.enter_context(patch.object(socket, "socket", _forbidden))
        stack.enter_context(patch.object(socket, "create_connection", _forbidden))
        stack.enter_context(patch.object(subprocess, "run", _forbidden))
        stack.enter_context(patch.object(subprocess, "Popen", _forbidden))
        stack.enter_context(patch.object(urllib.request, "urlopen", _forbidden))
        stack.enter_context(patch.object(os, "getenv", _forbidden))
        trapped = build_language_core_preview_response({"source_text": source})
    ledger.check(trapped.get("status") == "PREVIEW_READY", "adapter runs under external-effect traps", trapped)

    # Static route checks avoid importing the monolithic live server.
    main_source = (repo / "main.py").read_text(encoding="utf-8")
    ledger.check('"route_key":"ask_forge_language_core_preview"' in main_source, "route manifest key installed")
    ledger.check(f'"method":"POST","path":"{ENDPOINT_EXPECTED}"' in main_source, "route manifest method and path exact")
    ledger.check(f'_p281_req_path == "{ENDPOINT_EXPECTED}"' in main_source, "POST branch installed")
    segment = _handler_segment(main_source)
    ledger.check("_language_core_preview_api_v1(req)" in segment, "POST branch calls bounded adapter", segment)
    ledger.check("req = None" in segment, "invalid JSON passes typed invalid request", segment)
    ledger.check("str(e)" not in segment and "str(error)" not in segment, "route does not expose raw exception text", segment)
    ledger.check('elif self.path == "/api/operator/ask-forge/math-trace":' in main_source, "existing GP-015 route retained")
    ledger.check("_gp015_ask_forge_math_trace_surface_v1(question)" in main_source, "existing GP-015 adapter retained")

    print("AI.WEB ASK FORGE LANGUAGE CORE PREVIEW ROUTE")
    print(f"checks={ledger.checks}")
    print(f"failures={len(ledger.failures)}")
    print("endpoint=" + ENDPOINT_EXPECTED)
    print("existing_gp015_route_preserved=1")
    print("model_embedding_vector_similarity=0")
    print("filesystem_network_write_tool_action_delivery=0")
    print("RESULT=" + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
