"""Immutable Slice 43F Echo disposition, rejection and containment records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..schema import EchoDisposition
from ..drift_materiality_classification import (
    DriftKind,
    MaterialityState,
)
from .authority import (
    DIGEST_ALGORITHM,
    DISPOSITION_STATE_VALUES,
    SLICE43F_PROFILE_VERSION,
    SLICE43F_SCHEMA_VERSION,
)


class EchoDispositionExecutionStatus(str, Enum):
    DISPOSITION_CREATED = "DISPOSITION_CREATED"
    HELD_INVALID_REQUEST = "HELD_INVALID_REQUEST"
    HELD_CLASSIFICATION_NOT_READY = "HELD_CLASSIFICATION_NOT_READY"
    HELD_UNSUPPORTED_VERSION = "HELD_UNSUPPORTED_VERSION"
    HELD_IDENTITY_INVALID = "HELD_IDENTITY_INVALID"
    HELD_INCONSISTENT_ANCESTRY = "HELD_INCONSISTENT_ANCESTRY"
    HELD_MISSING_REQUIRED_VALUE = "HELD_MISSING_REQUIRED_VALUE"


class EchoDispositionCode(str, Enum):
    REQUEST_TYPE_INVALID = "request_type_invalid"
    REQUEST_ID_INVALID = "request_id_invalid"
    REQUEST_OPERATION_INVALID = "request_operation_invalid"
    RAW_TEXT_PROHIBITED = "raw_text_prohibited"
    EXPLICIT_REQUEST_REQUIRED = "explicit_request_required"
    CLASSIFICATION_RESULT_TYPE_INVALID = "classification_result_type_invalid"
    CLASSIFICATION_NOT_READY = "classification_not_ready"
    CLASSIFICATION_PACKAGE_MISSING = "classification_package_missing"
    CLASSIFICATION_RESULT_INVALID = "classification_result_invalid"
    CLASSIFICATION_FINDING_INVALID = "classification_finding_invalid"
    UNSUPPORTED_VERSION = "unsupported_version"
    RECOMPUTED_OR_FABRICATED_IDENTITY = "recomputed_or_fabricated_identity"
    INCONSISTENT_ANCESTRY = "inconsistent_ancestry"
    MISSING_REQUIRED_VALUE = "missing_required_value"
    DISPOSITION_INVALID = "disposition_invalid"
    REJECTION_RECORD_INVALID = "rejection_record_invalid"
    CONTAINMENT_RECORD_INVALID = "containment_record_invalid"
    PACKAGE_INVALID = "package_invalid"
    RESULT_INVALID = "result_invalid"
    REPAIR_OR_DOWNSTREAM_AUTHORITY_PROHIBITED = (
        "repair_or_downstream_authority_prohibited"
    )


class EchoDispositionState(str, Enum):
    ALL_MATERIAL_OBLIGATIONS_PASS = DISPOSITION_STATE_VALUES[0]
    DETERMINISTIC_ECHO_LAW_VIOLATION = DISPOSITION_STATE_VALUES[1]
    INCOMPLETE_AUTHORITY_CONTAINED = DISPOSITION_STATE_VALUES[2]


@dataclass(frozen=True, slots=True)
class EchoDispositionIssue:
    path: str
    code: EchoDispositionCode
    detail: str


@dataclass(frozen=True, slots=True)
class EchoDispositionValidationReport:
    issues: tuple[EchoDispositionIssue, ...]
    schema_version: str = SLICE43F_SCHEMA_VERSION
    profile_version: str = SLICE43F_PROFILE_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class EchoDispositionValidationError(ValueError):
    def __init__(self, report: EchoDispositionValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 43F Echo disposition validation failed")


@dataclass(frozen=True, slots=True)
class EchoDispositionRequest:
    request_id: str
    classification_result_ref: str
    classification_package_ref: str
    requested_operation: str
    raw_text: str | None
    explicit_disposition_request: bool
    schema_version: str = SLICE43F_SCHEMA_VERSION
    profile_version: str = SLICE43F_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class EchoRejectionRecord:
    rejection_id: str
    disposition_request_ref: str
    classification_result_ref: str
    classification_package_ref: str
    disposition: EchoDisposition
    violation_finding_refs: tuple[str, ...]
    violation_drift_kinds: tuple[DriftKind, ...]
    rejection_law_refs: tuple[str, ...]
    retained_all_finding_refs: tuple[str, ...]
    preserved_ancestry_refs: tuple[str, ...]
    deterministic_echo_law_violation: bool
    rejection_issued: bool
    candidate_rewritten_or_repaired: bool
    drift_removed_downgraded_or_suppressed: bool
    delivery_authorized_or_performed: bool
    echoforge_called: bool
    model_or_similarity_authority_used: bool
    downstream_authority_created: bool
    msm_v1_modified_or_integrated: bool
    gp014_superseded: bool
    schema_version: str = SLICE43F_SCHEMA_VERSION
    profile_version: str = SLICE43F_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class EchoContainmentRecord:
    containment_id: str
    disposition_request_ref: str
    classification_result_ref: str
    classification_package_ref: str
    disposition: EchoDisposition
    blocking_finding_refs: tuple[str, ...]
    incomplete_authority_finding_refs: tuple[str, ...]
    material_violation_finding_refs: tuple[str, ...]
    blocking_materiality_states: tuple[MaterialityState, ...]
    containment_law_refs: tuple[str, ...]
    retained_all_finding_refs: tuple[str, ...]
    preserved_ancestry_refs: tuple[str, ...]
    incomplete_authority_blocks_progression: bool
    coexistence_precedence_applied: bool
    containment_issued: bool
    candidate_rewritten_or_repaired: bool
    drift_removed_downgraded_or_suppressed: bool
    delivery_authorized_or_performed: bool
    echoforge_called: bool
    model_or_similarity_authority_used: bool
    downstream_authority_created: bool
    msm_v1_modified_or_integrated: bool
    gp014_superseded: bool
    schema_version: str = SLICE43F_SCHEMA_VERSION
    profile_version: str = SLICE43F_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class EchoDispositionRecord:
    disposition_id: str
    disposition_request_ref: str
    classification_result_ref: str
    classification_package_ref: str
    disposition: EchoDisposition
    disposition_state: EchoDispositionState
    all_finding_refs: tuple[str, ...]
    no_drift_finding_refs: tuple[str, ...]
    non_material_finding_refs: tuple[str, ...]
    material_violation_finding_refs: tuple[str, ...]
    incomplete_authority_finding_refs: tuple[str, ...]
    unsupported_finding_refs: tuple[str, ...]
    conflicted_finding_refs: tuple[str, ...]
    indeterminate_finding_refs: tuple[str, ...]
    retained_drift_kinds: tuple[DriftKind, ...]
    disposition_law_refs: tuple[str, ...]
    precedence_rule_ref: str
    all_findings_retention_rule_ref: str
    no_silent_drift_removal_rule_ref: str
    all_material_preservation_obligations_pass: bool
    deterministic_echo_law_violation: bool
    incomplete_authority_blocks_progression: bool
    coexistence_precedence_applied: bool
    rejection_record_ref: str | None
    containment_record_ref: str | None
    candidate_rewritten_or_repaired: bool
    drift_removed_downgraded_or_suppressed: bool
    delivery_authorized_or_performed: bool
    echoforge_called: bool
    model_or_similarity_authority_used: bool
    downstream_authority_created: bool
    msm_v1_modified_or_integrated: bool
    gp014_superseded: bool
    schema_version: str = SLICE43F_SCHEMA_VERSION
    profile_version: str = SLICE43F_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class EchoDispositionPackage:
    disposition_package_id: str
    disposition_package_digest: str
    disposition_request_ref: str
    classification_result_ref: str
    classification_package_ref: str
    disposition_record: EchoDispositionRecord
    rejection_record: EchoRejectionRecord | None
    containment_record: EchoContainmentRecord | None
    classification_record_count: int
    no_drift_finding_count: int
    non_material_finding_count: int
    material_violation_finding_count: int
    incomplete_authority_finding_count: int
    retained_finding_count: int
    disposition_decided: bool
    rejection_issued: bool
    containment_issued: bool
    candidate_rewritten_or_repaired: bool
    drift_removed_downgraded_or_suppressed: bool
    delivery_authorized_or_performed: bool
    truth_evidence_permission_execution_authority: bool
    route_api_network_filesystem_memory_tool_action_authority: bool
    echoforge_called: bool
    downstream_authority_created: bool
    model_or_similarity_authority_used: bool
    msm_v1_modified_or_integrated: bool
    gp014_superseded: bool
    schema_version: str = SLICE43F_SCHEMA_VERSION
    profile_version: str = SLICE43F_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


@dataclass(frozen=True, slots=True)
class EchoDispositionResult:
    disposition_result_id: str
    disposition_result_digest: str
    status: EchoDispositionExecutionStatus
    issue_codes: tuple[EchoDispositionCode, ...]
    reason_refs: tuple[str, ...]
    disposition_request_ref: str
    classification_result_ref: str
    classification_package_ref: str
    disposition_package: EchoDispositionPackage | None
    disposition_decided: bool
    disposition: EchoDisposition | None
    rejection_issued: bool
    containment_issued: bool
    classification_record_count: int
    retained_finding_count: int
    material_violation_finding_count: int
    incomplete_authority_finding_count: int
    candidate_rewritten_or_repaired: bool
    drift_removed_downgraded_or_suppressed: bool
    delivery_authorized_or_performed: bool
    echoforge_called: bool
    downstream_authority_created: bool
    model_or_similarity_authority_used: bool
    msm_v1_modified_or_integrated: bool
    gp014_superseded: bool
    schema_version: str = SLICE43F_SCHEMA_VERSION
    profile_version: str = SLICE43F_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


__all__ = tuple(name for name in globals() if not name.startswith("_"))
