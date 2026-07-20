"""Binding Slice 41A schema-only and non-authority boundaries.

These constants define the immutable vocabulary and deferred authority for the
first Selected Meaning Boundary Runtime increment.  They do not calculate
identities, validate records, evaluate eligibility, choose or rank candidates,
discard alternatives, resolve ambiguity, construct selected meaning, modify
MeaningStructureManifest v1, enable bootstrap integration, or create any
truth, evidence, permission, execution, route, tool, action, memory, rendering,
delivery, or external-resource authority.
"""

from typing import Final


ELIGIBILITY_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_evaluated",
    "ready_for_later_evaluation",
    "evaluation_deferred",
    "evaluation_unavailable",
)

DECISION_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_decided",
    "ready_for_later_decision",
    "decision_deferred",
    "decision_unavailable",
)

MSM_SELECTED_MEANING_INTEGRATION_DECISION: Final[str] = (
    "deferred_to_slice41e_exact_additive_adapter"
)
MSM_V1_SCHEMA_MODIFICATION_ALLOWED: Final[bool] = False
MSM_V1_AUTOMATIC_MIGRATION_ALLOWED: Final[bool] = False
SELECTION_ELIGIBILITY_EVALUATION_ALLOWED: Final[bool] = False
SELECTION_PERFORMANCE_ALLOWED: Final[bool] = False
SELECTED_GOVERNED_MEANING_CONSTRUCTION_ALLOWED: Final[bool] = False
BOOTSTRAP_INTEGRATION_ALLOWED: Final[bool] = False

POSITIVE_ELIGIBILITY_NAMING_DECISION: Final[str] = (
    "deferred_to_slice41c_source_and_document6_decision"
)
SELECTION_DECISION_NAMING_DECISION: Final[str] = (
    "deferred_to_slice41d_source_and_document6_decision"
)

DEFERRED_SLICE41_RUNTIME_AUTHORITY: Final[tuple[str, ...]] = (
    "deterministic_identity_calculation",
    "strict_validation",
    "canonical_serialization",
    "schema_version_enforcement",
    "duplicate_and_collision_rejection",
    "governed_lifecycle_transitions",
    "cross_record_consistency_validation",
    "selection_eligibility_evaluation",
    "positive_eligibility_disposition",
    "negative_eligibility_disposition",
    "candidate_selection_decision",
    "selected_meaning_construction",
    "alternative_candidate_disposition",
    "selection_trace_construction",
    "selection_receipt_construction",
    "msm_v1_selected_meaning_integration",
    "disabled_bootstrap_integration",
    "slice41_closeout",
)

PERMANENT_SELECTED_MEANING_BOUNDARIES: Final[tuple[str, ...]] = (
    "schema_existence_is_not_selection_eligibility",
    "schema_existence_is_not_selection_decision",
    "selection_candidate_custody_is_not_candidate_eligibility",
    "selection_candidate_custody_is_not_selected_candidate",
    "gate_custody_reference_is_not_gate_re_evaluation",
    "gate_supported_candidate_is_not_selected_meaning",
    "positive_selection_review_disposition_is_not_selection",
    "selection_authority_requirement_is_not_authority_satisfaction",
    "authority_reference_is_not_permission",
    "alternative_candidate_custody_is_not_ranking",
    "alternative_candidate_custody_is_not_preference",
    "alternative_candidate_custody_is_not_discard",
    "one_candidate_is_not_automatic_selection",
    "only_remaining_candidate_is_not_automatic_selection",
    "multiple_candidates_are_not_automatic_ambiguity",
    "material_ambiguity_is_not_ambiguity_resolution",
    "clarification_relevance_is_not_clarification_emission",
    "unsupported_disposition_is_not_refusal",
    "refusal_relevance_is_not_outward_refusal",
    "held_disposition_is_not_rejection",
    "blocked_progression_is_not_final_refusal",
    "unresolved_state_custody_is_not_resolution",
    "inherited_limitation_custody_cannot_silently_disappear",
    "eligibility_status_record_is_not_eligibility_outcome",
    "decision_status_record_is_not_selection_decision",
    "selection_trace_boundary_is_not_selection_trace_validation",
    "selection_receipt_boundary_is_not_selection_receipt_authority",
    "selection_eligibility_evaluation_belongs_to_slice41c",
    "selected_meaning_construction_belongs_to_slice41d",
    "msm_selected_meaning_integration_belongs_to_slice41e",
    "bootstrap_integration_and_closeout_belong_to_slice41f",
    "selected_meaning_is_not_truth",
    "selected_meaning_is_not_evidence",
    "selected_meaning_is_not_proof",
    "selected_meaning_is_not_permission",
    "selected_meaning_is_not_execution",
    "selected_meaning_is_not_capability_availability",
    "capability_reference_is_not_route",
    "route_reference_is_not_invocation",
    "effect_boundary_is_not_execution",
    "request_meaning_is_not_authorization",
    "report_meaning_is_not_evidence_validity",
    "verification_meaning_is_not_verified_status",
    "memory_meaning_is_not_memory_access_or_write",
    "delivery_meaning_is_not_delivery_authority",
    "installation_meaning_is_not_code_application_authority",
    "selected_meaning_is_not_governed_outward_meaning",
    "selected_meaning_is_not_output_rendering",
    "selected_meaning_is_not_delivery",
    "external_resource_reference_is_not_resource_admission",
)

PROHIBITED_AUTHORITY_PATHS: Final[tuple[str, ...]] = (
    "language_model_authority",
    "embedding_authority",
    "vector_authority",
    "rag_authority",
    "semantic_similarity_authority",
    "nearest_known_substitution",
    "confidence_scoring",
    "probability_ranking",
    "safest_candidate_selection",
    "first_candidate_selection",
    "only_remaining_candidate_selection",
    "hidden_intent_inference",
    "silent_role_filling",
    "silent_referent_resolution",
    "automatic_ambiguity_collapse",
    "alternative_deletion",
    "truth_determination",
    "evidence_validation",
    "proof_claim",
    "permission_grant",
    "execution_authorization",
    "capability_availability",
    "route_creation",
    "tool_invocation",
    "action_execution",
    "memory_access",
    "memory_write",
    "output_rendering",
    "delivery",
    "external_resource_loading",
    "msm_v1_mutation",
    "bootstrap_enablement",
)
