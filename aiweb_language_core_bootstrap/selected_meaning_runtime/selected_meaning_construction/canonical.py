"""Canonical deterministic serialization for Slice 41D records."""
from __future__ import annotations

import hashlib
import json
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any

from .schema import (
    PreservedAlternativeCandidateRecord,
    SelectedMeaningConstructionAuthorityProfile,
    SelectedMeaningConstructionInput,
    SelectedMeaningConstructionPackage,
    SelectedMeaningConstructionValidationIssue,
    SelectedMeaningConstructionValidationReport,
    SelectedMeaningContentProof,
    SelectedMeaningDecisionRecord,
    SelectedMeaningSelectionReceiptRecord,
    SelectedMeaningSelectionTraceRecord,
)

CANONICAL_FIELD_ORDER_VERSION = "aiweb-slice41d-canonical-field-order-v1"
SUPPORTED_RECORD_TYPES = (
    SelectedMeaningConstructionAuthorityProfile,
    SelectedMeaningConstructionInput,
    SelectedMeaningDecisionRecord,
    PreservedAlternativeCandidateRecord,
    SelectedMeaningContentProof,
    SelectedMeaningSelectionTraceRecord,
    SelectedMeaningSelectionReceiptRecord,
    SelectedMeaningConstructionPackage,
    SelectedMeaningConstructionValidationIssue,
    SelectedMeaningConstructionValidationReport,
)
CANONICAL_FIELD_ORDERS = {
    record_type: tuple(field.name for field in fields(record_type))
    for record_type in SUPPORTED_RECORD_TYPES
}


class SelectedMeaningConstructionCanonicalizationError(ValueError):
    pass


def canonical_field_order(record_type: type[Any]) -> tuple[str, ...]:
    try:
        return CANONICAL_FIELD_ORDERS[record_type]
    except KeyError as error:
        raise SelectedMeaningConstructionCanonicalizationError(
            f"unsupported record type: {record_type!r}"
        ) from error


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        if type(value) in CANONICAL_FIELD_ORDERS:
            order = canonical_field_order(type(value))
        else:
            order = tuple(field.name for field in fields(type(value)))
        return {name: _normalize(getattr(value, name)) for name in order}
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise SelectedMeaningConstructionCanonicalizationError(
                "canonical mappings require string keys"
            )
        return {key: _normalize(value[key]) for key in sorted(value)}
    if value is None or type(value) in (str, bool, int):
        return value
    raise SelectedMeaningConstructionCanonicalizationError(
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
        raise SelectedMeaningConstructionCanonicalizationError(
            "unknown excluded fields: " + ", ".join(sorted(unknown))
        )
    return {
        name: _normalize(getattr(record, name))
        for name in order
        if name not in excluded
    }


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
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
        raise SelectedMeaningConstructionCanonicalizationError("invalid namespace")
    return f"{namespace}:{deterministic_record_digest(record, exclude_fields=exclude_fields)}"


__all__ = (
    "CANONICAL_FIELD_ORDERS",
    "CANONICAL_FIELD_ORDER_VERSION",
    "SUPPORTED_RECORD_TYPES",
    "SelectedMeaningConstructionCanonicalizationError",
    "canonical_field_order",
    "canonical_json_bytes",
    "canonical_record_bytes",
    "canonical_record_mapping",
    "deterministic_digest",
    "deterministic_record_digest",
    "stable_identifier",
)
