"""Canonical serialization and deterministic identity support for Slice 47."""
from __future__ import annotations
from dataclasses import asdict, is_dataclass
from hashlib import sha256
import json
from typing import Any


def canonical_value(value: Any) -> Any:
    if is_dataclass(value):
        return canonical_value(asdict(value))
    if isinstance(value, dict):
        return {str(key): canonical_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (tuple, list)):
        return [canonical_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def stable_identifier(prefix: str, value: Any, *, excluded_fields: tuple[str, ...] = ()) -> str:
    body = canonical_value(value)
    if not isinstance(body, dict):
        raise TypeError("stable identifier body must be a mapping")
    for field in excluded_fields:
        body.pop(field, None)
    return f"{prefix}:{canonical_sha256(body)}"


__all__ = ("canonical_value", "canonical_bytes", "canonical_sha256", "stable_identifier")
