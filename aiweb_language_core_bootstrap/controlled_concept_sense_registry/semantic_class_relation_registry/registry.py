"""Closed read-only Slice 37E semantic-class and relation-type registry."""

from __future__ import annotations

from typing import Final

from ..sense_term_mapping_registry.registry import SENSE_TERM_MAPPING_REGISTRY
from .authority import (
    SLICE37E_DECISION_OWNER_REF,
    SLICE37E_HUMAN_APPROVAL_REF,
    SLICE37E_REGISTRY_AUTHORITY_LIMITATIONS,
)
from .identity import with_expected_manifest_id
from .records import (
    CLASS_DEFINITIONS,
    CURRENT_RELATION_FAMILIES,
    CURRENT_RELATION_TYPES,
    CURRENT_SEMANTIC_CLASSES,
    GOVERNANCE_BATCH,
    INVERSE_DECLARATIONS,
    MEMBERSHIPS,
    PROHIBITED_IMPLICATIONS,
    RELATION_FAMILY_DEFINITION_RECORDS,
    RELATION_STATE_POLICIES,
    RELATION_TYPE_RULES,
    RELATION_VERSIONS,
)
from .schema import (
    SLICE37E_SOURCE_AUTHORITY_PACKET_SHA256,
    SemanticClassRelationRegistry,
    SemanticClassRelationRegistryManifest,
)


_MANIFEST: Final[SemanticClassRelationRegistryManifest] = with_expected_manifest_id(
    SemanticClassRelationRegistryManifest(
        manifest_id="",
        registry_key=(
            "aiweb:language-core:concept-registry:"
            "semantic-class-relation-type:builtin:v1"
        ),
        source_authority_packet_sha256=SLICE37E_SOURCE_AUTHORITY_PACKET_SHA256,
        decision_owner_ref=SLICE37E_DECISION_OWNER_REF,
        human_approval_ref=SLICE37E_HUMAN_APPROVAL_REF,
        human_approved=True,
        read_only=True,
        closed_set=True,
        authority_limitations=SLICE37E_REGISTRY_AUTHORITY_LIMITATIONS,
        semantic_class_refs=tuple(
            item.semantic_class_id for item in CURRENT_SEMANTIC_CLASSES
        ),
        class_definition_refs=tuple(
            item.definition_id for item in CLASS_DEFINITIONS
        ),
        membership_refs=tuple(item.membership_id for item in MEMBERSHIPS),
        relation_family_refs=tuple(
            item.relation_family_id for item in CURRENT_RELATION_FAMILIES
        ),
        relation_family_definition_refs=tuple(
            item.definition_id for item in RELATION_FAMILY_DEFINITION_RECORDS
        ),
        relation_type_refs=tuple(
            item.relation_type_id for item in CURRENT_RELATION_TYPES
        ),
        relation_type_rule_refs=tuple(
            item.rule_id for item in RELATION_TYPE_RULES
        ),
        inverse_declaration_refs=tuple(
            item.declaration_id for item in INVERSE_DECLARATIONS
        ),
        relation_version_refs=tuple(
            item.relation_version_id for item in RELATION_VERSIONS
        ),
        relation_state_policy_refs=tuple(
            item.state_policy_id for item in RELATION_STATE_POLICIES
        ),
        prohibited_implication_refs=tuple(
            item.implication_rule_id for item in PROHIBITED_IMPLICATIONS
        ),
        exact_class_id_lookup_allowed=True,
        exact_relation_family_id_lookup_allowed=True,
        exact_relation_type_id_lookup_allowed=True,
        exact_membership_lookup_allowed=True,
        type_eligibility_evaluation_allowed=True,
        registry_population_authorized=True,
        semantic_class_population_authorized=True,
        class_membership_population_authorized=True,
        relation_family_population_authorized=True,
        relation_type_population_authorized=True,
        inverse_declaration_population_authorized=True,
        relation_instance_population_installed=False,
        relation_fact_assertion_installed=False,
        source_occurrence_interpretation_installed=False,
        sense_selection_installed=False,
        candidate_meaning_creation_installed=False,
        structural_integration_installed=False,
        truth_evaluation_installed=False,
        evidence_validation_installed=False,
        verified_status_application_installed=False,
        permission_authority_installed=False,
        action_authority_installed=False,
        memory_authority_installed=False,
        identity_authority_installed=False,
        economic_authority_installed=False,
        runtime_activation_installed=False,
        route_registration_installed=False,
        tool_activation_installed=False,
        rendering_installed=False,
        delivery_installed=False,
        external_resource_loading_installed=False,
        llm_authority_installed=False,
        embedding_installed=False,
        semantic_similarity_installed=False,
        structural_candidate_integration_deferred_to_slice37f=True,
    )
)

SEMANTIC_CLASS_RELATION_REGISTRY: Final[SemanticClassRelationRegistry] = (
    SemanticClassRelationRegistry(
        manifest=_MANIFEST,
        predecessor_registry=SENSE_TERM_MAPPING_REGISTRY,
        governance_batch=GOVERNANCE_BATCH,
        semantic_classes=CURRENT_SEMANTIC_CLASSES,
        class_definitions=CLASS_DEFINITIONS,
        memberships=MEMBERSHIPS,
        relation_families=CURRENT_RELATION_FAMILIES,
        relation_family_definitions=RELATION_FAMILY_DEFINITION_RECORDS,
        relation_types=CURRENT_RELATION_TYPES,
        relation_type_rules=RELATION_TYPE_RULES,
        inverse_declarations=INVERSE_DECLARATIONS,
        relation_versions=RELATION_VERSIONS,
        relation_state_policies=RELATION_STATE_POLICIES,
        prohibited_implications=PROHIBITED_IMPLICATIONS,
    )
)


def semantic_class_relation_registry() -> SemanticClassRelationRegistry:
    return SEMANTIC_CLASS_RELATION_REGISTRY


def registry_manifest() -> SemanticClassRelationRegistryManifest:
    return SEMANTIC_CLASS_RELATION_REGISTRY.manifest
