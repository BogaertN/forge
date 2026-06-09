#!/usr/bin/env python3
"""Patch 266R Verifier."""
import sys,os,subprocess,tempfile
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASS,FAIL="PASS","FAIL"; results=[]
def chk(n,ok,d=""): results.append((n,PASS if ok else FAIL,d))
try:
    from rmc_engine_v1.spc_cold_storage import preview_spc_record,boundary as sb,TIER_WARM,TIER_DEEP,APPROVAL_TOKEN_SPC_WRITE,commit_spc_record
    from rmc_engine_v1.drift_archive import preview_archive_record,boundary as db
    from rmc_engine_v1.dream_state_quarantine import preview_dream_record,boundary as dqb
    from rmc_engine_v1.ghost_loop_containment import preview_ghost_record,boundary as ghb
    chk("imports",True)
except ImportError as e: chk("imports",False,str(e)); sys.exit(1)
def sc(cb=False,ghost=0.0,breach=False,locked=False,eps=0.60):
    return {"candidate_id":"v","epsilon_s":eps,"math_terms":{"circuit_breaker":cb,"ghost_loop_pressure":ghost},"cold_storage_gate":{"ghost_loop_pressure":ghost},"breach":breach,"resurrection_limit_exceeded":locked}
b=sb(); chk("SPC_read_only",b["read_only"] is True); chk("SPC_no_proj",b["projection_allowed"] is False)
chk("SPC_idempotence_law","ϊ(⊙) = ⊙" in str(b["collapse_doctrine"]["idempotence_law"]))
p=preview_spc_record(sc()); chk("SPC_warm",p["tier"]==TIER_WARM); chk("SPC_residue",isinstance(p.get("residue"),float))
chk("SPC_lineage",bool(p.get("lineage_ref"))); chk("SPC_idem_key",bool(p.get("idempotence_key")))
p_breach=preview_spc_record(sc(breach=True)); chk("SPC_breach_deep",p_breach["tier"]==TIER_DEEP)
p_dup=preview_spc_record(sc(),known_spc_keys={p["idempotence_key"]}); chk("SPC_idem_noop",p_dup["status"]=="IDEMPOTENT_NO_OP")
with tempfile.TemporaryDirectory() as td:
    r=commit_spc_record(p,approval_token="WRONG",spc_root=td); chk("SPC_bad_token",r["status"]=="REFUSED")
    r=commit_spc_record(p,approval_token=APPROVAL_TOKEN_SPC_WRITE,spc_root=td); chk("SPC_commit",r["status"]=="COMMITTED")
    chk("SPC_in_tmpdir",td in r.get("path",""))
b=db(); chk("DA_no_truth",b["truth_support_allowed"] is False)
p=preview_archive_record(sc()); chk("DA_diagnostic",p["diagnostic_only"] is True)
b=dqb(); chk("DQ_future_arb",b["future_arbitration_required"] is True)
p=preview_dream_record(sc()); chk("DQ_no_proj",p["projection_allowed"] is False)
b=ghb(); chk("GH_gate7",b["gate_failed"]==7); chk("GH_no_reentry",b["active_runtime_reentry"] is False)
p=preview_ghost_record(sc(ghost=0.40)); chk("GH_preserve","not wrong" in p.get("preservation_note","").lower())

# behavior tests
r=subprocess.run([sys.executable,"scripts/test_patch266R_storage_preview.py"],capture_output=True,text=True,cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chk("behavior_84",r.returncode==0)

# route preservation + new endpoints
REQUIRED=["/api/rmc/route-manifest","/api/rmc/llm-renderer/status","/api/rmc/active-loop-state",
          "/api/rmc/pipeline-summary","/api/rmc/spc-cold-storage/preview",
          "/api/rmc/drift-archive/preview","/api/rmc/dream-state/preview","/api/rmc/ghost-loop/preview"]
mp=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"main.py")
if os.path.exists(mp):
    ms=open(mp).read()
    for ep in REQUIRED: chk(f"ROUTE_{ep.split('/')[-1][:18]}",f'"{ep}"' in ms)
    chk("MAIN_compiles",subprocess.run([sys.executable,"-m","py_compile",mp],capture_output=True).returncode==0)

passed=sum(1 for _,v,_ in results if v==PASS); failed=sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 266R VERIFIER  Total:{len(results)} Passed:{passed} Failed:{failed}")
if failed==0: print("RESULT: PATCH_266R_VERIFY_OK"); sys.exit(0)
else: print(f"RESULT: PATCH_266R_VERIFY_FAIL ({failed})"); sys.exit(1)
