#!/usr/bin/env python3
"""Patch 262J1R-Preflight-B6R verifier.

Verifies the professional repair to the Phase Parser boundary logic before
Candidate Generator extraction. The key live bug was a substring keyword match:
`or` inside `before` incorrectly activated Φ2 polarity.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))


def run_py(script: str) -> tuple[bool, str]:
    path = ROOT / "scripts" / script
    if not path.exists():
        return False, f"missing {script}"
    proc = subprocess.run([sys.executable, str(path)], cwd=str(ROOT), text=True, capture_output=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out.strip()[-1200:]


def main() -> int:
    phase_parser = ROOT / "rmc_engine_v1" / "phase_parser.py"
    main_py = ROOT / "main.py"
    test_file = ROOT / "scripts" / "test_rmc_phase_parser_boundary_B6R.py"

    add("file_exists_phase_parser.py", phase_parser.exists(), str(phase_parser))
    add("file_exists_main.py", main_py.exists(), str(main_py))
    add("file_exists_test_rmc_phase_parser_boundary_B6R.py", test_file.exists(), str(test_file))

    parser_text = phase_parser.read_text(encoding="utf-8") if phase_parser.exists() else ""
    main_text = main_py.read_text(encoding="utf-8", errors="replace") if main_py.exists() else ""

    add("phase_parser_engine_version_B6R", "rmc_phase_parser_engine_v1_patch262J1R_preflight_B6R" in parser_text)
    add("phase_parser_has_whole_word_boundary_helper", "whole-word keyword boundaries" in parser_text or "whole_word_keyword_matching_B6R" in parser_text)
    add("phase_parser_has_contains_symbolic_literal", "def _contains_symbolic_literal" in parser_text)
    add("phase_parser_has_phrase_evidence", "def _phrase_evidence" in parser_text)
    add("phase_parser_has_confidence_status", "confidence_status" in parser_text)
    add("main_phase_parser_current_patch_B6R", "Patch 262J1R-Preflight-B6R" in main_text)

    ok, detail = run_py("test_rmc_phase_parser_boundary_B6R.py")
    add("test_rmc_phase_parser_boundary_B6R.py_passes", ok, detail)

    # Preserve the prior B1/B6 guard if present on the live tree.
    for guard in ["test_rmc_phase_parser_behavior.py", "test_rmc_memory_recaller_behavior.py"]:
        path = ROOT / "scripts" / guard
        if path.exists():
            ok, detail = run_py(guard)
            add(f"{guard}_passes", ok, detail)
        else:
            add(f"{guard}_not_present_optional", True, "not packaged in B6R; expected to exist on live tree")

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed

    print("PATCH 262J1R-PREFLIGHT-B6R VERIFY")
    print("─" * 72)
    for name, ok, detail in CHECKS:
        status = "PASS" if ok else "FAIL"
        suffix = f" :: {detail}" if detail else ""
        print(f"[{status}] {name}{suffix}")
    print("─" * 72)
    print(f"Total: {len(CHECKS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_B6R_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_B6R_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
