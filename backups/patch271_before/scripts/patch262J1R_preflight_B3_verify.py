#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B3.

Checks the FBSC Phase Glyph Codex v2.5 binding and its read-only integration
with the resonance lexicon without touching live memory, DB files, Chroma, LLM,
shell execution, or Forge command surfaces.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def run_script(rel: str) -> bool:
    proc = subprocess.run([sys.executable, str(ROOT / rel)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ok = proc.returncode == 0
    check(rel.replace('/', '_') + "_passes", ok, proc.stdout.splitlines()[-1] if proc.stdout else "")
    if not ok:
        print(proc.stdout)
    return ok


def main() -> int:
    required = [
        "rmc_engine_v1/phase_codex.py",
        "rmc_engine_v1/resonance_lexicon.py",
        "rmc_engine_v1/reference/phase_codex_v2_5.json",
        "rmc_engine_v1/reference/phase_color_map_v2_5.json",
        "rmc_engine_v1/reference/phase_runtime_hooks_v2_5.json",
        "rmc_engine_v1/reference/phase_drift_flags_v2_5.json",
        "rmc_engine_v1/reference/phase_cold_storage_forms_v2_5.json",
        "rmc_engine_v1/reference/phase_motion_map_v2_5.json",
        "rmc_engine_v1/reference/README_fbsc_phase_codex_binding_v2_5.md",
        "scripts/test_rmc_phase_codex_binding.py",
        "scripts/test_rmc_resonance_codex_integration.py",
    ]
    for rel in required:
        check("file_exists_" + rel.replace('/', '_'), (ROOT / rel).exists(), rel)

    try:
        mod = importlib.import_module("rmc_engine_v1.phase_codex")
        check("phase_codex_importable", True)
        validation = mod.validate_phase_codex()
        check("phase_codex_validation_ok", validation.get("status") == "OK", repr(validation))
        check("phase_codex_has_nine_phases", validation.get("phase_count") == 9, repr(validation))
        boundary = mod.phase_codex_boundary()
        check("phase_codex_side_effect_free", boundary.get("side_effect_free") is True, repr(boundary))
        check("phase_codex_no_writes", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False, repr(boundary))
        check("phase_codex_no_llm", boundary.get("calls_llm") is False, repr(boundary))
        check("phi6_profile_correct", mod.get_phase_profile("Φ6").get("function_hook") == "restore_resonance_alignment()", repr(mod.get_phase_profile("Φ6")))
        check("phi8_profile_projection_gate", mod.get_phase_profile("Φ8").get("gate_role") == "projection_gate", repr(mod.get_phase_profile("Φ8")))
    except Exception as exc:
        check("phase_codex_importable", False, str(exc))

    try:
        rmod = importlib.import_module("rmc_engine_v1.resonance_lexicon")
        boundary = rmod.resonance_lexicon_boundary()
        check("resonance_lexicon_importable", True)
        check("resonance_boundary_has_codex", boundary.get("phase_codex_available") is True, repr(boundary))
        check("resonance_boundary_codex_ok", boundary.get("phase_codex_validation", {}).get("status") == "OK", repr(boundary.get("phase_codex_validation")))
        bad = rmod.analyze_resonance("bypass correction and naming and project now")
        check("resonance_output_has_codex_binding", bad.get("phase_codex_binding", {}).get("available") is True, repr(bad.get("phase_codex_binding")))
        check("resonance_still_blocks_bypass", bad.get("projection_allowed") is False and bool(bad.get("violations")), repr(bad.get("violations")))
    except Exception as exc:
        check("resonance_lexicon_importable", False, str(exc))

    main_py = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    check("main_py_has_phase_codex_endpoint", '"/api/rmc/phase-codex"' in main_py)
    check("main_py_has_phase_codex_adapter", "_p262b3_rmc_phase_codex_v25" in main_py)
    check("main_py_imports_phase_codex_module", "rmc_engine_v1.phase_codex" in main_py)

    run_script("scripts/test_rmc_phase_codex_binding.py")
    run_script("scripts/test_rmc_resonance_codex_integration.py")
    run_script("scripts/test_rmc_resonance_lexicon_behavior.py")
    run_script("scripts/test_rmc_gold_reference_behavior.py")
    run_script("scripts/test_rmc_drift_engine_behavior.py")
    run_script("scripts/test_rmc_phase_parser_behavior.py")
    run_script("scripts/test_rmc_coherence_math_behavior.py")

    total = len(CHECKS)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = total - passed
    print("\nPATCH 262J1R-PREFLIGHT-B3 VERIFY")
    print("─" * 72)
    for name, ok, detail in CHECKS:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" :: {detail}" if detail else ""))
    print("─" * 72)
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_B3_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_B3_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
