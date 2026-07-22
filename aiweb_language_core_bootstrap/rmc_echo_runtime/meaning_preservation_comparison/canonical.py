"""Canonical UTF-8 JSON and deterministic SHA-256 helpers for Slice 43D."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any

from .schema import (
    ComparisonIssue,
    ComparisonValidationReport,
    DimensionValueSnapshot,
    MeaningPreservationComparisonPackage,
    MeaningPreservationComparisonRequest,
    MeaningPreservationComparisonResult,
    MeaningPreservationFinding,
)


class ComparisonCanonicalizationError(ValueError):
    pass


SUPPORTED_RECORD_TYPES = (
    ComparisonIssue,
    ComparisonValidationReport,
    MeaningPreservationComparisonRequest,
    DimensionValueSnapshot,
    MeaningPreservationFinding,
    MeaningPreservationComparisonPackage,
    MeaningPreservationComparisonResult,
)


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _normalize(getattr(value, item.name))
            for item in fields(value)
        }
    if type(value) is tuple:
        return [_normalize(item) for item in value]
    if type(value) is list:
        return [_normalize(item) for item in value]
    if type(value) is dict:
        if not all(type(key) is str for key in value):
            raise ComparisonCanonicalizationError(
                "canonical mappings require exact string keys"
            )
        return {key: _normalize(value[key]) for key in sorted(value)}
    if value is None or type(value) in (str, bool, int):
        return value
    raise ComparisonCanonicalizationError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


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
    if type(record) not in SUPPORTED_RECORD_TYPES:
        raise ComparisonCanonicalizationError(
            f"unsupported top-level record type: {type(record)!r}"
        )
    field_names = tuple(item.name for item in fields(record))
    unknown = set(exclude_fields).difference(field_names)
    if unknown:
        raise ComparisonCanonicalizationError(
            "unknown excluded fields: " + ", ".join(sorted(unknown))
        )
    excluded = set(exclude_fields)
    value = {
        name: _normalize(getattr(record, name))
        for name in field_names
        if name not in excluded
    }
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=False,
    ).encode("utf-8")


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
        raise ComparisonCanonicalizationError("invalid namespace")
    return (
        f"{namespace}:"
        f"{deterministic_record_digest(record, exclude_fields=exclude_fields)}"
    )


__all__ = (
    "SUPPORTED_RECORD_TYPES",
    "ComparisonCanonicalizationError",
    "canonical_json_bytes",
    "canonical_record_bytes",
    "deterministic_digest",
    "deterministic_record_digest",
    "stable_identifier",
)
