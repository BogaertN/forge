from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-candidate-meaning-boundary-scaffold-v1"
SCOPE_STATUS = "candidate_meaning_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonicalize(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_boundary_id(prefix: str, *parts: Any) -> str:
    body = {"prefix": prefix, "parts": [_canonicalize(part) for part in parts]}
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    reason: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    ok: bool
    issues: Tuple[ValidationIssue, ...] = ()

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def _issue(field: str, reason: str) -> ValidationIssue:
    return ValidationIssue(field=field, reason=reason)


def _check_false_only(record: Any, fields: Tuple[str, ...], issues: list[ValidationIssue], namespace: str) -> None:
    for field_name in fields:
        if bool(getattr(record, field_name, False)):
            issues.append(_issue(field_name, f"{namespace}:{field_name}_must_remain_false"))


def _tuple_of_text(value: Tuple[str, ...], *, allow_empty: bool = True) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    return all(isinstance(item, str) and bool(item.strip()) for item in value)

ALLOWED_DERIVED_STRUCTURE_KINDS = (
    "source_grounded_candidate_structure_boundary",
    "no_action_safe_structure_boundary",
    "unsupported_structure_boundary",
    "unknown_structure_boundary",
)

ALLOWED_TRANSFORM_STATUS = (
    "referenced_only_boundary",
    "source_grounded_boundary",
    "missing_support_boundary",
    "held_boundary",
)

DERIVED_FALSE_ONLY_FIELDS = (
    "live_runtime_interpretation",
    "concept_resolution",
    "predicate_resolution",
    "gate_resolution",
    "selected_meaning",
    "final_meaning_selection",
    "truth_decision",
    "action_authorization",
    "tool_invocation",
    "delivery_action",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
)


@dataclass(frozen=True)
class DerivedStructureCustodyRecord:
    derived_structure_id: str
    source_expression_id: str
    derived_structure_kind: str
    meaning_object_refs: Tuple[str, ...] = ()
    law_trace_refs: Tuple[str, ...] = ()
    concept_boundary_refs: Tuple[str, ...] = ()
    predicate_boundary_refs: Tuple[str, ...] = ()
    gate_boundary_refs: Tuple[str, ...] = ()
    missing_support_refs: Tuple[str, ...] = ()
    transform_status: str = "referenced_only_boundary"
    provenance_tag: str = "slice11_boundary"
    version_tag: str = "v1"
    live_runtime_interpretation: bool = False
    concept_resolution: bool = False
    predicate_resolution: bool = False
    gate_resolution: bool = False
    selected_meaning: bool = False
    final_meaning_selection: bool = False
    truth_decision: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    delivery_action: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "source_expression_id": self.source_expression_id,
            "derived_structure_kind": self.derived_structure_kind,
            "meaning_object_refs": self.meaning_object_refs,
            "law_trace_refs": self.law_trace_refs,
            "concept_boundary_refs": self.concept_boundary_refs,
            "predicate_boundary_refs": self.predicate_boundary_refs,
            "gate_boundary_refs": self.gate_boundary_refs,
            "missing_support_refs": self.missing_support_refs,
            "transform_status": self.transform_status,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("derived_struct", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["derived_structure_id"] = self.derived_structure_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def validate_derived_structure_custody_record(record: DerivedStructureCustodyRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.derived_structure_kind not in ALLOWED_DERIVED_STRUCTURE_KINDS:
        issues.append(_issue("derived_structure_kind", "unsupported_derived_structure_kind"))
    if record.transform_status not in ALLOWED_TRANSFORM_STATUS:
        issues.append(_issue("transform_status", "unsupported_transform_status"))
    if not record.source_expression_id:
        issues.append(_issue("source_expression_id", "required"))
    for field_name in (
        "meaning_object_refs",
        "law_trace_refs",
        "concept_boundary_refs",
        "predicate_boundary_refs",
        "gate_boundary_refs",
        "missing_support_refs",
    ):
        if not _tuple_of_text(getattr(record, field_name)):
            issues.append(_issue(field_name, "must_be_tuple_of_text_boundary_refs"))
    if record.derived_structure_id != record.expected_id():
        issues.append(_issue("derived_structure_id", "does_not_match_canonical_body"))
    _check_false_only(record, DERIVED_FALSE_ONLY_FIELDS, issues, "slice11")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_derived_structure_custody_record() -> DerivedStructureCustodyRecord:
    body = {
        "source_expression_id": "src_expr:demo",
        "derived_structure_kind": "source_grounded_candidate_structure_boundary",
        "meaning_object_refs": ("meaning_object:demo",),
        "law_trace_refs": ("law_trace:demo",),
        "concept_boundary_refs": ("concept_boundary:reply", "concept_boundary:appointment_time"),
        "predicate_boundary_refs": ("predicate_frame:draft_reply_boundary",),
        "gate_boundary_refs": ("gate_boundary:clarification_required",),
        "missing_support_refs": ("missing_support:appointment_time",),
        "transform_status": "source_grounded_boundary",
        "provenance_tag": "slice11_demo_boundary",
        "version_tag": "v1",
    }
    return DerivedStructureCustodyRecord(derived_structure_id=stable_boundary_id("derived_struct", body), **body)
