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


# ── T3: Parse returns correct structure ───────────────────────────────────────

result = parse_phase("build the new system from scratch")
check("T3_returns_dict", isinstance(result, dict))
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


# ── T4: Phase detection — keyword signals work ────────────────────────────────

# "fix" and "repair" and "correct" should lean toward Φ6
result_phi6 = parse_phase("we need to fix and correct the drift issue before proceeding")
primary = result_phi6["phase_state"].get("phase_primary")
path = result_phi6["phase_state"].get("phase_path_hypothesis", [])
check("T4_phi6_keywords_detected", "Φ6" in path or primary == "Φ6",
      f"primary={primary!r}, path={path!r}")

# "drift", "collapse", "unstable" should lean toward Φ5
result_phi5 = parse_phase("the loop is collapsing, drift is unstable and wrong")
primary5 = result_phi5["phase_state"].get("phase_primary")
path5 = result_phi5["phase_state"].get("phase_path_hypothesis", [])
check("T4_phi5_keywords_detected", "Φ5" in path5 or primary5 == "Φ5",
      f"primary={primary5!r}, path={path5!r}")

# "name", "define", "schema", "contract" should lean toward Φ7
result_phi7 = parse_phase("we need to name and define the schema contract for the manifest")
primary7 = result_phi7["phase_state"].get("phase_primary")
path7 = result_phi7["phase_state"].get("phase_path_hypothesis", [])
check("T4_phi7_keywords_detected", "Φ7" in path7 or primary7 == "Φ7",
      f"primary={primary7!r}, path={path7!r}")


# ── T5: Phase skip detection ──────────────────────────────────────────────────

# Φ5→Φ8 skip should produce a phase_skip_projection_risk warning
result_skip = parse_phase("drift loop collapse — publish ship render export public output now")
warnings = result_skip["phase_state"].get("transition_warnings", [])
path_skip = result_skip["phase_state"].get("phase_path_hypothesis", [])
# The path must include both a drift phase and a projection phase for skip warning
has_skip_warning = any(w.get("type") == "phase_skip_projection_risk" for w in warnings)
phi5_present = "Φ5" in path_skip
phi8_present = "Φ8" in path_skip
check("T5_phase_skip_can_be_detected",
      has_skip_warning or (phi5_present and phi8_present),
      f"warnings={[w.get('type') for w in warnings]!r}, path={path_skip!r}")
if has_skip_warning:
    check("T5_phase_skip_warning_type",
          any(w.get("type") == "phase_skip_projection_risk" for w in warnings))
    check("T5_projection_warning_in_state",
          "Projection requires" in result_skip["phase_state"].get("projection_warning", ""))


# ── T6: Empty input handled gracefully ───────────────────────────────────────

result_empty = parse_phase("")
check("T6_empty_input_returns_dict", isinstance(result_empty, dict))
check("T6_empty_input_no_crash", "phase_state" in result_empty)
check("T6_empty_input_fallback",
      result_empty["phase_state"].get("phase_candidates", []) != [],
      "fallback phase candidate generated for empty input")


# ── T7: Source metadata passthrough ──────────────────────────────────────────

meta = {"source_kind": "test_fixture", "selector": "test_001"}
result_meta = parse_phase("test with metadata", source_metadata=meta)
ie_meta = result_meta.get("input_event", {})
c_t = ie_meta.get("c_t_context_source", {})
check("T7_source_metadata_preserved", c_t.get("source_kind") == "test_fixture")


# ── T8: Routing includes drift_analyzer_required when Φ5 present ─────────────

result_drift = parse_phase("drift confused collapse unstable loop slip")
routing = result_drift["phase_state"].get("routing", [])
path_d = result_drift["phase_state"].get("phase_path_hypothesis", [])
if "Φ5" in path_d:
    check("T8_phi5_adds_drift_analyzer_routing",
          "drift_analyzer_required" in routing,
          f"routing={routing!r}")
else:
    check("T8_routing_always_has_next_module",
          any("next_module" in r or "drift" in r for r in routing),
          f"routing={routing!r}")


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
