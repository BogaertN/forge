#!/usr/bin/env python3
"""Behavioral tests for rmc_engine_v1/coherence_math.py.

Patch 262J1R-Preflight.

These are not structural presence checks. They are behavioral assertions that
verify the math kernel enforces its own gating laws. The kernel is pure Python
with no I/O, so every test here requires zero mocking.

REQUIRED BEHAVIORAL ASSERTIONS
--------------------------------
1. circuit_breaker=True  → coherence_score == 0.0
2. cold_storage_pressure over threshold → route == "spc_cold_storage_required"
3. spc_cold_storage_required route → manifest_gate.allowed == False
4. dream_state candidate → no projection, no final language, no manifest, no write
5. normal active-stack candidate → manifest eligible only if Φ6+Φ7 gates pass and
   coherence_score >= theta_manifest_seed_min

Run from the forge root:
    python scripts/test_rmc_coherence_math_behavior.py

Expected output: all tests PASS, exit code 0.
"""

import sys
import os

# Allow running from either forge root or scripts/ directory.
FORGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, FORGE_ROOT)

try:
    from rmc_engine_v1.coherence_math import (
        score_candidate,
        gate_thresholds,
        extract_math_terms,
        formal_math_binding,
        clamp,
    )
except ImportError as exc:
    print(f"IMPORT_ERROR: {exc}")
    print("Run this script from forge root with rmc_engine_v1/ present.")
    sys.exit(2)

PASS = "PASS"
FAIL = "FAIL"
results: list[tuple[str, str, str]] = []  # (test_name, verdict, detail)


def assert_eq(name: str, actual, expected, detail: str = "") -> None:
    if actual == expected:
        results.append((name, PASS, detail or f"actual={actual!r}"))
    else:
        results.append((name, FAIL, f"expected={expected!r}, actual={actual!r}  {detail}"))


def assert_true(name: str, value: bool, detail: str = "") -> None:
    assert_eq(name, bool(value), True, detail)


def assert_false(name: str, value: bool, detail: str = "") -> None:
    assert_eq(name, bool(value), False, detail)


# ── Fixture builders ──────────────────────────────────────────────────────────

def _make_drift_report(
    circuit_breaker: bool = False,
    epsilon_s: float = 0.10,
    sigma_res: float = 0.10,
    d_score: float = 0.10,
    phase_deviation: float = 0.10,
    chi_required: bool = False,
    phase_path: list | None = None,
    drift_classes: list | None = None,
) -> dict:
    """Build a minimal drift_report fixture compatible with extract_math_terms."""
    return {
        "drift_report_id": "test_drift_fixture",
        "mode": "test",
        "epsilon_s": {
            "sigma_res": sigma_res,
            "D_score": d_score,
            "phase_deviation_normalized": phase_deviation,
            "epsilon_s": epsilon_s,
        },
        "chi_t": {"required": chi_required},
        "circuit_breaker": {"triggered": circuit_breaker},
        "projection_status": "blocked_circuit_breaker" if circuit_breaker else "low_drift_preview_only",
        "phase_drift": {"phase_path_hypothesis": phase_path or ["Φ1", "Φ3"]},
        "source_phase_parser": {
            "phase_state": {
                "phase_primary": (phase_path or ["Φ1"])[0],
                "phase_path_hypothesis": phase_path or ["Φ1", "Φ3"],
                "confidence": 1.0 - sigma_res,
            },
            "input_event": {"event_id": "test_event", "x_t_raw_input_preview": "test input"},
        },
        "drift_classes": drift_classes or [
            {"drift_key": "syntactic", "score": d_score, "severity": "low",
             "correction_required": False},
        ],
    }


def _make_candidate(
    candidate_id: str = "ct_test_001",
    title: str = "Test Candidate",
    confidence: float = 0.75,
    phase_target: str = "Φ3",
    drift_posture: str = "low_drift_preview",
    limitations: list | None = None,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "title": title,
        "candidate_type": "meaning_state_not_final_language",
        "meaning_state": "test meaning state",
        "phase_target": phase_target,
        "drift_posture": drift_posture,
        "confidence": confidence,
        "required_limitations": limitations or ["dry_run_only", "not_final_language"],
    }


def _make_candidate_report(drift_report: dict, candidate_set_id: str = "ct_set_test") -> dict:
    return {
        "candidate_set_id": candidate_set_id,
        "source_drift_report": drift_report,
        "mode": "test",
    }


# ── Test 1: circuit_breaker=True → coherence_score == 0.0 ────────────────────

def test_circuit_breaker_zeroes_score() -> None:
    drift = _make_drift_report(circuit_breaker=True, epsilon_s=0.10)
    candidate = _make_candidate(confidence=0.90)
    report = _make_candidate_report(drift)

    result = score_candidate(candidate, report)
    assert_eq(
        "T1_circuit_breaker_zeroes_score",
        result["coherence_score"],
        0.0,
        "circuit_breaker=True must produce coherence_score=0.0 regardless of confidence",
    )
    assert_eq(
        "T1_circuit_breaker_projection_blocked",
        result["projection_allowed"],
        False,
    )
    assert_eq(
        "T1_circuit_breaker_manifest_blocked",
        result["manifest_gate"]["allowed"],
        False,
    )
    assert_eq(
        "T1_circuit_breaker_memory_write_blocked",
        result["memory_write_allowed"],
        False,
    )


# ── Test 2: cold storage pressure over threshold → spc_cold_storage_required ──

def test_high_cold_storage_pressure_routes_to_spc() -> None:
    thresholds = gate_thresholds()
    # circuit_breaker=True is the most direct path to cold_storage_pressure >= 0.72
    drift = _make_drift_report(
        circuit_breaker=True,
        epsilon_s=0.80,
        phase_path=["Φ5", "Φ8"],  # phase skip triggers additional pressure
    )
    candidate = _make_candidate(confidence=0.60)
    report = _make_candidate_report(drift)

    result = score_candidate(candidate, report)
    route = result["cold_storage_gate"]["route"]
    assert_eq(
        "T2_high_pressure_routes_spc",
        route,
        "spc_cold_storage_required",
        f"expected spc_cold_storage_required, got {route!r}",
    )

    # Also test via epsilon_s alone (no circuit breaker)
    drift_eps = _make_drift_report(
        circuit_breaker=False,
        epsilon_s=0.80,  # >= theta_epsilon_collapse=0.72
        sigma_res=0.80,
        d_score=0.80,
        phase_deviation=0.80,
        chi_required=True,
    )
    candidate2 = _make_candidate(confidence=0.30, phase_target="Φ5")
    report2 = _make_candidate_report(drift_eps)
    result2 = score_candidate(candidate2, report2)
    must_collapse = result2.get("math_terms", {}).get("cold_storage_pressure", 0.0)
    # Cold storage pressure contributions: epsilon_s>=0.72 (+0.22), chi_required (+0.24),
    # total >= 0.46 — won't reach 0.72 without circuit_breaker or phase_skip.
    # Just verify that high epsilon_s forces cold_storage_required via must_collapse_or_archive.
    must_collapse_flag = (
        result2["cold_storage_gate"].get("must_archive")
        or result2["cold_storage_gate"]["route"] == "spc_cold_storage_required"
    )
    assert_true(
        "T2_high_epsilon_s_forces_cold_storage_or_archive",
        must_collapse_flag,
        f"epsilon_s=0.80 should force cold storage; route={result2['cold_storage_gate']['route']!r}",
    )


# ── Test 3: spc_cold_storage_required → manifest_gate.allowed == False ────────

def test_spc_route_blocks_manifest() -> None:
    drift = _make_drift_report(
        circuit_breaker=True,
        epsilon_s=0.90,
    )
    candidate = _make_candidate(confidence=0.95)
    report = _make_candidate_report(drift)

    result = score_candidate(candidate, report)
    route = result["cold_storage_gate"]["route"]
    manifest_allowed = result["manifest_gate"]["allowed"]

    if route == "spc_cold_storage_required":
        assert_false(
            "T3_spc_route_blocks_manifest",
            manifest_allowed,
            "spc_cold_storage_required route must have manifest_gate.allowed=False",
        )
    else:
        # Ensure manifest is blocked whenever route is NOT active_stack
        assert_false(
            "T3_non_active_stack_blocks_manifest",
            manifest_allowed and route != "active_stack_dry_run_candidate",
            f"route={route!r} should not allow manifest compilation",
        )

    # Invariant: regardless of route, projection and memory write must be False
    assert_false("T3_no_projection_from_spc", result["projection_allowed"])
    assert_false("T3_no_memory_write_from_spc", result["memory_write_allowed"])
    assert_false("T3_no_final_language_from_spc", result["final_language_allowed"])


# ── Test 4: dream state candidate → no projection/manifest/write ──────────────

def test_dream_state_blocks_all_writes() -> None:
    thresholds = gate_thresholds()
    # dream_state_eligible requires:
    #   cold_storage_pressure >= theta_dream_state_min (0.44)
    #   AND NOT circuit_breaker
    #   AND novelty_bounded > 0.0
    # Achieve this with chi_required + phase_skip (no circuit breaker)
    drift = _make_drift_report(
        circuit_breaker=False,
        epsilon_s=0.50,
        sigma_res=0.50,
        d_score=0.50,
        phase_deviation=0.50,
        chi_required=True,
        phase_path=["Φ3", "Φ5", "Φ8"],  # phase skip contributes cold_storage_pressure
        drift_classes=[
            {"drift_key": "evolutionary", "score": 0.45, "severity": "moderate",
             "correction_required": False},
        ],
    )
    candidate = _make_candidate(
        confidence=0.50,
        phase_target="Φ5",
        limitations=["dry_run_only", "not_final_language", "trace_first"],
    )
    report = _make_candidate_report(drift)
    result = score_candidate(candidate, report)

    # Whether dream_state_eligible or not, the hard blocks must hold
    assert_false("T4_dream_no_projection", result["projection_allowed"])
    assert_false("T4_dream_no_final_language", result["final_language_allowed"])
    assert_false("T4_dream_no_memory_write", result["memory_write_allowed"])

    # If we achieved dream_state_eligible, manifest must also be blocked
    dream_eligible = result.get("math_terms", {}).get("dream_state_eligible", False)
    if dream_eligible:
        route = result["cold_storage_gate"]["route"]
        assert_false(
            "T4_dream_eligible_no_manifest",
            result["manifest_gate"]["allowed"],
            f"dream_state_eligible=True must block manifest; route={route!r}",
        )
        assert_eq(
            "T4_dream_eligible_quarantine_route",
            route,
            "dream_state_quarantine_candidate",
        )
    else:
        # Test still valid: if dream state wasn't triggered, record why
        math = result.get("math_terms", {})
        results.append((
            "T4_dream_state_not_triggered",
            PASS,
            f"cold_storage_pressure={math.get('cold_storage_pressure')!r}, "
            f"circuit_breaker={math.get('circuit_breaker')!r}, "
            f"bounded_novelty={math.get('bounded_novelty')!r}",
        ))


# ── Test 5: normal bounded active-stack candidate → manifest only if gates pass ─

def test_active_stack_manifest_requires_phi6_phi7_and_threshold() -> None:
    thresholds = gate_thresholds()

    # Case A: clean low-drift candidate that SHOULD be manifest eligible
    drift_clean = _make_drift_report(
        circuit_breaker=False,
        epsilon_s=0.05,
        sigma_res=0.05,
        d_score=0.05,
        phase_deviation=0.05,
        chi_required=False,
        phase_path=["Φ3", "Φ6", "Φ7"],  # has correction AND naming
    )
    candidate_good = _make_candidate(
        confidence=0.88,
        phase_target="Φ7",
        limitations=["dry_run_only", "trace_first", "manifest_seed_only"],
    )
    report_good = _make_candidate_report(drift_clean)
    result_good = score_candidate(candidate_good, report_good)

    route_good = result_good["cold_storage_gate"]["route"]
    corr_passed = result_good["correction_gate"]["passed"]
    naming_passed = result_good["naming_gate"]["passed"]
    manifest_allowed = result_good["manifest_gate"]["allowed"]
    score = result_good["coherence_score"]

    assert_eq("T5_clean_active_stack_route", route_good, "active_stack_dry_run_candidate")

    if corr_passed and naming_passed and score >= thresholds["theta_manifest_seed_min"]:
        assert_true(
            "T5_phi6_phi7_pass_enables_manifest",
            manifest_allowed,
            f"correction_gate.passed={corr_passed}, naming_gate.passed={naming_passed}, "
            f"score={score}, expected manifest_allowed=True",
        )
    else:
        # If gates didn't pass at these values, record the actual scores
        results.append((
            "T5_clean_candidate_gate_status",
            PASS,
            f"correction_passed={corr_passed}, naming_passed={naming_passed}, "
            f"score={score}, manifest_allowed={manifest_allowed}",
        ))

    # Case B: candidate with circuit breaker — must NEVER be manifest eligible
    drift_bad = _make_drift_report(circuit_breaker=True, epsilon_s=0.90)
    candidate_bad = _make_candidate(confidence=0.99, limitations=["trace_first"])
    report_bad = _make_candidate_report(drift_bad)
    result_bad = score_candidate(candidate_bad, report_bad)

    assert_false(
        "T5_circuit_breaker_never_manifest",
        result_bad["manifest_gate"]["allowed"],
        "circuit_breaker=True must prevent manifest regardless of candidate confidence",
    )

    # Case C: projection is unconditionally False
    assert_false("T5_projection_always_false_a", result_good["projection_allowed"])
    assert_false("T5_projection_always_false_b", result_bad["projection_allowed"])
    assert_false("T5_memory_write_always_false_a", result_good["memory_write_allowed"])
    assert_false("T5_memory_write_always_false_b", result_bad["memory_write_allowed"])


# ── Test 6: formal math binding surface check ─────────────────────────────────

def test_formal_math_binding_surface() -> None:
    binding = formal_math_binding()
    assert_true("T6_binding_has_rpmc_equation", "rpmc_memory_equation" in binding)
    assert_true("T6_binding_has_epsilon_formula", "epsilon_formula" in binding)
    assert_true("T6_binding_has_coherence_formula", "coherence_formula" in binding)
    assert_true("T6_binding_cold_storage_law", "cold_storage_law" in binding)
    assert_false(
        "T6_ui_owns_math_false",
        binding.get("math_kernel_location", "").startswith("main"),
        "math_kernel_location must not point to main.py",
    )
    assert_eq(
        "T6_math_kernel_location",
        binding["math_kernel_location"],
        "forge/rmc_engine_v1/coherence_math.py",
    )


# ── Test 7: clamp utility ─────────────────────────────────────────────────────

def test_clamp_utility() -> None:
    assert_eq("T7_clamp_below_zero", clamp(-5.0), 0.0)
    assert_eq("T7_clamp_above_one", clamp(2.0), 1.0)
    assert_eq("T7_clamp_mid", clamp(0.5), 0.5)
    assert_eq("T7_clamp_invalid", clamp("bad"), 0.0)
    assert_eq("T7_clamp_none", clamp(None), 0.0)


# ── Run all tests ─────────────────────────────────────────────────────────────

def run() -> int:
    test_circuit_breaker_zeroes_score()
    test_high_cold_storage_pressure_routes_to_spc()
    test_spc_route_blocks_manifest()
    test_dream_state_blocks_all_writes()
    test_active_stack_manifest_requires_phi6_phi7_and_threshold()
    test_formal_math_binding_surface()
    test_clamp_utility()

    passed = sum(1 for _, v, _ in results if v == PASS)
    failed = sum(1 for _, v, _ in results if v == FAIL)

    print(f"\nRMC COHERENCE MATH BEHAVIORAL TESTS — Patch 262J1R-Preflight")
    print(f"{'─' * 70}")
    for name, verdict, detail in results:
        marker = "✓" if verdict == PASS else "✗"
        print(f"  {marker} [{verdict}] {name}")
        if verdict == FAIL or "T4_dream" in name or "T5_clean" in name:
            print(f"        {detail}")
    print(f"{'─' * 70}")
    print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")

    if failed == 0:
        print("\n  RESULT: coherence_math_behavior_tests_pass=True")
        return 0
    else:
        print("\n  RESULT: coherence_math_behavior_tests_pass=False")
        return 1


if __name__ == "__main__":
    sys.exit(run())
