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

ALLOWED_CANDIDATE_KINDS = (
    "source_grounded_candidate_boundary",
    "no_action_safe_candidate_boundary",
    "unsupported_candidate_boundary",
    "unknown_candidate_boundary",
)

ALLOWED_CANDIDATE_STATES = (
    "candidate_constructed_boundary",
    "candidate_held_boundary",
    "missing_support_boundary",
    "no_action_safe_boundary",
    "unsupported_boundary",
    "unknown_boundary",
)

ALLOWED_SUPPORT_STATUS = (
    "support_referenced_boundary",
    "support_missing_boundary",
    "support_held_boundary",
    "support_unknown_boundary",
)

CANDIDATE_FALSE_ONLY_FIELDS = (
    "live_runtime_interpretation",
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


def candidate_meaning_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "represents_source_expression_custody": True,
        "represents_derived_structure_custody": True,
        "represents_source_grounded_candidate_meaning": True,
        "represents_competing_candidate_separation": True,
        "represents_missing_support": True,
        "represents_no_action_safe_candidate_state": True,
        "references_slice7_meaning_and_law_trace_boundaries_only": True,
        "references_slice8_concept_boundaries_only": True,
        "references_slice9_predicate_role_boundaries_only": True,
        "references_slice10_gate_boundaries_only": True,
        "live_runtime_interpretation": False,
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
class CandidateMeaningBoundaryRecord:
    candidate_meaning_id: str
    candidate_key: str
    source_expression_id: str
    derived_structure_id: str
    candidate_kind: str
    candidate_state: str
    upstream_boundary_refs: Tuple[str, ...] = ()
    competing_candidate_group_id: str = ""
    missing_support_refs: Tuple[str, ...] = ()
    support_status_boundary: str = "support_referenced_boundary"
    no_action_safe: bool = True
    provenance_tag: str = "slice11_boundary"
    version_tag: str = "v1"
    live_runtime_interpretation: bool = False
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
            "candidate_key": self.candidate_key,
            "source_expression_id": self.source_expression_id,
            "derived_structure_id": self.derived_structure_id,
            "candidate_kind": self.candidate_kind,
            "candidate_state": self.candidate_state,
            "upstream_boundary_refs": self.upstream_boundary_refs,
            "competing_candidate_group_id": self.competing_candidate_group_id,
            "missing_support_refs": self.missing_support_refs,
            "support_status_boundary": self.support_status_boundary,
            "no_action_safe": self.no_action_safe,
            "provenance_tag": self.provenance_tag,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_boundary_id("candidate_meaning", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["candidate_meaning_id"] = self.candidate_meaning_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def validate_candidate_meaning_record(record: CandidateMeaningBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.candidate_kind not in ALLOWED_CANDIDATE_KINDS:
        issues.append(_issue("candidate_kind", "unsupported_candidate_kind"))
    if record.candidate_state not in ALLOWED_CANDIDATE_STATES:
        issues.append(_issue("candidate_state", "unsupported_candidate_state"))
    if record.support_status_boundary not in ALLOWED_SUPPORT_STATUS:
        issues.append(_issue("support_status_boundary", "unsupported_support_status_boundary"))
    if not record.candidate_key:
        issues.append(_issue("candidate_key", "required"))
    if not record.source_expression_id:
        issues.append(_issue("source_expression_id", "required"))
    if not record.derived_structure_id:
        issues.append(_issue("derived_structure_id", "required"))
    if not _tuple_of_text(record.upstream_boundary_refs, allow_empty=False):
        issues.append(_issue("upstream_boundary_refs", "at_least_one_upstream_boundary_ref_required"))
    if not _tuple_of_text(record.missing_support_refs):
        issues.append(_issue("missing_support_refs", "must_be_tuple_of_text_boundary_refs"))
    if record.no_action_safe is not True:
        issues.append(_issue("no_action_safe", "must_remain_true"))
    if record.candidate_meaning_id != record.expected_id():
        issues.append(_issue("candidate_meaning_id", "does_not_match_canonical_body"))
    _check_false_only(record, CANDIDATE_FALSE_ONLY_FIELDS, issues, "slice11")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_candidate_meaning_record() -> CandidateMeaningBoundaryRecord:
    body = {
        "candidate_key": "candidate_reply_requires_time_boundary",
        "source_expression_id": "src_expr:demo",
        "derived_structure_id": "derived_struct:demo",
        "candidate_kind": "source_grounded_candidate_boundary",
        "candidate_state": "candidate_constructed_boundary",
        "upstream_boundary_refs": (
            "meaning_object:demo",
            "law_trace:demo",
            "concept_boundary:appointment_time",
            "predicate_frame:draft_reply_boundary",
            "gate_boundary:clarification_required",
        ),
        "competing_candidate_group_id": "candidate_group:demo",
        "missing_support_refs": ("missing_support:appointment_time",),
        "support_status_boundary": "support_missing_boundary",
        "no_action_safe": True,
        "provenance_tag": "slice11_demo_boundary",
        "version_tag": "v1",
    }
    return CandidateMeaningBoundaryRecord(candidate_meaning_id=stable_boundary_id("candidate_meaning", body), **body)


def demo_no_action_candidate_record() -> CandidateMeaningBoundaryRecord:
    body = {
        "candidate_key": "candidate_no_action_safe_boundary",
        "source_expression_id": "src_expr:demo",
        "derived_structure_id": "derived_struct:demo",
        "candidate_kind": "no_action_safe_candidate_boundary",
        "candidate_state": "no_action_safe_boundary",
        "upstream_boundary_refs": ("gate_boundary:blocked_action",),
        "competing_candidate_group_id": "candidate_group:demo",
        "missing_support_refs": (),
        "support_status_boundary": "support_referenced_boundary",
        "no_action_safe": True,
        "provenance_tag": "slice11_demo_boundary",
        "version_tag": "v1",
    }
    return CandidateMeaningBoundaryRecord(candidate_meaning_id=stable_boundary_id("candidate_meaning", body), **body)


def demo_unsupported_candidate_record() -> CandidateMeaningBoundaryRecord:
    body = {
        "candidate_key": "candidate_unsupported_boundary",
        "source_expression_id": "src_expr:unknown",
        "derived_structure_id": "derived_struct:unknown",
        "candidate_kind": "unsupported_candidate_boundary",
        "candidate_state": "unsupported_boundary",
        "upstream_boundary_refs": ("gate_state:unsupported",),
        "competing_candidate_group_id": "",
        "missing_support_refs": ("missing_support:unsupported_language",),
        "support_status_boundary": "support_missing_boundary",
        "no_action_safe": True,
        "provenance_tag": "slice11_demo_boundary",
        "version_tag": "v1",
    }
    return CandidateMeaningBoundaryRecord(candidate_meaning_id=stable_boundary_id("candidate_meaning", body), **body)
