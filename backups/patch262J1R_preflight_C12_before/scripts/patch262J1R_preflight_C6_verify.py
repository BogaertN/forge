#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

CHECKS = []

def add(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))


def read(path):
    return (ROOT / path).read_text(errors="replace")


def run_script(path):
    proc = subprocess.run([sys.executable, str(ROOT / path)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return proc.returncode == 0, proc.stdout.strip()


def main() -> int:
    main_py = ROOT / "main.py"
    module = ROOT / "rmc_engine_v1" / "echo_validator.py"
    test = ROOT / "scripts" / "test_rmc_echo_validator_C6.py"

    add("file_exists_main.py", main_py.exists(), "main.py")
    add("file_exists_echo_validator.py", module.exists(), "rmc_engine_v1/echo_validator.py")
    add("file_exists_test_rmc_echo_validator_C6.py", test.exists(), "scripts/test_rmc_echo_validator_C6.py")

    main_text = read("main.py") if main_py.exists() else ""
    mod_text = read("rmc_engine_v1/echo_validator.py") if module.exists() else ""

    add("main_has_C6_label", "Patch 262J1R-Preflight-C6" in main_text)
    add("main_delegates_to_echo_validator", "from rmc_engine_v1.echo_validator import validate_echo" in main_text)
    add("main_echo_validator_endpoint_present", '"/api/rmc/echo-validator"' in main_text)
    add("main_echo_alias_present", '"/api/rmc/echo"' in main_text)
    add("main_render_echo_alias_present", '"/api/rmc/render-echo"' in main_text)
    add("module_engine_version_C6", "rmc_echo_validator_v1_patch262J1R_preflight_C6" in mod_text)
    add("module_has_validate_echo", "def validate_echo" in mod_text)
    add("module_has_V_t", "V_t" in mod_text and "echo_symbol" in mod_text)
    add("module_has_echo_score_formula", "0.24*claim" in mod_text and "distortion_penalty" in mod_text)
    add("module_checks_manifest_and_render", "source_manifest_packet_missing" in mod_text and "render_packet_missing_or_render_blocked" in mod_text)
    add("module_blocks_memory_write", '"memory_write_allowed": False' in mod_text)
    forbidden = ["open(", "subprocess", "os.system", "requests.", "sqlite3", "chromadb", "write_text", "send_email"]
    add("module_no_forbidden_side_effect_terms", not any(term in mod_text for term in forbidden))

    ok, out = run_script("scripts/test_rmc_echo_validator_C6.py") if test.exists() else (False, "missing test")
    add("test_rmc_echo_validator_C6.py_passes", ok, out.splitlines()[-1] if out else "")

    # Guard tests from prior pipeline stages, when present in live Forge.
    for script, marker in [
        ("scripts/test_rmc_output_renderer_C5.py", "output_renderer_C5_behavior_tests_pass=True"),
        ("scripts/test_rmc_manifest_compiler_C4.py", "manifest_compiler_C4_behavior_tests_pass=True"),
        ("scripts/test_rmc_correction_naming_C3R.py", "correction_naming_C3R_behavior_tests_pass=True"),
        ("scripts/test_rmc_measurement_kernel_C2R.py", "measurement_kernel_C2R_behavior_tests_pass=True"),
    ]:
        if (ROOT / script).exists():
            ok2, out2 = run_script(script)
            add(f"{pathlib.Path(script).name}_still_passes", ok2 and marker in out2, out2.splitlines()[-1] if out2 else "")

    print("PATCH 262J1R-PREFLIGHT-C6 VERIFY")
    print("─" * 72)
    failed = 0
    for name, ok, detail in CHECKS:
        if ok:
            print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))
        else:
            print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
            failed += 1
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {len(CHECKS)-failed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C6_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C6_VERIFY_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
