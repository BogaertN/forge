"""Canonical serialization and stable identity helpers for Slice 40D."""
from __future__ import annotations
from dataclasses import fields, is_dataclass, replace
from enum import Enum
import hashlib, json
from typing import Any

class CongruityCanonicalizationError(ValueError):
    pass

def _normalize(value: Any) -> Any:
    if isinstance(value, Enum): return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _normalize(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, tuple): return [_normalize(v) for v in value]
    if isinstance(value, list): return [_normalize(v) for v in value]
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise CongruityCanonicalizationError("canonical mappings require string keys")
        return {k: _normalize(value[k]) for k in sorted(value)}
    if value is None or type(value) in (str, bool, int): return value
    raise CongruityCanonicalizationError(f"unsupported canonical value type: {type(value).__name__}")

def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(_normalize(value), ensure_ascii=False, separators=(",", ":"), sort_keys=False, allow_nan=False).encode("utf-8")

def deterministic_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()

def stable_identifier(prefix: str, value: Any) -> str:
    if not isinstance(prefix, str) or not prefix:
        raise CongruityCanonicalizationError("identifier prefix must be non-empty text")
    return f"{prefix}:sha256:{deterministic_digest(value)}"

def with_expected_id(record: Any, field_name: str, prefix: str) -> Any:
    if not is_dataclass(record) or isinstance(record, type):
        raise CongruityCanonicalizationError("record must be a dataclass")
    names=tuple(f.name for f in fields(record))
    if field_name not in names:
        raise CongruityCanonicalizationError(f"unknown identity field: {field_name}")
    payload={f.name:_normalize(getattr(record,f.name)) for f in fields(record) if f.name != field_name}
    return replace(record, **{field_name: stable_identifier(prefix,payload)})
