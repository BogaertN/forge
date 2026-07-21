"""Fail-closed validation for Slice 42H closeout records."""
from __future__ import annotations

from dataclasses import replace
from enum import Enum

from .authority import (
    PRE_SLICE42_COMMIT,
    PRE_SLICE42_SUBJECT,
    PRE_SLICE42_TREE,
    REQUESTED_OPERATION,
    SLICE42_ACCEPTED_CHAIN,
    SLICE42_ACCEPTED_SCOPE,
    SLICE42_DEFERRED_SCOPE,
    SLICE42_INCREMENT_LABELS,
    SLICE42_PERMANENT_BOUNDARIES,
    SLICE42_PROHIBITED_AUTHORITY,
    SLICE42G_ACCEPTED_HEAD,
    SLICE42G_ACCEPTED_SUBJECT,
    SLICE42G_ACCEPTED_TREE,
    SLICE42H_ACCEPTANCE_RECORD_VERSION,
    SLICE42H_RECEIPT_VERSION,
    SLICE42H_ROLLBACK_METADATA_VERSION,
    SLICE42H_SCHEMA_VERSION,
)
from .canonical import deterministic_digest, stable_identifier
from .fixtures import is_exact_accepted_fixture
from .schema import (
    DisabledOutwardExpressionCloseoutResult,
    DisabledOutwardExpressionCloseoutState,
    OutwardExpressionCloseoutFixture,
    OutwardExpressionCloseoutInvocation,
    Slice42AcceptanceRecord,
    Slice42CloseoutStageReceipt,
    Slice42CloseoutStatus,
    Slice42RollbackMetadata,
)


class Slice42CloseoutValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    VERSION_MISMATCH = "version_mismatch"
    AUTHORITY_MISMATCH = "authority_mismatch"
    STATE_MISMATCH = "state_mismatch"
    FIXTURE_MISMATCH = "fixture_mismatch"
    INVOCATION_MISMATCH = "invocation_mismatch"
    PREDECESSOR_MISMATCH = "predecessor_mismatch"
    RECEIPT_MISMATCH = "receipt_mismatch"
    ACCEPTANCE_MISMATCH = "acceptance_mismatch"
    BOUNDARY_VIOLATION = "boundary_violation"
    RESULT_MISMATCH = "result_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"


class Slice42CloseoutValidationIssue(tuple):
    __slots__ = ()

    def __new__(cls, path: str, code: Slice42CloseoutValidationCode, detail: str):
        return tuple.__new__(cls, (path, code, detail))

    @property
    def path(self) -> str:
        return self[0]

    @property
    def code(self) -> Slice42CloseoutValidationCode:
        return self[1]

    @property
    def detail(self) -> str:
        return self[2]


class Slice42CloseoutValidationReport(tuple):
    __slots__ = ()

    def __new__(cls, issues: tuple[Slice42CloseoutValidationIssue, ...]):
        return tuple.__new__(cls, (issues,))

    @property
    def issues(self) -> tuple[Slice42CloseoutValidationIssue, ...]:
        return self[0]

    @property
    def ok(self) -> bool:
        return not self.issues


class Slice42CloseoutValidationError(ValueError):
    def __init__(self, report: Slice42CloseoutValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 42H validation failed")


def _report(issues: list[Slice42CloseoutValidationIssue]) -> Slice42CloseoutValidationReport:
    return Slice42CloseoutValidationReport(tuple(issues))


def _issue(
    issues: list[Slice42CloseoutValidationIssue],
    path: str,
    code: Slice42CloseoutValidationCode,
    detail: str,
) -> None:
    issues.append(Slice42CloseoutValidationIssue(path, code, detail))


def validate_state(value: object) -> Slice42CloseoutValidationReport:
    issues: list[Slice42CloseoutValidationIssue] = []
    if type(value) is not DisabledOutwardExpressionCloseoutState:
        _issue(issues, "state", Slice42CloseoutValidationCode.TYPE_MISMATCH, "exact type required")
        return _report(issues)
    expected_id = stable_identifier(
        "slice42h_disabled_closeout_state", value, excluded_fields=("state_id",)
    )
    if value.state_id != expected_id:
        _issue(issues, "state.state_id", Slice42CloseoutValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch")
    if value.schema_version != SLICE42H_SCHEMA_VERSION:
        _issue(issues, "state.schema_version", Slice42CloseoutValidationCode.VERSION_MISMATCH, "schema version mismatch")
    required_true = (
        "disabled_by_default", "explicit_invocation_required",
        "accepted_static_fixture_only", "offline_only", "read_only",
        "in_memory_only", "deterministic", "exact_profile_bounded",
        "source_preserving", "rollback_safe",
    )
    for name in required_true:
        if getattr(value, name) is not True:
            _issue(issues, f"state.{name}", Slice42CloseoutValidationCode.STATE_MISMATCH, "must be true")
    prohibited = (
        "automatic_activation_allowed", "arbitrary_input_allowed", "route_allowed",
        "api_allowed", "network_allowed", "filesystem_read_allowed",
        "filesystem_write_allowed", "memory_read_allowed", "memory_write_allowed",
        "tool_allowed", "action_allowed", "rendering_allowed", "delivery_allowed",
        "echo_validation_allowed", "truth_authority_allowed",
        "evidence_authority_allowed", "permission_authority_allowed",
        "execution_authority_allowed", "slice43_allowed",
    )
    for name in prohibited:
        if getattr(value, name) is not False:
            _issue(issues, f"state.{name}", Slice42CloseoutValidationCode.BOUNDARY_VIOLATION, "must be false")
    if value.enabled is not value.explicit_offline_developer_enable:
        _issue(issues, "state.enabled", Slice42CloseoutValidationCode.STATE_MISMATCH, "enable fields must agree")
    return _report(issues)


def validate_fixture(value: object) -> Slice42CloseoutValidationReport:
    issues: list[Slice42CloseoutValidationIssue] = []
    if type(value) is not OutwardExpressionCloseoutFixture:
        _issue(issues, "fixture", Slice42CloseoutValidationCode.TYPE_MISMATCH, "exact type required")
        return _report(issues)
    expected_id = stable_identifier(
        "slice42h_outward_expression_closeout_fixture",
        value,
        excluded_fields=("fixture_id",),
    )
    if value.fixture_id != expected_id:
        _issue(issues, "fixture.fixture_id", Slice42CloseoutValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch")
    if value.schema_version != SLICE42H_SCHEMA_VERSION:
        _issue(issues, "fixture.schema_version", Slice42CloseoutValidationCode.VERSION_MISMATCH, "schema version mismatch")
    if not is_exact_accepted_fixture(value):
        _issue(issues, "fixture", Slice42CloseoutValidationCode.FIXTURE_MISMATCH, "closed registry membership required")
    for name in (
        "accepted_fixture", "synthetic", "explicit_invocation_only",
        "offline_only", "in_memory_only", "deterministic",
    ):
        if getattr(value, name) is not True:
            _issue(issues, f"fixture.{name}", Slice42CloseoutValidationCode.FIXTURE_MISMATCH, "must be true")
    id_fields = tuple(
        name for name in value.__dataclass_fields__
        if name.startswith("expected_") and (name.endswith("_id") or name.endswith("_ref"))
    )
    for name in id_fields:
        if not getattr(value, name):
            _issue(issues, f"fixture.{name}", Slice42CloseoutValidationCode.FIXTURE_MISMATCH, "non-empty reference required")
    return _report(issues)


def validate_invocation(value: object) -> Slice42CloseoutValidationReport:
    issues: list[Slice42CloseoutValidationIssue] = []
    if type(value) is not OutwardExpressionCloseoutInvocation:
        _issue(issues, "invocation", Slice42CloseoutValidationCode.TYPE_MISMATCH, "exact type required")
        return _report(issues)
    expected_id = stable_identifier(
        "slice42h_outward_expression_closeout_invocation",
        value,
        excluded_fields=("invocation_id",),
    )
    if value.invocation_id != expected_id:
        _issue(issues, "invocation.invocation_id", Slice42CloseoutValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch")
    if value.schema_version != SLICE42H_SCHEMA_VERSION:
        _issue(issues, "invocation.schema_version", Slice42CloseoutValidationCode.VERSION_MISMATCH, "schema version mismatch")
    if value.requested_operation != REQUESTED_OPERATION:
        _issue(issues, "invocation.requested_operation", Slice42CloseoutValidationCode.INVOCATION_MISMATCH, "exact operation required")
    if value.explicit_offline_developer_enable is not True:
        _issue(issues, "invocation.explicit_offline_developer_enable", Slice42CloseoutValidationCode.INVOCATION_MISMATCH, "explicit enable required")
    if value.arbitrary_input_carried is not False:
        _issue(issues, "invocation.arbitrary_input_carried", Slice42CloseoutValidationCode.BOUNDARY_VIOLATION, "arbitrary input prohibited")
    return _report(issues)


def validate_rollback_metadata(value: object) -> Slice42CloseoutValidationReport:
    issues: list[Slice42CloseoutValidationIssue] = []
    if type(value) is not Slice42RollbackMetadata:
        _issue(issues, "rollback", Slice42CloseoutValidationCode.TYPE_MISMATCH, "exact type required")
        return _report(issues)
    expected_id = stable_identifier(
        "slice42h_rollback_metadata", value, excluded_fields=("metadata_id",)
    )
    if value.metadata_id != expected_id:
        _issue(issues, "rollback.metadata_id", Slice42CloseoutValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch")
    expected = {
        "metadata_version": SLICE42H_ROLLBACK_METADATA_VERSION,
        "pre_slice42_commit": PRE_SLICE42_COMMIT,
        "pre_slice42_tree": PRE_SLICE42_TREE,
        "pre_slice42_subject": PRE_SLICE42_SUBJECT,
        "accepted_slice42g_head": SLICE42G_ACCEPTED_HEAD,
        "accepted_slice42g_tree": SLICE42G_ACCEPTED_TREE,
        "accepted_slice42g_subject": SLICE42G_ACCEPTED_SUBJECT,
    }
    for name, wanted in expected.items():
        if getattr(value, name) != wanted:
            _issue(issues, f"rollback.{name}", Slice42CloseoutValidationCode.PREDECESSOR_MISMATCH, "exact predecessor metadata required")
    for name in (
        "recovery_requires_explicit_operator_action", "complete_history_required",
        "exact_tree_recovery_required",
    ):
        if getattr(value, name) is not True:
            _issue(issues, f"rollback.{name}", Slice42CloseoutValidationCode.PREDECESSOR_MISMATCH, "must be true")
    for name in ("runtime_rollback_performed", "repository_mutated"):
        if getattr(value, name) is not False:
            _issue(issues, f"rollback.{name}", Slice42CloseoutValidationCode.BOUNDARY_VIOLATION, "must be false")
    return _report(issues)


def validate_acceptance_record(value: object) -> Slice42CloseoutValidationReport:
    issues: list[Slice42CloseoutValidationIssue] = []
    if type(value) is not Slice42AcceptanceRecord:
        _issue(issues, "acceptance", Slice42CloseoutValidationCode.TYPE_MISMATCH, "exact type required")
        return _report(issues)
    expected_id = stable_identifier(
        "slice42_acceptance_record", value, excluded_fields=("record_id",)
    )
    if value.record_id != expected_id:
        _issue(issues, "acceptance.record_id", Slice42CloseoutValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch")
    if value.record_version != SLICE42H_ACCEPTANCE_RECORD_VERSION:
        _issue(issues, "acceptance.record_version", Slice42CloseoutValidationCode.VERSION_MISMATCH, "record version mismatch")
    exact_tuples = {
        "accepted_increment_labels": SLICE42_INCREMENT_LABELS,
        "accepted_chain": SLICE42_ACCEPTED_CHAIN,
        "accepted_scope": SLICE42_ACCEPTED_SCOPE,
        "deferred_scope": SLICE42_DEFERRED_SCOPE,
        "permanent_boundaries": SLICE42_PERMANENT_BOUNDARIES,
        "prohibited_authority": SLICE42_PROHIBITED_AUTHORITY,
    }
    for name, wanted in exact_tuples.items():
        if getattr(value, name) != wanted:
            _issue(issues, f"acceptance.{name}", Slice42CloseoutValidationCode.ACCEPTANCE_MISMATCH, "exact tuple required")
    if value.slice42_closed:
        for name in (
            "stop_after_slice42", "authorized_meaning_required",
            "selected_meaning_preserved", "scope_preserved", "certainty_preserved",
            "evidence_status_preserved", "caveats_preserved",
            "refusal_state_preserved", "unresolved_conditions_preserved",
            "deterministic_expression_candidate_created",
            "expression_candidate_remains_unvalidated",
        ):
            if getattr(value, name) is not True:
                _issue(issues, f"acceptance.{name}", Slice42CloseoutValidationCode.ACCEPTANCE_MISMATCH, "must be true for closeout")
    for name in (
        "slice43_started", "echo_validation_performed", "delivery_authority",
        "truth_authority", "evidence_authority", "permission_authority",
        "execution_authority", "runtime_self_grants_acceptance", "production_ready",
    ):
        if getattr(value, name) is not False:
            _issue(issues, f"acceptance.{name}", Slice42CloseoutValidationCode.BOUNDARY_VIOLATION, "must be false")
    return _report(issues)


def validate_stage_receipt(value: object) -> Slice42CloseoutValidationReport:
    issues: list[Slice42CloseoutValidationIssue] = []
    if type(value) is not Slice42CloseoutStageReceipt:
        _issue(issues, "receipt", Slice42CloseoutValidationCode.TYPE_MISMATCH, "exact type required")
        return _report(issues)
    expected_id = stable_identifier(
        "slice42h_closeout_stage_receipt", value, excluded_fields=("receipt_id",)
    )
    if value.receipt_id != expected_id:
        _issue(issues, "receipt.receipt_id", Slice42CloseoutValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch")
    if value.receipt_version != SLICE42H_RECEIPT_VERSION:
        _issue(issues, "receipt.receipt_version", Slice42CloseoutValidationCode.VERSION_MISMATCH, "receipt version mismatch")
    expected_digest = deterministic_digest(
        {
            "stage": value.stage.value,
            "stage_index": value.stage_index,
            "input_refs": value.input_refs,
            "output_refs": value.output_refs,
        }
    )
    if value.stage_digest != expected_digest:
        _issue(issues, "receipt.stage_digest", Slice42CloseoutValidationCode.DIGEST_MISMATCH, "stage digest mismatch")
    for name in ("deterministic", "source_preserved", "offline_only", "in_memory_only"):
        if getattr(value, name) is not True:
            _issue(issues, f"receipt.{name}", Slice42CloseoutValidationCode.RECEIPT_MISMATCH, "must be true")
    for name in (
        "route_created", "api_created", "network_accessed",
        "filesystem_read_performed", "filesystem_write_performed",
        "memory_read_performed", "memory_write_performed", "tool_invoked",
        "action_performed", "rendered", "echo_validated", "delivered",
    ):
        if getattr(value, name) is not False:
            _issue(issues, f"receipt.{name}", Slice42CloseoutValidationCode.BOUNDARY_VIOLATION, "must be false")
    return _report(issues)


def validate_result(value: object) -> Slice42CloseoutValidationReport:
    issues: list[Slice42CloseoutValidationIssue] = []
    if type(value) is not DisabledOutwardExpressionCloseoutResult:
        _issue(issues, "result", Slice42CloseoutValidationCode.TYPE_MISMATCH, "exact type required")
        return _report(issues)
    expected_id = stable_identifier(
        "slice42h_disabled_outward_expression_closeout_result",
        replace(value, result_digest="placeholder"),
        excluded_fields=("result_id",),
    )
    if value.result_id != expected_id:
        _issue(issues, "result.result_id", Slice42CloseoutValidationCode.IDENTITY_MISMATCH, "deterministic identity mismatch")
    expected_digest = deterministic_digest(replace(value, result_digest="placeholder"))
    if value.result_digest != expected_digest:
        _issue(issues, "result.result_digest", Slice42CloseoutValidationCode.DIGEST_MISMATCH, "result digest mismatch")
    if value.schema_version != SLICE42H_SCHEMA_VERSION:
        _issue(issues, "result.schema_version", Slice42CloseoutValidationCode.VERSION_MISMATCH, "schema version mismatch")
    issues.extend(validate_acceptance_record(value.acceptance_record).issues)
    issues.extend(validate_rollback_metadata(value.rollback_metadata).issues)
    for receipt in value.stage_receipts:
        issues.extend(validate_stage_receipt(receipt).issues)
    if value.status is Slice42CloseoutStatus.COMPLETED:
        if value.integration_input is None or value.integration_result is None:
            _issue(issues, "result.integration", Slice42CloseoutValidationCode.RESULT_MISMATCH, "completed result requires exact predecessor custody")
        if value.stage_receipt_count != 9 or len(value.stage_receipts) != 9:
            _issue(issues, "result.stage_receipts", Slice42CloseoutValidationCode.RECEIPT_MISMATCH, "exact nine-stage chain required")
        for name in (
            "explicitly_invoked", "exact_stage_chain_complete",
            "authorized_meaning_required", "selected_meaning_preserved",
            "scope_preserved", "certainty_preserved", "evidence_status_preserved",
            "caveats_preserved", "refusal_state_preserved",
            "unresolved_conditions_preserved",
            "deterministic_expression_candidate_created",
            "governed_outward_meaning_custody_preserved",
            "expression_link_custody_preserved",
            "complete_successor_manifest_validated",
            "expression_candidate_remains_unvalidated",
            "final_slice42_acceptance_record_created",
        ):
            if getattr(value, name) is not True:
                _issue(issues, f"result.{name}", Slice42CloseoutValidationCode.RESULT_MISMATCH, "must be true for completed result")
    for name in (
        "slice43_started", "msm_v1_schema_modified", "automatic_migration_performed",
        "selected_meaning_rewritten", "candidate_alternative_deleted",
        "unresolved_state_resolved", "certainty_upgraded", "evidence_status_upgraded",
        "caveat_omitted", "refusal_softened", "expression_candidate_rewritten",
        "validation_link_created", "delivery_link_created", "echo_validation_performed",
        "echo_approved", "delivery_authorized", "delivered", "truth_determined",
        "evidence_validated", "permission_granted", "execution_authorized",
        "route_created", "api_created", "network_accessed",
        "filesystem_read_performed", "filesystem_write_performed",
        "memory_read_performed", "memory_write_performed", "tool_invoked",
        "action_performed", "rendered", "external_resource_loaded",
        "language_model_used", "embedding_used", "vector_used", "rag_used",
        "semantic_similarity_used", "neural_parser_used", "hidden_classifier_used",
        "gp014_superseded",
    ):
        if getattr(value, name) is not False:
            _issue(issues, f"result.{name}", Slice42CloseoutValidationCode.BOUNDARY_VIOLATION, "must be false")
    return _report(issues)


def assert_valid_result(value: object) -> None:
    report = validate_result(value)
    if not report.ok:
        raise Slice42CloseoutValidationError(report)


PUBLIC_VALIDATORS = (
    validate_state,
    validate_fixture,
    validate_invocation,
    validate_rollback_metadata,
    validate_acceptance_record,
    validate_stage_receipt,
    validate_result,
)

__all__ = (
    "PUBLIC_VALIDATORS",
    "Slice42CloseoutValidationCode",
    "Slice42CloseoutValidationError",
    "Slice42CloseoutValidationIssue",
    "Slice42CloseoutValidationReport",
    "assert_valid_result",
    "validate_acceptance_record",
    "validate_fixture",
    "validate_invocation",
    "validate_result",
    "validate_rollback_metadata",
    "validate_stage_receipt",
    "validate_state",
)
