"""Slice 37A authority-profile and empty schema-contract construction.

Construction here is deliberately limited to an authority profile and an
empty schema contract. No concept, sense, lexical reference, mapping,
semantic class, relation family, relation type, or relation instance is
installed by this module.
"""

from __future__ import annotations

from .schema import (
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    SLICE37A_DEFERRED_SCOPE,
    ConceptAuthorityProfile,
    ConceptRegistrySchemaContract,
    ConceptResourceKind,
)


_REQUIRED_RECORD_FAMILIES = (
    "ConceptProvenanceReference",
    "ConceptNamespaceIdentity",
    "ControlledConceptIdentity",
    "ControlledSenseIdentity",
    "ControlledLexicalReference",
    "TermConceptMappingIdentity",
    "SemanticClassIdentity",
    "SemanticRelationFamilyIdentity",
    "SemanticRelationTypeIdentity",
)


def build_slice37a_authority_profile() -> ConceptAuthorityProfile:
    provisional = ConceptAuthorityProfile(
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
        unknown_state_first_class=True,
        unresolved_state_first_class=True,
        ambiguity_preserved=True,
        scale_is_not_authority=True,
        registry_population_installed=False,
        concept_lookup_allowed=False,
        source_occurrence_mapping_allowed=False,
        sense_selection_allowed=False,
        semantic_relation_edge_population_allowed=False,
        structural_result_consumption_allowed=False,
        candidate_meaning_creation_allowed=False,
        selected_meaning_allowed=False,
        predicate_authority_allowed=False,
        participant_role_authority_allowed=False,
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
    return ConceptAuthorityProfile(
        **{
            **provisional.to_dict(),
            "profile_id": provisional.expected_id(),
        }
    )


def build_slice37a_schema_contract() -> ConceptRegistrySchemaContract:
    provisional = ConceptRegistrySchemaContract(
        contract_id="",
        resource_kinds=tuple(ConceptResourceKind),
        required_record_families=_REQUIRED_RECORD_FAMILIES,
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
        deferred_scope=SLICE37A_DEFERRED_SCOPE,
        registry_entry_count=0,
        concept_entry_count=0,
        sense_entry_count=0,
        lexical_reference_entry_count=0,
        term_mapping_entry_count=0,
        semantic_class_entry_count=0,
        relation_family_entry_count=0,
        relation_type_entry_count=0,
        registry_population_installed=False,
        lookup_installed=False,
        mapping_installed=False,
        sense_selection_installed=False,
        relation_edge_population_installed=False,
        structural_integration_installed=False,
        historical_slice8_preserved=True,
        historical_slice8_superseded=False,
    )
    return ConceptRegistrySchemaContract(
        **{
            **provisional.to_dict(),
            "contract_id": provisional.expected_id(),
        }
    )
