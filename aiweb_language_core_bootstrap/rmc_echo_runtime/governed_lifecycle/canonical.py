"""Canonical UTF-8 JSON and SHA-256 helpers for Slice 43B."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Iterable, Mapping

from ..schema import (
    AuthorizedMeaningReferenceRecord,
    DriftFindingBoundaryRecord,
    EchoContainmentBoundaryRecord,
    EchoDispositionBoundaryRecord,
    EchoReceiptBoundaryRecord,
    EchoRejectionBoundaryRecord,
    EchoTraceBoundaryRecord,
    EchoValidationInputBoundaryRecord,
    PreservationDimensionRequirementRecord,
    ProposedExpressionReferenceRecord,
    RmcEchoRuntimeSchemaRecord,
    ValidationFindingBoundaryRecord,
)
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    RmcEchoGovernanceBundle,
    RmcEchoLifecycleRecord,
    RmcEchoLifecycleTransitionRecord,
    RmcEchoVersionCustody,
)


class RmcEchoCanonicalizationError(ValueError):
    """Raised when a supported record cannot be represented canonically."""


SUPPORTED_RECORD_TYPES = (
    AuthorizedMeaningReferenceRecord,
    ProposedExpressionReferenceRecord,
    EchoValidationInputBoundaryRecord,
    PreservationDimensionRequirementRecord,
    ValidationFindingBoundaryRecord,
    DriftFindingBoundaryRecord,
    EchoDispositionBoundaryRecord,
    EchoRejectionBoundaryRecord,
    EchoContainmentBoundaryRecord,
    EchoTraceBoundaryRecord,
    EchoReceiptBoundaryRecord,
    RmcEchoRuntimeSchemaRecord,
    RmcEchoVersionCustody,
    RmcEchoLifecycleRecord,
    RmcEchoLifecycleTransitionRecord,
    RmcEchoGovernanceBundle,
)

CANONICAL_FIELD_ORDERS: Mapping[type[Any], tuple[str, ...]] = {
    record_type: tuple(item.name for item in fields(record_type))
    for record_type in SUPPORTED_RECORD_TYPES
}


def canonical_field_order(record_type: type[Any]) -> tuple[str, ...]:
    try:
        return CANONICAL_FIELD_ORDERS[record_type]
    except KeyError as error:
        raise RmcEchoCanonicalizationError(
            f"unsupported record type: {record_type!r}"
        ) from error


def canonicalize_field_pairs(
    record_type: type[Any],
    field_pairs: Iterable[tuple[str, Any]],
) -> dict[str, Any]:
    expected = canonical_field_order(record_type)
    expected_set = set(expected)
    observed: dict[str, Any] = {}
    observed_order: list[str] = []
    for pair in field_pairs:
        if (
            type(pair) is not tuple
            or len(pair) != 2
            or type(pair[0]) is not str
        ):
            raise RmcEchoCanonicalizationError(
                "field pairs must be exact (str, value) tuples"
            )
        name, value = pair
        if name in observed:
            raise RmcEchoCanonicalizationError(f"duplicate field: {name}")
        if name not in expected_set:
            raise RmcEchoCanonicalizationError(f"unknown field: {name}")
        observed[name] = value
        observed_order.append(name)
    missing = tuple(name for name in expected if name not in observed)
    if missing:
        raise RmcEchoCanonicalizationError(
            "missing fields: " + ", ".join(missing)
        )
    if tuple(observed_order) != expected:
        raise RmcEchoCanonicalizationError(
            "field order does not match the canonical dataclass order"
        )
    return {name: observed[name] for name in expected}


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        order = canonical_field_order(type(value))
        return {name: _normalize(getattr(value, name)) for name in order}
    if type(value) is tuple:
        return [_normalize(item) for item in value]
    if type(value) is list:
        return [_normalize(item) for item in value]
    if type(value) is dict:
        if not all(type(key) is str for key in value):
            raise RmcEchoCanonicalizationError(
                "canonical mappings require string keys"
            )
        return {key: _normalize(value[key]) for key in sorted(value)}
    if value is None or type(value) in (str, bool, int):
        return value
    raise RmcEchoCanonicalizationError(
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
        raise RmcEchoCanonicalizationError(
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
    if type(data) is not bytes:
        raise TypeError("deterministic_digest requires exact bytes")
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
    if (
        type(namespace) is not str
        or not namespace
        or namespace.strip() != namespace
    ):
        raise RmcEchoCanonicalizationError("invalid namespace")
    return (
        f"{namespace}:"
        f"{deterministic_record_digest(record, exclude_fields=exclude_fields)}"
    )


__all__ = (
    "CANONICAL_FIELD_ORDERS",
    "CANONICAL_FIELD_ORDER_VERSION",
    "SUPPORTED_RECORD_TYPES",
    "RmcEchoCanonicalizationError",
    "canonical_field_order",
    "canonical_json_bytes",
    "canonical_record_bytes",
    "canonical_record_mapping",
    "canonicalize_field_pairs",
    "deterministic_digest",
    "deterministic_record_digest",
    "stable_identifier",
)
