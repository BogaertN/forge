"""Canonical serialization for Slice 39F constructor-owned records."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _canonical(asdict(value))
    if type(value) is dict:
        return {str(key): _canonical(value[key]) for key in sorted(value)}
    if type(value) is tuple:
        return [_canonical(item) for item in value]
    if type(value) is list:
        return [_canonical(item) for item in value]
    if type(value) in (str, int, bool) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def deterministic_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def stable_identifier(prefix: str, value: Any) -> str:
    return f"{prefix}:sha256:{deterministic_digest(value)}"

__all__ = ("canonical_json_bytes", "deterministic_digest", "stable_identifier")
