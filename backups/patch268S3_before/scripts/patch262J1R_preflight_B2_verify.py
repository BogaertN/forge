#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B2.

Checks the Resonance Lexicon + Gold Reference Foundation without touching live
memory, DB files, Chroma, LLM, shell execution, or Forge command surfaces.
"""
from __future__ import annotations

import importlib
import json
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
        "rmc_engine_v1/resonance_lexicon.py",
        "rmc_engine_v1/reference/letter_phase_map_v1.json",
        "rmc_engine_v1/reference/word_loop_seed_lexicon_v1.jsonl",
        "rmc_engine_v1/reference/operator_phrase_lexicon_v1.jsonl",
        "rmc_engine_v1/reference/transition_law_examples_v1.jsonl",
        "rmc_engine_v1/reference/syntactic_firewall_examples_v1.jsonl",
        "rmc_engine_v1/reference/gold_reference_v1.jsonl",
        "rmc_engine_v1/reference/scripture_phase_archetypes_v1.jsonl",
        "rmc_engine_v1/reference/README_rmc_resonance_reference_v1.md",
        "scripts/test_rmc_resonance_lexicon_behavior.py",
        "scripts/test_rmc_gold_reference_behavior.py",
    ]
    for rel in required:
        check("file_exists_" + rel.replace('/', '_'), (ROOT / rel).exists(), rel)

    try:
        mod = importlib.import_module("rmc_engine_v1.resonance_lexicon")
        check("resonance_lexicon_importable", True)
        boundary = mod.resonance_lexicon_boundary()
        check("resonance_lexicon_side_effect_free", boundary.get("side_effect_free") is True)
        check("resonance_lexicon_no_writes", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False)
        check("letter_level_cannot_trigger_circuit", boundary.get("letter_level_may_trigger_circuit_breaker") is False)
        bad = mod.analyze_resonance("bypass correction and naming and project now")
        check("bypass_correction_triggers_violation", bool(bad.get("violations")), json.dumps(bad.get("violations"), ensure_ascii=False))
        check("bypass_correction_blocks_projection", bad.get("projection_allowed") is False)
        safe = mod.analyze_resonance("do not bypass correction or naming before projection")
        check("negated_bypass_no_violation", not bool(safe.get("violations")), json.dumps(safe.get("violations"), ensure_ascii=False))
    except Exception as exc:
        check("resonance_lexicon_importable", False, str(exc))

    try:
        dmod = importlib.import_module("rmc_engine_v1.drift_engine")
        phase_report = {
            "input_event": {"event_id": "verify", "x_t_raw_input_preview": "bypass correction and naming and project now"},
            "phase_state": {
                "phase_primary": "Φ2",
                "phase_path_hypothesis": ["Φ2", "Φ6"],
                "confidence": 0.283,
                "phase_candidates": [{"phase":"Φ2","confidence":0.283},{"phase":"Φ6","confidence":0.283}],
                "transition_warnings": [{"type":"phase_skip_review"}],
                "routing": ["identify_poles", "correction_gate_candidate", "next_module:drift_analyzer"],
            },
        }
        out = dmod.analyze_drift(phase_report)
        check("drift_engine_importable", True)
        check("drift_engine_includes_resonance_lexicon", isinstance(out.get("resonance_lexicon"), dict) and out["resonance_lexicon"].get("status") == "OK")
        check("drift_engine_still_triggers_circuit", out.get("circuit_breaker", {}).get("triggered") is True)
    except Exception as exc:
        check("drift_engine_importable", False, str(exc))

    main_py = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    check("main_py_has_resonance_endpoint_handler", '"/api/rmc/resonance-lexicon"' in main_py)
    check("main_py_has_resonance_adapter", "_p262b2_rmc_resonance_lexicon_v1" in main_py)
    check("main_py_imports_resonance_module", "rmc_engine_v1.resonance_lexicon" in main_py)

    run_script("scripts/test_rmc_resonance_lexicon_behavior.py")
    run_script("scripts/test_rmc_gold_reference_behavior.py")
    run_script("scripts/test_rmc_drift_engine_behavior.py")
    run_script("scripts/test_rmc_phase_parser_behavior.py")
    run_script("scripts/test_rmc_coherence_math_behavior.py")

    total = len(CHECKS)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = total - passed
    print("\nPATCH 262J1R-PREFLIGHT-B2 VERIFY")
    print("─" * 72)
    for name, ok, detail in CHECKS:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" :: {detail}" if detail else ""))
    print("─" * 72)
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_B2_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_B2_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
