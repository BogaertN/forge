#!/usr/bin/env python3
"""Patch 269 Verifier. Run: python scripts/patch269_verify.py"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASS, FAIL = "PASS", "FAIL"; results = []; chk = lambda n,ok,d="": results.append((n,PASS if ok else FAIL,d))

try:
    from rmc_engine_v1.resurrection_engine import (evaluate_resurrection, boundary,
        DECISION_RESURRECTION_CANDIDATE, DECISION_DEEP_ARCHIVE_SEAL,
        DECISION_GHOST_LOOP_REQUIRED, DECISION_DEFER_NEXT_PHI9,
        GATE_7_SYSTEM_CAPACITY, GATE_2_RESURRECTION_LIMIT, GATE_5_DRIFT_SIGNATURE)
    chk("import_ok", True)
except ImportError as e: chk("import_ok", False, str(e)); sys.exit(1)

b = boundary()
chk("patch_269",       "269" in b["engine_version"])
chk("read_only",       b["read_only"] is True)
chk("no_writes",       b["writes_files"] is False)
chk("no_runtime",      b["re_enters_active_runtime"] is False)
chk("seven_gates",     len(b["gates"]) == 7)
chk("settle_window",   b["settle_window_seconds"] == 3.33)
chk("no_projection",   b["projection_allowed"] is False)
chk("no_manifest",     b["manifest_compile_allowed"] is False)
chk("no_spc_mutate",   b["mutates_spc_records"] is False)

def warm():
    return {"spc_record_id":"v","source_candidate_id":"c","tier":"WARM",
            "resurrection_eligible":True,"resurrection_attempts":0,"resurrection_limit":5,
            "phi9_eligible":True,"phase_at_collapse":"Φ7","phase_path":["Φ1","Φ3","Φ6","Φ7"],
            "collapse_code":"code1234","drift_signature":"sig1234abcd","lineage_ref":"lin1",
            "invariant_core":{"candidate_id":"c","epsilon_s":0.45},"residue":0.10,
            "epsilon_s":0.45,"breach":False,"ghost_loop_pressure":0.0}

r = evaluate_resurrection(warm())
chk("warm_resurrection",   r["resurrection_decision"] == DECISION_RESURRECTION_CANDIDATE)
chk("allowed_true",        r["resurrection_allowed"] is True)
chk("psi_prime_exists",    isinstance(r["psi_prime_candidate"], dict))
chk("no_writes_result",    r["writes_rmc_memory"] is False)

r = evaluate_resurrection({**warm(), "tier":"COLD"})
chk("cold_no_resurrect",   r["resurrection_decision"] == "no_resurrection_path_tier_not_warm")

r = evaluate_resurrection(warm()|{"resurrection_attempts":5})
chk("limit_deep_seal",     r["resurrection_decision"] == DECISION_DEEP_ARCHIVE_SEAL)

r = evaluate_resurrection(warm()|{"ghost_loop_pressure":0.40})
chk("ghost_gate7",         r["resurrection_decision"] == DECISION_GHOST_LOOP_REQUIRED)

r = evaluate_resurrection(warm()|{"breach":True})
chk("breach_deep_seal",    r["resurrection_decision"] == DECISION_DEEP_ARCHIVE_SEAL)

r = subprocess.run([sys.executable,"scripts/test_patch269_resurrection_engine.py"],
    capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chk("behavior_78", r.returncode == 0)

REQUIRED=["/api/rmc/resurrection-preview","/api/rmc/containment-router","/api/rmc/route-manifest"]
mp=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"main.py")
if os.path.exists(mp):
    ms=open(mp).read()
    for ep in REQUIRED: chk(f"ROUTE_{ep.split('/')[-1][:20]}", f'"{ep}"' in ms)
    chk("MAIN_compiles", subprocess.run([sys.executable,"-m","py_compile",mp],capture_output=True).returncode==0)

passed=sum(1 for _,v,_ in results if v==PASS); failed=sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 269 VERIFIER  Total:{len(results)} Passed:{passed} Failed:{failed}")
if failed==0: print("RESULT: PATCH_269_VERIFY_OK"); sys.exit(0)
else: print(f"RESULT: PATCH_269_VERIFY_FAIL ({failed})"); sys.exit(1)
