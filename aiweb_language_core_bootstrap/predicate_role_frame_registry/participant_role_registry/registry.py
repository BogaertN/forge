"""Closed read-only Slice 38D participant-role registry."""

from __future__ import annotations

from typing import Final

from ..built_in_action_root_registry.registry import registry_manifest as action_root_manifest
from .authority import (
    ADMITTED_PARTICIPANT_ROLE_KEYS,
    SLICE38D_AUTHORITY_LIMITATIONS,
    SLICE38D_DECISION_OWNER_REF,
    SLICE38D_DEFERRED_ROLE_CANDIDATES,
    SLICE38D_HUMAN_APPROVAL_REF,
)
from .identity import expected_lineage_id, with_expected_id
from .records import (
    ADMISSION_AUTHORITY,
    ADMITTED_ROLES,
    AUTHORITY_RECORDS,
    CONFLICTS,
    CORRECTIONS,
    CURRENT_NAMESPACE,
    DEPENDENCIES,
    DEPENDENCY_HISTORIES,
    PROVENANCE_RECORDS,
    RELATIONSHIPS,
    RELATIONSHIP_HISTORIES,
    ROLE_HISTORIES,
    TRANSITIONS,
)
from .schema import (
    SLICE38D_ACCEPTED_PARENT_HEAD,
    SLICE38D_ACCEPTED_PARENT_TREE,
    SLICE38D_SLICE38C_R2_EVIDENCE_SHA256,
    SLICE38D_SOURCE_AUTHORITY_PACKET_SHA256,
    ParticipantRoleDependencyRecord,
    ParticipantRoleIdentity,
    ParticipantRoleRegistry,
    ParticipantRoleRegistryManifest,
    ParticipantRoleRelationshipRecord,
)


_MANIFEST: Final[ParticipantRoleRegistryManifest] = with_expected_id(
    ParticipantRoleRegistryManifest(
        manifest_id="",
        registry_key="aiweb:language-core:predicate-role-frame:participant-role-registry:builtin:v1",
        namespace_ref=CURRENT_NAMESPACE.namespace_id,
        role_refs=tuple(role.role_id for role in ADMITTED_ROLES),
        role_lineage_refs=tuple(expected_lineage_id(role) for role in ADMITTED_ROLES),
        role_keys=ADMITTED_PARTICIPANT_ROLE_KEYS,
        dependency_refs=tuple(record.dependency_id for record in DEPENDENCIES),
        relationship_refs=tuple(record.relationship_id for record in RELATIONSHIPS),
        correction_refs=(),
        conflict_refs=(),
        transition_refs=tuple(record.transition_id for record in TRANSITIONS),
        authority_ref=ADMISSION_AUTHORITY.authority_id,
        action_root_registry_manifest_ref=action_root_manifest().manifest_id,
        source_authority_packet_sha256=SLICE38D_SOURCE_AUTHORITY_PACKET_SHA256,
        slice38c_r2_evidence_sha256=SLICE38D_SLICE38C_R2_EVIDENCE_SHA256,
        accepted_parent_head=SLICE38D_ACCEPTED_PARENT_HEAD,
        accepted_parent_tree=SLICE38D_ACCEPTED_PARENT_TREE,
        decision_owner_ref=SLICE38D_DECISION_OWNER_REF,
        human_approval_ref=SLICE38D_HUMAN_APPROVAL_REF,
        human_approved=True,
        registry_population_authorized=True,
        read_only=True,
        closed_set=True,
        exact_identity_lookup_allowed=True,
        exact_internal_key_lookup_allowed=True,
        surface_form_lookup_allowed=False,
        surface_normalization_allowed=False,
        occurrence_role_assignment_installed=False,
        concept_candidate_to_role_assignment_installed=False,
        semantic_relation_to_role_conversion_installed=False,
        source_span_to_actor_conversion_installed=False,
        grammatical_position_to_role_conversion_installed=False,
        nearest_known_role_substitution_installed=False,
        semantic_similarity_installed=False,
        predicate_frame_population_installed=False,
        frame_completion_installed=False,
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
        correction_schema_supported=True,
        conflict_schema_supported=True,
        dependency_schema_supported=True,
        relationship_schema_supported=True,
        lifecycle_history_preserved=True,
        predicate_frames_deferred_to_slice38e=True,
        effect_and_capability_references_deferred_to_slice38f=True,
        occurrence_candidate_proposal_deferred_to_slice38g=True,
        disabled_integration_deferred_to_slice38h=True,
        deferred_role_candidates=SLICE38D_DEFERRED_ROLE_CANDIDATES,
        authority_limitations=SLICE38D_AUTHORITY_LIMITATIONS,
    )
)

PARTICIPANT_ROLE_REGISTRY: Final[ParticipantRoleRegistry] = ParticipantRoleRegistry(
    manifest=_MANIFEST,
    current_namespace=CURRENT_NAMESPACE,
    admitted_roles=ADMITTED_ROLES,
    role_histories=ROLE_HISTORIES,
    dependencies=DEPENDENCIES,
    dependency_histories=DEPENDENCY_HISTORIES,
    relationships=RELATIONSHIPS,
    relationship_histories=RELATIONSHIP_HISTORIES,
    corrections=CORRECTIONS,
    conflicts=CONFLICTS,
    authority_records=AUTHORITY_RECORDS,
    transitions=TRANSITIONS,
    provenance_records=PROVENANCE_RECORDS,
)


def participant_role_registry() -> ParticipantRoleRegistry:
    return PARTICIPANT_ROLE_REGISTRY


def registry_manifest() -> ParticipantRoleRegistryManifest:
    return PARTICIPANT_ROLE_REGISTRY.manifest


def all_admitted_roles() -> tuple[ParticipantRoleIdentity, ...]:
    return PARTICIPANT_ROLE_REGISTRY.admitted_roles


def all_role_dependencies() -> tuple[ParticipantRoleDependencyRecord, ...]:
    return PARTICIPANT_ROLE_REGISTRY.dependencies


def all_role_relationships() -> tuple[ParticipantRoleRelationshipRecord, ...]:
    return PARTICIPANT_ROLE_REGISTRY.relationships


def role_by_id(role_id: str) -> ParticipantRoleIdentity:
    if type(role_id) is not str:
        raise TypeError("role_id must be exact str")
    for record in PARTICIPANT_ROLE_REGISTRY.admitted_roles:
        if record.role_id == role_id:
            return record
    raise KeyError(role_id)


def role_by_key(namespace_id: str, role_key: str) -> ParticipantRoleIdentity:
    if type(namespace_id) is not str:
        raise TypeError("namespace_id must be exact str")
    if type(role_key) is not str:
        raise TypeError("role_key must be exact str")
    for record in PARTICIPANT_ROLE_REGISTRY.admitted_roles:
        if record.namespace_id == namespace_id and record.role_key == role_key:
            return record
    raise KeyError((namespace_id, role_key))


def dependency_by_id(dependency_id: str) -> ParticipantRoleDependencyRecord:
    if type(dependency_id) is not str:
        raise TypeError("dependency_id must be exact str")
    for record in PARTICIPANT_ROLE_REGISTRY.dependencies:
        if record.dependency_id == dependency_id:
            return record
    raise KeyError(dependency_id)


def relationship_by_id(relationship_id: str) -> ParticipantRoleRelationshipRecord:
    if type(relationship_id) is not str:
        raise TypeError("relationship_id must be exact str")
    for record in PARTICIPANT_ROLE_REGISTRY.relationships:
        if record.relationship_id == relationship_id:
            return record
    raise KeyError(relationship_id)


def contains_role_id(role_id: object) -> bool:
    return type(role_id) is str and any(
        record.role_id == role_id for record in PARTICIPANT_ROLE_REGISTRY.admitted_roles
    )
