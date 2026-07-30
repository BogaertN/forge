"""Fail-closed validation for the packaged semantic-charter proposal."""

from __future__ import annotations

import hashlib

from ..meaning_compiler_preview.registry import forge_seed_registry
from .charter import build_proposed_semantic_charter
from .schema import (
    CharterStatus,
    GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION,
    ProposedConceptSense,
    ProposedConstructionContract,
    ProposedPredicate,
    ProposedRole,
    ProposedSemanticCharter,
    SemanticCharterBoundary,
    SemanticCharterValidationError,
    SemanticReplayFixture,
)


_EXPECTED_COUNTS = {
    "concept_senses": 7,
    "predicates": 6,
    "roles": 6,
    "constructions": 9,
    "replay_fixtures": 8,
}


def _duplicates(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return tuple(sorted(duplicates))


def _identity_issue(value: object, field: str, id_field: str) -> str | None:
    try:
        actual = getattr(value, id_field)
        expected = value.expected_id()
    except (AttributeError, TypeError, ValueError):
        return f"{field}:identity_not_computable"
    if actual != expected:
        return f"{field}:content_identity_mismatch"
    return None


def validate_semantic_charter(value: object) -> tuple[str, ...]:
    """Return exact validation issues; an empty tuple means the proposal is sound."""

    if type(value) is not ProposedSemanticCharter:
        return ("charter:must_be_exact_proposed_semantic_charter",)

    issues: list[str] = []
    if value.schema_version != GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION:
        issues.append("charter:schema_version_unsupported")
    if value.status is not CharterStatus.PROPOSED_FOR_OPERATOR_APPROVAL:
        issues.append("charter:status_not_proposed_for_operator_approval")
    identity_issue = _identity_issue(value, "charter", "charter_id")
    if identity_issue:
        issues.append(identity_issue)

    required_true = (
        "deterministic",
        "forge_owned",
        "proposed",
        "operator_approval_required",
    )
    required_false = (
        "operator_approval_present",
        "active",
        "canonical_authority",
        "runtime_authority",
        "memory_write_authority",
    )
    for field in required_true:
        if getattr(value, field) is not True:
            issues.append(f"charter:{field}_must_remain_true")
    for field in required_false:
        if getattr(value, field) is not False:
            issues.append(f"charter:{field}_must_remain_false")

    groups = (
        ("concept_senses", value.concept_senses, ProposedConceptSense, "proposal_id"),
        ("predicates", value.predicates, ProposedPredicate, "proposal_id"),
        ("roles", value.roles, ProposedRole, "proposal_id"),
        (
            "constructions",
            value.constructions,
            ProposedConstructionContract,
            "construction_id",
        ),
        (
            "replay_fixtures",
            value.replay_fixtures,
            SemanticReplayFixture,
            "fixture_id",
        ),
    )
    for name, records, expected_type, id_field in groups:
        if type(records) is not tuple:
            issues.append(f"{name}:must_be_tuple")
            continue
        if len(records) != _EXPECTED_COUNTS[name]:
            issues.append(f"{name}:unexpected_count")
        if any(type(record) is not expected_type for record in records):
            issues.append(f"{name}:contains_wrong_record_type")
            continue
        identifiers = tuple(str(getattr(record, id_field)) for record in records)
        if _duplicates(identifiers):
            issues.append(f"{name}:duplicate_record_identity")
        for index, record in enumerate(records):
            record_issue = _identity_issue(record, f"{name}[{index}]", id_field)
            if record_issue:
                issues.append(record_issue)
            if record.schema_version != GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION:
                issues.append(f"{name}[{index}]:schema_version_unsupported")

    concept_records = (
        value.concept_senses
        if type(value.concept_senses) is tuple
        and all(type(item) is ProposedConceptSense for item in value.concept_senses)
        else ()
    )
    predicate_records = (
        value.predicates
        if type(value.predicates) is tuple
        and all(type(item) is ProposedPredicate for item in value.predicates)
        else ()
    )
    role_records = (
        value.roles
        if type(value.roles) is tuple
        and all(type(item) is ProposedRole for item in value.roles)
        else ()
    )
    construction_records = (
        value.constructions
        if type(value.constructions) is tuple
        and all(
            type(item) is ProposedConstructionContract
            for item in value.constructions
        )
        else ()
    )
    fixture_records = (
        value.replay_fixtures
        if type(value.replay_fixtures) is tuple
        and all(type(item) is SemanticReplayFixture for item in value.replay_fixtures)
        else ()
    )

    registry = forge_seed_registry()
    if value.registry_ref != registry.registry_id:
        issues.append("charter:registry_ref_does_not_match_installed_registry")
    if value.registry_version != registry.version:
        issues.append("charter:registry_version_does_not_match_installed_registry")

    concept_by_key = {item.concept_key: item for item in registry.concepts}
    sense_by_key = {item.sense_key: item for item in registry.senses}
    predicate_by_key = {item.predicate_key: item for item in registry.predicates}
    role_by_key = {item.role_key: item for item in registry.roles}

    if concept_records:
        concept_keys = tuple(item.concept_key for item in concept_records)
        if _duplicates(concept_keys):
            issues.append("concept_senses:duplicate_concept_key")
        for item in concept_records:
            concept = concept_by_key.get(item.concept_key)
            sense = sense_by_key.get(item.sense_key)
            if concept is None or concept.concept_id != item.concept_ref:
                issues.append(f"concept_senses:{item.concept_key}:concept_binding_drift")
            if (
                sense is None
                or sense.sense_id != item.sense_ref
                or sense.concept_ref != item.concept_ref
            ):
                issues.append(f"concept_senses:{item.concept_key}:sense_binding_drift")
            if (
                item.forge_registry_owned is not True
                or item.source_record_provisional is not True
                or item.operator_approval_required is not True
            ):
                issues.append(f"concept_senses:{item.concept_key}:authority_boundary_drift")

    if predicate_records:
        predicate_keys = tuple(item.predicate_key for item in predicate_records)
        if _duplicates(predicate_keys):
            issues.append("predicates:duplicate_predicate_key")
        for item in predicate_records:
            predicate = predicate_by_key.get(item.predicate_key)
            if (
                predicate is None
                or predicate.predicate_id != item.predicate_ref
                or predicate.required_roles != item.declared_required_role_keys
            ):
                issues.append(f"predicates:{item.predicate_key}:registry_binding_drift")
            if (
                item.forge_registry_owned is not True
                or item.source_record_provisional is not True
                or item.operator_approval_required is not True
            ):
                issues.append(f"predicates:{item.predicate_key}:authority_boundary_drift")

    if role_records:
        role_keys = tuple(item.role_key for item in role_records)
        if _duplicates(role_keys):
            issues.append("roles:duplicate_role_key")
        for item in role_records:
            role = role_by_key.get(item.role_key)
            if role is None or role.role_id != item.role_ref:
                issues.append(f"roles:{item.role_key}:registry_binding_drift")
            if (
                item.forge_registry_owned is not True
                or item.source_record_provisional is not True
                or item.operator_approval_required is not True
            ):
                issues.append(f"roles:{item.role_key}:authority_boundary_drift")

    proposed_predicates = {
        item.predicate_key: item
        for item in predicate_records
    }
    proposed_roles = {
        item.role_key: item for item in role_records
    }
    constructions_by_id = {
        item.construction_id: item
        for item in construction_records
    }
    if construction_records and len(constructions_by_id) == len(construction_records):
        construction_keys = tuple(
            item.construction_key for item in construction_records
        )
        grammar_ids = tuple(item.grammar_rule_id for item in construction_records)
        if _duplicates(construction_keys):
            issues.append("constructions:duplicate_construction_key")
        if _duplicates(grammar_ids):
            issues.append("constructions:duplicate_grammar_rule_id")
        for item in construction_records:
            predicate = proposed_predicates.get(item.predicate_key)
            if predicate is None or predicate.predicate_ref != item.predicate_ref:
                issues.append(
                    f"constructions:{item.construction_key}:predicate_not_proposed"
                )
            if not item.effective_role_keys or any(
                role_key not in proposed_roles
                for role_key in item.effective_role_keys
            ):
                issues.append(
                    f"constructions:{item.construction_key}:effective_roles_not_proposed"
                )
            if len(item.effective_role_keys) != len(set(item.effective_role_keys)):
                issues.append(
                    f"constructions:{item.construction_key}:duplicate_effective_role"
                )
            if (
                item.exact_fixture_only is not True
                or item.operator_approval_required is not True
                or item.runtime_active is not False
            ):
                issues.append(
                    f"constructions:{item.construction_key}:authority_boundary_drift"
                )

    concept_refs = {
        item.concept_ref
        for item in concept_records
    }
    sense_refs = {
        item.sense_ref
        for item in concept_records
    }
    if fixture_records:
        fixture_keys = tuple(item.fixture_key for item in fixture_records)
        source_texts = tuple(item.exact_source_text for item in fixture_records)
        if _duplicates(fixture_keys):
            issues.append("replay_fixtures:duplicate_fixture_key")
        if _duplicates(source_texts):
            issues.append("replay_fixtures:duplicate_exact_source")
        for item in fixture_records:
            construction = constructions_by_id.get(item.construction_ref)
            source_hash = hashlib.sha256(
                item.exact_source_text.encode("utf-8")
            ).hexdigest()
            if source_hash != item.exact_source_sha256:
                issues.append(f"replay_fixtures:{item.fixture_key}:source_hash_mismatch")
            if construction is None:
                issues.append(
                    f"replay_fixtures:{item.fixture_key}:unknown_construction_ref"
                )
            else:
                if item.expected_predicate_ref != construction.predicate_ref:
                    issues.append(
                        f"replay_fixtures:{item.fixture_key}:predicate_ref_mismatch"
                    )
                if item.expected_role_keys != construction.effective_role_keys:
                    issues.append(
                        f"replay_fixtures:{item.fixture_key}:effective_role_shape_mismatch"
                    )
                if item.expected_negated is not construction.negated:
                    issues.append(
                        f"replay_fixtures:{item.fixture_key}:negation_contract_mismatch"
                    )
            if not item.expected_concept_refs or not set(
                item.expected_concept_refs
            ).issubset(concept_refs):
                issues.append(
                    f"replay_fixtures:{item.fixture_key}:concept_refs_not_proposed"
                )
            if not item.expected_sense_refs or not set(
                item.expected_sense_refs
            ).issubset(sense_refs):
                issues.append(
                    f"replay_fixtures:{item.fixture_key}:sense_refs_not_proposed"
                )
            if (
                item.expected_compiler_status != "PREVIEW_READY"
                or item.expected_echo_status != "PASS"
                or item.operator_approval_required is not True
                or item.runtime_authority is not False
            ):
                issues.append(
                    f"replay_fixtures:{item.fixture_key}:authority_or_status_contract_drift"
                )

    if type(value.boundary) is not SemanticCharterBoundary:
        issues.append("boundary:must_be_exact_semantic_charter_boundary")
    else:
        boundary_issue = _identity_issue(value.boundary, "boundary", "boundary_id")
        if boundary_issue:
            issues.append(boundary_issue)
        boundary_true = ("forge_owned", "proposal_only", "operator_approval_required")
        boundary_false = tuple(
            field
            for field in value.boundary.__dataclass_fields__
            if field
            not in {
                "boundary_id",
                "schema_version",
                *boundary_true,
            }
        )
        for field in boundary_true:
            if getattr(value.boundary, field) is not True:
                issues.append(f"boundary:{field}_must_remain_true")
        for field in boundary_false:
            if getattr(value.boundary, field) is not False:
                issues.append(f"boundary:{field}_must_remain_false")

    # This v0 validator admits exactly the reviewed packaged proposal.  A
    # caller cannot recompute content IDs around broader vocabulary or altered
    # grammar and have it silently become this charter.
    try:
        expected = build_proposed_semantic_charter()
        if value != expected:
            issues.append("charter:does_not_match_packaged_proposal")
    except (TypeError, ValueError):
        issues.append("charter:packaged_proposal_rebuild_failed")

    return tuple(sorted(set(issues)))


def assert_valid_semantic_charter(value: object) -> ProposedSemanticCharter:
    issues = validate_semantic_charter(value)
    if issues:
        raise SemanticCharterValidationError(issues)
    assert type(value) is ProposedSemanticCharter
    return value


__all__ = ("assert_valid_semantic_charter", "validate_semantic_charter")
