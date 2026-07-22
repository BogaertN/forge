"""Deterministic canonical encoding for Slice 43G records."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping


class MsmEchoValidationCanonicalizationError(TypeError):
    pass


def canonical_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: canonical_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): canonical_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, tuple):
        return [canonical_value(item) for item in value]
    if isinstance(value, list):
        return [canonical_value(item) for item in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise MsmEchoValidationCanonicalizationError(
        f"unsupported canonical value: {type(value).__name__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def deterministic_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def stable_identifier(namespace: str, value: Any) -> str:
    if type(namespace) is not str or not namespace or namespace != namespace.strip():
        raise ValueError("namespace must be non-empty trimmed text")
    return f"{namespace}:{deterministic_digest(value)}"


__all__ = (
    "MsmEchoValidationCanonicalizationError",
    "canonical_json_bytes",
    "canonical_value",
    "deterministic_digest",
    "stable_identifier",
)
