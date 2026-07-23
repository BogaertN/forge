"""Deterministic canonical helpers for Slice 45 records."""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping


def canonical_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return canonical_value(value.value)
    if is_dataclass(value):
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
    if isinstance(value, (set, frozenset)):
        rows = [canonical_value(item) for item in value]
        return sorted(rows, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"unsupported canonical type: {{type(value).__name__}}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def deterministic_digest(value: Any) -> str:
    return sha256(canonical_json_bytes(value)).hexdigest()


def stable_identifier(namespace: str, value: Any, *, excluded_fields: Iterable[str] = ()) -> str:
    if not isinstance(namespace, str) or not namespace.strip():
        raise ValueError("namespace must be non-empty text")
    body = canonical_value(value)
    if not isinstance(body, dict):
        raise TypeError("stable identifiers require an object body")
    for field in excluded_fields:
        body.pop(field, None)
    return f"{namespace}:{deterministic_digest(body)}"


def question_sha256(question: str) -> str:
    return sha256(question.encode("utf-8")).hexdigest()


__all__ = tuple(name for name in globals() if not name.startswith("_"))
