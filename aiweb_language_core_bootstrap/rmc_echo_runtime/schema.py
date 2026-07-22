"""Immutable Slice 43A RMC Echo custody schemas.

The records in this module are constructor-shape contracts only. All fields
that could imply an Echo decision, comparison, drift classification, rejection,
containment, repair, MSM integration, delivery, or authority consequence are
locked to their non-performed state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .authority import (
    CONTAINMENT_CUSTODY_STATE_VALUES,
    DRIFT_FINDING_CUSTODY_STATE_VALUES,
    ECHO_DISPOSITION_CUSTODY_STATE_VALUES,
    ECHO_DISPOSITION_VALUES,
    PERMANENT_RMC_ECHO_BOUNDARIES,
    PRESERVATION_DIMENSION_VALUES,
    PROHIBITED_AUTHORITY_PATHS,
    REJECTION_CUSTODY_STATE_VALUES,
    VALIDATION_FINDING_CUSTODY_STATE_VALUES,
    VALIDATION_INPUT_CUSTODY_STATE_VALUES,
)
from .identity import (
    AUTHORIZED_MEANING_REFERENCE_SCHEMA_ID,
    DRIFT_FINDING_BOUNDARY_SCHEMA_ID,
    ECHO_CONTAINMENT_BOUNDARY_SCHEMA_ID,
    ECHO_DISPOSITION_BOUNDARY_SCHEMA_ID,
    ECHO_RECEIPT_BOUNDARY_SCHEMA_ID,
    ECHO_REJECTION_BOUNDARY_SCHEMA_ID,
    ECHO_TRACE_BOUNDARY_SCHEMA_ID,
    ECHO_VALIDATION_INPUT_BOUNDARY_SCHEMA_ID,
    PRESERVATION_DIMENSION_REQUIREMENT_SCHEMA_ID,
    PROPOSED_EXPRESSION_REFERENCE_SCHEMA_ID,
    RMC_ECHO_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
    SCHEMA_VERSION,
    SPEC_ID,
    SPEC_VERSION,
    VALIDATION_FINDING_BOUNDARY_SCHEMA_ID,
)


class EchoValidationInputCustodyState(str, Enum):
    NOT_ADMITTED = VALIDATION_INPUT_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_ADMISSION = VALIDATION_INPUT_CUSTODY_STATE_VALUES[1]
    ADMISSION_DEFERRED = VALIDATION_INPUT_CUSTODY_STATE_VALUES[2]
    ADMISSION_UNAVAILABLE = VALIDATION_INPUT_CUSTODY_STATE_VALUES[3]


class ValidationFindingCustodyState(str, Enum):
    NOT_COMPARED = VALIDATION_FINDING_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_COMPARISON = VALIDATION_FINDING_CUSTODY_STATE_VALUES[1]
    COMPARISON_DEFERRED = VALIDATION_FINDING_CUSTODY_STATE_VALUES[2]
    COMPARISON_UNAVAILABLE = VALIDATION_FINDING_CUSTODY_STATE_VALUES[3]


class DriftFindingCustodyState(str, Enum):
    NOT_CLASSIFIED = DRIFT_FINDING_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_CLASSIFICATION = DRIFT_FINDING_CUSTODY_STATE_VALUES[1]
    CLASSIFICATION_DEFERRED = DRIFT_FINDING_CUSTODY_STATE_VALUES[2]
    CLASSIFICATION_UNAVAILABLE = DRIFT_FINDING_CUSTODY_STATE_VALUES[3]


class EchoDisposition(str, Enum):
    PASSED = ECHO_DISPOSITION_VALUES[0]
    REJECTED = ECHO_DISPOSITION_VALUES[1]
    CONTAINED = ECHO_DISPOSITION_VALUES[2]


class EchoDispositionCustodyState(str, Enum):
    NOT_DECIDED = ECHO_DISPOSITION_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_DECISION = ECHO_DISPOSITION_CUSTODY_STATE_VALUES[1]
    DECISION_DEFERRED = ECHO_DISPOSITION_CUSTODY_STATE_VALUES[2]
    DECISION_UNAVAILABLE = ECHO_DISPOSITION_CUSTODY_STATE_VALUES[3]


class RejectionCustodyState(str, Enum):
    NOT_ISSUED = REJECTION_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_REJECTION = REJECTION_CUSTODY_STATE_VALUES[1]
    REJECTION_DEFERRED = REJECTION_CUSTODY_STATE_VALUES[2]
    REJECTION_UNAVAILABLE = REJECTION_CUSTODY_STATE_VALUES[3]


class ContainmentCustodyState(str, Enum):
    NOT_ISSUED = CONTAINMENT_CUSTODY_STATE_VALUES[0]
    READY_FOR_LATER_CONTAINMENT = CONTAINMENT_CUSTODY_STATE_VALUES[1]
    CONTAINMENT_DEFERRED = CONTAINMENT_CUSTODY_STATE_VALUES[2]
    CONTAINMENT_UNAVAILABLE = CONTAINMENT_CUSTODY_STATE_VALUES[3]


class PreservationDimension(str, Enum):
    SELECTED_IDENTITY_AND_LINEAGE = PRESERVATION_DIMENSION_VALUES[0]
    ACTIVE_SCOPE = PRESERVATION_DIMENSION_VALUES[1]
    NEGATION = PRESERVATION_DIMENSION_VALUES[2]
    MEANING_MODIFIERS = PRESERVATION_DIMENSION_VALUES[3]
    CERTAINTY_AND_CLAIM_STRENGTH = PRESERVATION_DIMENSION_VALUES[4]
    MODALITY_AND_CONDITIONAL_SCOPE = PRESERVATION_DIMENSION_VALUES[5]
    TIME_AND_OPERATIONAL_STATUS = PRESERVATION_DIMENSION_VALUES[6]
    EVIDENCE_BOUNDARY = PRESERVATION_DIMENSION_VALUES[7]
    INHERITED_LIMITATIONS = PRESERVATION_DIMENSION_VALUES[8]
    REQUIRED_QUALIFICATIONS = PRESERVATION_DIMENSION_VALUES[9]
    REQUIRED_CAVEATS = PRESERVATION_DIMENSION_VALUES[10]
    REFUSAL_AND_CONTAINMENT_BOUNDARY = PRESERVATION_DIMENSION_VALUES[11]
    UNRESOLVED_AMBIGUITY = PRESERVATION_DIMENSION_VALUES[12]
    UNSUPPORTED_STATE = PRESERVATION_DIMENSION_VALUES[13]
    ACTION_PROPOSAL_SIMULATION_AND_OBSERVATION = PRESERVATION_DIMENSION_VALUES[14]
    PERMISSION_VERSUS_REQUEST = PRESERVATION_DIMENSION_VALUES[15]
    PRIVACY_AND_IDENTITY_BOUNDARY = PRESERVATION_DIMENSION_VALUES[16]
    MEMORY_BOUNDARY = PRESERVATION_DIMENSION_VALUES[17]
    EXTERNAL_RESOURCE_STATUS = PRESERVATION_DIMENSION_VALUES[18]
    DELIVERY_AUTHORITY = PRESERVATION_DIMENSION_VALUES[19]
    ECONOMIC_AND_LEDGER_BOUNDARY = PRESERVATION_DIMENSION_VALUES[20]
    NON_LLM_PROVENANCE = PRESERVATION_DIMENSION_VALUES[21]


@dataclass(frozen=True, slots=True)
class AuthorizedMeaningReferenceRecord:
    authorized_meaning_reference_id: str
    slice42g_integration_input_ref: str
    slice42g_integration_result_ref: str
    slice42g_integration_receipt_ref: str
    slice42h_acceptance_record_ref: str
    source_manifest_ref: str
    successor_manifest_ref: str
    lineage_id: str
    selected_governed_meaning_ref: str
    selected_candidate_ref: str
    selection_authority_reference_ref: str
    governed_outward_meaning_ref: str
    outward_expression_authority_ref: str
    expression_eligibility_result_ref: str
    preservation_obligation_package_ref: str
    expression_plan_ref: str
    selected_meaning_content_proof_ref: str
    governed_outward_meaning_content_proof_ref: str
    preserved_alternative_refs: tuple[str, ...]
    unresolved_condition_refs: tuple[str, ...]
    inherited_limitation_refs: tuple[str, ...]
    required_qualification_refs: tuple[str, ...]
    required_caveat_refs: tuple[str, ...]
    refusal_relevant_boundary_refs: tuple[str, ...]
    ambiguity_refs: tuple[str, ...]
    privacy_identity_boundary_refs: tuple[str, ...]
    preservation_class_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    exact_slice42_chain_required: bool = field(default=True, init=False)
    source_admitted: bool = field(default=False, init=False)
    source_validated: bool = field(default=False, init=False)
    truth_determined: bool = field(default=False, init=False)
    selected_meaning_rewritten: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=AUTHORIZED_MEANING_REFERENCE_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class ProposedExpressionReferenceRecord:
    proposed_expression_reference_id: str
    slice42f_realization_input_ref: str
    slice42f_realization_result_ref: str
    slice42f_realization_receipt_ref: str
    slice42g_integration_input_ref: str
    slice42g_integration_result_ref: str
    slice42g_integration_receipt_ref: str
    successor_manifest_ref: str
    lineage_id: str
    expression_link_ref: str
    expression_candidate_ref: str
    realized_expression_ref: str
    expression_plan_ref: str
    governed_outward_meaning_ref: str
    preservation_obligation_package_ref: str
    realized_text_sha256: str
    realization_trace_ref: str
    realization_receipt_ref: str
    admitted_realization_rule_refs: tuple[str, ...]
    controlled_resource_refs: tuple[str, ...]
    applied_rule_refs: tuple[str, ...]
    applied_resource_refs: tuple[str, ...]
    segment_refs: tuple[str, ...]
    version_refs: tuple[str, ...]
    exact_slice42_chain_required: bool = field(default=True, init=False)
    source_admitted: bool = field(default=False, init=False)
    source_validated: bool = field(default=False, init=False)
    expression_rewritten: bool = field(default=False, init=False)
    echo_approved: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=PROPOSED_EXPRESSION_REFERENCE_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class EchoValidationInputBoundaryRecord:
    validation_input_boundary_id: str
    authorized_meaning_reference: AuthorizedMeaningReferenceRecord
    proposed_expression_reference: ProposedExpressionReferenceRecord
    custody_state: EchoValidationInputCustodyState
    required_preservation_dimensions: tuple[PreservationDimension, ...]
    predecessor_receipt_refs: tuple[str, ...]
    authority_version_refs: tuple[tuple[str, str], ...]
    schema_version_refs: tuple[tuple[str, str], ...]
    later_admitter_ref: str | None
    input_admitted: bool = field(default=False, init=False)
    cross_record_consistency_validated: bool = field(default=False, init=False)
    meaning_preservation_comparison_performed: bool = field(default=False, init=False)
    drift_classification_performed: bool = field(default=False, init=False)
    echo_disposition_decided: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=ECHO_VALIDATION_INPUT_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class PreservationDimensionRequirementRecord:
    dimension_requirement_id: str
    validation_input_boundary_ref: str
    dimension: PreservationDimension
    authorized_meaning_feature_refs: tuple[str, ...]
    proposed_expression_feature_refs: tuple[str, ...]
    required_preservation_refs: tuple[str, ...]
    allowed_variation_refs: tuple[str, ...]
    prohibited_drift_refs: tuple[str, ...]
    later_comparator_ref: str | None
    comparison_performed: bool = field(default=False, init=False)
    validation_finding_created: bool = field(default=False, init=False)
    drift_finding_created: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=PRESERVATION_DIMENSION_REQUIREMENT_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class ValidationFindingBoundaryRecord:
    validation_finding_boundary_id: str
    validation_input_boundary_ref: str
    dimension_requirement_ref: str
    dimension: PreservationDimension
    custody_state: ValidationFindingCustodyState
    authorized_meaning_feature_refs: tuple[str, ...]
    proposed_expression_feature_refs: tuple[str, ...]
    finding_reason_refs: tuple[str, ...]
    later_comparator_ref: str | None
    finding_outcome_ref: str | None = field(default=None, init=False)
    comparison_performed: bool = field(default=False, init=False)
    meaning_preserved_determined: bool = field(default=False, init=False)
    validation_finding_created: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=VALIDATION_FINDING_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class DriftFindingBoundaryRecord:
    drift_finding_boundary_id: str
    validation_input_boundary_ref: str
    validation_finding_boundary_ref: str
    dimension: PreservationDimension
    custody_state: DriftFindingCustodyState
    candidate_drift_evidence_refs: tuple[str, ...]
    candidate_materiality_refs: tuple[str, ...]
    classification_reason_refs: tuple[str, ...]
    later_classifier_ref: str | None
    drift_classification_ref: str | None = field(default=None, init=False)
    materiality_ref: str | None = field(default=None, init=False)
    drift_classified: bool = field(default=False, init=False)
    materiality_decided: bool = field(default=False, init=False)
    drift_finding_created: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=DRIFT_FINDING_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class EchoDispositionBoundaryRecord:
    echo_disposition_boundary_id: str
    validation_input_boundary_ref: str
    validation_finding_boundary_refs: tuple[str, ...]
    drift_finding_boundary_refs: tuple[str, ...]
    custody_state: EchoDispositionCustodyState
    decision_reason_refs: tuple[str, ...]
    later_decider_ref: str | None
    disposition: EchoDisposition | None = field(default=None, init=False)
    disposition_decided: bool = field(default=False, init=False)
    output_approved: bool = field(default=False, init=False)
    delivery_authorized: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=ECHO_DISPOSITION_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class EchoRejectionBoundaryRecord:
    echo_rejection_boundary_id: str
    validation_input_boundary_ref: str
    echo_disposition_boundary_ref: str
    custody_state: RejectionCustodyState
    candidate_rejection_reason_refs: tuple[str, ...]
    preserved_ancestry_refs: tuple[str, ...]
    prohibited_consequence_refs: tuple[str, ...]
    later_rejection_issuer_ref: str | None
    rejection_issued: bool = field(default=False, init=False)
    expression_deleted: bool = field(default=False, init=False)
    source_truth_determined: bool = field(default=False, init=False)
    delivery_authorized: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=ECHO_REJECTION_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class EchoContainmentBoundaryRecord:
    echo_containment_boundary_id: str
    validation_input_boundary_ref: str
    echo_disposition_boundary_ref: str
    custody_state: ContainmentCustodyState
    candidate_containment_reason_refs: tuple[str, ...]
    preserved_ancestry_refs: tuple[str, ...]
    downstream_prohibition_refs: tuple[str, ...]
    later_containment_issuer_ref: str | None
    containment_issued: bool = field(default=False, init=False)
    semantic_content_deleted: bool = field(default=False, init=False)
    memory_written: bool = field(default=False, init=False)
    delivery_authorized: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=ECHO_CONTAINMENT_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class EchoTraceBoundaryRecord:
    echo_trace_boundary_id: str
    authorized_meaning_reference_ref: str
    proposed_expression_reference_ref: str
    validation_input_boundary_ref: str
    preservation_dimension_requirement_refs: tuple[str, ...]
    validation_finding_boundary_refs: tuple[str, ...]
    drift_finding_boundary_refs: tuple[str, ...]
    echo_disposition_boundary_ref: str
    rejection_boundary_ref: str
    containment_boundary_ref: str
    predecessor_trace_refs: tuple[str, ...]
    predecessor_receipt_refs: tuple[str, ...]
    authority_version_refs: tuple[tuple[str, str], ...]
    schema_version_refs: tuple[tuple[str, str], ...]
    trace_boundary_only: bool = field(default=True, init=False)
    trace_created: bool = field(default=False, init=False)
    validation_performed: bool = field(default=False, init=False)
    disposition_decided: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=ECHO_TRACE_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class EchoReceiptBoundaryRecord:
    echo_receipt_boundary_id: str
    authorized_meaning_reference_ref: str
    proposed_expression_reference_ref: str
    validation_input_boundary_ref: str
    echo_trace_boundary_ref: str
    echo_disposition_boundary_ref: str
    rejection_boundary_ref: str
    containment_boundary_ref: str
    required_law_refs: tuple[str, ...]
    prohibited_consequence_refs: tuple[str, ...]
    audit_note: str
    receipt_boundary_only: bool = field(default=True, init=False)
    receipt_created: bool = field(default=False, init=False)
    receipt_validated: bool = field(default=False, init=False)
    echo_validation_performed: bool = field(default=False, init=False)
    delivered: bool = field(default=False, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=ECHO_RECEIPT_BOUNDARY_SCHEMA_ID, init=False)


@dataclass(frozen=True, slots=True)
class RmcEchoRuntimeSchemaRecord:
    rmc_echo_runtime_schema_record_id: str
    authorized_meaning_reference: AuthorizedMeaningReferenceRecord
    proposed_expression_reference: ProposedExpressionReferenceRecord
    validation_input_boundary: EchoValidationInputBoundaryRecord
    preservation_dimension_requirements: tuple[PreservationDimensionRequirementRecord, ...]
    validation_finding_boundaries: tuple[ValidationFindingBoundaryRecord, ...]
    drift_finding_boundaries: tuple[DriftFindingBoundaryRecord, ...]
    echo_disposition_boundary: EchoDispositionBoundaryRecord
    rejection_boundary: EchoRejectionBoundaryRecord
    containment_boundary: EchoContainmentBoundaryRecord
    trace_boundary: EchoTraceBoundaryRecord
    receipt_boundary: EchoReceiptBoundaryRecord
    permanent_boundaries: tuple[str, ...] = field(
        default=PERMANENT_RMC_ECHO_BOUNDARIES,
        init=False,
    )
    prohibited_authority_paths: tuple[str, ...] = field(
        default=PROHIBITED_AUTHORITY_PATHS,
        init=False,
    )
    schema_only: bool = field(default=True, init=False)
    versioned_companion: bool = field(default=True, init=False)
    deterministic_identity_calculated: bool = field(default=False, init=False)
    validation_performed: bool = field(default=False, init=False)
    canonical_serialization_performed: bool = field(default=False, init=False)
    lifecycle_transition_performed: bool = field(default=False, init=False)
    slice42_sources_admitted: bool = field(default=False, init=False)
    meaning_preservation_comparison_performed: bool = field(default=False, init=False)
    validation_findings_created: bool = field(default=False, init=False)
    drift_findings_created: bool = field(default=False, init=False)
    materiality_decided: bool = field(default=False, init=False)
    echo_disposition_decided: bool = field(default=False, init=False)
    rejection_issued: bool = field(default=False, init=False)
    containment_issued: bool = field(default=False, init=False)
    expression_repaired: bool = field(default=False, init=False)
    msm_v1_schema_modified: bool = field(default=False, init=False)
    msm_v1_automatic_migration_performed: bool = field(default=False, init=False)
    msm_v1_validation_link_integrated: bool = field(default=False, init=False)
    bootstrap_integration_enabled: bool = field(default=False, init=False)
    truth_determined: bool = field(default=False, init=False)
    evidence_validated: bool = field(default=False, init=False)
    permission_granted: bool = field(default=False, init=False)
    execution_authorized: bool = field(default=False, init=False)
    capability_availability_created: bool = field(default=False, init=False)
    route_created: bool = field(default=False, init=False)
    api_created: bool = field(default=False, init=False)
    tool_invoked: bool = field(default=False, init=False)
    action_performed: bool = field(default=False, init=False)
    memory_accessed: bool = field(default=False, init=False)
    memory_written: bool = field(default=False, init=False)
    filesystem_read_performed: bool = field(default=False, init=False)
    filesystem_write_performed: bool = field(default=False, init=False)
    network_access_performed: bool = field(default=False, init=False)
    external_resource_loaded: bool = field(default=False, init=False)
    rendered_for_delivery: bool = field(default=False, init=False)
    delivered: bool = field(default=False, init=False)
    language_model_used: bool = field(default=False, init=False)
    embedding_used: bool = field(default=False, init=False)
    vector_used: bool = field(default=False, init=False)
    rag_used: bool = field(default=False, init=False)
    semantic_similarity_used: bool = field(default=False, init=False)
    neural_parser_used: bool = field(default=False, init=False)
    hidden_classifier_used: bool = field(default=False, init=False)
    echo_forge_used: bool = field(default=False, init=False)
    legacy_echo_validator_used: bool = field(default=False, init=False)
    gp014_superseded: bool = field(default=False, init=False)
    spec_id: str = field(default=SPEC_ID, init=False)
    spec_version: str = field(default=SPEC_VERSION, init=False)
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    schema_id: str = field(default=RMC_ECHO_RUNTIME_SCHEMA_RECORD_SCHEMA_ID, init=False)


__all__ = (
    "AuthorizedMeaningReferenceRecord",
    "ContainmentCustodyState",
    "DriftFindingBoundaryRecord",
    "DriftFindingCustodyState",
    "EchoContainmentBoundaryRecord",
    "EchoDisposition",
    "EchoDispositionBoundaryRecord",
    "EchoDispositionCustodyState",
    "EchoReceiptBoundaryRecord",
    "EchoRejectionBoundaryRecord",
    "EchoTraceBoundaryRecord",
    "EchoValidationInputBoundaryRecord",
    "EchoValidationInputCustodyState",
    "PreservationDimension",
    "PreservationDimensionRequirementRecord",
    "ProposedExpressionReferenceRecord",
    "RejectionCustodyState",
    "RmcEchoRuntimeSchemaRecord",
    "ValidationFindingBoundaryRecord",
    "ValidationFindingCustodyState",
)
