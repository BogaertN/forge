"""Deterministic identity helpers for Slice 38A schema records.

The helper assigns only the canonical identifier implied by an immutable
record body. It performs no action-root lookup, predicate selection, role
assignment, frame completion, capability routing, or execution.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TypeVar

from .schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
)


_RecordT = TypeVar(
    "_RecordT",
    PredicateProvenanceReference,
    PredicateNamespaceIdentity,
    ActionRootIdentity,
    PredicateIdentity,
)


def with_expected_predicate_resource_id(record: _RecordT) -> _RecordT:
    field_name = {
        PredicateProvenanceReference: "provenance_id",
        PredicateNamespaceIdentity: "namespace_id",
        ActionRootIdentity: "action_root_id",
        PredicateIdentity: "predicate_id",
    }.get(type(record))

    if field_name is None:
        raise TypeError(f"unsupported Slice 38A record type: {type(record).__name__}")

    return replace(record, **{field_name: record.expected_id()})
