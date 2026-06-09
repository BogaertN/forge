#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C11 — Active Loop State / L_t."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))
    print(("[PASS]" if ok else "[FAIL]") + f" {name}" + (f" :: {detail}" if detail else ""))


def text(rel: str) -> str:
    path = ROOT / rel
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def run_script(rel: str, expect: str) -> None:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ok = proc.returncode == 0 and expect in proc.stdout
    add(rel.replace("/", "_") + "_passes", ok, proc.stdout.strip()[-1200:])


def main() -> int:
    print("PATCH 262J1R-PREFLIGHT-C11 VERIFY")
    print("─" * 72)
    required = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/active_loop_state.py",
        "scripts/test_rmc_active_loop_state_C11.py",
        "scripts/patch262J1R_preflight_C11_verify.py",
        "scripts/README_patch262J1R_preflight_C11.md",
        "SHA256SUMS.txt",
    ]
    for rel in required:
        add(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

    active = text("rmc_engine_v1/active_loop_state.py")
    main_py = text("main.py")
    init_py = text("rmc_engine_v1/__init__.py")
    sha = text("SHA256SUMS.txt")

    add("active_engine_version_C11", "rmc_active_loop_state_v1_patch262J1R_preflight_C11" in active)
    add("active_has_L_t_formula", "L_t = reconstruct_active_loop" in active)
    add("active_required_current_loop_id", "current_loop_id" in active and "next_expected_step" in active)
    add("active_reads_memory_surface", "memory/rmc_dataset_v1" in active and "review_queue_count" in active)
    add("active_no_write_calls", not re.search(r"\.write_text\(|\.write_bytes\(|open\([^\n]*['\"]w|mkdir\(|os\.system|subprocess|requests\.", active))
    add("active_no_external_calls", not re.search(r"ollama|openai|anthropic|chromadb|vault\.db|requests\.|subprocess|socket|from\s+chrom|import\s+chrom", active, re.I))

    add("main_has_active_loop_kernel", "_p262p_rmc_active_loop_state_kernel" in main_py)
    add("main_route_active_loop_state", '"/api/rmc/active-loop-state"' in main_py)
    add("main_route_loop_state_alias", '"/api/rmc/loop-state"' in main_py)
    add("main_strips_commit_approval", 'q.pop("commit", None)' in main_py and 'q.pop("approval", None)' in main_py)
    add("main_uses_pipeline_summary_include_full", 'q["include_full"] = ["1"]' in main_py)
    add("init_registers_active_loop_state", '"active_loop_state"' in init_py and "read_only_active_loop_state_reconstruction" in init_py)

    add("sha_excludes_pycache_pyc_venv_node_modules", not re.search(r"__pycache__|\.pyc|\.venv|node_modules|dist", sha))

    # Compile focused source files.
    proc = subprocess.run([
        sys.executable, "-m", "py_compile",
        str(ROOT / "main.py"),
        str(ROOT / "rmc_engine_v1/__init__.py"),
        str(ROOT / "rmc_engine_v1/active_loop_state.py"),
        str(ROOT / "scripts/test_rmc_active_loop_state_C11.py"),
    ], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    add("py_compile_changed_files", proc.returncode == 0, proc.stdout.strip()[-800:])

    run_script("scripts/test_rmc_active_loop_state_C11.py", "RESULT: active_loop_state_C11_behavior_tests_pass=True")
    # Guard against breaking the prior compact trace and renderer guardrail surfaces.
    if (ROOT / "scripts/test_rmc_pipeline_summary_C9.py").exists():
        run_script("scripts/test_rmc_pipeline_summary_C9.py", "RESULT: pipeline_summary_C9_behavior_tests_pass=True")
    if (ROOT / "scripts/test_rmc_contract_guardrails_C10.py").exists():
        run_script("scripts/test_rmc_contract_guardrails_C10.py", "RESULT: rmc_contract_guardrails_C10_behavior_tests_pass=True")

    print("─" * 72)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C11_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C11_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
