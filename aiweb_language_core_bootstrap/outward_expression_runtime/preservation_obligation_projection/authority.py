"""Binding authority constants for Slice 42D preservation projection.

Slice 42D is intentionally narrow.  It may project an exact, immutable
expression-obligation package from an already validated Slice 42C state.  It
may not construct outward meaning, plan expression order, realize text, invoke
Echo, deliver content, access memory, load external resources, call tools, or
perform actions.
"""

from __future__ import annotations

from typing import Final


SLICE42D_ACCEPTED_PARENT_HEAD: Final[str] = (
    "b6f19dc58d56eb34044630efac2540306e855ffa"
)
SLICE42D_ACCEPTED_PARENT_TREE: Final[str] = (
    "7fd6ec02fce4a258bf4c3ed1347ae8ce7010992b"
)
SLICE42D_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 42C authorized meaning admission and expression eligibility"
)

SLICE42D_SCHEMA_VERSION: Final[str] = (
    "aiweb-slice42d-preservation-obligation-projection-v1"
)
SLICE42D_SPEC_ID: Final[str] = "canonical-roadmap:slice42d"
SLICE42D_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE42D_PROFILE_KEY: Final[str] = (
    "exact_receipt_bound_preservation_obligation_projection"
)
SLICE42D_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE42D_PROJECTION_AUTHORITY_KEY: Final[str] = (
    "outward-expression-preservation-obligation-projection"
)
DIGEST_ALGORITHM: Final[str] = "sha256"

# These negative status references already exist in the accepted Slice 42A/42B
# source and are promoted here from fixture-only custody into exact projected
# status markers.  They do not grant the authority they describe.
SLICE42D_BOUNDED_CERTAINTY_REF: Final[str] = "certainty:bounded"
SLICE42D_EVIDENCE_NOT_VALIDATED_REF: Final[str] = "evidence:not_validated"
SLICE42D_MEMORY_NO_WRITE_AUTHORITY_REF: Final[str] = (
    "memory:no_write_authority"
)
SLICE42D_EXTERNAL_RESOURCE_NOT_LOADED_REF: Final[str] = (
    "resource:not_loaded"
)
SLICE42D_DELIVERY_NOT_AUTHORIZED_REF: Final[str] = (
    "delivery:not_authorized"
)
SLICE42D_PRIVACY_IDENTITY_BOUNDARY_REF: Final[str] = (
    "privacy:identity-boundary"
)

SLICE42D_OBLIGATION_CATEGORY_NAMES: Final[tuple[str, ...]] = (
    "active_scope",
    "certainty_level",
    "evidence_status",
    "inherited_limitations",
    "required_caveats",
    "refusal_relevant_boundaries",
    "unresolved_conditions",
    "memory_authority",
    "external_resource_status",
    "delivery_authority",
)

SLICE42D_GOVERNING_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    "AI.Web Forge Canonical Production Roadmap v1.0/ 7-12-2026:Slice42D",
    "accepted_slice42c:authorized_meaning_admission_and_expression_eligibility",
    "accepted_slice42a:expression_preservation_obligation_custody_shape",
    "accepted_slice42b:deterministic_validation_identity_versioning_lifecycle",
    "document9:outbound_selected_meaning_and_authority_status_preservation",
    "document3:scope_certainty_evidence_caveat_refusal_and_unresolved_preservation",
)

SLICE42D_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "exact_slice42c_state_is_required",
    "slice42c_eligibility_is_not_projection_authority",
    "projection_authority_must_be_separate_explicit_versioned_and_receipt_bound",
    "all_obligation_categories_remain_separate",
    "selected_meaning_is_preserved_without_rewrite",
    "active_scope_may_not_be_expanded",
    "certainty_may_not_be_upgraded",
    "evidence_status_may_not_be_upgraded",
    "inherited_limitations_may_not_be_removed",
    "required_caveats_may_not_be_omitted",
    "refusal_relevant_boundaries_may_not_be_softened",
    "unresolved_conditions_may_not_be_resolved_by_projection",
    "ambiguity_may_not_be_erased",
    "unsupported_states_may_not_be_guessed_or_erased",
    "memory_status_is_custody_not_memory_access_or_write_authority",
    "external_resource_status_is_custody_not_resource_load_authority",
    "delivery_status_is_custody_not_delivery_authority",
    "projection_is_not_governed_outward_meaning_construction",
    "projection_is_not_expression_plan_construction",
    "projection_is_not_surface_realization",
    "projection_is_not_echo_validation",
    "projection_is_not_truth_evidence_permission_or_execution_authority",
    "projection_is_not_route_api_network_filesystem_tool_action_or_memory_authority",
    "no_llm_embedding_vector_rag_similarity_or_hidden_classifier_authority",
    "gp014_is_not_superseded",
)

SLICE42D_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "projection_authority_inference_from_slice42c_eligibility",
    "record_repair_or_nearest_known_substitution",
    "scope_expansion",
    "certainty_upgrade",
    "evidence_status_upgrade",
    "limitation_omission",
    "caveat_omission",
    "refusal_softening",
    "unresolved_condition_resolution",
    "ambiguity_erasure",
    "unsupported_state_erasure_or_guessing",
    "memory_authority_upgrade",
    "external_resource_status_upgrade",
    "delivery_authority_upgrade",
    "selected_meaning_rewrite",
    "governed_outward_meaning_construction",
    "expression_plan_construction",
    "surface_realization",
    "msm_v1_mutation_or_integration",
    "echo_validation",
    "bootstrap_activation",
    "delivery",
    "truth_evidence_permission_execution",
    "route_api_network_filesystem_memory_tool_action",
    "external_resource_or_model_authority",
    "gp014_supersession",
)


__all__ = tuple(
    name
    for name in globals()
    if name.startswith("SLICE42D_") or name == "DIGEST_ALGORITHM"
)
