#!/usr/bin/env python3
"""Behavioral tests for rmc_engine_v1/drift_engine.py — Patch 262J1R-Preflight-B1.

Required test cases (from patch spec):
  T1  — boundary contract (mode label, scoring mode, no writes)
  T2  — syntactic firewall: random malformed junk → high syntactic drift
  T3  — bypass violation: "bypass correction and naming and project now" → circuit breaker
  T4  — negation awareness: "do not bypass correction" → NOT circuit breaker
  T5  — lawful wide path (correct → name → validate → project later) NOT punished
  T6  — Phi5→Phi8 hard-triggers circuit breaker
  T7  — circuit_breaker=True forces coherence_score=0.0 (end-to-end)
  T8  — transition_legality: wide span without violations has low delta_phi
  T9  — sigma_res includes trace instability components (not just confidence spread)
  T10 — thresholds labeled as rmc_preflight_conservative
  T11 — evolutionary drift never dominates as danger signal
  T12 — unsafe markers in source text → syntactic critical
  T13 — clean minimal report does not trigger circuit breaker
  T14 — no writes in any code path

Run from forge root:
    python scripts/test_rmc_drift_engine_behavior.py
"""

import sys
import os
import inspect

FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FORGE_ROOT)

try:
    from rmc_engine_v1.drift_engine import (
        analyze_drift, drift_engine_boundary, drift_taxonomy,
        _detect_bypass_violations, _compute_transition_legality,
        _compute_trace_instability, _extract_features,
        THRESHOLDS, ENGINE_MODE,
    )
    from rmc_engine_v1.coherence_math import score_candidate
except ImportError as exc:
    print(f"IMPORT_ERROR: {exc}")
    sys.exit(2)

PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, str, str]] = []

def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, PASS if ok else FAIL, detail))


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _report(path=None, confidence=0.75, source="test input",
            warnings=None, candidates=None, primary=None):
    path = path or ["Φ1", "Φ3"]
    primary = primary or (path[0] if path else "Φ1")
    return {
        "input_event": {"event_id": "t", "x_t_raw_input_preview": source, "dry_run": True},
        "phase_state": {
            "phase_primary": primary,
            "phase_path_hypothesis": path,
            "confidence": confidence,
            "phase_candidates": candidates or [{"phase": p, "confidence": confidence} for p in path[:3]],
            "transition_warnings": warnings or [],
            "routing": [],
        },
    }

def _skip_report():
    return _report(
        path=["Φ5", "Φ8"], confidence=0.30,
        source="drift collapse project publish output",
        warnings=[{"type": "phase_skip_projection_risk", "from": "Φ5", "to": "Φ8", "law": "test"}],
    )

def _lawful_wide_report():
    """Wide phase span (Φ1→Φ3→Φ6→Φ7→Φ9) but all transitions are LAWFUL."""
    return _report(
        path=["Φ1", "Φ3", "Φ6", "Φ7", "Φ9"],
        confidence=0.82,
        source="build desire fix correct align name define close seal archive done",
    )

def _candidate_from_drift(drift_report):
    return {
        "candidate_id": "test_001",
        "title": "Test candidate",
        "confidence": 0.90,
        "required_limitations": ["dry_run_only"],
        "phase_target": "Φ5",
        "drift_posture": "test",
    }, {"candidate_set_id": "test_set", "source_drift_report": drift_report}


# ── T1: Boundary contract ─────────────────────────────────────────────────────

boundary = drift_engine_boundary()
check("T1_engine_mode_is_structural_contract",
      boundary.get("engine_mode") == "structural_contract_drift_analysis",
      f"mode={boundary.get('engine_mode')!r}")
check("T1_scoring_mode_structural",    boundary.get("scoring_mode") == "structural_contract_drift_analysis")
check("T1_keyword_counting_false",     boundary.get("keyword_counting_mode") is False)
check("T1_not_synthetic",              boundary.get("synthetic_taxonomy_mode") is False)
check("T1_no_writes",                  boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
check("T1_design_sources_present",     len(boundary.get("design_sources", [])) >= 3)
check("T1_sigma_res_explains_instability", "trace_instability" in boundary.get("sigma_res_measures", ""))
check("T1_delta_phi_explains_legality",    "transition_legality" in boundary.get("delta_phi_measures", ""))
check("T1_thresholds_labeled_conservative",
      boundary.get("thresholds", {}).get("label") == "rmc_preflight_conservative",
      f"threshold label={boundary.get('thresholds', {}).get('label')!r}")
check("T1_bypass_detection_negation_aware",
      "do not bypass correction" in boundary.get("bypass_detection", ""),
      f"bypass_detection={boundary.get('bypass_detection')!r}")


# ── T2: Syntactic firewall — malformed junk ───────────────────────────────────

# Random binary-looking junk with very low entropy (repeated chars) and unsafe markers
junk_text = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + "open(" * 5
junk_report = _report(source=junk_text, path=[], confidence=0.0, primary="", candidates=[])
result_junk = analyze_drift(junk_report)
syn_event = next((e for e in result_junk["drift_classes"] if e["drift_key"] == "syntactic"), {})
check("T2_malformed_junk_raises_syntactic",
      syn_event.get("score", 0) >= 0.55,
      f"syntactic score={syn_event.get('score')!r}")
check("T2_malformed_junk_syntactic_not_none",
      syn_event.get("severity") in ("high", "critical"),
      f"severity={syn_event.get('severity')!r}")

# Balanced braces test: no junk, balanced — should NOT raise syntactic dramatically
clean_src = "{ 'key': 'value', 'other': [1, 2, 3] } normal text here"
clean_brace = _report(source=clean_src)
result_brace = analyze_drift(clean_brace)
brace_syn = next((e for e in result_brace["drift_classes"] if e["drift_key"] == "syntactic"), {})
check("T2_balanced_braces_not_flagged", brace_syn.get("score", 1.0) < 0.40,
      f"balanced brace syntactic score={brace_syn.get('score')!r}")

# Unsafe markers
unsafe_text = "we need to use os.system('ls') and subprocess.run() to do this"
unsafe_report = _report(source=unsafe_text)
result_unsafe = analyze_drift(unsafe_report)
unsafe_syn = next((e for e in result_unsafe["drift_classes"] if e["drift_key"] == "syntactic"), {})
check("T2_unsafe_markers_raise_syntactic",
      unsafe_syn.get("score", 0) >= 0.55,
      f"unsafe markers syntactic score={unsafe_syn.get('score')!r}")


# ── T3: Bypass violation → circuit breaker ────────────────────────────────────

bypass_text = "bypass correction and naming and project now"
bypass_report = _report(
    source=bypass_text,
    path=["Φ3", "Φ8"],
    confidence=0.5,
)
result_bypass = analyze_drift(bypass_report)
cb_bypass = result_bypass.get("circuit_breaker", {})
check("T3_bypass_violation_triggers_circuit_breaker",
      cb_bypass.get("triggered") is True,
      f"triggered={cb_bypass.get('triggered')!r}, reason={cb_bypass.get('reason')!r}")
check("T3_bypass_violations_listed",
      bool(result_bypass.get("bypass_violations_detected")),
      f"violations={result_bypass.get('bypass_violations_detected')!r}")
check("T3_bypass_projection_blocked",
      result_bypass.get("projection_status") == "blocked_circuit_breaker")
check("T3_bypass_trigger_documented",
      cb_bypass.get("triggers", {}).get("bypass_violations_present") is True)


# ── T4: Negation awareness — "do not bypass correction" is NOT a violation ────

negated_text = "we must do not bypass correction and we must not skip naming under any circumstances"
negated_report = _report(
    source=negated_text,
    path=["Φ1", "Φ3", "Φ6", "Φ7"],
    confidence=0.80,
)
result_negated = analyze_drift(negated_report)
cb_negated = result_negated.get("circuit_breaker", {})
bypass_violations_negated = result_negated.get("bypass_violations_detected", [])
check("T4_negated_bypass_no_violations",
      len(bypass_violations_negated) == 0,
      f"violations_found={bypass_violations_negated!r}")
check("T4_negated_bypass_no_circuit_breaker",
      cb_negated.get("triggered") is False,
      f"triggered={cb_negated.get('triggered')!r}")

# Also test direct bypass detector function
direct_bypass = _detect_bypass_violations("bypass correction now")
direct_negated = _detect_bypass_violations("do not bypass correction")
check("T4_direct_bypass_detected", len(direct_bypass) > 0, f"violations={direct_bypass!r}")
check("T4_direct_negated_not_detected", len(direct_negated) == 0, f"violations={direct_negated!r}")


# ── T5: Lawful wide path not punished ─────────────────────────────────────────

result_lawful = analyze_drift(_lawful_wide_report())
delta_phi_lawful = result_lawful.get("epsilon_s", {}).get("phase_deviation_normalized", 1.0)
violations_lawful = result_lawful.get("transition_violations", [])
cb_lawful = result_lawful.get("circuit_breaker", {})
check("T5_lawful_wide_path_low_delta_phi",
      delta_phi_lawful < 0.35,
      f"delta_phi={delta_phi_lawful!r} (wide span but all transitions lawful)")
check("T5_lawful_wide_path_no_violations",
      len(violations_lawful) == 0,
      f"violations={violations_lawful!r}")
check("T5_lawful_wide_path_no_circuit_breaker",
      cb_lawful.get("triggered") is False,
      f"triggered={cb_lawful.get('triggered')!r}")
check("T5_lawful_wide_path_projection_not_hard_blocked",
      result_lawful.get("projection_status") != "blocked_circuit_breaker",
      f"status={result_lawful.get('projection_status')!r}")


# ── T6: Phi5→Phi8 hard-triggers circuit breaker ───────────────────────────────

result_skip = analyze_drift(_skip_report())
cb_skip = result_skip.get("circuit_breaker", {})
check("T6_phase_skip_triggers_circuit_breaker",
      cb_skip.get("triggered") is True,
      f"triggered={cb_skip.get('triggered')!r}, reason={cb_skip.get('reason')!r}")
check("T6_phase_skip_trigger_documented",
      cb_skip.get("triggers", {}).get("phase_5_to_8_projection_skip") is True)
check("T6_phase_skip_projection_blocked",
      result_skip.get("projection_status") == "blocked_circuit_breaker")

# Verify directly via transition legality function
features_skip = _extract_features(_skip_report())
dp_skip, viol_skip = _compute_transition_legality(features_skip)
check("T6_transition_legality_detects_skip",
      dp_skip > 0.0,
      f"delta_phi={dp_skip!r}, violations={[v['violation'] for v in viol_skip]!r}")


# ── T7: circuit_breaker=True forces coherence_score=0.0 (end-to-end) ─────────

drift_with_cb = analyze_drift(_skip_report())
cand, cand_report = _candidate_from_drift(drift_with_cb)
sc = score_candidate(cand, cand_report)

check("T7_circuit_breaker_from_drift_reaches_math_kernel",
      sc.get("math_terms", {}).get("circuit_breaker") is True,
      f"cb_in_math_terms={sc.get('math_terms', {}).get('circuit_breaker')!r}")
check("T7_circuit_breaker_forces_coherence_score_zero",
      sc.get("coherence_score") == 0.0,
      f"coherence_score={sc.get('coherence_score')!r}")
check("T7_circuit_breaker_blocks_manifest",
      sc.get("manifest_gate", {}).get("allowed") is False)
check("T7_circuit_breaker_blocks_projection",
      sc.get("projection_allowed") is False)
check("T7_circuit_breaker_blocks_memory_write",
      sc.get("memory_write_allowed") is False)
check("T7_raw_coherence_preserved",
      "raw_coherence_before_circuit_override" in sc.get("score_components", {}))


# ── T8: Transition legality delta_phi — legal wide span ───────────────────────

# Phi1→Phi3→Phi6→Phi7→Phi9 : span=8, all legal
features_lawful = _extract_features(_lawful_wide_report())
dp_lawful, viol_lawful = _compute_transition_legality(features_lawful)
check("T8_lawful_wide_span_zero_delta_phi",
      dp_lawful == 0.0,
      f"delta_phi={dp_lawful!r}, violations={viol_lawful!r}")

# Phi1→Phi8 without correction/naming: should have high delta_phi
short_bad = _report(path=["Φ1", "Φ8"], confidence=0.5)
features_bad = _extract_features(short_bad)
dp_bad, viol_bad = _compute_transition_legality(features_bad)
check("T8_illegal_path_high_delta_phi",
      dp_bad >= 0.60,
      f"Phi1->Phi8 without gates: delta_phi={dp_bad!r}")


# ── T9: sigma_res includes trace instability components ──────────────────────

# High-conflict report: two candidates with nearly identical confidence
conflict_candidates = [
    {"phase": "Φ3", "confidence": 0.70},
    {"phase": "Φ5", "confidence": 0.68},  # very close → phase conflict
]
conflict_report = _report(
    path=["Φ3", "Φ5"],
    confidence=0.70,
    candidates=conflict_candidates,
)
sigma_conflict, detail_conflict = _compute_trace_instability(conflict_report)
check("T9_phase_conflict_raises_sigma_res",
      detail_conflict.get("phase_conflict", 0) > 0,
      f"phase_conflict={detail_conflict.get('phase_conflict')!r}")

# Loop mismatch: primary is Phi5 (routing=drift_analyzer_required) but routing list is empty
loop_mismatch_report = _report(path=["Φ5"], confidence=0.6, primary="Φ5")
sigma_mismatch, detail_mismatch = _compute_trace_instability(loop_mismatch_report)
check("T9_loop_mismatch_raises_sigma_res",
      detail_mismatch.get("active_loop_mismatch", 0) > 0,
      f"loop_mismatch={detail_mismatch.get('active_loop_mismatch')!r}")

# Clean report: no conflict, good routing → sigma_res should stay modest
clean_r = _report(path=["Φ1", "Φ3", "Φ6", "Φ7"], confidence=0.85)
sigma_clean, detail_clean = _compute_trace_instability(clean_r)
check("T9_clean_report_modest_sigma_res",
      sigma_clean <= 0.35,
      f"clean sigma_res={sigma_clean!r}")


# ── T10: Thresholds labeled correctly ─────────────────────────────────────────

check("T10_thresholds_label_conservative",
      THRESHOLDS.get("label") == "rmc_preflight_conservative")
check("T10_thresholds_have_note",
      "task-sensitive" in THRESHOLDS.get("note", "") or "theta" in THRESHOLDS.get("note", "").lower())
check("T10_chi_t_threshold_labeled",
      "chi_t_correction_required" in THRESHOLDS)
check("T10_circuit_breaker_threshold_labeled",
      "circuit_breaker" in THRESHOLDS)

eps_dict = analyze_drift(_report())["epsilon_s"]
check("T10_threshold_label_in_output",
      eps_dict.get("thresholds", {}).get("label") == "rmc_preflight_conservative")


# ── T11: Evolutionary drift capped ───────────────────────────────────────────

result_evo = analyze_drift(_report(
    path=["Φ1","Φ3","Φ6","Φ7"], confidence=0.80,
    source="novel hypothesis branch prototype draft candidate idea framework",
))
evo = next((e for e in result_evo["drift_classes"] if e["drift_key"] == "evolutionary"), {})
check("T11_evolutionary_capped_at_0_55", evo.get("score", 1.0) <= 0.55)
destructive = [e for e in result_evo["drift_classes"] if e["drift_key"] != "evolutionary"]
max_dest = max((e.get("score", 0) for e in destructive), default=0)
check("T11_evolutionary_not_highest", evo.get("score", 1.0) <= max_dest or max_dest < 0.10)


# ── T12: Unsafe markers → syntactic critical ─────────────────────────────────

result_unsafe2 = analyze_drift(_report(
    source="subprocess.run(['rm', '-rf', '/'], shell=True) and eval(x) and exec(cmd)",
))
syn_unsafe = next((e for e in result_unsafe2["drift_classes"] if e["drift_key"] == "syntactic"), {})
check("T12_unsafe_shell_raises_syntactic_high",
      syn_unsafe.get("score", 0) >= 0.65,
      f"syntactic score={syn_unsafe.get('score')!r}")
check("T12_unsafe_markers_in_evidence",
      any("unsafe" in ev for ev in syn_unsafe.get("evidence", [])),
      f"evidence={syn_unsafe.get('evidence')!r}")


# ── T13: Clean minimal report no circuit breaker ─────────────────────────────

result_clean = analyze_drift(_report(
    path=["Φ1","Φ3","Φ6","Φ7"], confidence=0.85,
    source="build fix verify correct name define",
))
cb_clean = result_clean.get("circuit_breaker", {})
check("T13_clean_report_no_circuit_breaker",
      cb_clean.get("triggered") is False,
      f"triggered={cb_clean.get('triggered')!r}")
check("T13_clean_trigger_details_show_false",
      cb_clean.get("triggers", {}).get("phase_5_to_8_projection_skip") is False
      and cb_clean.get("triggers", {}).get("bypass_violations_present") is False)


# ── T14: No writes in any code path ──────────────────────────────────────────

import rmc_engine_v1.drift_engine as _dem
src = inspect.getsource(_dem)
check("T14_no_subprocess_import", "import subprocess" not in src and "subprocess.call(" not in src and "subprocess.run(" not in src, "no actual subprocess calls (detection strings are string literals)")
check("T14_no_open_write",  not any('"w"' in line and "open(" in line for line in src.splitlines()))
check("T14_result_no_writes",
      result_clean.get("writes_files") is False
      and result_clean.get("rmc_live_memory_write") is False
      and result_clean.get("approved_output") is False)


# ── Summary ───────────────────────────────────────────────────────────────────

passed = sum(1 for _, v, _ in results if v == PASS)
failed = sum(1 for _, v, _ in results if v == FAIL)

print(f"\nRMC DRIFT ENGINE BEHAVIORAL TESTS — Patch 262J1R-Preflight-B1")
print(f"{'─' * 72}")
for name, verdict, detail in results:
    marker = "✓" if verdict == PASS else "✗"
    line = f"  {marker} [{verdict}] {name}"
    if verdict == FAIL or detail:
        line += f"\n        {detail}"
    print(line)
print(f"{'─' * 72}")
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")

if failed == 0:
    print("\n  RESULT: drift_engine_B1_behavior_tests_pass=True")
    sys.exit(0)
else:
    print("\n  RESULT: drift_engine_B1_behavior_tests_pass=False")
    sys.exit(1)
