#!/usr/bin/env python3
"""Patch 265R Verifier. Run: python scripts/patch265R_verify.py"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASS,FAIL="PASS","FAIL"; results=[]
def chk(n,ok,d=""): results.append((n,PASS if ok else FAIL,d))

try:
    from rmc_engine_v1.containment_router import route_candidate, boundary, SEALED_ROUTES, ROUTE_ACTIVE_STACK, ROUTE_SPC_COLD_STORAGE, ROUTE_GHOST_LOOP, ALL_ROUTES, THRESHOLDS
    chk("import_ok",True)
except ImportError as e: chk("import_ok",False,str(e)); sys.exit(1)

b=boundary()
chk("read_only",b["read_only"] is True)
chk("no_writes",b["writes_files"] is False)
chk("six_routes",len(ALL_ROUTES)==6)
chk("four_sealed",len(SEALED_ROUTES)==4)
chk("babel_named","babel_cutoff_doctrine" in THRESHOLDS)

def mk(cb=False,ghost=0.0,dream=False,corr=False,eps=0.10,path=None):
    path=path or ["Φ1","Φ3","Φ6","Φ7"]
    return {"candidate_id":"v","epsilon_s":eps,"coherence_score":0.0 if cb else 0.80,
            "math_terms":{"circuit_breaker":cb,"ghost_loop_pressure":ghost,"dream_state_eligible":dream,"chi_required":corr},
            "correction_gate":{"required":corr},"cold_storage_gate":{"route":"spc_cold_storage_required" if cb else ("dream_state_quarantine_candidate" if dream else "active_stack_dry_run_candidate"),"must_archive":cb,"ghost_loop_pressure":ghost},
            "score_components":{"circuit_breaker_zeroed_score":cb},"phase_state":{"phase_path_hypothesis":path,"transition_warnings":[]}}

chk("route_active",route_candidate(mk())["route"]==ROUTE_ACTIVE_STACK)
chk("route_corr",route_candidate(mk(corr=True))["route"]=="correction_queue")
chk("route_cb_spc",route_candidate(mk(cb=True))["route"]==ROUTE_SPC_COLD_STORAGE)
chk("route_ghost",route_candidate(mk(ghost=0.40))["route"]==ROUTE_GHOST_LOOP)
chk("route_phi5phi8",route_candidate(mk(path=["Φ5","Φ8"],eps=0.60))["route"]==ROUTE_SPC_COLD_STORAGE)
chk("no_projection",all(not route_candidate(mk(cb=s=="spc",ghost=0.40 if s=="ghost" else 0.0))["projection_allowed"] for s in ["ok","spc","ghost"]))

# Behavior tests
r=subprocess.run([sys.executable,"scripts/test_patch265R_containment_router.py"],
    capture_output=True,text=True,cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chk("behavior_59",r.returncode==0,r.stdout[-100:] if r.returncode else "")

# main.py preserved routes + new endpoint
REQUIRED=["/api/rmc/route-manifest","/api/rmc/llm-renderer/status","/api/rmc/context-search-test",
          "/api/rmc/context-duplicates","/api/rmc/context-export-manifest","/api/rmc/latest-memory-writes",
          "/api/rmc/namespaces","/api/rmc/chroma-status","/api/rmc/glyph-renderer/status",
          "/api/rmc/phase-glyph","/api/rmc/glyph-packet","/api/rmc/promotion-path/status",
          "/api/rmc/promotion-path/preview","/api/rmc/promotion-path/promote",
          "/api/rmc/active-loop-state","/api/rmc/pipeline-summary","/api/rmc/containment-router"]
mp=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"main.py")
if os.path.exists(mp):
    ms=open(mp).read()
    for ep in REQUIRED: chk(f"ROUTE_{ep.split('/')[-1][:18]}",f'"{ep}"' in ms)
    chk("HANDLER_exists","_p265_rmc_containment_router_v1" in ms)
    chk("DO_GET_wired","_p265_rmc_containment_router_v1(self.path)" in ms)
    chk("ROUTE_MANIFEST_entry",'"containment_router"' in ms and '"path":"/api/rmc/containment-router"' in ms)
    chk("MAIN_compiles",subprocess.run([sys.executable,"-m","py_compile",mp],capture_output=True).returncode==0)

passed=sum(1 for _,v,_ in results if v==PASS)
failed=sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 265R VERIFIER")
print("─"*60)
for n,v,d in results:
    print(f"  {'✓' if v==PASS else '✗'} [{v}] {n}"+(f"\n        {d}" if d and v==FAIL else ""))
print("─"*60)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0: print("\nRESULT: PATCH_265R_VERIFY_OK"); sys.exit(0)
else: print(f"\nRESULT: PATCH_265R_VERIFY_FAIL ({failed})"); sys.exit(1)
