"""Immutable Slice 42F deterministic surface-realization records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..expression_plan_construction.schema import (
    ExpressionPlanConstructionInput,
    ExpressionPlanConstructionResult,
    ExpressionPlanDisposition,
)
from .authority import (
    DIGEST_ALGORITHM,
    SLICE42F_PROFILE_KEY,
    SLICE42F_PROFILE_VERSION,
    SLICE42F_RESOURCE_PROFILE_KEY,
    SLICE42F_RESOURCE_PROFILE_VERSION,
    SLICE42F_SCHEMA_VERSION,
)


class SurfaceRealizationDisposition(str, Enum):
    AUTHORIZED_EXPRESSION_CANDIDATE = "authorized_expression_candidate"
    BLOCKED_EXPRESSION_CANDIDATE = "blocked_expression_candidate"
    REFUSAL_EXPRESSION_CANDIDATE = "refusal_expression_candidate"
    UNRESOLVED_EXPRESSION_CANDIDATE = "unresolved_expression_candidate"
    HELD_PENDING_AUTHORITY = "held_pending_authority"
    INDETERMINATE = "indeterminate"


class ControlledRealizationResourceKind(str, Enum):
    DISPOSITION_TEMPLATE = "disposition_template"
    AUTHORIZED_CLAIM_TEXT = "authorized_claim_text"


class SurfaceRealizationFindingKind(str, Enum):
    EXACT_SLICE42E_PLAN_CONFIRMED = "exact_slice42e_plan_confirmed"
    EXPLICIT_REALIZATION_AUTHORITY_CONFIRMED = "explicit_realization_authority_confirmed"
    CONTROLLED_RESOURCES_CONFIRMED = "controlled_resources_confirmed"
    AUTHORIZED_CLAIM_NOT_STRENGTHENED = "authorized_claim_not_strengthened"
    CERTAINTY_AND_EVIDENCE_NOT_UPGRADED = "certainty_and_evidence_not_upgraded"
    CAVEATS_REFUSAL_AND_UNRESOLVED_VISIBLE = "caveats_refusal_and_unresolved_visible"
    DETERMINISTIC_TRACE_AND_RECEIPT_CREATED = "deterministic_trace_and_receipt_created"
    UNVALIDATED_NONDELIVERABLE_BOUNDARY_CONFIRMED = "unvalidated_nondeliverable_boundary_confirmed"


class SurfaceRealizationValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    RECORD_INVALID = "record_invalid"
    IDENTITY_MISMATCH = "identity_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    SLICE42E_STATE_MISMATCH = "slice42e_state_mismatch"
    REALIZATION_AUTHORITY_MISSING = "realization_authority_missing"
    REALIZATION_AUTHORITY_MISMATCH = "realization_authority_mismatch"
    RESOURCE_BUNDLE_MISMATCH = "resource_bundle_mismatch"
    UNADMITTED_RESOURCE = "unadmitted_resource"
    MISSING_TEMPLATE = "missing_template"
    MISSING_CLAIM_RESOURCE = "missing_claim_resource"
    DISPOSITION_MISMATCH = "disposition_mismatch"
    TEXT_MISMATCH = "text_mismatch"
    TEXT_HASH_MISMATCH = "text_hash_mismatch"
    PRESERVATION_MISMATCH = "preservation_mismatch"
    TRACE_MISMATCH = "trace_mismatch"
    RECEIPT_MISMATCH = "receipt_mismatch"
    FINDING_MISMATCH = "finding_mismatch"
    PROHIBITED_REQUEST = "prohibited_request"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"


@dataclass(frozen=True, slots=True)
class SurfaceRealizationValidationIssue:
    path: str
    code: SurfaceRealizationValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class SurfaceRealizationValidationReport:
    issues: tuple[SurfaceRealizationValidationIssue, ...]
    schema_version: str = SLICE42F_SCHEMA_VERSION

    @property
    def ok(self) -> bool:
        return not self.issues


class SurfaceRealizationValidationError(ValueError):
    def __init__(self, report: SurfaceRealizationValidationReport) -> None:
        self.report = report
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}:{issue.detail}"
            for issue in report.issues
        )
        super().__init__(detail or "Slice 42F surface-realization validation failed")


@dataclass(frozen=True, slots=True)
class ControlledRealizationResourceRecord:
    resource_record_id: str
    resource_key: str
    resource_kind: ControlledRealizationResourceKind
    resource_text: str
    bound_selected_meaning_ref: str | None
    permitted_plan_dispositions: tuple[ExpressionPlanDisposition, ...]
    authority_ref: str
    resource_version: str
    admitted: bool
    deterministic: bool
    external_resource: bool
    model_generated: bool
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ControlledRealizationResourceBundle:
    resource_bundle_id: str
    profile_key: str
    profile_version: str
    records: tuple[ControlledRealizationResourceRecord, ...]
    admitted_rule_refs: tuple[str, ...]
    resource_authority_receipt_ref: str
    deterministic: bool
    external_resource_loaded: bool
    model_or_similarity_authority_used: bool
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SurfaceRealizationAuthorityRecord:
    realization_authority_record_id: str
    authority_key: str
    authority_version: str
    plan_input_ref: str
    plan_result_ref: str
    expression_plan_ref: str
    selected_meaning_source_custody_ref: str
    source_plan_disposition: ExpressionPlanDisposition
    permitted_realization_disposition: SurfaceRealizationDisposition
    admitted_rule_refs: tuple[str, ...]
    controlled_resource_bundle_ref: str
    predecessor_receipt_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    disposition_authority_ref: str
    realization_authority_receipt_ref: str
    authority_active: bool
    surface_realization_authorized: bool
    authorized_claim_realization_authorized: bool
    containment_realization_authorized: bool
    expression_candidate_creation_authorized: bool
    governed_outward_meaning_construction_authorized: bool
    msm_v1_mutation_or_integration_authorized: bool
    echo_validation_authorized: bool
    delivery_authorized: bool
    truth_evidence_permission_execution_authorized: bool
    route_api_network_filesystem_memory_tool_action_authorized: bool
    external_resource_or_model_authority: bool
    gp014_supersession_authorized: bool
    profile_key: str = SLICE42F_PROFILE_KEY
    profile_version: str = SLICE42F_PROFILE_VERSION
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SurfaceRealizationInput:
    realization_input_id: str
    plan_input: ExpressionPlanConstructionInput
    plan_result: ExpressionPlanConstructionResult
    realization_authority_record: SurfaceRealizationAuthorityRecord
    controlled_resource_bundle: ControlledRealizationResourceBundle
    realization_reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    free_form_generation_requested: bool
    unadmitted_rule_requested: bool
    unadmitted_resource_requested: bool
    claim_invention_requested: bool
    claim_strengthening_requested: bool
    scope_expansion_requested: bool
    certainty_upgrade_requested: bool
    evidence_status_upgrade_requested: bool
    limitation_omission_requested: bool
    qualification_omission_requested: bool
    caveat_omission_requested: bool
    refusal_softening_requested: bool
    unresolved_resolution_requested: bool
    ambiguity_erasure_requested: bool
    unsupported_state_erasure_requested: bool
    selected_meaning_rewrite_requested: bool
    downstream_authority_requested: bool
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class UnvalidatedExpressionCandidate:
    expression_candidate_id: str
    expression_candidate_digest: str
    realization_input_ref: str
    plan_result_ref: str
    expression_plan_ref: str
    realization_authority_record_ref: str
    controlled_resource_bundle_ref: str
    selected_meaning_source_custody_ref: str
    source_plan_disposition: ExpressionPlanDisposition
    disposition: SurfaceRealizationDisposition
    realized_text: str
    realized_text_sha256: str
    segments: tuple[str, ...]
    selected_meaning_refs: tuple[str, ...]
    active_scope_refs: tuple[str, ...]
    certainty_level_refs: tuple[str, ...]
    evidence_status_refs: tuple[str, ...]
    meaning_modifier_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    required_qualification_refs: tuple[str, ...]
    required_caveat_refs: tuple[str, ...]
    refusal_relevant_boundary_refs: tuple[str, ...]
    unresolved_condition_refs: tuple[str, ...]
    ambiguity_refs: tuple[str, ...]
    unsupported_state_refs: tuple[str, ...]
    memory_authority_refs: tuple[str, ...]
    external_resource_status_refs: tuple[str, ...]
    delivery_authority_refs: tuple[str, ...]
    privacy_identity_boundary_refs: tuple[str, ...]
    preservation_class_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    applied_rule_refs: tuple[str, ...]
    applied_resource_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    exact_slice42e_plan_verified: bool
    exact_realization_authority_verified: bool
    admitted_rules_only: bool
    controlled_resources_only: bool
    authorized_claim_not_strengthened: bool
    certainty_not_upgraded: bool
    evidence_status_not_upgraded: bool
    caveats_visible: bool
    unresolved_states_visible: bool
    refusal_language_produced: bool
    deterministic_surface_realization_performed: bool
    human_readable_text_produced: bool
    expression_candidate_created: bool
    unvalidated_expression_candidate: bool
    echo_validation_performed: bool
    echo_approved: bool
    delivery_authorized: bool
    delivered: bool
    governed_outward_meaning_created: bool
    msm_v1_modified_or_integrated: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_or_api_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed_or_written: bool
    filesystem_or_network_accessed: bool
    external_resource_loaded: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SurfaceRealizationTrace:
    realization_trace_id: str
    realization_input_ref: str
    expression_plan_ref: str
    expression_candidate_ref: str
    realized_text_sha256: str
    segment_sha256s: tuple[str, ...]
    applied_rule_refs: tuple[str, ...]
    applied_resource_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    predecessor_trace_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    deterministic: bool
    semantic_strengthening_detected: bool
    certainty_upgrade_detected: bool
    evidence_upgrade_detected: bool
    omission_detected: bool
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SurfaceRealizationReceipt:
    realization_receipt_id: str
    realization_input_ref: str
    expression_plan_ref: str
    expression_candidate_ref: str
    realization_trace_ref: str
    realization_authority_record_ref: str
    controlled_resource_bundle_ref: str
    realized_text_sha256: str
    required_law_refs: tuple[str, ...]
    prohibited_consequence_refs: tuple[str, ...]
    deterministic: bool
    surface_realization_performed: bool
    expression_candidate_created: bool
    unvalidated_expression_candidate: bool
    echo_validated: bool
    echo_approved: bool
    delivery_authorized: bool
    delivered: bool
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SurfaceRealizationFinding:
    finding_id: str
    realization_input_ref: str
    expression_candidate_ref: str | None
    finding_kind: SurfaceRealizationFindingKind
    basis_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE42F_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class SurfaceRealizationResult:
    result_id: str
    result_digest: str
    realization_input_ref: str
    expression_candidate: UnvalidatedExpressionCandidate | None
    realization_trace: SurfaceRealizationTrace | None
    realization_receipt: SurfaceRealizationReceipt | None
    findings: tuple[SurfaceRealizationFinding, ...]
    required_law_refs: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    prohibited_authority: tuple[str, ...]
    source_plan_disposition: ExpressionPlanDisposition
    disposition: SurfaceRealizationDisposition
    surface_realization_performed: bool
    human_readable_text_produced: bool
    expression_candidate_created: bool
    refusal_language_produced: bool
    authorized_claim_not_strengthened: bool
    certainty_not_upgraded: bool
    evidence_status_not_upgraded: bool
    caveats_and_unresolved_states_visible: bool
    deterministic_trace_created: bool
    deterministic_receipt_created: bool
    unvalidated_expression_candidate: bool
    held_pending_authority: bool
    indeterminate: bool
    governed_outward_meaning_created: bool
    msm_v1_modified_or_integrated: bool
    echo_validation_performed: bool
    echo_approved: bool
    delivery_authorized: bool
    delivered: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_or_api_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed_or_written: bool
    filesystem_or_network_accessed: bool
    external_resource_loaded: bool
    model_or_similarity_authority_used: bool
    gp014_superseded: bool
    digest_algorithm: str = DIGEST_ALGORITHM
    schema_version: str = SLICE42F_SCHEMA_VERSION


__all__ = (
    "ControlledRealizationResourceBundle",
    "ControlledRealizationResourceKind",
    "ControlledRealizationResourceRecord",
    "SurfaceRealizationAuthorityRecord",
    "SurfaceRealizationDisposition",
    "SurfaceRealizationFinding",
    "SurfaceRealizationFindingKind",
    "SurfaceRealizationInput",
    "SurfaceRealizationReceipt",
    "SurfaceRealizationResult",
    "SurfaceRealizationTrace",
    "SurfaceRealizationValidationCode",
    "SurfaceRealizationValidationError",
    "SurfaceRealizationValidationIssue",
    "SurfaceRealizationValidationReport",
    "UnvalidatedExpressionCandidate",
)
