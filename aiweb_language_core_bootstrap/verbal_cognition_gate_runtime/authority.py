"""Binding schema-only and non-authority boundaries for Slice 40A."""

from typing import Final


GATE_FAMILY_VALUES: Final[tuple[str, ...]] = (
    "expectancy",
    "congruity",
    "connectedness",
    "recoverable_purpose",
)

RECOVERABLE_PURPOSE_ARCHITECTURE_ALIASES: Final[tuple[str, ...]] = (
    "intended_purport",
    "recoverable_purpose",
)

SCHEMA_ONLY_EVALUATION_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_evaluated",
    "ready_for_later_evaluation",
    "evaluation_deferred",
    "evaluation_unavailable",
)

MSM_GATE_CUSTODY_DECISION: Final[str] = "versioned_companion_required"
MSM_V1_SCHEMA_MODIFICATION_ALLOWED: Final[bool] = False
MSM_V1_AUTOMATIC_MIGRATION_ALLOWED: Final[bool] = False
POSITIVE_DISPOSITION_NAMING_DECISION: Final[str] = (
    "deferred_to_slice40g_source_and_document6_decision"
)

DEFERRED_SLICE40_RUNTIME_AUTHORITY: Final[tuple[str, ...]] = (
    "deterministic_identity_calculation",
    "strict_validation",
    "canonical_serialization",
    "lifecycle_transitions",
    "expectancy_evaluation",
    "congruity_evaluation",
    "connectedness_evaluation",
    "recoverable_purpose_evaluation",
    "gate_composition",
    "ambiguity_disposition",
    "clarification_relevance",
    "unsupported_disposition",
    "refusal_relevance",
    "held_disposition",
    "blocked_progression",
    "positive_selection_review_disposition",
    "msm_v1_gate_integration",
    "disabled_bootstrap_integration",
    "slice40_closeout",
)

PERMANENT_GATE_CORE_BOUNDARIES: Final[tuple[str, ...]] = (
    "schema_existence_is_not_gate_evaluation",
    "gate_record_is_not_gate_pass",
    "gate_record_is_not_gate_failure",
    "gate_family_identity_is_not_gate_outcome",
    "gate_profile_identity_is_not_runtime_evaluator",
    "candidate_input_reference_is_not_candidate_acceptance",
    "candidate_input_reference_is_not_selected_meaning",
    "requirement_reference_is_not_requirement_satisfaction",
    "reason_ground_shape_is_not_reason_ground_validation",
    "trace_reference_is_not_proof",
    "provenance_reference_is_not_truth",
    "limitation_reference_is_not_clarification",
    "missing_role_reference_is_not_clarification_required",
    "multiple_candidate_reference_is_not_ambiguity_disposition",
    "construction_status_is_not_gate_outcome",
    "gate_evaluation_state_is_not_composed_disposition",
    "gate_satisfaction_is_not_selected_meaning",
    "selected_meaning_belongs_to_slice41",
    "gate_result_is_not_truth",
    "gate_result_is_not_evidence_validity",
    "gate_result_is_not_permission",
    "gate_result_is_not_capability_availability",
    "capability_reference_is_not_route",
    "route_reference_is_not_invocation",
    "effect_boundary_is_not_execution",
    "request_meaning_is_not_authorization",
    "report_meaning_is_not_evidence_validity",
    "verification_meaning_is_not_verified_status",
    "memory_meaning_is_not_memory_access",
    "delivery_meaning_is_not_delivery_authority",
    "installation_meaning_is_not_code_application_authority",
    "external_resource_reference_is_not_resource_admission",
)

PROHIBITED_AUTHORITY_PATHS: Final[tuple[str, ...]] = (
    "language_model_authority",
    "embedding_authority",
    "vector_authority",
    "rag_authority",
    "semantic_similarity_authority",
    "nearest_known_substitution",
    "hidden_intent_inference",
    "silent_role_filling",
    "silent_referent_resolution",
    "automatic_ambiguity_collapse",
    "truth_determination",
    "evidence_validation",
    "permission_grant",
    "execution_authorization",
    "capability_availability",
    "route_creation",
    "tool_invocation",
    "action_execution",
    "memory_access",
    "rendering",
    "delivery",
    "external_resource_loading",
)
