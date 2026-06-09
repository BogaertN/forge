#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C12 — Promotion Path."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" :: {detail}" if detail else ""))
    CHECKS.append((name, ok, detail))


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def file_exists(rel: str) -> None:
    add(f"file_exists_{rel}", (ROOT / rel).exists(), rel)


def no_bad_imports(rel: str) -> None:
    src = text(rel)
    tree = ast.parse(src)
    banned = {"subprocess", "socket", "requests", "urllib.request", "openai", "chromadb", "sqlite3"}
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in banned:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod in banned:
                found.add(mod)
    add(f"{rel}_no_unapproved_external_imports", not found, ", ".join(sorted(found)))


def run_py(label: str, rel: str) -> None:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ok = proc.returncode == 0
    add(f"{label}_passes", ok, proc.stdout.strip()[-2000:])


def main() -> int:
    files = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/promotion_path.py",
        "scripts/test_rmc_promotion_path_C12.py",
        "scripts/patch262J1R_preflight_C12_verify.py",
        "scripts/README_patch262J1R_preflight_C12.md",
        "SHA256SUMS.txt",
    ]
    for rel in files:
        file_exists(rel)

    promotion = text("rmc_engine_v1/promotion_path.py")
    main_src = text("main.py")
    init_src = text("rmc_engine_v1/__init__.py")
    sha_src = text("SHA256SUMS.txt")

    add("promotion_engine_version_C12", "rmc_promotion_path_v1_patch262J1R_preflight_C12" in promotion)
    add("promotion_formula_present", "M_{t+1} = M_t" in promotion and "stable_memory" in promotion and "retrieval_index" in promotion)
    add("promotion_requires_approval", "APPROVE_RMC_PROMOTION" in promotion)
    add("promotion_has_status_preview_commit", all(x in promotion for x in ["promotion_status", "build_promotion_plan", "promote_review_item"]))
    add("promotion_stable_memory_contract", "REQUIRED_STABLE_MEMORY_FIELDS" in promotion and "stable_memory_id" in promotion and "source_review_path" in promotion)
    add("promotion_duplicate_guard", "_index_duplicate" in promotion and "duplicate" in promotion)
    add("promotion_path_guard", "_assert_safe_root" in promotion and "_inside" in promotion)
    add("promotion_dangerous_examples_not_truth", "negative_or_blocked_example_not_truth" in promotion and "blocked_patterns" in promotion)
    add("promotion_original_review_immutable", "source_review_queue_left_immutable" in promotion)
    add("main_has_promotion_kernel", "_p262q_rmc_promotion_path_v1" in main_src)
    add("main_has_promotion_routes", all(route in main_src for route in ["/api/rmc/promotion-path/status", "/api/rmc/promotion-path/preview", "/api/rmc/promotion-path/promote"]))
    add("init_registers_promotion_path", "promotion_path" in init_src and "APPROVE_RMC_PROMOTION" in init_src)
    add("sha_excludes_pycache_pyc_venv_node_modules", all(x not in sha_src for x in ["__pycache__", ".pyc", ".venv", "node_modules", "chroma_db", ".sqlite", ".db"]))

    no_bad_imports("rmc_engine_v1/promotion_path.py")

    compile_proc = subprocess.run([
        sys.executable, "-m", "py_compile",
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/promotion_path.py",
        "scripts/test_rmc_promotion_path_C12.py",
        "scripts/patch262J1R_preflight_C12_verify.py",
    ], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    add("py_compile_changed_files", compile_proc.returncode == 0, compile_proc.stdout.strip())

    run_py("scripts_test_rmc_promotion_path_C12.py", "scripts/test_rmc_promotion_path_C12.py")
    # Regression: keep the C11R proof alive because C12 follows immediately after it.
    if (ROOT / "scripts/test_rmc_memory_writer_C7.py").exists():
        run_py("scripts_test_rmc_memory_writer_C7.py", "scripts/test_rmc_memory_writer_C7.py")

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C12_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C12_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
