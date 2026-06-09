#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C12R — Promotion HTTP route repair."""
from pathlib import Path
import py_compile
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECKS = []

def add(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' :: ' + detail) if detail else ''}")

def text(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""

def run_py(name: str, rel: str) -> None:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    add(name, proc.returncode == 0, proc.stdout.strip())

def main() -> int:
    print("PATCH 262J1R-PREFLIGHT-C12R VERIFY")
    print("─" * 72)
    required = [
        "main.py",
        "scripts/test_rmc_promotion_route_C12R.py",
        "scripts/patch262J1R_preflight_C12R_verify.py",
        "scripts/README_patch262J1R_preflight_C12R.md",
        "SHA256SUMS.txt",
    ]
    for rel in required:
        add(f"file_exists_{rel}", (ROOT / rel).exists(), rel)
    main_src = text("main.py")
    add("promotion_adapter_function_present", "def _p262q_rmc_promotion_path_v1" in main_src)
    add("promotion_dispatch_routes_present", all(r in main_src for r in [
        "/api/rmc/promotion-path/status",
        "/api/rmc/promotion-path/preview",
        "/api/rmc/promotion-path/promote",
    ]))
    add("promotion_dispatch_calls_adapter", "_p262q_rmc_promotion_path_v1(self.path)" in main_src)
    status_pos = main_src.find('"/api/rmc/promotion-path/status"')
    forge_pos = main_src.find('elif self.path == "/api/forge/status"')
    add("promotion_dispatch_before_forge_status", status_pos != -1 and forge_pos != -1 and status_pos < forge_pos)
    add("promotion_approval_token_preserved", "APPROVE_RMC_PROMOTION" in main_src)
    bad = ["__pycache__", ".pyc", "node_modules", ".venv", "chroma_db", "identity_vault.db", "vault.db"]
    sha = text("SHA256SUMS.txt")
    add("sha_excludes_pycache_pyc_venv_node_modules", not any(b in sha for b in bad))
    try:
        py_compile.compile(str(ROOT / "main.py"), doraise=True)
        py_compile.compile(str(ROOT / "scripts/test_rmc_promotion_route_C12R.py"), doraise=True)
        add("py_compile_changed_files", True)
    except Exception as exc:
        add("py_compile_changed_files", False, str(exc))
    run_py("scripts_test_rmc_promotion_route_C12R.py_passes", "scripts/test_rmc_promotion_route_C12R.py")
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C12R_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C12R_VERIFY_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
