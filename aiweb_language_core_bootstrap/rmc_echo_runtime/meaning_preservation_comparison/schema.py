"""Immutable Slice 43D meaning-preservation comparison records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...outward_expression_runtime.disabled_outward_expression_closeout import (
    DisabledOutwardExpressionCloseoutResult,
)
from ..authorized_source_admission import SourceAdmissionResult
from .authority import (
    DIGEST_ALGORITHM,
    FINDING_OUTCOME_VALUES,
    SLICE43D_PROFILE_VERSION,
    SLICE43D_SCHEMA_VERSION,
    SNAPSHOT_SIDE_VALUES,
)


class ComparisonExecutionStatus(str, Enum):
    FINDINGS_CREATED = "FINDINGS_CREATED"
    HELD_INVALID_REQUEST = "HELD_INVALID_REQUEST"
    HELD_SOURCE_NOT_ADMITTED = "HELD_SOURCE_NOT_ADMITTED"
    HELD_UNSUPPORTED_VERSION = "HELD_UNSUPPORTED_VERSION"
    HELD_IDENTITY_INVALID = "HELD_IDENTITY_INVALID"
    HELD_MISSING_REQUIRED_VALUE = "HELD_MISSING_REQUIRED_VALUE"
    HELD_INCONSISTENT_ANCESTRY = "HELD_INCONSISTENT_ANCESTRY"


class ComparisonCode(str, Enum):
    REQUEST_TYPE_INVALID = "request_type_invalid"
    REQUEST_ID_INVALID = "request_id_invalid"
    REQUEST_OPERATION_INVALID = "request_operation_invalid"
    RAW_TEXT_PROHIBITED = "raw_text_prohibited"
    EXPLICIT_REQUEST_REQUIRED = "explicit_request_required"
    SOURCE_ADMISSION_RESULT_TYPE_INVALID = "source_admission_result_type_invalid"
    SOURCE_NOT_ADMITTED = "source_not_admitted"
    SOURCE_CLOSEOUT_TYPE_INVALID = "source_closeout_type_invalid"
    SOURCE_ANCESTRY_INVALID = "source_ancestry_invalid"
    UNSUPPORTED_VERSION = "unsupported_version"
    RECOMPUTED_OR_FABRICATED_IDENTITY = "recomputed_or_fabricated_identity"
    MISSING_REQUIRED_VALUE = "missing_required_value"
    INCONSISTENT_ANCESTRY = "inconsistent_ancestry"
    DIMENSION_INVALID = "dimension_invalid"
    SNAPSHOT_INVALID = "snapshot_invalid"
    FINDING_INVALID = "finding_invalid"
    PACKAGE_INVALID = "package_invalid"
    RESULT_INVALID = "result_invalid"
    DOWNSTREAM_AUTHORITY_PROHIBITED = "downstream_authority_prohibited"


class MeaningPreservationDimension(str, Enum):
    SEMANTIC_CONTENT = "semantic_content"
    COMMUNICATIVE_PURPOSE = "communicative_purpose"
    CLAIM_STATUS = "claim_status"
    SCOPE = "scope"
    CERTAINTY = "certainty"
    EVIDENCE_STATUS = "evidence_status"
    CAVEATS_AND_LIMITATIONS = "caveats_and_limitations"
    REFUSAL_STATE = "refusal_state"
    UNRESOLVED_CONDITIONS = "unresolved_conditions"
    ACTION_STATUS = "action_status"
    MEMORY_STATUS = "memory_status"
    DELIVERY_STATUS = "delivery_status"
    REQUIRED_NEXT_STEP_OR_HOLD_STATUS = "required_next_step_or_hold_status"


class FindingOutcome(str, Enum):
    PRESERVED = FINDING_OUTCOME_VALUES[0]
    CHANGED = FINDING_OUTCOME_VALUES[1]
    MISSING = FINDING_OUTCOME_VALUES[2]
    UNSUPPORTED = FINDING_OUTCOME_VALUES[3]
    CONFLICTED = FINDING_OUTCOME_VALUES[4]
    INDETERMINATE = FINDING_OUTCOME_VALUES[5]


class SnapshotSide(str, Enum):
    SOURCE = SNAPSHOT_SIDE_VALUES[0]
    PROPOSED_EXPRESSION = SNAPSHOT_SIDE_VALUES[1]


@dataclass(frozen=True, slots=True)
class ComparisonIssue:
    path: str
    code: ComparisonCode
    detail: str


@dataclass(frozen=True, slots=True)
class ComparisonValidationReport:
    issues: tuple[ComparisonIssue, ...]
    schema_version: str = SLICE43D_SCHEMA_VERSION
    profile_version: str = SLICE43D_PROFILE_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class ComparisonValidationError(ValueError):
    def __init__(self, report: ComparisonValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 43D comparison validation failed")


@dataclass(frozen=True, slots=True)
class MeaningPreservationComparisonRequest:
    request_id: str
    source_admission_result_ref: str
    source_closeout_result_ref: str
    requested_operation: str
    raw_text: str | None
    explicit_comparison_request: bool
    schema_version: str = SLICE43D_SCHEMA_VERSION
    profile_version: str = SLICE43D_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class DimensionValueSnapshot:
    snapshot_id: str
    dimension: MeaningPreservationDimension
    side: SnapshotSide
    field_paths: tuple[str, ...]
    values: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    supported: bool
    conflict_refs: tuple[str, ...]
    indeterminate_refs: tuple[str, ...]
    value_digest: str
    schema_version: str = SLICE43D_SCHEMA_VERSION
    profile_version: str = SLICE43D_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


@dataclass(frozen=True, slots=True)
class MeaningPreservationFinding:
    finding_id: str
    comparison_request_ref: str
    source_admission_result_ref: str
    validation_input_boundary_ref: str
    dimension: MeaningPreservationDimension
    outcome: FindingOutcome
    source_snapshot: DimensionValueSnapshot
    proposed_snapshot: DimensionValueSnapshot
    comparison_rule_ref: str
    evidence_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    exact_value_equality: bool
    required_value_missing: bool
    finding_only: bool
    drift_classified: bool
    materiality_decided: bool
    echo_disposition_decided: bool
    rejection_or_containment_issued: bool
    expression_rewritten: bool
    schema_version: str = SLICE43D_SCHEMA_VERSION
    profile_version: str = SLICE43D_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class MeaningPreservationComparisonPackage:
    comparison_package_id: str
    comparison_package_digest: str
    comparison_request_ref: str
    source_admission_result_ref: str
    source_admission_package_ref: str
    source_closeout_result_ref: str
    validation_input_boundary_ref: str
    findings: tuple[MeaningPreservationFinding, ...]
    comparison_dimension_values: tuple[str, ...]
    finding_count: int
    comparison_performed: bool
    findings_created: bool
    aggregate_pass_rejected_contained_decided: bool
    drift_classification_performed: bool
    materiality_decided: bool
    echo_disposition_decided: bool
    rejection_or_containment_issued: bool
    expression_rewritten: bool
    msm_v1_modified_or_integrated: bool
    delivery_authorized_or_performed: bool
    truth_evidence_permission_execution_authority: bool
    route_api_network_filesystem_memory_tool_action_authority: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE43D_SCHEMA_VERSION
    profile_version: str = SLICE43D_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


@dataclass(frozen=True, slots=True)
class MeaningPreservationComparisonResult:
    comparison_result_id: str
    comparison_result_digest: str
    status: ComparisonExecutionStatus
    issue_codes: tuple[ComparisonCode, ...]
    reason_refs: tuple[str, ...]
    comparison_request_ref: str
    source_admission_result_ref: str
    source_closeout_result_ref: str
    comparison_package: MeaningPreservationComparisonPackage | None
    comparison_performed: bool
    findings_created: bool
    dimension_finding_count: int
    preserved_finding_count: int
    changed_finding_count: int
    missing_finding_count: int
    unsupported_finding_count: int
    conflicted_finding_count: int
    indeterminate_finding_count: int
    aggregate_pass_rejected_contained_decided: bool
    drift_classification_performed: bool
    materiality_decided: bool
    echo_disposition_decided: bool
    rejection_or_containment_issued: bool
    expression_rewritten: bool
    msm_v1_modified_or_integrated: bool
    delivered: bool
    downstream_authority_created: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    schema_version: str = SLICE43D_SCHEMA_VERSION
    profile_version: str = SLICE43D_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


__all__ = tuple(name for name in globals() if not name.startswith("_"))
