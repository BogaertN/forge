"""Fail-closed validation for Slice 41F closeout records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from ..selected_meaning_runtime.msm_selected_meaning_integration import (
    MsmSelectedMeaningIntegrationInput,
    MsmSelectedMeaningIntegrationResult,
    validate_integration_input,
    validate_integration_result,
)
from .authority import (
    PRE_SLICE41_COMMIT,
    PRE_SLICE41_SUBJECT,
    PRE_SLICE41_TREE,
    REQUESTED_OPERATION,
    SLICE41_ACCEPTED_CHAIN,
    SLICE41_ACCEPTED_SCOPE,
    SLICE41_DEFERRED_SCOPE,
    SLICE41_INCREMENT_LABELS,
    SLICE41_PERMANENT_BOUNDARIES,
    SLICE41_PROHIBITED_AUTHORITY,
    SLICE41E_ACCEPTED_HEAD,
    SLICE41E_ACCEPTED_SUBJECT,
    SLICE41E_ACCEPTED_TREE,
    SLICE41F_ACCEPTANCE_RECORD_VERSION,
    SLICE41F_ROLLBACK_METADATA_VERSION,
    SLICE41F_SCHEMA_VERSION,
)
from .canonical import deterministic_digest, stable_identifier
from .fixtures import (
    get_selected_meaning_closeout_fixture,
    is_exact_accepted_fixture,
)
from .schema import (
    DisabledSelectedMeaningCloseoutResult,
    DisabledSelectedMeaningCloseoutState,
    SelectedMeaningCloseoutFixture,
    SelectedMeaningCloseoutInvocation,
    Slice41AcceptanceRecord,
    Slice41CloseoutStage,
    Slice41CloseoutStageReceipt,
    Slice41CloseoutStatus,
    Slice41RollbackMetadata,
)


class Slice41CloseoutValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    SCHEMA_MISMATCH = "schema_mismatch"
    IDENTITY_MISMATCH = "identity_mismatch"
    VALUE_MISMATCH = "value_mismatch"
    FIXTURE_MISMATCH = "fixture_mismatch"
    STAGE_MISMATCH = "stage_mismatch"
    PREDECESSOR_MISMATCH = "predecessor_mismatch"
    ACCEPTANCE_MISMATCH = "acceptance_mismatch"
    PROHIBITED_AUTHORITY = "prohibited_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class Slice41CloseoutValidationIssue:
    path: str
    code: Slice41CloseoutValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class Slice41CloseoutValidationReport:
    issues: tuple[Slice41CloseoutValidationIssue, ...]
    schema_version: str = SLICE41F_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class Slice41CloseoutValidationError(ValueError):
    def __init__(self, report: Slice41CloseoutValidationReport) -> None:
        self.report = report
        text = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(text or "Slice 41F validation failed")


def _report(
    issues: list[Slice41CloseoutValidationIssue],
) -> Slice41CloseoutValidationReport:
    return Slice41CloseoutValidationReport(tuple(issues))


def _issue(
    issues: list[Slice41CloseoutValidationIssue],
    path: str,
    code: Slice41CloseoutValidationCode,
    detail: str,
) -> None:
    issues.append(Slice41CloseoutValidationIssue(path, code, detail))


def _safe_expected(
    issues: list[Slice41CloseoutValidationIssue],
    path: str,
    function: Callable[[], str],
) -> str | None:
    try:
        return function()
    except (TypeError, ValueError, AttributeError, KeyError) as error:
        _issue(
            issues,
            path,
            Slice41CloseoutValidationCode.CANONICAL_MISMATCH,
            f"cannot compute expected value: {type(error).__name__}",
        )
        return None


def _expected_id(namespace: str, value: object, field: str) -> str:
    return stable_identifier(
        namespace,
        value,
        excluded_fields=(field,),
    )


def _schema(
    value: object,
    path: str,
    issues: list[Slice41CloseoutValidationIssue],
) -> None:
    if getattr(value, "schema_version", None) != SLICE41F_SCHEMA_VERSION:
        _issue(
            issues,
            path + ".schema_version",
            Slice41CloseoutValidationCode.SCHEMA_MISMATCH,
            "exact Slice 41F schema version required",
        )


def _false_fields(
    value: object,
    fields: tuple[str, ...],
    path: str,
    issues: list[Slice41CloseoutValidationIssue],
) -> None:
    for field in fields:
        if getattr(value, field, None) is not False:
            _issue(
                issues,
                f"{path}.{field}",
                Slice41CloseoutValidationCode.PROHIBITED_AUTHORITY,
                "must remain false",
            )


def _true_fields(
    value: object,
    fields: tuple[str, ...],
    path: str,
    issues: list[Slice41CloseoutValidationIssue],
) -> None:
    for field in fields:
        if getattr(value, field, None) is not True:
            _issue(
                issues,
                f"{path}.{field}",
                Slice41CloseoutValidationCode.VALUE_MISMATCH,
                "must be true",
            )


def validate_state(value: object) -> Slice41CloseoutValidationReport:
    issues: list[Slice41CloseoutValidationIssue] = []
    if type(value) is not DisabledSelectedMeaningCloseoutState:
        return _report(
            [
                Slice41CloseoutValidationIssue(
                    "state",
                    Slice41CloseoutValidationCode.TYPE_MISMATCH,
                    "exact state type required",
                )
            ]
        )
    _schema(value, "state", issues)
    expected = _safe_expected(
        issues,
        "state.state_id",
        lambda: _expected_id(
            "slice41f_disabled_closeout_state",
            value,
            "state_id",
        ),
    )
    if expected is not None and value.state_id != expected:
        _issue(
            issues,
            "state.state_id",
            Slice41CloseoutValidationCode.IDENTITY_MISMATCH,
            "state identity mismatch",
        )
    if value.enabled is not value.explicit_offline_developer_enable:
        _issue(
            issues,
            "state.enabled",
            Slice41CloseoutValidationCode.VALUE_MISMATCH,
            "enablement must equal explicit offline developer enable",
        )
    _true_fields(
        value,
        (
            "disabled_by_default",
            "explicit_invocation_required",
            "accepted_static_fixture_only",
            "offline_only",
            "read_only",
            "in_memory_only",
            "deterministic",
            "exact_profile_bounded",
            "source_preserving",
            "rollback_safe",
        ),
        "state",
        issues,
    )
    _false_fields(
        value,
        (
            "automatic_activation_allowed",
            "arbitrary_input_allowed",
            "route_allowed",
            "api_allowed",
            "network_allowed",
            "filesystem_read_allowed",
            "filesystem_write_allowed",
            "memory_read_allowed",
            "memory_write_allowed",
            "tool_allowed",
            "action_allowed",
            "rendering_allowed",
            "delivery_allowed",
            "truth_authority_allowed",
            "evidence_authority_allowed",
            "permission_authority_allowed",
            "execution_authority_allowed",
            "outward_expression_authority_allowed",
            "slice42_allowed",
        ),
        "state",
        issues,
    )
    return _report(issues)


def validate_fixture(value: object) -> Slice41CloseoutValidationReport:
    issues: list[Slice41CloseoutValidationIssue] = []
    if type(value) is not SelectedMeaningCloseoutFixture:
        return _report(
            [
                Slice41CloseoutValidationIssue(
                    "fixture",
                    Slice41CloseoutValidationCode.TYPE_MISMATCH,
                    "exact fixture type required",
                )
            ]
        )
    _schema(value, "fixture", issues)
    expected = _safe_expected(
        issues,
        "fixture.fixture_id",
        lambda: _expected_id(
            "slice41f_selected_meaning_closeout_fixture",
            value,
            "fixture_id",
        ),
    )
    if expected is not None and value.fixture_id != expected:
        _issue(
            issues,
            "fixture.fixture_id",
            Slice41CloseoutValidationCode.IDENTITY_MISMATCH,
            "fixture identity mismatch",
        )
    if not is_exact_accepted_fixture(value):
        _issue(
            issues,
            "fixture",
            Slice41CloseoutValidationCode.FIXTURE_MISMATCH,
            "fixture is not in the closed accepted registry",
        )
    for field in (
        "fixture_name",
        "expected_integration_input_id",
        "expected_source_manifest_id",
        "expected_source_manifest_sha256",
        "expected_successor_manifest_id",
        "expected_successor_manifest_sha256",
        "expected_integration_result_id",
        "expected_integration_result_digest",
        "expected_selected_candidate_ref",
        "expected_selection_receipt_ref",
        "expected_integrated_selected_meaning_ref",
    ):
        if type(getattr(value, field, None)) is not str or not getattr(value, field):
            _issue(
                issues,
                f"fixture.{field}",
                Slice41CloseoutValidationCode.VALUE_MISMATCH,
                "non-empty string required",
            )
    for field in (
        "expected_source_candidate_count",
        "expected_source_non_selection_count",
        "expected_successor_selected_count",
        "expected_unresolved_outcome_count",
    ):
        if type(getattr(value, field, None)) is not int or getattr(value, field) < 1:
            _issue(
                issues,
                f"fixture.{field}",
                Slice41CloseoutValidationCode.VALUE_MISMATCH,
                "positive integer required",
            )
    _true_fields(
        value,
        (
            "accepted_fixture",
            "synthetic",
            "explicit_invocation_only",
            "offline_only",
            "in_memory_only",
            "deterministic",
        ),
        "fixture",
        issues,
    )
    return _report(issues)


def validate_invocation(value: object) -> Slice41CloseoutValidationReport:
    issues: list[Slice41CloseoutValidationIssue] = []
    if type(value) is not SelectedMeaningCloseoutInvocation:
        return _report(
            [
                Slice41CloseoutValidationIssue(
                    "invocation",
                    Slice41CloseoutValidationCode.TYPE_MISMATCH,
                    "exact invocation type required",
                )
            ]
        )
    _schema(value, "invocation", issues)
    expected = _safe_expected(
        issues,
        "invocation.invocation_id",
        lambda: _expected_id(
            "slice41f_selected_meaning_closeout_invocation",
            value,
            "invocation_id",
        ),
    )
    if expected is not None and value.invocation_id != expected:
        _issue(
            issues,
            "invocation.invocation_id",
            Slice41CloseoutValidationCode.IDENTITY_MISMATCH,
            "invocation identity mismatch",
        )
    fixture = get_selected_meaning_closeout_fixture(value.fixture_name)
    if fixture is None or fixture.fixture_id != value.fixture_id:
        _issue(
            issues,
            "invocation.fixture_id",
            Slice41CloseoutValidationCode.FIXTURE_MISMATCH,
            "exact accepted fixture reference required",
        )
    if value.requested_operation != REQUESTED_OPERATION:
        _issue(
            issues,
            "invocation.requested_operation",
            Slice41CloseoutValidationCode.VALUE_MISMATCH,
            "exact requested operation required",
        )
    if value.explicit_offline_developer_enable is not True:
        _issue(
            issues,
            "invocation.explicit_offline_developer_enable",
            Slice41CloseoutValidationCode.VALUE_MISMATCH,
            "explicit enable required",
        )
    if value.arbitrary_input_carried is not False:
        _issue(
            issues,
            "invocation.arbitrary_input_carried",
            Slice41CloseoutValidationCode.PROHIBITED_AUTHORITY,
            "arbitrary input is prohibited",
        )
    return _report(issues)


def validate_stage_receipt(value: object) -> Slice41CloseoutValidationReport:
    issues: list[Slice41CloseoutValidationIssue] = []
    if type(value) is not Slice41CloseoutStageReceipt:
        return _report(
            [
                Slice41CloseoutValidationIssue(
                    "stage_receipt",
                    Slice41CloseoutValidationCode.TYPE_MISMATCH,
                    "exact stage receipt type required",
                )
            ]
        )
    _schema(value, "stage_receipt", issues)
    expected = _safe_expected(
        issues,
        "stage_receipt.receipt_id",
        lambda: _expected_id(
            "slice41f_closeout_stage_receipt",
            value,
            "receipt_id",
        ),
    )
    if expected is not None and value.receipt_id != expected:
        _issue(
            issues,
            "stage_receipt.receipt_id",
            Slice41CloseoutValidationCode.IDENTITY_MISMATCH,
            "stage receipt identity mismatch",
        )
    if type(value.stage) is not Slice41CloseoutStage:
        _issue(
            issues,
            "stage_receipt.stage",
            Slice41CloseoutValidationCode.STAGE_MISMATCH,
            "exact stage enum required",
        )
    if type(value.stage_index) is not int or not 1 <= value.stage_index <= 6:
        _issue(
            issues,
            "stage_receipt.stage_index",
            Slice41CloseoutValidationCode.STAGE_MISMATCH,
            "stage index must be 1 through 6",
        )
    expected_digest = _safe_expected(
        issues,
        "stage_receipt.stage_digest",
        lambda: deterministic_digest(
            {
                "stage": value.stage.value,
                "stage_index": value.stage_index,
                "input_refs": value.input_refs,
                "output_refs": value.output_refs,
            }
        ),
    )
    if expected_digest is not None and value.stage_digest != expected_digest:
        _issue(
            issues,
            "stage_receipt.stage_digest",
            Slice41CloseoutValidationCode.CANONICAL_MISMATCH,
            "stage digest mismatch",
        )
    if not value.input_refs or not value.output_refs:
        _issue(
            issues,
            "stage_receipt.references",
            Slice41CloseoutValidationCode.VALUE_MISMATCH,
            "non-empty input and output references required",
        )
    _true_fields(
        value,
        ("deterministic", "source_preserved", "offline_only", "in_memory_only"),
        "stage_receipt",
        issues,
    )
    _false_fields(
        value,
        (
            "route_created",
            "api_created",
            "network_accessed",
            "filesystem_read_performed",
            "filesystem_write_performed",
            "memory_read_performed",
            "memory_write_performed",
            "tool_invoked",
            "action_performed",
            "rendered",
            "delivered",
        ),
        "stage_receipt",
        issues,
    )
    return _report(issues)


def validate_rollback_metadata(value: object) -> Slice41CloseoutValidationReport:
    issues: list[Slice41CloseoutValidationIssue] = []
    if type(value) is not Slice41RollbackMetadata:
        return _report(
            [
                Slice41CloseoutValidationIssue(
                    "rollback_metadata",
                    Slice41CloseoutValidationCode.TYPE_MISMATCH,
                    "exact rollback metadata type required",
                )
            ]
        )
    _schema(value, "rollback_metadata", issues)
    expected = _safe_expected(
        issues,
        "rollback_metadata.metadata_id",
        lambda: _expected_id(
            "slice41f_rollback_metadata",
            value,
            "metadata_id",
        ),
    )
    if expected is not None and value.metadata_id != expected:
        _issue(
            issues,
            "rollback_metadata.metadata_id",
            Slice41CloseoutValidationCode.IDENTITY_MISMATCH,
            "rollback metadata identity mismatch",
        )
    exact = {
        "metadata_version": SLICE41F_ROLLBACK_METADATA_VERSION,
        "pre_slice41_commit": PRE_SLICE41_COMMIT,
        "pre_slice41_tree": PRE_SLICE41_TREE,
        "pre_slice41_subject": PRE_SLICE41_SUBJECT,
        "accepted_slice41e_head": SLICE41E_ACCEPTED_HEAD,
        "accepted_slice41e_tree": SLICE41E_ACCEPTED_TREE,
        "accepted_slice41e_subject": SLICE41E_ACCEPTED_SUBJECT,
    }
    for field, expected_value in exact.items():
        if getattr(value, field, None) != expected_value:
            _issue(
                issues,
                f"rollback_metadata.{field}",
                Slice41CloseoutValidationCode.PREDECESSOR_MISMATCH,
                "exact recovery boundary required",
            )
    _true_fields(
        value,
        (
            "recovery_requires_explicit_operator_action",
            "complete_history_required",
            "exact_tree_recovery_required",
        ),
        "rollback_metadata",
        issues,
    )
    _false_fields(
        value,
        ("runtime_rollback_performed", "repository_mutated"),
        "rollback_metadata",
        issues,
    )
    return _report(issues)


def validate_acceptance_record(value: object) -> Slice41CloseoutValidationReport:
    issues: list[Slice41CloseoutValidationIssue] = []
    if type(value) is not Slice41AcceptanceRecord:
        return _report(
            [
                Slice41CloseoutValidationIssue(
                    "acceptance_record",
                    Slice41CloseoutValidationCode.TYPE_MISMATCH,
                    "exact acceptance record type required",
                )
            ]
        )
    _schema(value, "acceptance_record", issues)
    expected = _safe_expected(
        issues,
        "acceptance_record.record_id",
        lambda: _expected_id(
            "slice41_acceptance_record",
            value,
            "record_id",
        ),
    )
    if expected is not None and value.record_id != expected:
        _issue(
            issues,
            "acceptance_record.record_id",
            Slice41CloseoutValidationCode.IDENTITY_MISMATCH,
            "acceptance record identity mismatch",
        )
    exact = {
        "record_version": SLICE41F_ACCEPTANCE_RECORD_VERSION,
        "accepted_increment_labels": SLICE41_INCREMENT_LABELS,
        "accepted_chain": SLICE41_ACCEPTED_CHAIN,
        "accepted_scope": SLICE41_ACCEPTED_SCOPE,
        "deferred_scope": SLICE41_DEFERRED_SCOPE,
        "permanent_boundaries": SLICE41_PERMANENT_BOUNDARIES,
        "prohibited_authority": SLICE41_PROHIBITED_AUTHORITY,
    }
    for field, expected_value in exact.items():
        if getattr(value, field, None) != expected_value:
            _issue(
                issues,
                f"acceptance_record.{field}",
                Slice41CloseoutValidationCode.ACCEPTANCE_MISMATCH,
                "exact Slice 41 acceptance content required",
            )
    if not value.rollback_metadata_ref:
        _issue(
            issues,
            "acceptance_record.rollback_metadata_ref",
            Slice41CloseoutValidationCode.VALUE_MISMATCH,
            "rollback metadata reference required",
        )
    _true_fields(
        value,
        (
            "stop_after_slice41",
            "selected_meaning_bounded_semantic_custody_only",
        ),
        "acceptance_record",
        issues,
    )
    if value.slice41_closed:
        _true_fields(
            value,
            ("alternatives_preserved", "unresolved_state_preserved"),
            "acceptance_record",
            issues,
        )
    else:
        _false_fields(
            value,
            ("alternatives_preserved", "unresolved_state_preserved"),
            "acceptance_record",
            issues,
        )
    _false_fields(
        value,
        (
            "slice42_started",
            "truth_authority",
            "evidence_authority",
            "permission_authority",
            "execution_authority",
            "outward_expression_authority",
            "runtime_self_grants_acceptance",
            "production_ready",
        ),
        "acceptance_record",
        issues,
    )
    return _report(issues)


def validate_result(value: object) -> Slice41CloseoutValidationReport:
    issues: list[Slice41CloseoutValidationIssue] = []
    if type(value) is not DisabledSelectedMeaningCloseoutResult:
        return _report(
            [
                Slice41CloseoutValidationIssue(
                    "result",
                    Slice41CloseoutValidationCode.TYPE_MISMATCH,
                    "exact result type required",
                )
            ]
        )
    _schema(value, "result", issues)
    expected = _safe_expected(
        issues,
        "result.result_id",
        lambda: _expected_id(
            "slice41f_disabled_selected_meaning_closeout_result",
            value,
            "result_id",
        ),
    )
    if expected is not None and value.result_id != expected:
        _issue(
            issues,
            "result.result_id",
            Slice41CloseoutValidationCode.IDENTITY_MISMATCH,
            "result identity mismatch",
        )
    issues.extend(validate_rollback_metadata(value.rollback_metadata).issues)
    issues.extend(validate_acceptance_record(value.acceptance_record).issues)
    if value.acceptance_record.rollback_metadata_ref != value.rollback_metadata.metadata_id:
        _issue(
            issues,
            "result.acceptance_record.rollback_metadata_ref",
            Slice41CloseoutValidationCode.PREDECESSOR_MISMATCH,
            "rollback metadata reference mismatch",
        )
    completed = value.status is Slice41CloseoutStatus.COMPLETED
    if completed:
        if type(value.integration_input) is not MsmSelectedMeaningIntegrationInput:
            _issue(
                issues,
                "result.integration_input",
                Slice41CloseoutValidationCode.TYPE_MISMATCH,
                "completed result requires exact Slice 41E input",
            )
        else:
            issues.extend(
                Slice41CloseoutValidationIssue(
                    "result.integration_input." + item.path,
                    Slice41CloseoutValidationCode.PREDECESSOR_MISMATCH,
                    item.detail,
                )
                for item in validate_integration_input(value.integration_input).issues
            )
        if type(value.integration_result) is not MsmSelectedMeaningIntegrationResult:
            _issue(
                issues,
                "result.integration_result",
                Slice41CloseoutValidationCode.TYPE_MISMATCH,
                "completed result requires exact Slice 41E result",
            )
        elif type(value.integration_input) is MsmSelectedMeaningIntegrationInput:
            issues.extend(
                Slice41CloseoutValidationIssue(
                    "result.integration_result." + item.path,
                    Slice41CloseoutValidationCode.PREDECESSOR_MISMATCH,
                    item.detail,
                )
                for item in validate_integration_result(
                    value.integration_result,
                    integration_input=value.integration_input,
                ).issues
            )
        if value.stage_receipt_count != 6 or len(value.stage_receipts) != 6:
            _issue(
                issues,
                "result.stage_receipts",
                Slice41CloseoutValidationCode.STAGE_MISMATCH,
                "completed result requires six stage receipts",
            )
        expected_stages = tuple(Slice41CloseoutStage)
        actual_stages = tuple(item.stage for item in value.stage_receipts)
        if actual_stages != expected_stages:
            _issue(
                issues,
                "result.stage_receipts",
                Slice41CloseoutValidationCode.STAGE_MISMATCH,
                "exact ordered stage chain required",
            )
        for index, receipt in enumerate(value.stage_receipts, 1):
            issues.extend(validate_stage_receipt(receipt).issues)
            if receipt.stage_index != index:
                _issue(
                    issues,
                    f"result.stage_receipts[{index - 1}].stage_index",
                    Slice41CloseoutValidationCode.STAGE_MISMATCH,
                    "stage index order mismatch",
                )
        _true_fields(
            value,
            (
                "exact_stage_chain_complete",
                "selected_meaning_integrated",
                "selected_meaning_bounded_semantic_custody_only",
                "candidate_meanings_retained",
                "non_selection_outcomes_retained",
                "alternatives_preserved",
                "unresolved_state_preserved",
                "slice40h_custody_preserved",
                "slice41d_construction_preserved",
                "slice41e_integration_preserved",
                "final_slice41_acceptance_record_created",
            ),
            "result",
            issues,
        )
        if value.acceptance_record.slice41_closed is not True:
            _issue(
                issues,
                "result.acceptance_record.slice41_closed",
                Slice41CloseoutValidationCode.ACCEPTANCE_MISMATCH,
                "completed result must close Slice 41",
            )
    else:
        if value.integration_input is not None or value.integration_result is not None:
            _issue(
                issues,
                "result.integration",
                Slice41CloseoutValidationCode.VALUE_MISMATCH,
                "held or refused result must not carry integration records",
            )
        if value.stage_receipts or value.stage_receipt_count != 0:
            _issue(
                issues,
                "result.stage_receipts",
                Slice41CloseoutValidationCode.STAGE_MISMATCH,
                "held or refused result must have no stage receipts",
            )
        _false_fields(
            value,
            (
                "exact_stage_chain_complete",
                "selected_meaning_integrated",
                "selected_meaning_bounded_semantic_custody_only",
                "candidate_meanings_retained",
                "non_selection_outcomes_retained",
                "alternatives_preserved",
                "unresolved_state_preserved",
                "slice40h_custody_preserved",
                "slice41d_construction_preserved",
                "slice41e_integration_preserved",
                "final_slice41_acceptance_record_created",
            ),
            "result",
            issues,
        )
        if value.acceptance_record.slice41_closed is not False:
            _issue(
                issues,
                "result.acceptance_record.slice41_closed",
                Slice41CloseoutValidationCode.ACCEPTANCE_MISMATCH,
                "held or refused result must not close Slice 41",
            )
    expected_digest = _safe_expected(
        issues,
        "result.deterministic_repeat_digest",
        lambda: deterministic_digest(
            {
                "state_id": value.state_id,
                "invocation_id": value.invocation_id,
                "fixture_id": value.fixture_id,
                "status": value.status.value,
                "reason_code": value.reason_code,
                "integration_input_id": getattr(
                    value.integration_input,
                    "integration_input_id",
                    "",
                ),
                "integration_result_id": getattr(
                    value.integration_result,
                    "result_id",
                    "",
                ),
                "acceptance_record_id": value.acceptance_record.record_id,
                "rollback_metadata_id": value.rollback_metadata.metadata_id,
                "stage_receipt_ids": tuple(
                    item.receipt_id for item in value.stage_receipts
                ),
            }
        ),
    )
    if (
        expected_digest is not None
        and value.deterministic_repeat_digest != expected_digest
    ):
        _issue(
            issues,
            "result.deterministic_repeat_digest",
            Slice41CloseoutValidationCode.CANONICAL_MISMATCH,
            "deterministic repeat digest mismatch",
        )
    _true_fields(
        value,
        (
            "disabled_by_default",
            "accepted_static_fixture_only",
            "offline_only",
            "read_only",
            "in_memory_only",
            "deterministic",
        ),
        "result",
        issues,
    )
    _false_fields(
        value,
        (
            "slice42_started",
            "truth_determined",
            "evidence_validated",
            "permission_granted",
            "execution_authorized",
            "outward_expression_authorized",
            "governed_outward_meaning_created",
            "expression_link_created",
            "validation_link_created",
            "delivery_link_created",
            "capability_availability_created",
            "route_created",
            "api_created",
            "network_accessed",
            "filesystem_read_performed",
            "filesystem_write_performed",
            "memory_read_performed",
            "memory_write_performed",
            "tool_invoked",
            "action_performed",
            "rendered",
            "delivered",
            "language_model_used",
            "embedding_used",
            "vector_used",
            "rag_used",
            "semantic_similarity_used",
        ),
        "result",
        issues,
    )
    return _report(issues)


def assert_valid_result(value: object) -> None:
    report = validate_result(value)
    if not report.ok:
        raise Slice41CloseoutValidationError(report)


PUBLIC_VALIDATORS = (
    validate_state,
    validate_fixture,
    validate_invocation,
    validate_stage_receipt,
    validate_rollback_metadata,
    validate_acceptance_record,
    validate_result,
)


__all__ = (
    "PUBLIC_VALIDATORS",
    "Slice41CloseoutValidationCode",
    "Slice41CloseoutValidationError",
    "Slice41CloseoutValidationIssue",
    "Slice41CloseoutValidationReport",
    "assert_valid_result",
    "validate_acceptance_record",
    "validate_fixture",
    "validate_invocation",
    "validate_result",
    "validate_rollback_metadata",
    "validate_stage_receipt",
    "validate_state",
)
