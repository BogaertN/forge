"""Closed read-only Slice 37C built-in concept registry.

Lookup is allowed only by exact stable concept ID or exact internal
(namespace_id, concept_key) pair.  No surface expression, normalization,
similarity, fallback, alias, lexical reference, or occurrence mapping is
performed.
"""

from __future__ import annotations

from typing import Final

from ..governed_lifecycle.identity import expected_resource_lineage_id
from ..schema import ConceptNamespaceIdentity, ControlledConceptIdentity
from .authority import (
    BUILT_IN_CONCEPT_KEYS,
    SLICE37C_ADDITIONAL_AUTHORITY_LIMITATIONS,
    SLICE37C_DECISION_OWNER_REF,
    SLICE37C_HUMAN_APPROVAL_REF,
)
from .identity import with_expected_manifest_id
from .records import (
    ADMITTED_CONCEPTS,
    CURRENT_NAMESPACE,
    GOVERNANCE_BATCH,
)
from .schema import (
    SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256,
    BuiltInConceptRegistry,
    BuiltInConceptRegistryManifest,
)


_MANIFEST: Final[BuiltInConceptRegistryManifest] = with_expected_manifest_id(
    BuiltInConceptRegistryManifest(
        manifest_id="",
        registry_key="aiweb:language-core:concept-registry:builtin:v1",
        namespace_ref=CURRENT_NAMESPACE.namespace_id,
        concept_refs=tuple(
            concept.concept_id
            for concept in ADMITTED_CONCEPTS
        ),
        concept_lineage_refs=tuple(
            expected_resource_lineage_id(concept)
            for concept in ADMITTED_CONCEPTS
        ),
        concept_keys=BUILT_IN_CONCEPT_KEYS,
        source_authority_packet_sha256=(
            SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256
        ),
        decision_owner_ref=SLICE37C_DECISION_OWNER_REF,
        human_approval_ref=SLICE37C_HUMAN_APPROVAL_REF,
        human_approved=True,
        registry_population_authorized=True,
        read_only=True,
        closed_set=True,
        authority_limitations=SLICE37C_ADDITIONAL_AUTHORITY_LIMITATIONS,
        exact_identity_lookup_allowed=True,
        exact_internal_key_lookup_allowed=True,
        surface_form_lookup_allowed=False,
        lexical_reference_population_installed=False,
        term_mapping_installed=False,
        occurrence_interpretation_installed=False,
        sense_population_installed=False,
        sense_selection_installed=False,
        semantic_class_population_installed=False,
        semantic_relation_population_installed=False,
        structural_integration_installed=False,
        candidate_meaning_creation_installed=False,
        runtime_activation_installed=False,
        route_registration_installed=False,
        tool_activation_installed=False,
        memory_access_installed=False,
        action_execution_installed=False,
        rendering_installed=False,
        delivery_installed=False,
        external_resource_loading_installed=False,
        llm_authority_installed=False,
        semantic_class_references_deferred_to_slice37e=True,
        sense_references_deferred_to_slice37d=True,
        relation_references_deferred_to_slice37e=True,
        historical_slice8_preserved=True,
        historical_slice8_superseded=False,
    )
)

BUILT_IN_REGISTRY: Final[BuiltInConceptRegistry] = BuiltInConceptRegistry(
    manifest=_MANIFEST,
    governance_batch=GOVERNANCE_BATCH,
    current_namespace=CURRENT_NAMESPACE,
    admitted_concepts=ADMITTED_CONCEPTS,
)


def built_in_registry() -> BuiltInConceptRegistry:
    """Return the immutable closed registry object."""

    return BUILT_IN_REGISTRY


def registry_manifest() -> BuiltInConceptRegistryManifest:
    return BUILT_IN_REGISTRY.manifest


def current_namespace() -> ConceptNamespaceIdentity:
    return BUILT_IN_REGISTRY.current_namespace


def all_admitted_concepts() -> tuple[ControlledConceptIdentity, ...]:
    """Return the exact deterministic concept tuple in canonical order."""

    return BUILT_IN_REGISTRY.admitted_concepts


def concept_by_id(concept_id: str) -> ControlledConceptIdentity:
    """Return one concept by exact stable ID or raise KeyError."""

    if not isinstance(concept_id, str):
        raise TypeError("concept_id must be str")

    for concept in BUILT_IN_REGISTRY.admitted_concepts:
        if concept.concept_id == concept_id:
            return concept

    raise KeyError(concept_id)


def concept_by_key(
    namespace_id: str,
    concept_key: str,
) -> ControlledConceptIdentity:
    """Return one concept by exact internal namespace ID and key."""

    if not isinstance(namespace_id, str):
        raise TypeError("namespace_id must be str")
    if not isinstance(concept_key, str):
        raise TypeError("concept_key must be str")

    for concept in BUILT_IN_REGISTRY.admitted_concepts:
        if (
            concept.namespace_id == namespace_id
            and concept.concept_key == concept_key
        ):
            return concept

    raise KeyError((namespace_id, concept_key))


def contains_concept_id(concept_id: str) -> bool:
    if not isinstance(concept_id, str):
        return False
    return any(
        concept.concept_id == concept_id
        for concept in BUILT_IN_REGISTRY.admitted_concepts
    )
