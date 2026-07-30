#!/usr/bin/env python3
"""Strict HTTP-adapter contract tests for the typed RSOC law lab."""

from __future__ import annotations

import builtins
from copy import deepcopy
from pathlib import Path
import socket
import subprocess
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.rsoc_law_lab import (
    ENDPOINT,
    ROUTE_KEY,
    build_rsoc_law_lab_preview_response,
)


checks = 0


def check(value: object, label: str) -> None:
    global checks
    if value is not True:
        raise AssertionError(label)
    checks += 1


def field(suffix: str = "alpha") -> dict[str, object]:
    return {
        "identity_refs": [f"identity:{suffix}"],
        "phase_index": 4,
        "recursion_depth": 2,
        "drift_micro": 200_000,
        "resonance_micro": 800_000,
        "memory_charge_micro": 500_000,
        "entropy_micro": 300_000,
        "loop_ref": f"loop:{suffix}",
        "echo_ancestry_refs": ["ancestry:origin", f"ancestry:{suffix}"],
        "lineage_refs": [f"lineage:{suffix}"],
        "locked": False,
        "archived": False,
        "grace_used": False,
        "revision": 0,
    }


archive_request = {"glyph": "Ĉ", "operands": [field()]}
original_request = deepcopy(archive_request)
archive = build_rsoc_law_lab_preview_response(archive_request)
check(archive_request == original_request, "adapter does not mutate request")
check(archive["status"] == "PREVIEW_READY", "archive typed preview ready")
check(archive["endpoint"] == ENDPOINT, "endpoint exact")
check(ENDPOINT == "/api/rmc/rsoc-law-lab/preview", "endpoint contract stable")
check(archive["route_key"] == ROUTE_KEY == "rsoc_law_lab_preview", "route key exact")
check(archive["read_only"] is True, "adapter read only")
check(len(archive["input_fields"]) == 1, "one typed field constructed")
check(len(archive["output_fields"]) == 1, "one preview successor returned")
check(archive["output_fields"][0]["archived"] is True, "successor archived")
check(archive["input_fields"][0]["archived"] is False, "input remains unchanged")
check(archive["output_fields"][0]["revision"] == 1, "successor revision incremented")
check(archive["receipt"]["result_id"] == archive["result"]["result_id"], "receipt identity exact")
check(archive == build_rsoc_law_lab_preview_response(archive_request), "adapter deterministic")

echo_request = {
    "glyph": "Ê",
    "operands": [field()],
    "expected_ancestry_ref": "ancestry:origin",
}
echo = build_rsoc_law_lab_preview_response(echo_request)
check(echo["status"] == "PREVIEW_READY", "Echo typed preview ready")
check(echo["echo_valid"] is True, "exact Echo ancestry succeeds")
check(not echo["output_fields"], "Echo does not produce successor")
echo_missing = build_rsoc_law_lab_preview_response(
    {**echo_request, "expected_ancestry_ref": "ancestry:missing"}
)
check(echo_missing["status"] == "PREVIEW_READY", "missing ancestry returns typed result")
check(echo_missing["echo_valid"] is False, "missing ancestry exact comparison false")

merge = build_rsoc_law_lab_preview_response(
    {"glyph": "⟁", "operands": [field("alpha"), field("beta")]}
)
check(merge["status"] == "HELD_REFERENCE_CONFLICT", "unadmitted merge held")
check(bool(merge["issue_codes"]), "unadmitted law exposes conflicts")
check(not merge["output_fields"], "unadmitted law has no successor")

lookalike = build_rsoc_law_lab_preview_response(
    {"glyph": "R^", "operands": [field()]}
)
check(lookalike["status"] == "UNSUPPORTED", "lookalike glyph refused")
check(not lookalike["output_fields"], "lookalike creates no output")

invalid_requests = (
    (None, "request_must_be_json_object"),
    ({}, "request_requires_glyph_and_operands"),
    ({"glyph": "Ĉ", "operands": [], "source_text": "archive it"}, "request_contains_unsupported_fields"),
    ({"glyph": "Ĉ", "operands": "field one"}, "operands_must_be_structured_array"),
    ({"glyph": "Ĉ", "operands": [{**field(), "field_id": "caller:id"}]}, "operand_requires_exact_structured_fields"),
    ({"glyph": "Ĉ", "operands": [{**field(), "identity_refs": "identity:alpha"}]}, "operand_reference_list_invalid_or_unbounded"),
    ({"glyph": "Ĉ", "operands": [{**field(), "phase_index": "four"}]}, "operand_value_failed_closed_validation"),
    ({"glyph": "Ê", "operands": [field()]}, "echo_requires_expected_ancestry_ref"),
    ({"glyph": "Ê", "operands": [field()], "expected_ancestry_ref": ""}, "expected_ancestry_ref_invalid_or_unbounded"),
    ({"glyph": "Ĉ", "operands": [field()], "expected_ancestry_ref": "ancestry:origin"}, "request_contains_unsupported_fields"),
    ({"glyph": "⟁", "operands": [field("a"), field("b"), field("c")]}, "operand_count_exceeds_lab_limit"),
)
for request, reason in invalid_requests:
    response = build_rsoc_law_lab_preview_response(request)
    check(response["status"] == "ERROR", f"invalid request held: {reason}")
    check(response["reason_code"] == reason, f"invalid reason exact: {reason}")
    check(response["result"] is None, f"invalid request has no result: {reason}")
    check(not response["output_fields"], f"invalid request has no output: {reason}")

check(len(archive["law_catalog"]) == 10, "all ten exact laws visible")
check(
    {item["glyph"] for item in archive["law_catalog"]}
    == {"⟁", "⧧", "⧒", "⧀", "⧙", "⧜", "χ(t)", "R̂", "Ĉ", "Ê"},
    "catalog glyph identities exact",
)
check(archive["request_contract"]["free_text_fields"] == [], "no free-text request field")
check(archive["request_contract"]["field_id_derived_by_forge"] is True, "caller cannot assign field identity")

for response in (archive, echo, merge, lookalike):
    boundary = response["boundary"]
    check(boundary["structured_field_operands_required"] is True, "structured fields required")
    check(boundary["exact_registered_glyph_required"] is True, "exact glyph required")
    check(boundary["free_text_interpretation_performed"] is False, "no free-text interpretation")
    check(boundary["natural_language_tokenization_performed"] is False, "no natural-language tokenization")
    check(boundary["persistence_performed"] is False, "no persistence")
    check(boundary["runtime_invocation_performed"] is False, "no runtime invocation")
    check(boundary["live_memory_read_performed"] is False, "no live memory read")
    check(boundary["live_memory_write_performed"] is False, "no live memory write")
    check(boundary["tool_routing_performed"] is False, "no tool routing")
    check(boundary["action_performed"] is False, "no action")
    check(boundary["delivery_performed"] is False, "no delivery")
    receipt = response["receipt"]
    check(receipt["runtime_authority"] is False, "no runtime authority")
    check(receipt["memory_authority"] is False, "no memory authority")
    check(receipt["action_authority"] is False, "no action authority")
    check(receipt["delivery_authority"] is False, "no delivery authority")


def forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("external side effect attempted")


with (
    patch.object(builtins, "open", forbidden),
    patch.object(socket, "socket", forbidden),
    patch.object(subprocess, "run", forbidden),
    patch.object(subprocess, "Popen", forbidden),
):
    isolated = build_rsoc_law_lab_preview_response(echo_request)
check(isolated["status"] == "PREVIEW_READY", "adapter executes without external side effects")

print(f"RSOC law lab adapter: {checks} checks passed")
