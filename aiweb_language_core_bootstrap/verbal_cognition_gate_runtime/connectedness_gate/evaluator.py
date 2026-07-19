"""Deterministic exact-authority Slice 40E connectedness evaluator."""
from __future__ import annotations

from .identity import with_expected_finding_id, with_expected_result_identity
from .schema import (
    ConnectednessAssertion,
    ConnectednessAuthorityState,
    ConnectednessEvaluationInput,
    ConnectednessFinding,
    ConnectednessFindingKind,
    ConnectednessGateResult,
    ConnectednessJudgment,
    ConnectednessOverallState,
)
from .validation import assert_valid_evaluation_input, assert_valid_result


def _finding(
    value: ConnectednessEvaluationInput,
    assertion: ConnectednessAssertion | None,
    observation,
    kind: ConnectednessFindingKind,
) -> ConnectednessFinding:
    return with_expected_finding_id(
        ConnectednessFinding(
            finding_id="connectedness_finding:placeholder",
            evaluation_input_ref=value.evaluation_input_id,
            assertion_ref=(assertion.assertion_id if assertion else None),
            finding_kind=kind,
            assertion_kind=(assertion.assertion_kind if assertion else None),
            authority_state=(
                observation.authority_state
                if observation
                else ConnectednessAuthorityState.ADMITTED
            ),
            connection_judgment=(
                observation.connection_judgment
                if observation
                else ConnectednessJudgment.CONNECTED
            ),
            supporting_refs=(observation.supporting_refs if observation else ()),
            disconnection_refs=(
                observation.disconnection_refs if observation else ()
            ),
            trace_refs=(observation.trace_refs if observation else value.trace_refs),
            provenance_refs=(
                observation.provenance_refs
                if observation
                else value.provenance_refs
            ),
            reason_refs=(
                (f"connectedness:{kind.value}",)
                + (
                    assertion.assertion_source_refs
                    if assertion
                    else ("slice40e:all_assertions_connected",)
                )
            ),
        )
    )


def evaluate_connectedness(
    value: ConnectednessEvaluationInput,
) -> ConnectednessGateResult:
    """Evaluate exact connection assertions without inventing any new link."""

    assert_valid_evaluation_input(value)
    observation_by_assertion = {
        observation.assertion_ref: observation
        for observation in value.observations
    }
    findings: list[ConnectednessFinding] = []
    counts = {
        "connected": 0,
        "disconnected": 0,
        "ambiguous": 0,
        "unsupported": 0,
        "conflicted": 0,
        "indeterminate": 0,
    }

    for assertion in value.assertions:
        observation = observation_by_assertion[assertion.assertion_id]
        if observation.authority_state is ConnectednessAuthorityState.ADMITTED:
            if observation.connection_judgment is ConnectednessJudgment.CONNECTED:
                counts["connected"] += 1
                kind = ConnectednessFindingKind.CONNECTED_ASSERTION
            else:
                counts["disconnected"] += 1
                kind = ConnectednessFindingKind.DISCONNECTED_ASSERTION
        elif observation.authority_state is ConnectednessAuthorityState.AMBIGUOUS:
            counts["ambiguous"] += 1
            kind = ConnectednessFindingKind.AMBIGUOUS_ASSERTION
        elif observation.authority_state is ConnectednessAuthorityState.UNSUPPORTED:
            counts["unsupported"] += 1
            kind = ConnectednessFindingKind.UNSUPPORTED_ASSERTION
        elif observation.authority_state is ConnectednessAuthorityState.CONFLICTED:
            counts["conflicted"] += 1
            kind = ConnectednessFindingKind.CONFLICTED_ASSERTION
        else:
            counts["indeterminate"] += 1
            kind = ConnectednessFindingKind.INDETERMINATE_AUTHORITY_ABSENT
        findings.append(_finding(value, assertion, observation, kind))

    if counts["conflicted"]:
        overall = ConnectednessOverallState.CONFLICTED
    elif counts["unsupported"]:
        overall = ConnectednessOverallState.UNSUPPORTED
    elif counts["ambiguous"]:
        overall = ConnectednessOverallState.AMBIGUOUS
    elif counts["indeterminate"]:
        overall = ConnectednessOverallState.INDETERMINATE
    elif counts["disconnected"]:
        overall = ConnectednessOverallState.DISCONNECTED
    else:
        overall = ConnectednessOverallState.CONNECTED
        findings.append(
            _finding(
                value,
                None,
                None,
                ConnectednessFindingKind.ALL_ASSERTIONS_CONNECTED,
            )
        )

    review = value.governance_bundle.review_record
    result = ConnectednessGateResult(
        result_id="connectedness_result:placeholder",
        evaluation_input_ref=value.evaluation_input_id,
        review_record_id=review.review_record_id,
        gate_id=review.identity.gate_id,
        gate_profile_id=review.profile.profile_id,
        candidate_input_ref=value.candidate_input_ref,
        predicate_id=value.predicate_id,
        predicate_version=value.predicate_version,
        frame_id=value.frame_id,
        frame_version=value.frame_version,
        overall_state=overall,
        findings=tuple(findings),
        assertion_count=len(value.assertions),
        connected_count=counts["connected"],
        disconnected_count=counts["disconnected"],
        ambiguous_count=counts["ambiguous"],
        unsupported_count=counts["unsupported"],
        conflicted_count=counts["conflicted"],
        indeterminate_count=counts["indeterminate"],
        deterministic=True,
        exact_connection_authority_preserved=True,
        candidate_structure_mutated=False,
        cooccurrence_only_connection_used=False,
        same_expression_only_connection_used=False,
        same_manifest_only_connection_used=False,
        implicit_transitive_connection_used=False,
        source_gap_bridged=False,
        ancestry_gap_bridged=False,
        scope_rewritten=False,
        attachment_reassigned=False,
        operator_trail_rewritten=False,
        predicate_frame_rewired=False,
        candidate_lineage_merged=False,
        similarity_fallback_used=False,
        hidden_model_judgment_used=False,
        clarification_required_created=False,
        rejection_created=False,
        refusal_relevant_created=False,
        blocked_progression_created=False,
        composed_gate_outcome_created=False,
        candidate_disposition_created=False,
        selected_meaning_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        vector_used=False,
        rag_used=False,
        semantic_similarity_used=False,
        canonical_digest="0" * 64,
    )
    return assert_valid_result(with_expected_result_identity(result))
