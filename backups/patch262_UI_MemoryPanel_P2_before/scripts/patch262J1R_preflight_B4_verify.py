#!/usr/bin/env python3
"""Verifier for Patch 262J1R-Preflight-B4.

B4 is not a cosmetic pass. It verifies that the resonance lexicon and gold
standard are materially expanded beyond seed stubs before Candidate Generator
extraction.
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
    detail = proc.stdout.splitlines()[-1] if proc.stdout else ""
    check(rel.replace('/', '_') + "_passes", ok, detail)
    if not ok:
        print(proc.stdout)
    return ok


def main() -> int:
    required = [
        "rmc_engine_v1/lexicon_audit.py",
        "rmc_engine_v1/resonance_lexicon.py",
        "rmc_engine_v1/phase_codex.py",
        "rmc_engine_v1/reference/word_loop_seed_lexicon_v1.jsonl",
        "rmc_engine_v1/reference/operator_phrase_lexicon_v1.jsonl",
        "rmc_engine_v1/reference/gold_reference_v1.jsonl",
        "rmc_engine_v1/reference/transition_law_examples_v1.jsonl",
        "rmc_engine_v1/reference/syntactic_firewall_examples_v1.jsonl",
        "rmc_engine_v1/reference/scripture_phase_archetypes_v1.jsonl",
        "scripts/test_rmc_lexicon_production_coverage.py",
        "scripts/test_rmc_expanded_gold_reference_behavior.py",
    ]
    for rel in required:
        check("file_exists_" + rel.replace('/', '_'), (ROOT / rel).exists(), rel)

    try:
        audit_mod = importlib.import_module("rmc_engine_v1.lexicon_audit")
        report = audit_mod.lexicon_audit_report()
        check("lexicon_audit_importable", True)
        check("lexicon_audit_status_ok", report.get("status") == "OK", repr(report.get("failure_code")))
        check("lexicon_word_rows_ge_250", report["counts"].get("word_loop_seed_lexicon_v1.jsonl", 0) >= 250, repr(report["counts"]))
        check("lexicon_phrase_rows_ge_150", report["counts"].get("operator_phrase_lexicon_v1.jsonl", 0) >= 150, repr(report["counts"]))
        check("gold_rows_ge_150", report["counts"].get("gold_reference_v1.jsonl", 0) >= 150, repr(report["counts"]))
        check("transitions_ge_75", report["counts"].get("transition_law_examples_v1.jsonl", 0) >= 75, repr(report["counts"]))
        check("syntactic_ge_50", report["counts"].get("syntactic_firewall_examples_v1.jsonl", 0) >= 50, repr(report["counts"]))
        check("scripture_ge_30", report["counts"].get("scripture_phase_archetypes_v1.jsonl", 0) >= 30, repr(report["counts"]))
        check("all_coverage_checks_true", all(report.get("coverage_checks", {}).values()), repr(report.get("coverage_checks")))
        boundary = audit_mod.lexicon_audit_boundary()
        check("audit_side_effect_free", boundary.get("side_effect_free") is True, repr(boundary))
        check("audit_no_writes", boundary.get("writes_files") is False and boundary.get("writes_rmc_memory") is False, repr(boundary))
        check("audit_no_llm_no_chroma", boundary.get("calls_llm") is False and boundary.get("queries_chroma") is False, repr(boundary))
    except Exception as exc:
        check("lexicon_audit_importable", False, str(exc))

    try:
        rmod = importlib.import_module("rmc_engine_v1.resonance_lexicon")
        boundary = rmod.resonance_lexicon_boundary()
        check("resonance_engine_version_b4", str(boundary.get("engine_version", "")).endswith("_B4"), repr(boundary.get("engine_version")))
        check("resonance_boundary_has_audit_ok", boundary.get("lexicon_audit_status") == "OK", repr(boundary))
        bad = rmod.analyze_resonance("bypass correction and naming and project now")
        safe = rmod.analyze_resonance("do not bypass correction or naming before projection")
        check("bypass_still_blocks", bad.get("projection_allowed") is False and bad.get("circuit_breaker_candidate") is True, repr(bad.get("violations")))
        check("safe_negation_still_safe", safe.get("circuit_breaker_candidate") is False and not safe.get("violations"), repr(safe.get("violations")))
        check("resonance_output_has_audit_summary", bad.get("lexicon_audit_summary", {}).get("status") == "OK", repr(bad.get("lexicon_audit_summary")))
    except Exception as exc:
        check("resonance_lexicon_importable", False, str(exc))

    main_py = (ROOT / "main.py").read_text(encoding="utf-8", errors="replace")
    check("main_py_has_lexicon_audit_endpoint", '"/api/rmc/lexicon-audit"' in main_py)
    check("main_py_has_lexicon_audit_adapter", "_p262b4_rmc_lexicon_audit_v1" in main_py)
    check("main_py_imports_lexicon_audit", "rmc_engine_v1.lexicon_audit" in main_py)
    check("main_py_resonance_reports_b4", "Patch 262J1R-Preflight-B4" in main_py)

    run_script("scripts/test_rmc_lexicon_production_coverage.py")
    run_script("scripts/test_rmc_expanded_gold_reference_behavior.py")
    run_script("scripts/test_rmc_resonance_lexicon_behavior.py")
    run_script("scripts/test_rmc_gold_reference_behavior.py")
    run_script("scripts/test_rmc_resonance_codex_integration.py")
    run_script("scripts/test_rmc_phase_codex_binding.py")
    run_script("scripts/test_rmc_drift_engine_behavior.py")
    run_script("scripts/test_rmc_phase_parser_behavior.py")
    run_script("scripts/test_rmc_coherence_math_behavior.py")

    total = len(CHECKS)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = total - passed
    print("\nPATCH 262J1R-PREFLIGHT-B4 VERIFY")
    print("─" * 72)
    for name, ok, detail in CHECKS:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" :: {detail}" if detail else ""))
    print("─" * 72)
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed:
        print("RESULT: PATCH_262J1R_PREFLIGHT_B4_VERIFY_FAILED")
        return 1
    print("RESULT: PATCH_262J1R_PREFLIGHT_B4_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
