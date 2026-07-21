"""Canonical serialization and deterministic digests for Slice 42F."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping


class SurfaceRealizationCanonicalizationError(ValueError):
    """Raised when a value cannot be canonically represented."""


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            item.name: _normalize(getattr(value, item.name))
            for item in fields(value)
        }
    if type(value) is tuple:
        return [_normalize(item) for item in value]
    if type(value) is list:
        return [_normalize(item) for item in value]
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise SurfaceRealizationCanonicalizationError(
                "canonical mapping keys must be exact strings"
            )
        return {key: _normalize(value[key]) for key in sorted(value)}
    if value is None or type(value) in (str, int, bool):
        return value
    raise SurfaceRealizationCanonicalizationError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def deterministic_digest(
    value: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> str:
    normalized = _normalize(value)
    if exclude_fields and isinstance(normalized, dict):
        normalized = {
            key: item
            for key, item in normalized.items()
            if key not in exclude_fields
        }
    return hashlib.sha256(canonical_json_bytes(normalized)).hexdigest()


def stable_identifier(
    namespace: str,
    value: Any,
    *,
    exclude_fields: tuple[str, ...] = (),
) -> str:
    if (
        type(namespace) is not str
        or not namespace
        or namespace.strip() != namespace
    ):
        raise SurfaceRealizationCanonicalizationError(
            "exact non-empty namespace required"
        )
    return f"{namespace}:{deterministic_digest(value, exclude_fields=exclude_fields)}"


__all__ = (
    "SurfaceRealizationCanonicalizationError",
    "canonical_json_bytes",
    "deterministic_digest",
    "stable_identifier",
)
