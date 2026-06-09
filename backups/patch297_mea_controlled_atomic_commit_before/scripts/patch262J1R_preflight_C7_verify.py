#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C7 Memory Writer Dry-Run."""
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
        proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
        return proc.returncode == 0, proc.stdout.strip()
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def forbidden_terms_absent(src: str) -> bool:
    forbidden = [
        "subprocess.",
        "os.system",
        "Popen(",
        "open(",
        ".write(",
        "Path.write_text",
        "Path.write_bytes",
        "sqlite3",
        "chromadb",
        "IdentityVaultClient",
        "identity_vault.write",
        "requests.",
        "urllib.request",
    ]
    return not any(term in src for term in forbidden)


def main() -> int:
    main_py = ROOT / "main.py"
    module = ROOT / "rmc_engine_v1" / "memory_writer.py"
    test = ROOT / "scripts" / "test_rmc_memory_writer_C7.py"

    main_src = text(main_py)
    mod_src = text(module)

    check("file_exists_main.py", main_py.exists(), "main.py")
    check("file_exists_memory_writer.py", module.exists(), "rmc_engine_v1/memory_writer.py")
    check("file_exists_test_rmc_memory_writer_C7.py", test.exists(), "scripts/test_rmc_memory_writer_C7.py")
    check("main_has_C7_label", "Patch 262J1R-Preflight-C7" in main_src)
    check("main_delegates_to_memory_writer", "_p262m_plan_memory_write_dry_run" in main_src)
    check("main_memory_writer_endpoint_present", '"/api/rmc/memory-writer"' in main_src)
    check("main_memory_write_dry_run_alias_present", '"/api/rmc/memory-write-dry-run"' in main_src)
    check("main_write_plan_alias_present", '"/api/rmc/write-plan"' in main_src)
    check("module_engine_version_C7", "rmc_memory_writer_dry_run_v1_patch262J1R_preflight_C7" in mod_src)
    check("module_has_plan_memory_write", "def plan_memory_write" in mod_src)
    check("module_has_W_t", "W_t" in mod_src and "memory_write_plan_allowed" in mod_src)
    check("module_has_write_eligibility_formula", "write_eligibility_formula" in mod_src)
    check("module_separates_gate_and_read_only", "gate_classification" in mod_src and "read_only_refusal" in mod_src)
    check("module_blocks_actual_writes", "actual_files_written" in mod_src and "writes_files" in mod_src and "rmc_live_memory_write" in mod_src)
    check("module_no_forbidden_side_effect_terms", forbidden_terms_absent(mod_src))

    ok, out = run_script(test)
    check("test_rmc_memory_writer_C7.py_passes", ok, out.splitlines()[-1] if out else "")

    # Soft regression guards: run earlier tests only if they are present on disk.
    for rel, marker in [
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

    print("PATCH 262J1R-PREFLIGHT-C7 VERIFY")
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
        print("RESULT: PATCH_262J1R_PREFLIGHT_C7_VERIFY_OK")
        return 0
    print("RESULT: PATCH_262J1R_PREFLIGHT_C7_VERIFY_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
