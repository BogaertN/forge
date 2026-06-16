"""Deterministic law-trace scaffold for Slice 7.

A law trace records what rule family was referenced and what narrow
scaffold decision was recorded. It does not perform full grammar work,
select intended meaning, or attach any executable capability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, Iterable, Mapping, Tuple


SCHEMA_VERSION = "aiweb-law-trace-scaffold-v1"
SCOPE_STATUS = "scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"

ALLOWED_RULE_FAMILIES = (
    "grammar",
    "scope",
    "inheritance",
    "operator",
    "reversibility",
    "boundary",
    "unknown",
)

ALLOWED_DECISIONS = (
    "recorded",
    "held",
    "blocked",
    "not_applicable",
)

ALLOWED_TRACE_KINDS = (
    "law_trace_scaffold",
    "boundary_trace_scaffold",
    "unknown_trace_scaffold",
)

CONTROLLED_STEP_KEYS = (
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


def law_trace_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "trace_scaffold_only": True,
        "full_grammar_engine": False,
        "intended_meaning_selection": False,
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


def _detail_has_controlled_overreach(details: Mapping[str, Any]) -> Tuple[bool, str]:
    for key in CONTROLLED_STEP_KEYS:
        if bool(details.get(key)):
            return True, key
    return False, ""


@dataclass(frozen=True)
class LawTraceStep:
    step_id: str
    rule_family: str
    rule_id: str
    input_ref: str
    decision: str
    note: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "rule_family": self.rule_family,
            "rule_id": self.rule_id,
            "input_ref": self.input_ref,
            "decision": self.decision,
            "note": self.note,
            "details": dict(self.details),
        }

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["step_id"] = self.step_id
        return _canonicalize(data)

    def validate(self) -> Tuple[bool, str]:
        if self.rule_family not in ALLOWED_RULE_FAMILIES:
            return False, "rule family is not allowed"
        if self.decision not in ALLOWED_DECISIONS:
            return False, "decision is not allowed"
        if not self.rule_id:
            return False, "rule id is required"
        if not self.input_ref:
            return False, "input reference is required"
        overreach, key = _detail_has_controlled_overreach(self.details)
        if overreach:
            return False, f"step requests controlled downstream field: {key}"
        expected = law_trace_step_id(
            rule_family=self.rule_family,
            rule_id=self.rule_id,
            input_ref=self.input_ref,
            decision=self.decision,
            note=self.note,
            details=self.details,
        )
        if self.step_id != expected:
            return False, "step id does not match canonical body"
        return True, "law trace step scaffold record is valid"


@dataclass(frozen=True)
class LawTrace:
    schema_version: str
    trace_id: str
    trace_kind: str
    authority_basis: Tuple[str, ...]
    linked_object_ids: Tuple[str, ...]
    steps: Tuple[LawTraceStep, ...]
    status: str = "scaffold_draft"
    metadata: Mapping[str, str] = field(default_factory=dict)

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "trace_kind": self.trace_kind,
            "authority_basis": list(self.authority_basis),
            "linked_object_ids": list(self.linked_object_ids),
            "steps": [step.canonical_dict() for step in self.steps],
            "status": self.status,
            "metadata": dict(self.metadata),
        }

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["trace_id"] = self.trace_id
        return _canonicalize(data)

    def canonical_json(self) -> str:
        return _canonical_json(self.canonical_dict())

    def content_hash(self) -> str:
        return _digest(self.canonical_dict())

    def validate(self) -> Tuple[bool, str]:
        if self.schema_version != SCHEMA_VERSION:
            return False, "schema version mismatch"
        if self.trace_kind not in ALLOWED_TRACE_KINDS:
            return False, "trace kind is not allowed"
        if not self.authority_basis:
            return False, "authority basis is required"
        if not self.steps:
            return False, "at least one trace step is required"
        seen = set()
        for step in self.steps:
            ok, detail = step.validate()
            if not ok:
                return False, detail
            if step.step_id in seen:
                return False, "duplicate trace step id"
            seen.add(step.step_id)
        expected = law_trace_id(
            trace_kind=self.trace_kind,
            authority_basis=self.authority_basis,
            linked_object_ids=self.linked_object_ids,
            steps=self.steps,
            status=self.status,
            metadata=self.metadata,
        )
        if self.trace_id != expected:
            return False, "trace id does not match canonical body"
        return True, "law trace scaffold record is valid"


def law_trace_step_id(
    *,
    rule_family: str,
    rule_id: str,
    input_ref: str,
    decision: str,
    note: str = "",
    details: Mapping[str, Any] | None = None,
) -> str:
    body = {
        "rule_family": rule_family,
        "rule_id": rule_id,
        "input_ref": input_ref,
        "decision": decision,
        "note": note,
        "details": dict(details or {}),
    }
    return "lts_" + _digest(body)[:20]


def build_law_trace_step(
    *,
    rule_family: str,
    rule_id: str,
    input_ref: str,
    decision: str = "recorded",
    note: str = "",
    details: Mapping[str, Any] | None = None,
) -> LawTraceStep:
    safe_details = dict(details or {})
    step_id = law_trace_step_id(
        rule_family=rule_family,
        rule_id=rule_id,
        input_ref=input_ref,
        decision=decision,
        note=note,
        details=safe_details,
    )
    step = LawTraceStep(
        step_id=step_id,
        rule_family=rule_family,
        rule_id=rule_id,
        input_ref=input_ref,
        decision=decision,
        note=note,
        details=safe_details,
    )
    ok, detail = step.validate()
    if not ok:
        raise ValueError(detail)
    return step


def law_trace_id(
    *,
    trace_kind: str,
    authority_basis: Iterable[str],
    linked_object_ids: Iterable[str],
    steps: Iterable[LawTraceStep],
    status: str = "scaffold_draft",
    metadata: Mapping[str, str] | None = None,
) -> str:
    body = {
        "schema_version": SCHEMA_VERSION,
        "trace_kind": trace_kind,
        "authority_basis": list(authority_basis),
        "linked_object_ids": list(linked_object_ids),
        "steps": [step.canonical_dict() for step in steps],
        "status": status,
        "metadata": dict(metadata or {}),
    }
    return "lt_" + _digest(body)[:24]


def build_law_trace(
    *,
    trace_kind: str = "law_trace_scaffold",
    authority_basis: Iterable[str] = (),
    linked_object_ids: Iterable[str] = (),
    steps: Iterable[LawTraceStep] = (),
    status: str = "scaffold_draft",
    metadata: Mapping[str, str] | None = None,
) -> LawTrace:
    basis = tuple(str(item) for item in authority_basis)
    linked = tuple(str(item) for item in linked_object_ids)
    step_tuple = tuple(steps)
    safe_metadata = {str(k): str(v) for k, v in dict(metadata or {}).items()}
    trace_id = law_trace_id(
        trace_kind=trace_kind,
        authority_basis=basis,
        linked_object_ids=linked,
        steps=step_tuple,
        status=status,
        metadata=safe_metadata,
    )
    trace = LawTrace(
        schema_version=SCHEMA_VERSION,
        trace_id=trace_id,
        trace_kind=trace_kind,
        authority_basis=basis,
        linked_object_ids=linked,
        steps=step_tuple,
        status=status,
        metadata=safe_metadata,
    )
    ok, detail = trace.validate()
    if not ok:
        raise ValueError(detail)
    return trace
