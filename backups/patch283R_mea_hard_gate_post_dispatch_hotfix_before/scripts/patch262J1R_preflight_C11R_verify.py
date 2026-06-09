#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C11R.

C11R repairs the C11 behavior-test import path and hardens Algorithm 6 by
making feedback_t a first-class memory object in both dry-run planning and
explicitly approved gated commits.
"""
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
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except Exception:
        return ""


def run_script(rel: str, expect: str) -> None:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ok = proc.returncode == 0 and expect in proc.stdout
    add(rel.replace("/", "_") + "_passes", ok, proc.stdout.strip()[-1600:])


def main() -> int:
    print("PATCH 262J1R-PREFLIGHT-C11R VERIFY")
    print("─" * 72)
    required = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/active_loop_state.py",
        "rmc_engine_v1/memory_writer.py",
        "scripts/test_rmc_active_loop_state_C11.py",
        "scripts/test_rmc_memory_writer_C7.py",
        "scripts/test_rmc_memory_writer_C8.py",
        "scripts/patch262J1R_preflight_C11_verify.py",
        "scripts/patch262J1R_preflight_C11R_verify.py",
        "scripts/README_patch262J1R_preflight_C11R.md",
        "SHA256SUMS.txt",
    ]
    for rel in required:
        add(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

    active_test = text("scripts/test_rmc_active_loop_state_C11.py")
    memory = text("rmc_engine_v1/memory_writer.py")
    active = text("rmc_engine_v1/active_loop_state.py")
    sha = text("SHA256SUMS.txt")

    add("active_loop_test_import_path_repaired", "sys.path.insert" in active_test and "parents[1]" in active_test)
    add("active_loop_engine_still_C11", "rmc_active_loop_state_v1_patch262J1R_preflight_C11" in active)
    add("active_loop_is_read_only", ("writes_files\": False" in active or '"writes_files": False' in active))

    add("memory_writer_dry_run_version_C11R", "rmc_memory_writer_dry_run_v2_patch262J1R_preflight_C11R_feedback_t" in memory)
    add("gated_writer_version_C11R", "rmc_gated_memory_writer_v2_patch262J1R_preflight_C11R_feedback_t" in memory)
    add("feedback_required_fields_present", "REQUIRED_FEEDBACK_FIELDS" in memory and "feedback_id" in memory and "retrieval_tags" in memory)
    add("feedback_update_formula_present", "M_{t+1} = M_t ∪ {T_t, μ_t, R_t, feedback_t}" in memory)
    add("feedback_object_builder_present", "def _build_feedback_object" in memory and "feedback_t" in memory)
    add("feedback_preview_in_W_t", "feedback_object_preview" in memory and "feedback_target_preview" in memory)
    add("feedback_commit_path_present", '"feedback_object"' in memory and "feedback_objects" in memory)
    add("feedback_no_fake_user_feedback", "user_feedback_present\": False" in memory or '"user_feedback_present": False' in memory)
    add("gated_writer_requires_approval", "APPROVE_RMC_MEMORY_WRITE" in memory and "approval_token" in memory)
    add("gated_writer_path_guard_present", "_ensure_inside_root" in memory and "unsafe_target_path" in memory)
    add("no_llm_chroma_shell_added", not re.search(r"openai|anthropic|ollama|chromadb|requests\.|subprocess|os\.system|socket", memory, re.I))
    add("sha_excludes_pycache_pyc_venv_node_modules", not re.search(r"__pycache__|\.pyc|\.venv|node_modules|dist", sha))

    proc = subprocess.run([
        sys.executable, "-m", "py_compile",
        str(ROOT / "main.py"),
        str(ROOT / "rmc_engine_v1/__init__.py"),
        str(ROOT / "rmc_engine_v1/active_loop_state.py"),
        str(ROOT / "rmc_engine_v1/memory_writer.py"),
        str(ROOT / "scripts/test_rmc_active_loop_state_C11.py"),
        str(ROOT / "scripts/test_rmc_memory_writer_C7.py"),
        str(ROOT / "scripts/test_rmc_memory_writer_C8.py"),
        str(ROOT / "scripts/patch262J1R_preflight_C11R_verify.py"),
    ], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    add("py_compile_changed_files", proc.returncode == 0, proc.stdout.strip()[-1000:])

    run_script("scripts/test_rmc_active_loop_state_C11.py", "RESULT: active_loop_state_C11_behavior_tests_pass=True")
    run_script("scripts/test_rmc_memory_writer_C7.py", "RESULT: memory_writer_C7_behavior_tests_pass=True")
    run_script("scripts/test_rmc_memory_writer_C8.py", "RESULT: memory_writer_C8_behavior_tests_pass=True")

    print("─" * 72)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C11R_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C11R_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
