"""Slice 39F deterministic constructor authority and permanent boundaries."""

from __future__ import annotations

from typing import Final

SLICE39F_SPEC_ID: Final[str] = "aiweb-slice39f-deterministic-candidate-meaning-constructor"
SLICE39F_SPEC_VERSION: Final[str] = "aiweb-slice39f-deterministic-candidate-meaning-constructor-v1"
SLICE39F_SCHEMA_VERSION: Final[str] = "aiweb-language-core-slice39f-deterministic-candidate-meaning-constructor-v1"
SLICE39F_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE39F_CANDIDATE_VERSION: Final[str] = "v1.0.0"

SLICE39F_REQUIRED_PATH: Final[tuple[str, ...]] = (
    "accepted_slice37_structural_concept_sense_proposal",
    "accepted_slice38_predicate_role_frame_proposal",
    "exact_ancestry_verification",
    "exact_snapshot_verification",
    "candidate_semantic_content_assembly",
    "zero_one_many_candidate_meaning_state_construction",
    "deterministic_construction_receipt",
)

SLICE39F_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
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

SLICE39F_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "arbitrary_raw_text_inspection",
    "tokenization_or_new_structural_analysis",
    "similarity_or_nearest_known_fallback",
    "hidden_repair_or_silent_role_filling",
    "silent_referent_resolution",
    "candidate_ranking_or_selection",
    "automatic_ambiguity_resolution",
    "gate_outcome_creation",
    "selected_meaning_creation",
    "truth_or_evidence_determination",
    "permission_or_capability_availability",
    "route_or_invocation",
    "tool_or_action",
    "memory_access",
    "rendering_or_delivery",
    "filesystem_or_network_access",
    "external_resource_loading",
    "language_model_embedding_vector_rag_similarity_authority",
    "meaning_structure_manifest_integration",
    "bootstrap_integration_or_slice39_closeout",
)

__all__ = (
    "SLICE39F_CANDIDATE_VERSION",
    "SLICE39F_PERMANENT_BOUNDARIES",
    "SLICE39F_PROFILE_VERSION",
    "SLICE39F_PROHIBITED_AUTHORITY",
    "SLICE39F_REQUIRED_PATH",
    "SLICE39F_SCHEMA_VERSION",
    "SLICE39F_SPEC_ID",
    "SLICE39F_SPEC_VERSION",
)
