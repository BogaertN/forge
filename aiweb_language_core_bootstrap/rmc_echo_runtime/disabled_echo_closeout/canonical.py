"""Canonical deterministic helpers for Slice 43H records."""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable


def canonical_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {field.name: canonical_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(key): canonical_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (tuple, list)):
        return [canonical_value(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value), ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def deterministic_digest(value: Any) -> str:
    return sha256(canonical_json_bytes(value)).hexdigest()


def stable_identifier(namespace: str, value: Any) -> str:
    return f"{namespace}:{deterministic_digest(value)}"


def unique_strings(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
