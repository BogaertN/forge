#!/usr/bin/env python3
"""Patch 265R — Containment Router Tests (rebased against live main.py).
Run: python scripts/test_patch265R_containment_router.py
"""
import sys, os, subprocess, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rmc_engine_v1.containment_router import (
    route_candidate, boundary, check_permission, assert_not_sealed, ContainmentViolation,
    ROUTE_ACTIVE_STACK, ROUTE_CORRECTION_QUEUE, ROUTE_SPC_COLD_STORAGE,
    ROUTE_DREAM_STATE_QUARANTINE, ROUTE_DRIFT_ARCHIVE, ROUTE_GHOST_LOOP,
    SEALED_ROUTES, THRESHOLDS,
)
PASS,FAIL="PASS","FAIL"
results=[]
def chk(n,ok,d=""): results.append((n,PASS if ok else FAIL,d))

def mk(cb=False,ghost=0.0,dream=False,corr=False,eps=0.10,path=None,over=False,breach=False,locked=False):
    path=path or ["Φ1","Φ3","Φ6","Φ7"]
    return {"candidate_id":"t","epsilon_s":eps,"coherence_score":0.0 if cb else 0.80,
            "overextended":over,"math_terms":{"circuit_breaker":cb,"chi_required":corr,
            "ghost_loop_pressure":ghost,"dream_state_eligible":dream},
            "correction_gate":{"required":corr or cb,"chi_t_required":corr},
            "cold_storage_gate":{"route":"spc_cold_storage_required" if cb else ("dream_state_quarantine_candidate" if dream else "active_stack_dry_run_candidate"),
            "must_archive":cb,"cold_storage_pressure":0.08,"ghost_loop_pressure":ghost},
            "score_components":{"circuit_breaker_zeroed_score":cb},
            "phase_state":{"phase_path_hypothesis":path,"transition_warnings":[]},
            "breach":breach,"resurrection_limit_exceeded":locked}

b=boundary()
chk("B_read_only",b["read_only"] is True)
chk("B_six_routes",len(b["routes"])==6)
chk("B_four_sealed",len(b["sealed_routes"])==4)
chk("B_babel_named","babel_cutoff_doctrine" in b["thresholds"])
chk("B_no_writes",b["writes_files"] is False)
chk("B_no_llm",b["calls_llm"] is False)

r=route_candidate(mk()); chk("T1_active_stack",r["route"]==ROUTE_ACTIVE_STACK)
chk("T1_no_containment",r["containment_required"] is False)
r=route_candidate(mk(corr=True)); chk("T2_correction_queue",r["route"]==ROUTE_CORRECTION_QUEUE)
chk("T2_manifest_blocked",r["manifest_compile_allowed"] is False)
r=route_candidate(mk(cb=True)); chk("T3_spc_cb",r["route"]==ROUTE_SPC_COLD_STORAGE)
chk("T3_sealed",r["is_sealed"] is True)
chk("T3_no_projection",r["projection_allowed"] is False)
r=route_candidate(mk(over=True,eps=0.40)); chk("T4_overextended_not_active",r["route"]!=ROUTE_ACTIVE_STACK)
chk("T4_overextended_no_proj",r["projection_allowed"] is False)
r=route_candidate(mk(dream=True,eps=0.48)); chk("T5_dream_quarantine",r["route"]==ROUTE_DREAM_STATE_QUARANTINE)
chk("T5_dream_sealed",r["is_sealed"] is True)
r=route_candidate({}); chk("T6_drift_archive_empty",r["route"]==ROUTE_DRIFT_ARCHIVE)
chk("T6_drift_no_proj",r["projection_allowed"] is False)
r=route_candidate(mk(ghost=0.40)); chk("T7_ghost_loop",r["route"]==ROUTE_GHOST_LOOP)
chk("T7_ghost_sealed",r["is_sealed"] is True)
chk("T7_ghost_no_reentry",r["manifest_compile_allowed"] is False)
r=route_candidate(mk(path=["Φ5","Φ8"],eps=0.60)); chk("T8_phi5_phi8_spc",r["route"]==ROUTE_SPC_COLD_STORAGE)
chk("T8_phi5_phi8_no_proj",r["projection_allowed"] is False)
r=route_candidate(mk(path=["Φ1","Φ3","Φ7"])); chk("T9_phi7_no_phi6_correction",r["route"] in (ROUTE_CORRECTION_QUEUE,ROUTE_SPC_COLD_STORAGE))
chk("T9_phi7_no_proj",r["projection_allowed"] is False)
r=route_candidate(mk(path=["Φ1","Φ3","Φ8"])); chk("T10_phi8_no_gates_spc",r["route"]==ROUTE_SPC_COLD_STORAGE)
chk("T10_phi8_no_proj",r["projection_allowed"] is False)
# memory write before echo validation
mwbe=mk(corr=True); mwbe["memory_write_allowed"]=True; mwbe["echo_validated"]=False
r=route_candidate(mwbe); chk("T11_mwbe_blocked",r["memory_write_allowed"] is False)
# all sealed no projection
for sealed in sorted(SEALED_ROUTES):
    pkt=mk(cb=True) if sealed==ROUTE_SPC_COLD_STORAGE else mk(ghost=0.40) if sealed==ROUTE_GHOST_LOOP else mk(dream=True,eps=0.48) if sealed==ROUTE_DREAM_STATE_QUARANTINE else {}
    rv=route_candidate(pkt)
    if rv["route"]==sealed: chk(f"T12_sealed_{sealed[:10]}_no_proj",rv["projection_allowed"] is False)
# assert_not_sealed
for sealed in sorted(SEALED_ROUTES):
    try: assert_not_sealed(sealed,"manifest"); chk(f"T13_raises_{sealed[:10]}",False)
    except ContainmentViolation: chk(f"T13_raises_{sealed[:10]}",True)
try: assert_not_sealed(ROUTE_ACTIVE_STACK,"manifest"); chk("T13_active_no_raise",True)
except: chk("T13_active_no_raise",False)

# No writes, no shell, no Chroma, no LLM
src=inspect.getsource(sys.modules["rmc_engine_v1.containment_router"])
chk("T14_no_subprocess","import subprocess" not in src)
chk("T14_no_llm","openai" not in src and "anthropic" not in src)
chk("T14_no_chroma","chromadb" not in src)

# ── Current route preservation test ──────────────────────────────────────────
REQUIRED_ROUTES = [
    "/api/rmc/route-manifest", "/api/rmc/llm-renderer/status",
    "/api/rmc/context-search-test", "/api/rmc/context-duplicates",
    "/api/rmc/context-export-manifest", "/api/rmc/latest-memory-writes",
    "/api/rmc/namespaces", "/api/rmc/chroma-status",
    "/api/rmc/glyph-renderer/status", "/api/rmc/phase-glyph",
    "/api/rmc/glyph-packet", "/api/rmc/promotion-path/status",
    "/api/rmc/promotion-path/preview", "/api/rmc/promotion-path/promote",
    "/api/rmc/active-loop-state", "/api/rmc/pipeline-summary",
    "/api/rmc/containment-router",
]
mp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
if os.path.exists(mp):
    ms = open(mp).read()
    for ep in REQUIRED_ROUTES:
        chk(f"PRESERVE_{ep.split('/')[-1][:20]}", f'"{ep}"' in ms or f"'{ep}'" in ms)
    chk("MAIN_compiles", subprocess.run([sys.executable,"-m","py_compile",mp],capture_output=True).returncode==0)

passed=sum(1 for _,v,_ in results if v==PASS)
failed=sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 265R — CONTAINMENT ROUTER TESTS")
print("─"*65)
for n,v,d in results:
    print(f"  {'✓' if v==PASS else '✗'} [{v}] {n}"+(f"\n        {d}" if d else ""))
print("─"*65)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0: print("\n  RESULT: patch265R_tests=PASS"); sys.exit(0)
else: print("\n  RESULT: patch265R_tests=FAIL"); sys.exit(1)
