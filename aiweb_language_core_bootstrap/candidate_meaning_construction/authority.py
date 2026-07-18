"""Binding non-authority boundaries for Slice 39A.

These constants make the schema-only scope explicit.  They do not perform
validation, select meaning, create a gate result, or connect any runtime path.
"""

from typing import Final


CONSTRUCTION_ONLY_STATUS_VALUES: Final[tuple[str, ...]] = (
    "constructed",
    "construction_incomplete",
    "construction_unknown",
    "construction_unsupported",
    "construction_conflicted",
    "predecessor_invalid",
)

DEFERRED_SLICE40_GATE_OUTCOMES: Final[tuple[str, ...]] = (
    "accepted_meaning",
    "selected_meaning",
    "ambiguous_gate_disposition",
    "clarification_required",
    "refusal",
    "blocked_progression",
    "rejection",
    "unsupported_language_disposition",
)

PERMANENT_CANDIDATE_MEANING_BOUNDARIES: Final[tuple[str, ...]] = (
    "source_text_is_not_candidate_meaning",
    "structural_candidate_is_not_candidate_meaning",
    "concept_candidate_is_not_accepted_concept_occurrence",
    "sense_candidate_is_not_selected_sense",
    "predicate_candidate_is_not_selected_predicate",
    "frame_candidate_is_not_selected_frame",
    "role_layout_candidate_is_not_participant_assignment",
    "referent_candidate_is_not_resolved_referent",
    "multiple_candidates_are_not_ambiguous_gate_outcome",
    "missing_role_is_not_clarification_required_outcome",
    "unsupported_construction_is_not_refusal",
    "complete_candidate_is_not_gate_pass",
    "complete_candidate_is_not_selected_meaning",
    "candidate_meaning_is_not_truth",
    "candidate_meaning_is_not_evidence",
    "candidate_meaning_is_not_permission",
    "candidate_meaning_is_not_capability_availability",
    "capability_reference_is_not_route",
    "route_reference_is_not_invocation",
    "effect_boundary_is_not_execution",
    "request_meaning_is_not_authorization",
    "report_meaning_is_not_evidence_validity",
    "verification_meaning_is_not_verified_status",
    "memory_meaning_is_not_memory_access",
    "delivery_meaning_is_not_delivery_authority",
    "installation_meaning_is_not_code_application_authority",
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
    "capability_availability",
    "route_creation",
    "tool_invocation",
    "action_execution",
    "memory_access",
    "rendering",
    "delivery",
)
