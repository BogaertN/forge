"""Deterministic Slice 40C expectancy evaluator."""

from __future__ import annotations

from .identity import with_expected_finding_id, with_expected_result_identity
from .schema import (
    ExpectancyAuthorityState,
    ExpectancyEvaluationInput,
    ExpectancyFinding,
    ExpectancyFindingKind,
    ExpectancyGateResult,
    ExpectancyOverallState,
    ExpectancyRequirementKind,
)
from .validation import assert_valid_evaluation_input, assert_valid_result


_MISSING_FINDING = {
    ExpectancyRequirementKind.REQUIRED_ROLE: ExpectancyFindingKind.REQUIRED_ROLE_MISSING,
    ExpectancyRequirementKind.REQUIRED_RELATION: ExpectancyFindingKind.REQUIRED_RELATION_MISSING,
    ExpectancyRequirementKind.REQUIRED_COMPLEMENT: ExpectancyFindingKind.REQUIRED_COMPLEMENT_MISSING,
    ExpectancyRequirementKind.REQUIRED_PURPOSE_INFORMATION: ExpectancyFindingKind.REQUIRED_PURPOSE_INFORMATION_MISSING,
}


def _finding(
    value: ExpectancyEvaluationInput,
    *,
    requirement_ref: str | None,
    kind: ExpectancyFindingKind,
    authority_state: ExpectancyAuthorityState,
    required_count: int,
    observed_count: int,
    record_refs: tuple[str, ...] = (),
    relation_refs: tuple[str, ...] = (),
    trace_refs: tuple[str, ...] = (),
    provenance_refs: tuple[str, ...] = (),
    reason_refs: tuple[str, ...] = (),
) -> ExpectancyFinding:
    return with_expected_finding_id(
        ExpectancyFinding(
            finding_id="expectancy_finding:placeholder",
            evaluation_input_ref=value.evaluation_input_id,
            requirement_ref=requirement_ref,
            finding_kind=kind,
            authority_state=authority_state,
            required_count=required_count,
            observed_count=observed_count,
            supporting_record_refs=record_refs,
            supporting_relation_refs=relation_refs,
            trace_refs=trace_refs,
            provenance_refs=provenance_refs,
            reason_refs=reason_refs,
        )
    )


def evaluate_expectancy(value: ExpectancyEvaluationInput) -> ExpectancyGateResult:
    """Evaluate exact admitted requirements without repairing the candidate."""

    assert_valid_evaluation_input(value)
    observations = {item.requirement_ref: item for item in value.observations}
    findings: list[ExpectancyFinding] = []
    satisfied_required = 0
    missing_required = 0
    optional_omitted = 0
    indeterminate = 0

    for requirement in value.requirements:
        observation = observations[requirement.requirement_id]
        if observation.authority_state is not ExpectancyAuthorityState.ADMITTED:
            indeterminate += 1
            findings.append(
                _finding(
                    value,
                    requirement_ref=requirement.requirement_id,
                    kind=ExpectancyFindingKind.INDETERMINATE_REQUIRED_AUTHORITY_ABSENT,
                    authority_state=observation.authority_state,
                    required_count=requirement.minimum_count,
                    observed_count=0,
                    trace_refs=observation.trace_refs,
                    provenance_refs=observation.provenance_refs,
                    reason_refs=(
                        f"expectancy_authority:{observation.authority_state.value}",
                        *requirement.authority_refs,
                    ),
                )
            )
            continue

        count = observation.observed_count
        if count >= requirement.minimum_count:
            if requirement.required:
                satisfied_required += 1
            continue

        if requirement.requirement_kind is ExpectancyRequirementKind.OPTIONAL_DETAIL:
            optional_omitted += 1
            kind = ExpectancyFindingKind.OPTIONAL_DETAIL_OMITTED
        else:
            missing_required += 1
            kind = _MISSING_FINDING[requirement.requirement_kind]
        findings.append(
            _finding(
                value,
                requirement_ref=requirement.requirement_id,
                kind=kind,
                authority_state=observation.authority_state,
                required_count=requirement.minimum_count,
                observed_count=count,
                record_refs=observation.observed_record_refs,
                relation_refs=observation.observed_relation_refs,
                trace_refs=observation.trace_refs,
                provenance_refs=observation.provenance_refs,
                reason_refs=(
                    f"expectancy_requirement:{requirement.requirement_kind.value}",
                    *requirement.requirement_source_refs,
                ),
            )
        )

    if indeterminate:
        overall = ExpectancyOverallState.INDETERMINATE
    elif missing_required:
        overall = ExpectancyOverallState.INCOMPLETE
    else:
        overall = ExpectancyOverallState.STRUCTURALLY_COMPLETE
        findings.append(
            _finding(
                value,
                requirement_ref=None,
                kind=ExpectancyFindingKind.STRUCTURALLY_COMPLETE,
                authority_state=ExpectancyAuthorityState.ADMITTED,
                required_count=sum(item.required for item in value.requirements),
                observed_count=satisfied_required,
                trace_refs=value.trace_refs,
                provenance_refs=value.provenance_refs,
                reason_refs=("slice40c:all_required_expectancy_structure_present",),
            )
        )

    review = value.governance_bundle.review_record
    result = ExpectancyGateResult(
        result_id="expectancy_result:placeholder",
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
        requirement_count=len(value.requirements),
        required_requirement_count=sum(item.required for item in value.requirements),
        satisfied_required_count=satisfied_required,
        missing_required_count=missing_required,
        optional_omitted_count=optional_omitted,
        indeterminate_count=indeterminate,
        deterministic=True,
        exact_requirement_authority_preserved=True,
        candidate_structure_mutated=False,
        missing_role_filled=False,
        referent_invented=False,
        unstated_participant_inferred=False,
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


__all__ = ("evaluate_expectancy",)
