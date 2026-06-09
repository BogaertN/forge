#!/usr/bin/env python3
"""
forge/scripts/test_patch276_mea_scoring_foundations.py

Behavior tests for Patch 276 — MEA Scoring Foundations.
All tests are read-only and deterministic.
"""

from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
os.chdir(FORGE_ROOT)
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    ClaimStatus,
    MemoryRef,
    PhaseState,
    ProblemManifest,
    build_144hz_test_manifest,
    build_manifest,
    score_information_gain,
    score_proof_debt,
    proof_debt_scoring_boundary,
    information_gain_scoring_boundary,
)


class Results:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        if ok:
            self.passed += 1
            suffix = f" — {detail}" if detail else ""
            print(f"  ✓ [PASS] {name}{suffix}")
        else:
            self.failed += 1
            suffix = f" — {detail}" if detail else ""
            print(f"  ✗ [FAIL] {name}{suffix}")


def build_parent_manifest():
    return build_manifest(
        problem_id="patch276_information_gain_case",
        goal="Determine whether the candidate structurally advances the problem.",
        known_facts=["Known fact A is established."],
        unknowns=["Unknown Q1 remains open.", "Unknown Q2 remains open."],
        constraints=["Must not assert stronger status than evidence allows."],
        contradictions=["Contradiction X remains unresolved."],
        success_conditions=["Resolve at least one unknown or add a verified fact."],
        failure_conditions=["No information gain and no replayable operator path."],
        phase_state=PhaseState.PHI4.value,
        proof_debt=0.60,
        claim_status=ClaimStatus.TEST_REQUIRED.value,
    )


def main() -> int:
    r = Results()
    print("PATCH 276 BEHAVIOR TESTS — MEA Scoring Foundations")
    print(f"Forge root: {FORGE_ROOT}")

    fixture = build_144hz_test_manifest()
    proof = score_proof_debt(fixture)
    r.check("proof_formula_locked", proof.formula == "B(c_i) = 1 - E(c_i)")
    r.check("proof_debt_equals_one_minus_evidence_support", round(1.0 - proof.evidence_support, 6) == proof.proof_debt)
    r.check("144hz_proof_debt_preserved_085", proof.proof_debt == 0.85, str(proof.proof_debt))
    r.check("144hz_evidence_support_015", proof.evidence_support == 0.15, str(proof.evidence_support))
    r.check("144hz_source_absence_count", proof.evidence_profile.source_absence_count >= 1, str(proof.evidence_profile.source_absence_count))
    r.check("144hz_explicit_unknown_count_2", proof.evidence_profile.explicit_unknown_count == 2, str(proof.evidence_profile.explicit_unknown_count))
    r.check("144hz_blocks_verified_claim", proof.blocks_verified_claim is True)
    r.check("144hz_blocks_derived_claim", proof.blocks_derived_claim is True)

    low_debt = ProblemManifest(
        problem_id="published_measurement_case",
        goal="Check low proof debt behavior with direct evidence refs.",
        known_facts=["Published measurement directly supports the claim."],
        unknowns=[],
        constraints=["Do not exceed published measurement scope."],
        success_conditions=["Primary measurement source exists."],
        failure_conditions=["Measurement source withdrawn."],
        memory_ancestry=[MemoryRef(memory_key="source:published_measurement", source="test", relevance=1.0, evidence_tier="published_measurement")],
        phase_state=PhaseState.PHI6.value,
        proof_debt=0.05,
        claim_status=ClaimStatus.DERIVED_CLAIM.value,
    )
    low_score = score_proof_debt(low_debt)
    r.check("low_debt_case_below_verified_block_threshold", low_score.proof_debt < 0.20, str(low_score.proof_debt))
    r.check("low_debt_case_does_not_block_verified_claim", low_score.blocks_verified_claim is False)

    info_self = score_information_gain(fixture, fixture)
    r.check("information_gain_formula_locked", info_self.formula == "I(c_i) = delta-K + delta-Q + delta-X")
    r.check("self_information_gain_zero", info_self.information_gain == 0.0, str(info_self.information_gain))
    r.check("self_information_gain_is_recall", info_self.is_noop_recall is True)

    parent = build_parent_manifest()
    candidate = copy.deepcopy(parent)
    candidate.known_facts = parent.known_facts + ["Known fact B is newly derived from a checked operator path."]
    candidate.unknowns = ["Unknown Q2 remains open."]
    candidate.contradictions = []
    candidate.proof_debt = 0.35
    advanced = score_information_gain(parent, candidate)
    r.check("advanced_candidate_information_gain_positive", advanced.information_gain > 0.0, str(advanced.information_gain))
    r.check("advanced_candidate_new_known_fact_count_1", advanced.new_known_fact_count == 1, str(advanced.new_known_fact_count))
    r.check("advanced_candidate_resolved_unknown_count_1", advanced.resolved_unknown_count == 1, str(advanced.resolved_unknown_count))
    r.check("advanced_candidate_resolved_contradiction_count_1", advanced.resolved_contradiction_count == 1, str(advanced.resolved_contradiction_count))
    r.check("advanced_candidate_not_recall", advanced.is_noop_recall is False)

    candidate_bad = copy.deepcopy(parent)
    candidate_bad.unknowns = parent.unknowns + ["New unknown introduced by unsupported leap."]
    bad = score_information_gain(parent, candidate_bad)
    r.check("introduced_unknown_does_not_create_gain", bad.information_gain == 0.0, str(bad.information_gain))
    r.check("introduced_unknown_count_1", bad.introduced_unknown_count == 1, str(bad.introduced_unknown_count))

    pb = proof_debt_scoring_boundary()
    ib = information_gain_scoring_boundary()
    for key in ("read_only", "writes_files", "writes_memory", "writes_chroma", "writes_identity_vault", "calls_llm", "executes_shell", "creates_post_routes", "seals_candidates", "promotes_to_memory"):
        if key == "read_only":
            r.check(f"proof_boundary_{key}", pb[key] is True)
            r.check(f"info_boundary_{key}", ib[key] is True)
        else:
            r.check(f"proof_boundary_no_{key}", pb[key] is False)
            r.check(f"info_boundary_no_{key}", ib[key] is False)

    print(f"RESULT: PATCH_276_BEHAVIOR {'PASS' if r.failed == 0 else 'FAIL'}  Total:{r.passed + r.failed} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
