"""Deterministic Slice 42F surface realization."""

from __future__ import annotations

import hashlib
from typing import Iterable

from ..expression_plan_construction.schema import ExpressionPlanDisposition
from .authority import (
    SLICE42F_ADMITTED_RULE_REFS,
    SLICE42F_GOVERNING_AUTHORITY_REFS,
    SLICE42F_PERMANENT_BOUNDARIES,
    SLICE42F_PROHIBITED_AUTHORITY,
)
from .identity import with_expected_candidate_identity, with_expected_id, with_expected_result_identity
from .schema import (
    ControlledRealizationResourceKind,
    SurfaceRealizationDisposition,
    SurfaceRealizationFinding,
    SurfaceRealizationFindingKind,
    SurfaceRealizationInput,
    SurfaceRealizationReceipt,
    SurfaceRealizationResult,
    SurfaceRealizationTrace,
    UnvalidatedExpressionCandidate,
)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _unique(*groups: Iterable[str]) -> tuple[str, ...]:
    ordered: dict[str, None] = {}
    for group in groups:
        for value in group:
            ordered.setdefault(value, None)
    return tuple(ordered)


def determine_realization_disposition(source: ExpressionPlanDisposition) -> SurfaceRealizationDisposition:
    return {
        ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN: SurfaceRealizationDisposition.AUTHORIZED_EXPRESSION_CANDIDATE,
        ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN: SurfaceRealizationDisposition.BLOCKED_EXPRESSION_CANDIDATE,
        ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN: SurfaceRealizationDisposition.REFUSAL_EXPRESSION_CANDIDATE,
        ExpressionPlanDisposition.UNRESOLVED_PRESERVING_PLAN: SurfaceRealizationDisposition.UNRESOLVED_EXPRESSION_CANDIDATE,
        ExpressionPlanDisposition.HELD_PENDING_AUTHORITY: SurfaceRealizationDisposition.HELD_PENDING_AUTHORITY,
        ExpressionPlanDisposition.INDETERMINATE: SurfaceRealizationDisposition.INDETERMINATE,
    }[source]


def _resource_by_key(value: SurfaceRealizationInput, key: str):
    matches = tuple(record for record in value.controlled_resource_bundle.records if record.resource_key == key)
    return matches[0] if len(matches) == 1 else None


def _template_resource(value: SurfaceRealizationInput):
    plan = value.plan_result.expression_plan
    return None if plan is None else _resource_by_key(value, f"template:{plan.disposition.value}")


def _claim_resource(value: SurfaceRealizationInput):
    plan = value.plan_result.expression_plan
    if plan is None:
        return None
    matches = tuple(
        record for record in value.controlled_resource_bundle.records
        if record.resource_kind is ControlledRealizationResourceKind.AUTHORIZED_CLAIM_TEXT
        and record.bound_selected_meaning_ref == plan.selected_meaning_source_custody_ref
    )
    return matches[0] if len(matches) == 1 else None


def _visible_refs(label: str, refs: tuple[str, ...]) -> str | None:
    return None if not refs else f"{label}: " + "; ".join(refs) + "."


def build_realization_segments(value: SurfaceRealizationInput) -> tuple[str, ...]:
    plan = value.plan_result.expression_plan
    template = _template_resource(value)
    if plan is None or template is None:
        return ()
    segments: list[str] = [template.resource_text]
    if plan.disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN:
        claim = _claim_resource(value)
        if claim is None:
            return ()
        segments.append(claim.resource_text)
    else:
        segments.append(
            "The selected meaning remains unchanged and no affirmative claim "
            "is authorized by this containment expression."
        )
    groups = (
        ("Selected meaning references remain", plan.selected_meaning_refs),
        ("Active scope remains", plan.active_scope_refs),
        ("Certainty status remains", plan.certainty_level_refs),
        ("Evidence status remains", plan.evidence_status_refs),
        ("Meaning modifiers remain", plan.meaning_modifier_refs),
        ("Inherited limitations remain", plan.inherited_limitation_refs),
        ("Required qualifications remain", plan.required_qualification_refs),
        ("Required caveats remain", plan.required_caveat_refs),
        ("Refusal boundaries remain", plan.refusal_relevant_boundary_refs),
        ("Unresolved conditions remain", plan.unresolved_condition_refs),
        ("Ambiguity remains", plan.ambiguity_refs),
        ("Unsupported states remain", plan.unsupported_state_refs),
        ("Memory authority status remains", plan.memory_authority_refs),
        ("External-resource status remains", plan.external_resource_status_refs),
        ("Delivery authority status remains", plan.delivery_authority_refs),
        ("Privacy and identity boundaries remain", plan.privacy_identity_boundary_refs),
    )
    for label, refs in groups:
        segment = _visible_refs(label, refs)
        if segment is not None:
            segments.append(segment)
    segments.append(
        "This is an unvalidated expression candidate. It has not been "
        "Echo-approved and is not authorized for delivery."
    )
    return tuple(segments)


def applied_resource_records(value: SurfaceRealizationInput):
    template = _template_resource(value)
    if template is None:
        return ()
    records = [template]
    plan = value.plan_result.expression_plan
    if plan is not None and plan.disposition is ExpressionPlanDisposition.AUTHORIZED_MEANING_PLAN:
        claim = _claim_resource(value)
        if claim is not None:
            records.append(claim)
    return tuple(records)


def _finding(value, candidate, kind, basis_refs, reason_refs):
    return with_expected_id(
        SurfaceRealizationFinding(
            finding_id="pending",
            realization_input_ref=value.realization_input_id,
            expression_candidate_ref=candidate.expression_candidate_id if candidate else None,
            finding_kind=kind,
            basis_refs=basis_refs,
            reason_refs=reason_refs,
            trace_refs=value.trace_refs,
            provenance_refs=value.provenance_refs,
        )
    )


def realize_surface_expression(value: SurfaceRealizationInput) -> SurfaceRealizationResult:
    from .validation import assert_valid_surface_realization_input, assert_valid_surface_realization_result
    assert_valid_surface_realization_input(value)
    plan_result = value.plan_result
    plan = plan_result.expression_plan
    disposition = determine_realization_disposition(plan_result.disposition)
    candidate = trace = receipt = None
    constructible = plan is not None and disposition in (
        SurfaceRealizationDisposition.AUTHORIZED_EXPRESSION_CANDIDATE,
        SurfaceRealizationDisposition.BLOCKED_EXPRESSION_CANDIDATE,
        SurfaceRealizationDisposition.REFUSAL_EXPRESSION_CANDIDATE,
        SurfaceRealizationDisposition.UNRESOLVED_EXPRESSION_CANDIDATE,
    )
    if constructible:
        segments = build_realization_segments(value)
        text = " ".join(segments)
        resources = applied_resource_records(value)
        candidate = with_expected_candidate_identity(
            UnvalidatedExpressionCandidate(
                expression_candidate_id="pending",
                expression_candidate_digest="0" * 64,
                realization_input_ref=value.realization_input_id,
                plan_result_ref=plan_result.result_id,
                expression_plan_ref=plan.expression_plan_id,
                realization_authority_record_ref=value.realization_authority_record.realization_authority_record_id,
                controlled_resource_bundle_ref=value.controlled_resource_bundle.resource_bundle_id,
                selected_meaning_source_custody_ref=plan.selected_meaning_source_custody_ref,
                source_plan_disposition=plan.disposition,
                disposition=disposition,
                realized_text=text,
                realized_text_sha256=_sha256_text(text),
                segments=segments,
                selected_meaning_refs=plan.selected_meaning_refs,
                active_scope_refs=plan.active_scope_refs,
                certainty_level_refs=plan.certainty_level_refs,
                evidence_status_refs=plan.evidence_status_refs,
                meaning_modifier_refs=plan.meaning_modifier_refs,
                inherited_limitation_refs=plan.inherited_limitation_refs,
                required_qualification_refs=plan.required_qualification_refs,
                required_caveat_refs=plan.required_caveat_refs,
                refusal_relevant_boundary_refs=plan.refusal_relevant_boundary_refs,
                unresolved_condition_refs=plan.unresolved_condition_refs,
                ambiguity_refs=plan.ambiguity_refs,
                unsupported_state_refs=plan.unsupported_state_refs,
                memory_authority_refs=plan.memory_authority_refs,
                external_resource_status_refs=plan.external_resource_status_refs,
                delivery_authority_refs=plan.delivery_authority_refs,
                privacy_identity_boundary_refs=plan.privacy_identity_boundary_refs,
                preservation_class_refs=plan.preservation_class_refs,
                ancestry_refs=plan.ancestry_refs,
                predecessor_receipt_refs=plan.predecessor_receipt_refs,
                applied_rule_refs=SLICE42F_ADMITTED_RULE_REFS,
                applied_resource_refs=tuple(r.resource_record_id for r in resources),
                trace_refs=_unique(plan.trace_refs, value.trace_refs),
                provenance_refs=_unique(plan.provenance_refs, value.provenance_refs),
                version_refs=_unique(plan.version_refs, value.version_refs),
                exact_slice42e_plan_verified=True,
                exact_realization_authority_verified=True,
                admitted_rules_only=True,
                controlled_resources_only=True,
                authorized_claim_not_strengthened=True,
                certainty_not_upgraded=True,
                evidence_status_not_upgraded=True,
                caveats_visible=bool(plan.required_caveat_refs),
                unresolved_states_visible=bool(plan.unresolved_condition_refs or plan.ambiguity_refs or plan.unsupported_state_refs),
                refusal_language_produced=plan.disposition in (
                    ExpressionPlanDisposition.BLOCKED_CONSEQUENCE_PLAN,
                    ExpressionPlanDisposition.REFUSAL_PRESERVING_PLAN,
                ),
                deterministic_surface_realization_performed=True,
                human_readable_text_produced=True,
                expression_candidate_created=True,
                unvalidated_expression_candidate=True,
                echo_validation_performed=False,
                echo_approved=False,
                delivery_authorized=False,
                delivered=False,
                governed_outward_meaning_created=False,
                msm_v1_modified_or_integrated=False,
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
        )
        trace = with_expected_id(
            SurfaceRealizationTrace(
                realization_trace_id="pending",
                realization_input_ref=value.realization_input_id,
                expression_plan_ref=plan.expression_plan_id,
                expression_candidate_ref=candidate.expression_candidate_id,
                realized_text_sha256=candidate.realized_text_sha256,
                segment_sha256s=tuple(_sha256_text(item) for item in segments),
                applied_rule_refs=candidate.applied_rule_refs,
                applied_resource_refs=candidate.applied_resource_refs,
                ancestry_refs=candidate.ancestry_refs,
                predecessor_trace_refs=candidate.trace_refs,
                predecessor_receipt_refs=candidate.predecessor_receipt_refs,
                provenance_refs=candidate.provenance_refs,
                version_refs=candidate.version_refs,
                deterministic=True,
                semantic_strengthening_detected=False,
                certainty_upgrade_detected=False,
                evidence_upgrade_detected=False,
                omission_detected=False,
            )
        )
        receipt = with_expected_id(
            SurfaceRealizationReceipt(
                realization_receipt_id="pending",
                realization_input_ref=value.realization_input_id,
                expression_plan_ref=plan.expression_plan_id,
                expression_candidate_ref=candidate.expression_candidate_id,
                realization_trace_ref=trace.realization_trace_id,
                realization_authority_record_ref=value.realization_authority_record.realization_authority_record_id,
                controlled_resource_bundle_ref=value.controlled_resource_bundle.resource_bundle_id,
                realized_text_sha256=candidate.realized_text_sha256,
                required_law_refs=SLICE42F_GOVERNING_AUTHORITY_REFS,
                prohibited_consequence_refs=SLICE42F_PROHIBITED_AUTHORITY,
                deterministic=True,
                surface_realization_performed=True,
                expression_candidate_created=True,
                unvalidated_expression_candidate=True,
                echo_validated=False,
                echo_approved=False,
                delivery_authorized=False,
                delivered=False,
            )
        )
    findings = (
        _finding(value, candidate, SurfaceRealizationFindingKind.EXACT_SLICE42E_PLAN_CONFIRMED,
                 (value.plan_input.plan_input_id, value.plan_result.result_id, plan.expression_plan_id if plan else value.plan_result.result_id),
                 ("exact_validated_slice42e_plan_state",)),
        _finding(value, candidate, SurfaceRealizationFindingKind.EXPLICIT_REALIZATION_AUTHORITY_CONFIRMED,
                 (value.realization_authority_record.realization_authority_record_id,
                  value.realization_authority_record.realization_authority_receipt_ref),
                 ("separate_explicit_surface_realization_authority",)),
        _finding(value, candidate, SurfaceRealizationFindingKind.CONTROLLED_RESOURCES_CONFIRMED,
                 tuple(r.resource_record_id for r in applied_resource_records(value)),
                 ("admitted_deterministic_rules_and_controlled_resources_only",)),
        _finding(value, candidate, SurfaceRealizationFindingKind.AUTHORIZED_CLAIM_NOT_STRENGTHENED,
                 candidate.selected_meaning_refs if candidate else (),
                 ("no_claim_invention_strengthening_or_scope_expansion",)),
        _finding(value, candidate, SurfaceRealizationFindingKind.CERTAINTY_AND_EVIDENCE_NOT_UPGRADED,
                 _unique(candidate.certainty_level_refs if candidate else (), candidate.evidence_status_refs if candidate else ()),
                 ("certainty_and_evidence_status_preserved_exactly",)),
        _finding(value, candidate, SurfaceRealizationFindingKind.CAVEATS_REFUSAL_AND_UNRESOLVED_VISIBLE,
                 _unique(candidate.required_caveat_refs if candidate else (),
                         candidate.refusal_relevant_boundary_refs if candidate else (),
                         candidate.unresolved_condition_refs if candidate else (),
                         candidate.ambiguity_refs if candidate else (),
                         candidate.unsupported_state_refs if candidate else ()),
                 ("required_nonaffirmative_conditions_visible",)),
        _finding(value, candidate, SurfaceRealizationFindingKind.DETERMINISTIC_TRACE_AND_RECEIPT_CREATED,
                 (trace.realization_trace_id if trace else value.realization_input_id,
                  receipt.realization_receipt_id if receipt else value.realization_input_id),
                 ("exact_text_rule_resource_ancestry_trace_receipt_binding",)),
        _finding(value, candidate, SurfaceRealizationFindingKind.UNVALIDATED_NONDELIVERABLE_BOUNDARY_CONFIRMED,
                 (candidate.expression_candidate_id if candidate else value.realization_input_id,),
                 ("candidate_not_echo_approved_and_not_deliverable",)),
    )
    result = with_expected_result_identity(
        SurfaceRealizationResult(
            result_id="pending",
            result_digest="0" * 64,
            realization_input_ref=value.realization_input_id,
            expression_candidate=candidate,
            realization_trace=trace,
            realization_receipt=receipt,
            findings=findings,
            required_law_refs=SLICE42F_GOVERNING_AUTHORITY_REFS,
            permanent_boundaries=SLICE42F_PERMANENT_BOUNDARIES,
            prohibited_authority=SLICE42F_PROHIBITED_AUTHORITY,
            source_plan_disposition=plan_result.disposition,
            disposition=disposition,
            surface_realization_performed=candidate is not None,
            human_readable_text_produced=candidate is not None,
            expression_candidate_created=candidate is not None,
            refusal_language_produced=candidate.refusal_language_produced if candidate else False,
            authorized_claim_not_strengthened=candidate is not None,
            certainty_not_upgraded=candidate is not None,
            evidence_status_not_upgraded=candidate is not None,
            caveats_and_unresolved_states_visible=candidate is not None,
            deterministic_trace_created=trace is not None,
            deterministic_receipt_created=receipt is not None,
            unvalidated_expression_candidate=candidate is not None,
            held_pending_authority=disposition is SurfaceRealizationDisposition.HELD_PENDING_AUTHORITY,
            indeterminate=disposition is SurfaceRealizationDisposition.INDETERMINATE,
            governed_outward_meaning_created=False,
            msm_v1_modified_or_integrated=False,
            echo_validation_performed=False,
            echo_approved=False,
            delivery_authorized=False,
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
    )
    assert_valid_surface_realization_result(result, realization_input=value)
    return result


__all__ = (
    "applied_resource_records",
    "build_realization_segments",
    "determine_realization_disposition",
    "realize_surface_expression",
)
