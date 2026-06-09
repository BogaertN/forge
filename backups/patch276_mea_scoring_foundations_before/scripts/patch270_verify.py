#!/usr/bin/env python3
"""Patch 270R Verifier. Run: python scripts/patch270_verify.py"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASS, FAIL = "PASS", "FAIL"; results = []; chk = lambda n,ok,d="": results.append((n,PASS if ok else FAIL,d))

try:
    from rmc_engine_v1.deep_pipeline_preflight import run_preflight, boundary, PIPELINE_STAGES, HARD_BOUNDARIES
    chk("import_ok", True)
except ImportError as e: chk("import_ok", False, str(e)); sys.exit(1)

b = boundary()
chk("patch_270",       "270" in b.get("patch",""))
chk("read_only",       b["read_only"] is True)
chk("no_activate",     b["activates_pipeline"] is False)
chk("7_boundaries",    b["hard_boundaries_count"] == 7)
chk("no_writes",       b["writes_files"] is False)
chk("no_llm",          b["calls_llm"] is False)

sids = [s[0] for s in PIPELINE_STAGES]
chk("containment_before_manifest",  sids.index("containment_router") < sids.index("manifest_compiler"))
chk("echo_before_memory",           sids.index("echo_validator") < sids.index("memory_writer"))

deep_mods = {"rmc_engine_v1.containment_router","rmc_engine_v1.spc_cold_storage",
             "rmc_engine_v1.drift_archive","rmc_engine_v1.dream_state_quarantine",
             "rmc_engine_v1.ghost_loop_containment","rmc_engine_v1.chi_correction_gate",
             "rmc_engine_v1.protoforge2_drift_connector","rmc_engine_v1.resurrection_engine"}
r = run_preflight(_override_available=deep_mods)
chk("installed_has_containment",  "containment_router" in r["installed_modules"])
chk("installed_has_chi",          "chi_correction_gate" in r["installed_modules"])
chk("has_7_hard_boundaries",      len(r["hard_boundaries"]) == 7)
chk("has_forbidden_shortcuts",    len(r["forbidden_shortcuts"]) >= 5)
chk("no_writes_result",           r["writes_rmc_memory"] is False)
chk("no_activate_result",         r["activates_pipeline"] is False)
chk("boundary_verifications_pass", r.get("boundary_verifications_passed") is True)
chk("no_boundary_failures",        len(r.get("boundary_verification_failures", [])) == 0)

r2 = run_preflight(_override_available={"rmc_engine_v1.containment_router"})
chk("partial_not_ready",          r2["activation_ready"] is False)
chk("has_blocking_reasons",       len(r2.get("blocking_reasons",[])) > 0)

r3 = run_preflight(_override_available=deep_mods - {"rmc_engine_v1.resurrection_engine"})
chk("resurrection_optional",      "resurrection_engine" not in r3.get("missing_modules",[]))

r_bt = subprocess.run([sys.executable,"scripts/test_patch270_deep_pipeline_preflight.py"],
    capture_output=True,text=True,cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chk("behavior_64", r_bt.returncode==0)

REQUIRED=["/api/rmc/deep-pipeline-preflight","/api/rmc/resurrection-preview","/api/rmc/route-manifest"]
mp=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"main.py")
if os.path.exists(mp):
    ms=open(mp).read()
    for ep in REQUIRED: chk(f"ROUTE_{ep.split('/')[-1][:22]}", f'"{ep}"' in ms)
    chk("MAIN_compiles", subprocess.run([sys.executable,"-m","py_compile",mp],capture_output=True).returncode==0)

passed=sum(1 for _,v,_ in results if v==PASS); failed=sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 270R VERIFIER  Total:{len(results)} Passed:{passed} Failed:{failed}")
if failed==0: print("RESULT: PATCH_270R_VERIFY_OK"); sys.exit(0)
else: print(f"RESULT: PATCH_270R_VERIFY_FAIL ({failed})"); sys.exit(1)
