#!/usr/bin/env python3
"""Patch 270R — Deep Pipeline Preflight Tests.
Run: python scripts/test_patch270_deep_pipeline_preflight.py
"""
import sys, os, inspect, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rmc_engine_v1.deep_pipeline_preflight import (
    run_preflight, boundary, PIPELINE_STAGES, HARD_BOUNDARIES,
    FORBIDDEN_SHORTCUTS, ENGINE_VERSION,
)

PASS, FAIL = "PASS", "FAIL"
results = []
def chk(n, ok, d=""): results.append((n, PASS if ok else FAIL, d))


# ── T1: Boundary ──────────────────────────────────────────────────────────────
b = boundary()
chk("T1_patch_270",          "270" in b.get("patch",""))
chk("T1_read_only",          b["read_only"] is True)
chk("T1_no_writes",          b["writes_files"] is False)
chk("T1_no_memory",          b["writes_rmc_memory"] is False)
chk("T1_no_activate",        b["activates_pipeline"] is False)
chk("T1_no_llm",             b["calls_llm"] is False)
chk("T1_no_shell",           b["executes_shell"] is False)
chk("T1_no_chroma",          b["queries_chroma"] is False)
chk("T1_no_iv",              b["writes_identity_vault"] is False)
chk("T1_7_boundaries",       b["hard_boundaries_count"] == 7)
chk("T1_forbidden_list",     b["forbidden_shortcuts_count"] >= 5)


# ── T2: Stage registry ────────────────────────────────────────────────────────
stage_ids = [s[0] for s in PIPELINE_STAGES]
chk("T2_containment_router", "containment_router" in stage_ids)
chk("T2_manifest_compiler",  "manifest_compiler" in stage_ids)
chk("T2_chi_gate",           "chi_correction_gate" in stage_ids)
chk("T2_spc",                "spc_cold_storage" in stage_ids)
chk("T2_ghost",              "ghost_loop_containment" in stage_ids)
chk("T2_resurrection",       "resurrection_engine" in stage_ids)
chk("T2_pf2_connector",      "protoforge2_connector" in stage_ids)
chk("T2_containment_before_manifest",
    stage_ids.index("containment_router") < stage_ids.index("manifest_compiler"),
    f"containment at {stage_ids.index('containment_router')}, manifest at {stage_ids.index('manifest_compiler')}")
chk("T2_echo_before_memory",
    stage_ids.index("echo_validator") < stage_ids.index("memory_writer"))


# ── T3: All installed deep modules reported ───────────────────────────────────
# Inject override set containing all deep patches
deep_mods = {
    "rmc_engine_v1.containment_router",
    "rmc_engine_v1.spc_cold_storage",
    "rmc_engine_v1.drift_archive",
    "rmc_engine_v1.dream_state_quarantine",
    "rmc_engine_v1.ghost_loop_containment",
    "rmc_engine_v1.chi_correction_gate",
    "rmc_engine_v1.protoforge2_drift_connector",
    "rmc_engine_v1.resurrection_engine",
}
r = run_preflight(_override_available=deep_mods)
chk("T3_installed_has_containment",   "containment_router" in r["installed_modules"])
chk("T3_installed_has_chi",           "chi_correction_gate" in r["installed_modules"])
chk("T3_installed_has_spc",           "spc_cold_storage" in r["installed_modules"])
chk("T3_installed_has_ghost",         "ghost_loop_containment" in r["installed_modules"])
chk("T3_installed_has_resurrection",  "resurrection_engine" in r["installed_modules"])
chk("T3_has_pipeline_stages",         isinstance(r["pipeline_stages"], list) and len(r["pipeline_stages"]) > 10)
chk("T3_has_hard_boundaries",         len(r["hard_boundaries"]) == 7)
chk("T3_has_forbidden",               len(r["forbidden_shortcuts"]) >= 5)
chk("T3_has_integration_plan",        len(r["integration_plan"]) > 0)
chk("T3_no_writes",                   r["writes_rmc_memory"] is False)
chk("T3_no_activate",                 r["activates_pipeline"] is False)
chk("T3_boundary_verifications_pass", r.get("boundary_verifications_passed") is True)
chk("T3_no_boundary_failures",        len(r.get("boundary_verification_failures", [])) == 0)


# ── T4: Missing resurrection_engine identified (no override) ──────────────────
# Inject only the core deep mods WITHOUT resurrection_engine
no_resurrection = deep_mods - {"rmc_engine_v1.resurrection_engine"}
r = run_preflight(_override_available=no_resurrection)
chk("T4_resurrection_not_installed",  "resurrection_engine" not in r["installed_modules"])
# resurrection_engine is optional, so missing it shouldn't be in missing_required
chk("T4_resurrection_optional",       "resurrection_engine" not in r.get("missing_modules", []))


# ── T5: activation_ready false until required modules present ─────────────────
# Inject only a subset — missing some required core modules
partial = {"rmc_engine_v1.containment_router", "rmc_engine_v1.chi_correction_gate"}
r = run_preflight(_override_available=partial)
chk("T5_not_ready_partial",           r["activation_ready"] is False)
chk("T5_has_blocking_reasons",        len(r.get("blocking_reasons", [])) > 0)


# ── T6: Hard boundaries listed ────────────────────────────────────────────────
r = run_preflight(_override_available=deep_mods)
hb_ids = [h["id"] for h in r["hard_boundaries"]]
chk("T6_containment_before_manifest", "containment_before_manifest" in hb_ids)
chk("T6_sealed_no_manifest",          "sealed_routes_no_manifest" in hb_ids)
chk("T6_chi_no_projection",           "chi_t_no_direct_projection" in hb_ids)
chk("T6_resurrection_no_runtime",     "resurrection_no_runtime_activation" in hb_ids)
chk("T6_memory_after_echo",           "memory_write_after_echo" in hb_ids)
chk("T6_stable_memory_gated",         "stable_memory_gated" in hb_ids)
chk("T6_pf2_no_replace_drift",        "pf2_no_replace_structural_drift" in hb_ids)


# ── T7: Forbidden shortcuts listed ────────────────────────────────────────────
r = run_preflight(_override_available=deep_mods)
fs = r["forbidden_shortcuts"]
chk("T7_no_skip_containment",
    any("skip_containment_router" in s for s in fs))
chk("T7_no_manifest_from_sealed",
    any("manifest_compiler_with_spc" in s for s in fs))
chk("T7_no_chi_projection",
    any("project_from_chi_t" in s for s in fs))
chk("T7_no_ungate_memory",
    any("memory_without" in s for s in fs))


# ── T8: PF2 connector reported correctly ─────────────────────────────────────
r_with_pf2 = run_preflight(_override_available=deep_mods)
r_no_pf2   = run_preflight(_override_available=deep_mods - {"rmc_engine_v1.protoforge2_drift_connector"})
chk("T8_pf2_in_installed",    "protoforge2_connector" in r_with_pf2["installed_modules"])
chk("T8_pf2_not_required",    "protoforge2_connector" not in r_with_pf2.get("missing_modules",[]))


# ── T9: No writes, no shell, no Chroma, no Identity Vault, no LLM ────────────
src = inspect.getsource(sys.modules["rmc_engine_v1.deep_pipeline_preflight"])
chk("T9_no_subprocess",  "import subprocess" not in src and "subprocess.run(" not in src)
chk("T9_no_os_system",   "os.system(" not in src)
chk("T9_no_llm",         "openai" not in src and "anthropic" not in src)
chk("T9_no_chroma",      "chromadb" not in src)
chk("T9_no_iv",          "identity_vault" not in src.lower().replace("writes_identity_vault",""))
chk("T9_no_open_write",  'open(' not in src or '"w"' not in src)


# ── T10: Route preservation + new endpoint ────────────────────────────────────
REQUIRED = [
    "/api/rmc/route-manifest", "/api/rmc/active-loop-state", "/api/rmc/pipeline-summary",
    "/api/rmc/containment-router", "/api/rmc/spc-cold-storage/preview",
    "/api/rmc/chi-correction-preview", "/api/rmc/protoforge2-drift-status",
    "/api/rmc/resurrection-preview", "/api/rmc/deep-pipeline-preflight",
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
print(f"\nPATCH 270R — DEEP PIPELINE PREFLIGHT TESTS")
print("─"*65)
for n,v,d in results:
    print(f"  {'✓' if v==PASS else '✗'} [{v}] {n}" + (f"\n        {d}" if d else ""))
print("─"*65)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0: print("\n  RESULT: patch270R_tests=PASS"); sys.exit(0)
else: print("\n  RESULT: patch270R_tests=FAIL"); sys.exit(1)
