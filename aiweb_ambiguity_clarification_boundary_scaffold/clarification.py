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

ALLOWED_CLARIFICATION_MODES = (
    "clarification_required_boundary",
    "clarification_not_askable_boundary",
    "clarification_deferred_boundary",
    "clarification_blocked_boundary",
)

ALLOWED_ASKABILITY = (
    "lawfully_askable_boundary",
    "not_askable_boundary",
    "external_authority_required_boundary",
    "missing_trace_boundary",
    "unknown_askability_boundary",
)

CLARIFICATION_FALSE_ONLY_FIELDS = (
    "live_clarification",
    "user_facing_question_emission",
    "clarification_bypasses_external_authority",
    "memory_write",
    "delivery_action",
    "tool_invocation",
    "action_authorization",
    "evidence_validation",
    "external_resource_admission",
    "selected_meaning",
    "truth_decision",
    "production_readiness",
    "release_authority",
)


@dataclass(frozen=True)
class ClarificationRequirementBoundaryRecord:
    clarification_boundary_id: str
    clarification_key: str
    candidate_ref: str
    state_ref: str
    clarification_mode: str
    askability_boundary: str
    missing_support_refs: Tuple[str, ...]
    allowed_question_slot_boundaries: Tuple[str, ...] = ()
    forbidden_question_reason_refs: Tuple[str, ...] = ()
    trace_required: bool = True
    no_action_safe: bool = True
    provenance_tag: str = "slice12_boundary"
    version_tag: str = "v1"
    live_clarification: bool = False
    user_facing_question_emission: bool = False
    clarification_bypasses_external_authority: bool = False
    memory_write: bool = False
    delivery_action: bool = False
    tool_invocation: bool = False
    action_authorization: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    production_readiness: bool = False
    release_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "clarification_key": self.clarification_key,
            "candidate_ref": self.candidate_ref,
            "state_ref": self.state_ref,
            "clarification_mode": self.clarification_mode,
            "askability_boundary": self.askability_boundary,
            "missing_support_refs": self.missing_support_refs,
            "allowed_question_slot_boundaries": self.allowed_question_slot_boundaries,
            "forbidden_question_reason_refs": self.forbidden_question_reason_refs,
            "trace_required": self.trace_required,
            "no_action_safe": self.no_action_safe,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("clarification_req", self.canonical_body())


def build_clarification_requirement_record(
    *,
    clarification_key: str,
    candidate_ref: str,
    state_ref: str,
    clarification_mode: str,
    askability_boundary: str,
    missing_support_refs: Tuple[str, ...],
    allowed_question_slot_boundaries: Tuple[str, ...] = (),
    forbidden_question_reason_refs: Tuple[str, ...] = (),
    provenance_tag: str = "slice12_boundary",
    version_tag: str = "v1",
) -> ClarificationRequirementBoundaryRecord:
    body = {
        "clarification_key": clarification_key,
        "candidate_ref": candidate_ref,
        "state_ref": state_ref,
        "clarification_mode": clarification_mode,
        "askability_boundary": askability_boundary,
        "missing_support_refs": missing_support_refs,
        "allowed_question_slot_boundaries": allowed_question_slot_boundaries,
        "forbidden_question_reason_refs": forbidden_question_reason_refs,
        "trace_required": True,
        "no_action_safe": True,
        "provenance_tag": provenance_tag,
        "version_tag": version_tag,
    }
    return ClarificationRequirementBoundaryRecord(clarification_boundary_id=stable_boundary_id("clarification_req", body), **body)


def validate_clarification_requirement_record(record: ClarificationRequirementBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.clarification_mode not in ALLOWED_CLARIFICATION_MODES:
        issues.append(_issue("clarification_mode", "unsupported_clarification_mode"))
    if record.askability_boundary not in ALLOWED_ASKABILITY:
        issues.append(_issue("askability_boundary", "unsupported_askability_boundary"))
    if not record.clarification_key:
        issues.append(_issue("clarification_key", "required"))
    if not record.candidate_ref:
        issues.append(_issue("candidate_ref", "required"))
    if not record.state_ref:
        issues.append(_issue("state_ref", "required"))
    if not _tuple_of_text(record.missing_support_refs, allow_empty=False):
        issues.append(_issue("missing_support_refs", "at_least_one_missing_support_ref_required"))
    if not _tuple_of_text(record.allowed_question_slot_boundaries):
        issues.append(_issue("allowed_question_slot_boundaries", "must_be_tuple_of_text_boundaries"))
    if not _tuple_of_text(record.forbidden_question_reason_refs):
        issues.append(_issue("forbidden_question_reason_refs", "must_be_tuple_of_text_refs"))
    if record.trace_required is not True:
        issues.append(_issue("trace_required", "must_remain_true"))
    if record.no_action_safe is not True:
        issues.append(_issue("no_action_safe", "must_remain_true"))
    if record.clarification_boundary_id != record.expected_id():
        issues.append(_issue("clarification_boundary_id", "does_not_match_canonical_body"))
    _check_false_only(record, CLARIFICATION_FALSE_ONLY_FIELDS, issues, "slice12")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_clarification_required_record() -> ClarificationRequirementBoundaryRecord:
    return build_clarification_requirement_record(
        clarification_key="askable_missing_time_boundary",
        candidate_ref="candidate_meaning:reply_requires_time",
        state_ref="ambiguity_state:demo",
        clarification_mode="clarification_required_boundary",
        askability_boundary="lawfully_askable_boundary",
        missing_support_refs=("missing_support:appointment_time",),
        allowed_question_slot_boundaries=("slot:appointment_time",),
        provenance_tag="slice12_demo_boundary",
    )


def demo_clarification_blocked_record() -> ClarificationRequirementBoundaryRecord:
    return build_clarification_requirement_record(
        clarification_key="resource_clarification_blocked_boundary",
        candidate_ref="candidate_meaning:external_resource_needed",
        state_ref="ambiguity_state:deferred_external_resource",
        clarification_mode="clarification_blocked_boundary",
        askability_boundary="external_authority_required_boundary",
        missing_support_refs=("missing_support:resource_license",),
        forbidden_question_reason_refs=("reason:external_authority_missing",),
        provenance_tag="slice12_demo_boundary",
    )
