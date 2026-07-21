"""Binding authority constants for Slice 42E controlled plan construction.

Slice 42E constructs deterministic expression structure from an exact Slice
42D obligation package.  It may create a controlled expression plan, including
blocked, refusal-preserving and unresolved-preserving containment plans.  It
may not realize words, create a human-readable expression candidate, integrate
MSM-v1, invoke Echo, deliver content, access memory or resources, call tools,
or perform actions.
"""

from __future__ import annotations

from typing import Final


SLICE42E_ACCEPTED_PARENT_HEAD: Final[str] = (
    "64bd7a1fbb4e8d374d5a49808de60e69ba4adc25"
)
SLICE42E_ACCEPTED_PARENT_TREE: Final[str] = (
    "6cb77aab753d2d6164ee07372bab6d09d47acf89"
)
SLICE42E_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 42D preservation obligation projection"
)

SLICE42E_SCHEMA_VERSION: Final[str] = (
    "aiweb-slice42e-controlled-expression-plan-construction-v1"
)
SLICE42E_SPEC_ID: Final[str] = "canonical-roadmap:slice42e"
SLICE42E_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE42E_PROFILE_KEY: Final[str] = (
    "exact_receipt_bound_controlled_expression_plan_construction"
)
SLICE42E_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE42E_PLAN_AUTHORITY_KEY: Final[str] = (
    "outward-expression-controlled-plan-construction"
)
DIGEST_ALGORITHM: Final[str] = "sha256"

SLICE42E_PLAN_DISPOSITION_VALUES: Final[tuple[str, ...]] = (
    "authorized_meaning_plan",
    "blocked_consequence_plan",
    "refusal_preserving_plan",
    "unresolved_preserving_plan",
    "held_pending_authority",
    "indeterminate",
)

SLICE42E_SECTION_ORDER_VALUES: Final[tuple[str, ...]] = (
    "governing_disposition",
    "selected_meaning",
    "active_scope",
    "certainty",
    "evidence_status",
    "meaning_modifiers",
    "inherited_limitations",
    "required_qualifications",
    "required_caveats",
    "refusal_boundaries",
    "unresolved_conditions",
    "ambiguity",
    "unsupported_states",
    "memory_authority",
    "external_resource_status",
    "delivery_authority",
    "privacy_identity_boundaries",
)

SLICE42E_GOVERNING_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    "AI.Web Forge Canonical Production Roadmap v1.0/ 7-12-2026:Slice42E",
    "accepted_slice42d:preservation_obligation_projection",
    "accepted_slice42c:authorized_meaning_admission_and_expression_eligibility",
    "accepted_slice42a:expression_plan_boundary_shape",
    "accepted_slice42b:deterministic_validation_identity_versioning_lifecycle",
    "document9:outbound_blocked_refusal_unresolved_and_limitation_preservation",
    "document3:governed_outward_meaning_to_rule_governed_expression_planning",
)

SLICE42E_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "exact_slice42d_projection_input_result_and_obligation_package_are_required",
    "slice42d_projection_is_not_expression_plan_authority",
    "plan_authority_must_be_separate_explicit_versioned_and_receipt_bound",
    "expression_plan_is_structure_not_final_text",
    "all_slice42d_obligation_categories_must_be_preserved_exactly",
    "governing_disposition_precedes_lower_order_expression_choices",
    "blocked_refusal_and_unresolved_plans_are_nonaffirmative_containment_plans",
    "selected_meaning_may_not_be_rewritten_or_enlarged",
    "active_scope_may_not_be_expanded",
    "certainty_may_not_be_upgraded",
    "evidence_status_may_not_be_upgraded",
    "meaning_modifiers_may_not_be_removed_or_invented",
    "inherited_limitations_may_not_be_removed",
    "required_qualifications_and_caveats_may_not_be_omitted",
    "refusal_boundaries_may_not_be_softened",
    "unresolved_ambiguity_and_unsupported_states_may_not_be_erased_or_guessed",
    "memory_resource_delivery_and_privacy_status_remain_custody_only",
    "lower_order_wording_choices_may_not_override_higher_order_semantics",
    "ancestry_to_authorized_selected_meaning_must_remain_exact",
    "plan_construction_is_not_governed_outward_meaning_msm_integration",
    "plan_construction_is_not_surface_realization",
    "plan_construction_is_not_echo_validation_or_delivery",
    "plan_construction_is_not_truth_evidence_permission_or_execution_authority",
    "plan_construction_is_not_route_api_network_filesystem_memory_tool_or_action_authority",
    "no_llm_embedding_vector_rag_similarity_or_hidden_classifier_authority",
    "gp014_is_not_superseded",
)

SLICE42E_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "planning_authority_inference_from_slice42d_projection",
    "record_repair_or_nearest_known_substitution",
    "obligation_omission",
    "structural_reordering_outside_permitted_order",
    "scope_expansion",
    "certainty_upgrade",
    "evidence_status_upgrade",
    "modifier_omission_or_invention",
    "qualification_omission",
    "caveat_omission",
    "refusal_softening",
    "unresolved_condition_resolution",
    "ambiguity_erasure",
    "unsupported_state_erasure_or_guessing",
    "lower_order_override_of_higher_order_semantics",
    "selected_meaning_rewrite",
    "human_readable_wording_or_surface_realization",
    "governed_outward_meaning_msm_integration",
    "expression_candidate_creation",
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
    if name.startswith("SLICE42E_") or name == "DIGEST_ALGORITHM"
)
