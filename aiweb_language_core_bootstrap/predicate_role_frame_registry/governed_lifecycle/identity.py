"""Deterministic Slice 38B record, lineage, and version helpers.

The helpers use exact caller-supplied fields.  They do not normalize language,
perform lexical lookup, compare semantic similarity, select a predicate,
admit a resource, or mutate any source record.
"""

from __future__ import annotations

from dataclasses import replace
import re
from typing import Final

from ...schema import stable_record_id
from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateNamespaceIdentity,
)
from .schema import (
    GovernedPredicateResource,
    PredicateGovernanceBatch,
    PredicateLifecycleAuthorityRecord,
    PredicateLifecycleTransitionRecord,
)


_STRICT_VERSION_RE: Final[re.Pattern[str]] = re.compile(
    r"^v(0|[1-9][0-9]*)(?:\.(0|[1-9][0-9]*))?(?:\.(0|[1-9][0-9]*))?$"
)


def resource_identity_field(record: GovernedPredicateResource) -> str:
    field_name = {
        PredicateNamespaceIdentity: "namespace_id",
        ActionRootIdentity: "action_root_id",
        PredicateIdentity: "predicate_id",
    }.get(type(record))

    if field_name is None:
        raise TypeError(
            "unsupported governed predicate resource type: "
            f"{type(record).__name__}"
        )

    return field_name


def resource_id(record: GovernedPredicateResource) -> str:
    return getattr(record, resource_identity_field(record))


def recompute_resource_id(record: GovernedPredicateResource) -> str:
    """Recompute the exact immutable version-record identifier."""

    return record.expected_id()


def with_recomputed_resource_id(
    record: GovernedPredicateResource,
) -> GovernedPredicateResource:
    """Return an immutable copy carrying its exact version-record identifier."""

    return replace(
        record,
        **{resource_identity_field(record): recompute_resource_id(record)},
    )


def resource_lineage_body(
    record: GovernedPredicateResource,
) -> dict[str, object]:
    """Return the exact material identity boundary preserved across versions."""

    if type(record) is PredicateNamespaceIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_key": record.namespace_key,
        }

    if type(record) is ActionRootIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_id": record.namespace_id,
            "action_root_key": record.action_root_key,
        }

    if type(record) is PredicateIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_id": record.namespace_id,
            "action_root_id": record.action_root_id,
            "predicate_key": record.predicate_key,
        }

    raise TypeError(
        "unsupported governed predicate resource type: "
        f"{type(record).__name__}"
    )


def expected_resource_lineage_id(
    record: GovernedPredicateResource,
) -> str:
    return stable_record_id(
        "predicate_registry_resource_lineage",
        resource_lineage_body(record),
    )


def parse_resource_version(version: str) -> tuple[int, int, int]:
    """Parse canonical vN, vN.N, or vN.N.N form without leading zeros."""

    if not isinstance(version, str):
        raise TypeError("version must be str")

    match = _STRICT_VERSION_RE.fullmatch(version)
    if match is None:
        raise ValueError(
            "version must use canonical vN, vN.N, or vN.N.N form "
            "without leading zeros"
        )

    values = tuple(
        int(item) if item is not None else 0
        for item in match.groups()
    )
    return values[0], values[1], values[2]


def version_advances(source_version: str, target_version: str) -> bool:
    return parse_resource_version(target_version) > parse_resource_version(
        source_version
    )


def version_compatible(source_version: str, target_version: str) -> bool:
    """Require strict advancement inside the same declared major version.

    Slice 38B does not silently accept a breaking major-version transition.  A
    later governed change may introduce a new lineage or a separately approved
    compatibility policy, but this slice fails closed.
    """

    source = parse_resource_version(source_version)
    target = parse_resource_version(target_version)
    return target > source and target[0] == source[0]


def with_expected_authority_id(
    record: PredicateLifecycleAuthorityRecord,
) -> PredicateLifecycleAuthorityRecord:
    return replace(record, authority_id=record.expected_id())


def with_expected_transition_id(
    record: PredicateLifecycleTransitionRecord,
) -> PredicateLifecycleTransitionRecord:
    return replace(record, transition_id=record.expected_id())


def with_expected_batch_id(
    batch: PredicateGovernanceBatch,
) -> PredicateGovernanceBatch:
    return replace(batch, batch_id=batch.expected_id())
