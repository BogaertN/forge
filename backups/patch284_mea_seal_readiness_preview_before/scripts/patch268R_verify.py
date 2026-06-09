#!/usr/bin/env python3
"""Patch 268R Verifier."""
import sys,os,subprocess,tempfile
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASS,FAIL="PASS","FAIL"; results=[]
def chk(n,ok,d=""): results.append((n,PASS if ok else FAIL,d))
try:
    from rmc_engine_v1.protoforge2_drift_connector import probe_protoforge2_status,probe_protoforge2_import,preview_drift_call,boundary,_is_safe_function_name,_normalize_pf2_output
    chk("import",True)
except ImportError as e: chk("import",False,str(e)); sys.exit(1)
b=boundary(); chk("read_only",b["read_only"] is True); chk("no_shell",b["executes_shell"] is False)
chk("no_writes",b["writes_files"] is False); chk("three_modes",set(b["adapter_modes"])=={"LIVE","SKIPPED","FALLBACK"})
chk("no_modify_pf2",b["safety_rules"]["no_modify_pf2"] is True)
# boundary wording: "controlled local import" not "no arbitrary code"
chk("honest_boundary","controlled local import" in str(b).lower() or "no_shell" in str(b))
r=probe_protoforge2_status("/tmp/pf2_missing_xyz"); chk("missing_skipped",r["status"]=="SKIPPED")
r=probe_protoforge2_status("/etc/passwd"); chk("unsafe_refused",r["status"]=="REFUSED_UNSAFE_PATH")
with tempfile.TemporaryDirectory() as td:
    with open(os.path.join(td,"memory-drift.py"),"w") as f:
        f.write("def analyze_drift(x):\n    return {'epsilon_s':0.15,'drift_type':'test','circuit_breaker':False}\n")
    r=probe_protoforge2_status(td); chk("hyphen_found",r["drift_module_found"] is True)
    chk("sha256_present",len(r.get("module_sha256",""))==64)
    ri=probe_protoforge2_import(td); chk("importable",ri.get("importable") is True)
    fpath=os.path.join(td,"memory-drift.py")
    rp=preview_drift_call(test_module_path=fpath); chk("preview_ok",rp["status"]=="PREVIEW_OK")
    chk("normalized","epsilon_s" in rp.get("normalized_result",{}))
n=_normalize_pf2_output({"epsilon_s":0.55},"fn"); chk("norm_eps",n["epsilon_s"]==0.55)
chk("safe_fn",_is_safe_function_name("analyze_drift") is True)
chk("unsafe_fn",_is_safe_function_name("write_data") is False)
r=subprocess.run([sys.executable,"scripts/test_patch268R_pf2_drift_connector.py"],capture_output=True,text=True,cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chk("behavior_61",r.returncode==0)
REQUIRED=["/api/rmc/route-manifest","/api/rmc/active-loop-state","/api/rmc/protoforge2-drift-status","/api/rmc/protoforge2-drift-preview"]
mp=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"main.py")
if os.path.exists(mp):
    ms=open(mp).read()
    for ep in REQUIRED: chk(f"ROUTE_{ep.split('/')[-1][:20]}",f'"{ep}"' in ms)
    chk("MAIN_compiles",subprocess.run([sys.executable,"-m","py_compile",mp],capture_output=True).returncode==0)
passed=sum(1 for _,v,_ in results if v==PASS); failed=sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 268R VERIFIER  Total:{len(results)} Passed:{passed} Failed:{failed}")
if failed==0: print("RESULT: PATCH_268R_VERIFY_OK"); sys.exit(0)
else: print(f"RESULT: PATCH_268R_VERIFY_FAIL ({failed})"); sys.exit(1)
