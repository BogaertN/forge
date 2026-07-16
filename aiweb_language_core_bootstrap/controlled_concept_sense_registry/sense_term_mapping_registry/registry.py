"""Closed read-only Slice 37D controlled-sense and term-mapping registry."""

from __future__ import annotations

from typing import Final

from ..built_in_registry.registry import BUILT_IN_REGISTRY
from .authority import (
    SLICE37D_DECISION_OWNER_REF,
    SLICE37D_HUMAN_APPROVAL_REF,
    SLICE37D_REGISTRY_AUTHORITY_LIMITATIONS,
)
from .identity import with_expected_manifest_id
from .records import (
    CURRENT_LEXICAL_REFERENCES,
    CURRENT_MAPPINGS,
    CURRENT_SENSES,
    GOVERNANCE_BATCH,
    OUTWARD_ELIGIBILITY_REFERENCES,
    PROHIBITED_EXPANSION_REFUSALS,
)
from .schema import (
    SLICE37D_SOURCE_AUTHORITY_PACKET_SHA256,
    SenseTermMappingRegistry,
    SenseTermMappingRegistryManifest,
)


_MANIFEST: Final[SenseTermMappingRegistryManifest] = with_expected_manifest_id(
    SenseTermMappingRegistryManifest(
        manifest_id="",
        registry_key=(
            "aiweb:language-core:concept-registry:"
            "sense-term-mapping:builtin:v1"
        ),
        source_authority_packet_sha256=(
            SLICE37D_SOURCE_AUTHORITY_PACKET_SHA256
        ),
        decision_owner_ref=SLICE37D_DECISION_OWNER_REF,
        human_approval_ref=SLICE37D_HUMAN_APPROVAL_REF,
        human_approved=True,
        read_only=True,
        closed_set=True,
        authority_limitations=SLICE37D_REGISTRY_AUTHORITY_LIMITATIONS,
        sense_refs=tuple(item.sense_id for item in CURRENT_SENSES),
        lexical_reference_refs=tuple(
            item.lexical_reference_id
            for item in CURRENT_LEXICAL_REFERENCES
        ),
        mapping_refs=tuple(item.mapping_id for item in CURRENT_MAPPINGS),
        outward_eligibility_refs=tuple(
            item.eligibility_id
            for item in OUTWARD_ELIGIBILITY_REFERENCES
        ),
        prohibited_expansion_refusal_refs=tuple(
            item.refusal_id
            for item in PROHIBITED_EXPANSION_REFUSALS
        ),
        exact_term_lookup_allowed=True,
        exact_reference_id_lookup_allowed=True,
        exact_sense_id_lookup_allowed=True,
        exact_mapping_id_lookup_allowed=True,
        registry_population_authorized=True,
        sense_population_authorized=True,
        lexical_reference_population_authorized=True,
        mapping_population_authorized=True,
        outward_eligibility_reference_population_authorized=True,
        occurrence_interpretation_installed=False,
        sense_selection_installed=False,
        candidate_meaning_creation_installed=False,
        structural_integration_installed=False,
        case_fold_expansion_installed=False,
        spelling_correction_installed=False,
        stemming_installed=False,
        synonym_expansion_installed=False,
        nearest_match_installed=False,
        frequency_ranking_installed=False,
        semantic_similarity_installed=False,
        embedding_installed=False,
        model_inference_installed=False,
        ordinary_dictionary_fallback_installed=False,
        external_resource_loading_installed=False,
        runtime_activation_installed=False,
        route_registration_installed=False,
        tool_activation_installed=False,
        memory_access_installed=False,
        action_execution_installed=False,
        rendering_installed=False,
        delivery_installed=False,
        semantic_classes_deferred_to_slice37e=True,
        semantic_relations_deferred_to_slice37e=True,
        structural_candidate_integration_deferred_to_slice37f=True,
    )
)


SENSE_TERM_MAPPING_REGISTRY: Final[SenseTermMappingRegistry] = (
    SenseTermMappingRegistry(
        manifest=_MANIFEST,
        concept_registry=BUILT_IN_REGISTRY,
        governance_batch=GOVERNANCE_BATCH,
        senses=CURRENT_SENSES,
        lexical_references=CURRENT_LEXICAL_REFERENCES,
        mappings=CURRENT_MAPPINGS,
        outward_eligibility_references=OUTWARD_ELIGIBILITY_REFERENCES,
        prohibited_expansion_refusals=PROHIBITED_EXPANSION_REFUSALS,
    )
)


def sense_term_mapping_registry() -> SenseTermMappingRegistry:
    return SENSE_TERM_MAPPING_REGISTRY


def registry_manifest() -> SenseTermMappingRegistryManifest:
    return SENSE_TERM_MAPPING_REGISTRY.manifest
