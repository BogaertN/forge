#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C3R."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    checks.append((name, bool(ok), detail))


def run_script(path: str) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, path], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
    return proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""


def main() -> int:
    main_py = ROOT / "main.py"
    module = ROOT / "rmc_engine_v1" / "correction_naming_engine.py"
    test = ROOT / "scripts" / "test_rmc_correction_naming_C3R.py"
    add("file_exists_main.py", main_py.exists(), "main.py")
    add("file_exists_correction_naming_engine.py", module.exists(), "rmc_engine_v1/correction_naming_engine.py")
    add("file_exists_test_rmc_correction_naming_C3R.py", test.exists(), "scripts/test_rmc_correction_naming_C3R.py")
    main_text = main_py.read_text(errors="replace") if main_py.exists() else ""
    mod_text = module.read_text(errors="replace") if module.exists() else ""
    add("main_has_C3R_label", "PATCH 262J1R-PREFLIGHT-C3R" in main_text and "Correction/Naming Calibration" in main_text)
    add("main_correction_naming_endpoint_present", '"/api/rmc/correction-naming"' in main_text)
    add("main_correction_engine_endpoint_present", '"/api/rmc/correction-engine"' in main_text)
    add("main_naming_engine_endpoint_present", '"/api/rmc/naming-engine"' in main_text)
    add("module_engine_version_C3R", "rmc_correction_naming_engine_v2_patch262J1R_preflight_C3R" in mod_text)
    add("module_separates_validity_from_projection_score", "candidate_validity_score" in mod_text and "projection_gated_score" in mod_text)
    add("module_has_route_consistency", "route_consistent" in mod_text and "recommended_route" in mod_text and "chi_t_action" in mod_text)
    add("module_penalizes_high_semantic_novelty", "high_semantic_penalty" in mod_text and "high_novelty_penalty" in mod_text and "low_memory_penalty" in mod_text)
    add("module_name_derivation_from_candidate", "_extract_name_terms" in mod_text and "name_derivation" in mod_text)
    add("module_uses_measurement_kernel", "from rmc_engine_v1.measurement_kernel" in mod_text)
    forbidden = ["subprocess", "os.system", "Path.write", ".write_text", ".write_bytes", "open(", "requests", "urllib.request"]
    add("module_no_forbidden_side_effect_terms", not any(term in mod_text for term in forbidden), ",".join([term for term in forbidden if term in mod_text]))
    ok, detail = run_script("scripts/test_rmc_correction_naming_C3R.py")
    add("test_rmc_correction_naming_C3R.py_passes", ok and "correction_naming_C3R_behavior_tests_pass=True" in detail, detail)
    for script, expected in [
        ("scripts/test_rmc_measurement_kernel_C2R.py", "measurement_kernel_C2R_behavior_tests_pass=True"),
        ("scripts/test_rmc_evolutionary_drift_coherence_C2.py", "evolutionary_drift_coherence_C2R_behavior_tests_pass=True"),
        ("scripts/test_rmc_candidate_generator_behavior.py", "candidate_generator_C_behavior_tests_pass=True"),
    ]:
        sp = ROOT / script
        if sp.exists():
            ok, detail = run_script(script)
            add(f"{Path(script).name}_still_passes", ok and expected in detail, detail)
        else:
            add(f"{Path(script).name}_still_passes", False, "missing")
    print("PATCH 262J1R-PREFLIGHT-C3R VERIFY")
    print("─" * 72)
    passed = 0
    for name, ok, detail in checks:
        if ok:
            passed += 1
            print(f"[PASS] {name}" + (f" :: {detail}" if detail else ""))
        else:
            print(f"[FAIL] {name}" + (f" :: {detail}" if detail else ""))
    print("─" * 72)
    print(f"Total: {len(checks)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(checks)-passed}")
    if passed == len(checks):
        print("RESULT: PATCH_262J1R_PREFLIGHT_C3R_VERIFY_OK")
        return 0
    print("RESULT: PATCH_262J1R_PREFLIGHT_C3R_VERIFY_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
