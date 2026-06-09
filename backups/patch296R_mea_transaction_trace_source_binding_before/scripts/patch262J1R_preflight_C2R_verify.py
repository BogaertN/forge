#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C2R.

Fails if the reinforcement is only cosmetic. It checks that the shared
measurement kernel exists, that C_t/E_t/S_t modules bind to it, and that direct
behavior tests prove actual readings: entropy, structure delta, semantic
distance, phase deviation, epsilon_s, bounded drift, and measured coherence.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def run_script(path: str, expect: str) -> None:
    script = ROOT / path
    if not script.exists():
        add(f"{path}_exists", False, "missing")
        return
    proc = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), text=True, capture_output=True, timeout=60)
    ok = proc.returncode == 0 and expect in (proc.stdout + proc.stderr)
    detail = (proc.stdout + proc.stderr).strip().splitlines()[-1] if (proc.stdout + proc.stderr).strip() else f"returncode={proc.returncode}"
    add(f"{path}_passes", ok, detail)


def main() -> int:
    print("PATCH 262J1R-PREFLIGHT-C2R VERIFY")
    print("─" * 72)

    files = [
        "main.py",
        "rmc_engine_v1/measurement_kernel.py",
        "rmc_engine_v1/candidate_generator.py",
        "rmc_engine_v1/evolutionary_drift_explorer.py",
        "scripts/test_rmc_measurement_kernel_C2R.py",
        "scripts/test_rmc_evolutionary_drift_coherence_C2.py",
        "scripts/test_rmc_candidate_generator_behavior.py",
    ]
    for f in files:
        add(f"file_exists_{f}", (ROOT / f).exists(), f)

    main_py = read("main.py")
    kernel = read("rmc_engine_v1/measurement_kernel.py")
    candidate = read("rmc_engine_v1/candidate_generator.py")
    evo = read("rmc_engine_v1/evolutionary_drift_explorer.py")

    add("main_has_C2R_label", "Preflight-C2R" in main_py)
    add("main_evolutionary_endpoint_present", "/api/rmc/evolutionary-drift-explorer" in main_py)
    add("main_coherence_endpoint_present", "/api/rmc/coherence-scorer" in main_py)
    add("kernel_has_entropy", "def normalized_shannon_entropy" in kernel and "math.log2" in kernel)
    add("kernel_has_structure_signature", "def structure_signature" in kernel and "key_paths" in kernel)
    add("kernel_has_semantic_distance", "def semantic_distance" in kernel and "weighted_semantic_similarity" in kernel)
    add("kernel_has_phase_delta", "def phase_path_metrics" in kernel and "phase_5_to_8_projection_skip" in kernel)
    add("kernel_has_epsilon_formula", "def symbolic_epsilon" in kernel and "sigma_res" in kernel and "D_score" in kernel)
    add("kernel_has_coherence_formula", "def coherence_components" in kernel and "0.24 * mem_fit" in kernel)
    add("candidate_uses_measurement_kernel", "measure_candidate" in candidate and "measurement_kernel" in candidate)
    add("evo_uses_measurement_kernel", "measure_candidate" in evo and "coherence_components" in evo and "measured_evolutionary_drift" in evo)

    forbidden = ["open(", "subprocess", "os.system", "requests.", "ollama", "chat.completions", "write("]
    # The verifier itself uses subprocess; production modules must not.
    for mod_name, text in [("measurement_kernel", kernel), ("candidate_generator", candidate), ("evolutionary_drift_explorer", evo)]:
        bad = [term for term in forbidden if term in text]
        add(f"{mod_name}_no_forbidden_side_effect_terms", not bad, ", ".join(bad))

    run_script("scripts/test_rmc_measurement_kernel_C2R.py", "RESULT: measurement_kernel_C2R_behavior_tests_pass=True")
    run_script("scripts/test_rmc_evolutionary_drift_coherence_C2.py", "RESULT: evolutionary_drift_coherence_C2R_behavior_tests_pass=True")
    run_script("scripts/test_rmc_candidate_generator_behavior.py", "RESULT: candidate_generator_C_behavior_tests_pass=True")

    passed = 0
    failed = 0
    for name, ok, detail in CHECKS:
        if ok:
            passed += 1
            suffix = f" :: {detail}" if detail else ""
            print(f"[PASS] {name}{suffix}")
        else:
            failed += 1
            suffix = f" :: {detail}" if detail else ""
            print(f"[FAIL] {name}{suffix}")
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_C2R_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C2R_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
