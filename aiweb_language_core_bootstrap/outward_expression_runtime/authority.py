"""Binding Slice 42A schema-only and non-authority boundaries.

Slice 42A defines immutable custody shapes for later controlled outward
expression work.  It does not validate records, calculate identities, admit an
authority record, evaluate expression eligibility, project obligations,
construct governed outward meaning, build an expression plan, realize text,
modify MeaningStructureManifest v1, perform Echo validation, enable bootstrap
integration, or create delivery, truth, evidence, permission, execution,
memory, tool, action, route, API, network, filesystem, resource, or model
authority.
"""

from typing import Final


EXPRESSION_ELIGIBILITY_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_evaluated",
    "ready_for_later_evaluation",
    "evaluation_deferred",
    "evaluation_unavailable",
)

OUTWARD_MEANING_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_constructed",
    "ready_for_later_construction",
    "construction_deferred",
    "construction_unavailable",
)

EXPRESSION_PLAN_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_constructed",
    "ready_for_later_planning",
    "planning_deferred",
    "planning_unavailable",
)

REALIZED_EXPRESSION_CUSTODY_STATE_VALUES: Final[tuple[str, ...]] = (
    "not_realized",
    "ready_for_later_realization",
    "realization_deferred",
    "realization_unavailable",
)

MSM_OUTWARD_INTEGRATION_DECISION: Final[str] = (
    "deferred_to_slice42g_exact_additive_adapter"
)
MSM_V1_SCHEMA_MODIFICATION_ALLOWED: Final[bool] = False
MSM_V1_AUTOMATIC_MIGRATION_ALLOWED: Final[bool] = False
EXPRESSION_AUTHORITY_ADMISSION_ALLOWED: Final[bool] = False
EXPRESSION_ELIGIBILITY_EVALUATION_ALLOWED: Final[bool] = False
PRESERVATION_OBLIGATION_PROJECTION_ALLOWED: Final[bool] = False
GOVERNED_OUTWARD_MEANING_CONSTRUCTION_ALLOWED: Final[bool] = False
EXPRESSION_PLAN_CONSTRUCTION_ALLOWED: Final[bool] = False
SURFACE_REALIZATION_ALLOWED: Final[bool] = False
ECHO_VALIDATION_ALLOWED: Final[bool] = False
BOOTSTRAP_INTEGRATION_ALLOWED: Final[bool] = False
DELIVERY_AUTHORITY_ALLOWED: Final[bool] = False

EXPRESSION_ELIGIBILITY_NAMING_DECISION: Final[str] = (
    "deferred_to_slice42c_exact_source_and_authority_decision"
)
OUTWARD_MEANING_LIFECYCLE_NAMING_DECISION: Final[str] = (
    "deferred_to_slice42b_deterministic_lifecycle_decision"
)

DEFERRED_SLICE42_RUNTIME_AUTHORITY: Final[tuple[str, ...]] = (
    "deterministic_identity_calculation",
    "strict_validation",
    "canonical_serialization",
    "schema_and_profile_version_enforcement",
    "duplicate_and_collision_rejection",
    "governed_lifecycle_transitions",
    "cross_record_consistency_validation",
    "exact_selected_meaning_chain_admission",
    "exact_outward_expression_authority_admission",
    "expression_eligibility_evaluation",
    "preservation_obligation_projection",
    "governed_outward_meaning_construction",
    "controlled_expression_plan_construction",
    "deterministic_surface_realization",
    "realization_trace_construction",
    "realization_receipt_construction",
    "msm_v1_outward_meaning_integration",
    "msm_v1_expression_link_integration",
    "disabled_bootstrap_integration",
    "slice42_closeout",
    "slice43_rmc_echo_validation",
)

PERMANENT_OUTWARD_EXPRESSION_BOUNDARIES: Final[tuple[str, ...]] = (
    "schema_existence_is_not_expression_authority",
    "selected_meaning_is_not_expression_authority",
    "selected_meaning_alone_is_not_expression_eligibility",
    "selected_meaning_may_not_be_rewritten",
    "selected_candidate_identity_must_remain_exact",
    "selected_candidate_lineage_must_remain_exact",
    "selected_semantic_content_must_remain_exact",
    "candidate_alternatives_may_not_be_deleted",
    "non_selection_outcomes_may_not_be_deleted",
    "unresolved_state_may_not_be_silently_resolved",
    "ambiguity_may_not_be_silently_collapsed",
    "uncertainty_may_not_be_upgraded",
    "claim_strength_may_not_be_upgraded",
    "evidence_status_may_not_be_upgraded",
    "inherited_limitations_may_not_disappear",
    "required_caveats_may_not_be_omitted",
    "refusal_may_not_be_softened_into_permission",
    "memory_reference_is_not_memory_authority",
    "external_resource_reference_is_not_resource_admission",
    "delivery_reference_is_not_delivery_authority",
    "outward_expression_authority_must_be_exact_and_receipt_bound",
    "expression_eligibility_is_not_governed_outward_meaning",
    "governed_outward_meaning_is_not_expression_plan",
    "expression_plan_is_not_realized_expression",
    "realized_expression_is_not_echo_validation",
    "echo_validation_belongs_to_slice43",
    "echo_validation_is_not_delivery_authority",
    "expression_is_not_truth",
    "expression_is_not_evidence_validation",
    "expression_is_not_permission",
    "expression_is_not_execution",
    "expression_is_not_tool_routing",
    "expression_is_not_memory_write",
    "expression_is_not_delivery",
    "msm_v1_schema_is_not_rewritten",
    "gp014_is_not_superseded",
)

PROHIBITED_AUTHORITY_PATHS: Final[tuple[str, ...]] = (
    "language_model_authority",
    "embedding_authority",
    "vector_authority",
    "rag_authority",
    "semantic_similarity_authority",
    "neural_parser_authority",
    "hidden_classifier_authority",
    "nearest_known_substitution",
    "confidence_scoring",
    "probability_ranking",
    "selected_meaning_rewrite",
    "semantic_enrichment",
    "semantic_deletion",
    "alternative_deletion",
    "non_selection_deletion",
    "unresolved_state_resolution",
    "ambiguity_collapse",
    "uncertainty_upgrade",
    "claim_strength_upgrade",
    "evidence_status_upgrade",
    "caveat_omission",
    "refusal_softening",
    "truth_determination",
    "evidence_validation",
    "permission_grant",
    "execution_authorization",
    "capability_availability",
    "route_creation",
    "api_creation",
    "tool_invocation",
    "action_execution",
    "memory_access",
    "memory_write",
    "filesystem_read",
    "filesystem_write",
    "network_access",
    "external_resource_loading",
    "output_delivery",
    "msm_v1_mutation",
    "bootstrap_enablement",
    "echo_validation",
    "gp014_supersession",
)

REQUIRED_PRESERVATION_OBLIGATION_CATEGORIES: Final[tuple[str, ...]] = (
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

__all__ = tuple(name for name in globals() if not name.startswith("_"))
