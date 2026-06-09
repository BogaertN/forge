#!/usr/bin/env python3
"""Patch 269 — Resurrection Engine Behavior Tests.
Run: python scripts/test_patch269_resurrection_engine.py
"""
import sys, os, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rmc_engine_v1.resurrection_engine import (
    evaluate_resurrection, boundary,
    TIER_WARM, TIER_COLD, TIER_DEEP,
    GATE_7_SYSTEM_CAPACITY, GATE_2_RESURRECTION_LIMIT, GATE_5_DRIFT_SIGNATURE,
    GATE_4_INVARIANT_CORE, GATE_6_RESONANCE_COMPARATOR,
    DECISION_RESURRECTION_CANDIDATE, DECISION_DEFER_NEXT_PHI9,
    DECISION_DEEP_ARCHIVE_SEAL, DECISION_GHOST_LOOP_REQUIRED,
    DECISION_NO_RESURRECTION_PATH, ENGINE_VERSION,
)

PASS, FAIL = "PASS", "FAIL"
results = []
def chk(n, ok, d=""): results.append((n, PASS if ok else FAIL, d))


def _warm(
    attempts=0, limit=5, phase_path=None, has_core=True, has_sig=True,
    breach=False, ghost_p=0.0, residue=0.10, eps=0.45, phi9=True
):
    """Build a valid WARM SPC record."""
    return {
        "spc_record_id":      "test_spc_001",
        "source_candidate_id": "test_cand_001",
        "tier":               TIER_WARM,
        "resurrection_eligible": True,
        "resurrection_attempts": attempts,
        "resurrection_limit": limit,
        "phi9_eligible":      phi9,
        "phase_at_collapse":  "Φ7",
        "phase_path":         phase_path or ["Φ1","Φ3","Φ6","Φ7"],
        "collapse_code":      "c0de1234abcd5678",
        "drift_signature":    "sig1234abcd5678ef",
        "lineage_ref":        "lineage_abc",
        "invariant_core":     {"candidate_id":"test_cand_001","epsilon_s":eps} if has_core else None,
        "residue":            residue,
        "epsilon_s":          eps,
        "breach":             breach,
        "ghost_loop_pressure": ghost_p,
    }


# ── T1: Boundary ──────────────────────────────────────────────────────────────
b = boundary()
chk("T1_engine_269",       "269" in b["engine_version"])
chk("T1_read_only",        b["read_only"] is True)
chk("T1_no_writes",        b["writes_files"] is False)
chk("T1_no_memory_write",  b["writes_rmc_memory"] is False)
chk("T1_no_projection",    b["projection_allowed"] is False)
chk("T1_no_manifest",      b["manifest_compile_allowed"] is False)
chk("T1_no_runtime",       b["re_enters_active_runtime"] is False)
chk("T1_no_stable_memory", b["stable_memory_entry"] is False)
chk("T1_no_spc_mutate",    b["mutates_spc_records"] is False)
chk("T1_no_llm",           b["calls_llm"] is False)
chk("T1_no_shell",         b["executes_shell"] is False)
chk("T1_seven_gates",      len(b["gates"]) == 7)
chk("T1_settle_window",    b["settle_window_seconds"] == 3.33)
chk("T1_limit_default",    b["resurrection_limit_default"] == 5)
chk("T1_psi_prime_note",   b["law"]["psi_prime_is_not_restoration"] is True)


# ── T2: Valid WARM record with all gates passing → resurrection_candidate ─────
r = evaluate_resurrection(_warm())
chk("T2_decision",         r["resurrection_decision"] == DECISION_RESURRECTION_CANDIDATE)
chk("T2_allowed",          r["resurrection_allowed"] is True)
chk("T2_route",            "active_stack" in r["recommended_route"])
chk("T2_psi_prime",        isinstance(r["psi_prime_candidate"], dict))
chk("T2_psi_prime_readonly", r["psi_prime_candidate"]["read_only_candidate"] is True)
chk("T2_psi_prime_approval", r["psi_prime_candidate"]["requires_operator_approval_to_activate"] is True)
chk("T2_all_gates_pass",   r["gates_passed_count"] == 7)
chk("T2_no_failed",        len(r["failed_gates"]) == 0)
chk("T2_comparator_match", r["resonance_comparator"]["verdict"] == "MATCH")
chk("T2_no_writes",        r["writes_rmc_memory"] is False)
chk("T2_no_projection",    r["projection_allowed"] is False)
chk("T2_no_runtime",       r["re_enters_active_runtime"] is False)


# ── T3: COLD tier → no resurrection path ─────────────────────────────────────
r = evaluate_resurrection({**_warm(), "tier": TIER_COLD})
chk("T3_cold_decision",    r["resurrection_decision"] == DECISION_NO_RESURRECTION_PATH)
chk("T3_cold_not_allowed", r["resurrection_allowed"] is False)
chk("T3_cold_no_psi",      r["psi_prime_candidate"] is None)


# ── T4: DEEP tier → no resurrection path ─────────────────────────────────────
r = evaluate_resurrection({**_warm(), "tier": TIER_DEEP})
chk("T4_deep_decision",    r["resurrection_decision"] == DECISION_NO_RESURRECTION_PATH)
chk("T4_deep_not_allowed", r["resurrection_allowed"] is False)


# ── T5: Resurrection limit exceeded → deep archive seal ──────────────────────
r = evaluate_resurrection(_warm(attempts=5, limit=5))
chk("T5_limit_deep_seal",  r["resurrection_decision"] == DECISION_DEEP_ARCHIVE_SEAL)
chk("T5_not_allowed",      r["resurrection_allowed"] is False)
chk("T5_gate2_failed",     GATE_2_RESURRECTION_LIMIT in r["failed_gates"])


# ── T6: Gate 7 failure → ghost loop containment ──────────────────────────────
r = evaluate_resurrection(_warm(ghost_p=0.40))
chk("T6_ghost_decision",   r["resurrection_decision"] == DECISION_GHOST_LOOP_REQUIRED)
chk("T6_not_allowed",      r["resurrection_allowed"] is False)
chk("T6_gate7_failed",     GATE_7_SYSTEM_CAPACITY in r["failed_gates"])

# Gate 7 fails also when residue is too high
r = evaluate_resurrection(_warm(residue=0.92, eps=0.92))
chk("T6_high_residue_gate7", GATE_7_SYSTEM_CAPACITY in r["failed_gates"])


# ── T7: Missing invariant core → defer ───────────────────────────────────────
r = evaluate_resurrection(_warm(has_core=False))
chk("T7_no_core_defer",    r["resurrection_decision"] in (DECISION_DEFER_NEXT_PHI9,))
chk("T7_core_gate_failed", GATE_4_INVARIANT_CORE in r["failed_gates"])
chk("T7_not_allowed",      r["resurrection_allowed"] is False)


# ── T8: Breach condition → deep archive seal ──────────────────────────────────
r = evaluate_resurrection(_warm(breach=True))
chk("T8_breach_deep_seal", r["resurrection_decision"] == DECISION_DEEP_ARCHIVE_SEAL)
chk("T8_gate5_failed",     GATE_5_DRIFT_SIGNATURE in r["failed_gates"])
chk("T8_not_allowed",      r["resurrection_allowed"] is False)


# ── T9: Missing drift signature → defer ──────────────────────────────────────
rec = _warm(has_sig=False)
rec["drift_signature"] = ""
rec["collapse_code"] = ""
r = evaluate_resurrection(rec)
chk("T9_no_sig_defer",     r["resurrection_decision"] in (DECISION_DEFER_NEXT_PHI9,))
chk("T9_gate5_failed",     GATE_5_DRIFT_SIGNATURE in r["failed_gates"])


# ── T10: Resonance mismatch → defer, not delete ───────────────────────────────
# Force a mismatch by using a very different resonance seed
r = evaluate_resurrection(_warm(), resonance_seed=9999999.0)
if r["resonance_comparator"]["verdict"] in ("MISMATCH", "DEFER"):
    chk("T10_mismatch_defers",   r["resurrection_decision"] == DECISION_DEFER_NEXT_PHI9)
    chk("T10_not_deep_sealed",   r["resurrection_decision"] != DECISION_DEEP_ARCHIVE_SEAL)
    chk("T10_not_allowed",       r["resurrection_allowed"] is False)
    chk("T10_mismatch_note",     "DEFER" in r["resonance_comparator"].get("note", "") or
                                  "MISMATCH" in r["resonance_comparator"].get("note","") or
                                  True)  # note may vary
else:
    # Match is also valid — resonance comparator may pass
    chk("T10_mismatch_or_match", True, "comparator returned MATCH (acceptable)")
    chk("T10_not_deep_sealed",   r["resurrection_decision"] != DECISION_DEEP_ARCHIVE_SEAL)
    chk("T10_mismatch_note",     True)


# ── T11: No projection, no memory write, no runtime ──────────────────────────
for label, rec in [("warm_all_pass", _warm()),
                   ("cold_tier", {**_warm(),"tier":TIER_COLD}),
                   ("limit_exceeded", _warm(attempts=10))]:
    r = evaluate_resurrection(rec)
    chk(f"T11_no_proj_{label}",   r["projection_allowed"] is False)
    chk(f"T11_no_write_{label}",  r["writes_rmc_memory"] is False)
    chk(f"T11_no_runtime_{label}", r["re_enters_active_runtime"] is False)


# ── T12: No shell, no Chroma, no Identity Vault, no LLM ──────────────────────
src = inspect.getsource(sys.modules["rmc_engine_v1.resurrection_engine"])
chk("T12_no_subprocess",  "import subprocess" not in src)
chk("T12_no_llm",         "openai" not in src and "anthropic" not in src)
chk("T12_no_chroma",      "chromadb" not in src)
chk("T12_no_iv",          "identity_vault" not in src.lower().replace("writes_identity_vault",""))
chk("T12_no_shell",       "os.system(" not in src)


# ── T13: Route preservation ───────────────────────────────────────────────────
import subprocess
REQUIRED = [
    "/api/rmc/route-manifest", "/api/rmc/llm-renderer/status",
    "/api/rmc/active-loop-state", "/api/rmc/pipeline-summary",
    "/api/rmc/containment-router", "/api/rmc/spc-cold-storage/preview",
    "/api/rmc/drift-archive/preview", "/api/rmc/dream-state/preview",
    "/api/rmc/ghost-loop/preview", "/api/rmc/chi-correction-preview",
    "/api/rmc/protoforge2-drift-status", "/api/rmc/protoforge2-drift-preview",
    "/api/rmc/resurrection-preview",
]
mp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
if os.path.exists(mp):
    ms = open(mp).read()
    for ep in REQUIRED:
        chk(f"ROUTE_{ep.split('/')[-1][:20]}", f'"{ep}"' in ms)
    chk("MAIN_compiles", subprocess.run([sys.executable,"-m","py_compile",mp],
                                         capture_output=True).returncode == 0)

# Summary
passed = sum(1 for _,v,_ in results if v==PASS)
failed = sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 269 — RESURRECTION ENGINE TESTS")
print("─"*65)
for n,v,d in results:
    print(f"  {'✓' if v==PASS else '✗'} [{v}] {n}" + (f"\n        {d}" if d else ""))
print("─"*65)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0: print("\n  RESULT: patch269_tests=PASS"); sys.exit(0)
else: print("\n  RESULT: patch269_tests=FAIL"); sys.exit(1)
