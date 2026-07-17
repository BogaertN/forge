"""Canonical immutable Slice 38G profile and registry snapshots."""

from __future__ import annotations

from .authority import SLICE38G_NON_AUTHORITY_BOUNDARIES
from .compatibility import CANONICAL_COMPATIBILITY_SNAPSHOT
from .identity import with_expected_id
from .schema import PredicateRoleFrameProposalProfile
from .snapshot import build_slice38_registry_snapshot


def build_default_predicate_role_frame_proposal_profile(
) -> PredicateRoleFrameProposalProfile:
    raw = PredicateRoleFrameProposalProfile(
        profile_id="",
        profile_key="slice38g_exact_candidate_proposal",
        profile_version="v1.0.0",
        explicit_invocation_required=True,
        offline_only=True,
        standard_library_only=True,
        deterministic=True,
        immutable_records=True,
        exact_source_ancestry_required=True,
        exact_registry_snapshot_required=True,
        exact_identity_lookup_only=True,
        zero_one_many_preserved=True,
        unresolved_alternatives_preserved=True,
        explicit_unknown_required=True,
        explicit_unsupported_required=True,
        incomplete_state_required=True,
        conflict_state_required=True,
        caller_supplied_surface_hint_allowed=False,
        normalization_allowed=False,
        nearest_known_substitution_allowed=False,
        semantic_similarity_allowed=False,
        language_model_allowed=False,
        selected_predicate_allowed=False,
        selected_frame_allowed=False,
        selected_participant_assignment_allowed=False,
        candidate_meaning_creation_allowed=False,
        selected_meaning_allowed=False,
        permission_inference_allowed=False,
        route_creation_allowed=False,
        tool_invocation_allowed=False,
        action_execution_allowed=False,
        memory_access_allowed=False,
        delivery_allowed=False,
        evidence_validity_allowed=False,
        truth_determination_allowed=False,
        clarification_outcome_allowed=False,
        refusal_outcome_allowed=False,
        blocked_progression_outcome_allowed=False,
        non_authority_boundaries=SLICE38G_NON_AUTHORITY_BOUNDARIES,
    )
    return with_expected_id(raw, "profile_id")


DEFAULT_PROPOSAL_PROFILE = build_default_predicate_role_frame_proposal_profile()
SLICE38_REGISTRY_SNAPSHOT = build_slice38_registry_snapshot()

__all__ = (
    "CANONICAL_COMPATIBILITY_SNAPSHOT",
    "DEFAULT_PROPOSAL_PROFILE",
    "SLICE38_REGISTRY_SNAPSHOT",
    "build_default_predicate_role_frame_proposal_profile",
)
