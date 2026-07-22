"""Immutable Slice 43G MSM-v1 Echo-validation integration records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...meaning_structure_manifest import (
    DeliveryContainmentLinkRecord,
    ExternalAuthorityReferenceRecord,
    MeaningStructureManifestV1,
    SemanticTransitionTraceRecord,
    ValidationLinkRecord,
)
from ...outward_expression_runtime.msm_outward_expression_integration import (
    MsmOutwardExpressionIntegrationInput,
    MsmOutwardExpressionIntegrationResult,
)
from ..drift_materiality_classification import DriftClassificationResult
from ..echo_disposition import EchoDisposition, EchoDispositionResult
from .authority import (
    DIGEST_ALGORITHM,
    SLICE43G_COMPANION_VERSION,
    SLICE43G_PROFILE_VERSION,
    SLICE43G_RECEIPT_VERSION,
    SLICE43G_SCHEMA_VERSION,
)


class MsmEchoValidationIntegrationStatus(str, Enum):
    SUCCESSOR_CREATED = "SUCCESSOR_CREATED"
    HELD_INVALID_INPUT = "HELD_INVALID_INPUT"


class MsmEchoValidationIntegrationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_TEXT = "invalid_text"
    INVALID_VERSION = "invalid_version"
    IDENTITY_MISMATCH = "identity_mismatch"
    SOURCE_42G_INVALID = "source_42g_invalid"
    SOURCE_43E_INVALID = "source_43e_invalid"
    SOURCE_43F_INVALID = "source_43f_invalid"
    SOURCE_CHAIN_MISMATCH = "source_chain_mismatch"
    SOURCE_MANIFEST_INVALID = "source_manifest_invalid"
    DORMANT_RECORD_MISMATCH = "dormant_record_mismatch"
    DISPOSITION_MISMATCH = "disposition_mismatch"
    VALIDATION_LINK_MISMATCH = "validation_link_mismatch"
    CONTAINMENT_CUSTODY_MISMATCH = "containment_custody_mismatch"
    REJECTION_CUSTODY_MISMATCH = "rejection_custody_mismatch"
    TRACE_MISMATCH = "trace_mismatch"
    SUCCESSOR_MANIFEST_INVALID = "successor_manifest_invalid"
    RETENTION_MISMATCH = "retention_mismatch"
    DELIVERY_LINK_PROHIBITED = "delivery_link_prohibited"
    PROHIBITED_AUTHORITY = "prohibited_authority"
    RESULT_INVALID = "result_invalid"


@dataclass(frozen=True, slots=True)
class MsmEchoValidationIntegrationIssue:
    path: str
    code: MsmEchoValidationIntegrationCode
    detail: str


@dataclass(frozen=True, slots=True)
class MsmEchoValidationIntegrationReport:
    issues: tuple[MsmEchoValidationIntegrationIssue, ...]
    schema_version: str = SLICE43G_SCHEMA_VERSION
    profile_version: str = SLICE43G_PROFILE_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class MsmEchoValidationIntegrationError(ValueError):
    def __init__(self, report: MsmEchoValidationIntegrationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 43G integration validation failed")


@dataclass(frozen=True, slots=True)
class MsmEchoValidationIntegrationInput:
    integration_input_id: str
    source_42g_input: MsmOutwardExpressionIntegrationInput
    source_42g_result: MsmOutwardExpressionIntegrationResult
    source_43e_classification_result: DriftClassificationResult
    source_43f_disposition_result: EchoDispositionResult
    requested_operation: str
    explicit_integration_request: bool
    raw_text: str | None
    validation_transition_reason: str
    containment_transition_reason: str
    validation_link_creation_requested: bool
    containment_custody_requested: bool
    rejection_custody_requested: bool
    delivery_link_creation_requested: bool
    candidate_rewrite_requested: bool
    drift_suppression_requested: bool
    delivery_requested: bool
    echoforge_requested: bool
    model_or_similarity_authority_requested: bool
    truth_evidence_permission_execution_requested: bool
    route_api_network_filesystem_memory_tool_action_requested: bool
    msm_schema_rewrite_requested: bool
    gp014_supersession_requested: bool
    schema_version: str = SLICE43G_SCHEMA_VERSION
    profile_version: str = SLICE43G_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class MsmEchoValidationCustodyCompanionV1:
    companion_id: str
    companion_version: str
    integration_input_ref: str
    source_manifest_ref: str
    successor_manifest_ref: str
    source_expression_link_ref: str
    source_expression_candidate_ref: str
    source_43e_classification_result_ref: str
    source_43f_disposition_result_ref: str
    source_43f_disposition_package_ref: str
    source_43f_disposition_record_ref: str
    validation_authority_reference_ref: str
    containment_authority_reference_ref: str | None
    exact_validation_link_ref: str
    exact_validation_disposition: EchoDisposition
    validation_trace_ref: str
    rejection_record_ref: str | None
    containment_record_ref: str | None
    containment_link_ref: str | None
    containment_trace_ref: str | None
    authorized_trace_refs: tuple[str, ...]
    source_validation_link_refs: tuple[str, ...]
    successor_validation_link_refs: tuple[str, ...]
    source_delivery_or_containment_refs: tuple[str, ...]
    successor_delivery_or_containment_refs: tuple[str, ...]
    immutable_successor: bool
    additive_only: bool
    exact_chain_proved: bool
    dormant_validation_record_used: bool
    rejection_custody_preserved: bool
    containment_custody_preserved: bool
    delivery_link_created: bool
    source_manifest_mutated: bool
    schema_version: str = SLICE43G_SCHEMA_VERSION
    profile_version: str = SLICE43G_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class MsmEchoValidationIntegrationReceiptV1:
    receipt_id: str
    receipt_version: str
    integration_input_ref: str
    source_manifest_ref: str
    successor_manifest_ref: str
    source_manifest_sha256: str
    successor_manifest_sha256: str
    validation_authority_reference_ref: str
    containment_authority_reference_ref: str | None
    validation_link_ref: str
    validation_disposition: EchoDisposition
    validation_receipt_ref: str
    validation_trace_ref: str
    rejection_record_ref: str | None
    containment_record_ref: str | None
    containment_link_ref: str | None
    containment_trace_ref: str | None
    authorized_trace_refs: tuple[str, ...]
    delivery_link_created: bool
    delivery_authorized_or_performed: bool
    candidate_rewritten_or_repaired: bool
    drift_removed_downgraded_or_suppressed: bool
    echoforge_called: bool
    model_or_similarity_authority_used: bool
    truth_evidence_permission_execution_authority: bool
    route_api_network_filesystem_memory_tool_action_authority: bool
    msm_schema_modified: bool
    gp014_superseded: bool
    schema_version: str = SLICE43G_SCHEMA_VERSION
    profile_version: str = SLICE43G_PROFILE_VERSION


@dataclass(frozen=True, slots=True)
class MsmEchoValidationIntegrationResult:
    result_id: str
    result_digest: str
    status: MsmEchoValidationIntegrationStatus
    issue_codes: tuple[MsmEchoValidationIntegrationCode, ...]
    reason_refs: tuple[str, ...]
    integration_input_ref: str
    source_manifest: MeaningStructureManifestV1
    successor_manifest: MeaningStructureManifestV1
    validation_authority_reference_record: ExternalAuthorityReferenceRecord | None
    containment_authority_reference_record: ExternalAuthorityReferenceRecord | None
    validation_link_record: ValidationLinkRecord | None
    validation_transition_trace: SemanticTransitionTraceRecord | None
    containment_link_record: DeliveryContainmentLinkRecord | None
    containment_transition_trace: SemanticTransitionTraceRecord | None
    companion: MsmEchoValidationCustodyCompanionV1 | None
    receipt: MsmEchoValidationIntegrationReceiptV1 | None
    validation_disposition: EchoDisposition | None
    immutable_successor_created: bool
    additive_only: bool
    exact_chain_proved: bool
    validation_link_created: bool
    rejection_custody_preserved: bool
    containment_custody_preserved: bool
    delivery_link_created: bool
    delivery_authorized_or_performed: bool
    candidate_rewritten_or_repaired: bool
    drift_removed_downgraded_or_suppressed: bool
    echoforge_called: bool
    model_or_similarity_authority_used: bool
    truth_evidence_permission_execution_authority: bool
    route_api_network_filesystem_memory_tool_action_authority: bool
    msm_schema_modified: bool
    gp014_superseded: bool
    schema_version: str = SLICE43G_SCHEMA_VERSION
    profile_version: str = SLICE43G_PROFILE_VERSION
    digest_algorithm: str = DIGEST_ALGORITHM


__all__ = tuple(name for name in globals() if not name.startswith("_"))
