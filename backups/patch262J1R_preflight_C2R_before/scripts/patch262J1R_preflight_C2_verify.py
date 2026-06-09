#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-C2 — Evolutionary Drift Explorer + Coherence Scorer."""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(condition), detail))


def run_script(rel: str) -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, capture_output=True, timeout=90)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out.strip()[-1600:]


def main() -> int:
    main_py = ROOT / "main.py"
    module = ROOT / "rmc_engine_v1" / "evolutionary_drift_explorer.py"
    cand = ROOT / "rmc_engine_v1" / "candidate_generator.py"
    test = ROOT / "scripts" / "test_rmc_evolutionary_drift_coherence_C2.py"
    check("file_exists_main.py", main_py.exists(), "main.py")
    check("file_exists_evolutionary_drift_explorer.py", module.exists(), "rmc_engine_v1/evolutionary_drift_explorer.py")
    check("file_exists_candidate_generator.py", cand.exists(), "rmc_engine_v1/candidate_generator.py")
    check("file_exists_test_rmc_evolutionary_drift_coherence_C2.py", test.exists(), "scripts/test_rmc_evolutionary_drift_coherence_C2.py")

    main_text = main_py.read_text(errors="replace") if main_py.exists() else ""
    mod_text = module.read_text(errors="replace") if module.exists() else ""
    check("main_has_patch_C2_label", "Patch 262J1R-Preflight-C2" in main_text)
    check("main_delegates_to_evolutionary_drift_explorer", "from rmc_engine_v1.evolutionary_drift_explorer import" in main_text)
    check("main_evolutionary_endpoint_present", '"/api/rmc/evolutionary-drift-explorer"' in main_text)
    check("main_coherence_scorer_endpoint_present", '"/api/rmc/coherence-scorer"' in main_text)
    check("main_evolutionary_dispatch_present", 'elif _p249_req_path == "/api/rmc/evolutionary-drift-explorer"' in main_text)
    check("main_coherence_scorer_dispatch_present", 'elif _p249_req_path == "/api/rmc/coherence-scorer"' in main_text)
    check("module_has_explore_evolutionary_drift", "def explore_evolutionary_drift" in mod_text)
    check("module_has_score_coherence", "def score_coherence" in mod_text)
    check("module_has_E_t_and_S_t", "E_t" in mod_text and "S_t" in mod_text)
    check("module_no_llm_calls", "openai" not in mod_text.lower() and "ollama" not in mod_text.lower())
    check("module_no_file_writes", ".write(" not in mod_text and "open(" not in mod_text)
    check("module_no_shell", "subprocess" not in mod_text and "os.system" not in mod_text)

    ok, out = run_script("scripts/test_rmc_evolutionary_drift_coherence_C2.py")
    check("test_rmc_evolutionary_drift_coherence_C2.py_passes", ok and "evolutionary_drift_coherence_C2_behavior_tests_pass=True" in out, out)
    ok2, out2 = run_script("scripts/test_rmc_candidate_generator_behavior.py")
    check("test_rmc_candidate_generator_behavior.py_still_passes", ok2 and "candidate_generator_C_behavior_tests_pass=True" in out2, out2)

    print("PATCH 262J1R-PREFLIGHT-C2 VERIFY")
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
        print("RESULT: PATCH_262J1R_PREFLIGHT_C2_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_C2_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
