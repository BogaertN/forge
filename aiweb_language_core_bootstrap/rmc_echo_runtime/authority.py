"""Binding Slice 43A schema-only and permanent non-authority boundaries.

Slice 43A defines immutable record shapes for later deterministic RMC Echo
work. It performs no admission, comparison, validation, drift classification,
materiality decision, Echo disposition, rejection, containment, repair,
MeaningStructureManifest successor creation, delivery, action, or runtime
integration.
"""

from typing import Final


VALIDATION_INPUT_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_admitted",
    "ready_for_later_admission",
    "admission_deferred",
    "admission_unavailable",
)
VALIDATION_FINDING_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_compared",
    "ready_for_later_comparison",
    "comparison_deferred",
    "comparison_unavailable",
)
DRIFT_FINDING_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_classified",
    "ready_for_later_classification",
    "classification_deferred",
    "classification_unavailable",
)
ECHO_DISPOSITION_VALUES: Final[tuple[str, ...]] = (
    "PASSED",
    "REJECTED",
    "CONTAINED",
)
ECHO_DISPOSITION_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_decided",
    "ready_for_later_decision",
    "decision_deferred",
    "decision_unavailable",
)
REJECTION_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_issued",
    "ready_for_later_rejection",
    "rejection_deferred",
    "rejection_unavailable",
)
CONTAINMENT_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_issued",
    "ready_for_later_containment",
    "containment_deferred",
    "containment_unavailable",
)

PRESERVATION_DIMENSION_VALUES: Final[tuple[str, ...]] = (
    "selected_identity_and_lineage",
    "active_scope",
    "negation",
    "meaning_modifiers",
    "certainty_and_claim_strength",
    "modality_and_conditional_scope",
    "time_and_operational_status",
    "evidence_boundary",
    "inherited_limitations",
    "required_qualifications",
    "required_caveats",
    "refusal_and_containment_boundary",
    "unresolved_ambiguity",
    "unsupported_state",
    "action_proposal_simulation_and_observation",
    "permission_versus_request",
    "privacy_and_identity_boundary",
    "memory_boundary",
    "external_resource_status",
    "delivery_authority",
    "economic_and_ledger_boundary",
    "non_llm_provenance",
)

SLICE42_SOURCE_ADMISSION_DECISION: Final[str] = (
    "deferred_to_slice43c_exact_slice42_ancestry_admission"
)
MSM_VALIDATION_LINK_INTEGRATION_DECISION: Final[str] = (
    "deferred_to_slice43g_exact_additive_adapter"
)
SLICE19_SCAFFOLD_REUSE_DECISION: Final[str] = (
    "protected_historical_boundary_only_not_runtime_authority"
)
DORMANT_ECHO_VALIDATOR_REUSE_DECISION: Final[str] = (
    "historical_only_no_import_no_call_no_runtime_authority"
)

IDENTITY_VALIDATION_ALLOWED: Final[bool] = False
CANONICAL_SERIALIZATION_ALLOWED: Final[bool] = False
LIFECYCLE_TRANSITION_ALLOWED: Final[bool] = False
SLICE42_SOURCE_ADMISSION_ALLOWED: Final[bool] = False
MEANING_PRESERVATION_COMPARISON_ALLOWED: Final[bool] = False
VALIDATION_FINDING_CREATION_ALLOWED: Final[bool] = False
DRIFT_CLASSIFICATION_ALLOWED: Final[bool] = False
MATERIALITY_DECISION_ALLOWED: Final[bool] = False
ECHO_DISPOSITION_DECISION_ALLOWED: Final[bool] = False
REJECTION_ISSUANCE_ALLOWED: Final[bool] = False
CONTAINMENT_ISSUANCE_ALLOWED: Final[bool] = False
EXPRESSION_REPAIR_ALLOWED: Final[bool] = False
MSM_VALIDATION_LINK_CREATION_ALLOWED: Final[bool] = False
MSM_V1_SCHEMA_MODIFICATION_ALLOWED: Final[bool] = False
MSM_V1_AUTOMATIC_MIGRATION_ALLOWED: Final[bool] = False
BOOTSTRAP_INTEGRATION_ALLOWED: Final[bool] = False
DELIVERY_AUTHORITY_ALLOWED: Final[bool] = False

DEFERRED_SLICE43_RUNTIME_AUTHORITY: Final[tuple[str, ...]] = (
    "deterministic_validation_and_identity",
    "schema_and_profile_version_enforcement",
    "canonical_serialization",
    "duplicate_collision_and_predecessor_rejection",
    "governed_lifecycle_transitions",
    "exact_slice42_authorized_meaning_admission",
    "exact_slice42_proposed_expression_admission",
    "meaning_preservation_comparison",
    "validation_finding_construction",
    "drift_classification",
    "drift_materiality_determination",
    "echo_disposition_decision",
    "rejection_issuance",
    "containment_issuance",
    "msm_v1_validation_link_integration",
    "disabled_bootstrap_integration",
    "slice43_closeout",
)

PERMANENT_RMC_ECHO_BOUNDARIES: Final[tuple[str, ...]] = (
    "schema_existence_is_not_echo_authority",
    "authorized_meaning_reference_is_not_truth_authority",
    "proposed_expression_reference_is_not_output_approval",
    "validation_input_custody_is_not_source_admission",
    "source_admission_is_not_meaning_preservation_comparison",
    "preservation_dimension_is_not_validation_finding",
    "validation_finding_is_not_drift_materiality",
    "drift_finding_is_not_echo_disposition",
    "disposition_vocabulary_is_not_disposition_decision",
    "rejection_record_shape_is_not_rejection_issuance",
    "containment_record_shape_is_not_containment_issuance",
    "echo_trace_is_not_echo_receipt",
    "echo_receipt_is_not_proof_beyond_verified_scope",
    "echo_pass_is_not_delivery_authority",
    "echo_rejection_is_not_source_truth_determination",
    "echo_containment_is_not_semantic_deletion",
    "selected_meaning_may_not_be_rewritten",
    "proposed_expression_may_not_be_rewritten",
    "candidate_alternatives_may_not_be_deleted",
    "non_selection_outcomes_may_not_be_deleted",
    "unresolved_state_may_not_be_silently_resolved",
    "ambiguity_may_not_be_silently_collapsed",
    "uncertainty_may_not_be_upgraded",
    "claim_strength_may_not_be_upgraded",
    "evidence_status_may_not_be_upgraded",
    "required_qualifications_may_not_be_omitted",
    "required_caveats_may_not_be_omitted",
    "refusal_may_not_be_softened_into_permission",
    "memory_reference_is_not_memory_authority",
    "external_resource_reference_is_not_resource_admission",
    "delivery_reference_is_not_delivery_authority",
    "validation_link_creation_belongs_to_slice43g",
    "msm_v1_schema_is_not_rewritten",
    "automatic_migration_is_not_authorized",
    "slice19_scaffold_is_not_slice43_runtime",
    "legacy_echo_validator_is_not_current_authority",
    "echo_validation_is_not_truth",
    "echo_validation_is_not_evidence_validation",
    "echo_validation_is_not_permission",
    "echo_validation_is_not_execution",
    "echo_validation_is_not_tool_routing",
    "echo_validation_is_not_memory_write",
    "echo_validation_is_not_delivery",
    "gp014_is_not_superseded",
)

PROHIBITED_AUTHORITY_PATHS: Final[tuple[str, ...]] = (
    "language_model_authority",
    "embedding_authority",
    "vector_authority",
    "rag_authority",
    "semantic_similarity_authority",
    "neural_parser_authority",
    "hidden_classifier_authority",
    "nearest_known_substitution",
    "confidence_scoring",
    "probability_ranking",
    "selected_meaning_rewrite",
    "expression_candidate_rewrite",
    "semantic_enrichment",
    "semantic_deletion",
    "alternative_deletion",
    "non_selection_deletion",
    "unresolved_state_resolution",
    "ambiguity_collapse",
    "uncertainty_upgrade",
    "claim_strength_upgrade",
    "evidence_status_upgrade",
    "qualification_omission",
    "caveat_omission",
    "refusal_softening",
    "truth_determination",
    "evidence_validation",
    "permission_grant",
    "execution_authorization",
    "capability_availability",
    "route_creation",
    "api_creation",
    "tool_invocation",
    "action_execution",
    "memory_access",
    "memory_write",
    "filesystem_read",
    "filesystem_write",
    "network_access",
    "external_resource_loading",
    "output_delivery",
    "msm_v1_schema_rewrite",
    "msm_v1_automatic_migration",
    "bootstrap_enablement",
    "legacy_echo_validator_activation",
    "echo_forge_activation",
    "expression_repair",
    "gp014_supersession",
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
