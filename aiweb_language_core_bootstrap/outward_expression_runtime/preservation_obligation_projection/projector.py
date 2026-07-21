"""Deterministic Slice 42D preservation-obligation projection."""

from __future__ import annotations

from typing import Any, Iterable

from .authority import (
    SLICE42D_BOUNDED_CERTAINTY_REF,
    SLICE42D_DELIVERY_NOT_AUTHORIZED_REF,
    SLICE42D_EVIDENCE_NOT_VALIDATED_REF,
    SLICE42D_EXTERNAL_RESOURCE_NOT_LOADED_REF,
    SLICE42D_GOVERNING_AUTHORITY_REFS,
    SLICE42D_MEMORY_NO_WRITE_AUTHORITY_REF,
    SLICE42D_PERMANENT_BOUNDARIES,
    SLICE42D_PRIVACY_IDENTITY_BOUNDARY_REF,
    SLICE42D_PROHIBITED_AUTHORITY,
)
from .identity import (
    with_expected_id,
    with_expected_package_identity,
    with_expected_result_identity,
)
from .schema import (
    ExpressionObligationPackage,
    PreservationObligationProjectionFinding,
    PreservationObligationProjectionFindingKind,
    PreservationObligationProjectionInput,
    PreservationObligationProjectionResult,
)


def _unique(*groups: Iterable[str]) -> tuple[str, ...]:
    ordered: dict[str, None] = {}
    for group in groups:
        for value in group:
            ordered.setdefault(value, None)
    return tuple(ordered)


def derive_obligation_values(
    value: PreservationObligationProjectionInput,
) -> dict[str, Any]:
    """Derive every projected category from exact predecessor records.

    This function performs no validation and no side effects.  Its caller must
    validate the complete Slice 42C and Slice 42D input before using the
    returned values as authority.
    """

    eligibility_input = value.expression_eligibility_evaluation_input
    eligibility_result = value.expression_eligibility_result
    projection_authority = value.projection_authority_record
    source = eligibility_input.selected_meaning_source_custody
    outward_authority = eligibility_input.outward_expression_authority_record
    closeout = eligibility_input.selected_meaning_closeout_result

    integration_input = closeout.integration_input
    if integration_input is None:
        raise ValueError("completed Slice 41F integration input is required")

    construction_input = integration_input.selected_meaning_construction_input
    selection_eligibility = construction_input.eligibility_result
    selected_package = integration_input.selected_meaning_package
    selected_record = selected_package.selected_meaning_record

    selected_meaning_refs = _unique(
        (
            source.selected_governed_meaning_ref,
            source.selected_candidate_ref,
            source.selection_eligibility_result_ref,
            source.selection_decision_ref,
            source.selection_trace_ref,
            source.selection_receipt_ref,
            source.content_proof_ref,
        )
    )

    inherited_limitation_refs = _unique(
        source.inherited_limitation_refs,
        selection_eligibility.inherited_limitation_refs,
        selected_record.inherited_limitations,
    )

    ambiguity_refs = _unique(
        source.ambiguity_ancestry_refs,
        selection_eligibility.material_ambiguity_refs,
    )

    unsupported_state_refs = _unique(
        selection_eligibility.unsupported_refs,
    )

    refusal_relevant_boundary_refs = _unique(
        source.refusal_relevant_refs,
        selection_eligibility.refusal_relevant_refs,
    )

    unresolved_condition_refs = _unique(
        source.unresolved_alternative_refs,
        source.ambiguity_ancestry_refs,
        source.clarification_ancestry_refs,
        selection_eligibility.material_ambiguity_refs,
        selection_eligibility.clarification_dependency_refs,
        selection_eligibility.unsupported_refs,
        selection_eligibility.conflicted_refs,
        selection_eligibility.missing_authority_refs,
        selection_eligibility.held_refs,
    )

    required_caveat_refs = _unique(
        inherited_limitation_refs,
        source.authority_sensitive_distinction_refs,
        ambiguity_refs,
        unsupported_state_refs,
        refusal_relevant_boundary_refs,
        unresolved_condition_refs,
    )

    privacy_identity_boundary_refs: tuple[str, ...]
    if "privacy_and_identity_boundary" in source.preservation_class_refs:
        privacy_identity_boundary_refs = (
            SLICE42D_PRIVACY_IDENTITY_BOUNDARY_REF,
        )
    else:
        privacy_identity_boundary_refs = ()

    predecessor_receipt_refs = _unique(
        (
            source.slice41e_integration_receipt_ref,
            source.selection_receipt_ref,
            outward_authority.authority_receipt_ref,
            projection_authority.projection_authority_receipt_ref,
        )
    )

    return {
        "selected_meaning_refs": selected_meaning_refs,
        "active_scope_refs": outward_authority.authority_scope_refs,
        "certainty_level_refs": (SLICE42D_BOUNDED_CERTAINTY_REF,),
        "evidence_status_refs": (SLICE42D_EVIDENCE_NOT_VALIDATED_REF,),
        "inherited_limitation_refs": inherited_limitation_refs,
        "required_caveat_refs": required_caveat_refs,
        "refusal_relevant_boundary_refs": (
            refusal_relevant_boundary_refs
        ),
        "unresolved_condition_refs": unresolved_condition_refs,
        "ambiguity_refs": ambiguity_refs,
        "unsupported_state_refs": unsupported_state_refs,
        "memory_authority_refs": (
            SLICE42D_MEMORY_NO_WRITE_AUTHORITY_REF,
        ),
        "external_resource_status_refs": (
            SLICE42D_EXTERNAL_RESOURCE_NOT_LOADED_REF,
        ),
        "delivery_authority_refs": (
            SLICE42D_DELIVERY_NOT_AUTHORIZED_REF,
        ),
        "privacy_identity_boundary_refs": (
            privacy_identity_boundary_refs
        ),
        "preservation_class_refs": source.preservation_class_refs,
        "predecessor_receipt_refs": predecessor_receipt_refs,
        "trace_refs": _unique(
            value.trace_refs,
            (source.selection_trace_ref,),
        ),
        "provenance_refs": _unique(
            value.provenance_refs,
            (
                eligibility_result.result_id,
                source.source_custody_id,
                projection_authority.projection_authority_record_id,
            ),
        ),
        "version_refs": _unique(
            value.version_refs,
            projection_authority.version_refs,
        ),
    }


def _finding(
    value: PreservationObligationProjectionInput,
    package: ExpressionObligationPackage,
    kind: PreservationObligationProjectionFindingKind,
    basis_refs: tuple[str, ...],
    reason_refs: tuple[str, ...],
) -> PreservationObligationProjectionFinding:
    basis = basis_refs or (package.expression_eligibility_result_ref,)
    return with_expected_id(
        PreservationObligationProjectionFinding(
            finding_id="pending",
            projection_input_ref=value.projection_input_id,
            obligation_package_ref=package.obligation_package_id,
            finding_kind=kind,
            basis_refs=_unique(basis),
            reason_refs=_unique(reason_refs),
            trace_refs=package.trace_refs,
            provenance_refs=package.provenance_refs,
        )
    )


def project_preservation_obligations(
    value: PreservationObligationProjectionInput,
) -> PreservationObligationProjectionResult:
    """Create the exact immutable Slice 42D obligation package."""

    from .validation import (
        assert_valid_projection_input,
        assert_valid_projection_result,
    )

    assert_valid_projection_input(value)

    eligibility_input = value.expression_eligibility_evaluation_input
    eligibility_result = value.expression_eligibility_result
    projection_authority = value.projection_authority_record
    source = eligibility_input.selected_meaning_source_custody
    outward_requirement = (
        eligibility_input.outward_expression_authority_requirement
    )
    outward_authority = eligibility_input.outward_expression_authority_record
    derived = derive_obligation_values(value)

    package = ExpressionObligationPackage(
        obligation_package_id="pending",
        obligation_package_digest="0" * 64,
        projection_input_ref=value.projection_input_id,
        expression_eligibility_result_ref=eligibility_result.result_id,
        projection_authority_record_ref=(
            projection_authority.projection_authority_record_id
        ),
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=(
            outward_requirement.authority_requirement_id
        ),
        outward_expression_authority_record_ref=(
            outward_authority.authority_record_id
        ),
        source_eligibility_outcome=eligibility_result.outcome,
        selected_meaning_refs=derived["selected_meaning_refs"],
        active_scope_refs=derived["active_scope_refs"],
        certainty_level_refs=derived["certainty_level_refs"],
        evidence_status_refs=derived["evidence_status_refs"],
        inherited_limitation_refs=derived["inherited_limitation_refs"],
        required_caveat_refs=derived["required_caveat_refs"],
        refusal_relevant_boundary_refs=derived[
            "refusal_relevant_boundary_refs"
        ],
        unresolved_condition_refs=derived["unresolved_condition_refs"],
        ambiguity_refs=derived["ambiguity_refs"],
        unsupported_state_refs=derived["unsupported_state_refs"],
        memory_authority_refs=derived["memory_authority_refs"],
        external_resource_status_refs=derived[
            "external_resource_status_refs"
        ],
        delivery_authority_refs=derived["delivery_authority_refs"],
        privacy_identity_boundary_refs=derived[
            "privacy_identity_boundary_refs"
        ],
        preservation_class_refs=derived["preservation_class_refs"],
        predecessor_receipt_refs=derived["predecessor_receipt_refs"],
        trace_refs=derived["trace_refs"],
        provenance_refs=derived["provenance_refs"],
        version_refs=derived["version_refs"],
        exact_slice42c_state_verified=True,
        exact_projection_authority_verified=True,
        obligation_categories_separately_projected=True,
        selected_meaning_preserved=True,
        active_scope_preserved=True,
        certainty_preserved=True,
        evidence_status_preserved=True,
        inherited_limitations_preserved=True,
        required_caveats_preserved=True,
        refusal_boundaries_preserved=True,
        unresolved_conditions_preserved=True,
        ambiguity_preserved=True,
        unsupported_states_preserved=True,
        memory_authority_preserved=True,
        external_resource_status_preserved=True,
        delivery_authority_preserved=True,
        planning_progression_eligible=(
            eligibility_result.eligible_for_expression_planning
        ),
        projection_performed=True,
        obligation_package_created=True,
        scope_upgraded=False,
        certainty_upgraded=False,
        evidence_status_upgraded=False,
        limitation_omitted=False,
        caveat_omitted=False,
        refusal_softened=False,
        unresolved_condition_resolved=False,
        ambiguity_erased=False,
        unsupported_state_erased_or_guessed=False,
        memory_authority_upgraded=False,
        external_resource_status_upgraded=False,
        delivery_authority_upgraded=False,
        selected_meaning_rewritten=False,
        human_readable_text_produced=False,
        governed_outward_meaning_created=False,
        expression_plan_created=False,
        expression_candidate_created=False,
        msm_v1_modified_or_integrated=False,
        echo_validation_performed=False,
        bootstrap_integration_enabled=False,
        delivered=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_or_api_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed_or_written=False,
        filesystem_or_network_accessed=False,
        external_resource_loaded=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    package = with_expected_package_identity(package)

    findings = (
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.EXACT_SLICE42C_STATE_CONFIRMED,
            (
                eligibility_input.evaluation_input_id,
                eligibility_result.result_id,
            ),
            ("exact_validated_slice42c_state",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.EXPLICIT_PROJECTION_AUTHORITY_CONFIRMED,
            (
                projection_authority.projection_authority_record_id,
                projection_authority.projection_authority_receipt_ref,
            ),
            ("separate_explicit_projection_authority",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.SELECTED_MEANING_PRESERVED,
            package.selected_meaning_refs,
            ("selected_meaning_not_rewritten",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.ACTIVE_SCOPE_PRESERVED,
            package.active_scope_refs,
            ("active_scope_not_expanded",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.CERTAINTY_AND_EVIDENCE_STATUS_PRESERVED,
            package.certainty_level_refs + package.evidence_status_refs,
            ("certainty_and_evidence_not_upgraded",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.LIMITATIONS_AND_CAVEATS_PRESERVED,
            package.inherited_limitation_refs + package.required_caveat_refs,
            ("limitations_and_caveats_not_omitted",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.REFUSAL_BOUNDARIES_PRESERVED,
            package.refusal_relevant_boundary_refs,
            ("refusal_boundaries_not_softened",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.UNRESOLVED_AMBIGUITY_PRESERVED,
            package.unresolved_condition_refs + package.ambiguity_refs,
            ("unresolved_and_ambiguity_state_not_erased",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.UNSUPPORTED_STATE_PRESERVED,
            package.unsupported_state_refs,
            ("unsupported_state_not_guessed_or_erased",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.MEMORY_AUTHORITY_STATUS_PRESERVED,
            package.memory_authority_refs,
            ("memory_status_preserved_without_access_or_write",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.EXTERNAL_RESOURCE_STATUS_PRESERVED,
            package.external_resource_status_refs,
            ("external_resource_status_preserved_without_load",),
        ),
        _finding(
            value,
            package,
            PreservationObligationProjectionFindingKind.DELIVERY_AUTHORITY_STATUS_PRESERVED,
            package.delivery_authority_refs,
            ("delivery_status_preserved_without_delivery",),
        ),
    )

    result = PreservationObligationProjectionResult(
        result_id="pending",
        result_digest="0" * 64,
        projection_input_ref=value.projection_input_id,
        obligation_package=package,
        findings=findings,
        required_law_refs=SLICE42D_GOVERNING_AUTHORITY_REFS,
        permanent_boundaries=SLICE42D_PERMANENT_BOUNDARIES,
        prohibited_authority=SLICE42D_PROHIBITED_AUTHORITY,
        source_eligibility_outcome=eligibility_result.outcome,
        eligible_for_expression_planning=(
            eligibility_result.eligible_for_expression_planning
        ),
        held_pending_authority=eligibility_result.held_pending_authority,
        blocked=eligibility_result.blocked,
        refusal_preserving=eligibility_result.refusal_preserving,
        unresolved_preserving=eligibility_result.unresolved_preserving,
        indeterminate=eligibility_result.indeterminate,
        preservation_obligations_projected=True,
        obligation_package_created=True,
        governed_outward_meaning_created=False,
        expression_plan_created=False,
        expression_candidate_created=False,
        human_readable_text_produced=False,
        msm_v1_modified_or_integrated=False,
        echo_validation_performed=False,
        bootstrap_integration_enabled=False,
        delivered=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_or_api_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed_or_written=False,
        filesystem_or_network_accessed=False,
        external_resource_loaded=False,
        model_or_similarity_authority_used=False,
        gp014_superseded=False,
    )
    result = with_expected_result_identity(result)
    assert_valid_projection_result(result, projection_input=value)
    return result


__all__ = (
    "derive_obligation_values",
    "project_preservation_obligations",
)
