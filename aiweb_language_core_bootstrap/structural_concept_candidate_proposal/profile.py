"""Human-approved bounded Slice 37F proposal profile."""

from __future__ import annotations

from .identity import with_expected_id
from .schema import (
    SLICE37F_NON_AUTHORITY_BOUNDARIES,
    StructuralConceptProposalProfile,
)
from ..controlled_concept_sense_registry.built_in_registry import (
    current_namespace,
)
from ..controlled_concept_sense_registry.sense_term_mapping_registry import (
    SLICE37D_DOMAIN_SCOPE,
    SLICE37D_NAMESPACE_SCOPE,
)


def build_default_structural_concept_proposal_profile(
) -> StructuralConceptProposalProfile:
    namespace = current_namespace()
    return with_expected_id(
        StructuralConceptProposalProfile(
            profile_id="",
            profile_key="slice37f_exact_source_registry_profile",
            profile_version="1.0.0",
            explicit_invocation_required=True,
            offline_only=True,
            standard_library_only=True,
            deterministic=True,
            immutable_records=True,
            exact_source_preservation_required=True,
            exact_case_sensitive_matching=True,
            ascii_identifier_boundary_profile=True,
            normalization_allowed=False,
            casefolding_allowed=False,
            spelling_correction_allowed=False,
            stemming_allowed=False,
            synonym_expansion_allowed=False,
            nearest_match_allowed=False,
            frequency_ranking_allowed=False,
            semantic_similarity_allowed=False,
            model_inference_allowed=False,
            dictionary_fallback_allowed=False,
            language_tags=("en", "und-x-aiweb"),
            namespace_id=namespace.namespace_id,
            namespace_scope=SLICE37D_NAMESPACE_SCOPE,
            domain_scope=SLICE37D_DOMAIN_SCOPE,
            structural_result_consumption_allowed=True,
            exact_term_lookup_allowed=True,
            concept_candidate_proposal_allowed=True,
            sense_candidate_proposal_allowed=True,
            preserve_zero_one_many=True,
            preserve_unresolved_alternatives=True,
            explicit_unknown_required=True,
            explicit_unsupported_required=True,
            candidate_meaning_creation_allowed=False,
            selected_meaning_allowed=False,
            selected_sense_allowed=False,
            predicate_identity_allowed=False,
            participant_role_assignment_allowed=False,
            truth_determination_allowed=False,
            evidence_validity_determination_allowed=False,
            clarification_allowed=False,
            permission_inference_allowed=False,
            capability_routing_allowed=False,
            tool_invocation_allowed=False,
            action_execution_allowed=False,
            memory_read_allowed=False,
            memory_write_allowed=False,
            outward_rendering_allowed=False,
            delivery_allowed=False,
            non_authority_boundaries=SLICE37F_NON_AUTHORITY_BOUNDARIES,
        )
    )
