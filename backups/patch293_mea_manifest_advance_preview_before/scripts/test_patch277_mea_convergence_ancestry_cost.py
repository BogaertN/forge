#!/usr/bin/env python3
"""
forge/scripts/test_patch277_mea_convergence_ancestry_cost.py

Patch 277 behavior tests — MEA Convergence / Ancestry / Cost Scoring.
These tests prove the new scorers are deterministic, read-only, and do not
promote any candidate into live MEA runtime behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    ClaimStatus,
    OutputPermission,
    build_144hz_test_manifest,
    build_manifest,
    score_convergence,
    score_goal_ancestry,
    score_information_gain,
    score_operator_cost,
    convergence_scoring_boundary,
    goal_ancestry_scoring_boundary,
    operator_cost_scoring_boundary,
    CONVERGENCE_FORMULA,
    GOAL_ANCESTRY_FORMULA,
    OPERATOR_COST_FORMULA,
)


class Results:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        if ok:
            self.passed += 1
            print(f"  ✓ [PASS] {name}{' — ' + detail if detail else ''}")
        else:
            self.failed += 1
            print(f"  ✗ [FAIL] {name}{' — ' + detail if detail else ''}")


def partial_harmonic_candidate(parent):
    return build_manifest(
        problem_id=parent.problem_id,
        goal=parent.goal,
        known_facts=parent.known_facts + [
            "144 Hz formally derived as harmonic from published substrate with derivation chain."
        ],
        unknowns=["Direct empirical measurement of 144 Hz in myelin."],
        constraints=parent.constraints,
        success_conditions=parent.success_conditions,
        failure_conditions=parent.failure_conditions,
        proof_debt=0.55,
        claim_status=ClaimStatus.HYPOTHESIS.value,
        output_permissions=OutputPermission.SEALED.value,
        goal_ancestry=parent.goal_ancestry + [
            "Determine whether 144 Hz can be formally derived as a harmonic from 90 Hz."
        ],
    )


def drifted_signal_processing_candidate(parent):
    return build_manifest(
        problem_id=parent.problem_id,
        goal="Develop general signal processing tutorials for audio windowing.",
        known_facts=parent.known_facts + [
            "Fourier transform windowing reduces spectral leakage in audio processing."
        ],
        unknowns=parent.unknowns,
        constraints=parent.constraints,
        success_conditions=parent.success_conditions,
        failure_conditions=parent.failure_conditions,
        proof_debt=0.40,
        claim_status=ClaimStatus.HYPOTHESIS.value,
        output_permissions=OutputPermission.SEALED.value,
        goal_ancestry=parent.goal_ancestry + [
            "Evaluate 144 Hz substrate versus harmonic.",
            "Compare resonance relations in signal analysis.",
            "General signal processing resonance tools.",
            "Fourier transform windowing methods.",
            "Audio DSP spectral leakage tutorial.",
        ],
    )


def main() -> int:
    r = Results()
    print("PATCH 277 BEHAVIOR TESTS — MEA Convergence / Ancestry / Cost")
    print(f"Forge root: {FORGE_ROOT}")

    parent = build_144hz_test_manifest()
    partial = partial_harmonic_candidate(parent)
    drifted = drifted_signal_processing_candidate(parent)

    conv_self = score_convergence(parent, parent)
    conv_partial = score_convergence(parent, partial)
    conv_drifted = score_convergence(parent, drifted)
    ancestry_self = score_goal_ancestry(parent, parent)
    ancestry_partial = score_goal_ancestry(parent, partial)
    ancestry_drifted = score_goal_ancestry(parent, drifted)
    info_drifted = score_information_gain(parent, drifted)
    cost_empty = score_operator_cost(parent)
    cost_cheap = score_operator_cost(["check_phase", "check_constraint"])
    cost_expensive = score_operator_cost(["run_simulation", "external_search"])
    cost_unknown = score_operator_cost(["made_up_operator"])

    r.check("convergence_formula_locked", conv_self.formula == CONVERGENCE_FORMULA)
    r.check("convergence_self_not_terminal", conv_self.omega < 0.50, str(conv_self.omega))
    r.check("partial_candidate_converges_one_path", 0.45 <= conv_partial.omega <= 0.70, str(conv_partial.omega))
    r.check("partial_candidate_has_one_fully_satisfied_condition", conv_partial.fully_satisfied_count == 1, str(conv_partial.fully_satisfied_count))
    r.check("drifted_candidate_has_positive_information_gain", info_drifted.information_gain > 0.0, str(info_drifted.information_gain))
    r.check("drifted_candidate_low_convergence_despite_info_gain", conv_drifted.omega <= 0.25, str(conv_drifted.omega))

    r.check("goal_ancestry_formula_locked", ancestry_self.formula == GOAL_ANCESTRY_FORMULA)
    r.check("goal_ancestry_self_high", ancestry_self.ancestry_score >= 0.95, str(ancestry_self.ancestry_score))
    r.check("goal_ancestry_partial_still_high", ancestry_partial.ancestry_score >= 0.70, str(ancestry_partial.ancestry_score))
    r.check("goal_ancestry_drifted_chain_degrades", ancestry_drifted.ancestry_score < 0.35, str(ancestry_drifted.ancestry_score))
    r.check("goal_ancestry_drifted_lineage_long", ancestry_drifted.lineage_length >= 5, str(ancestry_drifted.lineage_length))

    r.check("operator_cost_formula_locked", cost_cheap.formula == OPERATOR_COST_FORMULA)
    r.check("operator_cost_empty_zero", cost_empty.operator_cost == 0.0, str(cost_empty.operator_cost))
    r.check("operator_cost_cheap_low", cost_cheap.operator_cost < 0.20, str(cost_cheap.operator_cost))
    r.check("operator_cost_expensive_high", cost_expensive.operator_cost >= 0.90, str(cost_expensive.operator_cost))
    r.check("operator_cost_unknown_charged_default", cost_unknown.unknown_operator_count == 1, str(cost_unknown.to_dict()))
    r.check("operator_cost_unknown_midrange", 0.35 <= cost_unknown.operator_cost <= 0.55, str(cost_unknown.operator_cost))

    for label, boundary in [
        ("convergence", convergence_scoring_boundary()),
        ("goal_ancestry", goal_ancestry_scoring_boundary()),
        ("operator_cost", operator_cost_scoring_boundary()),
    ]:
        r.check(f"{label}_boundary_read_only", boundary.get("read_only") is True)
        r.check(f"{label}_boundary_no_writes_files", boundary.get("writes_files") is False)
        r.check(f"{label}_boundary_no_writes_memory", boundary.get("writes_memory") is False)
        r.check(f"{label}_boundary_no_writes_chroma", boundary.get("writes_chroma") is False)
        r.check(f"{label}_boundary_no_writes_identity_vault", boundary.get("writes_identity_vault") is False)
        r.check(f"{label}_boundary_no_calls_llm", boundary.get("calls_llm") is False)
        r.check(f"{label}_boundary_no_executes_shell", boundary.get("executes_shell") is False)
        r.check(f"{label}_boundary_no_creates_post_routes", boundary.get("creates_post_routes") is False)
        r.check(f"{label}_boundary_no_seals_candidates", boundary.get("seals_candidates") is False)
        r.check(f"{label}_boundary_no_promotes_to_memory", boundary.get("promotes_to_memory") is False)

    total = r.passed + r.failed
    print(f"RESULT: PATCH_277_BEHAVIOR {'PASS' if r.failed == 0 else 'FAIL'}  Total:{total} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
