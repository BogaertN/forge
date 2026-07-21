"""Fail-closed Slice 42C validation and exact cross-record consistency law."""
from __future__ import annotations
from dataclasses import fields
import re
from typing import Any

from ...disabled_selected_meaning_closeout import assert_valid_result as assert_valid_slice41f_result
from ...disabled_selected_meaning_closeout.schema import DisabledSelectedMeaningCloseoutResult, Slice41CloseoutStatus
from ..schema import SelectedMeaningExpressionSourceCustodyRecord, OutwardExpressionAuthorityRequirementRecord
from ..governed_lifecycle import validate_source_custody, validate_authority_requirement, validate_governance_bundle
from ..governed_lifecycle.schema import OutwardExpressionGovernanceBundle, OutwardExpressionLifecycleStage
from .authority import SLICE42C_PROFILE_KEY, SLICE42C_PROFILE_VERSION, SLICE42C_SCHEMA_VERSION
from .identity import expected_record_id, expected_result_digest, expected_result_id
from .schema import (
    AuthorizedMeaningAdmissionRecord, ExpressionEligibilityEvaluationInput,
    ExpressionEligibilityFinding, ExpressionEligibilityOutcome, ExpressionEligibilityResult,
    ExpressionEligibilityValidationCode as Code, ExpressionEligibilityValidationError,
    ExpressionEligibilityValidationIssue as Issue, ExpressionEligibilityValidationReport as Report,
    OutwardExpressionAuthorityRecord,
)

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#@+\-]{0,1023}$")

def _issue(path: str, code: Code, detail: str) -> Issue: return Issue(path, code, detail)
def _report(issues: list[Issue] | tuple[Issue, ...]) -> Report: return Report(tuple(issues))
def _id(value: Any, path: str) -> list[Issue]:
    return [] if type(value) is str and bool(_ID.fullmatch(value)) else [_issue(path, Code.INVALID_IDENTIFIER, "exact governed identifier required")]
def _ids(value: Any, path: str, *, allow_empty: bool=True) -> list[Issue]:
    if type(value) is not tuple: return [_issue(path, Code.TYPE_MISMATCH, "exact tuple required")]
    issues: list[Issue] = []
    if not allow_empty and not value: issues.append(_issue(path, Code.RECORD_INVALID, "non-empty tuple required"))
    if len(value) != len(set(value)): issues.append(_issue(path, Code.DUPLICATE_ID, "duplicate tuple values prohibited"))
    for index, item in enumerate(value): issues.extend(_id(item, f"{path}[{index}]"))
    return issues

def _downstream_true(value: Any) -> tuple[str, ...]:
    names = (
        "preservation_obligation_projection_authorized", "governed_outward_meaning_construction_authorized",
        "expression_plan_construction_authorized", "surface_realization_authorized",
        "msm_v1_mutation_or_integration_authorized", "echo_validation_authorized", "delivery_authorized",
        "truth_evidence_permission_execution_authorized", "route_api_network_filesystem_memory_tool_action_authorized",
        "external_resource_or_model_authority", "gp014_supersession_authorized",
    )
    return tuple(name for name in names if getattr(value, name, False) is not False)

def validate_authority_record(value: Any, *, requirement: OutwardExpressionAuthorityRequirementRecord | None=None) -> Report:
    if type(value) is not OutwardExpressionAuthorityRecord:
        return _report([_issue("authority_record", Code.TYPE_MISMATCH, "exact OutwardExpressionAuthorityRecord required")])
    issues: list[Issue] = []
    for name in ("authority_record_id", "authority_key", "authority_version", "selected_meaning_source_custody_ref", "authority_requirement_ref", "disposition_authority_ref", "authority_receipt_ref"):
        issues.extend(_id(getattr(value, name), f"authority_record.{name}"))
    for name in ("authority_scope_refs", "expression_purpose_refs", "predecessor_receipt_refs", "version_refs"):
        issues.extend(_ids(getattr(value, name), f"authority_record.{name}", allow_empty=False))
    if value.profile_key != SLICE42C_PROFILE_KEY or value.profile_version != SLICE42C_PROFILE_VERSION or value.schema_version != SLICE42C_SCHEMA_VERSION:
        issues.append(_issue("authority_record.version", Code.INVALID_VERSION, "exact Slice 42C profile and schema versions required"))
    for name in ("authority_active", "eligibility_evaluation_authorized", "expression_planning_progression_authorized"):
        if type(getattr(value, name)) is not bool: issues.append(_issue(f"authority_record.{name}", Code.TYPE_MISMATCH, "exact bool required"))
    for name in _downstream_true(value): issues.append(_issue(f"authority_record.{name}", Code.DOWNSTREAM_AUTHORITY, "Slice 42C may not grant downstream authority"))
    if requirement is not None:
        if value.authority_key != requirement.required_outward_expression_authority_ref: issues.append(_issue("authority_record.authority_key", Code.AUTHORITY_RECORD_MISMATCH, "required authority key mismatch"))
        if value.selected_meaning_source_custody_ref != requirement.selected_meaning_source_custody_ref: issues.append(_issue("authority_record.selected_meaning_source_custody_ref", Code.AUTHORITY_RECORD_MISMATCH, "source custody mismatch"))
        if value.authority_requirement_ref != requirement.authority_requirement_id: issues.append(_issue("authority_record.authority_requirement_ref", Code.AUTHORITY_REQUIREMENT_MISMATCH, "authority requirement mismatch"))
        if value.authority_scope_refs != requirement.required_authority_scope_refs: issues.append(_issue("authority_record.authority_scope_refs", Code.AUTHORITY_SCOPE_MISMATCH, "exact required scope tuple required"))
        if value.expression_purpose_refs != requirement.required_expression_purpose_refs: issues.append(_issue("authority_record.expression_purpose_refs", Code.AUTHORITY_PURPOSE_MISMATCH, "exact required purpose tuple required"))
        if not set(requirement.required_predecessor_receipt_refs).issubset(value.predecessor_receipt_refs): issues.append(_issue("authority_record.predecessor_receipt_refs", Code.AUTHORITY_RECEIPT_MISMATCH, "all required predecessor receipts required"))
        if not set(requirement.required_version_refs).issubset(value.version_refs): issues.append(_issue("authority_record.version_refs", Code.AUTHORITY_VERSION_MISMATCH, "all required versions required"))
    try:
        if value.authority_record_id != expected_record_id(value): issues.append(_issue("authority_record.authority_record_id", Code.IDENTITY_MISMATCH, "deterministic identity mismatch"))
    except Exception as exc: issues.append(_issue("authority_record.authority_record_id", Code.IDENTITY_MISMATCH, str(exc)))
    return _report(issues)

def _expected_source(closeout: DisabledSelectedMeaningCloseoutResult) -> dict[str, Any]:
    integration_input = closeout.integration_input
    integration_result = closeout.integration_result
    assert integration_input is not None and integration_result is not None
    package = integration_input.selected_meaning_package
    return {
        "slice41e_integration_input_ref": integration_input.integration_input_id,
        "slice41e_integration_result_ref": integration_result.result_id,
        "slice41e_integration_receipt_ref": integration_result.receipt.receipt_id,
        "source_manifest_ref": integration_result.source_manifest.manifest_id,
        "successor_manifest_ref": integration_result.successor_manifest.manifest_id,
        "selected_governed_meaning_ref": integration_result.integrated_selected_meaning_record.record_id,
        "selected_candidate_ref": package.selected_candidate_record.record_id,
        "selection_authority_reference_ref": integration_result.authority_reference_record.record_id,
        "selection_eligibility_result_ref": package.eligibility_result_ref,
        "selection_decision_ref": package.decision_record.decision_id,
        "selection_trace_ref": package.selection_trace.trace_id,
        "selection_receipt_ref": package.selection_receipt.receipt_id,
        "content_proof_ref": package.content_proof.proof_id,
        "slice41f_acceptance_record_ref": closeout.acceptance_record.record_id,
        "preserved_alternative_refs": tuple(item.preservation_id for item in package.preserved_alternatives),
        "unresolved_alternative_refs": package.unresolved_alternative_refs,
        "ambiguity_ancestry_refs": package.ambiguity_ancestry_refs,
        "clarification_ancestry_refs": package.clarification_ancestry_refs,
        "inherited_limitation_refs": package.inherited_limitation_refs,
        "blocked_consequence_refs": package.blocked_consequence_refs,
        "refusal_relevant_refs": package.refusal_relevant_refs,
        "authority_sensitive_distinction_refs": package.authority_sensitive_distinction_refs,
        "preservation_class_refs": tuple(item.value for item in package.selected_meaning_record.preservation_classes),
    }

def validate_evaluation_input(value: Any) -> Report:
    if type(value) is not ExpressionEligibilityEvaluationInput:
        return _report([_issue("evaluation_input", Code.TYPE_MISMATCH, "exact ExpressionEligibilityEvaluationInput required")])
    issues: list[Issue] = []
    issues.extend(_id(value.evaluation_input_id, "evaluation_input.evaluation_input_id"))
    for name in ("evaluation_reason_refs", "trace_refs", "provenance_refs", "version_refs"):
        issues.extend(_ids(getattr(value, name), f"evaluation_input.{name}", allow_empty=False))
    if value.schema_version != SLICE42C_SCHEMA_VERSION: issues.append(_issue("evaluation_input.schema_version", Code.INVALID_VERSION, "unknown Slice 42C schema version"))
    for name in ("selected_meaning_alone_claimed_sufficient", "authority_inference_requested", "record_repair_requested", "scope_expansion_requested", "purpose_expansion_requested", "refusal_softening_requested", "unresolved_resolution_requested", "blocked_consequence_erasure_requested", "downstream_authority_requested"):
        if getattr(value, name) is not False: issues.append(_issue(f"evaluation_input.{name}", Code.DOWNSTREAM_AUTHORITY, "prohibited request must be false"))
    closeout = value.selected_meaning_closeout_result
    if type(closeout) is not DisabledSelectedMeaningCloseoutResult:
        issues.append(_issue("evaluation_input.selected_meaning_closeout_result", Code.TYPE_MISMATCH, "exact Slice 41F result required"))
    else:
        try: assert_valid_slice41f_result(closeout)
        except Exception as exc: issues.append(_issue("evaluation_input.selected_meaning_closeout_result", Code.RECORD_INVALID, str(exc)))
        if closeout.status is not Slice41CloseoutStatus.COMPLETED: issues.append(_issue("evaluation_input.selected_meaning_closeout_result.status", Code.SELECTED_MEANING_CHAIN_MISMATCH, "completed Slice 41F closeout required"))
        if closeout.outward_expression_authorized is not False: issues.append(_issue("evaluation_input.selected_meaning_closeout_result.outward_expression_authorized", Code.DOWNSTREAM_AUTHORITY, "selected meaning must carry zero outward authority"))
    source = value.selected_meaning_source_custody
    if type(source) is not SelectedMeaningExpressionSourceCustodyRecord:
        issues.append(_issue("evaluation_input.selected_meaning_source_custody", Code.TYPE_MISMATCH, "exact Slice 42A source custody required"))
    else:
        for item in validate_source_custody(source).issues: issues.append(_issue("evaluation_input.selected_meaning_source_custody." + item.path, Code.RECORD_INVALID, item.detail))
        if type(closeout) is DisabledSelectedMeaningCloseoutResult and closeout.status is Slice41CloseoutStatus.COMPLETED:
            try:
                expected = _expected_source(closeout)
                for name, expected_value in expected.items():
                    if getattr(source, name) != expected_value: issues.append(_issue(f"evaluation_input.selected_meaning_source_custody.{name}", Code.SELECTED_MEANING_CHAIN_MISMATCH, "does not match exact accepted Slice 41 chain"))
            except Exception as exc: issues.append(_issue("evaluation_input.selected_meaning_source_custody", Code.SELECTED_MEANING_CHAIN_MISMATCH, str(exc)))
    requirement = value.outward_expression_authority_requirement
    if type(requirement) is not OutwardExpressionAuthorityRequirementRecord:
        issues.append(_issue("evaluation_input.outward_expression_authority_requirement", Code.TYPE_MISMATCH, "exact Slice 42A requirement required"))
    else:
        for item in validate_authority_requirement(requirement).issues: issues.append(_issue("evaluation_input.outward_expression_authority_requirement." + item.path, Code.RECORD_INVALID, item.detail))
        if type(source) is SelectedMeaningExpressionSourceCustodyRecord and requirement.selected_meaning_source_custody_ref != source.source_custody_id: issues.append(_issue("evaluation_input.outward_expression_authority_requirement.selected_meaning_source_custody_ref", Code.AUTHORITY_REQUIREMENT_MISMATCH, "source custody reference mismatch"))
    bundle = value.outward_expression_governance_bundle
    if type(bundle) is not OutwardExpressionGovernanceBundle:
        issues.append(_issue("evaluation_input.outward_expression_governance_bundle", Code.TYPE_MISMATCH, "exact Slice 42B governance bundle required"))
    else:
        for item in validate_governance_bundle(bundle).issues: issues.append(_issue("evaluation_input.outward_expression_governance_bundle." + item.path, Code.RECORD_INVALID, item.detail))
        if bundle.lifecycle_record.stage is not OutwardExpressionLifecycleStage.RECORD_SEALED: issues.append(_issue("evaluation_input.outward_expression_governance_bundle.lifecycle_record.stage", Code.GOVERNANCE_NOT_SEALED, "record_sealed lifecycle required"))
        runtime = bundle.runtime_schema_record
        if type(source) is SelectedMeaningExpressionSourceCustodyRecord and runtime.selected_meaning_source_custody != source: issues.append(_issue("evaluation_input.outward_expression_governance_bundle.runtime_schema_record.selected_meaning_source_custody", Code.GOVERNANCE_BUNDLE_MISMATCH, "bundle source custody mismatch"))
        if type(requirement) is OutwardExpressionAuthorityRequirementRecord and runtime.outward_expression_authority_requirement != requirement: issues.append(_issue("evaluation_input.outward_expression_governance_bundle.runtime_schema_record.outward_expression_authority_requirement", Code.GOVERNANCE_BUNDLE_MISMATCH, "bundle authority requirement mismatch"))
        if bundle.structural_validity_grants_expression_authority or bundle.selected_meaning_chain_admitted or bundle.outward_expression_authority_admitted or bundle.expression_eligibility_evaluated: issues.append(_issue("evaluation_input.outward_expression_governance_bundle", Code.DOWNSTREAM_AUTHORITY, "Slice 42B bundle must remain validation-only"))
    if type(requirement) is OutwardExpressionAuthorityRequirementRecord:
        issues.extend(validate_authority_record(value.outward_expression_authority_record, requirement=requirement).issues)
    else: issues.extend(validate_authority_record(value.outward_expression_authority_record).issues)
    try:
        if value.evaluation_input_id != expected_record_id(value): issues.append(_issue("evaluation_input.evaluation_input_id", Code.IDENTITY_MISMATCH, "deterministic identity mismatch"))
    except Exception as exc: issues.append(_issue("evaluation_input.evaluation_input_id", Code.IDENTITY_MISMATCH, str(exc)))
    return _report(issues)

def validate_admission_record(value: Any, *, evaluation_input: ExpressionEligibilityEvaluationInput | None=None) -> Report:
    if type(value) is not AuthorizedMeaningAdmissionRecord: return _report([_issue("admission_record", Code.TYPE_MISMATCH, "exact admission record required")])
    issues: list[Issue] = []
    try:
        if value.admission_record_id != expected_record_id(value): issues.append(_issue("admission_record.admission_record_id", Code.IDENTITY_MISMATCH, "deterministic identity mismatch"))
    except Exception as exc: issues.append(_issue("admission_record.admission_record_id", Code.IDENTITY_MISMATCH, str(exc)))
    if value.exact_selected_meaning_chain_admitted is not True: issues.append(_issue("admission_record.exact_selected_meaning_chain_admitted", Code.SELECTED_MEANING_CHAIN_MISMATCH, "exact chain admission required"))
    if value.selected_meaning_alone_sufficient or value.structural_validity_grants_expression_authority or value.authority_inferred or value.record_repaired_or_substituted: issues.append(_issue("admission_record", Code.DOWNSTREAM_AUTHORITY, "admission cannot infer or manufacture authority"))
    if evaluation_input is not None:
        source = evaluation_input.selected_meaning_source_custody; req = evaluation_input.outward_expression_authority_requirement; auth = evaluation_input.outward_expression_authority_record; closeout = evaluation_input.selected_meaning_closeout_result; bundle = evaluation_input.outward_expression_governance_bundle
        exact = {
            "evaluation_input_ref": evaluation_input.evaluation_input_id, "slice41f_closeout_result_ref": closeout.result_id,
            "slice41f_acceptance_record_ref": closeout.acceptance_record.record_id, "slice41e_integration_input_ref": source.slice41e_integration_input_ref,
            "slice41e_integration_result_ref": source.slice41e_integration_result_ref, "slice41e_integration_receipt_ref": source.slice41e_integration_receipt_ref,
            "selected_meaning_source_custody_ref": source.source_custody_id, "outward_expression_authority_requirement_ref": req.authority_requirement_id,
            "outward_expression_governance_bundle_ref": bundle.bundle_id, "explicit_outward_expression_authority_record_ref": auth.authority_record_id,
            "selected_governed_meaning_ref": source.selected_governed_meaning_ref, "selected_candidate_ref": source.selected_candidate_ref,
            "selection_receipt_ref": source.selection_receipt_ref, "preserved_alternative_refs": source.preserved_alternative_refs,
            "unresolved_alternative_refs": source.unresolved_alternative_refs, "blocked_consequence_refs": source.blocked_consequence_refs,
            "refusal_relevant_refs": source.refusal_relevant_refs,
        }
        for name, expected in exact.items():
            if getattr(value, name) != expected: issues.append(_issue(f"admission_record.{name}", Code.SELECTED_MEANING_CHAIN_MISMATCH, "cross-record reference mismatch"))
        expected_authority = auth.authority_active and auth.eligibility_evaluation_authorized
        if value.exact_outward_expression_authority_admitted is not expected_authority: issues.append(_issue("admission_record.exact_outward_expression_authority_admitted", Code.AUTHORITY_RECORD_MISMATCH, "authority admission flag mismatch"))
    return _report(issues)

def validate_result(value: Any, *, evaluation_input: ExpressionEligibilityEvaluationInput | None=None) -> Report:
    if type(value) is not ExpressionEligibilityResult: return _report([_issue("result", Code.TYPE_MISMATCH, "exact ExpressionEligibilityResult required")])
    issues: list[Issue] = []
    if evaluation_input is not None:
        issues.extend(validate_evaluation_input(evaluation_input).issues)
        issues.extend(validate_admission_record(value.admission_record, evaluation_input=evaluation_input).issues)
        if value.evaluation_input_ref != evaluation_input.evaluation_input_id: issues.append(_issue("result.evaluation_input_ref", Code.IDENTITY_MISMATCH, "input reference mismatch"))
        if value.authority_record_ref != evaluation_input.outward_expression_authority_record.authority_record_id: issues.append(_issue("result.authority_record_ref", Code.AUTHORITY_RECORD_MISMATCH, "authority record reference mismatch"))
    outcome_flags = {
        ExpressionEligibilityOutcome.ELIGIBLE_FOR_EXPRESSION_PLANNING: "eligible_for_expression_planning",
        ExpressionEligibilityOutcome.HELD_PENDING_AUTHORITY: "held_pending_authority",
        ExpressionEligibilityOutcome.BLOCKED: "blocked",
        ExpressionEligibilityOutcome.REFUSAL_PRESERVING: "refusal_preserving",
        ExpressionEligibilityOutcome.UNRESOLVED_PRESERVING: "unresolved_preserving",
        ExpressionEligibilityOutcome.INDETERMINATE: "indeterminate",
    }
    for outcome, name in outcome_flags.items():
        expected = value.outcome is outcome
        if getattr(value, name) is not expected: issues.append(_issue(f"result.{name}", Code.OUTCOME_MISMATCH, "exclusive outcome flag mismatch"))
    if not value.eligibility_evaluated or not value.selected_meaning_chain_admitted: issues.append(_issue("result", Code.OUTCOME_MISMATCH, "validated result must record evaluation and exact chain admission"))
    downstream = ("preservation_obligations_projected", "governed_outward_meaning_created", "expression_plan_created", "expression_candidate_created", "human_readable_text_produced", "msm_v1_modified_or_integrated", "echo_validation_performed", "bootstrap_integration_enabled", "delivered", "truth_determined", "evidence_validated", "permission_granted", "execution_authorized", "route_or_api_created", "tool_invoked", "action_performed", "memory_accessed_or_written", "filesystem_or_network_accessed", "external_resource_loaded", "model_or_similarity_authority_used", "gp014_superseded")
    for name in downstream:
        if getattr(value, name) is not False: issues.append(_issue(f"result.{name}", Code.DOWNSTREAM_AUTHORITY, "Slice 42C downstream authority must remain false"))
    if value.selected_meaning_alone_sufficient or value.structural_validity_grants_expression_authority: issues.append(_issue("result", Code.DOWNSTREAM_AUTHORITY, "selected meaning or structural validity cannot grant expression authority"))
    try:
        if value.result_digest != expected_result_digest(value): issues.append(_issue("result.result_digest", Code.CANONICAL_MISMATCH, "result digest mismatch"))
        if value.result_id != expected_result_id(value): issues.append(_issue("result.result_id", Code.IDENTITY_MISMATCH, "result identity mismatch"))
    except Exception as exc: issues.append(_issue("result.identity", Code.CANONICAL_MISMATCH, str(exc)))
    ids = [value.admission_record.admission_record_id, *(item.finding_id for item in value.findings)]
    if len(ids) != len(set(ids)): issues.append(_issue("result.findings", Code.DUPLICATE_ID, "duplicate admission or finding identity"))
    return _report(issues)

def assert_valid_evaluation_input(value: ExpressionEligibilityEvaluationInput) -> None:
    report = validate_evaluation_input(value)
    if not report.ok: raise ExpressionEligibilityValidationError(report)

def assert_valid_result(value: ExpressionEligibilityResult, *, evaluation_input: ExpressionEligibilityEvaluationInput | None=None) -> None:
    report = validate_result(value, evaluation_input=evaluation_input)
    if not report.ok: raise ExpressionEligibilityValidationError(report)

__all__ = ("assert_valid_evaluation_input", "assert_valid_result", "validate_admission_record", "validate_authority_record", "validate_evaluation_input", "validate_result")
