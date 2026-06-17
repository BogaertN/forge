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

ALLOWED_COMPETITION_STATUSES = (
    "competing_candidates_separated_boundary",
    "single_candidate_boundary",
    "competition_unknown_boundary",
    "held_boundary",
)

COMPETITION_FALSE_ONLY_FIELDS = (
    "candidate_ranking",
    "candidate_selection",
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
class CandidateCompetitionSetBoundaryRecord:
    competition_set_id: str
    group_key: str
    source_expression_id: str
    candidate_meaning_ids: Tuple[str, ...]
    separation_reason_refs: Tuple[str, ...]
    competition_status: str = "competing_candidates_separated_boundary"
    unresolved_selection_boundary: bool = True
    no_action_safe: bool = True
    provenance_tag: str = "slice11_boundary"
    version_tag: str = "v1"
    candidate_ranking: bool = False
    candidate_selection: bool = False
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
            "group_key": self.group_key,
            "source_expression_id": self.source_expression_id,
            "candidate_meaning_ids": self.candidate_meaning_ids,
            "separation_reason_refs": self.separation_reason_refs,
            "competition_status": self.competition_status,
            "unresolved_selection_boundary": self.unresolved_selection_boundary,
            "no_action_safe": self.no_action_safe,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("candidate_competition", self.canonical_body())


def validate_candidate_competition_set_record(record: CandidateCompetitionSetBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.competition_status not in ALLOWED_COMPETITION_STATUSES:
        issues.append(_issue("competition_status", "unsupported_competition_status"))
    if not record.group_key:
        issues.append(_issue("group_key", "required"))
    if not record.source_expression_id:
        issues.append(_issue("source_expression_id", "required"))
    if not _tuple_of_text(record.candidate_meaning_ids, allow_empty=False):
        issues.append(_issue("candidate_meaning_ids", "at_least_one_candidate_required"))
    if not _tuple_of_text(record.separation_reason_refs, allow_empty=False):
        issues.append(_issue("separation_reason_refs", "at_least_one_reason_required"))
    if record.unresolved_selection_boundary is not True:
        issues.append(_issue("unresolved_selection_boundary", "must_remain_true"))
    if record.no_action_safe is not True:
        issues.append(_issue("no_action_safe", "must_remain_true"))
    if record.competition_set_id != record.expected_id():
        issues.append(_issue("competition_set_id", "does_not_match_canonical_body"))
    _check_false_only(record, COMPETITION_FALSE_ONLY_FIELDS, issues, "slice11")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_candidate_competition_set_record() -> CandidateCompetitionSetBoundaryRecord:
    body = {
        "group_key": "reply_candidate_group_boundary",
        "source_expression_id": "src_expr:demo",
        "candidate_meaning_ids": ("candidate_meaning:reply_requires_time", "candidate_meaning:no_action_safe"),
        "separation_reason_refs": ("missing_support:appointment_time", "gate_boundary:clarification_required"),
        "competition_status": "competing_candidates_separated_boundary",
        "unresolved_selection_boundary": True,
        "no_action_safe": True,
        "provenance_tag": "slice11_demo_boundary",
        "version_tag": "v1",
    }
    return CandidateCompetitionSetBoundaryRecord(competition_set_id=stable_boundary_id("candidate_competition", body), **body)
