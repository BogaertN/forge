#!/usr/bin/env python3
"""Patch 271 verifier — RMC Deep Pipeline Dry-Run Orchestrator."""
from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

results: list[tuple[str, bool, str]] = []

def chk(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))

try:
    from rmc_engine_v1.deep_dry_run_orchestrator import (
        ENGINE_VERSION, boundary, run_deep_dry_run, summarize_dry_run,
    )
    b = boundary()
    r = run_deep_dry_run()
    s = summarize_dry_run(r)
    chk("import_ok", True)
    chk("engine_271", ENGINE_VERSION == "rmc_deep_dry_run_orchestrator_v1_patch271", ENGINE_VERSION)
    chk("boundary_read_only", b.get("read_only") is True)
    chk("no_writes", b.get("writes_files") is False and b.get("writes_rmc_memory") is False)
    chk("no_projection", b.get("projection_allowed") is False)
    chk("no_memory_commit", b.get("memory_write_committed") is False)
    chk("no_llm", b.get("calls_llm") is False)
    chk("no_shell", b.get("executes_shell") is False)
    chk("dry_run_status", r.get("status") in {"DRY_RUN_COMPLETE", "DRY_RUN_COMPLETED_WITH_BOUNDARY_WARNINGS"}, str(r.get("status")))
    chk("has_16_stages", int(r.get("stage_count") or 0) >= 16, str(r.get("stage_count")))
    chk("has_final_route", bool((r.get("final_route") or {}).get("route")))
    chk("no_forbidden_violations", r.get("forbidden_effect_violations") == [], str(r.get("forbidden_effect_violations")))
    chk("manifest_not_emitted", (r.get("eligibility") or {}).get("manifest_emitted") is False)
    chk("projection_false", r.get("projection_allowed") is False)
    chk("summary_ok", s.get("engine_version") == ENGINE_VERSION and s.get("forbidden_effect_violation_count") == 0)
except Exception as exc:
    chk("import_or_run", False, repr(exc))

main_text = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
init_text = (ROOT / "rmc_engine_v1" / "__init__.py").read_text(encoding="utf-8", errors="replace")
module_text = (ROOT / "rmc_engine_v1" / "deep_dry_run_orchestrator.py").read_text(encoding="utf-8", errors="replace")

chk("main_compiles_ast", ast.parse(main_text) is not None)
chk("route_manifest_has_deep_dry_run", '"path":"/api/rmc/deep-dry-run"' in main_text or '"/api/rmc/deep-dry-run"' in main_text)
chk("handler_has_deep_dry_run", "_p271_rmc_deep_dry_run_v1" in main_text and "/api/rmc/deep-dry-run" in main_text)
chk("old_route_manifest_preserved", "/api/rmc/route-manifest" in main_text)
chk("pf2_268S3_preserved", "rmc_protoforge2_drift_connector_v2_patch268S3" in (ROOT / "rmc_engine_v1" / "protoforge2_drift_connector.py").read_text(encoding="utf-8", errors="replace"))
chk("resurrection_route_preserved", "/api/rmc/resurrection-preview" in main_text)
chk("deep_preflight_route_preserved", "/api/rmc/deep-pipeline-preflight" in main_text)
chk("registry_updated", "deep_dry_run_orchestrator" in init_text and "rmc_engine_v1_patch271" in init_text)
chk("module_no_subprocess", "subprocess" not in module_text)
chk("module_no_os_system", "os.system" not in module_text)
chk("module_no_open_write", "open(" not in module_text and ".write(" not in module_text)
chk("module_no_llm", "openai" not in module_text.lower() and "anthropic" not in module_text.lower() and "ollama" not in module_text.lower())

passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
print(f"\nPATCH 271 VERIFIER  Total:{len(results)} Passed:{passed} Failed:{failed}")
for name, ok, detail in results:
    mark = "✓ [PASS]" if ok else "✗ [FAIL]"
    suffix = f" — {detail}" if detail else ""
    print(f"  {mark} {name}{suffix}")
if failed:
    print(f"RESULT: PATCH_271_VERIFY_FAIL ({failed})")
    raise SystemExit(1)
print("RESULT: PATCH_271_VERIFY_OK")
