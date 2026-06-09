#!/usr/bin/env python3
"""Production coverage tests for Patch 262J1R-Preflight-B4.

These tests fail if the resonance lexicon is still only a tiny seed fixture.
They enforce real corpus size, schema coverage, phase coverage, safe/bad contrast
pairs, and no duplicate key rows.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.lexicon_audit import lexicon_audit_report, lexicon_audit_boundary


def assert_true(expr, msg: str) -> None:
    if not expr:
        raise AssertionError(msg)


def main() -> int:
    report = lexicon_audit_report()
    boundary = lexicon_audit_boundary()
    checks = []

    def check(name, expr, detail=""):
        checks.append((name, bool(expr), detail))
        assert_true(expr, f"{name}: {detail}")

    check("audit_status_ok", report.get("status") == "OK", repr(report.get("failure_code")))
    check("boundary_read_only", boundary.get("side_effect_free") is True and boundary.get("writes_files") is False, repr(boundary))
    check("no_llm_no_chroma", boundary.get("calls_llm") is False and boundary.get("queries_chroma") is False, repr(boundary))
    for fname, result in report["threshold_results"].items():
        check("threshold_" + fname, result["passed"], repr(result))
    for phase, count in report["word_phase_counts"].items():
        check("phase_word_coverage_" + phase, count >= 25, f"count={count}")
    for name, ok in report["coverage_checks"].items():
        check("coverage_" + name, ok, repr(report.get(name)))
    check("bad_gold_balance", report["gold_reference_balance"]["bad_circuit_breaker_examples"] >= 60, repr(report["gold_reference_balance"]))
    check("safe_gold_balance", report["gold_reference_balance"]["safe_non_violation_examples"] >= 60, repr(report["gold_reference_balance"]))
    check("syntactic_gold_balance", report["gold_reference_balance"]["syntactic_gold_examples"] >= 10, repr(report["gold_reference_balance"]))

    print(f"Total: {len(checks)}")
    print(f"Passed: {len(checks)}")
    print("Failed: 0")
    print("RESULT: lexicon_production_coverage_B4_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
