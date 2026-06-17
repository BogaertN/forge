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

ALLOWED_SUPPORT_CATEGORIES = (
    "no_missing_support_boundary",
    "missing_concept_support_boundary",
    "missing_predicate_support_boundary",
    "missing_role_support_boundary",
    "missing_gate_support_boundary",
    "missing_source_support_boundary",
    "unsupported_language_support_boundary",
    "unknown_support_boundary",
)

ALLOWED_SUPPORT_STATUS = (
    "satisfied_boundary",
    "missing_boundary",
    "unsupported_boundary",
    "held_boundary",
)

SUPPORT_FALSE_ONLY_FIELDS = (
    "support_resolution",
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
class MissingSupportBoundaryRecord:
    support_boundary_id: str
    support_key: str
    source_expression_id: str
    support_category: str
    support_status: str
    required_future_boundary: str
    explanation_boundary: str = ""
    no_action_safe: bool = True
    provenance_tag: str = "slice11_boundary"
    version_tag: str = "v1"
    support_resolution: bool = False
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
            "support_key": self.support_key,
            "source_expression_id": self.source_expression_id,
            "support_category": self.support_category,
            "support_status": self.support_status,
            "required_future_boundary": self.required_future_boundary,
            "explanation_boundary": self.explanation_boundary,
            "no_action_safe": self.no_action_safe,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("missing_support", self.canonical_body())


def validate_missing_support_boundary_record(record: MissingSupportBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.support_category not in ALLOWED_SUPPORT_CATEGORIES:
        issues.append(_issue("support_category", "unsupported_support_category"))
    if record.support_status not in ALLOWED_SUPPORT_STATUS:
        issues.append(_issue("support_status", "unsupported_support_status"))
    if not record.support_key:
        issues.append(_issue("support_key", "required"))
    if not record.source_expression_id:
        issues.append(_issue("source_expression_id", "required"))
    if not record.required_future_boundary:
        issues.append(_issue("required_future_boundary", "required"))
    if record.no_action_safe is not True:
        issues.append(_issue("no_action_safe", "must_remain_true"))
    if record.support_boundary_id != record.expected_id():
        issues.append(_issue("support_boundary_id", "does_not_match_canonical_body"))
    _check_false_only(record, SUPPORT_FALSE_ONLY_FIELDS, issues, "slice11")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_missing_support_boundary_record() -> MissingSupportBoundaryRecord:
    body = {
        "support_key": "appointment_time_missing_boundary",
        "source_expression_id": "src_expr:demo",
        "support_category": "missing_gate_support_boundary",
        "support_status": "missing_boundary",
        "required_future_boundary": "clarification_required_state_boundary",
        "explanation_boundary": "appointment time is required before any later reply candidate could become actionable",
        "no_action_safe": True,
        "provenance_tag": "slice11_demo_boundary",
        "version_tag": "v1",
    }
    return MissingSupportBoundaryRecord(support_boundary_id=stable_boundary_id("missing_support", body), **body)


def demo_no_missing_support_boundary_record() -> MissingSupportBoundaryRecord:
    body = {
        "support_key": "no_missing_support_fixture_boundary",
        "source_expression_id": "src_expr:demo",
        "support_category": "no_missing_support_boundary",
        "support_status": "satisfied_boundary",
        "required_future_boundary": "none_boundary",
        "explanation_boundary": "fixture only records that no missing support was observed inside this scaffold",
        "no_action_safe": True,
        "provenance_tag": "slice11_demo_boundary",
        "version_tag": "v1",
    }
    return MissingSupportBoundaryRecord(support_boundary_id=stable_boundary_id("missing_support", body), **body)
