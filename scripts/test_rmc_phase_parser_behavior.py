#!/usr/bin/env python3
"""Behavioral tests for rmc_engine_v1/phase_parser.py.

Patch 262J1R-Preflight-A.

Run from forge root:
    python scripts/test_rmc_phase_parser_behavior.py
"""

import sys
import os

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FORGE_ROOT)

try:
    from rmc_engine_v1.phase_parser import (
        parse_phase, phase_catalog, phase_parser_boundary
    )
except ImportError as exc:
    print(f"IMPORT_ERROR: {exc}")
    sys.exit(2)

PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, str, str]] = []


def check(name: str, value: bool, detail: str = "") -> None:
    results.append((name, PASS if value else FAIL, detail))


# ── T1: Boundary contract ─────────────────────────────────────────────────────

boundary = phase_parser_boundary()
check("T1_boundary_no_calls_to_main_py", boundary.get("calls_main_py_functions") is False)
check("T1_boundary_source_supplied_by_adapter", boundary.get("source_text_supplied_by_adapter") is True)
check("T1_boundary_no_writes", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
check("T1_boundary_engine_location", "phase_parser" in boundary.get("engine_module_location", ""))


# ── T2: Phase catalog completeness ───────────────────────────────────────────

catalog = phase_catalog()
for expected_phase in ["Φ1", "Φ2", "Φ3", "Φ4", "Φ5", "Φ6", "Φ7", "Φ8", "Φ9"]:
    check(f"T2_catalog_{expected_phase}", expected_phase in catalog, f"catalog has {expected_phase}")
check("T2_catalog_phi5_routing", catalog["Φ5"]["routing"] == "drift_analyzer_required")
check("T2_catalog_phi6_routing", catalog["Φ6"]["routing"] == "correction_engine")
check("T2_catalog_phi8_routing", catalog["Φ8"]["routing"] == "projection_gate")


# ── T3: Admitted parse returns the compatibility structure ───────────────────

result = parse_phase("Inspect the current build status.")
check("T3_returns_dict", isinstance(result, dict))
check("T3_status_ok", result.get("status") == "OK")
check("T3_has_input_event", "input_event" in result)
check("T3_has_phase_state", "phase_state" in result)
check("T3_has_drift_anchor", "drift_foundation_anchor" in result)
check("T3_has_engine_boundary", "engine_boundary" in result)
check("T3_no_writes", result.get("writes_files") is False and result.get("rmc_live_memory_write") is False)
check("T3_no_approved_output", result.get("approved_output") is False)

ps = result.get("phase_state", {})
check("T3_phase_state_has_primary", "phase_primary" in ps)
check("T3_phase_state_has_path", "phase_path_hypothesis" in ps)
check("T3_phase_state_has_confidence", "confidence" in ps)
check("T3_phase_state_has_warnings", "transition_warnings" in ps)

ie = result.get("input_event", {})
check("T3_input_event_has_id", "event_id" in ie)
check("T3_input_event_has_raw", "x_t_raw_input_preview" in ie)
check("T3_input_event_dry_run", ie.get("dry_run") is True)


# ── T4: Deterministic action-profile phase bindings ──────────────────────────

for source, expected_phase in (
    ("Inspect the current build status.", "Φ6"),
    ("Report the repository state.", "Φ8"),
    ("Can you request a read-only audit?", "Φ3"),
):
    bound = parse_phase(source)
    state = bound["phase_state"]
    check(
        f"T4_{expected_phase}_profile_binding",
        bound.get("status") == "OK"
        and state.get("phase_primary") == expected_phase
        and state.get("phase_path_hypothesis") == [expected_phase],
        f"source={source!r}, state={state!r}",
    )


# ── T5: Retired heuristics and unadmitted meanings stop ──────────────────────

unsupported = parse_phase(
    "we need to fix and correct the drift issue before proceeding"
)
check(
    "T5_keywords_do_not_create_phase",
    unsupported.get("status") == "UNRESOLVED"
    and unsupported["phase_state"].get("phase_primary") is None,
)
check(
    "T5_unsupported_routes_to_hold",
    unsupported["phase_state"].get("routing")
    == ["stop_before_rmc_meaning_admission"],
)

ambiguous = parse_phase("Inspect the repository with the audit.")
check(
    "T5_ambiguity_is_held",
    ambiguous.get("status") == "UNRESOLVED"
    and ambiguous.get("reason_code")
    == "LC_RMC_001_AMBIGUOUS_MEANING_HELD"
    and ambiguous["phase_state"].get("linguistic_candidate_count") == 2,
)

negated = parse_phase("Do not verify the packet checksum.")
check(
    "T5_negated_action_is_held",
    negated.get("status") == "UNRESOLVED"
    and negated.get("reason_code") == "LC_RMC_001_NEGATED_ACTION_HELD"
    and negated["phase_state"].get("negated") is True,
)


# ── T6: Empty input handled gracefully ───────────────────────────────────────

result_empty = parse_phase("")
check("T6_empty_input_returns_dict", isinstance(result_empty, dict))
check("T6_empty_input_no_crash", "phase_state" in result_empty)
check(
    "T6_empty_input_fails_closed",
    result_empty.get("status") == "UNRESOLVED"
    and result_empty["phase_state"].get("phase_primary") is None,
)
check(
    "T6_empty_input_no_fallback",
    result_empty.get("fallback_performed") is False,
)


# ── T7: Source metadata passthrough ──────────────────────────────────────────

meta = {"source_kind": "test_fixture", "selector": "test_001"}
result_meta = parse_phase(
    "Inspect the current build status.", source_metadata=meta
)
ie_meta = result_meta.get("input_event", {})
c_t = ie_meta.get("c_t_context_source", {})
check("T7_source_metadata_preserved", c_t.get("source_kind") == "test_fixture")


# ── T8: Only admitted meanings route to the next RMC module ─────────────────

result_report = parse_phase("Report the repository state.")
routing = result_report["phase_state"].get("routing", [])
check(
    "T8_admitted_routing_has_next_module",
    result_report.get("language_core_admitted") is True
    and "projection_gate" in routing
    and "next_module:drift_analyzer" in routing,
    f"routing={routing!r}",
)


# ── Summary ───────────────────────────────────────────────────────────────────

passed = sum(1 for _, v, _ in results if v == PASS)
failed = sum(1 for _, v, _ in results if v == FAIL)

print(f"\nRMC PHASE PARSER BEHAVIORAL TESTS — Patch 262J1R-Preflight-A")
print(f"{'─' * 68}")
for name, verdict, detail in results:
    marker = "✓" if verdict == PASS else "✗"
    line = f"  {marker} [{verdict}] {name}"
    if verdict == FAIL or detail:
        line += f"\n        {detail}"
    print(line)
print(f"{'─' * 68}")
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")

if failed == 0:
    print("\n  RESULT: phase_parser_behavior_tests_pass=True")
    sys.exit(0)
else:
    print("\n  RESULT: phase_parser_behavior_tests_pass=False")
    sys.exit(1)
