"""Canonical serialization and SHA-256 helpers for Slice 41B."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Iterable, Mapping

from ..schema import (
    AlternativeCandidateCustodyRecord,
    GateCustodyReferenceRecord,
    InheritedLimitationCustodyRecord,
    SelectedMeaningDecisionStatusRecord,
    SelectedMeaningRuntimeSchemaRecord,
    SelectionAuthorityRequirementRecord,
    SelectionCandidateCustodyRecord,
    SelectionEligibilityStatusRecord,
    SelectionReceiptBoundaryRecord,
    SelectionTraceBoundaryRecord,
    UnresolvedStateCustodyRecord,
)
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    SelectedMeaningGovernanceBundle,
    SelectedMeaningLifecycleRecord,
    SelectedMeaningLifecycleTransitionRecord,
    SelectedMeaningVersionCustody,
)


class SelectedMeaningCanonicalizationError(ValueError):
    """Raised when a supported record cannot be represented canonically."""


SUPPORTED_RECORD_TYPES = (
    SelectionCandidateCustodyRecord,
    GateCustodyReferenceRecord,
    SelectionAuthorityRequirementRecord,
    AlternativeCandidateCustodyRecord,
    UnresolvedStateCustodyRecord,
    InheritedLimitationCustodyRecord,
    SelectionEligibilityStatusRecord,
    SelectedMeaningDecisionStatusRecord,
    SelectionTraceBoundaryRecord,
    SelectionReceiptBoundaryRecord,
    SelectedMeaningRuntimeSchemaRecord,
    SelectedMeaningVersionCustody,
    SelectedMeaningLifecycleRecord,
    SelectedMeaningLifecycleTransitionRecord,
    SelectedMeaningGovernanceBundle,
)

CANONICAL_FIELD_ORDERS: Mapping[type[Any], tuple[str, ...]] = {
    record_type: tuple(item.name for item in fields(record_type))
    for record_type in SUPPORTED_RECORD_TYPES
}


def canonical_field_order(record_type: type[Any]) -> tuple[str, ...]:
    try:
        return CANONICAL_FIELD_ORDERS[record_type]
    except KeyError as error:
        raise SelectedMeaningCanonicalizationError(
            f"unsupported record type: {record_type!r}"
        ) from error


def canonicalize_field_pairs(
    record_type: type[Any],
    field_pairs: Iterable[tuple[str, Any]],
) -> dict[str, Any]:
    expected = canonical_field_order(record_type)
    expected_set = set(expected)
    observed: dict[str, Any] = {}
    for pair in field_pairs:
        if (
            not isinstance(pair, tuple)
            or len(pair) != 2
            or not isinstance(pair[0], str)
        ):
            raise SelectedMeaningCanonicalizationError(
                "field pairs must be (str, value) tuples"
            )
        name, value = pair
        if name in observed:
            raise SelectedMeaningCanonicalizationError(
                f"duplicate field: {name}"
            )
        if name not in expected_set:
            raise SelectedMeaningCanonicalizationError(
                f"unknown field: {name}"
            )
        observed[name] = value
    missing = tuple(name for name in expected if name not in observed)
    if missing:
        raise SelectedMeaningCanonicalizationError(
            "missing fields: " + ", ".join(missing)
        )
    return {name: observed[name] for name in expected}


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        order = canonical_field_order(type(value))
        return {name: _normalize(getattr(value, name)) for name in order}
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise SelectedMeaningCanonicalizationError(
                "canonical mappings require string keys"
            )
        return {key: _normalize(value[key]) for key in sorted(value)}
    if value is None or type(value) in (str, bool, int):
        return value
    raise SelectedMeaningCanonicalizationError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


def canonical_record_mapping(
    record: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> dict[str, Any]:
    order = canonical_field_order(type(record))
    excluded = set(exclude_fields)
    unknown = excluded.difference(order)
    if unknown:
        raise SelectedMeaningCanonicalizationError(
            "unknown excluded fields: " + ", ".join(sorted(unknown))
        )
    return {
        name: _normalize(getattr(record, name))
        for name in order
        if name not in excluded
    }


def canonical_json_bytes(value: Any) -> bytes:
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")


def canonical_record_bytes(
    record: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> bytes:
    return canonical_json_bytes(
        canonical_record_mapping(record, exclude_fields=exclude_fields)
    )


def deterministic_digest(data: bytes) -> str:
    if not isinstance(data, bytes):
        raise TypeError("deterministic_digest requires bytes")
    return hashlib.sha256(data).hexdigest()


def deterministic_record_digest(
    record: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> str:
    return deterministic_digest(
        canonical_record_bytes(record, exclude_fields=exclude_fields)
    )


def stable_identifier(
    namespace: str,
    record: Any,
    *,
    exclude_fields: tuple[str, ...],
) -> str:
    if not isinstance(namespace, str) or not namespace or namespace.strip() != namespace:
        raise SelectedMeaningCanonicalizationError("invalid namespace")
    return f"{namespace}:{deterministic_record_digest(record, exclude_fields=exclude_fields)}"


__all__ = (
    "CANONICAL_FIELD_ORDERS",
    "CANONICAL_FIELD_ORDER_VERSION",
    "SUPPORTED_RECORD_TYPES",
    "SelectedMeaningCanonicalizationError",
    "canonical_field_order",
    "canonical_json_bytes",
    "canonical_record_bytes",
    "canonical_record_mapping",
    "canonicalize_field_pairs",
    "deterministic_digest",
    "deterministic_record_digest",
    "stable_identifier",
)
