"""Binding authority constants for Slice 42F deterministic surface realization.

Slice 42F converts an exact accepted Slice 42E expression plan into one
human-readable, deterministic, unvalidated expression candidate.  Only
explicitly admitted realization rules and exact controlled resources may
contribute text.  Realization must preserve claim scope, certainty, evidence
status, limitations, caveats, refusal boundaries, unresolved conditions and
ancestry.  It is not Echo validation and does not authorize delivery.
"""

from __future__ import annotations

from typing import Final


SLICE42F_ACCEPTED_PARENT_HEAD: Final[str] = (
    "48f4b6d698350461eea3aec95b7b2cc8ec08b204"
)
SLICE42F_ACCEPTED_PARENT_TREE: Final[str] = (
    "734b9d55e5341b8d60de982ad9b3f6ca7d425c98"
)
SLICE42F_ACCEPTED_PARENT_SUBJECT: Final[str] = (
    "Slice 42E controlled expression plan construction"
)

SLICE42F_SCHEMA_VERSION: Final[str] = (
    "aiweb-slice42f-deterministic-surface-realization-v1"
)
SLICE42F_SPEC_ID: Final[str] = "canonical-roadmap:slice42f"
SLICE42F_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE42F_PROFILE_KEY: Final[str] = (
    "exact_receipt_bound_deterministic_surface_realization"
)
SLICE42F_PROFILE_VERSION: Final[str] = "v1.0.0"
SLICE42F_REALIZATION_AUTHORITY_KEY: Final[str] = (
    "outward-expression-deterministic-surface-realization"
)
SLICE42F_RESOURCE_PROFILE_KEY: Final[str] = (
    "admitted_builtin_surface_realization_resources"
)
SLICE42F_RESOURCE_PROFILE_VERSION: Final[str] = "v1.0.0"
DIGEST_ALGORITHM: Final[str] = "sha256"

SLICE42F_DISPOSITION_VALUES: Final[tuple[str, ...]] = (
    "authorized_expression_candidate",
    "blocked_expression_candidate",
    "refusal_expression_candidate",
    "unresolved_expression_candidate",
    "held_pending_authority",
    "indeterminate",
)

SLICE42F_ADMITTED_RULE_REFS: Final[tuple[str, ...]] = (
    "slice42f-rule:exact-plan-disposition",
    "slice42f-rule:controlled-template-selection",
    "slice42f-rule:authorized-claim-resource-required",
    "slice42f-rule:containment-never-affirmative",
    "slice42f-rule:certainty-visible-without-upgrade",
    "slice42f-rule:evidence-status-visible-without-upgrade",
    "slice42f-rule:limitations-visible",
    "slice42f-rule:qualifications-and-caveats-visible",
    "slice42f-rule:refusal-boundaries-visible",
    "slice42f-rule:unresolved-ambiguity-unsupported-visible",
    "slice42f-rule:memory-resource-delivery-status-visible",
    "slice42f-rule:privacy-identity-boundaries-visible",
    "slice42f-rule:exact-reference-order",
    "slice42f-rule:unvalidated-candidate-marker",
    "slice42f-rule:deterministic-trace-and-receipt",
)

SLICE42F_REQUIRED_TEMPLATE_KEYS: Final[tuple[str, ...]] = (
    "template:authorized_meaning_plan",
    "template:blocked_consequence_plan",
    "template:refusal_preserving_plan",
    "template:unresolved_preserving_plan",
)

SLICE42F_GOVERNING_AUTHORITY_REFS: Final[tuple[str, ...]] = (
    "AI.Web Forge Canonical Production Roadmap v1.0/ 7-12-2026:Slice42F",
    "accepted_slice42e:controlled_expression_plan_construction",
    "accepted_slice42d:preservation_obligation_projection",
    "accepted_slice42a:realized_expression_boundary_shape",
    "accepted_slice42b:deterministic_validation_identity_versioning_lifecycle",
    "document9:outbound_meaning_ambiguity_unsupported_limitation_and_authority_verification",
    "document3:rule_governed_surface_realization_and_controlled_reversibility",
)

SLICE42F_PERMANENT_BOUNDARIES: Final[tuple[str, ...]] = (
    "exact_slice42e_plan_input_result_and_expression_plan_are_required",
    "slice42e_plan_is_not_surface_realization_authority",
    "surface_realization_authority_must_be_separate_explicit_versioned_and_receipt_bound",
    "only_admitted_deterministic_rules_and_controlled_resources_may_contribute_text",
    "authorized_claim_text_requires_exact_controlled_claim_resource",
    "missing_controlled_claim_text_must_hold_not_guess",
    "blocked_refusal_and_unresolved_plans_must_remain_nonaffirmative",
    "selected_meaning_may_not_be_rewritten_strengthened_or_enlarged",
    "active_scope_may_not_be_expanded",
    "certainty_may_not_be_upgraded_or_hidden",
    "evidence_status_may_not_be_upgraded_or_hidden",
    "limitations_qualifications_caveats_refusal_and_unresolved_conditions_must_remain_visible",
    "ambiguity_and_unsupported_states_may_not_be_erased_or_guessed",
    "memory_resource_delivery_privacy_and_identity_status_remain_visible_custody",
    "realized_text_and_segments_must_be_deterministic",
    "realization_trace_and_receipt_must_bind_exact_plan_text_rules_resources_and_ancestry",
    "output_is_an_unvalidated_expression_candidate",
    "surface_realization_is_not_governed_outward_meaning_msm_integration",
    "surface_realization_is_not_echo_validation",
    "surface_realization_is_not_delivery",
    "surface_realization_is_not_truth_evidence_permission_or_execution_authority",
    "surface_realization_is_not_route_api_network_filesystem_memory_tool_or_action_authority",
    "no_llm_embedding_vector_rag_similarity_or_hidden_classifier_authority",
    "gp014_is_not_superseded",
)

SLICE42F_PROHIBITED_AUTHORITY: Final[tuple[str, ...]] = (
    "realization_authority_inference_from_slice42e_plan",
    "unadmitted_rule_or_resource_use",
    "free_form_generation",
    "record_repair_or_nearest_known_substitution",
    "claim_invention",
    "claim_strengthening",
    "scope_expansion",
    "certainty_upgrade",
    "evidence_status_upgrade",
    "limitation_omission",
    "qualification_omission",
    "caveat_omission",
    "refusal_softening",
    "unresolved_condition_resolution",
    "ambiguity_erasure",
    "unsupported_state_erasure_or_guessing",
    "memory_resource_delivery_or_privacy_status_upgrade",
    "selected_meaning_rewrite",
    "governed_outward_meaning_msm_integration",
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
    if name.startswith("SLICE42F_") or name == "DIGEST_ALGORITHM"
)
