#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B1 — Drift Engine Hardening.

Run from forge root:
    python scripts/patch262J1R_preflight_B1_verify.py

Expected: PATCH_262J1R_PREFLIGHT_B1_VERIFY_OK
"""
import sys, os, subprocess, inspect
FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FORGE_ROOT)
PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, str, str]] = []
def check(n: str, ok: bool, d: str = "") -> None:
    results.append((n, PASS if ok else FAIL, d))

# ── 1. Engine mode and boundary ───────────────────────────────────────────────
try:
    from rmc_engine_v1.drift_engine import (
        analyze_drift, drift_engine_boundary, drift_taxonomy, THRESHOLDS, ENGINE_MODE
    )
    check("drift_engine_importable", True)
except ImportError as e:
    check("drift_engine_importable", False, str(e)); sys.exit(1)

boundary = drift_engine_boundary()
check("engine_mode_structural_contract",
      ENGINE_MODE == "structural_contract_drift_analysis" and boundary.get("engine_mode") == ENGINE_MODE)
check("keyword_counting_false", boundary.get("keyword_counting_mode") is False)
check("synthetic_mode_false",   boundary.get("synthetic_taxonomy_mode") is False)
check("no_writes",              boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
check("sigma_res_explains_instability", "trace_instability" in boundary.get("sigma_res_measures", ""))
check("delta_phi_explains_legality",    "transition_legality" in boundary.get("delta_phi_measures", ""))
check("thresholds_conservative",        THRESHOLDS.get("label") == "rmc_preflight_conservative")
check("thresholds_note_present",        bool(THRESHOLDS.get("note")))
check("bypass_negation_aware",          "do not bypass correction" in boundary.get("bypass_detection", ""))
check("seven_taxonomy_categories",      len(drift_taxonomy()) == 7)

# ── 2. Syntactic firewall ─────────────────────────────────────────────────────
junk_report = {"input_event": {"event_id": "v", "x_t_raw_input_preview": "aaaaaa" * 10 + "open(" * 3, "dry_run": True},
               "phase_state": {"phase_primary": "", "phase_path_hypothesis": [], "confidence": 0.0, "phase_candidates": [], "transition_warnings": [], "routing": []}}
r_junk = analyze_drift(junk_report)
syn_junk = next((e for e in r_junk["drift_classes"] if e["drift_key"] == "syntactic"), {})
check("syntactic_firewall_detects_junk", syn_junk.get("score", 0) >= 0.55,
      f"junk syntactic score={syn_junk.get('score')!r}")

# ── 3. Bypass detection + negation ───────────────────────────────────────────
from rmc_engine_v1.drift_engine import _detect_bypass_violations
v_bypass  = _detect_bypass_violations("bypass correction and project now")
v_negated = _detect_bypass_violations("do not bypass correction at all")
check("bypass_violation_detected",       len(v_bypass) > 0,  f"violations={v_bypass!r}")
check("negated_bypass_not_detected",     len(v_negated) == 0, f"violations={v_negated!r}")

r_byp = analyze_drift({"input_event": {"event_id": "v", "x_t_raw_input_preview": "bypass correction and name and project now", "dry_run": True},
                        "phase_state": {"phase_primary": "Φ3", "phase_path_hypothesis": ["Φ3","Φ8"], "confidence": 0.5, "phase_candidates": [], "transition_warnings": [], "routing": []}})
check("bypass_triggers_circuit_breaker", r_byp.get("circuit_breaker", {}).get("triggered") is True)

# ── 4. Transition legality delta_phi ─────────────────────────────────────────
from rmc_engine_v1.drift_engine import _compute_transition_legality, _extract_features
def _mk_features(path, has6=False, has7=False, has8=False, warnings=None):
    nums = []
    for p in path:
        try: nums.append(int(p.replace("Φ","").replace("phi","").strip()))
        except: pass
    return {"path": path, "nums": sorted(set(nums)), "nums_all": nums,
            "warnings": warnings or [],
            "has_phi5": 5 in nums, "has_phi6": 6 in nums, "has_phi7": 7 in nums,
            "has_phi8_or_9": any(n >= 8 for n in nums), "has_phi9": 9 in nums,
            "has_projection_skip": any(w.get("type") == "phase_skip_projection_risk" for w in (warnings or [])),
            "has_any_skip": bool(warnings), "repeated_phases": False,
            "phase_span": (max(nums)-min(nums)) if len(nums) >= 2 else 0,
            "source_text": "", "source_missing": True, "candidates_empty": True,
            "primary": "", "primary_num": None, "confidence": 0.7,
            "candidates": [], "routing": []}

dp_lawful, viol_lawful = _compute_transition_legality(_mk_features(["Φ1","Φ3","Φ6","Φ7","Φ9"]))
check("lawful_wide_path_zero_delta_phi", dp_lawful == 0.0, f"delta_phi={dp_lawful!r}")
dp_illegal, _ = _compute_transition_legality(_mk_features(["Φ1","Φ8"]))
check("illegal_path_high_delta_phi", dp_illegal >= 0.60, f"delta_phi={dp_illegal!r}")

# ── 5. Trace instability (sigma_res) ─────────────────────────────────────────
from rmc_engine_v1.drift_engine import _compute_trace_instability
conflict_pr = {"input_event": {}, "phase_state": {"phase_primary": "Φ5", "phase_path_hypothesis": ["Φ5"], "confidence": 0.6,
    "phase_candidates": [{"phase": "Φ5", "confidence": 0.61}, {"phase": "Φ3", "confidence": 0.60}],
    "transition_warnings": [], "routing": []}}
sigma, detail = _compute_trace_instability(conflict_pr)
check("phase_conflict_in_sigma_res", detail.get("phase_conflict", 0) > 0, f"phase_conflict={detail.get('phase_conflict')!r}")
mismatch_pr = {"input_event": {}, "phase_state": {"phase_primary": "Φ5", "phase_path_hypothesis": ["Φ5"], "confidence": 0.6,
    "phase_candidates": [], "transition_warnings": [], "routing": []}}
_, detail_mm = _compute_trace_instability(mismatch_pr)
check("loop_mismatch_in_sigma_res", detail_mm.get("active_loop_mismatch", 0) > 0, f"mismatch={detail_mm.get('active_loop_mismatch')!r}")

# ── 6. Circuit breaker + coherence_score=0.0 ─────────────────────────────────
skip_report = {"input_event": {"event_id": "v", "x_t_raw_input_preview": "test", "dry_run": True},
               "phase_state": {"phase_primary": "Φ5", "phase_path_hypothesis": ["Φ5","Φ8"], "confidence": 0.3,
                               "phase_candidates": [], "transition_warnings": [{"type": "phase_skip_projection_risk", "from": "Φ5", "to": "Φ8", "law": "test"}], "routing": []}}
r_skip = analyze_drift(skip_report)
check("phase_skip_triggers_cb", r_skip.get("circuit_breaker", {}).get("triggered") is True)

from rmc_engine_v1.coherence_math import score_candidate
sc = score_candidate({"candidate_id": "v", "title": "v", "confidence": 0.99, "required_limitations": []},
                     {"candidate_set_id": "v", "source_drift_report": r_skip})
check("circuit_breaker_forces_score_zero", sc.get("coherence_score") == 0.0, f"score={sc.get('coherence_score')!r}")
check("circuit_breaker_proof_in_components", sc.get("score_components", {}).get("circuit_breaker_zeroed_score") is True)

# ── 7. main.py checks ─────────────────────────────────────────────────────────
main_py = os.path.join(FORGE_ROOT, "main.py")
if os.path.exists(main_py):
    msrc = open(main_py).read()
    check("main_py_old_drift_taxonomy_gone",  "_p262g_drift_taxonomy" not in msrc)
    check("main_py_imports_drift_engine",     "from rmc_engine_v1.drift_engine import" in msrc)
    check("main_py_mode_label_structural",    "structural_contract_drift_analysis" in msrc or "read_only_structural_drift_analysis" in msrc)
    check("main_py_circuit_breaker_contract", "circuit_breaker_kernel_contract" in msrc)
    check("main_py_B1_label",                 "Preflight-B1" in msrc)
else:
    for k in ["main_py_old_drift_taxonomy_gone","main_py_imports_drift_engine","main_py_B1_label"]:
        check(k, False, "main.py not at forge root")

# ── 8. Behavioral tests ───────────────────────────────────────────────────────
for script, key in [
    ("test_rmc_drift_engine_behavior.py",   "drift_engine_B1_behavior_tests_pass"),
    ("test_rmc_phase_parser_behavior.py",   "phase_parser_behavior_tests_pass"),
    ("test_rmc_coherence_math_behavior.py", "coherence_math_behavior_tests_pass"),
]:
    path = os.path.join(FORGE_ROOT, "scripts", script)
    if os.path.exists(path):
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=FORGE_ROOT)
        check(key, p.returncode == 0, "exit=0" if p.returncode == 0 else p.stdout[-300:])
    else:
        check(key, False, f"{script} not found")

# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(1 for _,v,_ in results if v == PASS)
failed = sum(1 for _,v,_ in results if v == FAIL)
print(f"\nPATCH 262J1R-PREFLIGHT-B1 VERIFIER — Drift Engine Hardening")
print(f"{'─' * 72}")
for name, verdict, detail in results:
    m = "✓" if verdict == PASS else "✗"
    line = f"  {m} [{verdict}] {name}"
    if verdict == FAIL or (detail and len(detail) < 80):
        line += f"\n        {detail}"
    print(line)
print(f"{'─' * 72}")
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
print()
print("MACHINE_READABLE_VERDICTS:")
for k in ["drift_engine_importable","engine_mode_structural_contract","keyword_counting_false",
          "thresholds_conservative","bypass_violation_detected","negated_bypass_not_detected",
          "bypass_triggers_circuit_breaker","lawful_wide_path_zero_delta_phi",
          "phase_conflict_in_sigma_res","circuit_breaker_forces_score_zero",
          "circuit_breaker_proof_in_components","syntactic_firewall_detects_junk",
          "main_py_old_drift_taxonomy_gone","drift_engine_B1_behavior_tests_pass",
          "phase_parser_behavior_tests_pass","coherence_math_behavior_tests_pass"]:
    for n,v,_ in results:
        if n == k:
            print(f"  {k}={v == PASS}"); break
if failed == 0:
    print("\nRESULT: PATCH_262J1R_PREFLIGHT_B1_VERIFY_OK"); sys.exit(0)
else:
    print(f"\nRESULT: PATCH_262J1R_PREFLIGHT_B1_VERIFY_FAIL ({failed} failed)"); sys.exit(1)
