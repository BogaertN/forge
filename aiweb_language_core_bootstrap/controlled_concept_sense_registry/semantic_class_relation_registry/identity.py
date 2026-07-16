"""Deterministic Slice 37E record-identity helpers."""

from __future__ import annotations

from dataclasses import replace

from .schema import (
    ConceptClassMembershipRule,
    InverseRelationDeclaration,
    ProhibitedImplicationRule,
    RelationEligibilityRequest,
    RelationEligibilityResult,
    RelationFamilyDefinition,
    RelationStatePolicy,
    RelationTypeRule,
    RelationVersionIdentity,
    SemanticClassDefinition,
    SemanticClassRelationRegistryManifest,
)


def with_expected_class_definition_id(
    record: SemanticClassDefinition,
) -> SemanticClassDefinition:
    return replace(record, definition_id=record.expected_id())


def with_expected_membership_id(
    record: ConceptClassMembershipRule,
) -> ConceptClassMembershipRule:
    return replace(record, membership_id=record.expected_id())


def with_expected_family_definition_id(
    record: RelationFamilyDefinition,
) -> RelationFamilyDefinition:
    return replace(record, definition_id=record.expected_id())


def with_expected_relation_type_rule_id(
    record: RelationTypeRule,
) -> RelationTypeRule:
    return replace(record, rule_id=record.expected_id())


def with_expected_inverse_declaration_id(
    record: InverseRelationDeclaration,
) -> InverseRelationDeclaration:
    return replace(record, declaration_id=record.expected_id())


def with_expected_relation_version_id(
    record: RelationVersionIdentity,
) -> RelationVersionIdentity:
    return replace(record, relation_version_id=record.expected_id())


def with_expected_relation_state_policy_id(
    record: RelationStatePolicy,
) -> RelationStatePolicy:
    return replace(record, state_policy_id=record.expected_id())


def with_expected_prohibited_implication_id(
    record: ProhibitedImplicationRule,
) -> ProhibitedImplicationRule:
    return replace(record, implication_rule_id=record.expected_id())


def with_expected_eligibility_request_id(
    record: RelationEligibilityRequest,
) -> RelationEligibilityRequest:
    return replace(record, request_id=record.expected_id())


def with_expected_eligibility_result_id(
    record: RelationEligibilityResult,
) -> RelationEligibilityResult:
    return replace(record, result_id=record.expected_id())


def with_expected_manifest_id(
    record: SemanticClassRelationRegistryManifest,
) -> SemanticClassRelationRegistryManifest:
    return replace(record, manifest_id=record.expected_id())
