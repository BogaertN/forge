"""Deterministic identities for Slice 40H records."""
from __future__ import annotations
from dataclasses import asdict, replace
from ..schema import stable_record_id

def with_id(value, namespace: str, field_name: str):
    body = asdict(value); body.pop(field_name, None)
    return replace(value, **{field_name: stable_record_id(namespace, body)})
