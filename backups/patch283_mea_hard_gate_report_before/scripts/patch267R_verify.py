#!/usr/bin/env python3
"""Patch 267R Verifier."""
import sys,os,subprocess
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASS,FAIL="PASS","FAIL"; results=[]
def chk(n,ok,d=""): results.append((n,PASS if ok else FAIL,d))
try:
    from rmc_engine_v1.chi_correction_gate import evaluate_chi_t,boundary,THRESHOLDS
    chk("import",True)
except ImportError as e: chk("import",False,str(e)); sys.exit(1)
b=boundary(); chk("read_only",b["read_only"] is True)
chk("formula","χ(t) = Φ₁·α + Σ(Δψ / t)" in b["formula"])
chk("babel_named","babel_cutoff" in THRESHOLDS)
chk("settle_333",THRESHOLDS["settle_window_seconds"]==3.33)
chk("residue_03",THRESHOLDS["residue_decay"]==0.30)
def sc(eps=0.10,cb=False,chi=False):
    return {"candidate_id":"v","epsilon_s":eps,"math_terms":{"circuit_breaker":cb,"chi_required":chi},"score_components":{"circuit_breaker_zeroed_score":cb}}
r=evaluate_chi_t(sc(0.10)); chk("low_not_req",r["chi_required"] is False)
r=evaluate_chi_t(sc(0.80)); chk("babel_collapse",r["status"]=="COLLAPSE_REQUIRED")
r=evaluate_chi_t(sc(0.52),prior_epsilon_series=[0.40,0.45,0.51,0.53]); chk("drift_spiral",r["drift_spiral_detected"] is True or r["status"]=="DRIFT_SPIRAL_ABORT")
r=evaluate_chi_t(sc(0.45)); chk("psi1_absent_no_crash","status" in r)
chk("no_writes_all",all(evaluate_chi_t(sc(e))["writes_files"] is False for e in [0.10,0.50,0.80]))
r=subprocess.run([sys.executable,"scripts/test_patch267R_chi_correction_gate.py"],capture_output=True,text=True,cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chk("behavior_50",r.returncode==0)
REQUIRED=["/api/rmc/route-manifest","/api/rmc/active-loop-state","/api/rmc/chi-correction-preview"]
mp=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"main.py")
if os.path.exists(mp):
    ms=open(mp).read()
    for ep in REQUIRED: chk(f"ROUTE_{ep.split('/')[-1][:18]}",f'"{ep}"' in ms)
    chk("MAIN_compiles",subprocess.run([sys.executable,"-m","py_compile",mp],capture_output=True).returncode==0)
passed=sum(1 for _,v,_ in results if v==PASS); failed=sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 267R VERIFIER  Total:{len(results)} Passed:{passed} Failed:{failed}")
if failed==0: print("RESULT: PATCH_267R_VERIFY_OK"); sys.exit(0)
else: print(f"RESULT: PATCH_267R_VERIFY_FAIL ({failed})"); sys.exit(1)
