"""Deterministic candidate-specific Slice 41C eligibility evaluator."""
from __future__ import annotations

from dataclasses import replace

from ...verbal_cognition_gate_runtime.gate_composition.schema import (
    GateCompositionDispositionKind,
    GateCompositionStatus,
)
from .identity import with_expected_finding_id, with_expected_result_identity
from .schema import (
    SelectionEligibilityEvaluationInput,
    SelectionEligibilityFinding,
    SelectionEligibilityFindingKind,
    SelectionEligibilityOutcome,
    SelectionEligibilityResult,
)


def _unique(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _disposition_refs(
    value: SelectionEligibilityEvaluationInput,
    kind: GateCompositionDispositionKind,
) -> tuple[str, ...]:
    return tuple(
        disposition.disposition_id
        for disposition in value.candidate_dispositions
        if disposition.disposition_kind is kind
    )


def _disposition_reason_refs(
    value: SelectionEligibilityEvaluationInput,
    kind: GateCompositionDispositionKind,
) -> tuple[str, ...]:
    return _unique(
        tuple(
            reason
            for disposition in value.candidate_dispositions
            if disposition.disposition_kind is kind
            for reason in disposition.reason_refs
        )
    )


def determine_outcome(
    value: SelectionEligibilityEvaluationInput,
) -> SelectionEligibilityOutcome:
    """Return the exact fail-closed outcome using explicit records only."""
    result = value.gate_composition_result
    unresolved = value.unresolved_state_custody
    alternatives = value.alternative_candidate_custody

    if (
        result.composition_status is GateCompositionStatus.CONFLICTED_AUTHORITY
        or result.conflicted_authority_count
        or unresolved.conflicted_refs
    ):
        return SelectionEligibilityOutcome.CONFLICTED

    if (
        result.composition_status is GateCompositionStatus.UNSUPPORTED_AUTHORITY
        or result.unsupported_authority_count
        or result.unsupported_disposition_count
        or unresolved.unsupported_refs
        or _disposition_refs(value, GateCompositionDispositionKind.UNSUPPORTED)
    ):
        return SelectionEligibilityOutcome.UNSUPPORTED

    if (
        result.clarification_relevant_count
        or unresolved.clarification_dependency_refs
        or _disposition_refs(
            value,
            GateCompositionDispositionKind.CLARIFICATION_RELEVANT,
        )
    ):
        return SelectionEligibilityOutcome.CLARIFICATION_DEPENDENT

    if (
        result.composition_status is GateCompositionStatus.AMBIGUOUS_AUTHORITY
        or result.ambiguous_authority_count
        or result.material_ambiguity_count
        or unresolved.unresolved_candidate_refs
        or alternatives.material_ambiguity_refs
        or _disposition_refs(
            value,
            GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED,
        )
    ):
        return SelectionEligibilityOutcome.MATERIALLY_UNRESOLVED

    if (
        result.held_count
        or result.blocked_progression_count
        or result.refusal_relevant_count
        or unresolved.held_refs
        or unresolved.blocked_progression_refs
        or unresolved.refusal_relevant_refs
        or unresolved.missing_authority_refs
        or _disposition_refs(value, GateCompositionDispositionKind.HELD)
        or _disposition_refs(
            value,
            GateCompositionDispositionKind.BLOCKED_PROGRESSION,
        )
        or _disposition_refs(
            value,
            GateCompositionDispositionKind.REFUSAL_RELEVANT,
        )
    ):
        return SelectionEligibilityOutcome.HELD_PENDING_AUTHORITY

    if value.explicit_not_eligible_refs:
        return SelectionEligibilityOutcome.NOT_ELIGIBLE

    if (
        result.composition_status is GateCompositionStatus.INDETERMINATE_AUTHORITY
        or result.indeterminate_authority_count
    ):
        return SelectionEligibilityOutcome.INDETERMINATE

    positive = _disposition_refs(
        value,
        GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
    )
    if positive and value.explicit_positive_support_refs:
        return SelectionEligibilityOutcome.ELIGIBLE_FOR_SELECTED_MEANING_CONSTRUCTION

    return SelectionEligibilityOutcome.INDETERMINATE


def _finding(
    value: SelectionEligibilityEvaluationInput,
    kind: SelectionEligibilityFindingKind,
    basis_refs: tuple[str, ...],
    reason_refs: tuple[str, ...],
) -> SelectionEligibilityFinding:
    candidate = value.selection_candidate_custody
    record = SelectionEligibilityFinding(
        finding_id="pending",
        evaluation_input_ref=value.evaluation_input_id,
        candidate_meaning_ref=candidate.candidate_meaning_id,
        finding_kind=kind,
        basis_refs=_unique(basis_refs),
        reason_refs=_unique(reason_refs),
        trace_refs=value.trace_refs,
        provenance_refs=value.provenance_refs,
    )
    return with_expected_finding_id(record)


def evaluate_selection_eligibility(
    value: SelectionEligibilityEvaluationInput,
) -> SelectionEligibilityResult:
    """Evaluate lawful progression eligibility without selecting anything."""
    from .validation import assert_valid_evaluation_input, assert_valid_result

    assert_valid_evaluation_input(value)
    candidate = value.selection_candidate_custody
    gate = value.gate_custody_reference
    unresolved = value.unresolved_state_custody
    alternatives = value.alternative_candidate_custody
    limitations = value.inherited_limitation_custody
    composition = value.gate_composition_result
    outcome = determine_outcome(value)

    positive_refs = _disposition_refs(
        value,
        GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
    )
    material_refs = _disposition_refs(
        value,
        GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED,
    )
    clarification_refs = _disposition_refs(
        value,
        GateCompositionDispositionKind.CLARIFICATION_RELEVANT,
    )
    unsupported_disposition_refs = _disposition_refs(
        value,
        GateCompositionDispositionKind.UNSUPPORTED,
    )
    refusal_refs = _disposition_refs(
        value,
        GateCompositionDispositionKind.REFUSAL_RELEVANT,
    )
    held_disposition_refs = _disposition_refs(
        value,
        GateCompositionDispositionKind.HELD,
    )
    blocked_disposition_refs = _disposition_refs(
        value,
        GateCompositionDispositionKind.BLOCKED_PROGRESSION,
    )

    findings = [
        _finding(
            value,
            SelectionEligibilityFindingKind.EXACT_CANDIDATE_CUSTODY_CONFIRMED,
            (candidate.selection_candidate_custody_id,),
            ("exact_candidate_specific_custody",),
        ),
        _finding(
            value,
            SelectionEligibilityFindingKind.EXACT_GATE_CUSTODY_CONFIRMED,
            (gate.gate_custody_reference_id, value.msm_gate_custody_companion.companion_id),
            ("exact_slice40h_gate_custody",),
        ),
        _finding(
            value,
            SelectionEligibilityFindingKind.ALL_FOUR_GATE_RESULTS_CONFIRMED,
            (
                gate.expectancy_result_ref,
                gate.congruity_result_ref,
                gate.connectedness_result_ref,
                gate.recoverable_purpose_result_ref,
            ),
            ("all_four_gate_family_results_preserved",),
        ),
        _finding(
            value,
            SelectionEligibilityFindingKind.EXACT_COMPOSITION_CONFIRMED,
            (composition.result_id,),
            ("exact_slice40g_composition_result",),
        ),
    ]

    if positive_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.EXPLICIT_CANDIDATE_SUPPORT_CONFIRMED,
                positive_refs + value.explicit_positive_support_refs,
                _disposition_reason_refs(
                    value,
                    GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
                ),
            )
        )
    if unresolved.missing_authority_refs or held_disposition_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.MISSING_AUTHORITY_PRESERVED,
                unresolved.missing_authority_refs + held_disposition_refs,
                ("authority_remains_missing_or_held",),
            )
        )
    if alternatives.material_ambiguity_refs or material_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.MATERIAL_AMBIGUITY_PRESERVED,
                alternatives.material_ambiguity_refs + material_refs,
                ("material_ambiguity_blocks_eligibility",),
            )
        )
    if unresolved.clarification_dependency_refs or clarification_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.CLARIFICATION_DEPENDENCY_PRESERVED,
                unresolved.clarification_dependency_refs + clarification_refs,
                ("clarification_dependency_blocks_eligibility",),
            )
        )
    if unresolved.unsupported_refs or unsupported_disposition_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.UNSUPPORTED_STATE_PRESERVED,
                unresolved.unsupported_refs + unsupported_disposition_refs,
                ("unsupported_state_blocks_eligibility",),
            )
        )
    if unresolved.conflicted_refs or composition.conflicted_authority_count:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.CONFLICT_PRESERVED,
                unresolved.conflicted_refs,
                ("conflict_blocks_eligibility",),
            )
        )
    if unresolved.refusal_relevant_refs or refusal_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.REFUSAL_RELEVANCE_PRESERVED,
                unresolved.refusal_relevant_refs + refusal_refs,
                ("refusal_relevance_preserved_not_issued",),
            )
        )
    if unresolved.blocked_progression_refs or blocked_disposition_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.BLOCKED_PROGRESSION_PRESERVED,
                unresolved.blocked_progression_refs + blocked_disposition_refs,
                ("blocked_progression_preserved",),
            )
        )
    if alternatives.preserved_alternative_candidate_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.ALTERNATIVE_CUSTODY_PRESERVED,
                alternatives.preserved_alternative_candidate_refs,
                ("alternatives_preserved_without_ranking_or_discard",),
            )
        )
    if value.explicit_not_eligible_refs:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.EXPLICIT_NOT_ELIGIBLE_PRESERVED,
                value.explicit_not_eligible_refs,
                ("explicit_candidate_specific_not_eligible_authority",),
            )
        )
    if outcome is SelectionEligibilityOutcome.INDETERMINATE:
        findings.append(
            _finding(
                value,
                SelectionEligibilityFindingKind.INDETERMINATE_FAIL_CLOSED,
                tuple(),
                ("explicit_positive_support_absent_or_authority_indeterminate",),
            )
        )

    preserved_dispositions = tuple(
        disposition.disposition_id for disposition in value.candidate_dispositions
    )
    inherited_refs = _unique(
        limitations.source_limitation_refs
        + limitations.candidate_limitation_refs
        + limitations.gate_limitation_refs
        + limitations.effect_boundary_refs
        + limitations.domain_sensitive_refs
        + limitations.authority_sensitive_distinction_refs
        + limitations.evidence_boundary_refs
        + limitations.memory_boundary_refs
        + limitations.privacy_boundary_refs
        + limitations.delivery_boundary_refs
        + limitations.execution_boundary_refs
        + limitations.correction_ancestry_refs
        + limitations.supersession_ancestry_refs
    )
    reason_refs = _unique(
        tuple(reason for finding in findings for reason in finding.reason_refs)
    )

    record = SelectionEligibilityResult(
        result_id="pending",
        evaluation_input_ref=value.evaluation_input_id,
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        candidate_meaning_ref=candidate.candidate_meaning_id,
        candidate_lineage_ref=candidate.candidate_lineage_id,
        manifest_candidate_record_ref=candidate.manifest_candidate_record_ref,
        manifest_candidate_companion_ref=value.manifest_candidate_companion.companion_id,
        msm_gate_custody_companion_ref=value.msm_gate_custody_companion.companion_id,
        gate_composition_result_ref=composition.result_id,
        authority_profile_ref=value.authority_profile.profile_id,
        outcome=outcome,
        findings=tuple(findings),
        preserved_disposition_refs=preserved_dispositions,
        explicit_positive_support_refs=value.explicit_positive_support_refs,
        explicit_not_eligible_refs=value.explicit_not_eligible_refs,
        material_ambiguity_refs=_unique(alternatives.material_ambiguity_refs + material_refs),
        clarification_dependency_refs=_unique(
            unresolved.clarification_dependency_refs + clarification_refs
        ),
        unsupported_refs=_unique(unresolved.unsupported_refs + unsupported_disposition_refs),
        conflicted_refs=unresolved.conflicted_refs,
        missing_authority_refs=unresolved.missing_authority_refs,
        held_refs=_unique(unresolved.held_refs + held_disposition_refs),
        refusal_relevant_refs=_unique(unresolved.refusal_relevant_refs + refusal_refs),
        blocked_progression_refs=_unique(
            unresolved.blocked_progression_refs + blocked_disposition_refs
        ),
        preserved_alternative_candidate_refs=alternatives.preserved_alternative_candidate_refs,
        inherited_limitation_refs=inherited_refs,
        reason_refs=reason_refs,
        trace_refs=value.trace_refs,
        provenance_refs=value.provenance_refs,
        deterministic=True,
        candidate_specific=True,
        exact_msm_candidate_verified=True,
        exact_slice40h_companion_verified=True,
        all_four_gate_results_verified=True,
        exact_slice40g_composition_verified=True,
        approved_authority_profile_verified=True,
        explicit_candidate_support_verified=bool(positive_refs and value.explicit_positive_support_refs),
        alternatives_preserved=True,
        unresolved_states_preserved=True,
        refusal_relevance_preserved=True,
        blocked_progression_preserved=True,
        inherited_limitations_preserved=True,
        eligibility_evaluated=True,
        eligible_for_selected_meaning_construction=(
            outcome
            is SelectionEligibilityOutcome.ELIGIBLE_FOR_SELECTED_MEANING_CONSTRUCTION
        ),
        candidate_ranked=False,
        selection_performed=False,
        selected_meaning_created=False,
        msm_v1_modified=False,
        bootstrap_integration_enabled=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        memory_written=False,
        rendered=False,
        delivered=False,
        external_resource_loaded=False,
        language_model_used=False,
        hidden_classifier_used=False,
        confidence_scoring_used=False,
        probability_ranking_used=False,
        semantic_similarity_used=False,
        nearest_known_substitution_used=False,
        only_candidate_automatic_eligibility_used=False,
        first_candidate_automatic_eligibility_used=False,
        safest_candidate_automatic_eligibility_used=False,
        refusal_relevance_erased=False,
        blocked_progression_erased=False,
        unresolved_alternatives_erased=False,
        understood_meaning_converted_to_permission=False,
        canonical_digest="pending",
    )
    sealed = with_expected_result_identity(record)
    assert_valid_result(sealed, evaluation_input=value)
    return sealed


__all__ = (
    "determine_outcome",
    "evaluate_selection_eligibility",
)
