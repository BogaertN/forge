#!/usr/bin/env python3
"""Patch 266 — Storage Preview Suite Behavior Tests.
Run: python scripts/test_patch266_storage_preview.py
"""
from __future__ import annotations
import sys, os, tempfile, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rmc_engine_v1.spc_cold_storage import (
    preview_spc_record, commit_spc_record, boundary as spc_boundary,
    TIER_WARM, TIER_COLD, TIER_DEEP, APPROVAL_TOKEN_SPC_WRITE,
)
from rmc_engine_v1.drift_archive import (
    preview_archive_record, commit_archive_record, boundary as da_boundary,
    APPROVAL_TOKEN as DA_TOKEN,
)
from rmc_engine_v1.dream_state_quarantine import (
    preview_dream_record, commit_dream_record, boundary as dq_boundary,
    APPROVAL_TOKEN as DQ_TOKEN,
)
from rmc_engine_v1.ghost_loop_containment import (
    preview_ghost_record, commit_ghost_record, boundary as gh_boundary,
    APPROVAL_TOKEN as GH_TOKEN,
)

PASS, FAIL = "PASS", "FAIL"
results = []
def chk(name, ok, detail=""):
    results.append((name, PASS if ok else FAIL, detail))


def _scored(cb=False, ghost=0.0, dream=False, eps=0.60, coherence=0.0,
            path=None, overextended=False, breach=False, locked=False):
    return {
        "candidate_id": "test_266",
        "epsilon_s": eps,
        "coherence_score": coherence,
        "overextended": overextended,
        "math_terms": {"circuit_breaker": cb, "ghost_loop_pressure": ghost,
                       "dream_state_eligible": dream},
        "cold_storage_gate": {"ghost_loop_pressure": ghost, "cold_storage_pressure": 0.60},
        "phase_path": path or ["Φ5", "Φ8"],
        "drift_report": {"drift_type": "catastrophic_drift"},
        "breach": breach,
        "resurrection_limit_exceeded": locked,
    }


# ── SPC Cold Storage ──────────────────────────────────────────────────────────
b = spc_boundary()
chk("SPC_boundary_read_only",      b["read_only"] is True)
chk("SPC_boundary_no_writes",      b["writes_files"] is False)
chk("SPC_boundary_no_llm",         b["calls_llm"] is False)
chk("SPC_boundary_no_projection",  b["projection_allowed"] is False)
chk("SPC_tiers_defined",           "tier_doctrine" in b)

# Default new entry → WARM
p = preview_spc_record(_scored())
chk("SPC_preview_ok",               p["status"] == "PREVIEW_OK")
chk("SPC_new_entry_warm",           p["tier"] == TIER_WARM)
chk("SPC_resurrection_eligible",    p["resurrection_eligible"] is True)
chk("SPC_has_idempotence_key",      bool(p.get("idempotence_key")))
chk("SPC_has_invariant_core",       isinstance(p.get("invariant_core"), dict))
chk("SPC_has_residue",              isinstance(p.get("residue"), float))
chk("SPC_has_collapse_code",        bool(p.get("collapse_code")))
chk("SPC_has_lineage_ref",          bool(p.get("lineage_ref")))
chk("SPC_no_writes",                p["writes_files"] is False)

# DEEP tier for breach
p_deep = preview_spc_record(_scored(breach=True))
chk("SPC_breach_tier_deep",         p_deep["tier"] == TIER_DEEP)
chk("SPC_deep_no_resurrection",     p_deep["resurrection_eligible"] is False)
chk("SPC_deep_reentry_empty",       p_deep["reentry_conditions"] == [])

# DEEP for resurrection limit exceeded
p_locked = preview_spc_record(_scored(locked=True))
chk("SPC_locked_tier_deep",         p_locked["tier"] == TIER_DEEP)

# Idempotence law
idem_key = p["idempotence_key"]
p_dup = preview_spc_record(_scored(), known_spc_keys={idem_key})
chk("SPC_idempotence_no_op",        p_dup["status"] == "IDEMPOTENT_NO_OP")
chk("SPC_idempotence_reason",       "ϊ(⊙) = ⊙" in p_dup.get("reason", ""))

# Commit requires token
with tempfile.TemporaryDirectory() as tmpdir:
    r_bad = commit_spc_record(p, approval_token="WRONG", spc_root=tmpdir)
    chk("SPC_bad_token_refused",        r_bad["status"] == "REFUSED")
    r_ok = commit_spc_record(p, approval_token=APPROVAL_TOKEN_SPC_WRITE, spc_root=tmpdir)
    chk("SPC_commit_ok",               r_ok["status"] == "COMMITTED")
    chk("SPC_commit_file_exists",       os.path.exists(r_ok.get("path", "")))
    # Duplicate commit via idempotence preview
    p_dup2 = preview_spc_record(_scored(), known_spc_keys={idem_key})
    r_dup  = commit_spc_record(p_dup2, approval_token=APPROVAL_TOKEN_SPC_WRITE, spc_root=tmpdir)
    chk("SPC_commit_idempotent_noop",   r_dup["status"] == "IDEMPOTENT_NO_OP")
    # No write outside tmpdir
    chk("SPC_write_inside_tmpdir",      str(tmpdir) in r_ok.get("path", ""))


# ── Drift Archive ──────────────────────────────────────────────────────────────
b = da_boundary()
chk("DA_boundary_no_truth_support",  b["truth_support_allowed"] is False)
chk("DA_boundary_no_projection",     b["projection_allowed"] is False)
chk("DA_boundary_read_only",         b["read_only"] is True)
chk("DA_boundary_no_resurrection",   b["resurrection_eligible"] is False)

p = preview_archive_record(_scored())
chk("DA_preview_ok",                 p["status"] == "PREVIEW_OK")
chk("DA_diagnostic_only",            p["diagnostic_only"] is True)
chk("DA_no_truth_support",           p["truth_support_allowed"] is False)
chk("DA_no_projection",              p["projection_allowed"] is False)
chk("DA_has_drift_signature",        bool(p.get("drift_signature")))
chk("DA_has_record_id",              bool(p.get("archive_record_id")))
chk("DA_no_writes",                  p["writes_files"] is False)

with tempfile.TemporaryDirectory() as tmpdir:
    r_bad = commit_archive_record(p, approval_token="WRONG", archive_root=tmpdir)
    chk("DA_bad_token_refused",       r_bad["status"] == "REFUSED")
    r_ok  = commit_archive_record(p, approval_token=DA_TOKEN, archive_root=tmpdir)
    chk("DA_commit_ok",              r_ok["status"] == "COMMITTED")
    # Append-only: second commit returns IDEMPOTENT
    r_dup = commit_archive_record(p, approval_token=DA_TOKEN, archive_root=tmpdir)
    chk("DA_append_only_idempotent",  r_dup["status"] == "IDEMPOTENT_NO_OP")


# ── Dream State Quarantine ────────────────────────────────────────────────────
b = dq_boundary()
chk("DQ_boundary_no_truth",          b["truth_support_allowed"] is False)
chk("DQ_boundary_no_projection",     b["projection_allowed"] is False)
chk("DQ_boundary_no_manifest",       b["manifest_compile_allowed"] is False)
chk("DQ_boundary_future_arb",        b["future_arbitration_required"] is True)

p = preview_dream_record(_scored(dream=True))
chk("DQ_preview_ok",                 p["status"] == "PREVIEW_OK")
chk("DQ_no_projection",              p["projection_allowed"] is False)
chk("DQ_no_stable_memory",           p["stable_memory_allowed"] is False)
chk("DQ_future_arb",                 p["future_arbitration_required"] is True)
chk("DQ_speculative_status",         "quarantined" in p.get("speculative_status", ""))
chk("DQ_has_hypothesis_state",       isinstance(p.get("hypothesis_state"), dict))

with tempfile.TemporaryDirectory() as tmpdir:
    r_bad = commit_dream_record(p, approval_token="WRONG", quarantine_root=tmpdir)
    chk("DQ_bad_token_refused",       r_bad["status"] == "REFUSED")
    r_ok  = commit_dream_record(p, approval_token=DQ_TOKEN, quarantine_root=tmpdir)
    chk("DQ_commit_ok",              r_ok["status"] == "COMMITTED")


# ── Ghost Loop Containment ────────────────────────────────────────────────────
b = gh_boundary()
chk("GH_boundary_no_reentry",        b["active_runtime_reentry"] is False)
chk("GH_boundary_no_projection",     b["projection_allowed"] is False)
chk("GH_boundary_no_current_res",    b["resurrection_via_current_protocol"] is False)
chk("GH_boundary_future_ok",         b["resurrection_via_future_runtime"] is True)
chk("GH_boundary_no_deletion",       b["deletion_allowed"] is False)
chk("GH_gate_7",                     b["gate_failed"] == 7)
chk("GH_system_capacity_type",       "system_capacity" in b["failure_type"])

p = preview_ghost_record(_scored(ghost=0.40))
chk("GH_preview_ok",                 p["status"] == "PREVIEW_OK")
chk("GH_gate_7_in_preview",          p["gate_failed"] == 7)
chk("GH_no_reentry",                 p["active_runtime_reentry_allowed"] is False)
chk("GH_no_current_resurrection",    p["resurrection_via_current_protocol"] is False)
chk("GH_has_ghost_id",               bool(p.get("ghost_loop_id")))
chk("GH_has_capacity_reason",        bool(p.get("capacity_failure_reason")))
chk("GH_preservation_note",          "not wrong" in p.get("preservation_note", "").lower())
chk("GH_no_writes",                  p["writes_files"] is False)

with tempfile.TemporaryDirectory() as tmpdir:
    r_bad = commit_ghost_record(p, approval_token="WRONG", ghost_root=tmpdir)
    chk("GH_bad_token_refused",       r_bad["status"] == "REFUSED")
    r_ok  = commit_ghost_record(p, approval_token=GH_TOKEN, ghost_root=tmpdir)
    chk("GH_commit_ok",              r_ok["status"] == "COMMITTED")


# ── No writes / no shell / no Chroma / no Identity Vault / no LLM ─────────────
import rmc_engine_v1.spc_cold_storage as _spc
import rmc_engine_v1.drift_archive as _da
import rmc_engine_v1.dream_state_quarantine as _dq
import rmc_engine_v1.ghost_loop_containment as _gh
for modname, mod in [("SPC", _spc), ("DA", _da), ("DQ", _dq), ("GH", _gh)]:
    src = inspect.getsource(mod)
    chk(f"{modname}_no_subprocess",  "import subprocess" not in src and "subprocess.run(" not in src)
    chk(f"{modname}_no_llm",         "openai" not in src and "anthropic" not in src)
    chk(f"{modname}_no_chroma",      "chromadb" not in src)
    chk(f"{modname}_no_iv",          "identity_vault" not in src.lower().replace("writes_identity_vault",""))

# Summary
passed = sum(1 for _,v,_ in results if v==PASS)
failed = sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 266 — STORAGE PREVIEW SUITE BEHAVIOR TESTS")
print("─"*65)
for name, verdict, detail in results:
    m = "✓" if verdict == PASS else "✗"
    print(f"  {m} [{verdict}] {name}" + (f"\n        {detail}" if detail else ""))
print("─"*65)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0:
    print("\n  RESULT: patch266_storage_preview_tests=PASS"); sys.exit(0)
else:
    print("\n  RESULT: patch266_storage_preview_tests=FAIL"); sys.exit(1)
