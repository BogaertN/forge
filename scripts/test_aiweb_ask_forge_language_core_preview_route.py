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
    import rmc_engine_v1.meaning_compiler_preview as preview_adapter
    from aiweb_language_core_bootstrap.meaning_compiler_preview import (
        meaning_compiler_preview_boundary,
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
    provider = first.get("trusted_rmc_provider") or {}
    ledger.check(provider.get("load_status") in {"TRUSTED_EMPTY", "TRUSTED_STRUCTURED"}, "trusted exact-ID RMC provider visible", provider)
    ledger.check(provider.get("tokenization_used") is False, "RMC provider uses no tokenization", provider)
    ledger.check(provider.get("vector_used") is False, "RMC provider uses no vectors", provider)
    council = first.get("operator_council") or {}
    ledger.check(council.get("status") in {"HOLD_FOR_EVIDENCE", "RECOMMEND_FOR_OPERATOR_REVIEW"}, "Council disposition visible", council)
    ledger.check(council.get("recommendation_only") is True, "Council is recommendation only", council)
    council_result = council.get("result") or {}
    recommendation = council_result.get("recommendation") or {}
    ledger.check(recommendation.get("executable") is False, "Council recommendation is not executable", recommendation)
    ledger.check(recommendation.get("authoritative") is False, "Council recommendation is not authoritative", recommendation)
    ledger.check(any(stage.get("label") == "Operator Council recommendation" for stage in first.get("stages", ())), "Council stage appears in Ask Forge trace", first.get("stages"))
    surface_boundary = _boundary(first)
    ledger.check(surface_boundary.get("compiler_boundary_id") == meaning_compiler_preview_boundary().boundary_id, "surface cites compiler-only boundary", surface_boundary)
    ledger.check(surface_boundary.get("boundary_id") != surface_boundary.get("compiler_boundary_id"), "surface boundary has its own content identity", surface_boundary)
    integrated_receipt = first.get("receipt") or {}
    ledger.check(integrated_receipt.get("integrated_result_ref") == first.get("result_id"), "integrated receipt binds surface result", integrated_receipt)
    ledger.check(integrated_receipt.get("compiler_result_ref") == first.get("compiler_result_id"), "integrated receipt binds compiler result", integrated_receipt)

    exact_definition = build_language_core_preview_response(
        {"source_text": "What does language core mean?"}
    )
    ledger.check(
        exact_definition.get("status") == "PREVIEW_READY",
        "exact governed definition remains independently selectable",
        exact_definition,
    )
    ledger.check(
        (exact_definition.get("rmc_context") or {}).get("context_used_for_selection")
        is False,
        "exact governed definition does not need RMC to select its unique meaning",
        exact_definition.get("rmc_context"),
    )
    definition_selected = (
        (exact_definition.get("selected_meaning") or {}).get("meaning_candidate_id")
    )
    definition_support = [
        item
        for item in exact_definition.get("rmc_exact_identity_resonances", ())
        if item.get("meaning_candidate_ref") == definition_selected
        and bool(item.get("exact_semantic_contract_refs"))
    ]
    if definition_support:
        definition_council = exact_definition.get("operator_council") or {}
        definition_recommendation = (
            (definition_council.get("result") or {}).get("recommendation") or {}
        )
        ledger.check(
            provider.get("load_status") == "TRUSTED_STRUCTURED",
            "exact governed definition support originates in structured RMC",
            provider,
        )
        ledger.check(
            all(item.get("approximate_match_used") is False for item in definition_support),
            "exact governed definition support uses no approximate match",
            definition_support,
        )
        ledger.check(
            definition_council.get("status") == "RECOMMEND_FOR_OPERATOR_REVIEW"
            and definition_council.get("recommendation_only") is True,
            "promoted exact definition reaches recommendation-only review",
            definition_council,
        )
        ledger.check(
            definition_recommendation.get("executable") is False
            and definition_recommendation.get("authoritative") is False,
            "promoted exact definition remains non-executable and non-authoritative",
            definition_recommendation,
        )
    else:
        ledger.check(
            (exact_definition.get("operator_council") or {}).get("status")
            == "HOLD_FOR_EVIDENCE",
            "unpromoted exact definition remains held for RMC evidence",
            exact_definition.get("operator_council"),
        )

    ambiguous = build_language_core_preview_response({"source_text": "What does core mean?"})
    if ambiguous.get("status") == "PREVIEW_READY":
        # A trusted structured provider may resolve this declared polysemy, but
        # only through one complete exact semantic-contract match.  Partial
        # concept/relation overlap remains evidence-only and cannot select.
        ledger.check(
            provider.get("load_status") == "TRUSTED_STRUCTURED",
            "core ambiguity can resolve only with structured trusted RMC",
            provider,
        )
        ledger.check(
            ambiguous.get("reason_code") == "unique_exact_rmc_resonance",
            "structured core resolution has the exact-RMC reason",
            ambiguous,
        )
        selected = ambiguous.get("selected_meaning") or {}
        selected_ref = selected.get("meaning_candidate_id")
        context = ambiguous.get("rmc_context") or {}
        selection_resonances = [
            item
            for item in context.get("resonances", ())
            if item.get("meaning_candidate_ref") == selected_ref
            and item.get("used_for_selection") is True
            and bool(item.get("exact_semantic_contract_refs"))
        ]
        ledger.check(bool(selected_ref), "structured core resolution exposes selected meaning", selected)
        ledger.check(
            context.get("context_used_for_selection") is True,
            "structured core resolution reports RMC selection influence",
            context,
        )
        ledger.check(
            len(selection_resonances) == 1,
            "exactly one complete semantic-contract resonance selects core",
            context,
        )
        ledger.check(
            context.get("memory_write_performed") is False,
            "core resolution performs no memory write",
            context,
        )
        exact_support = [
            item
            for item in ambiguous.get("rmc_exact_identity_resonances", ())
            if item.get("meaning_candidate_ref") == selected_ref
            and bool(item.get("exact_semantic_contract_refs"))
        ]
        ledger.check(
            bool(exact_support)
            and all(item.get("approximate_match_used") is False for item in exact_support)
            and all(item.get("used_for_selection") is False for item in exact_support),
            "external exact-RMC evidence is exact and recommendation-only",
            exact_support,
        )
        ambiguous_council = ambiguous.get("operator_council") or {}
        ambiguous_recommendation = (
            (ambiguous_council.get("result") or {}).get("recommendation") or {}
        )
        ledger.check(
            ambiguous_council.get("status") == "RECOMMEND_FOR_OPERATOR_REVIEW"
            and ambiguous_council.get("recommendation_only") is True,
            "RMC-resolved core reaches recommendation-only Council review",
            ambiguous_council,
        )
        ledger.check(
            ambiguous_recommendation.get("executable") is False
            and ambiguous_recommendation.get("authoritative") is False,
            "RMC-resolved core grants no execution or authority",
            ambiguous_recommendation,
        )
    else:
        ledger.check(ambiguous.get("status") == "HELD", "unsupported core ambiguity remains held", ambiguous)
        ledger.check(
            (ambiguous.get("rmc_context") or {}).get("context_used_for_selection") is False,
            "held core ambiguity reports no RMC selection influence",
            ambiguous.get("rmc_context"),
        )
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
        invalid_council = response.get("operator_council") or {}
        ledger.check(invalid_council.get("status") == "NOT_CONVENED", f"invalid request never convenes Council: {request!r}", invalid_council)
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
    ledger.check(
        boundary.get("filesystem_read_performed")
        is provider.get("filesystem_read_performed"),
        "surface filesystem-read fact matches trusted provider load",
        {"boundary": boundary, "provider": provider},
    )
    ledger.check(
        boundary.get("memory_read_performed")
        is provider.get("memory_read_performed"),
        "surface memory-read fact matches trusted provider load",
        {"boundary": boundary, "provider": provider},
    )
    if provider.get("load_status") == "TRUSTED_STRUCTURED":
        ledger.check(
            provider.get("stable_record_count", 0) + provider.get("live_record_count", 0) > 0
            and provider.get("filesystem_read_performed") is True
            and provider.get("memory_read_performed") is True,
            "structured provider reports its immutable snapshot read",
            provider,
        )
    else:
        ledger.check(
            provider.get("stable_record_count") == 0
            and provider.get("live_record_count") == 0
            and provider.get("memory_read_performed") is False,
            "empty provider reports no loaded memory records",
            provider,
        )
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
        "filesystem_write_performed",
        "network_access_performed",
        "environment_access_performed",
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

    with patch.object(preview_adapter, "evaluate_exact_identity_resonance", side_effect=ValueError("forced")):
        contained_rmc_failure = build_language_core_preview_response({"source_text": source})
    ledger.check(contained_rmc_failure.get("status") == "ERROR", "RMC post-compile exception contained", contained_rmc_failure)
    ledger.check(contained_rmc_failure.get("reason_code") == "rmc_exact_resonance_failed_closed", "RMC post-compile failure typed", contained_rmc_failure)
    with patch.object(preview_adapter, "build_operator_council_preview", side_effect=ValueError("forced")):
        contained_council_failure = build_language_core_preview_response({"source_text": source})
    ledger.check(contained_council_failure.get("status") == "ERROR", "Council post-compile exception contained", contained_council_failure)
    ledger.check(contained_council_failure.get("reason_code") == "operator_council_preview_failed_closed", "Council post-compile failure typed", contained_council_failure)
    with patch.object(preview_adapter, "build_operator_council_preview", return_value=None):
        invalid_council_result = build_language_core_preview_response({"source_text": source})
    ledger.check(invalid_council_result.get("status") == "ERROR", "invalid Council return contained", invalid_council_result)
    ledger.check(invalid_council_result.get("reason_code") == "operator_council_preview_invalid_result", "invalid Council return typed", invalid_council_result)
    with patch.object(preview_adapter, "_integrated_result_and_receipt", side_effect=ValueError("forced")):
        contained_receipt_failure = build_language_core_preview_response({"source_text": source})
    ledger.check(contained_receipt_failure.get("status") == "ERROR", "surface receipt exception contained", contained_receipt_failure)
    ledger.check(contained_receipt_failure.get("reason_code") == "language_core_surface_receipt_failed_closed", "surface receipt failure typed", contained_receipt_failure)

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
