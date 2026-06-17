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

ALLOWED_STATE_KINDS = (
    "ambiguous_state_boundary",
    "unknown_state_boundary",
    "unsupported_state_boundary",
    "clarification_required_state_boundary",
    "incongruent_state_boundary",
    "understood_but_blocked_state_boundary",
    "deferred_state_boundary",
    "no_action_safe_termination_boundary",
)

ALLOWED_STATE_STATUS = (
    "state_represented_boundary",
    "state_preserved_boundary",
    "state_held_boundary",
    "state_blocked_boundary",
    "state_deferred_boundary",
    "state_no_action_safe_boundary",
)

STATE_FALSE_ONLY_FIELDS = (
    "live_runtime_interpretation",
    "live_clarification",
    "user_facing_question_emission",
    "selected_meaning",
    "final_meaning_selection",
    "truth_decision",
    "permission_grant",
    "action_authorization",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "memory_write",
    "evidence_validation",
    "external_resource_admission",
    "expression_rendering",
    "production_readiness",
    "release_authority",
)


def ambiguity_clarification_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "represents_ambiguity": True,
        "represents_unknown": True,
        "represents_unsupported": True,
        "represents_clarification_required": True,
        "represents_incongruent": True,
        "represents_understood_but_blocked": True,
        "represents_deferred": True,
        "represents_no_action_safe_termination": True,
        "preserves_uncertainty_without_guessing": True,
        "references_slice10_gate_boundaries_only": True,
        "references_slice11_candidate_boundaries_only": True,
        "live_runtime_interpretation": False,
        "live_clarification": False,
        "user_facing_question_emission": False,
        "selected_meaning": False,
        "final_meaning_selection": False,
        "truth_decision": False,
        "permission_grant": False,
        "action_authorization": False,
        "tool_invocation": False,
        "capability_route": False,
        "delivery_action": False,
        "memory_write": False,
        "evidence_validation": False,
        "external_resource_admission": False,
        "expression_rendering": False,
        "production_readiness": False,
        "release_authority": False,
        "gp014_status": "protected_not_superseded",
        "gp015_status": "failed_not_repaired",
        "gp015r1_status": "uninstalled_not_live",
        "sanskrit_wordnet_status": "hold_unadmitted",
    }


@dataclass(frozen=True)
class AmbiguityStateBoundaryRecord:
    state_boundary_id: str
    state_key: str
    state_kind: str
    state_status: str
    candidate_ref: str
    gate_ref: str
    reason_refs: Tuple[str, ...]
    missing_support_refs: Tuple[str, ...] = ()
    no_action_safe: bool = True
    uncertainty_preserved: bool = True
    provenance_tag: str = "slice12_boundary"
    version_tag: str = "v1"
    live_runtime_interpretation: bool = False
    live_clarification: bool = False
    user_facing_question_emission: bool = False
    selected_meaning: bool = False
    final_meaning_selection: bool = False
    truth_decision: bool = False
    permission_grant: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False
    expression_rendering: bool = False
    production_readiness: bool = False
    release_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "state_key": self.state_key,
            "state_kind": self.state_kind,
            "state_status": self.state_status,
            "candidate_ref": self.candidate_ref,
            "gate_ref": self.gate_ref,
            "reason_refs": self.reason_refs,
            "missing_support_refs": self.missing_support_refs,
            "no_action_safe": self.no_action_safe,
            "uncertainty_preserved": self.uncertainty_preserved,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("ambiguity_state", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["state_boundary_id"] = self.state_boundary_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_state_boundary_record(
    *,
    state_key: str,
    state_kind: str,
    state_status: str,
    candidate_ref: str,
    gate_ref: str,
    reason_refs: Tuple[str, ...],
    missing_support_refs: Tuple[str, ...] = (),
    provenance_tag: str = "slice12_boundary",
    version_tag: str = "v1",
) -> AmbiguityStateBoundaryRecord:
    body = {
        "state_key": state_key,
        "state_kind": state_kind,
        "state_status": state_status,
        "candidate_ref": candidate_ref,
        "gate_ref": gate_ref,
        "reason_refs": reason_refs,
        "missing_support_refs": missing_support_refs,
        "no_action_safe": True,
        "uncertainty_preserved": True,
        "provenance_tag": provenance_tag,
        "version_tag": version_tag,
    }
    return AmbiguityStateBoundaryRecord(state_boundary_id=stable_boundary_id("ambiguity_state", body), **body)


def validate_state_boundary_record(record: AmbiguityStateBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.state_kind not in ALLOWED_STATE_KINDS:
        issues.append(_issue("state_kind", "unsupported_state_kind"))
    if record.state_status not in ALLOWED_STATE_STATUS:
        issues.append(_issue("state_status", "unsupported_state_status"))
    if not record.state_key:
        issues.append(_issue("state_key", "required"))
    if not record.candidate_ref:
        issues.append(_issue("candidate_ref", "required"))
    if not record.gate_ref:
        issues.append(_issue("gate_ref", "required"))
    if not _tuple_of_text(record.reason_refs, allow_empty=False):
        issues.append(_issue("reason_refs", "at_least_one_reason_ref_required"))
    if not _tuple_of_text(record.missing_support_refs):
        issues.append(_issue("missing_support_refs", "must_be_tuple_of_text_refs"))
    if record.no_action_safe is not True:
        issues.append(_issue("no_action_safe", "must_remain_true"))
    if record.uncertainty_preserved is not True:
        issues.append(_issue("uncertainty_preserved", "must_remain_true"))
    if record.state_boundary_id != record.expected_id():
        issues.append(_issue("state_boundary_id", "does_not_match_canonical_body"))
    _check_false_only(record, STATE_FALSE_ONLY_FIELDS, issues, "slice12")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_ambiguity_state_record() -> AmbiguityStateBoundaryRecord:
    return build_state_boundary_record(
        state_key="ambiguous_reply_request_boundary",
        state_kind="ambiguous_state_boundary",
        state_status="state_preserved_boundary",
        candidate_ref="candidate_meaning:reply_requires_time",
        gate_ref="gate_boundary:clarification_required",
        reason_refs=("reason:multiple_candidate_meanings", "reason:missing_time"),
        missing_support_refs=("missing_support:appointment_time",),
        provenance_tag="slice12_demo_boundary",
    )


def demo_unknown_state_record() -> AmbiguityStateBoundaryRecord:
    return build_state_boundary_record(
        state_key="unknown_term_boundary",
        state_kind="unknown_state_boundary",
        state_status="state_held_boundary",
        candidate_ref="candidate_meaning:unknown_term",
        gate_ref="gate_boundary:unknown_concept",
        reason_refs=("reason:concept_authority_missing",),
        missing_support_refs=("missing_support:concept_authority",),
        provenance_tag="slice12_demo_boundary",
    )


def demo_unsupported_state_record() -> AmbiguityStateBoundaryRecord:
    return build_state_boundary_record(
        state_key="unsupported_language_boundary",
        state_kind="unsupported_state_boundary",
        state_status="state_blocked_boundary",
        candidate_ref="candidate_meaning:unsupported_language",
        gate_ref="gate_boundary:unsupported_language",
        reason_refs=("reason:language_support_missing",),
        missing_support_refs=("missing_support:language_lane",),
        provenance_tag="slice12_demo_boundary",
    )


def demo_deferred_state_record() -> AmbiguityStateBoundaryRecord:
    return build_state_boundary_record(
        state_key="deferred_external_resource_boundary",
        state_kind="deferred_state_boundary",
        state_status="state_deferred_boundary",
        candidate_ref="candidate_meaning:needs_external_resource",
        gate_ref="gate_boundary:external_authority_required",
        reason_refs=("reason:resource_not_admitted",),
        missing_support_refs=("missing_support:resource_license",),
        provenance_tag="slice12_demo_boundary",
    )
