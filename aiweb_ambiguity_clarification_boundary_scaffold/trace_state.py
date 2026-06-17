from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-ambiguity-clarification-boundary-scaffold-v1"
SCOPE_STATUS = "ambiguity_clarification_boundary_scaffold_only"
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

ALLOWED_TRACE_STATUS = (
    "trace_required_boundary",
    "trace_present_boundary",
    "trace_missing_boundary",
    "trace_deferred_boundary",
)

TRACE_FALSE_ONLY_FIELDS = (
    "evidence_validation",
    "memory_write",
    "delivery_action",
    "external_resource_admission",
    "implementation_action",
    "selected_meaning",
    "truth_decision",
)


@dataclass(frozen=True)
class StateTraceBoundaryRecord:
    trace_state_id: str
    state_ref: str
    candidate_ref: str
    trace_status: str
    reason_refs: Tuple[str, ...]
    affected_boundary_refs: Tuple[str, ...]
    trace_integrity_required: bool = True
    no_action_safe: bool = True
    provenance_tag: str = "slice12_boundary"
    version_tag: str = "v1"
    evidence_validation: bool = False
    memory_write: bool = False
    delivery_action: bool = False
    external_resource_admission: bool = False
    implementation_action: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "state_ref": self.state_ref,
            "candidate_ref": self.candidate_ref,
            "trace_status": self.trace_status,
            "reason_refs": self.reason_refs,
            "affected_boundary_refs": self.affected_boundary_refs,
            "trace_integrity_required": self.trace_integrity_required,
            "no_action_safe": self.no_action_safe,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("state_trace", self.canonical_body())


def build_state_trace_record(
    *,
    state_ref: str,
    candidate_ref: str,
    trace_status: str,
    reason_refs: Tuple[str, ...],
    affected_boundary_refs: Tuple[str, ...],
    provenance_tag: str = "slice12_boundary",
    version_tag: str = "v1",
) -> StateTraceBoundaryRecord:
    body = {
        "state_ref": state_ref,
        "candidate_ref": candidate_ref,
        "trace_status": trace_status,
        "reason_refs": reason_refs,
        "affected_boundary_refs": affected_boundary_refs,
        "trace_integrity_required": True,
        "no_action_safe": True,
        "provenance_tag": provenance_tag,
        "version_tag": version_tag,
    }
    return StateTraceBoundaryRecord(trace_state_id=stable_boundary_id("state_trace", body), **body)


def validate_state_trace_record(record: StateTraceBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.trace_status not in ALLOWED_TRACE_STATUS:
        issues.append(_issue("trace_status", "unsupported_trace_status"))
    if not record.state_ref:
        issues.append(_issue("state_ref", "required"))
    if not record.candidate_ref:
        issues.append(_issue("candidate_ref", "required"))
    if not _tuple_of_text(record.reason_refs, allow_empty=False):
        issues.append(_issue("reason_refs", "at_least_one_reason_ref_required"))
    if not _tuple_of_text(record.affected_boundary_refs, allow_empty=False):
        issues.append(_issue("affected_boundary_refs", "at_least_one_affected_boundary_ref_required"))
    if record.trace_integrity_required is not True:
        issues.append(_issue("trace_integrity_required", "must_remain_true"))
    if record.no_action_safe is not True:
        issues.append(_issue("no_action_safe", "must_remain_true"))
    if record.trace_state_id != record.expected_id():
        issues.append(_issue("trace_state_id", "does_not_match_canonical_body"))
    _check_false_only(record, TRACE_FALSE_ONLY_FIELDS, issues, "slice12")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_state_trace_record() -> StateTraceBoundaryRecord:
    return build_state_trace_record(
        state_ref="ambiguity_state:demo",
        candidate_ref="candidate_meaning:reply_requires_time",
        trace_status="trace_required_boundary",
        reason_refs=("reason:clarification_affects_interpretation",),
        affected_boundary_refs=("interpretation_boundary", "clarification_boundary", "deferral_boundary"),
        provenance_tag="slice12_demo_boundary",
    )
