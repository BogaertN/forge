"""Slice 41D selected-meaning construction authority contract.

The authority defined here is intentionally narrow.  Slice 41D may construct
one immutable selected-meaning package only from an exact successful Slice 41C
eligibility result.  It may not modify MSM-v1, render output, validate truth or
evidence, grant permission, authorize execution, or erase any alternative.
"""
from __future__ import annotations

SLICE41D_ACCEPTED_PARENT_HEAD = "d26423ccd5ed7c71b2f29f19ffd40c1010d87b98"
SLICE41D_ACCEPTED_PARENT_TREE = "d900c3e1e50bc9d94a0340ae0d0f60128985d273"
SLICE41D_ACCEPTED_PARENT_SUBJECT = (
    "Slice 41C deterministic selection eligibility evaluation runtime"
)
SLICE41D_SPEC_ID = "aiweb-slice41d-selected-meaning-construction-alternative-preservation"
SLICE41D_SPEC_VERSION = (
    "aiweb-slice41d-selected-meaning-construction-alternative-preservation-v1"
)
SLICE41D_SCHEMA_VERSION = SLICE41D_SPEC_VERSION
SLICE41D_PROFILE_VERSION = "v1.0.0"
SLICE41D_PROFILE_KEY = "strict_exact_selected_meaning_construction"
SLICE41D_PROFILE_ID = "selected_meaning_construction_profile:strict_exact:v1"
DIGEST_ALGORITHM = "sha256"

SLICE41D_GOVERNING_AUTHORITY_REFS = (
    "AI.Web Forge Canonical Production Roadmap v1.0/ 7-12-2026:Slice41D",
    "MeaningStructureManifest v1:selected-governed-meaning-record",
    "RMC Language Law v1:meaning-preservation-and-no-enlargement",
    "RMC Verbal Cognition Gate Engine v1:candidate-specific-selection-authority",
    "Slice 39G:manifest-candidate-companion-custody",
    "Slice 40G:gate-composition-and-non-selection-dispositions",
    "Slice 40H:MSM-gate-custody-companion",
    "Slice 41A:selected-meaning-runtime-core-schema",
    "Slice 41B:selected-meaning-runtime-validation-identity-lifecycle",
    "Slice 41C:deterministic-selection-eligibility-result",
)

SLICE41D_PERMANENT_BOUNDARIES = (
    "selected_candidate_is_not_only_candidate_that_ever_existed",
    "selected_meaning_is_not_truth",
    "selected_meaning_is_not_evidence",
    "selected_meaning_is_not_permission",
    "selected_meaning_is_not_execution",
    "selected_meaning_is_not_outward_answer",
    "selected_meaning_is_not_delivery",
    "selected_meaning_is_not_msm_v1_integration",
    "selected_meaning_is_not_governed_outward_meaning",
    "selected_meaning_is_not_expression",
    "successful_eligibility_is_required",
    "selected_candidate_identity_must_be_exact",
    "selected_candidate_lineage_must_be_exact",
    "semantic_content_must_be_exact",
    "semantic_enrichment_is_prohibited",
    "semantic_deletion_is_prohibited",
    "authority_sensitive_distinctions_must_be_preserved",
    "limitations_must_be_inherited",
    "blocked_consequence_markers_must_be_preserved",
    "refusal_relevance_must_be_preserved",
    "every_non_selected_candidate_must_be_preserved_by_exact_reference",
    "unresolved_alternatives_must_be_preserved_separately",
    "ambiguity_ancestry_must_be_preserved",
    "clarification_ancestry_must_be_preserved",
    "selection_trace_must_be_deterministic",
    "selection_receipt_must_be_deterministic",
    "candidate_ranking_is_prohibited",
    "confidence_scoring_is_prohibited",
    "probability_ranking_is_prohibited",
    "semantic_similarity_is_prohibited",
    "nearest_known_substitution_is_prohibited",
    "language_model_or_hidden_classifier_is_prohibited",
    "route_tool_action_memory_rendering_delivery_are_out_of_scope",
)

SLICE41D_PROHIBITED_AUTHORITY = (
    "candidate_ranking",
    "confidence_scoring",
    "probability_ranking",
    "semantic_similarity",
    "nearest_known_substitution",
    "language_model",
    "hidden_classifier",
    "automatic_only_candidate_selection",
    "automatic_first_candidate_selection",
    "automatic_safest_candidate_selection",
    "semantic_content_enrichment",
    "semantic_content_deletion",
    "alternative_deletion",
    "unresolved_alternative_erasure",
    "ambiguity_ancestry_erasure",
    "clarification_ancestry_erasure",
    "refusal_relevance_erasure",
    "blocked_progression_erasure",
    "msm_v1_mutation",
    "governed_outward_meaning_creation",
    "expression_creation",
    "truth_determination",
    "evidence_validation",
    "permission_grant",
    "execution_authorization",
    "route_creation",
    "tool_invocation",
    "action_performance",
    "memory_access_or_write",
    "rendering",
    "delivery",
    "external_resource_loading",
    "bootstrap_integration",
)

__all__ = tuple(name for name in globals() if name.startswith("SLICE41D_")) + (
    "DIGEST_ALGORITHM",
)
