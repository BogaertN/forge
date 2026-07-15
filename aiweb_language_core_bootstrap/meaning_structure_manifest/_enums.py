"""Closed semantic distinctions bound by MeaningStructureManifest v1.

The names below are a transparent Python representation chosen for Slice 35A.
Document 2 binds the distinctions but explicitly defers final serialized enum
names and storage representation. No transition law is implemented here.
"""

from enum import Enum


class SemanticRecordKind(str, Enum):
    LINEAGE_ROOT = "lineage_root"
    CANDIDATE_MEANING = "candidate_meaning"
    NON_SELECTION_OUTCOME = "non_selection_outcome"
    SELECTED_GOVERNED_MEANING = "selected_governed_meaning"
    GOVERNED_RESULT_REFERENCE = "governed_result_reference"
    GOVERNED_OUTWARD_MEANING = "governed_outward_meaning"
    EXPRESSION_LINK = "expression_link"
    VALIDATION_LINK = "validation_link"
    DELIVERY_OR_CONTAINMENT_LINK = "delivery_or_containment_link"
    EXTERNAL_AUTHORITY_REFERENCE = "external_authority_reference"
    SEMANTIC_TRANSITION_TRACE = "semantic_transition_trace"
    MEANING_STRUCTURE_MANIFEST = "meaning_structure_manifest"


class SemanticDirection(str, Enum):
    INWARD = "inward"
    OUTWARD = "outward"


class LineageOriginKind(str, Enum):
    SOURCE_BOUND_HUMAN_EXPRESSION = "source_bound_human_expression"
    AUTHORIZED_OUTWARD_EXPRESSION_PURPOSE = (
        "authorized_outward_expression_purpose"
    )


class SemanticLifecycleState(str, Enum):
    LINEAGE_ORIGIN = "lineage_origin"
    CANDIDATE_MEANING = "candidate_meaning"
    UNRESOLVED = "unresolved"
    CLARIFICATION_REQUIRED = "clarification_required"
    REFUSED = "refused"
    UNSUPPORTED = "unsupported"
    AUTHORITY_BLOCKED = "authority_blocked"
    SELECTED_GOVERNED_MEANING = "selected_governed_meaning"
    GOVERNED_RESULT_REFERENCED = "governed_result_referenced"
    GOVERNED_OUTWARD_MEANING = "governed_outward_meaning"
    EXPRESSION_LINKED = "expression_linked"
    VALIDATION_LINKED = "validation_linked"
    DELIVERY_LINKED = "delivery_linked"
    CONTAINMENT_LINKED = "containment_linked"
    CORRECTED = "corrected"
    SUPERSEDED = "superseded"


class NonSelectionOutcomeKind(str, Enum):
    UNRESOLVED = "unresolved"
    CLARIFICATION_REQUIRED = "clarification_required"
    REFUSED = "refused"
    UNSUPPORTED = "unsupported"
    AUTHORITY_BLOCKED = "authority_blocked"


class DeliveryContainmentKind(str, Enum):
    DELIVERY_LINKED = "delivery_linked"
    CONTAINMENT_LINKED = "containment_linked"


class SemanticTransitionKind(str, Enum):
    ANCESTRY = "ancestry"
    CORRECTION = "correction"
    SUPERSESSION = "supersession"
    REJECTION = "rejection"
    CONTAINMENT = "containment"
    NARROWING = "narrowing"
    BROADENING = "broadening"


class ExternalAuthorityKind(str, Enum):
    RAW_SOURCE_OR_INPUT_EVENT = "raw_source_or_input_event"
    PARSED_QUESTION_OR_TYPED_INPUT = "parsed_question_or_typed_input"
    SOURCE_CUSTODY = "source_custody"
    EVIDENCE_OR_CLAIM_STATUS = "evidence_or_claim_status"
    MEA_PROBLEM_STATE = "mea_problem_state"
    EXISTING_RMC_MEANING_OR_RENDER_ARTIFACT = (
        "existing_rmc_meaning_or_render_artifact"
    )
    MANIFEST_CONTRACT = "manifest_contract"
    CAPABILITY_CONTRACT_OR_ROUTING_ADMISSION = (
        "capability_contract_or_routing_admission"
    )
    INVOCATION_EXECUTION_OR_VERIFICATION_RECEIPT = (
        "invocation_execution_or_verification_receipt"
    )
    RENDER_PREVIEW_OR_OUTPUT_OBJECT = "render_preview_or_output_object"
    RMC_ECHO_VALIDATOR_RECEIPT = "rmc_echo_validator_receipt"
    DELIVERY_OR_CONTAINMENT_RECEIPT = "delivery_or_containment_receipt"
    MEMORY_AUTHORIZATION_OR_EVENT_RECEIPT = (
        "memory_authorization_or_event_receipt"
    )
    IDENTITY_ACCESS_CONSENT_OR_USER_AUTHORITY = (
        "identity_access_consent_or_user_authority"
    )
    CONTRIBUTION_ECONOMY_OR_LEDGER = "contribution_economy_or_ledger"
    ROLLBACK_PATCH_RUNTIME_OR_CONTAINMENT = (
        "rollback_patch_runtime_or_containment"
    )
    LICENSING_PROVENANCE_OR_RESOURCE_ADMISSION = (
        "licensing_provenance_or_resource_admission"
    )


class SemanticPreservationClass(str, Enum):
    NEGATION = "negation"
    UNCERTAINTY_AND_CLAIM_STRENGTH = "uncertainty_and_claim_strength"
    MODALITY_AND_CONDITIONAL_SCOPE = "modality_and_conditional_scope"
    TIME_AND_OPERATIONAL_STATUS = "time_and_operational_status"
    EVIDENCE_BOUNDARY = "evidence_boundary"
    ACTION_PROPOSAL_SIMULATION_AND_OBSERVATION = (
        "action_proposal_simulation_and_observation"
    )
    PERMISSION_VERSUS_REQUEST = "permission_versus_request"
    PRIVACY_AND_IDENTITY_BOUNDARY = "privacy_and_identity_boundary"
    REFUSAL_AND_CONTAINMENT_BOUNDARY = "refusal_and_containment_boundary"
    UNRESOLVED_AMBIGUITY = "unresolved_ambiguity"
    MEMORY_BOUNDARY = "memory_boundary"
    ECONOMIC_AND_LEDGER_BOUNDARY = "economic_and_ledger_boundary"
    NON_LLM_PROVENANCE = "non_llm_provenance"
