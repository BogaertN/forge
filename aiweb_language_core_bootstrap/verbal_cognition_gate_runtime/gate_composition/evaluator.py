"""Deterministic Slice 40G gate-composition evaluator."""
from __future__ import annotations

from collections import Counter

from .identity import (
    with_expected_disposition_id,
    with_expected_finding_id,
    with_expected_result_identity,
)
from .schema import (
    CandidateNonSelectionDisposition,
    GateCompositionAuthorityState,
    GateCompositionDispositionAssertion,
    GateCompositionDispositionKind,
    GateCompositionEvaluationInput,
    GateCompositionFinding,
    GateCompositionFindingKind,
    GateCompositionJudgment,
    GateCompositionResult,
    GateCompositionStatus,
)
from .validation import assert_valid_evaluation_input, assert_valid_result


def _basis_refs(assertion: GateCompositionDispositionAssertion) -> tuple[str, ...]:
    return (
        assertion.ambiguity_refs
        + assertion.clarification_refs
        + assertion.unsupported_refs
        + assertion.refusal_relevance_refs
        + assertion.hold_refs
        + assertion.blocked_progression_refs
        + assertion.later_selection_review_refs
    )


def _finding_kind(assertion: GateCompositionDispositionAssertion) -> GateCompositionFindingKind:
    if assertion.authority_state is GateCompositionAuthorityState.ADMITTED:
        if assertion.judgment is GateCompositionJudgment.APPLIES:
            return GateCompositionFindingKind.DISPOSITION_APPLIED
        return GateCompositionFindingKind.DISPOSITION_NOT_APPLIED
    if assertion.authority_state is GateCompositionAuthorityState.AMBIGUOUS:
        return GateCompositionFindingKind.AMBIGUOUS_AUTHORITY
    if assertion.authority_state is GateCompositionAuthorityState.UNSUPPORTED:
        return GateCompositionFindingKind.UNSUPPORTED_AUTHORITY
    if assertion.authority_state is GateCompositionAuthorityState.CONFLICTED:
        return GateCompositionFindingKind.CONFLICTED_AUTHORITY
    return GateCompositionFindingKind.INDETERMINATE_AUTHORITY_ABSENT


def _finding(
    value: GateCompositionEvaluationInput,
    assertion: GateCompositionDispositionAssertion | None,
    kind: GateCompositionFindingKind,
) -> GateCompositionFinding:
    if assertion is None:
        gate_result_refs = (
            value.expectancy_result.result_id,
            value.congruity_result.result_id,
            value.connectedness_result.result_id,
            value.recoverable_purpose_result.result_id,
        )
        return with_expected_finding_id(
            GateCompositionFinding(
                finding_id="gate_composition_finding:placeholder",
                evaluation_input_ref=value.evaluation_input_id,
                assertion_ref=None,
                finding_kind=kind,
                disposition_kind=None,
                authority_state=GateCompositionAuthorityState.ADMITTED,
                judgment=GateCompositionJudgment.APPLIES,
                gate_result_refs=gate_result_refs,
                supporting_refs=("slice40g:all_four_family_results_preserved",),
                missing_authority_refs=(),
                conflicting_refs=(),
                reason_refs=("document6:33.4:composition_by_preservation",),
                trace_refs=value.trace_refs,
                provenance_refs=value.provenance_refs,
            )
        )
    return with_expected_finding_id(
        GateCompositionFinding(
            finding_id="gate_composition_finding:placeholder",
            evaluation_input_ref=value.evaluation_input_id,
            assertion_ref=assertion.assertion_id,
            finding_kind=kind,
            disposition_kind=assertion.disposition_kind,
            authority_state=assertion.authority_state,
            judgment=assertion.judgment,
            gate_result_refs=assertion.gate_result_refs,
            supporting_refs=assertion.supporting_refs,
            missing_authority_refs=assertion.missing_authority_refs,
            conflicting_refs=assertion.conflicting_refs,
            reason_refs=_basis_refs(assertion),
            trace_refs=assertion.trace_refs,
            provenance_refs=assertion.provenance_refs,
        )
    )


def _disposition(
    value: GateCompositionEvaluationInput,
    assertion: GateCompositionDispositionAssertion,
) -> CandidateNonSelectionDisposition:
    return with_expected_disposition_id(
        CandidateNonSelectionDisposition(
            disposition_id="candidate_non_selection_disposition:placeholder",
            evaluation_input_ref=value.evaluation_input_id,
            assertion_ref=assertion.assertion_id,
            candidate_input_ref=value.candidate_input_ref,
            candidate_branch_ref=value.candidate_branch_ref,
            disposition_kind=assertion.disposition_kind,
            gate_result_refs=assertion.gate_result_refs,
            reason_refs=_basis_refs(assertion),
            later_authority_dependency_refs=(
                assertion.later_authority_dependency_refs
            ),
            effect_boundary_refs=assertion.effect_boundary_refs,
            domain_marker_refs=assertion.domain_marker_refs,
            no_action_boundary_refs=assertion.no_action_boundary_refs,
            trace_refs=assertion.trace_refs,
            provenance_refs=assertion.provenance_refs,
            non_selection_only=True,
        )
    )


def _status(value: GateCompositionEvaluationInput) -> GateCompositionStatus:
    states = {item.authority_state for item in value.disposition_assertions}
    if GateCompositionAuthorityState.CONFLICTED in states:
        return GateCompositionStatus.CONFLICTED_AUTHORITY
    if GateCompositionAuthorityState.UNSUPPORTED in states:
        return GateCompositionStatus.UNSUPPORTED_AUTHORITY
    if GateCompositionAuthorityState.AMBIGUOUS in states:
        return GateCompositionStatus.AMBIGUOUS_AUTHORITY
    if GateCompositionAuthorityState.ABSENT in states:
        return GateCompositionStatus.INDETERMINATE_AUTHORITY
    return GateCompositionStatus.COMPOSED


def evaluate_gate_composition(
    value: GateCompositionEvaluationInput,
) -> GateCompositionResult:
    """Compose all four exact gate-family results without selecting meaning."""
    assert_valid_evaluation_input(value)
    findings = []
    dispositions = []
    authority_counts: Counter[GateCompositionAuthorityState] = Counter()
    judgment_counts: Counter[GateCompositionJudgment] = Counter()
    disposition_counts: Counter[GateCompositionDispositionKind] = Counter()

    for assertion in value.disposition_assertions:
        authority_counts[assertion.authority_state] += 1
        judgment_counts[assertion.judgment] += 1
        kind = _finding_kind(assertion)
        findings.append(_finding(value, assertion, kind))
        if (
            assertion.authority_state is GateCompositionAuthorityState.ADMITTED
            and assertion.judgment is GateCompositionJudgment.APPLIES
        ):
            dispositions.append(_disposition(value, assertion))
            disposition_counts[assertion.disposition_kind] += 1

    findings.append(
        _finding(
            value,
            None,
            GateCompositionFindingKind.ALL_FAMILY_RESULTS_PRESERVED,
        )
    )

    result = GateCompositionResult(
        result_id="gate_composition_result:placeholder",
        evaluation_input_ref=value.evaluation_input_id,
        candidate_input_ref=value.candidate_input_ref,
        candidate_branch_ref=value.candidate_branch_ref,
        expectancy_result_id=value.expectancy_result.result_id,
        expectancy_result_digest=value.expectancy_result.canonical_digest,
        expectancy_candidate_input_ref=value.expectancy_result.candidate_input_ref,
        congruity_result_id=value.congruity_result.result_id,
        congruity_result_digest=value.congruity_result.canonical_digest,
        congruity_candidate_input_ref=value.congruity_result.candidate_input_ref,
        connectedness_result_id=value.connectedness_result.result_id,
        connectedness_result_digest=value.connectedness_result.canonical_digest,
        connectedness_candidate_input_ref=value.connectedness_result.candidate_input_ref,
        recoverable_purpose_result_id=value.recoverable_purpose_result.result_id,
        recoverable_purpose_result_digest=(
            value.recoverable_purpose_result.canonical_digest
        ),
        recoverable_purpose_candidate_input_ref=(
            value.recoverable_purpose_result.candidate_input_ref
        ),
        composition_status=_status(value),
        dispositions=tuple(dispositions),
        findings=tuple(findings),
        assertion_count=len(value.disposition_assertions),
        applied_disposition_count=judgment_counts[GateCompositionJudgment.APPLIES],
        not_applied_count=judgment_counts[GateCompositionJudgment.DOES_NOT_APPLY],
        ambiguous_authority_count=authority_counts[GateCompositionAuthorityState.AMBIGUOUS],
        unsupported_authority_count=authority_counts[GateCompositionAuthorityState.UNSUPPORTED],
        conflicted_authority_count=authority_counts[GateCompositionAuthorityState.CONFLICTED],
        indeterminate_authority_count=authority_counts[GateCompositionAuthorityState.ABSENT],
        material_ambiguity_count=disposition_counts[GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED],
        clarification_relevant_count=disposition_counts[GateCompositionDispositionKind.CLARIFICATION_RELEVANT],
        unsupported_disposition_count=disposition_counts[GateCompositionDispositionKind.UNSUPPORTED],
        refusal_relevant_count=disposition_counts[GateCompositionDispositionKind.REFUSAL_RELEVANT],
        held_count=disposition_counts[GateCompositionDispositionKind.HELD],
        blocked_progression_count=disposition_counts[GateCompositionDispositionKind.BLOCKED_PROGRESSION],
        later_selection_review_count=disposition_counts[GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW],
        deterministic=True,
        family_results_preserved=True,
        family_result_count=4,
        candidate_branches_preserved=True,
        effect_boundaries_preserved=True,
        domain_markers_preserved=True,
        no_action_boundaries_preserved=True,
        candidate_ancestry_preserved=True,
        version_discipline_preserved=True,
        material_ambiguity_preserved=bool(disposition_counts[GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED]),
        clarification_relevant_created=bool(disposition_counts[GateCompositionDispositionKind.CLARIFICATION_RELEVANT]),
        unsupported_disposition_created=bool(disposition_counts[GateCompositionDispositionKind.UNSUPPORTED]),
        refusal_relevant_disposition_created=bool(disposition_counts[GateCompositionDispositionKind.REFUSAL_RELEVANT]),
        held_disposition_created=bool(disposition_counts[GateCompositionDispositionKind.HELD]),
        blocked_progression_created=bool(disposition_counts[GateCompositionDispositionKind.BLOCKED_PROGRESSION]),
        positive_selection_review_disposition_created=bool(disposition_counts[GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW]),
        candidate_accepted=False,
        candidate_rejected=False,
        candidate_clarified=False,
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
        raw_text_used_as_selected_meaning=False,
        gate_substitution_used=False,
        gate_outcome_erased=False,
        generic_flattening_used=False,
        global_pass_generalized=False,
        global_failure_generalized=False,
        candidate_branch_erased=False,
        effect_boundary_rewritten=False,
        domain_marker_erased=False,
        no_action_boundary_converted=False,
        automatic_ambiguity_used=False,
        automatic_clarification_used=False,
        automatic_refusal_used=False,
        safest_candidate_selected=False,
        candidate_structure_mutated=False,
        canonical_digest="",
    )
    result = with_expected_result_identity(result)
    assert_valid_result(result)
    return result
