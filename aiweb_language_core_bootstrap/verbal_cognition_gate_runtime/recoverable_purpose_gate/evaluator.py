"""Deterministic exact-authority Slice 40F intended-purport evaluator."""
from __future__ import annotations

from .identity import with_expected_finding_id, with_expected_result_identity
from .schema import (
    RecoverablePurposeAssertion,
    RecoverablePurposeAuthorityState,
    RecoverablePurposeEvaluationInput,
    RecoverablePurposeFinding,
    RecoverablePurposeFindingKind,
    RecoverablePurposeGateResult,
    RecoverablePurposeJudgment,
    RecoverablePurposeOverallState,
)
from .validation import assert_valid_evaluation_input, assert_valid_result


def _finding(
    value: RecoverablePurposeEvaluationInput,
    assertion: RecoverablePurposeAssertion | None,
    observation,
    kind: RecoverablePurposeFindingKind,
) -> RecoverablePurposeFinding:
    return with_expected_finding_id(
        RecoverablePurposeFinding(
            finding_id="recoverable_purpose_finding:placeholder",
            evaluation_input_ref=value.evaluation_input_id,
            assertion_ref=(assertion.assertion_id if assertion else None),
            finding_kind=kind,
            distinction_kind=(assertion.distinction_kind if assertion else None),
            represented_act=(assertion.represented_act if assertion else None),
            authority_state=(
                observation.authority_state
                if observation
                else RecoverablePurposeAuthorityState.ADMITTED
            ),
            purpose_judgment=(
                observation.purpose_judgment
                if observation
                else RecoverablePurposeJudgment.RECOVERABLE
            ),
            supporting_refs=(
                observation.supporting_refs if observation else ()
            ),
            missing_authority_refs=(
                observation.missing_authority_refs if observation else ()
            ),
            conflicting_refs=(
                observation.conflicting_refs if observation else ()
            ),
            trace_refs=(
                observation.trace_refs if observation else value.trace_refs
            ),
            provenance_refs=(
                observation.provenance_refs
                if observation
                else value.provenance_refs
            ),
            reason_refs=(
                (f"recoverable_purpose:{kind.value}",)
                + (
                    assertion.purpose_support_refs
                    if assertion
                    else (
                        "slice40f:all_purpose_assertions_recovered",
                    )
                )
            ),
        )
    )


def evaluate_recoverable_purpose(
    value: RecoverablePurposeEvaluationInput,
) -> RecoverablePurposeGateResult:
    """Recover explicit communicative purpose without guessing hidden intent."""

    assert_valid_evaluation_input(value)
    observation_by_assertion = {
        item.assertion_ref: item for item in value.observations
    }
    findings: list[RecoverablePurposeFinding] = []
    counts = {
        "recoverable": 0,
        "unrecoverable": 0,
        "ambiguous": 0,
        "unsupported": 0,
        "conflicted": 0,
        "indeterminate": 0,
    }

    for assertion in value.assertions:
        observation = observation_by_assertion[assertion.assertion_id]
        if (
            observation.authority_state
            is RecoverablePurposeAuthorityState.ADMITTED
        ):
            if (
                observation.purpose_judgment
                is RecoverablePurposeJudgment.RECOVERABLE
            ):
                counts["recoverable"] += 1
                kind = RecoverablePurposeFindingKind.RECOVERED_PURPOSE
            else:
                counts["unrecoverable"] += 1
                kind = RecoverablePurposeFindingKind.UNRECOVERABLE_PURPOSE
        elif (
            observation.authority_state
            is RecoverablePurposeAuthorityState.AMBIGUOUS
        ):
            counts["ambiguous"] += 1
            kind = RecoverablePurposeFindingKind.AMBIGUOUS_PURPOSE
        elif (
            observation.authority_state
            is RecoverablePurposeAuthorityState.UNSUPPORTED
        ):
            counts["unsupported"] += 1
            kind = RecoverablePurposeFindingKind.UNSUPPORTED_PURPOSE
        elif (
            observation.authority_state
            is RecoverablePurposeAuthorityState.CONFLICTED
        ):
            counts["conflicted"] += 1
            kind = RecoverablePurposeFindingKind.CONFLICTED_PURPOSE
        else:
            counts["indeterminate"] += 1
            kind = (
                RecoverablePurposeFindingKind
                .INDETERMINATE_AUTHORITY_ABSENT
            )
        findings.append(_finding(value, assertion, observation, kind))

    if counts["conflicted"]:
        overall = RecoverablePurposeOverallState.CONFLICTED
    elif counts["unsupported"]:
        overall = RecoverablePurposeOverallState.UNSUPPORTED
    elif counts["ambiguous"]:
        overall = RecoverablePurposeOverallState.AMBIGUOUS
    elif counts["indeterminate"]:
        overall = RecoverablePurposeOverallState.INDETERMINATE
    elif counts["unrecoverable"]:
        overall = RecoverablePurposeOverallState.UNRECOVERABLE
    else:
        overall = RecoverablePurposeOverallState.RECOVERABLE
        findings.append(
            _finding(
                value,
                None,
                None,
                RecoverablePurposeFindingKind
                .ALL_PURPOSE_ASSERTIONS_RECOVERED,
            )
        )

    review = value.governance_bundle.review_record
    result = RecoverablePurposeGateResult(
        result_id="recoverable_purpose_result:placeholder",
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
        recoverable_count=counts["recoverable"],
        unrecoverable_count=counts["unrecoverable"],
        ambiguous_count=counts["ambiguous"],
        unsupported_count=counts["unsupported"],
        conflicted_count=counts["conflicted"],
        indeterminate_count=counts["indeterminate"],
        deterministic=True,
        exact_purpose_authority_preserved=True,
        candidate_structure_mutated=False,
        hidden_intent_inference_used=False,
        capability_existence_inference_used=False,
        prior_conversation_habit_used=False,
        assistant_intuition_used=False,
        psychological_inference_used=False,
        emotional_interpretation_used=False,
        raw_text_only_inference_used=False,
        purpose_conflation_used=False,
        automatic_purpose_collapse_used=False,
        unauthorized_context_used=False,
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
        capability_availability_created=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        memory_written=False,
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
