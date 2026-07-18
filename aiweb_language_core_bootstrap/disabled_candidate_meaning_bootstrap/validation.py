"""Total fail-closed validators for Slice 39H records."""
from __future__ import annotations
from dataclasses import fields
from ..schema import ValidationIssue, ValidationReport, issue
from .schema import (
    SLICE39H_SCHEMA_VERSION, SLICE39H_SPEC_ID, SLICE39H_SPEC_VERSION,
    PRE_SLICE39_COMMIT, PRE_SLICE39_TREE, SLICE39G_ACCEPTED_HEAD,
    SLICE39G_ACCEPTED_TREE, SLICE39G_ACCEPTED_SUBJECT, SLICE39H_COMMIT_SUBJECT,
    SLICE39_INCREMENT_LABELS, SLICE39_ACCEPTED_CHAIN, SLICE39_PERMANENT_BOUNDARIES,
    SLICE39_PROHIBITED_AUTHORITY, SLICE39_ACCEPTED_SCOPE, SLICE39_DEFERRED_SCOPE,
    CloseoutStage, CloseoutStatus, DisabledCandidateMeaningBootstrapState,
    DisabledCandidateMeaningFixture, DisabledCandidateMeaningInvocation,
    CloseoutStageReceipt, Slice39RollbackMetadata, Slice39AcceptanceRecord,
    DisabledCandidateMeaningBootstrapResult,
)

_TRUE_STATE = (
    "disabled_by_default", "explicit_invocation_required", "accepted_static_fixture_only",
    "offline_only", "standard_library_only", "deterministic", "read_only",
    "in_memory_only", "exact_profile_bounded", "source_preserving", "rollback_safe",
)
_FALSE_STATE = (
    "automatic_activation_allowed", "arbitrary_raw_text_allowed", "filesystem_read_allowed",
    "filesystem_write_allowed", "network_allowed", "external_resource_loading_allowed",
    "model_authority_allowed", "embedding_authority_allowed", "vector_authority_allowed",
    "rag_authority_allowed", "semantic_similarity_allowed", "nearest_known_substitution_allowed",
    "hidden_intent_inference_allowed", "silent_role_filling_allowed",
    "silent_referent_resolution_allowed", "automatic_ambiguity_collapse_allowed",
    "gate_outcome_allowed", "selected_meaning_allowed", "truth_determination_allowed",
    "evidence_validation_allowed", "permission_allowed", "capability_availability_allowed",
    "route_allowed", "invocation_allowed", "memory_access_allowed", "tool_allowed",
    "action_allowed", "rendering_allowed", "delivery_allowed",
    "runtime_self_acceptance_allowed", "release_authorized", "production_ready",
)
_FALSE_RESULT = (
    "gate_outcome_created", "selected_meaning_created", "truth_determined",
    "evidence_validated", "permission_granted", "capability_availability_created",
    "route_created", "invocation_created", "memory_accessed", "tool_invoked",
    "action_performed", "rendered", "delivered", "filesystem_read_performed",
    "filesystem_write_performed", "network_access_performed", "external_resource_loaded",
    "language_model_used", "model_authority_used", "embedding_used", "vector_used",
    "rag_used", "semantic_similarity_used", "nearest_known_substitution_used",
    "hidden_intent_inference_used", "silent_role_filling_used",
    "silent_referent_resolution_used", "automatic_ambiguity_collapse_used",
    "technical_acceptance_granted_by_runtime", "release_authorized", "production_ready",
)

def _report(issues: list[ValidationIssue]) -> ValidationReport:
    return ValidationReport(schema_version=SLICE39H_SCHEMA_VERSION, ok=not issues, issues=tuple(issues))

def _safe(fn, value: object) -> ValidationReport:
    try:
        return fn(value)
    except Exception as exc:
        return _report([issue("record", "validator_failed_closed", type(exc).__name__)])

def _id(issues: list[ValidationIssue], value: object, field: str) -> None:
    if getattr(value, field, None) != value.expected_id():
        issues.append(issue(field, "identity_mismatch"))

def _schema(issues: list[ValidationIssue], value: object) -> None:
    if getattr(value, "schema_version", None) != SLICE39H_SCHEMA_VERSION:
        issues.append(issue("schema_version", "version_mismatch"))

def _bools(issues: list[ValidationIssue], value: object, names: tuple[str, ...], expected: bool) -> None:
    for name in names:
        if getattr(value, name, None) is not expected:
            issues.append(issue(name, "must_remain_true" if expected else "must_remain_false"))

def _validate_state(value: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(value) is not DisabledCandidateMeaningBootstrapState:
        return _report([issue("record", "type_mismatch")])
    _schema(issues, value); _id(issues, value, "state_id")
    if value.enabled is not value.explicit_offline_developer_enable:
        issues.append(issue("enabled", "enablement_mismatch"))
    if value.spec_id != SLICE39H_SPEC_ID or value.spec_version != SLICE39H_SPEC_VERSION:
        issues.append(issue("spec", "version_mismatch"))
    _bools(issues, value, _TRUE_STATE, True); _bools(issues, value, _FALSE_STATE, False)
    return _report(issues)

def validate_integration_state(value: object) -> ValidationReport: return _safe(_validate_state, value)

def _validate_fixture(value: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(value) is not DisabledCandidateMeaningFixture:
        return _report([issue("record", "type_mismatch")])
    _schema(issues, value); _id(issues, value, "fixture_id")
    for name in ("fixture_name", "exact_source_text", "source_id", "channel_id", "expected_constructor_status", "expected_manifest_status"):
        if type(getattr(value, name, None)) is not str or not getattr(value, name).strip(): issues.append(issue(name, "required_non_empty_text"))
    if type(value.sequence_number) is not int or value.sequence_number < 1: issues.append(issue("sequence_number", "invalid_integer"))
    if type(value.expected_unique_candidate_count) is not int or value.expected_unique_candidate_count < 0: issues.append(issue("expected_unique_candidate_count", "invalid_integer"))
    if type(value.expected_manifest_candidate_count) is not int or value.expected_manifest_candidate_count < 0: issues.append(issue("expected_manifest_candidate_count", "invalid_integer"))
    _bools(issues, value, ("accepted_fixture", "synthetic", "explicit_invocation_only", "offline_only", "in_memory_only", "raw_text_not_carried_by_invocation"), True)
    return _report(issues)

def validate_fixture(value: object) -> ValidationReport: return _safe(_validate_fixture, value)

def _validate_invocation(value: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(value) is not DisabledCandidateMeaningInvocation: return _report([issue("record", "type_mismatch")])
    _schema(issues, value); _id(issues, value, "invocation_id")
    if not value.fixture_name or not value.fixture_id or not value.requested_operation: issues.append(issue("invocation", "required_non_empty_text"))
    _bools(issues, value, ("explicit_invocation",), True); _bools(issues, value, ("raw_text_carried_by_invocation",), False)
    return _report(issues)

def validate_invocation(value: object) -> ValidationReport: return _safe(_validate_invocation, value)

def _validate_receipt(value: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(value) is not CloseoutStageReceipt: return _report([issue("record", "type_mismatch")])
    _schema(issues, value); _id(issues, value, "receipt_id")
    if type(value.stage_ordinal) is not int or not 1 <= value.stage_ordinal <= 4: issues.append(issue("stage_ordinal", "out_of_range"))
    if type(value.stage) is not CloseoutStage: issues.append(issue("stage", "type_mismatch"))
    if not value.output_record_id or not value.output_schema_version or not value.output_exact_type: issues.append(issue("output", "required_non_empty_text"))
    _bools(issues, value, ("output_validation_passed", "source_preserved", "candidate_only"), True)
    _bools(issues, value, ("gate_outcome_created", "selected_meaning_created", "truth_determined", "evidence_validated", "permission_granted", "route_created", "invocation_created", "memory_accessed", "tool_invoked", "action_performed", "rendered", "delivered"), False)
    return _report(issues)

def validate_stage_receipt(value: object) -> ValidationReport: return _safe(_validate_receipt, value)

def _validate_rollback(value: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(value) is not Slice39RollbackMetadata: return _report([issue("record", "type_mismatch")])
    _schema(issues, value); _id(issues, value, "rollback_id")
    exact = (value.pre_slice39_commit == PRE_SLICE39_COMMIT and value.pre_slice39_tree == PRE_SLICE39_TREE and value.accepted_parent_head == SLICE39G_ACCEPTED_HEAD and value.accepted_parent_tree == SLICE39G_ACCEPTED_TREE and value.accepted_parent_subject == SLICE39G_ACCEPTED_SUBJECT and value.expected_closeout_commit_subject == SLICE39H_COMMIT_SUBJECT)
    if not exact: issues.append(issue("rollback_identity", "mismatch"))
    _bools(issues, value, ("exact_commit_checkout_required", "exact_tree_match_required", "separate_recovery_clone_required", "exact_staged_path_containment_required", "git_object_verification_required", "rollback_proof_external_to_runtime"), True)
    _bools(issues, value, ("live_repository_mutation_authorized", "runtime_rollback_execution_authorized"), False)
    return _report(issues)

def validate_rollback_metadata(value: object) -> ValidationReport: return _safe(_validate_rollback, value)

def _validate_acceptance(value: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(value) is not Slice39AcceptanceRecord: return _report([issue("record", "type_mismatch")])
    _schema(issues, value); _id(issues, value, "acceptance_record_id")
    if value.accepted_increment_labels != SLICE39_INCREMENT_LABELS or value.accepted_chain != SLICE39_ACCEPTED_CHAIN: issues.append(issue("accepted_chain", "mismatch"))
    if value.permanent_boundaries != SLICE39_PERMANENT_BOUNDARIES or value.prohibited_authority != SLICE39_PROHIBITED_AUTHORITY: issues.append(issue("boundaries", "mismatch"))
    if value.accepted_scope != SLICE39_ACCEPTED_SCOPE or value.deferred_scope != SLICE39_DEFERRED_SCOPE: issues.append(issue("scope", "mismatch"))
    _bools(issues, value, ("disabled_by_default", "explicitly_invoked_only", "fixture_only", "offline_only", "deterministic", "read_only", "in_memory_only", "exact_profile_bounded", "source_preserving", "zero_candidate_reproducibility_required", "one_candidate_reproducibility_required", "multi_candidate_reproducibility_required", "missing_role_preservation_required", "unknown_concept_preservation_required", "unknown_predicate_preservation_required", "conflicting_role_preservation_required", "exact_staged_path_containment_required", "pre_slice39_recovery_required", "no_selected_meaning_authority", "no_gate_outcome_authority", "no_permission_or_execution_authority", "decision_owner_acceptance_required"), True)
    _bools(issues, value, ("runtime_self_grants_acceptance", "release_authorized", "production_ready"), False)
    return _report(issues)

def validate_acceptance_record(value: object) -> ValidationReport: return _safe(_validate_acceptance, value)

def _validate_result(value: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(value) is not DisabledCandidateMeaningBootstrapResult: return _report([issue("record", "type_mismatch")])
    _schema(issues, value); _id(issues, value, "result_id")
    if value.stage_receipt_count != len(value.stage_receipts): issues.append(issue("stage_receipt_count", "count_mismatch"))
    for index, receipt in enumerate(value.stage_receipts):
        report = validate_stage_receipt(receipt)
        for item in report.issues: issues.append(issue(f"stage_receipts[{index}].{item.field}", item.code, item.detail))
    if not validate_acceptance_record(value.acceptance_record).ok: issues.append(issue("acceptance_record", "invalid"))
    if not validate_rollback_metadata(value.rollback_metadata).ok: issues.append(issue("rollback_metadata", "invalid"))
    _bools(issues, value, ("disabled_by_default", "fixture_only", "offline_only", "standard_library_only", "deterministic", "read_only", "in_memory_only", "exact_profile_bounded", "rollback_safe"), True)
    _bools(issues, value, _FALSE_RESULT, False)
    if value.status is CloseoutStatus.REFUSED_DISABLED:
        if value.stage_receipts or value.constructor_result is not None or value.manifest_integration_result is not None: issues.append(issue("status", "disabled_result_must_be_empty"))
    elif value.status.value.startswith("COMPLETED"):
        if value.stage_receipt_count != 4 or not value.exact_stage_chain_complete: issues.append(issue("stage_receipts", "complete_chain_required"))
        if value.constructor_result is None or value.manifest_integration_result is None: issues.append(issue("outputs", "required"))
        if not value.explicitly_invoked or not value.source_preserved: issues.append(issue("execution", "explicit_source_preserved_required"))
    return _report(issues)

def validate_integration_result(value: object) -> ValidationReport: return _safe(_validate_result, value)

PUBLIC_VALIDATORS = (validate_integration_state, validate_fixture, validate_invocation, validate_stage_receipt, validate_rollback_metadata, validate_acceptance_record, validate_integration_result)
__all__ = tuple(fn.__name__ for fn in PUBLIC_VALIDATORS) + ("PUBLIC_VALIDATORS",)
