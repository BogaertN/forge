"""Immutable Slice 43C exact-source admission records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...outward_expression_runtime.disabled_outward_expression_closeout import (
    DisabledOutwardExpressionCloseoutResult,
)
from ..schema import (
    AuthorizedMeaningReferenceRecord,
    EchoValidationInputBoundaryRecord,
    ProposedExpressionReferenceRecord,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE43C_PROFILE_VERSION,
    SLICE43C_SCHEMA_VERSION,
)


class SourceAdmissionStatus(str, Enum):
    ADMITTED = "ADMITTED"
    HELD_INVALID_REQUEST = "HELD_INVALID_REQUEST"
    HELD_RAW_TEXT = "HELD_RAW_TEXT"
    HELD_UNSUPPORTED_VERSION = "HELD_UNSUPPORTED_VERSION"
    HELD_IDENTITY_INVALID = "HELD_IDENTITY_INVALID"
    HELD_MISSING_LINK = "HELD_MISSING_LINK"
    HELD_ORPHAN_EXPRESSION = "HELD_ORPHAN_EXPRESSION"
    HELD_ALREADY_DELIVERED = "HELD_ALREADY_DELIVERED"
    HELD_UNAUTHORIZED_CANDIDATE = "HELD_UNAUTHORIZED_CANDIDATE"
    HELD_INCONSISTENT_ANCESTRY = "HELD_INCONSISTENT_ANCESTRY"
    HELD_SOURCE_NOT_ACCEPTED = "HELD_SOURCE_NOT_ACCEPTED"


class SourceAdmissionCode(str, Enum):
    REQUEST_TYPE_INVALID = "request_type_invalid"
    REQUEST_ID_INVALID = "request_id_invalid"
    REQUEST_OPERATION_INVALID = "request_operation_invalid"
    RAW_TEXT_WITHOUT_ACCEPTED_ANCESTRY = (
        "raw_text_without_accepted_ancestry"
    )
    SOURCE_TYPE_INVALID = "source_type_invalid"
    SOURCE_NOT_COMPLETED = "source_not_completed"
    SOURCE_NOT_ACCEPTED = "source_not_accepted"
    UNSUPPORTED_VERSION = "unsupported_version"
    IDENTITY_MISMATCH = "identity_mismatch"
    RECOMPUTED_OR_FABRICATED_IDENTITY = (
        "recomputed_or_fabricated_identity"
    )
    MISSING_REQUIRED_LINK = "missing_required_link"
    ORPHAN_EXPRESSION = "orphan_expression"
    ALREADY_DELIVERED_CANDIDATE = "already_delivered_candidate"
    UNAUTHORIZED_CANDIDATE = "unauthorized_candidate"
    INCONSISTENT_ANCESTRY = "inconsistent_accepted_ancestry"
    PREDECESSOR_VALIDATION_FAILED = "predecessor_validation_failed"
    ADMISSION_RECORD_INVALID = "admission_record_invalid"
    DOWNSTREAM_AUTHORITY_PROHIBITED = (
        "downstream_authority_prohibited"
    )


@dataclass(frozen=True, slots=True)
class SourceAdmissionIssue:
    path: str
    code: SourceAdmissionCode
    detail: str


@dataclass(frozen=True, slots=True)
class SourceAdmissionValidationReport:
    issues: tuple[SourceAdmissionIssue, ...]
    schema_version: str = SLICE43C_SCHEMA_VERSION
    profile_version: str = SLICE43C_PROFILE_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class SourceAdmissionValidationError(ValueError):
    def __init__(self, report: SourceAdmissionValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 43C source admission failed")


@dataclass(frozen=True, slots=True)
class SourceAdmissionRequest:
    request_id: str
    source_closeout_result: DisabledOutwardExpressionCloseoutResult
    requested_operation: str
    raw_text: str | None
    explicit_admission_request: bool
    schema_version: str = SLICE43C_SCHEMA_VERSION
    profile_version: str = SLICE43C_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class AuthorizedMeaningAdmissionRecord:
    admission_record_id: str
    request_ref: str
    source_closeout_result_ref: str
    source_acceptance_record_ref: str
    authorized_meaning_reference: AuthorizedMeaningReferenceRecord
    source_manifest_sha256: str
    successor_manifest_sha256: str
    exact_accepted_ancestry_validated: bool
    identity_and_version_validated: bool
    source_admitted_for_later_comparison: bool
    raw_text_used: bool
    source_rewritten: bool
    alternatives_deleted: bool
    unresolved_conditions_resolved: bool
    schema_version: str = SLICE43C_SCHEMA_VERSION
    profile_version: str = SLICE43C_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class ProposedExpressionAdmissionRecord:
    admission_record_id: str
    request_ref: str
    source_closeout_result_ref: str
    proposed_expression_reference: ProposedExpressionReferenceRecord
    expression_candidate_authorized_for_admission: bool
    expression_candidate_already_delivered: bool
    expression_candidate_echo_approved: bool
    exact_expression_link_validated: bool
    exact_realization_identity_validated: bool
    source_admitted_for_later_comparison: bool
    expression_rewritten: bool
    schema_version: str = SLICE43C_SCHEMA_VERSION
    profile_version: str = SLICE43C_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class EchoValidationAdmissionPackage:
    admission_package_id: str
    admission_package_digest: str
    request_ref: str
    authorized_meaning_admission: AuthorizedMeaningAdmissionRecord
    proposed_expression_admission: ProposedExpressionAdmissionRecord
    validation_input_boundary: EchoValidationInputBoundaryRecord
    source_closeout_result_ref: str
    source_acceptance_record_ref: str
    source_manifest_ref: str
    successor_manifest_ref: str
    source_trace_refs: tuple[str, ...]
    source_receipt_refs: tuple[str, ...]
    required_preservation_dimension_values: tuple[str, ...]
    admitted_for_slice43d_comparison: bool
    exact_accepted_slice42_ancestry: bool
    duplicate_source_rejected: bool
    identity_collision_rejected: bool
    meaning_preservation_comparison_performed: bool
    validation_findings_created: bool
    drift_findings_created: bool
    materiality_decided: bool
    echo_disposition_decided: bool
    rejection_issued: bool
    containment_issued: bool
    msm_v1_modified_or_integrated: bool
    delivery_authorized_or_performed: bool
    truth_evidence_permission_execution_authority: bool
    route_api_network_filesystem_memory_tool_action_authority: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE43C_SCHEMA_VERSION
    profile_version: str = SLICE43C_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


@dataclass(frozen=True, slots=True)
class SourceAdmissionResult:
    admission_result_id: str
    admission_result_digest: str
    status: SourceAdmissionStatus
    rejection_codes: tuple[SourceAdmissionCode, ...]
    reason_refs: tuple[str, ...]
    request_ref: str
    source_closeout_result_ref: str
    admission_package: EchoValidationAdmissionPackage | None
    source_admitted: bool
    exact_accepted_slice42_ancestry: bool
    selected_governed_meaning_admitted: bool
    governed_outward_meaning_admitted: bool
    realized_expression_candidate_admitted: bool
    msm_v1_expression_link_admitted: bool
    slice42_trace_and_custody_admitted: bool
    raw_text_admitted: bool
    orphan_expression_admitted: bool
    recomputed_or_fabricated_identity_admitted: bool
    unsupported_version_admitted: bool
    missing_link_admitted: bool
    already_delivered_candidate_admitted: bool
    unauthorized_candidate_admitted: bool
    meaning_preservation_comparison_performed: bool
    drift_classification_performed: bool
    echo_disposition_decided: bool
    rejection_or_containment_issued: bool
    msm_v1_modified_or_integrated: bool
    delivered: bool
    downstream_authority_created: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE43C_SCHEMA_VERSION
    profile_version: str = SLICE43C_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


__all__ = tuple(name for name in globals() if not name.startswith("_"))
