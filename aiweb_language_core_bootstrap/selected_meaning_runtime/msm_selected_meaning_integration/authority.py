"""Slice 41E MSM-v1 selected-meaning integration authority.

This module binds the exact additive adapter decision.  It does not modify the
accepted MSM-v1 schema and does not grant outward, truth, evidence, permission,
execution, route, tool, action, memory, rendering, or delivery authority.
"""
from __future__ import annotations

from typing import Final

SLICE41E_SPEC_ID: Final[str] = (
    "aiweb-slice41e-msm-v1-selected-meaning-integration-and-custody"
)
SLICE41E_SPEC_VERSION: Final[str] = (
    "aiweb-slice41e-msm-v1-selected-meaning-integration-and-custody-v1"
)
SLICE41E_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-slice41e-msm-selected-meaning-integration-v1"
)
SLICE41E_PROFILE_KEY: Final[str] = "strict_additive_msm_selected_meaning_integration"
SLICE41E_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE41E_COMPANION_VERSION: Final[str] = "v1.0.0"
SLICE41E_RECEIPT_VERSION: Final[str] = "v1.0.0"
SLICE41E_ADAPTER_DECISION: Final[str] = "exact_additive_adapter_and_versioned_companion"
SLICE41E_ACCEPTED_PARENT_HEAD: Final[str] = "95ba97835634d35f097267dae20d555b2b80bbcd"
SLICE41E_ACCEPTED_PARENT_TREE: Final[str] = "7d7d2c1cb40f2fd650ad1358c36bb7f5e2acd16f"
SLICE41E_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 41D selected meaning construction alternative preservation"
)
SLICE41E_COMMIT_SUBJECT: Final[str] = (
    "Slice 41E MSM-v1 selected meaning integration and custody"
)

SLICE41E_GOVERNING_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    "canonical_roadmap:slice41e",
    "msm-v1:selected_governed_meanings",
    "slice39g:manifest_candidate_integration",
    "slice40h:msm_gate_custody_companion",
    "slice41c:selection_eligibility_result",
    "slice41d:selected_meaning_package",
    "slice41d:selection_receipt",
)

SLICE41E_REQUIRED_PATH: Final[tuple[str, ...]] = (
    "exact_slice40h_successor_manifest",
    "exact_slice40h_custody_companion",
    "exact_valid_slice41d_construction_input",
    "exact_valid_slice41d_selected_meaning_package",
    "selection_receipt_authority_reference",
    "immutable_msm_v1_successor",
    "lawful_candidate_to_selected_transition",
    "complete_successor_manifest_validation",
    "versioned_companion_and_receipt",
)

SLICE41E_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "msm_selected_meaning_integration_is_not_outward_meaning",
    "selected_candidate_reference_is_not_only_candidate_claim",
    "selected_meaning_is_not_truth",
    "selected_meaning_is_not_evidence",
    "selected_meaning_is_not_permission",
    "selected_meaning_is_not_execution",
    "selected_meaning_is_not_outward_answer",
    "selected_meaning_is_not_rendering",
    "selected_meaning_is_not_delivery",
    "selection_receipt_reference_is_not_general_authority",
    "candidate_meanings_remain_immutable_and_retained",
    "non_selection_outcomes_remain_immutable_and_retained",
    "slice40h_companion_remains_exact_and_retained",
    "msm_v1_schema_remains_unchanged",
    "versioned_companion_is_custody_not_schema_replacement",
    "semantic_transition_trace_is_custody_not_consequence_authority",
)

SLICE41E_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "msm_v1_schema_rewrite",
    "automatic_schema_migration",
    "candidate_meaning_deletion",
    "non_selection_outcome_deletion",
    "slice40h_custody_deletion",
    "candidate_ranking_or_reselection",
    "semantic_enrichment_or_deletion",
    "alternative_erasure",
    "governed_result_reference_creation",
    "governed_outward_meaning_creation",
    "expression_link_creation",
    "validation_link_creation",
    "delivery_or_containment_link_creation",
    "truth_or_evidence_claim",
    "permission_or_execution_authority",
    "capability_availability",
    "route_or_invocation",
    "tool_or_action",
    "memory_access_or_write",
    "rendering_or_delivery",
    "filesystem_or_network_runtime_effect",
    "external_resource_loading",
    "language_model_embedding_vector_rag_similarity_authority",
    "bootstrap_integration_or_slice41_closeout",
)

SLICE41E_REQUIRED_EMPTY_SUCCESSOR_SECTIONS: Final[tuple[str, ...]] = (
    "governed_result_references",
    "governed_outward_meanings",
    "expression_links",
    "validation_links",
    "delivery_or_containment_links",
)

__all__ = tuple(name for name in globals() if name.startswith("SLICE41E_"))
