"""Canonical serialization and deterministic identity for Slice 41F records."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Iterable


def canonical_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return canonical_value(asdict(value))
    if isinstance(value, dict):
        return {
            str(key): canonical_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [canonical_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def deterministic_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def stable_identifier(
    namespace: str,
    value: Any,
    *,
    excluded_fields: Iterable[str] = (),
) -> str:
    if type(namespace) is not str or not namespace:
        raise ValueError("non-empty namespace required")
    body = canonical_value(value)
    if not isinstance(body, dict):
        raise TypeError("record-like mapping required")
    for field in excluded_fields:
        body.pop(field, None)
    return f"{namespace}:{deterministic_digest(body)}"


__all__ = (
    "canonical_json_bytes",
    "canonical_value",
    "deterministic_digest",
    "stable_identifier",
)
