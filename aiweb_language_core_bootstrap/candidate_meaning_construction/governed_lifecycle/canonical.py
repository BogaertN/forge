"""Canonical field ordering and deterministic digest helpers for Slice 39B."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Iterable, Mapping

from ..schema import (
    CandidateMeaningAlternativeReference,
    CandidateMeaningConstructionReceipt,
    CandidateMeaningContent,
    CandidateMeaningIdentity,
    CandidateMeaningProvenance,
    CandidateMeaningState,
)
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    CandidateMeaningGovernanceBundle,
    CandidateMeaningLifecycleRecord,
    CandidateMeaningLifecycleTransitionRecord,
    CandidateMeaningVersionCustody,
)


class CandidateMeaningCanonicalizationError(ValueError):
    """Raised when a record cannot be canonically represented."""


SUPPORTED_RECORD_TYPES = (
    CandidateMeaningIdentity,
    CandidateMeaningContent,
    CandidateMeaningProvenance,
    CandidateMeaningAlternativeReference,
    CandidateMeaningConstructionReceipt,
    CandidateMeaningState,
    CandidateMeaningVersionCustody,
    CandidateMeaningLifecycleRecord,
    CandidateMeaningLifecycleTransitionRecord,
    CandidateMeaningGovernanceBundle,
)

CANONICAL_FIELD_ORDERS: Mapping[type[Any], tuple[str, ...]] = {
    record_type: tuple(item.name for item in fields(record_type))
    for record_type in SUPPORTED_RECORD_TYPES
}


def canonical_field_order(record_type: type[Any]) -> tuple[str, ...]:
    """Return the exact versioned field order for a supported record type."""

    try:
        return CANONICAL_FIELD_ORDERS[record_type]
    except KeyError as error:
        raise CandidateMeaningCanonicalizationError(
            f"unsupported record type: {record_type!r}"
        ) from error


def canonicalize_field_pairs(
    record_type: type[Any],
    field_pairs: Iterable[tuple[str, Any]],
) -> dict[str, Any]:
    """Reject duplicate, unknown, and missing fields, then order canonically."""

    expected = canonical_field_order(record_type)
    expected_set = set(expected)
    observed: dict[str, Any] = {}

    for pair in field_pairs:
        if (
            not isinstance(pair, tuple)
            or len(pair) != 2
            or not isinstance(pair[0], str)
        ):
            raise CandidateMeaningCanonicalizationError(
                "field pairs must be (str, value) tuples"
            )
        name, value = pair
        if name in observed:
            raise CandidateMeaningCanonicalizationError(
                f"duplicate field: {name}"
            )
        if name not in expected_set:
            raise CandidateMeaningCanonicalizationError(
                f"unknown field: {name}"
            )
        observed[name] = value

    missing = tuple(name for name in expected if name not in observed)
    if missing:
        raise CandidateMeaningCanonicalizationError(
            "missing fields: " + ", ".join(missing)
        )

    return {name: observed[name] for name in expected}


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        order = canonical_field_order(type(value))
        return {
            name: _normalize(getattr(value, name))
            for name in order
        }
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise CandidateMeaningCanonicalizationError(
                "canonical mappings require string keys"
            )
        return {
            key: _normalize(value[key])
            for key in sorted(value)
        }
    if value is None or type(value) in (str, bool, int):
        return value
    raise CandidateMeaningCanonicalizationError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


def canonical_record_mapping(
    record: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Return an ordered canonical mapping for a supported frozen record."""

    record_type = type(record)
    order = canonical_field_order(record_type)
    excluded = set(exclude_fields)
    unknown_exclusions = excluded.difference(order)
    if unknown_exclusions:
        raise CandidateMeaningCanonicalizationError(
            "unknown excluded fields: " + ", ".join(sorted(unknown_exclusions))
        )
    return {
        name: _normalize(getattr(record, name))
        for name in order
        if name not in excluded
    }


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a supported value with stable separators and UTF-8 bytes."""

    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_record_bytes(
    record: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> bytes:
    return canonical_json_bytes(
        canonical_record_mapping(record, exclude_fields=exclude_fields)
    )


def deterministic_digest(value: Any) -> str:
    """Return the lower-case SHA-256 digest of the canonical value."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def deterministic_record_digest(
    record: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> str:
    return hashlib.sha256(
        canonical_record_bytes(record, exclude_fields=exclude_fields)
    ).hexdigest()


def stable_identifier(prefix: str, value: Any) -> str:
    if not isinstance(prefix, str) or not prefix:
        raise CandidateMeaningCanonicalizationError(
            "identifier prefix must be non-empty text"
        )
    return f"{prefix}:sha256:{deterministic_digest(value)}"


__all__ = (
    "CANONICAL_FIELD_ORDER_VERSION",
    "CANONICAL_FIELD_ORDERS",
    "CandidateMeaningCanonicalizationError",
    "SUPPORTED_RECORD_TYPES",
    "canonical_field_order",
    "canonical_json_bytes",
    "canonical_record_bytes",
    "canonical_record_mapping",
    "canonicalize_field_pairs",
    "deterministic_digest",
    "deterministic_record_digest",
    "stable_identifier",
)
