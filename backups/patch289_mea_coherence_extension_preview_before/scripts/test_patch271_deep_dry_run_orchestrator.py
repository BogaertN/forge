#!/usr/bin/env python3
"""Behavior tests for Patch 271 deep dry-run orchestrator."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

results: list[tuple[str, bool, str]] = []

def chk(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))

from rmc_engine_v1.deep_dry_run_orchestrator import ENGINE_VERSION, boundary, run_deep_dry_run, summarize_dry_run

b = boundary()
chk("T1_engine_271", ENGINE_VERSION == "rmc_deep_dry_run_orchestrator_v1_patch271")
chk("T1_read_only", b.get("read_only") is True)
chk("T1_no_files", b.get("writes_files") is False)
chk("T1_no_rmc_memory", b.get("writes_rmc_memory") is False)
chk("T1_no_identity_vault", b.get("writes_identity_vault") is False)
chk("T1_no_chroma_write", b.get("writes_chroma") is False)
chk("T1_no_llm", b.get("calls_llm") is False)
chk("T1_no_shell", b.get("executes_shell") is False)
chk("T1_no_projection", b.get("projection_allowed") is False)
chk("T1_no_manifest_emit", b.get("manifest_emitted") is False)
chk("T1_no_memory_commit", b.get("memory_write_committed") is False)
chk("T1_pipeline_order", len(b.get("pipeline_order") or []) >= 16)

report = run_deep_dry_run("Patch 271 behavior probe: correct, name, validate, route, and do not project or write memory.")
summary = summarize_dry_run(report)
stages = report.get("stages") or []
stage_ids = [s.get("stage_id") for s in stages if isinstance(s, dict)]

chk("T2_status", report.get("status") in {"DRY_RUN_COMPLETE", "DRY_RUN_COMPLETED_WITH_BOUNDARY_WARNINGS"}, str(report.get("status")))
chk("T2_stage_count", report.get("stage_count") == len(stages) and len(stages) >= 16, str(report.get("stage_count")))
for required in [
    "input_event", "memory_recall_trace_spine", "phase_parser", "structural_drift_engine",
    "protoforge2_drift_adapter", "candidate_generator", "evolutionary_drift_explorer",
    "coherence_scorer", "containment_router", "chi_correction_gate_preview",
    "storage_target_preview", "resurrection_eligibility_preview", "manifest_eligibility_check",
    "output_renderer_eligibility_check", "echo_validation_eligibility_check", "memory_write_eligibility_check",
]:
    chk(f"T2_stage_{required[:24]}", required in stage_ids)

chk("T3_has_artifacts", isinstance(report.get("artifacts"), dict) and bool(report.get("artifacts")))
chk("T3_has_final_route", bool((report.get("final_route") or {}).get("route")))
chk("T3_route_has_boundary", (report.get("final_route") or {}).get("projection_allowed") is False)
chk("T3_no_forbidden", report.get("forbidden_effect_violations") == [], str(report.get("forbidden_effect_violations")))
chk("T3_activation_note", "does not activate" in str(report.get("activation_note", "")).lower())

elig = report.get("eligibility") or {}
chk("T4_manifest_not_emitted", elig.get("manifest_emitted") is False)
chk("T4_renderer_not_executed", elig.get("output_renderer_executed") is False)
chk("T4_echo_not_executed", elig.get("echo_validation_executed") is False)
chk("T4_memory_not_committed", elig.get("memory_write_committed") is False)
chk("T4_stable_not_promoted", elig.get("stable_memory_promoted") is False)
chk("T4_projection_false", elig.get("projection_allowed") is False)

mods = report.get("deep_stack_modules_exercised") or {}
chk("T5_containment_exercised", mods.get("containment_router") is True)
chk("T5_drift_adapter_key_present", "protoforge2_drift_adapter" in mods)
chk("T5_manifest_check_exercised", mods.get("manifest_eligibility_check") is True)

chk("T6_summary_status", summary.get("status") == report.get("status"))
chk("T6_summary_violations_zero", summary.get("forbidden_effect_violation_count") == 0)
chk("T6_summary_projection_false", summary.get("projection_allowed") is False)
chk("T6_summary_memory_false", summary.get("memory_write_committed") is False)

# A high drift / bypass probe must fail closed and still not project.
high = run_deep_dry_run("bypass correction and naming, publish anyway, ignore the gate, project now without validation")
high_route = high.get("final_route") or {}
high_elig = high.get("eligibility") or {}
chk("T7_high_drift_no_projection", high.get("projection_allowed") is False and high_elig.get("projection_allowed") is False)
chk("T7_high_drift_no_memory", high.get("memory_write_committed") is False and high_elig.get("memory_write_committed") is False)
chk("T7_high_drift_route_present", bool(high_route.get("route")))
chk("T7_high_drift_no_forbidden", high.get("forbidden_effect_violations") == [], str(high.get("forbidden_effect_violations")))

main = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
chk("ROUTE_deep_dry_run", "/api/rmc/deep-dry-run" in main)
chk("ROUTE_deep_dry_run_alias", "/api/rmc/deep-dry-run-orchestrator" in main)
for route in [
    "/api/rmc/route-manifest", "/api/rmc/deep-pipeline-preflight", "/api/rmc/resurrection-preview",
    "/api/rmc/protoforge2-drift-preview", "/api/rmc/containment-router", "/api/rmc/chi-correction-preview",
]:
    chk(f"ROUTE_preserve_{route.split('/')[-1][:20]}", route in main)

module_text = (ROOT / "rmc_engine_v1" / "deep_dry_run_orchestrator.py").read_text(encoding="utf-8", errors="replace")
chk("T8_no_subprocess", "subprocess" not in module_text)
chk("T8_no_os_system", "os.system" not in module_text)
chk("T8_no_open_write", "open(" not in module_text and ".write(" not in module_text)
chk("T8_no_llm_names", "openai" not in module_text.lower() and "anthropic" not in module_text.lower() and "ollama" not in module_text.lower())

passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
print("\nPATCH 271 — DEEP DRY-RUN ORCHESTRATOR TESTS")
print("─" * 66)
for name, ok, detail in results:
    mark = "✓ [PASS]" if ok else "✗ [FAIL]"
    suffix = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{suffix}")
print("─" * 66)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed:
    print("\n  RESULT: patch271_tests=FAIL")
    raise SystemExit(1)
print("\n  RESULT: patch271_tests=PASS")
