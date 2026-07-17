"""Slice 38A authority profile and zero-population schema contract."""

from __future__ import annotations

from .schema import (
    PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    SLICE38A_DEFERRED_SCOPE,
    PredicateAuthorityProfile,
    PredicateRegistrySchemaContract,
    PredicateResourceKind,
)


_REQUIRED_RECORD_FAMILIES = (
    "PredicateProvenanceReference",
    "PredicateNamespaceIdentity",
    "ActionRootIdentity",
    "PredicateIdentity",
)


def build_slice38a_authority_profile() -> PredicateAuthorityProfile:
    provisional = PredicateAuthorityProfile(
        profile_id="",
        disabled_by_default=True,
        explicit_invocation_required=True,
        offline_only=True,
        standard_library_only=True,
        deterministic=True,
        immutable_records=True,
        exact_version_required=True,
        provenance_required=True,
        lifecycle_state_required=True,
        scope_non_scope_required=True,
        unknown_state_first_class=True,
        unresolved_state_first_class=True,
        unsupported_state_first_class=True,
        ambiguity_preserved=True,
        action_authority_separated=True,
        predicate_frame_dependency_required=True,
        participant_role_dependency_required=True,
        speech_act_separation_required=True,
        effect_boundary_dependency_required=True,
        capability_non_invocation_required=True,
        scale_is_not_authority=True,
        registry_population_installed=False,
        action_root_lookup_allowed=False,
        predicate_selection_allowed=False,
        occurrence_interpretation_allowed=False,
        participant_role_population_allowed=False,
        role_assignment_allowed=False,
        predicate_frame_population_allowed=False,
        frame_completion_allowed=False,
        capability_family_reference_population_allowed=False,
        candidate_meaning_creation_allowed=False,
        selected_meaning_allowed=False,
        selected_predicate_allowed=False,
        selected_frame_allowed=False,
        evidence_validation_allowed=False,
        memory_read_allowed=False,
        memory_write_allowed=False,
        external_resource_loading_allowed=False,
        llm_allowed=False,
        embedding_allowed=False,
        vector_database_allowed=False,
        semantic_similarity_allowed=False,
        rag_allowed=False,
        learned_parser_allowed=False,
        neural_classifier_allowed=False,
        api_route_allowed=False,
        capability_route_allowed=False,
        tool_activation_allowed=False,
        action_execution_allowed=False,
        outward_rendering_allowed=False,
        delivery_authorization_allowed=False,
        release_authorized=False,
        production_ready=False,
    )
    return PredicateAuthorityProfile(
        **{**provisional.to_dict(), "profile_id": provisional.expected_id()}
    )


def build_slice38a_schema_contract() -> PredicateRegistrySchemaContract:
    provisional = PredicateRegistrySchemaContract(
        contract_id="",
        resource_kinds=tuple(PredicateResourceKind),
        required_record_families=_REQUIRED_RECORD_FAMILIES,
        prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
        deferred_scope=SLICE38A_DEFERRED_SCOPE,
        registry_entry_count=0,
        namespace_entry_count=0,
        action_root_entry_count=0,
        predicate_entry_count=0,
        action_root_schema_defined=True,
        predicate_identity_schema_defined=True,
        registry_population_installed=False,
        action_root_lookup_installed=False,
        predicate_selection_installed=False,
        participant_role_schema_installed=False,
        predicate_frame_schema_installed=False,
        capability_reference_schema_installed=False,
        source_occurrence_integration_installed=False,
        selected_predicate_installed=False,
        action_authority_installed=False,
        slice37_boundaries_preserved=True,
        slice37_runtime_superseded=False,
    )
    return PredicateRegistrySchemaContract(
        **{**provisional.to_dict(), "contract_id": provisional.expected_id()}
    )
