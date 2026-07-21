"""Binding Slice 42G MSM-v1 outward-expression integration authority.

Slice 42G is an exact additive adapter over the accepted dormant MSM-v1
records. It does not rewrite MSM-v1, validate the expression candidate through
Echo, authorize delivery, or grant truth, evidence, permission, execution,
route, tool, action, memory, filesystem, network, resource, model, or GP-014
supersession authority.
"""

from typing import Final

SLICE42G_SPEC_ID: Final[str] = (
    "aiweb-slice42g-msm-v1-outward-meaning-expression-link-custody"
)
SLICE42G_SPEC_VERSION: Final[str] = (
    "aiweb-slice42g-msm-v1-outward-meaning-expression-link-custody-v1"
)
SLICE42G_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-slice42g-msm-outward-expression-integration-v1"
)
SLICE42G_PROFILE_KEY: Final[str] = (
    "strict_additive_msm_outward_expression_integration"
)
SLICE42G_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE42G_COMPANION_VERSION: Final[str] = "v1.0.0"
SLICE42G_RECEIPT_VERSION: Final[str] = "v1.0.0"
SLICE42G_ADAPTER_DECISION: Final[str] = (
    "exact_additive_adapter_and_versioned_companion"
)
SLICE42G_ACCEPTED_PARENT_HEAD: Final[str] = (
    "535bba7c40542d66029b3e3a193ed23998fe711e"
)
SLICE42G_ACCEPTED_PARENT_TREE: Final[str] = (
    "48807967b0f2248220f505ad922116e50ed9fc8d"
)
SLICE42G_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 42F deterministic surface realization"
)
SLICE42G_COMMIT_SUBJECT: Final[str] = (
    "Slice 42G MSM-v1 outward meaning and expression-link custody"
)
DIGEST_ALGORITHM: Final[str] = "sha256"

SLICE42G_GOVERNING_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    "canonical-roadmap:slice42g",
    "msm-v1:governed-outward-meaning-record",
    "msm-v1:expression-link-record",
    "msm-v1:immutable-successor-lifecycle",
    "slice41e:msm-selected-meaning-integration",
    "slice42e:controlled-expression-plan",
    "slice42f:deterministic-surface-realization",
    "document9:outward-expression-custody-verification",
)

SLICE42G_REQUIRED_PATH: Final[tuple[str, ...]] = (
    "exact_slice41e_integration_input",
    "exact_slice41e_integration_result",
    "exact_slice42f_realization_input",
    "exact_slice42f_realization_result",
    "exact_unvalidated_expression_candidate",
    "existing_dormant_msm_v1_record_types",
    "exact_additive_external_authority_reference",
    "exact_additive_governed_outward_meaning_record",
    "exact_additive_expression_link_record",
    "selected_to_outward_lifecycle_trace",
    "outward_to_expression_lifecycle_trace",
    "immutable_msm_v1_successor",
    "complete_successor_manifest_validation",
    "versioned_custody_companion",
    "deterministic_integration_receipt",
)

SLICE42G_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "msm_v1_schema_remains_unchanged",
    "adapter_is_additive_not_rewrite",
    "source_manifest_remains_immutable",
    "selected_governed_meaning_remains_exact",
    "candidate_meanings_remain_exact_and_retained",
    "non_selection_outcomes_remain_exact_and_retained",
    "alternatives_remain_exact_and_retained",
    "unresolved_conditions_remain_exact_and_retained",
    "governed_result_references_remain_unchanged",
    "validation_links_remain_unchanged",
    "delivery_or_containment_links_remain_unchanged",
    "expression_candidate_remains_unvalidated",
    "expression_link_is_not_echo_validation",
    "expression_link_is_not_delivery_authority",
    "governed_outward_meaning_is_not_truth",
    "governed_outward_meaning_is_not_evidence_validation",
    "governed_outward_meaning_is_not_permission",
    "governed_outward_meaning_is_not_execution",
    "governed_outward_meaning_is_not_route_or_tool_authority",
    "realized_text_is_not_rewritten_or_strengthened",
    "certainty_and_evidence_status_remain_bounded",
    "caveats_refusal_and_unresolved_states_remain_preserved",
    "memory_resource_delivery_and_privacy_boundaries_remain_preserved",
    "echo_validation_belongs_to_slice43",
    "gp014_is_not_superseded",
)

SLICE42G_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "msm_v1_schema_rewrite",
    "automatic_schema_migration",
    "source_manifest_mutation",
    "candidate_meaning_deletion",
    "non_selection_outcome_deletion",
    "selected_governed_meaning_deletion_or_rewrite",
    "alternative_deletion",
    "unresolved_state_resolution",
    "governed_result_reference_creation",
    "validation_link_creation",
    "delivery_or_containment_link_creation",
    "expression_candidate_rewrite",
    "claim_strengthening",
    "scope_expansion",
    "certainty_upgrade",
    "evidence_status_upgrade",
    "caveat_omission",
    "refusal_softening",
    "ambiguity_erasure",
    "unsupported_state_erasure",
    "echo_validation_or_approval",
    "delivery_authorization_or_delivery",
    "truth_determination",
    "evidence_validation",
    "permission_grant",
    "execution_authorization",
    "route_or_api_creation",
    "tool_invocation",
    "action_execution",
    "memory_access_or_write",
    "filesystem_or_network_access",
    "external_resource_loading",
    "language_model_authority",
    "embedding_vector_rag_similarity_authority",
    "bootstrap_enablement_or_slice42_closeout",
    "gp014_supersession",
)

SLICE42G_ALLOWED_MSM_ADDITIONS: Final[tuple[str, ...]] = (
    "one_external_authority_reference",
    "one_governed_outward_meaning",
    "one_expression_link",
    "two_semantic_transition_traces",
)

SLICE42G_REQUIRED_UNCHANGED_SECTIONS: Final[tuple[str, ...]] = (
    "lineage_root",
    "candidate_meanings",
    "non_selection_outcomes",
    "selected_governed_meanings",
    "governed_result_references",
    "validation_links",
    "delivery_or_containment_links",
)

__all__ = tuple(name for name in globals() if name.startswith("SLICE42G_") or name == "DIGEST_ALGORITHM")
