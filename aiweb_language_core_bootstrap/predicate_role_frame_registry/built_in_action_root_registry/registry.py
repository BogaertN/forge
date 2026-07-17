"""Closed read-only Slice 38C action-root registry.

Lookup is permitted only by exact stable identity or exact internal
(namespace_id, key) pairs.  No surface expression, alias, normalization,
semantic similarity, nearest-known fallback, occurrence mapping, predicate
selection, role assignment, frame completion, capability routing, or execution
is performed.
"""

from __future__ import annotations

from typing import Final

from ..governed_lifecycle.identity import expected_resource_lineage_id
from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateNamespaceIdentity,
)
from .authority import (
    BUILT_IN_ACTION_ROOT_KEYS,
    BUILT_IN_PREDICATE_KEYS,
    SLICE38C_ADDITIONAL_AUTHORITY_LIMITATIONS,
    SLICE38C_DECISION_OWNER_REF,
    SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES,
    SLICE38C_HUMAN_APPROVAL_REF,
)
from .identity import with_expected_manifest_id
from .records import (
    ADMITTED_ACTION_ROOTS,
    ADMITTED_PREDICATES,
    CURRENT_NAMESPACE,
    GOVERNANCE_BATCH,
)
from .schema import (
    SLICE38C_SOURCE_AUTHORITY_PACKET_SHA256,
    BuiltInActionRootRegistry,
    BuiltInActionRootRegistryManifest,
)


_MANIFEST: Final[BuiltInActionRootRegistryManifest] = with_expected_manifest_id(
    BuiltInActionRootRegistryManifest(
        manifest_id="",
        registry_key=(
            "aiweb:language-core:predicate-role-frame:action-root-registry:builtin:v1"
        ),
        namespace_ref=CURRENT_NAMESPACE.namespace_id,
        action_root_refs=tuple(
            record.action_root_id for record in ADMITTED_ACTION_ROOTS
        ),
        action_root_lineage_refs=tuple(
            expected_resource_lineage_id(record)
            for record in ADMITTED_ACTION_ROOTS
        ),
        action_root_keys=BUILT_IN_ACTION_ROOT_KEYS,
        predicate_refs=tuple(
            record.predicate_id for record in ADMITTED_PREDICATES
        ),
        predicate_lineage_refs=tuple(
            expected_resource_lineage_id(record)
            for record in ADMITTED_PREDICATES
        ),
        predicate_keys=BUILT_IN_PREDICATE_KEYS,
        source_authority_packet_sha256=(
            SLICE38C_SOURCE_AUTHORITY_PACKET_SHA256
        ),
        decision_owner_ref=SLICE38C_DECISION_OWNER_REF,
        human_approval_ref=SLICE38C_HUMAN_APPROVAL_REF,
        human_approved=True,
        registry_population_authorized=True,
        read_only=True,
        closed_set=True,
        authority_limitations=SLICE38C_ADDITIONAL_AUTHORITY_LIMITATIONS,
        deferred_higher_consequence_families=(
            SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES
        ),
        exact_identity_lookup_allowed=True,
        exact_internal_key_lookup_allowed=True,
        exact_action_root_to_predicate_link_allowed=True,
        surface_form_lookup_allowed=False,
        surface_normalization_allowed=False,
        occurrence_interpretation_installed=False,
        predicate_selection_installed=False,
        nearest_known_mapping_installed=False,
        semantic_similarity_installed=False,
        concept_to_predicate_conversion_installed=False,
        participant_role_population_installed=False,
        role_assignment_installed=False,
        predicate_frame_population_installed=False,
        frame_completion_installed=False,
        effect_boundary_population_installed=False,
        capability_reference_population_installed=False,
        capability_routing_installed=False,
        route_registration_installed=False,
        tool_activation_installed=False,
        action_execution_installed=False,
        evidence_validation_installed=False,
        memory_access_installed=False,
        rendering_installed=False,
        delivery_installed=False,
        external_resource_loading_installed=False,
        llm_authority_installed=False,
        participant_roles_deferred_to_slice38d=True,
        predicate_frames_deferred_to_slice38e=True,
        effect_and_capability_references_deferred_to_slice38f=True,
        occurrence_candidate_proposal_deferred_to_slice38g=True,
        disabled_integration_deferred_to_slice38h=True,
        slice38a_preserved=True,
        slice38b_preserved=True,
        slice38a_superseded=False,
        slice38b_superseded=False,
    )
)

BUILT_IN_ACTION_ROOT_REGISTRY: Final[BuiltInActionRootRegistry] = (
    BuiltInActionRootRegistry(
        manifest=_MANIFEST,
        governance_batch=GOVERNANCE_BATCH,
        current_namespace=CURRENT_NAMESPACE,
        admitted_action_roots=ADMITTED_ACTION_ROOTS,
        admitted_predicates=ADMITTED_PREDICATES,
    )
)


def built_in_action_root_registry() -> BuiltInActionRootRegistry:
    return BUILT_IN_ACTION_ROOT_REGISTRY


def registry_manifest() -> BuiltInActionRootRegistryManifest:
    return BUILT_IN_ACTION_ROOT_REGISTRY.manifest


def current_namespace() -> PredicateNamespaceIdentity:
    return BUILT_IN_ACTION_ROOT_REGISTRY.current_namespace


def all_admitted_action_roots() -> tuple[ActionRootIdentity, ...]:
    return BUILT_IN_ACTION_ROOT_REGISTRY.admitted_action_roots


def all_admitted_predicates() -> tuple[PredicateIdentity, ...]:
    return BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates


def action_root_by_id(action_root_id: str) -> ActionRootIdentity:
    if type(action_root_id) is not str:
        raise TypeError("action_root_id must be exact str")
    for record in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_action_roots:
        if record.action_root_id == action_root_id:
            return record
    raise KeyError(action_root_id)


def action_root_by_key(
    namespace_id: str,
    action_root_key: str,
) -> ActionRootIdentity:
    if type(namespace_id) is not str:
        raise TypeError("namespace_id must be exact str")
    if type(action_root_key) is not str:
        raise TypeError("action_root_key must be exact str")
    for record in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_action_roots:
        if (
            record.namespace_id == namespace_id
            and record.action_root_key == action_root_key
        ):
            return record
    raise KeyError((namespace_id, action_root_key))


def predicate_by_id(predicate_id: str) -> PredicateIdentity:
    if type(predicate_id) is not str:
        raise TypeError("predicate_id must be exact str")
    for record in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates:
        if record.predicate_id == predicate_id:
            return record
    raise KeyError(predicate_id)


def predicate_by_key(
    namespace_id: str,
    predicate_key: str,
) -> PredicateIdentity:
    if type(namespace_id) is not str:
        raise TypeError("namespace_id must be exact str")
    if type(predicate_key) is not str:
        raise TypeError("predicate_key must be exact str")
    for record in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates:
        if (
            record.namespace_id == namespace_id
            and record.predicate_key == predicate_key
        ):
            return record
    raise KeyError((namespace_id, predicate_key))


def predicate_for_action_root_id(action_root_id: str) -> PredicateIdentity:
    if type(action_root_id) is not str:
        raise TypeError("action_root_id must be exact str")
    matches = tuple(
        record
        for record in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates
        if record.action_root_id == action_root_id
    )
    if len(matches) != 1:
        raise KeyError(action_root_id)
    return matches[0]


def contains_action_root_id(action_root_id: object) -> bool:
    return type(action_root_id) is str and any(
        record.action_root_id == action_root_id
        for record in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_action_roots
    )


def contains_predicate_id(predicate_id: object) -> bool:
    return type(predicate_id) is str and any(
        record.predicate_id == predicate_id
        for record in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates
    )
