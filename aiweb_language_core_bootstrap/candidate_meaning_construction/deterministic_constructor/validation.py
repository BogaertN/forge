"""Fail-closed Slice 39F validation."""

from __future__ import annotations

from dataclasses import fields

from ..candidate_semantic_content import validate_assembly
from ..candidate_set_preservation import validate_member, validate_preservation_result
from ..predecessor_custody import validate_custody
from ..governed_lifecycle import (
    validate_alternative_reference,
    validate_construction_receipt,
    validate_content_record,
    validate_identity_record,
    validate_state_record,
)
from .authority import (
    SLICE39F_PERMANENT_BOUNDARIES,
    SLICE39F_PROFILE_VERSION,
    SLICE39F_PROHIBITED_AUTHORITY,
    SLICE39F_REQUIRED_PATH,
    SLICE39F_SCHEMA_VERSION,
)
from .identity import (
    expected_constructed_record_id,
    expected_profile_id,
    expected_result_digest,
    expected_result_id,
)
from .schema import (
    CandidateMeaningConstructedRecord,
    CandidateMeaningConstructorProfile,
    CandidateMeaningConstructorResult,
    CandidateMeaningConstructorStatus,
    CandidateMeaningConstructorValidationCode,
    CandidateMeaningConstructorValidationError,
    CandidateMeaningConstructorValidationIssue,
    CandidateMeaningConstructorValidationReport,
)


def _issue(path: str, code: CandidateMeaningConstructorValidationCode, detail: str) -> CandidateMeaningConstructorValidationIssue:
    return CandidateMeaningConstructorValidationIssue(path, code, detail)


def validate_profile(record: object) -> CandidateMeaningConstructorValidationReport:
    issues: list[CandidateMeaningConstructorValidationIssue] = []
    if type(record) is not CandidateMeaningConstructorProfile:
        return CandidateMeaningConstructorValidationReport((_issue("profile", CandidateMeaningConstructorValidationCode.TYPE_MISMATCH, "exact CandidateMeaningConstructorProfile required"),))
    assert isinstance(record, CandidateMeaningConstructorProfile)
    if record.profile_version != SLICE39F_PROFILE_VERSION:
        issues.append(_issue("profile.profile_version", CandidateMeaningConstructorValidationCode.PROFILE_MISMATCH, "profile version mismatch"))
    if record.required_path != SLICE39F_REQUIRED_PATH or record.permanent_boundaries != SLICE39F_PERMANENT_BOUNDARIES or record.prohibited_authority != SLICE39F_PROHIBITED_AUTHORITY:
        issues.append(_issue("profile", CandidateMeaningConstructorValidationCode.PROFILE_MISMATCH, "sealed authority inventory mismatch"))
    true_fields = ("explicitly_invoked", "exact_input_types_required", "offline_only", "standard_library_only", "read_only", "deterministic", "in_memory_only", "source_preserving", "fail_closed")
    false_fields = ("raw_text_inspection_allowed", "similarity_allowed", "nearest_known_fallback_allowed", "hidden_repair_allowed", "ranking_allowed", "selection_allowed", "ambiguity_resolution_allowed", "gate_outcome_allowed", "manifest_integration_allowed", "bootstrap_integration_allowed", "truth_evidence_permission_allowed", "route_action_memory_rendering_delivery_allowed")
    for name in true_fields:
        if getattr(record, name) is not True:
            issues.append(_issue(f"profile.{name}", CandidateMeaningConstructorValidationCode.PROFILE_MISMATCH, "must be true"))
    for name in false_fields:
        if getattr(record, name) is not False:
            issues.append(_issue(f"profile.{name}", CandidateMeaningConstructorValidationCode.PROFILE_MISMATCH, "must be false"))
    if record.schema_version != SLICE39F_SCHEMA_VERSION or record.profile_id != expected_profile_id(record):
        issues.append(_issue("profile.profile_id", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "deterministic profile identity mismatch"))
    return CandidateMeaningConstructorValidationReport(tuple(issues))


def validate_constructed_record(record: object) -> CandidateMeaningConstructorValidationReport:
    issues: list[CandidateMeaningConstructorValidationIssue] = []
    if type(record) is not CandidateMeaningConstructedRecord:
        return CandidateMeaningConstructorValidationReport((_issue("constructed_record", CandidateMeaningConstructorValidationCode.TYPE_MISMATCH, "exact CandidateMeaningConstructedRecord required"),))
    assert isinstance(record, CandidateMeaningConstructedRecord)
    state = record.candidate_meaning_state
    if not validate_custody(record.predecessor_custody).ok:
        issues.append(_issue("predecessor_custody", CandidateMeaningConstructorValidationCode.PREDECESSOR_REJECTED, "Slice 39C custody validation failed"))
    if not validate_assembly(record.semantic_content_assembly).ok:
        issues.append(_issue("semantic_content_assembly", CandidateMeaningConstructorValidationCode.CONTENT_ASSEMBLY_REJECTED, "Slice 39D assembly validation failed"))
    if not validate_member(record.candidate_set_member).ok:
        issues.append(_issue("candidate_set_member", CandidateMeaningConstructorValidationCode.CANDIDATE_SET_REJECTED, "Slice 39E member validation failed"))
    if state.provenance != record.predecessor_custody.provenance:
        issues.append(_issue("provenance", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "state provenance must equal exact Slice 39C provenance"))
    if state.content != record.semantic_content_assembly.candidate_meaning_content:
        issues.append(_issue("content", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "state content must equal exact Slice 39D content"))
    if record.candidate_result_id != record.candidate_set_member.candidate_result_id:
        issues.append(_issue("candidate_result_id", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "record/member candidate result mismatch"))
    for report, path in (
        (validate_content_record(state.content), "content"),
        (validate_identity_record(state.identity, content=state.content, provenance=state.provenance), "identity"),
        (validate_construction_receipt(record.construction_receipt, identity=state.identity, content=state.content, provenance=state.provenance), "receipt"),
        (validate_state_record(state), "state"),
    ):
        if not report.ok:
            issues.append(_issue(path, CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "accepted Slice 39B validation failed"))
    for alternative in state.alternative_references:
        report = validate_alternative_reference(alternative, candidate_meaning_id=state.identity.candidate_meaning_id)
        if not report.ok:
            issues.append(_issue("alternative_references", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "alternative validation failed"))
    if state.construction_receipt != record.construction_receipt:
        issues.append(_issue("construction_receipt", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "state/record receipt mismatch"))
    if record.record_id != expected_constructed_record_id(record):
        issues.append(_issue("record_id", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "constructed record identity mismatch"))
    if record.deterministic_position < 1 or record.duplicate_occurrence_count < 1:
        issues.append(_issue("deterministic_position", CandidateMeaningConstructorValidationCode.COUNT_MISMATCH, "positive counts required"))
    for name in ("exact_typed_predecessors_verified", "exact_ancestry_verified", "exact_snapshots_verified", "source_preserved"):
        if getattr(record, name) is not True:
            issues.append(_issue(name, CandidateMeaningConstructorValidationCode.PREDECESSOR_REJECTED, "verification flag must be true"))
    return CandidateMeaningConstructorValidationReport(tuple(issues))


def validate_result(record: object) -> CandidateMeaningConstructorValidationReport:
    issues: list[CandidateMeaningConstructorValidationIssue] = []
    if type(record) is not CandidateMeaningConstructorResult:
        return CandidateMeaningConstructorValidationReport((_issue("result", CandidateMeaningConstructorValidationCode.TYPE_MISMATCH, "exact CandidateMeaningConstructorResult required"),))
    assert isinstance(record, CandidateMeaningConstructorResult)
    if not validate_profile(record.profile).ok:
        issues.append(_issue("profile", CandidateMeaningConstructorValidationCode.PROFILE_MISMATCH, "profile validation failed"))
    if not validate_preservation_result(record.candidate_set_result).ok:
        issues.append(_issue("candidate_set_result", CandidateMeaningConstructorValidationCode.CANDIDATE_SET_REJECTED, "Slice 39E validation failed"))
    if record.status is CandidateMeaningConstructorStatus.REJECTED:
        if not record.issues or record.constructed_records or record.construction_receipts:
            issues.append(_issue("result", CandidateMeaningConstructorValidationCode.COUNT_MISMATCH, "rejected result must preserve issues and no constructed records"))
    else:
        if record.issues:
            issues.append(_issue("issues", CandidateMeaningConstructorValidationCode.COUNT_MISMATCH, "successful result cannot contain issues"))
        if len(record.constructed_records) != record.unique_candidate_count or len(record.construction_receipts) != record.unique_candidate_count:
            issues.append(_issue("unique_candidate_count", CandidateMeaningConstructorValidationCode.COUNT_MISMATCH, "constructed count mismatch"))
        if record.status is CandidateMeaningConstructorStatus.ZERO_CANDIDATES and record.unique_candidate_count != 0:
            issues.append(_issue("status", CandidateMeaningConstructorValidationCode.COUNT_MISMATCH, "zero status requires zero candidates"))
        if record.status is CandidateMeaningConstructorStatus.CONSTRUCTED and record.unique_candidate_count < 1:
            issues.append(_issue("status", CandidateMeaningConstructorValidationCode.COUNT_MISMATCH, "constructed status requires candidates"))
        for item in record.constructed_records:
            if not validate_constructed_record(item).ok:
                issues.append(_issue("constructed_records", CandidateMeaningConstructorValidationCode.IDENTITY_MISMATCH, "constructed record validation failed"))
    required_true = ("explicitly_invoked", "offline", "standard_library_only", "read_only", "deterministic", "in_memory_only", "fail_closed")
    if record.status is not CandidateMeaningConstructorStatus.REJECTED:
        required_true += ("exact_input_types_verified", "exact_ancestry_verified", "exact_snapshots_verified", "source_preserved")
    required_false = ("raw_text_inspected", "similarity_used", "nearest_known_fallback_used", "hidden_repair_used", "candidate_ranked", "candidate_selected", "ambiguity_resolved", "gate_outcome_created", "selected_meaning_created", "truth_determined", "evidence_validated", "permission_granted", "route_created", "action_performed", "memory_accessed", "rendered", "delivered", "filesystem_read_performed", "filesystem_write_performed", "network_access_performed", "external_resource_loaded", "language_model_used", "embedding_used", "vector_used", "rag_used", "semantic_similarity_used", "manifest_integrated", "bootstrap_integrated", "slice39_closeout_created")
    for name in required_true:
        if getattr(record, name) is not True:
            issues.append(_issue(name, CandidateMeaningConstructorValidationCode.DOWNSTREAM_AUTHORITY, "required constructor boundary flag must be true"))
    for name in required_false:
        if getattr(record, name) is not False:
            issues.append(_issue(name, CandidateMeaningConstructorValidationCode.DOWNSTREAM_AUTHORITY, "prohibited authority flag must be false"))
    if record.canonical_digest != expected_result_digest(record) or record.result_id != expected_result_id(record):
        issues.append(_issue("result_id", CandidateMeaningConstructorValidationCode.CANONICAL_MISMATCH, "result identity mismatch"))
    if record.schema_version != SLICE39F_SCHEMA_VERSION:
        issues.append(_issue("schema_version", CandidateMeaningConstructorValidationCode.CANONICAL_MISMATCH, "schema version mismatch"))
    return CandidateMeaningConstructorValidationReport(tuple(issues))


def assert_valid_result(record: object) -> None:
    report = validate_result(record)
    if not report.ok:
        raise CandidateMeaningConstructorValidationError(report)

__all__ = ("assert_valid_result", "validate_constructed_record", "validate_profile", "validate_result")
