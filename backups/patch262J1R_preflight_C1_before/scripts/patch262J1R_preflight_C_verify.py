#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C — Candidate Generator."""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(condition), detail))


def run_script(rel: str) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, capture_output=True, timeout=60)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out.strip()[-1200:]


def main() -> int:
    main_py = ROOT / "main.py"
    module = ROOT / "rmc_engine_v1" / "candidate_generator.py"
    test = ROOT / "scripts" / "test_rmc_candidate_generator_behavior.py"
    check("file_exists_main.py", main_py.exists(), "main.py")
    check("file_exists_candidate_generator.py", module.exists(), "rmc_engine_v1/candidate_generator.py")
    check("file_exists_test_rmc_candidate_generator_behavior.py", test.exists(), "scripts/test_rmc_candidate_generator_behavior.py")

    main_text = main_py.read_text(errors="replace") if main_py.exists() else ""
    mod_text = module.read_text(errors="replace") if module.exists() else ""
    check("main_has_patch_C_label", "Patch 262J1R-Preflight-C" in main_text)
    check("main_delegates_to_candidate_generator", "from rmc_engine_v1.candidate_generator import" in main_text)
    check("main_candidate_endpoint_present", '"/api/rmc/candidate-conclusion"' in main_text)
    check("main_candidate_alias_present", '"/api/rmc/candidate-generator"' in main_text)
    check("module_has_generate_candidates", "def generate_candidates" in mod_text)
    check("module_no_llm_calls", "openai" not in mod_text.lower() and "ollama" not in mod_text.lower())
    check("module_no_file_writes", ".write(" not in mod_text and "open(" not in mod_text)
    check("module_no_shell", "subprocess" not in mod_text and "os.system" not in mod_text)
    ok, out = run_script("scripts/test_rmc_candidate_generator_behavior.py")
    check("test_rmc_candidate_generator_behavior.py_passes", ok and "candidate_generator_C_behavior_tests_pass=True" in out, out)

    print("PATCH 262J1R-PREFLIGHT-C VERIFY")
    print("─" * 72)
    failed = 0
    for name, ok_, detail in CHECKS:
        print(("[PASS]" if ok_ else "[FAIL]"), name, (f":: {detail}" if detail else ""))
        if not ok_:
            failed += 1
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {len(CHECKS) - failed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
