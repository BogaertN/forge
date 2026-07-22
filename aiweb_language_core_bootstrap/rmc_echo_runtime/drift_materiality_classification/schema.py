"""Immutable Slice 43E drift and materiality classification records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..meaning_preservation_comparison import (
    FindingOutcome,
    MeaningPreservationComparisonResult,
    MeaningPreservationDimension,
)
from .authority import (
    CLASSIFICATION_STATE_VALUES,
    DIGEST_ALGORITHM,
    DRIFT_KIND_VALUES,
    MATERIALITY_VALUES,
    SLICE43E_PROFILE_VERSION,
    SLICE43E_SCHEMA_VERSION,
)


class DriftClassificationExecutionStatus(str, Enum):
    FINDINGS_CREATED = "FINDINGS_CREATED"
    HELD_INVALID_REQUEST = "HELD_INVALID_REQUEST"
    HELD_COMPARISON_NOT_READY = "HELD_COMPARISON_NOT_READY"
    HELD_UNSUPPORTED_VERSION = "HELD_UNSUPPORTED_VERSION"
    HELD_IDENTITY_INVALID = "HELD_IDENTITY_INVALID"
    HELD_INCONSISTENT_ANCESTRY = "HELD_INCONSISTENT_ANCESTRY"
    HELD_MISSING_REQUIRED_VALUE = "HELD_MISSING_REQUIRED_VALUE"


class DriftClassificationCode(str, Enum):
    REQUEST_TYPE_INVALID = "request_type_invalid"
    REQUEST_ID_INVALID = "request_id_invalid"
    REQUEST_OPERATION_INVALID = "request_operation_invalid"
    RAW_TEXT_PROHIBITED = "raw_text_prohibited"
    EXPLICIT_REQUEST_REQUIRED = "explicit_request_required"
    COMPARISON_RESULT_TYPE_INVALID = "comparison_result_type_invalid"
    COMPARISON_NOT_READY = "comparison_not_ready"
    COMPARISON_PACKAGE_MISSING = "comparison_package_missing"
    COMPARISON_RESULT_INVALID = "comparison_result_invalid"
    COMPARISON_FINDING_INVALID = "comparison_finding_invalid"
    UNSUPPORTED_VERSION = "unsupported_version"
    RECOMPUTED_OR_FABRICATED_IDENTITY = "recomputed_or_fabricated_identity"
    INCONSISTENT_ANCESTRY = "inconsistent_ancestry"
    MISSING_REQUIRED_VALUE = "missing_required_value"
    DRIFT_KIND_INVALID = "drift_kind_invalid"
    MATERIALITY_INVALID = "materiality_invalid"
    CLASSIFICATION_INVALID = "classification_invalid"
    PACKAGE_INVALID = "package_invalid"
    RESULT_INVALID = "result_invalid"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"


class DriftKind(str, Enum):
    OMITTED_MEANING = DRIFT_KIND_VALUES[0]
    CLAIM_STRENGTHENING = DRIFT_KIND_VALUES[1]
    SCOPE_EXPANSION = DRIFT_KIND_VALUES[2]
    CERTAINTY_UPGRADE = DRIFT_KIND_VALUES[3]
    EVIDENCE_STATUS_UPGRADE = DRIFT_KIND_VALUES[4]
    CAVEAT_OMISSION = DRIFT_KIND_VALUES[5]
    REFUSAL_SOFTENING = DRIFT_KIND_VALUES[6]
    AMBIGUITY_ERASURE = DRIFT_KIND_VALUES[7]
    UNRESOLVED_STATE_ERASURE = DRIFT_KIND_VALUES[8]
    INVENTED_FACT = DRIFT_KIND_VALUES[9]
    INVENTED_EVIDENCE = DRIFT_KIND_VALUES[10]
    AUTHORITY_ESCALATION = DRIFT_KIND_VALUES[11]
    ACTION_STATUS_DISTORTION = DRIFT_KIND_VALUES[12]
    MEMORY_STATUS_DISTORTION = DRIFT_KIND_VALUES[13]
    DELIVERY_STATUS_DISTORTION = DRIFT_KIND_VALUES[14]
    ANCESTRY_MISMATCH = DRIFT_KIND_VALUES[15]
    UNSUPPORTED_SURFACE_ADDITION = DRIFT_KIND_VALUES[16]


class MaterialityState(str, Enum):
    NOT_APPLICABLE = MATERIALITY_VALUES[0]
    NON_MATERIAL = MATERIALITY_VALUES[1]
    MATERIAL = MATERIALITY_VALUES[2]
    UNSUPPORTED = MATERIALITY_VALUES[3]
    CONFLICTED = MATERIALITY_VALUES[4]
    INDETERMINATE = MATERIALITY_VALUES[5]


class DriftClassificationState(str, Enum):
    NO_DRIFT = CLASSIFICATION_STATE_VALUES[0]
    DRIFT_CLASSIFIED = CLASSIFICATION_STATE_VALUES[1]
    CLASSIFICATION_UNSUPPORTED = CLASSIFICATION_STATE_VALUES[2]
    CLASSIFICATION_CONFLICTED = CLASSIFICATION_STATE_VALUES[3]
    CLASSIFICATION_INDETERMINATE = CLASSIFICATION_STATE_VALUES[4]


@dataclass(frozen=True, slots=True)
class DriftClassificationIssue:
    path: str
    code: DriftClassificationCode
    detail: str


@dataclass(frozen=True, slots=True)
class DriftClassificationValidationReport:
    issues: tuple[DriftClassificationIssue, ...]
    schema_version: str = SLICE43E_SCHEMA_VERSION
    profile_version: str = SLICE43E_PROFILE_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class DriftClassificationValidationError(ValueError):
    def __init__(self, report: DriftClassificationValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 43E drift classification validation failed")


@dataclass(frozen=True, slots=True)
class DriftClassificationRequest:
    request_id: str
    comparison_result_ref: str
    comparison_package_ref: str
    requested_operation: str
    raw_text: str | None
    explicit_classification_request: bool
    schema_version: str = SLICE43E_SCHEMA_VERSION
    profile_version: str = SLICE43E_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class DriftMaterialityFinding:
    drift_finding_id: str
    classification_request_ref: str
    comparison_result_ref: str
    comparison_package_ref: str
    comparison_finding_ref: str
    dimension: MeaningPreservationDimension
    comparison_outcome: FindingOutcome
    classification_state: DriftClassificationState
    drift_kinds: tuple[DriftKind, ...]
    materiality: MaterialityState
    source_snapshot_ref: str
    proposed_snapshot_ref: str
    source_values: tuple[str, ...]
    proposed_values: tuple[str, ...]
    source_field_paths: tuple[str, ...]
    proposed_field_paths: tuple[str, ...]
    comparison_evidence_refs: tuple[str, ...]
    comparison_trace_refs: tuple[str, ...]
    classification_rule_refs: tuple[str, ...]
    materiality_rule_ref: str
    materiality_ground_refs: tuple[str, ...]
    ancestry_mismatch_refs: tuple[str, ...]
    finding_only: bool
    text_repaired_or_rewritten: bool
    echo_disposition_decided: bool
    rejection_or_containment_issued: bool
    msm_v1_modified_or_integrated: bool
    delivery_authorized_or_performed: bool
    downstream_authority_created: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE43E_SCHEMA_VERSION
    profile_version: str = SLICE43E_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class DriftClassificationPackage:
    classification_package_id: str
    classification_package_digest: str
    classification_request_ref: str
    comparison_result_ref: str
    comparison_package_ref: str
    drift_findings: tuple[DriftMaterialityFinding, ...]
    admitted_drift_kind_values: tuple[str, ...]
    materiality_values: tuple[str, ...]
    classification_record_count: int
    drift_finding_count: int
    material_finding_count: int
    non_material_finding_count: int
    not_applicable_finding_count: int
    unsupported_finding_count: int
    conflicted_finding_count: int
    indeterminate_finding_count: int
    drift_classification_performed: bool
    materiality_findings_created: bool
    aggregate_pass_rejected_contained_decided: bool
    echo_disposition_decided: bool
    rejection_or_containment_issued: bool
    text_repaired_or_rewritten: bool
    msm_v1_modified_or_integrated: bool
    delivery_authorized_or_performed: bool
    truth_evidence_permission_execution_authority: bool
    route_api_network_filesystem_memory_tool_action_authority: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE43E_SCHEMA_VERSION
    profile_version: str = SLICE43E_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


@dataclass(frozen=True, slots=True)
class DriftClassificationResult:
    classification_result_id: str
    classification_result_digest: str
    status: DriftClassificationExecutionStatus
    issue_codes: tuple[DriftClassificationCode, ...]
    reason_refs: tuple[str, ...]
    classification_request_ref: str
    comparison_result_ref: str
    comparison_package_ref: str
    classification_package: DriftClassificationPackage | None
    drift_classification_performed: bool
    materiality_findings_created: bool
    classification_record_count: int
    drift_finding_count: int
    material_finding_count: int
    non_material_finding_count: int
    not_applicable_finding_count: int
    unsupported_finding_count: int
    conflicted_finding_count: int
    indeterminate_finding_count: int
    aggregate_pass_rejected_contained_decided: bool
    echo_disposition_decided: bool
    rejection_or_containment_issued: bool
    text_repaired_or_rewritten: bool
    msm_v1_modified_or_integrated: bool
    delivered: bool
    downstream_authority_created: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE43E_SCHEMA_VERSION
    profile_version: str = SLICE43E_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


__all__ = tuple(name for name in globals() if not name.startswith("_"))
