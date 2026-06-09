#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C8 Gated Memory Writer Commit."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(condition), detail))


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def run_script(path: Path) -> tuple[bool, str]:
    try:
        proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        return proc.returncode == 0, proc.stdout.strip()
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def forbidden_uncontrolled_terms_absent(src: str) -> bool:
    forbidden = [
        "subprocess.",
        "os.system",
        "Popen(",
        "sqlite3",
        "chromadb",
        "IdentityVaultClient",
        "identity_vault.write",
        "requests.",
        "urllib.request",
        "openai",
        "ollama",
        ".env",
        "/forge/rmc_engine_v1/reference/",
    ]
    return not any(term in src for term in forbidden)


def main() -> int:
    main_py = ROOT / "main.py"
    module = ROOT / "rmc_engine_v1" / "memory_writer.py"
    test = ROOT / "scripts" / "test_rmc_memory_writer_C8.py"

    main_src = text(main_py)
    mod_src = text(module)

    check("file_exists_main.py", main_py.exists(), "main.py")
    check("file_exists_memory_writer.py", module.exists(), "rmc_engine_v1/memory_writer.py")
    check("file_exists_test_rmc_memory_writer_C8.py", test.exists(), "scripts/test_rmc_memory_writer_C8.py")
    check("main_has_C8_label", "Patch 262J1R-Preflight-C8" in main_src)
    check("main_delegates_to_commit_memory_write", "_p262n_commit_memory_write_gated" in main_src)
    check("main_gated_memory_writer_endpoint_present", '"/api/rmc/gated-memory-writer"' in main_src)
    check("main_memory_write_commit_alias_present", '"/api/rmc/memory-write-commit"' in main_src)
    check("main_commit_memory_write_alias_present", '"/api/rmc/commit-memory-write"' in main_src)
    check("module_engine_version_C8", "rmc_gated_memory_writer_v1_patch262J1R_preflight_C8" in mod_src)
    check("module_keeps_C7_dry_run", "def plan_memory_write" in mod_src and "rmc_memory_writer_dry_run_v1_patch262J1R_preflight_C7" in mod_src)
    check("module_has_commit_memory_write", "def commit_memory_write" in mod_src)
    check("module_requires_explicit_approval", "APPROVE_RMC_MEMORY_WRITE" in mod_src and "approval_token" in mod_src)
    check("module_has_duplicate_guard", "duplicate_memory_candidate" in mod_src and "_read_index_hashes" in mod_src)
    check("module_has_safe_path_guard", "_ensure_inside_root" in mod_src and "unsafe_target_path" in mod_src)
    check("module_writes_node_receipt_index", "memory_node_json" in mod_src and "write_receipt_json" in mod_src and "memory_writer_index_jsonl" in mod_src)
    check("module_blocks_identity_and_canonical", "identity_vault_write" in mod_src and "canonical_reference_write" in mod_src)
    check("module_no_uncontrolled_side_effect_terms", forbidden_uncontrolled_terms_absent(mod_src))

    ok, out = run_script(test)
    check("test_rmc_memory_writer_C8.py_passes", ok and "memory_writer_C8_behavior_tests_pass=True" in out, out.splitlines()[-1] if out else "")

    # Soft regression guards: run earlier tests only if they are present on disk.
    for rel, marker in [
        ("scripts/test_rmc_memory_writer_C7.py", "memory_writer_C7_behavior_tests_pass=True"),
        ("scripts/test_rmc_echo_validator_C6.py", "echo_validator_C6_behavior_tests_pass=True"),
        ("scripts/test_rmc_output_renderer_C5.py", "output_renderer_C5_behavior_tests_pass=True"),
        ("scripts/test_rmc_manifest_compiler_C4.py", "manifest_compiler_C4_behavior_tests_pass=True"),
        ("scripts/test_rmc_correction_naming_C3R.py", "correction_naming_C3R_behavior_tests_pass=True"),
        ("scripts/test_rmc_measurement_kernel_C2R.py", "measurement_kernel_C2R_behavior_tests_pass=True"),
    ]:
        p = ROOT / rel
        if p.exists():
            ok2, out2 = run_script(p)
            check(f"{p.name}_still_passes", ok2 and marker in out2, out2.splitlines()[-1] if out2 else "")

    print("PATCH 262J1R-PREFLIGHT-C8 VERIFY")
    print("─" * 72)
    passed = 0
    for name, ok, detail in CHECKS:
        if ok:
            passed += 1
            print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))
        else:
            print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(CHECKS) - passed}")
    if passed == len(CHECKS):
        print("RESULT: PATCH_262J1R_PREFLIGHT_C8_VERIFY_OK")
        return 0
    print("RESULT: PATCH_262J1R_PREFLIGHT_C8_VERIFY_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
