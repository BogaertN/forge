"""Deterministic Slice 42C authorized admission and eligibility evaluator."""
from __future__ import annotations
from .authority import SLICE42C_GOVERNING_AUTHORITY_REFS, SLICE42C_PERMANENT_BOUNDARIES, SLICE42C_PROHIBITED_AUTHORITY
from .identity import with_expected_id, with_expected_result_identity
from .schema import (
    AuthorizedMeaningAdmissionRecord, ExpressionEligibilityEvaluationInput,
    ExpressionEligibilityFinding, ExpressionEligibilityFindingKind,
    ExpressionEligibilityOutcome, ExpressionEligibilityResult,
)

def _unique(values: tuple[str, ...]) -> tuple[str, ...]: return tuple(dict.fromkeys(values))

def determine_outcome(value: ExpressionEligibilityEvaluationInput) -> ExpressionEligibilityOutcome:
    source = value.selected_meaning_source_custody
    authority = value.outward_expression_authority_record
    if source.blocked_consequence_refs: return ExpressionEligibilityOutcome.BLOCKED
    if source.refusal_relevant_refs: return ExpressionEligibilityOutcome.REFUSAL_PRESERVING
    if source.unresolved_alternative_refs or source.ambiguity_ancestry_refs or source.clarification_ancestry_refs: return ExpressionEligibilityOutcome.UNRESOLVED_PRESERVING
    if not authority.authority_active or not authority.eligibility_evaluation_authorized: return ExpressionEligibilityOutcome.HELD_PENDING_AUTHORITY
    if authority.expression_planning_progression_authorized: return ExpressionEligibilityOutcome.ELIGIBLE_FOR_EXPRESSION_PLANNING
    return ExpressionEligibilityOutcome.INDETERMINATE

def _finding(value, admission, kind, basis, reasons):
    return with_expected_id(ExpressionEligibilityFinding(
        finding_id="pending", evaluation_input_ref=value.evaluation_input_id,
        admission_record_ref=admission.admission_record_id, finding_kind=kind,
        basis_refs=_unique(basis), reason_refs=_unique(reasons),
        trace_refs=value.trace_refs, provenance_refs=value.provenance_refs,
    ))

def evaluate_expression_eligibility(value: ExpressionEligibilityEvaluationInput) -> ExpressionEligibilityResult:
    from .validation import assert_valid_evaluation_input, assert_valid_result
    assert_valid_evaluation_input(value)
    source=value.selected_meaning_source_custody; req=value.outward_expression_authority_requirement
    auth=value.outward_expression_authority_record; closeout=value.selected_meaning_closeout_result
    bundle=value.outward_expression_governance_bundle
    authority_admitted = auth.authority_active and auth.eligibility_evaluation_authorized
    admission = with_expected_id(AuthorizedMeaningAdmissionRecord(
        admission_record_id="pending", evaluation_input_ref=value.evaluation_input_id,
        slice41f_closeout_result_ref=closeout.result_id, slice41f_acceptance_record_ref=closeout.acceptance_record.record_id,
        slice41e_integration_input_ref=source.slice41e_integration_input_ref,
        slice41e_integration_result_ref=source.slice41e_integration_result_ref,
        slice41e_integration_receipt_ref=source.slice41e_integration_receipt_ref,
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=req.authority_requirement_id,
        outward_expression_governance_bundle_ref=bundle.bundle_id,
        explicit_outward_expression_authority_record_ref=auth.authority_record_id,
        selected_governed_meaning_ref=source.selected_governed_meaning_ref,
        selected_candidate_ref=source.selected_candidate_ref, selection_receipt_ref=source.selection_receipt_ref,
        preserved_alternative_refs=source.preserved_alternative_refs,
        unresolved_alternative_refs=source.unresolved_alternative_refs,
        blocked_consequence_refs=source.blocked_consequence_refs,
        refusal_relevant_refs=source.refusal_relevant_refs,
        exact_selected_meaning_chain_admitted=True,
        exact_outward_expression_authority_admitted=authority_admitted,
        selected_meaning_alone_sufficient=False, structural_validity_grants_expression_authority=False,
        authority_inferred=False, record_repaired_or_substituted=False,
    ))
    findings=[
        _finding(value, admission, ExpressionEligibilityFindingKind.EXACT_SELECTED_MEANING_CHAIN_CONFIRMED,
                 (closeout.result_id, closeout.acceptance_record.record_id, source.selection_receipt_ref), ("exact_accepted_slice41_chain",)),
        _finding(value, admission, ExpressionEligibilityFindingKind.EXACT_SLICE42A_CUSTODY_CONFIRMED,
                 (source.source_custody_id, req.authority_requirement_id), ("exact_slice42a_custody",)),
        _finding(value, admission, ExpressionEligibilityFindingKind.SEALED_SLICE42B_GOVERNANCE_CONFIRMED,
                 (bundle.bundle_id, bundle.lifecycle_record.lifecycle_record_id), ("record_sealed_validation_governance",)),
    ]
    if authority_admitted:
        findings.append(_finding(value, admission, ExpressionEligibilityFindingKind.EXPLICIT_OUTWARD_AUTHORITY_CONFIRMED,
                    (auth.authority_record_id, auth.authority_receipt_ref, auth.disposition_authority_ref), ("explicit_exact_receipt_bound_authority",)))
    else:
        findings.append(_finding(value, admission, ExpressionEligibilityFindingKind.AUTHORITY_MISSING_OR_INACTIVE,
                    (req.authority_requirement_id, auth.authority_record_id), ("authority_not_active_for_eligibility",)))
    if source.blocked_consequence_refs: findings.append(_finding(value, admission, ExpressionEligibilityFindingKind.BLOCKED_CONSEQUENCE_PRESERVED, source.blocked_consequence_refs, ("blocked_consequence_not_erased",)))
    if source.refusal_relevant_refs: findings.append(_finding(value, admission, ExpressionEligibilityFindingKind.REFUSAL_RELEVANCE_PRESERVED, source.refusal_relevant_refs, ("refusal_relevance_not_softened",)))
    unresolved = source.unresolved_alternative_refs + source.ambiguity_ancestry_refs + source.clarification_ancestry_refs
    if unresolved: findings.append(_finding(value, admission, ExpressionEligibilityFindingKind.UNRESOLVED_STATE_PRESERVED, unresolved, ("unresolved_state_not_resolved",)))
    outcome=determine_outcome(value)
    if outcome is ExpressionEligibilityOutcome.INDETERMINATE: findings.append(_finding(value, admission, ExpressionEligibilityFindingKind.INDETERMINATE_FAIL_CLOSED, (value.evaluation_input_id,), ("no_lawful_positive_disposition",)))
    result=ExpressionEligibilityResult(
        result_id="pending", result_digest="0"*64, evaluation_input_ref=value.evaluation_input_id,
        admission_record=admission, authority_record_ref=auth.authority_record_id,
        authority_requirement_ref=req.authority_requirement_id, source_custody_ref=source.source_custody_id,
        governance_bundle_ref=bundle.bundle_id, outcome=outcome, findings=tuple(findings),
        reason_refs=value.evaluation_reason_refs, required_law_refs=SLICE42C_GOVERNING_AUTHORITY_REFS,
        permanent_boundaries=SLICE42C_PERMANENT_BOUNDARIES, prohibited_authority=SLICE42C_PROHIBITED_AUTHORITY,
        eligibility_evaluated=True,
        eligible_for_expression_planning=outcome is ExpressionEligibilityOutcome.ELIGIBLE_FOR_EXPRESSION_PLANNING,
        held_pending_authority=outcome is ExpressionEligibilityOutcome.HELD_PENDING_AUTHORITY,
        blocked=outcome is ExpressionEligibilityOutcome.BLOCKED,
        refusal_preserving=outcome is ExpressionEligibilityOutcome.REFUSAL_PRESERVING,
        unresolved_preserving=outcome is ExpressionEligibilityOutcome.UNRESOLVED_PRESERVING,
        indeterminate=outcome is ExpressionEligibilityOutcome.INDETERMINATE,
        selected_meaning_chain_admitted=True, outward_expression_authority_admitted=authority_admitted,
        selected_meaning_alone_sufficient=False, structural_validity_grants_expression_authority=False,
        preservation_obligations_projected=False, governed_outward_meaning_created=False,
        expression_plan_created=False, expression_candidate_created=False, human_readable_text_produced=False,
        msm_v1_modified_or_integrated=False, echo_validation_performed=False, bootstrap_integration_enabled=False,
        delivered=False, truth_determined=False, evidence_validated=False, permission_granted=False,
        execution_authorized=False, route_or_api_created=False, tool_invoked=False, action_performed=False,
        memory_accessed_or_written=False, filesystem_or_network_accessed=False, external_resource_loaded=False,
        model_or_similarity_authority_used=False, gp014_superseded=False,
    )
    result=with_expected_result_identity(result)
    assert_valid_result(result, evaluation_input=value)
    return result

__all__=("determine_outcome", "evaluate_expression_eligibility")
