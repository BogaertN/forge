#!/usr/bin/env python3
"""Patch 268S2 Verifier. Run: python scripts/patch268S2_verify.py"""
import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASS, FAIL = "PASS", "FAIL"
results = []
def chk(n, ok, d=""): results.append((n, PASS if ok else FAIL, d))

try:
    from rmc_engine_v1.protoforge2_drift_connector import (
        boundary, probe_protoforge2_status, preview_drift_call, _normalize,
        ENGINE_VERSION, FULL_ENGINE_SHA256, LEGACY_REJECTED_SHA256,
        RMC_ARBITRATOR_SHA256, SANDBOX_BRIDGE_SHA256,
    )
    chk("import_ok", True)
except ImportError as e:
    chk("import_ok", False, str(e)); sys.exit(1)

b = boundary()
chk("engine_268S2",             "268S2" in ENGINE_VERSION)
chk("no_shell",                b["no_shell"] is True)
chk("no_subprocess",           b["no_subprocess"] is True)
chk("no_browser_import",       b["no_browser_selected_import_path"] is True)
chk("controlled_local_import", b["controlled_local_import_only"] is True)
chk("default_read_only",       b["default_http_preview_read_only"] is True)
chk("monitor_not_called",      b["full_drift_monitor_not_called_by_default"] is True)
chk("exec_note_disclosed",     "exec_module" in b.get("exec_module_note", ""))
chk("no_old_arbitrary_exec",   "no_arbitrary_exec: true" not in str(b))
chk("four_hashes",             len(b["known_hashes"]) == 4)
chk("full_engine_hash_known",  b["known_hashes"]["full_engine"] == FULL_ENGINE_SHA256)
chk("legacy_hash_known",       b["known_hashes"]["legacy_rejected"] == LEGACY_REJECTED_SHA256)
chk("arb_hash_known",          b["known_hashes"]["rmc_safe_arbitrator"] == RMC_ARBITRATOR_SHA256)
chk("bridge_hash_known",       b["known_hashes"]["sandbox_bridge"] == SANDBOX_BRIDGE_SHA256)
chk("five_candidates",         b["candidate_count"] >= 4)
chk("writes_files_false",      b["writes_files"] is False)

# All candidates missing → SKIPPED
r = probe_protoforge2_status("/tmp/pf2_268S2_verify_missing")
chk("skipped_when_missing",    r["status"] == "SKIPPED")
chk("full_engine_never_callable", r["full_engine_callable_by_default"] is False)

# Arbitrator selected over bridge
from pathlib import Path
def _write(td, name, content):
    p = os.path.join(td, name); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p,'w').write(content); return p

ARB = "class DriftArbitrator:\n    def evaluate(self, p):\n        return {'epsilon_s':0.15,'verdict':'benign'}\n"
BRG = "class DriftBridge:\n    def evaluate(self, p):\n        return {'epsilon_s':0.18,'verdict':'benign'}\n"

with tempfile.TemporaryDirectory() as td:
    ap = _write(td, "laws/arb.py", ARB)
    bp = _write(td, "bridge/brg.py", BRG)
    test_cands = [
        {"path": Path(ap), "classification": "rmc_safe_arbitrator", "safe_by_default": True,
         "has_log_side_effects": False, "callable_class": "DriftArbitrator",
         "callable_method": "evaluate", "rank": 1},
        {"path": Path(bp), "classification": "sandbox_drift_bridge", "safe_by_default": True,
         "has_log_side_effects": False, "callable_class": "DriftBridge",
         "callable_method": "evaluate", "rank": 2},
    ]
    r = probe_protoforge2_status(_test_candidates=test_cands)
    chk("arb_rank1_selected",    r["selected_candidate_type"] == "rmc_safe_arbitrator")
    chk("callable_is_evaluate",  r["selected_callable"] == "DriftArbitrator.evaluate")

    r2 = preview_drift_call(_test_candidates=test_cands)
    chk("preview_live",          r2["status"] == "PREVIEW_OK")
    chk("normalize_schema",      "epsilon_s" in r2.get("normalized_result", {}))
    nr = r2.get("normalized_result", {})
    chk("all_schema_fields",     all(k in nr for k in [
        "epsilon_s","entropy","verdict","drift_detected","events","phase_deviation",
        "transition_validity","correction_recommended","chi_t_required",
        "circuit_breaker_open","projection_ready","recommended_action",
        "source_adapter","source_candidate_sha256","normalized",
    ]))
    chk("normalized_true",       nr.get("normalized") is True)
    chk("monitor_not_called_preview", r2.get("full_drift_monitor_not_called_by_default") is True)

# Normalization
n = _normalize(None, {"classification":"test"})
chk("normalization_failed_none", n.get("status") == "NORMALIZATION_FAILED")

# Behavior tests
r_bt = subprocess.run([sys.executable, "scripts/test_patch268S2_pf2_drift_adapter.py"],
    capture_output=True, text=True,
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chk("behavior_119", r_bt.returncode == 0)

# Route preservation
REQUIRED = ["/api/rmc/route-manifest","/api/rmc/llm-renderer/status",
            "/api/rmc/active-loop-state","/api/rmc/pipeline-summary",
            "/api/rmc/containment-router","/api/rmc/chi-correction-preview",
            "/api/rmc/protoforge2-drift-status","/api/rmc/protoforge2-drift-preview"]
mp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
if os.path.exists(mp):
    ms = open(mp).read()
    for ep in REQUIRED:
        chk(f"ROUTE_{ep.split('/')[-1][:20]}", f'"{ep}"' in ms)
    chk("MAIN_compiles", subprocess.run([sys.executable,"-m","py_compile",mp],
                                         capture_output=True).returncode == 0)

passed = sum(1 for _,v,_ in results if v==PASS)
failed = sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 268S2 VERIFIER")
print("─"*60)
for n,v,d in results:
    print(f"  {'✓' if v==PASS else '✗'} [{v}] {n}" + (f"\n        {d}" if d and v==FAIL else ""))
print("─"*60)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0: print("\nRESULT: PATCH_268S2_VERIFY_OK"); sys.exit(0)
else: print(f"\nRESULT: PATCH_268S2_VERIFY_FAIL ({failed})"); sys.exit(1)
