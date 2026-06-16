"""Deterministic neutral meaning-object scaffold for Slice 7.

This module creates stable records only. It does not select concepts,
complete frames, choose gates, render outward text, update stored material,
route tools, or alter any accepted baseline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, Iterable, Mapping, Tuple


SCHEMA_VERSION = "aiweb-meaning-object-scaffold-v1"
SCOPE_STATUS = "scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"

ALLOWED_OBJECT_KINDS = (
    "neutral_input_record",
    "neutral_intermediate_record",
    "neutral_output_record",
)

ALLOWED_STATUSES = (
    "scaffold_draft",
    "held",
    "validated_scaffold",
)

CONTROLLED_PAYLOAD_KEYS = (
    "concept_resolution",
    "predicate_resolution",
    "gate_selection",
    "expression_rendering",
    "ui_surface",
    "stored_material_update",
    "external_resource_use",
    "delivery_step",
    "action_route",
    "baseline_change",
)


def _normalize_text(value: str) -> str:
    return " ".join(str(value).split())


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonicalize(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def meaning_object_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "object_scaffold_only": True,
        "concept_resolution": False,
        "predicate_resolution": False,
        "gate_selection": False,
        "expression_rendering": False,
        "ui_surface": False,
        "stored_material_update": False,
        "external_resource_use": False,
        "delivery_step": False,
        "action_route": False,
        "baseline_change": False,
    }


def _payload_has_controlled_overreach(payload: Mapping[str, Any]) -> Tuple[bool, str]:
    for key in CONTROLLED_PAYLOAD_KEYS:
        if bool(payload.get(key)):
            return True, key
    return False, ""


@dataclass(frozen=True)
class MeaningObject:
    schema_version: str
    object_id: str
    object_kind: str
    source_label: str
    normalized_text: str
    authority_basis: Tuple[str, ...]
    law_trace_ids: Tuple[str, ...] = field(default_factory=tuple)
    status: str = "scaffold_draft"
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_kind": self.object_kind,
            "source_label": self.source_label,
            "normalized_text": self.normalized_text,
            "authority_basis": list(self.authority_basis),
            "law_trace_ids": list(self.law_trace_ids),
            "status": self.status,
            "payload": dict(self.payload),
            "metadata": dict(self.metadata),
        }

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["object_id"] = self.object_id
        return _canonicalize(data)

    def canonical_json(self) -> str:
        return _canonical_json(self.canonical_dict())

    def content_hash(self) -> str:
        return _digest(self.canonical_dict())

    def validate(self) -> Tuple[bool, str]:
        if self.schema_version != SCHEMA_VERSION:
            return False, "schema version mismatch"
        if self.object_kind not in ALLOWED_OBJECT_KINDS:
            return False, "object kind is not allowed"
        if self.status not in ALLOWED_STATUSES:
            return False, "status is not allowed"
        if not self.normalized_text:
            return False, "normalized text is required"
        if not self.authority_basis:
            return False, "authority basis is required"
        overreach, key = _payload_has_controlled_overreach(self.payload)
        if overreach:
            return False, f"payload requests controlled downstream field: {key}"
        expected = meaning_object_id(
            object_kind=self.object_kind,
            source_label=self.source_label,
            normalized_text=self.normalized_text,
            authority_basis=self.authority_basis,
            law_trace_ids=self.law_trace_ids,
            status=self.status,
            payload=self.payload,
            metadata=self.metadata,
        )
        if self.object_id != expected:
            return False, "object id does not match canonical body"
        return True, "meaning object scaffold record is valid"


def meaning_object_id(
    *,
    object_kind: str,
    source_label: str,
    normalized_text: str,
    authority_basis: Iterable[str],
    law_trace_ids: Iterable[str] = (),
    status: str = "scaffold_draft",
    payload: Mapping[str, Any] | None = None,
    metadata: Mapping[str, str] | None = None,
) -> str:
    body = {
        "schema_version": SCHEMA_VERSION,
        "object_kind": object_kind,
        "source_label": source_label,
        "normalized_text": normalized_text,
        "authority_basis": list(authority_basis),
        "law_trace_ids": list(law_trace_ids),
        "status": status,
        "payload": dict(payload or {}),
        "metadata": dict(metadata or {}),
    }
    return "mo_" + _digest(body)[:24]


def build_meaning_object(
    *,
    source_text: str,
    source_label: str,
    object_kind: str = "neutral_input_record",
    authority_basis: Iterable[str] = (),
    law_trace_ids: Iterable[str] = (),
    status: str = "scaffold_draft",
    payload: Mapping[str, Any] | None = None,
    metadata: Mapping[str, str] | None = None,
) -> MeaningObject:
    normalized_text = _normalize_text(source_text)
    basis = tuple(str(item) for item in authority_basis)
    traces = tuple(str(item) for item in law_trace_ids)
    safe_payload = dict(payload or {})
    safe_metadata = {str(k): str(v) for k, v in dict(metadata or {}).items()}
    object_id = meaning_object_id(
        object_kind=object_kind,
        source_label=str(source_label),
        normalized_text=normalized_text,
        authority_basis=basis,
        law_trace_ids=traces,
        status=status,
        payload=safe_payload,
        metadata=safe_metadata,
    )
    record = MeaningObject(
        schema_version=SCHEMA_VERSION,
        object_id=object_id,
        object_kind=object_kind,
        source_label=str(source_label),
        normalized_text=normalized_text,
        authority_basis=basis,
        law_trace_ids=traces,
        status=status,
        payload=safe_payload,
        metadata=safe_metadata,
    )
    ok, detail = record.validate()
    if not ok:
        raise ValueError(detail)
    return record
