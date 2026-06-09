#!/usr/bin/env python3
"""
forge/scripts/test_patch279_mea_claim_status_classifier.py

Behavior tests for Patch 279 — MEA Claim Status Classifier.
"""

from __future__ import annotations

import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORGE_ROOT))

from rmc_engine_v1.mea import (  # noqa: E402
    ClaimStatus,
    OutputPermission,
    ProblemManifest,
    DriftState,
    build_144hz_test_manifest,
    canonical_hash,
    claim_status_classifier_boundary,
    claim_status_taxonomy,
    classify_claim_status,
    from_dict,
    replay_candidate,
    replay_operator_path,
    score_convergence,
    score_information_gain,
    score_proof_debt,
)


class Results:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: object = "") -> None:
        if ok:
            self.passed += 1
            suffix = f" — {detail}" if detail != "" else ""
            print(f"  ✓ [PASS] {name}{suffix}")
        else:
            self.failed += 1
            suffix = f" — {detail}" if detail != "" else ""
            print(f"  ✗ [FAIL] {name}{suffix}")


def make_144hz_hypothesis_path(parent: ProblemManifest):
    ops = [
        {"operator_id": "branch", "theta_k": {"branch_label": "substrate-vs-harmonic", "branch_goal": parent.goal, "branch_unknown": ""}},
        {
            "operator_id": "hypothesize",
            "theta_k": {
                "hypothesis_id": "harmonic_from_90hz",
                "hypothesis_text": "144 Hz is a harmonic hypothesis derived from 90 Hz via the golden ratio relation.",
                "confidence": 0.35,
            },
        },
        {
            "operator_id": "derive",
            "theta_k": {
                "derived_fact": "144 Hz remains hypothesis-bound until direct measurement or a sealed derivation chain exists.",
                "proof_debt_delta": 0.30,
            },
        },
    ]
    preview = replay_operator_path(parent, ops)
    confirmed = replay_operator_path(parent, ops, expected_final_hash=preview.produced_final_hash)
    return confirmed, from_dict(confirmed.final_manifest)


def make_manifest(problem_id: str, *, proof_debt: float, facts=None, unknowns=None, claim_status="unclassified", drift=None) -> ProblemManifest:
    return ProblemManifest(
        problem_id=problem_id,
        goal="Classify candidate status.",
        known_facts=list(facts or ["A cited primary measurement supports the candidate."]),
        unknowns=list(unknowns or []),
        constraints=["Must not exceed evidence tier."],
        success_conditions=["Candidate satisfies the success condition."],
        phase_state="Phi6",
        proof_debt=proof_debt,
        claim_status=claim_status,
        output_permissions="sealed",
        goal_ancestry=["Classify candidate status."],
        drift_state=drift or DriftState(),
    )


def main() -> int:
    r = Results()
    print("PATCH 279 BEHAVIOR TESTS — MEA Claim Status Classifier")
    print(f"Forge root: {FORGE_ROOT}")

    taxonomy = claim_status_taxonomy()
    r.check("taxonomy_contains_recall", "recall" in taxonomy["statuses"])
    r.check("taxonomy_contains_verified_claim", "verified_claim" in taxonomy["statuses"])
    r.check("taxonomy_contains_hypothesis", "hypothesis" in taxonomy["statuses"])
    r.check("taxonomy_contains_rejected", "rejected" in taxonomy["statuses"])
    r.check("hard_law_hypothesis_not_verified", taxonomy["hard_laws"]["hypothesis_must_not_render_as_verified_claim"] is True)
    r.check("hard_law_recall_not_discovery", taxonomy["hard_laws"]["recall_must_not_render_as_discovery"] is True)
    r.check("hard_law_rejected_not_visible", taxonomy["hard_laws"]["rejected_candidate_not_user_visible"] is True)

    parent = build_144hz_test_manifest()
    recall_replay = replay_candidate(parent, "noop_recall", {}, expected_candidate_hash=canonical_hash(parent))
    recall_class = classify_claim_status(parent, parent, replay_result=recall_replay)
    r.check("recall_replay_confirmed", recall_replay.replay_confirmed is True)
    r.check("recall_classification", recall_class.claim_status == ClaimStatus.RECALL.value, recall_class.to_dict())
    r.check("recall_information_gain_zero", recall_class.information_gain == 0.0, recall_class.information_gain)
    r.check("recall_cannot_render_as_discovery", "discovery" in " ".join(recall_class.cannot_render_as))
    r.check("recall_user_visible_as_reference", recall_class.user_visible is True)

    path, candidate = make_144hz_hypothesis_path(parent)
    hypothesis_class = classify_claim_status(parent, candidate, replay_result=path)
    r.check("144hz_path_replay_confirmed", path.replay_confirmed is True)
    r.check("144hz_information_gain_positive", hypothesis_class.information_gain > 0.0, hypothesis_class.information_gain)
    r.check("144hz_hypothesis_not_verified_claim", hypothesis_class.claim_status == ClaimStatus.HYPOTHESIS.value, hypothesis_class.to_dict())
    r.check("144hz_hypothesis_blocks_verified_render", "verified fact" in " ".join(hypothesis_class.cannot_render_as))
    r.check("144hz_hypothesis_render_allowed", hypothesis_class.output_permissions == OutputPermission.RENDER_ALLOWED.value)

    bad_replay = replay_candidate(
        parent,
        "hypothesize",
        {"hypothesis_id": "harmonic_from_90hz", "hypothesis_text": "144 Hz is already empirically verified in myelin.", "confidence": 0.35},
        expected_candidate_hash=path.produced_final_hash,
    )
    rejected_class = classify_claim_status(parent, parent, replay_result=bad_replay)
    r.check("tampered_replay_not_confirmed", bad_replay.replay_confirmed is False)
    r.check("tampered_replay_classified_rejected", rejected_class.claim_status == ClaimStatus.REJECTED.value, rejected_class.to_dict())
    r.check("rejected_not_user_visible", rejected_class.user_visible is False)
    r.check("rejected_output_sealed", rejected_class.output_permissions == OutputPermission.SEALED.value)

    verified_parent = make_manifest("verified_case_parent", proof_debt=0.10, facts=["Primary source A exists."], unknowns=["Implementation target not yet written."])
    verified_parent.success_conditions = ["Full implementation target verified by published measurement."]
    verified_candidate = make_manifest("verified_case_parent", proof_debt=0.10, facts=["Primary source A exists.", "Primary measurement supports implementation target."], unknowns=[])
    verified_replay = replay_candidate(verified_candidate, "noop_recall", {}, expected_candidate_hash=canonical_hash(verified_candidate))
    verified_class = classify_claim_status(
        verified_parent,
        verified_candidate,
        replay_result=verified_replay,
        proof_debt_score=score_proof_debt(verified_candidate),
        information_gain_score=score_information_gain(verified_parent, verified_candidate),
        convergence_score=score_convergence(verified_parent, verified_candidate),
    )
    r.check("verified_case_information_gain_positive", verified_class.information_gain > 0.0, verified_class.information_gain)
    r.check("verified_case_classified_verified_claim", verified_class.claim_status == ClaimStatus.VERIFIED_CLAIM.value, verified_class.to_dict())

    derived_parent = make_manifest("derived_case_parent", proof_debt=0.30, facts=["Root theorem is sourced."], unknowns=["Derived relation missing."])
    derived_candidate = make_manifest("derived_case_parent", proof_debt=0.30, facts=["Root theorem is sourced.", "Derived relation follows from root theorem."], unknowns=[])
    derived_replay = replay_candidate(derived_candidate, "noop_recall", {}, expected_candidate_hash=canonical_hash(derived_candidate))
    derived_class = classify_claim_status(
        derived_parent,
        derived_candidate,
        replay_result=derived_replay,
        proof_debt_score=score_proof_debt(derived_candidate),
        information_gain_score=score_information_gain(derived_parent, derived_candidate),
        convergence_score=score_convergence(derived_parent, derived_candidate),
        logically_derived=True,
    )
    r.check("derived_case_classified_derived_claim", derived_class.claim_status == ClaimStatus.DERIVED_CLAIM.value, derived_class.to_dict())
    r.check("derived_case_cannot_render_empirical_fact", "empirical fact without derivation basis" in " ".join(derived_class.cannot_render_as))

    contradiction_parent = make_manifest("contradiction_case_parent", proof_debt=0.35, facts=["Two source paths disagree."], unknowns=["Conflict must be exposed."])
    contradiction_parent.contradictions.append("Source A conflicts with Source B.")
    contradiction_candidate = make_manifest("contradiction_case_parent", proof_debt=0.35, facts=["Two source paths disagree.", "The conflict is now exposed."], unknowns=["Conflict must be resolved later."])
    contradiction_replay = replay_candidate(contradiction_candidate, "noop_recall", {}, expected_candidate_hash=canonical_hash(contradiction_candidate))
    contradiction_class = classify_claim_status(
        contradiction_parent,
        contradiction_candidate,
        replay_result=contradiction_replay,
        proof_debt_score=score_proof_debt(contradiction_candidate),
        information_gain_score=score_information_gain(contradiction_parent, contradiction_candidate),
        convergence_score=score_convergence(contradiction_parent, contradiction_candidate),
    )
    r.check("contradiction_exposed_classification", contradiction_class.claim_status == ClaimStatus.CONTRADICTION_EXPOSED.value, contradiction_class.to_dict())

    test_parent = make_manifest("test_required_parent", proof_debt=0.60, facts=["Candidate has partial lab relevance."], unknowns=["Experiment not yet run."])
    test_parent.success_conditions = ["A test specification is now defined."]
    test_candidate = make_manifest("test_required_parent", proof_debt=0.60, facts=["Candidate has partial lab relevance.", "A test specification is now defined."], unknowns=["Experiment not yet run."], claim_status="test_required")
    test_replay = replay_candidate(test_candidate, "noop_recall", {}, expected_candidate_hash=canonical_hash(test_candidate))
    test_class = classify_claim_status(
        test_parent,
        test_candidate,
        replay_result=test_replay,
        proof_debt_score=score_proof_debt(test_candidate),
        information_gain_score=score_information_gain(test_parent, test_candidate),
        convergence_score=score_convergence(test_parent, test_candidate),
        requires_test=True,
    )
    r.check("test_required_classification", test_class.claim_status == ClaimStatus.TEST_REQUIRED.value, test_class.to_dict())
    r.check("test_required_cannot_render_claim", "claim" in " ".join(test_class.cannot_render_as))

    cold_parent = make_manifest("cold_parent", proof_debt=0.80, facts=["Weak path exists."], unknowns=["No path yet."])
    cold_candidate = make_manifest("cold_parent", proof_debt=0.80, facts=["Weak path exists.", "A speculative branch was attempted."], unknowns=["No path yet."])
    cold_replay = replay_candidate(cold_candidate, "noop_recall", {}, expected_candidate_hash=canonical_hash(cold_candidate))
    cold_class = classify_claim_status(
        cold_parent,
        cold_candidate,
        replay_result=cold_replay,
        proof_debt_score=score_proof_debt(cold_candidate),
        information_gain_score=score_information_gain(cold_parent, cold_candidate),
        convergence_score=score_convergence(cold_parent, cold_candidate),
    )
    r.check("cold_storage_classification", cold_class.claim_status == ClaimStatus.COLD_STORED.value, cold_class.to_dict())

    speculative_parent = make_manifest("spec_parent", proof_debt=0.80, facts=["Weak path exists."], unknowns=["Open path."])
    speculative_candidate = make_manifest("spec_parent", proof_debt=0.80, facts=["Weak path exists.", "Candidate satisfies the success condition weakly."], unknowns=["Open path."])
    speculative_replay = replay_candidate(speculative_candidate, "noop_recall", {}, expected_candidate_hash=canonical_hash(speculative_candidate))
    speculative_class = classify_claim_status(
        speculative_parent,
        speculative_candidate,
        replay_result=speculative_replay,
        proof_debt_score=score_proof_debt(speculative_candidate),
        information_gain_score=score_information_gain(speculative_parent, speculative_candidate),
        convergence_score=score_convergence(speculative_parent, speculative_candidate),
    )
    r.check("speculative_branch_classification", speculative_class.claim_status == ClaimStatus.SPECULATIVE_BRANCH.value, speculative_class.to_dict())

    drift_parent = make_manifest("drift_parent", proof_debt=0.20, facts=["Good source."], unknowns=["Open."])
    drift_candidate = make_manifest("drift_parent", proof_debt=0.20, facts=["Good source.", "New fact."], unknowns=[], drift=DriftState(phase_deviation=1.0, symbolic_entropy=1.0, semantic_drift=1.0, constraint_violations=1.0))
    drift_replay = replay_candidate(drift_candidate, "noop_recall", {}, expected_candidate_hash=canonical_hash(drift_candidate))
    drift_class = classify_claim_status(drift_parent, drift_candidate, replay_result=drift_replay)
    r.check("drift_above_threshold_rejected", drift_class.claim_status == ClaimStatus.REJECTED.value, drift_class.to_dict())

    boundary = claim_status_classifier_boundary()
    for key in [
        "read_only",
        "writes_files",
        "writes_memory",
        "writes_chroma",
        "writes_identity_vault",
        "calls_llm",
        "executes_shell",
        "creates_post_routes",
        "seeds_live_manifests",
        "seals_candidates",
        "promotes_to_memory",
        "renders_user_output",
        "mutates_existing_rmc_behavior",
    ]:
        expected = True if key == "read_only" else False
        r.check(f"classifier_boundary_{key}", boundary.get(key) is expected, boundary.get(key))

    print(f"RESULT: PATCH_279_BEHAVIOR {'PASS' if r.failed == 0 else 'FAIL'}  Total:{r.passed + r.failed} Passed:{r.passed} Failed:{r.failed}")
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
