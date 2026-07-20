"""Slice 41C selection-eligibility authority contract.

This module defines the exact, candidate-specific authority profile used by the
Slice 41C evaluator.  It does not create a selected meaning, rank candidates,
modify MSM-v1, authorize action, or infer missing support.
"""
from __future__ import annotations

SLICE41C_ACCEPTED_PARENT_HEAD = "f48ed086c19f1a24fd23710cd2d852326ccee229"
SLICE41C_ACCEPTED_PARENT_TREE = "0b9a9af60ab5de8c71841dbbe7e5a30402fd38fd"
SLICE41C_ACCEPTED_PARENT_SUBJECT = (
    "Slice 41B deterministic validation identity versioning lifecycle"
)
SLICE41C_SPEC_ID = "aiweb-slice41c-selection-eligibility-evaluation-runtime"
SLICE41C_SPEC_VERSION = "aiweb-slice41c-selection-eligibility-evaluation-runtime-v1"
SLICE41C_SCHEMA_VERSION = "aiweb-slice41c-selection-eligibility-evaluation-runtime-v1"
SLICE41C_PROFILE_VERSION = "v1.0.0"
SLICE41C_PROFILE_KEY = "strict_candidate_specific_selection_eligibility"
SLICE41C_PROFILE_ID = "selection_eligibility_profile:strict_candidate_specific:v1"
DIGEST_ALGORITHM = "sha256"

SLICE41C_GOVERNING_AUTHORITY_REFS = (
    "AI.Web Forge Canonical Production Roadmap v1.0/ 7-12-2026:Slice41C",
    "MeaningStructureManifest v1:selected-meaning-custody-boundary",
    "RMC Language Law v1:unsupported-unknown-ambiguity-preservation",
    "RMC Verbal Cognition Gate Engine v1:candidate-specific-selection-support",
    "Slice 40G:gate-composition-non-selection-disposition-runtime",
    "Slice 40H:MSM-gate-custody-companion",
    "Slice 41A:selected-meaning-runtime-core-schema",
    "Slice 41B:selected-meaning-runtime-validation-identity-lifecycle",
)

SLICE41C_PERMITTED_OUTCOMES = (
    "eligible_for_selected_meaning_construction",
    "held_pending_authority",
    "materially_unresolved",
    "clarification_dependent",
    "unsupported",
    "conflicted",
    "indeterminate",
    "not_eligible",
)

SLICE41C_REQUIRED_POSITIVE_DISPOSITION = (
    "candidate_supported_for_later_selection_review",
)

SLICE41C_ADVERSE_DISPOSITION_PRECEDENCE = (
    "conflicted",
    "unsupported",
    "clarification_dependent",
    "materially_unresolved",
    "held_pending_authority",
    "not_eligible",
    "indeterminate",
)

SLICE41C_PERMANENT_BOUNDARIES = (
    "eligibility_is_not_selection",
    "eligibility_is_not_selected_meaning",
    "eligibility_is_not_msm_mutation",
    "valid_record_is_not_valid_candidate_meaning",
    "valid_record_is_not_successful_gate_result",
    "valid_record_is_not_selection_eligibility",
    "selection_lifecycle_is_not_selected_meaning",
    "positive_selection_review_is_not_automatic_eligibility",
    "one_candidate_is_not_automatic_eligibility",
    "only_remaining_candidate_is_not_automatic_eligibility",
    "first_candidate_is_not_automatic_eligibility",
    "safest_candidate_is_not_automatic_eligibility",
    "understood_meaning_is_not_permission",
    "refusal_relevance_must_not_be_erased",
    "blocked_progression_must_not_be_erased",
    "unresolved_alternatives_must_not_be_erased",
    "candidate_specific_support_is_required",
    "all_four_gate_results_must_be_preserved",
    "composition_result_must_be_exact",
    "msm_gate_custody_must_be_exact",
    "confidence_scoring_is_prohibited",
    "probability_ranking_is_prohibited",
    "semantic_similarity_is_prohibited",
    "nearest_known_substitution_is_prohibited",
    "language_model_or_hidden_classifier_is_prohibited",
    "truth_evidence_permission_execution_are_out_of_scope",
    "route_tool_action_memory_rendering_delivery_are_out_of_scope",
)

SLICE41C_PROHIBITED_AUTHORITY = (
    "candidate_ranking",
    "candidate_selection",
    "selected_meaning_construction",
    "msm_v1_mutation",
    "automatic_only_candidate_selection",
    "automatic_first_candidate_selection",
    "automatic_safest_candidate_selection",
    "confidence_scoring",
    "probability_ranking",
    "semantic_similarity",
    "nearest_known_substitution",
    "language_model",
    "hidden_classifier",
    "refusal_relevance_erasure",
    "blocked_progression_erasure",
    "unresolved_alternative_erasure",
    "permission_conversion",
    "truth_determination",
    "evidence_validation",
    "execution_authorization",
    "route_creation",
    "tool_invocation",
    "action_performance",
    "memory_access_or_write",
    "rendering_or_delivery",
    "external_resource_loading",
    "bootstrap_integration",
)

__all__ = tuple(name for name in globals() if name.startswith("SLICE41C_")) + (
    "DIGEST_ALGORITHM",
)
