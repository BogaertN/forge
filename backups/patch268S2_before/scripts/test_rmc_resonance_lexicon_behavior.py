#!/usr/bin/env python3
"""Behavior tests for Patch 262J1R-Preflight-B2 resonance lexicon."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rmc_engine_v1.resonance_lexicon import analyze_resonance, resonance_lexicon_boundary


def fail(msg: str) -> None:
    raise AssertionError(msg)


def assert_true(expr, msg: str) -> None:
    if not expr:
        fail(msg)


def assert_false(expr, msg: str) -> None:
    if expr:
        fail(msg)


def main() -> int:
    total = 0

    boundary = resonance_lexicon_boundary(); total += 1
    assert_true(boundary["side_effect_free"] is True, "boundary must be side-effect free")
    assert_true(boundary["letter_level_may_trigger_circuit_breaker"] is False, "letters cannot trigger circuit breaker")

    bad = analyze_resonance("bypass correction and naming and project now"); total += 1
    assert_true(bad["circuit_breaker_candidate"], "bypass correction must become circuit breaker candidate")
    assert_true(any(v["target_gate"] == "correction_gate" for v in bad["violations"]), "correction gate violation missing")
    assert_true(bad["projection_allowed"] is False, "projection must be blocked")

    safe = analyze_resonance("do not bypass correction or naming before projection"); total += 1
    assert_false(safe["circuit_breaker_candidate"], "negated bypass must not trigger circuit breaker")
    assert_false(bool(safe["violations"]), "negated bypass must not create violations")
    assert_true(safe["recommended_route"] in {"correction_then_naming_then_projection", "correction_required", "bounded_preview_only"}, "safe route unexpected")

    pv = analyze_resonance("project now without validation"); total += 1
    assert_true(pv["circuit_breaker_candidate"], "projection without validation must trigger circuit candidate")
    assert_true(any(v["target_gate"] == "validation_gate" for v in pv["violations"]), "validation gate violation missing")

    lawful = analyze_resonance("This is drifting. Correct it, name it, validate it, then prepare projection."); total += 1
    assert_false(lawful["circuit_breaker_candidate"], "lawful correction/naming/projection prep must not trigger circuit")
    assert_false(bool(lawful["violations"]), "lawful sequence must not create violations")
    assert_true(lawful["phase_vector"].get("Φ6", 0) > 0, "lawful sequence should activate Φ6")
    assert_true(lawful["phase_vector"].get("Φ7", 0) > 0, "lawful sequence should activate Φ7")

    junk = analyze_resonance("asdkjashd 8293u4 23!!!! $$$$ {{ {{ malformed ))))"); total += 1
    assert_true(junk["syntactic_firewall"]["syntactic_drift"], "malformed junk must trigger syntactic drift")

    weak = analyze_resonance("mmmmmmmmmmmm"); total += 1
    assert_false(weak["circuit_breaker_candidate"], "letter-only Φ5 signal must not trigger circuit breaker")
    assert_true(weak["letter_pulse_count"] >= 8, "letter pulses should be detected")

    phrase_first = analyze_resonance("validate before projection"); total += 1
    assert_false(phrase_first["circuit_breaker_candidate"], "validate before projection must be lawful")
    assert_true(any(ev.get("matched_text", "").lower() == "validate before projection" for ev in phrase_first["operator_phrases"]), "phrase operator not matched")

    print(f"Total: {total}")
    print(f"Passed: {total}")
    print("Failed: 0")
    print("RESULT: resonance_lexicon_B2_behavior_tests_pass=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
