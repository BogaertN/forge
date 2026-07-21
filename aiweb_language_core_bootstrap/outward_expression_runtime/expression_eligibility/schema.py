"""Immutable Slice 42C admission, authority, finding, and result records."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ...disabled_selected_meaning_closeout.schema import DisabledSelectedMeaningCloseoutResult
from ..schema import SelectedMeaningExpressionSourceCustodyRecord, OutwardExpressionAuthorityRequirementRecord
from ..governed_lifecycle.schema import OutwardExpressionGovernanceBundle
from .authority import (
    DIGEST_ALGORITHM, SLICE42C_GOVERNING_AUTHORITY_REFS, SLICE42C_OUTCOME_VALUES,
    SLICE42C_PERMANENT_BOUNDARIES, SLICE42C_PROFILE_KEY, SLICE42C_PROFILE_VERSION,
    SLICE42C_PROHIBITED_AUTHORITY, SLICE42C_SCHEMA_VERSION,
)

class ExpressionEligibilityOutcome(str, Enum):
    ELIGIBLE_FOR_EXPRESSION_PLANNING = SLICE42C_OUTCOME_VALUES[0]
    HELD_PENDING_AUTHORITY = SLICE42C_OUTCOME_VALUES[1]
    BLOCKED = SLICE42C_OUTCOME_VALUES[2]
    REFUSAL_PRESERVING = SLICE42C_OUTCOME_VALUES[3]
    UNRESOLVED_PRESERVING = SLICE42C_OUTCOME_VALUES[4]
    INDETERMINATE = SLICE42C_OUTCOME_VALUES[5]

class ExpressionEligibilityFindingKind(str, Enum):
    EXACT_SELECTED_MEANING_CHAIN_CONFIRMED = "exact_selected_meaning_chain_confirmed"
    EXACT_SLICE42A_CUSTODY_CONFIRMED = "exact_slice42a_custody_confirmed"
    SEALED_SLICE42B_GOVERNANCE_CONFIRMED = "sealed_slice42b_governance_confirmed"
    EXPLICIT_OUTWARD_AUTHORITY_CONFIRMED = "explicit_outward_authority_confirmed"
    AUTHORITY_MISSING_OR_INACTIVE = "authority_missing_or_inactive"
    BLOCKED_CONSEQUENCE_PRESERVED = "blocked_consequence_preserved"
    REFUSAL_RELEVANCE_PRESERVED = "refusal_relevance_preserved"
    UNRESOLVED_STATE_PRESERVED = "unresolved_state_preserved"
    INDETERMINATE_FAIL_CLOSED = "indeterminate_fail_closed"

class ExpressionEligibilityValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_SHA256 = "invalid_sha256"
    RECORD_INVALID = "record_invalid"
    IDENTITY_MISMATCH = "identity_mismatch"
    SELECTED_MEANING_CHAIN_MISMATCH = "selected_meaning_chain_mismatch"
    SOURCE_CUSTODY_MISMATCH = "source_custody_mismatch"
    AUTHORITY_REQUIREMENT_MISMATCH = "authority_requirement_mismatch"
    AUTHORITY_RECORD_MISMATCH = "authority_record_mismatch"
    AUTHORITY_SCOPE_MISMATCH = "authority_scope_mismatch"
    AUTHORITY_PURPOSE_MISMATCH = "authority_purpose_mismatch"
    AUTHORITY_RECEIPT_MISMATCH = "authority_receipt_mismatch"
    AUTHORITY_VERSION_MISMATCH = "authority_version_mismatch"
    GOVERNANCE_BUNDLE_MISMATCH = "governance_bundle_mismatch"
    GOVERNANCE_NOT_SEALED = "governance_not_sealed"
    DUPLICATE_ID = "duplicate_id"
    OUTCOME_MISMATCH = "outcome_mismatch"
    FINDING_MISMATCH = "finding_mismatch"
    DOWNSTREAM_AUTHORITY = "downstream_authority"
    CANONICAL_MISMATCH = "canonical_mismatch"

@dataclass(frozen=True, slots=True)
class ExpressionEligibilityValidationIssue:
    path: str
    code: ExpressionEligibilityValidationCode
    detail: str

@dataclass(frozen=True, slots=True)
class ExpressionEligibilityValidationReport:
    issues: tuple[ExpressionEligibilityValidationIssue, ...]
    schema_version: str = SLICE42C_SCHEMA_VERSION
    @property
    def ok(self) -> bool:
        return not self.issues

class ExpressionEligibilityValidationError(ValueError):
    def __init__(self, report: ExpressionEligibilityValidationReport) -> None:
        self.report = report
        detail = "; ".join(f"{x.path}:{x.code.value}:{x.detail}" for x in report.issues)
        super().__init__(detail or "Slice 42C expression-eligibility validation failed")

@dataclass(frozen=True, slots=True)
class OutwardExpressionAuthorityRecord:
    authority_record_id: str
    authority_key: str
    authority_version: str
    selected_meaning_source_custody_ref: str
    authority_requirement_ref: str
    authority_scope_refs: tuple[str, ...]
    expression_purpose_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    disposition_authority_ref: str
    authority_receipt_ref: str
    authority_active: bool
    eligibility_evaluation_authorized: bool
    expression_planning_progression_authorized: bool
    preservation_obligation_projection_authorized: bool
    governed_outward_meaning_construction_authorized: bool
    expression_plan_construction_authorized: bool
    surface_realization_authorized: bool
    msm_v1_mutation_or_integration_authorized: bool
    echo_validation_authorized: bool
    delivery_authorized: bool
    truth_evidence_permission_execution_authorized: bool
    route_api_network_filesystem_memory_tool_action_authorized: bool
    external_resource_or_model_authority: bool
    gp014_supersession_authorized: bool
    profile_key: str = SLICE42C_PROFILE_KEY
    profile_version: str = SLICE42C_PROFILE_VERSION
    schema_version: str = SLICE42C_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class ExpressionEligibilityEvaluationInput:
    evaluation_input_id: str
    selected_meaning_closeout_result: DisabledSelectedMeaningCloseoutResult
    selected_meaning_source_custody: SelectedMeaningExpressionSourceCustodyRecord
    outward_expression_authority_requirement: OutwardExpressionAuthorityRequirementRecord
    outward_expression_governance_bundle: OutwardExpressionGovernanceBundle
    outward_expression_authority_record: OutwardExpressionAuthorityRecord
    evaluation_reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    selected_meaning_alone_claimed_sufficient: bool
    authority_inference_requested: bool
    record_repair_requested: bool
    scope_expansion_requested: bool
    purpose_expansion_requested: bool
    refusal_softening_requested: bool
    unresolved_resolution_requested: bool
    blocked_consequence_erasure_requested: bool
    downstream_authority_requested: bool
    schema_version: str = SLICE42C_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class AuthorizedMeaningAdmissionRecord:
    admission_record_id: str
    evaluation_input_ref: str
    slice41f_closeout_result_ref: str
    slice41f_acceptance_record_ref: str
    slice41e_integration_input_ref: str
    slice41e_integration_result_ref: str
    slice41e_integration_receipt_ref: str
    selected_meaning_source_custody_ref: str
    outward_expression_authority_requirement_ref: str
    outward_expression_governance_bundle_ref: str
    explicit_outward_expression_authority_record_ref: str
    selected_governed_meaning_ref: str
    selected_candidate_ref: str
    selection_receipt_ref: str
    preserved_alternative_refs: tuple[str, ...]
    unresolved_alternative_refs: tuple[str, ...]
    blocked_consequence_refs: tuple[str, ...]
    refusal_relevant_refs: tuple[str, ...]
    exact_selected_meaning_chain_admitted: bool
    exact_outward_expression_authority_admitted: bool
    selected_meaning_alone_sufficient: bool
    structural_validity_grants_expression_authority: bool
    authority_inferred: bool
    record_repaired_or_substituted: bool
    schema_version: str = SLICE42C_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class ExpressionEligibilityFinding:
    finding_id: str
    evaluation_input_ref: str
    admission_record_ref: str
    finding_kind: ExpressionEligibilityFindingKind
    basis_refs: tuple[str, ...]
    reason_refs: tuple[str, ...]
    trace_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    schema_version: str = SLICE42C_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class ExpressionEligibilityResult:
    result_id: str
    result_digest: str
    evaluation_input_ref: str
    admission_record: AuthorizedMeaningAdmissionRecord
    authority_record_ref: str
    authority_requirement_ref: str
    source_custody_ref: str
    governance_bundle_ref: str
    outcome: ExpressionEligibilityOutcome
    findings: tuple[ExpressionEligibilityFinding, ...]
    reason_refs: tuple[str, ...]
    required_law_refs: tuple[str, ...]
    permanent_boundaries: tuple[str, ...]
    prohibited_authority: tuple[str, ...]
    eligibility_evaluated: bool
    eligible_for_expression_planning: bool
    held_pending_authority: bool
    blocked: bool
    refusal_preserving: bool
    unresolved_preserving: bool
    indeterminate: bool
    selected_meaning_chain_admitted: bool
    outward_expression_authority_admitted: bool
    selected_meaning_alone_sufficient: bool
    structural_validity_grants_expression_authority: bool
    preservation_obligations_projected: bool
    governed_outward_meaning_created: bool
    expression_plan_created: bool
    expression_candidate_created: bool
    human_readable_text_produced: bool
    msm_v1_modified_or_integrated: bool
    echo_validation_performed: bool
    bootstrap_integration_enabled: bool
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
    schema_version: str = SLICE42C_SCHEMA_VERSION

__all__ = (
    "AuthorizedMeaningAdmissionRecord", "ExpressionEligibilityEvaluationInput",
    "ExpressionEligibilityFinding", "ExpressionEligibilityFindingKind",
    "ExpressionEligibilityOutcome", "ExpressionEligibilityResult",
    "ExpressionEligibilityValidationCode", "ExpressionEligibilityValidationError",
    "ExpressionEligibilityValidationIssue", "ExpressionEligibilityValidationReport",
    "OutwardExpressionAuthorityRecord",
)
