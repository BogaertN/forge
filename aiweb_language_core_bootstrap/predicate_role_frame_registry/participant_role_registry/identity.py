"""Deterministic identity and version helpers for Slice 38D."""

from __future__ import annotations

from dataclasses import asdict, replace
import re
from typing import Any

from ...schema import stable_record_id
from .schema import (
    ParticipantRoleConflictRecord,
    ParticipantRoleCorrectionRecord,
    ParticipantRoleDependencyRecord,
    ParticipantRoleGovernedResource,
    ParticipantRoleIdentity,
    ParticipantRoleLifecycleAuthorityRecord,
    ParticipantRoleLifecycleTransitionRecord,
    ParticipantRoleNamespaceIdentity,
    ParticipantRoleProvenanceReference,
    ParticipantRoleRegistryManifest,
    ParticipantRoleRelationshipRecord,
)

_VERSION = re.compile(r"^v([1-9][0-9]*)\.([0-9]+)\.([0-9]+)$")

_IDENTITY_FIELDS = {
    ParticipantRoleProvenanceReference: "provenance_id",
    ParticipantRoleNamespaceIdentity: "namespace_id",
    ParticipantRoleIdentity: "role_id",
    ParticipantRoleDependencyRecord: "dependency_id",
    ParticipantRoleRelationshipRecord: "relationship_id",
    ParticipantRoleCorrectionRecord: "correction_id",
    ParticipantRoleConflictRecord: "conflict_id",
    ParticipantRoleLifecycleAuthorityRecord: "authority_id",
    ParticipantRoleLifecycleTransitionRecord: "transition_id",
    ParticipantRoleRegistryManifest: "manifest_id",
}


def identity_field(record: object) -> str:
    field = _IDENTITY_FIELDS.get(type(record))
    if field is None:
        raise TypeError(f"unsupported Slice 38D record type: {type(record).__name__}")
    return field


def record_id(record: object) -> str:
    field = identity_field(record)
    value = getattr(record, field)
    if type(value) is not str:
        raise TypeError(f"{field} must be exact str")
    return value


def with_expected_id(record: Any) -> Any:
    field = identity_field(record)
    return replace(record, **{field: record.expected_id()})


def parse_version(version: object) -> tuple[int, int, int]:
    if type(version) is not str:
        raise TypeError("version must be exact str")
    match = _VERSION.fullmatch(version)
    if match is None:
        raise ValueError("version must match vMAJOR.MINOR.PATCH")
    return tuple(int(part) for part in match.groups())


def version_advances(source: object, target: object) -> bool:
    try:
        return parse_version(target) > parse_version(source)
    except (TypeError, ValueError):
        return False


def resource_lineage_body(record: ParticipantRoleGovernedResource) -> dict[str, object]:
    body = asdict(record)
    for field in (
        "namespace_id",
        "role_id",
        "dependency_id",
        "relationship_id",
        "version",
        "lifecycle_state",
    ):
        body.pop(field, None)
    return body


def expected_lineage_id(record: ParticipantRoleGovernedResource) -> str:
    return stable_record_id(
        f"slice38d_{record.resource_kind.value}_lineage",
        resource_lineage_body(record),
    )
