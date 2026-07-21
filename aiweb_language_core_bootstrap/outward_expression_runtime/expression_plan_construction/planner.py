"""Deterministic Slice 42E controlled expression-plan construction."""

from __future__ import annotations

from typing import Any, Iterable

from ..expression_eligibility.schema import ExpressionEligibilityOutcome
from .authority import (
    SLICE42E_GOVERNING_AUTHORITY_REFS,
    SLICE42E_PERMANENT_BOUNDARIES,
    SLICE42E_PROHIBITED_AUTHORITY,
    SLICE42E_SECTION_ORDER_VALUES,
)
from .identity import (
    with_expected_id,
    with_expected_plan_identity,
    with_expected_result_identity,
)
from .schema import (
    ControlledExpressionPlan,
    ExpressionPlanConstructionFinding,
    ExpressionPlanConstructionFindingKind,
    ExpressionPlanConstructionInput,
    ExpressionPlanConstructionResult,
    ExpressionPlanDisposition,
    ExpressionPlanSection,
    ExpressionPlanSectionKind,
)


def _unique(*groups: Iterable[str]) -> tuple[str, ...]:
    ordered: dict[str, None] = {}
    for group in groups:
        for value in group:
            ordered.setdefault(value, None)
    return tuple(ordered)


def structural_order() -> tuple[ExpressionPlanSectionKind, ...]:
    return tuple(ExpressionPlanSectionKind(value) for value in SLICE42E_SECTION_ORDER_VALUES)


def determine_plan_disposition(
    value: ExpressionPlanConstructionInput,
) -> ExpressionPlanDisposition:
    result = value.projection_result
    if result.eligible_for_expression_planning:
        return ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN
    if result.blocked:
        return ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN
    if result.refusal_preserving:
        return ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN
    if result.unresolved_preserving:
        return ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN
    if result.held_pending_authority:
        return ExpressionPlanDisposition.HELD_PENDING_AUTHORITY
    return ExpressionPlanDisposition.INDETERMINATE


def _selected_meaning_record(value: ExpressionPlanConstructionInput) -> Any:
    closeout = (
        value.projection_input.expression_eligibility_evaluation_input
        .selected_meaning_closeout_result
    )
    integration_input = closeout.integration_input
    if integration_input is None:
        raise ValueError("completed Slice 41F integration input is required")
    return integration_input.selected_meaning_package.selected_meaning_record


def derive_plan_values(
    value: ExpressionPlanConstructionInput,
) -> dict[str, Any]:
    package = value.projection_result.obligation_package
    selected = _selected_meaning_record(value)
    authority = value.planning_authority_record
    disposition = determine_plan_disposition(value)
    qualifications = _unique(
        package.active_scope_refs,
        package.certainty_level_refs,
        package.evidence_status_refs,
        package.inherited_limitation_refs,
        package.required_caveat_refs,
    )
    ancestry = _unique(
        package.selected_meaning_refs,
        (
            package.selected_meaning_source_custody_ref,
            package.obligation_package_id,
            value.projection_result.result_id,
        ),
    )
    receipts = _unique(
        package.predecessor_receipt_refs,
        (
            value.projection_input.projection_authority_record
            .projection_authority_receipt_ref,
        ),
    )
    return {
        "disposition": disposition,
        "selected_meaning_refs": package.selected_meaning_refs,
        "active_scope_refs": package.active_scope_refs,
        "certainty_level_refs": package.certainty_level_refs,
        "evidence_status_refs": package.evidence_status_refs,
        "meaning_modifier_refs": tuple(selected.meaning_modifiers),
        "inherited_limitation_refs": package.inherited_limitation_refs,
        "required_qualification_refs": qualifications,
        "required_caveat_refs": package.required_caveat_refs,
        "refusal_relevant_boundary_refs": package.refusal_relevant_boundary_refs,
        "unresolved_condition_refs": package.unresolved_condition_refs,
        "ambiguity_refs": package.ambiguity_refs,
        "unsupported_state_refs": package.unsupported_state_refs,
        "memory_authority_refs": package.memory_authority_refs,
        "external_resource_status_refs": package.external_resource_status_refs,
        "delivery_authority_refs": package.delivery_authority_refs,
        "privacy_identity_boundary_refs": package.privacy_identity_boundary_refs,
        "preservation_class_refs": package.preservation_class_refs,
        "ancestry_refs": ancestry,
        "predecessor_receipt_refs": receipts,
        "trace_refs": _unique(package.trace_refs, value.trace_refs),
        "provenance_refs": _unique(package.provenance_refs, value.provenance_refs),
        "version_refs": _unique(package.version_refs, value.version_refs, authority.version_refs),
    }


def section_source_values(
    value: ExpressionPlanConstructionInput,
    derived: dict[str, Any] | None = None,
) -> dict[ExpressionPlanSectionKind, tuple[str, ...]]:
    data = derived or derive_plan_values(value)
    disposition = data["disposition"]
    projection_result = value.projection_result
    return {
        ExpressionPlanSectionKind.GOVERNING_DISPOSITION: (
            f"expression-plan-disposition:{disposition.value}",
            projection_result.result_id,
        ),
        ExpressionPlanSectionKind.SELECTED_MEANING: data["selected_meaning_refs"],
        ExpressionPlanSectionKind.ACTIVE_SCOPE: data["active_scope_refs"],
        ExpressionPlanSectionKind.CERTAINTY: data["certainty_level_refs"],
        ExpressionPlanSectionKind.EVIDENCE_STATUS: data["evidence_status_refs"],
        ExpressionPlanSectionKind.MEANING_MODIFIERS: data["meaning_modifier_refs"],
        ExpressionPlanSectionKind.INHERITED_LIMITATIONS: data["inherited_limitation_refs"],
        ExpressionPlanSectionKind.REQUIRED_QUALIFICATIONS: data["required_qualification_refs"],
        ExpressionPlanSectionKind.REQUIRED_CAVEATS: data["required_caveat_refs"],
        ExpressionPlanSectionKind.REFUSAL_BOUNDARIES: data["refusal_relevant_boundary_refs"],
        ExpressionPlanSectionKind.UNRESOLVED_CONDITIONS: data["unresolved_condition_refs"],
        ExpressionPlanSectionKind.AMBIGUITY: data["ambiguity_refs"],
        ExpressionPlanSectionKind.UNSUPPORTED_STATES: data["unsupported_state_refs"],
        ExpressionPlanSectionKind.MEMORY_AUTHORITY: data["memory_authority_refs"],
        ExpressionPlanSectionKind.EXTERNAL_RESOURCE_STATUS: data["external_resource_status_refs"],
        ExpressionPlanSectionKind.DELIVERY_AUTHORITY: data["delivery_authority_refs"],
        ExpressionPlanSectionKind.PRIVACY_IDENTITY_BOUNDARIES: data["privacy_identity_boundary_refs"],
    }


def build_plan_sections(
    value: ExpressionPlanConstructionInput,
    derived: dict[str, Any] | None = None,
) -> tuple[ExpressionPlanSection, ...]:
    data = derived or derive_plan_values(value)
    sources = section_source_values(value, data)
    return tuple(
        with_expected_id(
            ExpressionPlanSection(
                section_id="pending",
                plan_input_ref=value.plan_input_id,
                section_kind=kind,
                precedence_index=index,
                source_refs=sources[kind],
                required_for_plan_custody=True,
                omission_prohibited=True,
                lower_order_override_prohibited=True,
                human_readable_text_present=False,
            )
        )
        for index, kind in enumerate(structural_order(), start=1)
    )


def _finding(
    value: ExpressionPlanConstructionInput,
    plan: ControlledExpressionPlan | None,
    kind: ExpressionPlanConstructionFindingKind,
    basis: tuple[str, ...],
    reasons: tuple[str, ...],
) -> ExpressionPlanConstructionFinding:
    return with_expected_id(
        ExpressionPlanConstructionFinding(
            finding_id="pending",
            plan_input_ref=value.plan_input_id,
            expression_plan_ref=(plan.expression_plan_id if plan else None),
            finding_kind=kind,
            basis_refs=_unique(basis),
            reason_refs=_unique(reasons),
            trace_refs=value.trace_refs,
            provenance_refs=value.provenance_refs,
        )
    )


def construct_expression_plan(
    value: ExpressionPlanConstructionInput,
) -> ExpressionPlanConstructionResult:
    from .validation import (
        assert_valid_plan_input,
        assert_valid_plan_result,
    )

    assert_valid_plan_input(value)
    projection_result = value.projection_result
    package = projection_result.obligation_package
    authority = value.planning_authority_record
    derived = derive_plan_values(value)
    disposition = derived["disposition"]
    constructible = disposition in (
        ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
        ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
        ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
        ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN,
    )

    plan: ControlledExpressionPlan | None = None
    if constructible:
        sections = build_plan_sections(value, derived)
        plan = ControlledExpressionPlan(
            expression_plan_id="pending",
            expression_plan_digest="0" * 64,
            plan_input_ref=value.plan_input_id,
            projection_result_ref=projection_result.result_id,
            obligation_package_ref=package.obligation_package_id,
            planning_authority_record_ref=authority.planning_authority_record_id,
            selected_meaning_source_custody_ref=package.selected_meaning_source_custody_ref,
            outward_expression_authority_record_ref=package.outward_expression_authority_record_ref,
            source_eligibility_outcome=package.source_eligibility_outcome,
            disposition=disposition,
            sections=sections,
            structural_order=structural_order(),
            selected_meaning_refs=derived["selected_meaning_refs"],
            active_scope_refs=derived["active_scope_refs"],
            certainty_level_refs=derived["certainty_level_refs"],
            evidence_status_refs=derived["evidence_status_refs"],
            meaning_modifier_refs=derived["meaning_modifier_refs"],
            inherited_limitation_refs=derived["inherited_limitation_refs"],
            required_qualification_refs=derived["required_qualification_refs"],
            required_caveat_refs=derived["required_caveat_refs"],
            refusal_relevant_boundary_refs=derived["refusal_relevant_boundary_refs"],
            unresolved_condition_refs=derived["unresolved_condition_refs"],
            ambiguity_refs=derived["ambiguity_refs"],
            unsupported_state_refs=derived["unsupported_state_refs"],
            memory_authority_refs=derived["memory_authority_refs"],
            external_resource_status_refs=derived["external_resource_status_refs"],
            delivery_authority_refs=derived["delivery_authority_refs"],
            privacy_identity_boundary_refs=derived["privacy_identity_boundary_refs"],
            preservation_class_refs=derived["preservation_class_refs"],
            ancestry_refs=derived["ancestry_refs"],
            predecessor_receipt_refs=derived["predecessor_receipt_refs"],
            trace_refs=derived["trace_refs"],
            provenance_refs=derived["provenance_refs"],
            version_refs=derived["version_refs"],
            exact_slice42d_state_verified=True,
            exact_plan_authority_verified=True,
            all_slice42d_obligations_preserved=True,
            structural_ordering_determined=True,
            meaning_modifiers_preserved=True,
            required_qualifications_preserved=True,
            required_caveats_preserved=True,
            refusal_boundaries_preserved=True,
            higher_order_restrictions_dominant=True,
            selected_meaning_ancestry_preserved=True,
            source_planning_progression_eligible=package.planning_progression_eligible,
            affirmative_claim_plan=(disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN),
            blocked_consequence_plan=(disposition is ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN),
            refusal_preserving_plan=(disposition is ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN),
            unresolved_preserving_plan=(disposition is ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN),
            containment_plan_does_not_upgrade_source_eligibility=(
                disposition is not ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN
            ),
            expression_plan_created=True,
            governed_outward_meaning_created=False,
            human_readable_text_produced=False,
            expression_candidate_created=False,
            surface_realization_performed=False,
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
        plan = with_expected_plan_identity(plan)

    plan_ref = plan.expression_plan_id if plan else None
    findings = (
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.EXACT_SLICE42D_STATE_CONFIRMED,
            (value.projection_input.projection_input_id, projection_result.result_id, package.obligation_package_id),
            ("exact_validated_slice42d_state",),
        ),
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.EXPLICIT_PLAN_AUTHORITY_CONFIRMED,
            (authority.planning_authority_record_id, authority.planning_authority_receipt_ref),
            ("separate_explicit_plan_authority",),
        ),
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.OBLIGATIONS_PRESERVED,
            (package.obligation_package_id,),
            ("all_slice42d_obligation_categories_preserved",),
        ),
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.STRUCTURAL_ORDER_DETERMINED,
            tuple(section.section_id for section in plan.sections) if plan else (),
            ("fixed_permitted_structural_order",),
        ),
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.MODIFIERS_QUALIFICATIONS_CAVEATS_REFUSAL_PRESERVED,
            _unique(
                derived["meaning_modifier_refs"],
                derived["required_qualification_refs"],
                derived["required_caveat_refs"],
                derived["refusal_relevant_boundary_refs"],
            ),
            ("no_modifier_qualification_caveat_or_refusal_loss",),
        ),
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.HIGHER_ORDER_RESTRICTIONS_DOMINANT,
            (f"expression-plan-disposition:{disposition.value}",),
            ("lower_order_choices_cannot_override_governed_disposition",),
        ),
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.SELECTED_MEANING_ANCESTRY_PRESERVED,
            derived["ancestry_refs"],
            ("exact_selected_meaning_ancestry",),
        ),
        _finding(
            value,
            plan,
            ExpressionPlanConstructionFindingKind.NON_REALIZATION_BOUNDARY_CONFIRMED,
            (plan_ref,) if plan_ref else (value.plan_input_id,),
            ("expression_structure_not_final_text",),
        ),
    )

    result = ExpressionPlanConstructionResult(
        result_id="pending",
        result_digest="0" * 64,
        plan_input_ref=value.plan_input_id,
        expression_plan=plan,
        findings=findings,
        required_law_refs=SLICE42E_GOVERNING_AUTHORITY_REFS,
        permanent_boundaries=SLICE42E_PERMANENT_BOUNDARIES,
        prohibited_authority=SLICE42E_PROHIBITED_AUTHORITY,
        source_eligibility_outcome=projection_result.source_eligibility_outcome,
        disposition=disposition,
        expression_plan_created=plan is not None,
        affirmative_claim_plan=disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN,
        blocked_consequence_plan=disposition is ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
        refusal_preserving_plan=disposition is ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
        unresolved_preserving_plan=disposition is ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN,
        held_pending_authority=disposition is ExpressionPlanDisposition.HELD_PENDING_AUTHORITY,
        indeterminate=disposition is ExpressionPlanDisposition.INDETERMINATE,
        all_slice42d_obligations_preserved=plan is not None,
        structural_ordering_determined=plan is not None,
        lower_order_choice_overrode_semantics=False,
        governed_outward_meaning_created=False,
        human_readable_text_produced=False,
        expression_candidate_created=False,
        surface_realization_performed=False,
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
    assert_valid_plan_result(result, plan_input=value)
    return result


__all__ = (
    "build_plan_sections",
    "construct_expression_plan",
    "derive_plan_values",
    "determine_plan_disposition",
    "section_source_values",
    "structural_order",
)
