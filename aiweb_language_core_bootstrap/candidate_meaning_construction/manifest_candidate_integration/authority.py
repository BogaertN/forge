"""Slice 39G MSM-v1 candidate-integration authority and boundaries."""

from __future__ import annotations

from typing import Final

SLICE39G_SPEC_ID: Final[str] = (
    "aiweb-slice39g-meaning-structure-manifest-candidate-integration"
)
SLICE39G_SPEC_VERSION: Final[str] = (
    "aiweb-slice39g-meaning-structure-manifest-candidate-integration-v1"
)
SLICE39G_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-slice39g-meaning-structure-manifest-candidate-integration-v1"
)
SLICE39G_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE39G_COMPANION_VERSION: Final[str] = "v1.0.0"

SLICE39G_ADAPTER_DECISION: Final[str] = "versioned_companion_required"

SLICE39G_ADAPTER_DECISION_REASONS: Final[tuple[str, ...]] = (
    "msm_v1_candidate_record_has_no_exact_source_checksum_or_span_custody",
    "msm_v1_candidate_record_has_no_operator_phase_or_scope_ancestry_custody",
    "msm_v1_candidate_record_has_no_registry_snapshot_or_resource_version_custody",
    "msm_v1_candidate_record_has_no_construction_receipt_custody",
    "msm_v1_candidate_record_has_no_candidate_limitation_reference_family",
    "msm_v1_candidate_record_has_no_candidate_alternative_relationship_family",
    "overloading_existing_msm_fields_would_misclassify_typed_slice39_records",
    "accepted_slice35_schema_must_not_be_modified_or_auto_migrated",
)

SLICE39G_REQUIRED_PATH: Final[tuple[str, ...]] = (
    "accepted_slice39f_constructor_result",
    "exact_constructor_result_validation",
    "exact_source_lineage_verification",
    "lossless_versioned_companion_custody",
    "exact_adapter_to_msm_v1_candidate_projection",
    "candidate_only_manifest_validation",
)

SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS: Final[tuple[str, ...]] = (
    "non_selection_outcomes",
    "selected_governed_meanings",
    "governed_result_references",
    "governed_outward_meanings",
    "expression_links",
    "validation_links",
    "delivery_or_containment_links",
)

SLICE39G_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "manifest_candidate_projection_is_not_full_slice39_candidate_state",
    "versioned_companion_is_custody_not_selected_meaning",
    "manifest_integration_is_not_gate_progression",
    "semantic_transition_trace_is_not_gate_outcome",
    "external_authority_reference_is_not_authority_grant",
    "candidate_limitation_is_not_clarification_required",
    "candidate_alternative_relationship_is_not_ambiguous_gate_outcome",
    "construction_status_is_not_non_selection_outcome",
    "constructed_candidate_is_not_selected_governed_meaning",
    "candidate_meaning_is_not_truth",
    "candidate_meaning_is_not_evidence",
    "candidate_meaning_is_not_permission",
    "capability_reference_is_not_capability_availability",
    "effect_boundary_is_not_execution",
    "request_meaning_is_not_authorization",
    "report_meaning_is_not_evidence_validity",
    "memory_meaning_is_not_memory_access",
    "delivery_meaning_is_not_delivery_authority",
    "installation_meaning_is_not_code_application_authority",
)

SLICE39G_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "accepted_slice35_schema_modification",
    "automatic_schema_migration",
    "raw_text_inspection",
    "new_structural_or_semantic_interpretation",
    "similarity_or_nearest_known_fallback",
    "hidden_repair_or_silent_role_filling",
    "silent_referent_resolution",
    "candidate_ranking_or_selection",
    "automatic_ambiguity_resolution",
    "non_selection_gate_outcome_creation",
    "selected_governed_meaning_creation",
    "governed_result_or_outward_meaning_creation",
    "expression_validation_or_delivery_link_creation",
    "truth_or_evidence_determination",
    "permission_or_capability_availability",
    "route_or_invocation",
    "tool_or_action",
    "memory_access",
    "rendering_or_delivery",
    "filesystem_or_network_access",
    "external_resource_loading",
    "language_model_embedding_vector_rag_similarity_authority",
    "bootstrap_integration_or_slice39_closeout",
)

__all__ = (
    "SLICE39G_ADAPTER_DECISION",
    "SLICE39G_ADAPTER_DECISION_REASONS",
    "SLICE39G_COMPANION_VERSION",
    "SLICE39G_PERMANENT_BOUNDARIES",
    "SLICE39G_PROFILE_VERSION",
    "SLICE39G_PROHIBITED_AUTHORITY",
    "SLICE39G_REQUIRED_EMPTY_MANIFEST_SECTIONS",
    "SLICE39G_REQUIRED_PATH",
    "SLICE39G_SCHEMA_VERSION",
    "SLICE39G_SPEC_ID",
    "SLICE39G_SPEC_VERSION",
)
