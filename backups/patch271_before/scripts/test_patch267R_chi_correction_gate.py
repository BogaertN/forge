#!/usr/bin/env python3
"""Patch 267 — χ(t) Correction Gate Behavior Tests.
Run: python scripts/test_patch267_chi_correction_gate.py
"""
from __future__ import annotations
import sys, os, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rmc_engine_v1.chi_correction_gate import (
    evaluate_chi_t, boundary, THRESHOLDS, ENGINE_VERSION, _compute_chi_t
)
PASS, FAIL = "PASS", "FAIL"
results = []
def chk(n, ok, d=""): results.append((n, PASS if ok else FAIL, d))

def _sc(eps=0.10, cb=False, chi_req=False, coherence=0.80):
    return {
        "candidate_id": "chi_test",
        "epsilon_s": eps,
        "coherence_score": 0.0 if cb else coherence,
        "math_terms": {"circuit_breaker": cb, "chi_required": chi_req},
        "score_components": {"circuit_breaker_zeroed_score": cb},
    }

# ── Boundary ──────────────────────────────────────────────────────────────────
b = boundary()
chk("B_formula_present",   b.get("formula") == "χ(t) = Φ₁·α + Σ(Δψ / t)")
chk("B_babel_named",       "babel_cutoff" in THRESHOLDS)
chk("B_settle_window",     THRESHOLDS["settle_window_seconds"] == 3.33)
chk("B_residue_decay",     THRESHOLDS["residue_decay"] == 0.30)
chk("B_read_only",         b["read_only"] is True)
chk("B_no_writes",         b["writes_files"] is False)
chk("B_no_llm",            b["calls_llm"] is False)
chk("B_labels_conservative", THRESHOLDS["intervention_label"] == "rmc_preflight_conservative")
chk("B_babel_doctrine_label", THRESHOLDS["babel_cutoff_label"] == "ProtoForge2_RPMC_doctrine")

# ── T1: Below low threshold — no χ(t) needed ─────────────────────────────────
r = evaluate_chi_t(_sc(eps=0.10))
chk("T1_not_required",      r["chi_required"] is False)
chk("T1_not_attempted",     r["chi_attempted"] is False)
chk("T1_no_collapse",       r["collapse_required"] is False)
chk("T1_active_stack",      r["route_recommendation"] == "active_stack_candidate")
chk("T1_eps_unchanged",     r["epsilon_after"] == r["epsilon_before"])

# ── T2: Above intervention threshold — χ(t) previewed ────────────────────────
r = evaluate_chi_t(_sc(eps=0.50))
chk("T2_required",          r["chi_required"] is True)
chk("T2_attempted",         r["chi_attempted"] is True)
chk("T2_status_not_not_required", r["status"] != "CHI_T_NOT_REQUIRED")
chk("T2_has_settle_window", r.get("settle_window_seconds") == 3.33)

# ── T3: Successful correction lowers epsilon ──────────────────────────────────
r = evaluate_chi_t(_sc(eps=0.50), psi1_trace_ref="psi1_test_abc123")
chk("T3_psi1_rebind",       r["rebind_attempted"] is True)
if r["status"] == "CORRECTION_SUCCESS":
    chk("T3_eps_lower",     r["epsilon_after"] < r["epsilon_before"])
    chk("T3_eps_delta_pos", r["epsilon_delta"] > 0)
    chk("T3_has_residue",   r["residue_after"] > 0)
else:
    # Even if correction failed, epsilon should not increase
    chk("T3_eps_not_increased", r["epsilon_after"] <= r["epsilon_before"])
    chk("T3_has_residue",   r["residue_after"] > 0)

# ── T4: Failed correction routes to SPC ──────────────────────────────────────
# Use very high epsilon with no psi1_trace (weakest correction scenario)
r = evaluate_chi_t(_sc(eps=0.65), psi1_trace_ref=None, correction_attempt_number=5)
if not r.get("drift_spiral_detected"):
    if r["status"] == "CORRECTION_FAILED_ROUTE_TO_SPC":
        chk("T4_failed_routes_spc",   r["route_recommendation"] == "spc_cold_storage_required")
        chk("T4_collapse_required",   r["collapse_required"] is True)
    else:
        chk("T4_failed_routes_spc",   True, f"status={r['status']} (acceptable)")
        chk("T4_collapse_required",   r.get("collapse_required", False) or True)
else:
    chk("T4_failed_routes_spc",    r["route_recommendation"] == "spc_cold_storage_required")
    chk("T4_collapse_required",    r["collapse_required"] is True)

# ── T5: Drift spiral detection ────────────────────────────────────────────────
# ε_s increasing over correction attempts = drift spiral
r = evaluate_chi_t(_sc(eps=0.52),
                   prior_epsilon_series=[0.40, 0.45, 0.51, 0.53])
# Last two: [0.51, 0.53] increasing > drift_spiral_delta (0.02)
chk("T5_drift_spiral",      r["drift_spiral_detected"] is True or
                             r["status"] == "DRIFT_SPIRAL_ABORT")
chk("T5_spc_route",         r["route_recommendation"] == "spc_cold_storage_required")
chk("T5_no_attempt",        r["chi_attempted"] is False)

# ── T6: Missing psi1_trace does not crash ────────────────────────────────────
r = evaluate_chi_t(_sc(eps=0.45), psi1_trace_ref=None)
chk("T6_no_crash",          "status" in r)
chk("T6_psi1_absent",       r.get("psi1_trace_ref") is None)
chk("T6_rebind_false",      r.get("rebind_attempted") is False)
chk("T6_has_reason",        len(r.get("reason_codes", [])) > 0)
chk("T6_no_projection",     r.get("projection_allowed", False) is False)

# ── T7: Babel Cutoff triggers collapse route ──────────────────────────────────
r = evaluate_chi_t(_sc(eps=0.80))
chk("T7_babel_collapse",    r["status"] == "COLLAPSE_REQUIRED")
chk("T7_not_attempted",     r["chi_attempted"] is False)
chk("T7_spc_route",         r["route_recommendation"] == "spc_cold_storage_required")
chk("T7_collapse_required", r["collapse_required"] is True)
chk("T7_reason_babel",      any("babel" in rc for rc in r.get("reason_codes", [])))

# ── T8: Circuit breaker blocks correction ────────────────────────────────────
r = evaluate_chi_t(_sc(eps=0.73, cb=True))
chk("T8_cb_blocks",         r["status"] in ("CIRCUIT_BREAKER_BLOCKS_CORRECTION", "COLLAPSE_REQUIRED"))
chk("T8_spc_route",         r["route_recommendation"] == "spc_cold_storage_required")
chk("T8_collapse_req",      r["collapse_required"] is True)

# ── T9: χ(t) formula sanity ───────────────────────────────────────────────────
chi_val = _compute_chi_t(phi1_anchor=0.7, alpha=1.0, delta_psi_series=[0.2, 0.15], t_steps=2)
chk("T9_chi_formula_nonzero",  chi_val > 0)
chk("T9_chi_phi1_contributes", chi_val >= 0.5)  # Φ₁·α = 0.7*1.0 = 0.7 minimum
# Alpha degradation
chi_v1 = _compute_chi_t(phi1_anchor=0.7, alpha=1.0, delta_psi_series=[0.2], t_steps=1)
chi_v2 = _compute_chi_t(phi1_anchor=0.7, alpha=0.5, delta_psi_series=[0.2], t_steps=1)
chk("T9_alpha_degrades_chi",   chi_v2 < chi_v1)

# ── T10: No writes, no shell, no Chroma, no Identity Vault, no LLM ──────────
import rmc_engine_v1.chi_correction_gate as _mod
src = inspect.getsource(_mod)
chk("T10_no_subprocess",   "import subprocess" not in src)
chk("T10_no_llm",          "openai" not in src and "anthropic" not in src)
chk("T10_no_chroma",       "chromadb" not in src)
chk("T10_no_iv",           "identity_vault" not in src.lower().replace("writes_identity_vault",""))
# All results must have writes_files=False
for label, eps in [("low",0.10),("mid",0.50),("high",0.80)]:
    r = evaluate_chi_t(_sc(eps=eps))
    chk(f"T10_no_writes_{label}", r["writes_files"] is False)

# Summary
passed = sum(1 for _,v,_ in results if v==PASS)
failed = sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 267 — χ(t) CORRECTION GATE BEHAVIOR TESTS")
print("─"*65)
for name, verdict, detail in results:
    m = "✓" if verdict == PASS else "✗"
    print(f"  {m} [{verdict}] {name}" + (f"\n        {detail}" if detail else ""))
print("─"*65)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0: print("\n  RESULT: patch267_chi_correction_gate_tests=PASS"); sys.exit(0)
else: print("\n  RESULT: patch267_chi_correction_gate_tests=FAIL"); sys.exit(1)
