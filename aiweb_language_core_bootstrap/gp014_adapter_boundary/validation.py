"""Deterministic validation for Slice 45 adapter records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .authority import (
    ADAPTER_SCOPE,
    GP014_ALLOWED_SOURCE_STATUSES,
    GP014_BUILD_ID,
    GP014_EXPRESSION_LEXICON_AUTHORITY_CLASS,
    GP014_REALIZER_SCHEMA_VERSION,
    GP014_SUPPORTED_OPERATION_FAMILIES,
    MAX_QUESTION_CHARACTERS,
    REQUESTED_OPERATION,
    SLICE45_SCHEMA_VERSION,
    STATUS_COMPLETED_ANSWERED,
    STATUS_COMPLETED_CONTAINED,
    STATUS_CONTAINED_SOURCE_FAILURE,
    STATUS_HELD_GP014_IDENTITY,
    STATUS_HELD_GP014_RESULT,
    STATUS_HELD_INVALID_REQUEST,
    STATUS_HELD_INVALID_STATE,
    STATUS_REFUSED_DISABLED,
)
from .canonical import question_sha256
from .schema import (
    Gp014AdapterReceipt,
    Gp014AdapterRequest,
    Gp014AdapterResult,
    Gp014AdapterState,
    Gp014BindingIdentity,
)


class Slice45ValidationCode(str, Enum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_SCHEMA = "INVALID_SCHEMA"
    INVALID_ID = "INVALID_ID"
    INVALID_FIELD = "INVALID_FIELD"
    AUTHORITY_ESCALATION = "AUTHORITY_ESCALATION"
    SOURCE_MISMATCH = "SOURCE_MISMATCH"


@dataclass(frozen=True, slots=True)
class Slice45ValidationIssue:
    path: str
    code: Slice45ValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class Slice45ValidationReport:
    issues: tuple[Slice45ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


def _report(issues: list[Slice45ValidationIssue]) -> Slice45ValidationReport:
    return Slice45ValidationReport(tuple(issues))


def _issue(issues: list[Slice45ValidationIssue], path: str, code: Slice45ValidationCode, detail: str) -> None:
    issues.append(Slice45ValidationIssue(path, code, detail))


def validate_state(value: Any) -> Slice45ValidationReport:
    issues: list[Slice45ValidationIssue] = []
    if type(value) is not Gp014AdapterState:
        _issue(issues, "$", Slice45ValidationCode.INVALID_TYPE, "exact Gp014AdapterState required")
        return _report(issues)
    if value.schema_version != SLICE45_SCHEMA_VERSION:
        _issue(issues, "schema_version", Slice45ValidationCode.INVALID_SCHEMA, "unsupported schema")
    if value.state_id != value.expected_id():
        _issue(issues, "state_id", Slice45ValidationCode.INVALID_ID, "stable identity mismatch")
    for name in (
        "disabled_by_default", "explicit_invocation_required", "exact_question_forwarding_required",
        "unchanged_gp014_required", "existing_gp014_scope_only", "deterministic", "local_only",
        "adapter_read_only", "adapter_in_memory_only",
    ):
        if getattr(value, name) is not True:
            _issue(issues, name, Slice45ValidationCode.INVALID_FIELD, "must remain true")
    for name in (
        "runtime_registration_allowed", "main_registration_allowed", "route_allowed", "api_allowed",
        "ui_allowed", "network_authority_added", "filesystem_write_authority_added",
        "memory_authority_added", "evidence_authority_added", "truth_authority_added",
        "permission_authority_added", "delivery_authority_added", "tool_authority_added",
        "action_authority_added", "external_resource_authority_added", "gp014_modification_allowed",
        "gp014_supersession_allowed", "gp015_reuse_allowed", "production_ready", "release_authorized",
    ):
        if getattr(value, name) is not False:
            _issue(issues, name, Slice45ValidationCode.AUTHORITY_ESCALATION, "must remain false")
    if value.enabled is not value.explicit_offline_developer_enable:
        _issue(issues, "enabled", Slice45ValidationCode.INVALID_FIELD, "enable fields must match")
    if value.gp014_import_allowed is not value.enabled or value.gp014_call_allowed is not value.enabled:
        _issue(issues, "gp014_authority", Slice45ValidationCode.AUTHORITY_ESCALATION, "GP-014 import and call allowed only in explicit enabled state")
    return _report(issues)


def validate_request(value: Any) -> Slice45ValidationReport:
    issues: list[Slice45ValidationIssue] = []
    if type(value) is not Gp014AdapterRequest:
        _issue(issues, "$", Slice45ValidationCode.INVALID_TYPE, "exact Gp014AdapterRequest required")
        return _report(issues)
    if value.schema_version != SLICE45_SCHEMA_VERSION:
        _issue(issues, "schema_version", Slice45ValidationCode.INVALID_SCHEMA, "unsupported schema")
    if value.request_id != value.expected_id():
        _issue(issues, "request_id", Slice45ValidationCode.INVALID_ID, "stable identity mismatch")
    if not isinstance(value.question, str) or not value.question.strip() or len(value.question) > MAX_QUESTION_CHARACTERS or "\x00" in value.question:
        _issue(issues, "question", Slice45ValidationCode.INVALID_FIELD, "bounded non-empty UTF-8 question required")
    if value.question_sha256 != question_sha256(value.question):
        _issue(issues, "question_sha256", Slice45ValidationCode.INVALID_ID, "question hash mismatch")
    if value.requested_operation != REQUESTED_OPERATION or value.adapter_scope != ADAPTER_SCOPE:
        _issue(issues, "scope", Slice45ValidationCode.AUTHORITY_ESCALATION, "exact adapter scope required")
    if value.explicit_invocation is not True or value.preserve_question_byte_for_byte is not True:
        _issue(issues, "invocation", Slice45ValidationCode.INVALID_FIELD, "explicit exact forwarding required")
    for name in ("permit_normalization_or_rewrite", "permit_scope_broadening", "permit_route_or_ui_use", "permit_gp015_reuse"):
        if getattr(value, name) is not False:
            _issue(issues, name, Slice45ValidationCode.AUTHORITY_ESCALATION, "must remain false")
    return _report(issues)


def validate_binding_identity(value: Any) -> Slice45ValidationReport:
    issues: list[Slice45ValidationIssue] = []
    if type(value) is not Gp014BindingIdentity:
        _issue(issues, "$", Slice45ValidationCode.INVALID_TYPE, "exact Gp014BindingIdentity required")
        return _report(issues)
    if value.schema_version != SLICE45_SCHEMA_VERSION:
        _issue(issues, "schema_version", Slice45ValidationCode.INVALID_SCHEMA, "unsupported schema")
    if value.identity_id != value.expected_id():
        _issue(issues, "identity_id", Slice45ValidationCode.INVALID_ID, "stable identity mismatch")
    if value.build_id != GP014_BUILD_ID or value.realizer_schema_version != GP014_REALIZER_SCHEMA_VERSION:
        _issue(issues, "gp014_identity", Slice45ValidationCode.SOURCE_MISMATCH, "GP-014 build identity mismatch")
    if value.expression_lexicon_authority_class != GP014_EXPRESSION_LEXICON_AUTHORITY_CLASS:
        _issue(issues, "lexicon_authority", Slice45ValidationCode.SOURCE_MISMATCH, "lexicon authority mismatch")
    if value.supported_operation_families != GP014_SUPPORTED_OPERATION_FAMILIES:
        _issue(issues, "supported_operation_families", Slice45ValidationCode.SOURCE_MISMATCH, "operation-family scope mismatch")
    for name in ("meaning_locked_before_phrase_selection", "actual_echo_required_after_selection"):
        if getattr(value, name) is not True:
            _issue(issues, name, Slice45ValidationCode.SOURCE_MISMATCH, "required GP-014 invariant absent")
    for name in ("realizer_adds_delivery_authority", "route_or_ui_added", "corpus_ingestion_added", "llm_used", "memory_write_added", "gp015_loaded"):
        if getattr(value, name) is not False:
            _issue(issues, name, Slice45ValidationCode.AUTHORITY_ESCALATION, "prohibited source authority")
    return _report(issues)


def validate_receipt(value: Any) -> Slice45ValidationReport:
    issues: list[Slice45ValidationIssue] = []
    if type(value) is not Gp014AdapterReceipt:
        _issue(issues, "$", Slice45ValidationCode.INVALID_TYPE, "exact Gp014AdapterReceipt required")
        return _report(issues)
    if value.schema_version != SLICE45_SCHEMA_VERSION:
        _issue(issues, "schema_version", Slice45ValidationCode.INVALID_SCHEMA, "unsupported schema")
    if value.receipt_id != value.expected_id():
        _issue(issues, "receipt_id", Slice45ValidationCode.INVALID_ID, "stable identity mismatch")
    for name in ("source_status_rewritten", "source_answer_rewritten", "source_trace_mutated", "gp014_modified", "gp014_superseded", "gp015_used", "main_modified_or_called", "route_created_or_called", "api_created_or_called", "ui_created_or_called", "network_authority_added", "filesystem_write_authority_added", "memory_authority_added", "evidence_authority_added", "truth_authority_added", "permission_authority_added", "delivery_authority_added_by_adapter", "tool_authority_added", "action_authority_added", "external_resource_authority_added", "raw_exception_exposed"):
        if getattr(value, name) is not False:
            _issue(issues, name, Slice45ValidationCode.AUTHORITY_ESCALATION, "must remain false")
    return _report(issues)


def validate_result(value: Any) -> Slice45ValidationReport:
    issues: list[Slice45ValidationIssue] = []
    if type(value) is not Gp014AdapterResult:
        _issue(issues, "$", Slice45ValidationCode.INVALID_TYPE, "exact Gp014AdapterResult required")
        return _report(issues)
    if value.schema_version != SLICE45_SCHEMA_VERSION:
        _issue(issues, "schema_version", Slice45ValidationCode.INVALID_SCHEMA, "unsupported schema")
    if value.result_id != value.expected_id():
        _issue(issues, "result_id", Slice45ValidationCode.INVALID_ID, "stable identity mismatch")
    issues.extend(validate_receipt(value.receipt).issues)
    if value.binding_identity is not None:
        issues.extend(validate_binding_identity(value.binding_identity).issues)
    allowed = {
        STATUS_REFUSED_DISABLED, STATUS_HELD_INVALID_STATE, STATUS_HELD_INVALID_REQUEST,
        STATUS_HELD_GP014_IDENTITY, STATUS_HELD_GP014_RESULT, STATUS_CONTAINED_SOURCE_FAILURE,
        STATUS_COMPLETED_ANSWERED, STATUS_COMPLETED_CONTAINED,
    }
    if value.status not in allowed:
        _issue(issues, "status", Slice45ValidationCode.INVALID_FIELD, "unknown result status")
    if value.adapter_completed:
        if value.source_result is None or value.receipt.source_result_hash is None:
            _issue(issues, "source_result", Slice45ValidationCode.SOURCE_MISMATCH, "completed result requires source result")
        else:
            if not callable(getattr(value.source_result, "result_hash", None)):
                _issue(issues, "source_result", Slice45ValidationCode.INVALID_TYPE, "source result_hash unavailable")
            elif value.source_result.result_hash() != value.receipt.source_result_hash:
                _issue(issues, "source_result_hash", Slice45ValidationCode.SOURCE_MISMATCH, "source result hash mismatch")
            if getattr(value.source_result, "status", None) not in GP014_ALLOWED_SOURCE_STATUSES:
                _issue(issues, "source_status", Slice45ValidationCode.SOURCE_MISMATCH, "unexpected GP-014 source status")
    return _report(issues)


PUBLIC_VALIDATORS = (validate_state, validate_request, validate_binding_identity, validate_receipt, validate_result)
__all__ = tuple(name for name in globals() if not name.startswith("_"))
