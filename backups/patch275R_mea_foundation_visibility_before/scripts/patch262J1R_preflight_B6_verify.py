#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B6 — RMC Trace Spine + Memory Recaller."""
from __future__ import annotations

import importlib
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(condition), detail))


def main() -> int:
    files = [
        ROOT / "main.py",
        ROOT / "rmc_engine_v1" / "memory_recaller.py",
        ROOT / "rmc_engine_v1" / "phase_parser.py",
        ROOT / "rmc_engine_v1" / "resonance_lexicon.py",
        ROOT / "rmc_engine_v1" / "drift_engine.py",
        ROOT / "scripts" / "test_rmc_memory_recaller_behavior.py",
    ]
    for path in files:
        check(f"file_exists:{path.relative_to(ROOT)}", path.exists(), str(path))
        if path.exists() and path.suffix == ".py":
            try:
                py_compile.compile(str(path), doraise=True)
                check(f"py_compile:{path.relative_to(ROOT)}", True)
            except Exception as exc:
                check(f"py_compile:{path.relative_to(ROOT)}", False, str(exc))

    try:
        mod = importlib.import_module("rmc_engine_v1.memory_recaller")
        check("import_memory_recaller", True)
        boundary = mod.memory_recaller_boundary()
        check("boundary_no_llm", boundary.get("calls_llm") is False)
        check("boundary_no_writes", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
        check("boundary_no_chroma", boundary.get("queries_chroma") is False and boundary.get("reads_db_files") is False)
        check("boundary_engine_version_b6", "B6" in boundary.get("engine_version", "") or "preflight_B6" in boundary.get("engine_version", ""), boundary.get("engine_version", ""))
        sample = mod.recall_memory("Correct drift before projection", {"source_kind": "verifier"}, root=ROOT, limit=3)
        check("sample_recall_ok", sample.get("status") == "OK")
        check("sample_recall_has_input_event", bool(sample.get("input_event", {}).get("event_id")))
        trace = mod.build_trace_spine("Correct drift before projection", {"source_kind": "verifier"}, root=ROOT, limit=3)
        check("sample_trace_ok", trace.get("status") == "OK")
        check("sample_trace_has_symbolic_trace", bool(trace.get("symbolic_trace", {}).get("trace_id")))
        check("sample_trace_no_render", trace.get("trace_spine_readiness", {}).get("rendering_allowed") is False)
    except Exception as exc:
        check("import_or_sample_memory_recaller", False, str(exc))

    main_text = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    check("main_has_memory_recaller_endpoint", "/api/rmc/memory-recaller" in main_text)
    check("main_has_trace_spine_endpoint", "/api/rmc/trace-spine" in main_text)
    check("main_routes_memory_recaller", "_p262b6_rmc_memory_recaller_v1" in main_text)
    check("main_routes_trace_spine", "_p262b6_rmc_trace_spine_v1" in main_text)
    check("output_state_slot_present", "rmc_trace_spine_slot" in main_text)

    # Direct behavior test.
    test_path = ROOT / "scripts" / "test_rmc_memory_recaller_behavior.py"
    if test_path.exists():
        proc = subprocess.run([sys.executable, str(test_path)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(proc.stdout.strip())
        check("behavior_test_passes", proc.returncode == 0, proc.stdout[-500:])

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = [(n, d) for n, ok, d in CHECKS if not ok]
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failed)}")
    for name, detail in failed:
        print(f"FAIL: {name} {detail}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_B6_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_B6_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
