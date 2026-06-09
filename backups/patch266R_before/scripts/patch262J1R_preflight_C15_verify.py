#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C15 — Chroma Integration Boundary."""
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(condition), detail))


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_script(rel: str) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode == 0, proc.stdout


def no_bad_runtime(rel: str) -> None:
    src = read(rel)
    bad_tokens = ["requests", "subprocess", "os.system", "Popen", "socket", "open(", ".write(", "sqlite3", "IdentityVault"]
    hits = [tok for tok in bad_tokens if tok in src]
    check(f"{rel}_no_unapproved_write_shell_network", not hits, ",".join(hits))


def main() -> int:
    required = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/chroma_connector.py",
        "rmc_engine_v1/memory_recaller.py",
        "scripts/test_rmc_chroma_connector_C15.py",
        "scripts/test_rmc_memory_recaller_behavior.py",
        "scripts/test_rmc_pipeline_summary_C9.py",
        "scripts/patch262J1R_preflight_C15_verify.py",
        "scripts/README_patch262J1R_preflight_C15.md",
        "SHA256SUMS.txt",
    ]
    for rel in required:
        check(f"file_exists_{rel}", (ROOT / rel).exists(), rel)

    chroma = read("rmc_engine_v1/chroma_connector.py")
    memory = read("rmc_engine_v1/memory_recaller.py")
    main_py = read("main.py")
    init = read("rmc_engine_v1/__init__.py")
    sha = read("SHA256SUMS.txt")

    check("chroma_engine_version_C15", "rmc_chroma_connector_v1_patch262J1R_preflight_C15" in chroma)
    check("chroma_has_approved_path_guard", "APPROVED_CHROMA_RELATIVE_PATH" in chroma and "context_library_v1/chroma_db" in chroma)
    check("chroma_query_function_present", "def query_chroma_memory" in chroma and "get_collection" in chroma and "query_texts" in chroma)
    check("chroma_never_writes", "writes_chroma" in chroma and "writes_files" in chroma and ".add(" not in chroma and ".upsert(" not in chroma and ".delete(" not in chroma)
    check("memory_recaller_version_C15", "rmc_memory_recaller_v1_patch262J1R_preflight_C15" in memory)
    check("memory_imports_chroma_connector", "from rmc_engine_v1.chroma_connector import" in memory)
    check("memory_default_filesystem", "retrieval_backend_default" in memory and "filesystem" in memory)
    check("memory_supports_hybrid", "supported_retrieval_backends" in memory and "hybrid" in memory)
    check("memory_exposes_chroma_state", "chroma_retrieval" in memory and "chroma_nodes_collected" in memory and "vector_similarity" in memory)
    check("main_has_chroma_status_adapter", "_p262s_rmc_chroma_status_v1" in main_py)
    check("main_has_chroma_status_route", "/api/rmc/chroma-status" in main_py and "_p262s_rmc_chroma_status_v1(self.path)" in main_py)
    check("main_passes_retrieval_backend", "retrieval_backend" in main_py and "chroma_collection" in main_py and "chroma_limit" in main_py)
    check("init_registers_chroma_connector", "chroma_connector" in init and "rmc_engine_v1.chroma_connector" in init)
    check("sha_excludes_pycache_pyc_venv_node_modules", "__pycache__" not in sha and ".pyc" not in sha and ".venv" not in sha and "node_modules" not in sha)

    no_bad_runtime("rmc_engine_v1/chroma_connector.py")

    compile_targets = [
        "main.py",
        "rmc_engine_v1/__init__.py",
        "rmc_engine_v1/chroma_connector.py",
        "rmc_engine_v1/memory_recaller.py",
        "scripts/test_rmc_chroma_connector_C15.py",
        "scripts/patch262J1R_preflight_C15_verify.py",
    ]
    ok_compile = True
    details = []
    for rel in compile_targets:
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
        except Exception as exc:
            ok_compile = False
            details.append(f"{rel}:{exc}")
    check("py_compile_changed_files", ok_compile, "; ".join(details))

    for rel, marker in [
        ("scripts/test_rmc_chroma_connector_C15.py", "RESULT: chroma_connector_C15_behavior_tests_pass=True"),
        ("scripts/test_rmc_memory_recaller_behavior.py", "RESULT: memory_recaller_B6_behavior_tests_pass=True"),
        ("scripts/test_rmc_pipeline_summary_C9.py", "RESULT: pipeline_summary_C9_behavior_tests_pass=True"),
    ]:
        ok, output = run_script(rel)
        check(f"{rel}_passes", ok and marker in output, output[-2500:])

    print("PATCH 262J1R-PREFLIGHT-C15 VERIFY")
    print("────────────────────────────────────────────────────────────────────────")
    passed = 0
    for name, ok, detail in CHECKS:
        if ok:
            passed += 1
            print(f"[PASS] {name}" + (f" :: {detail}" if detail and name.startswith("file_exists") else ""))
        else:
            print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
    total = len(CHECKS)
    failed = total - passed
    print("────────────────────────────────────────────────────────────────────────")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C15_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C15_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
