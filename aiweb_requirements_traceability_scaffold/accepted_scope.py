from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    _canonicalize,
    check_false_only,
    issue,
    stable_traceability_id,
    tuple_of_text,
)

ALLOWED_SCOPE_STATUS = (
    "accepted_scope_represented_only",
    "boundary_only_scope",
    "no_runtime_effect_scope",
)

ALLOWED_ROLLBACK_TRIGGER_STATUS = (
    "rollback_trigger_represented_only",
    "rollback_required_on_test_failure",
    "rollback_required_on_verifier_failure",
    "rollback_required_on_scope_widening",
)


@dataclass(frozen=True)
class AcceptedScopeRecord:
    accepted_scope_id: str
    slice_ref: str
    accepted_scope_status: str
    allowed_scope_items: Tuple[str, ...]
    blocked_scope_items: Tuple[str, ...]
    upstream_scope_refs: Tuple[str, ...]
    version_tag: str = "v1"
    live_runtime_behavior: bool = False
    capability_acceptance: bool = False
    verifier_gate_replacement: bool = False
    result_packet_bypass: bool = False
    accepted_scope_widening: bool = False
    release_authority: bool = False
    production_readiness: bool = False
    delivery_action: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False
    final_meaning_selection: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    live_clarification: bool = False
    user_facing_question_emission: bool = False
    gp014_supersession: bool = False
    gp015_repair: bool = False
    gp015r1_installation: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "slice_ref": self.slice_ref,
            "accepted_scope_status": self.accepted_scope_status,
            "allowed_scope_items": self.allowed_scope_items,
            "blocked_scope_items": self.blocked_scope_items,
            "upstream_scope_refs": self.upstream_scope_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_traceability_id("accepted_scope", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["accepted_scope_id"] = self.accepted_scope_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


@dataclass(frozen=True)
class RollbackTriggerRecord:
    rollback_trigger_id: str
    slice_ref: str
    trigger_status: str
    trigger_conditions: Tuple[str, ...]
    backup_marker_ref: str
    rollback_script_ref: str
    version_tag: str = "v1"
    live_runtime_behavior: bool = False
    capability_acceptance: bool = False
    verifier_gate_replacement: bool = False
    result_packet_bypass: bool = False
    accepted_scope_widening: bool = False
    release_authority: bool = False
    production_readiness: bool = False
    delivery_action: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False
    final_meaning_selection: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    live_clarification: bool = False
    user_facing_question_emission: bool = False
    gp014_supersession: bool = False
    gp015_repair: bool = False
    gp015r1_installation: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "slice_ref": self.slice_ref,
            "trigger_status": self.trigger_status,
            "trigger_conditions": self.trigger_conditions,
            "backup_marker_ref": self.backup_marker_ref,
            "rollback_script_ref": self.rollback_script_ref,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_traceability_id("rollback_trigger", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["rollback_trigger_id"] = self.rollback_trigger_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_accepted_scope_record(
    *,
    slice_ref: str,
    accepted_scope_status: str,
    allowed_scope_items: Tuple[str, ...],
    blocked_scope_items: Tuple[str, ...],
    upstream_scope_refs: Tuple[str, ...],
    version_tag: str = "v1",
) -> AcceptedScopeRecord:
    body = {
        "slice_ref": slice_ref,
        "accepted_scope_status": accepted_scope_status,
        "allowed_scope_items": allowed_scope_items,
        "blocked_scope_items": blocked_scope_items,
        "upstream_scope_refs": upstream_scope_refs,
        "version_tag": version_tag,
    }
    return AcceptedScopeRecord(accepted_scope_id=stable_traceability_id("accepted_scope", body), **body)


def build_rollback_trigger_record(
    *,
    slice_ref: str,
    trigger_status: str,
    trigger_conditions: Tuple[str, ...],
    backup_marker_ref: str,
    rollback_script_ref: str,
    version_tag: str = "v1",
) -> RollbackTriggerRecord:
    body = {
        "slice_ref": slice_ref,
        "trigger_status": trigger_status,
        "trigger_conditions": trigger_conditions,
        "backup_marker_ref": backup_marker_ref,
        "rollback_script_ref": rollback_script_ref,
        "version_tag": version_tag,
    }
    return RollbackTriggerRecord(rollback_trigger_id=stable_traceability_id("rollback_trigger", body), **body)


def validate_accepted_scope_record(record: AcceptedScopeRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record.slice_ref, str) or not record.slice_ref.strip():
        issues.append(issue("slice_ref", "required_non_empty_text"))
    if record.accepted_scope_status not in ALLOWED_SCOPE_STATUS:
        issues.append(issue("accepted_scope_status", "unsupported_scope_status"))
    if not tuple_of_text(record.allowed_scope_items, allow_empty=False):
        issues.append(issue("allowed_scope_items", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.blocked_scope_items, allow_empty=False):
        issues.append(issue("blocked_scope_items", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.upstream_scope_refs, allow_empty=False):
        issues.append(issue("upstream_scope_refs", "required_non_empty_text_tuple"))
    if record.accepted_scope_id != record.expected_id():
        issues.append(issue("accepted_scope_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "accepted_scope")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def validate_rollback_trigger_record(record: RollbackTriggerRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record.slice_ref, str) or not record.slice_ref.strip():
        issues.append(issue("slice_ref", "required_non_empty_text"))
    if record.trigger_status not in ALLOWED_ROLLBACK_TRIGGER_STATUS:
        issues.append(issue("trigger_status", "unsupported_rollback_trigger_status"))
    if not tuple_of_text(record.trigger_conditions, allow_empty=False):
        issues.append(issue("trigger_conditions", "required_non_empty_text_tuple"))
    if not isinstance(record.backup_marker_ref, str) or not record.backup_marker_ref.strip():
        issues.append(issue("backup_marker_ref", "required_non_empty_text"))
    if not isinstance(record.rollback_script_ref, str) or not record.rollback_script_ref.strip():
        issues.append(issue("rollback_script_ref", "required_non_empty_text"))
    if record.rollback_trigger_id != record.expected_id():
        issues.append(issue("rollback_trigger_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "rollback_trigger")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_accepted_scope_record() -> AcceptedScopeRecord:
    return build_accepted_scope_record(
        slice_ref="Slice13",
        accepted_scope_status="boundary_only_scope",
        allowed_scope_items=("traceability_records", "requirement_crosswalk_records", "receipt_references"),
        blocked_scope_items=("capability_acceptance", "scope_widening", "result_packet_bypass", "live_runtime_behavior"),
        upstream_scope_refs=("Slice1", "Slice2", "Slice3", "Slice4", "Slice5", "Slice6", "Slice7", "Slice8", "Slice9", "Slice10", "Slice11", "Slice12"),
    )


def demo_rollback_trigger_record() -> RollbackTriggerRecord:
    return build_rollback_trigger_record(
        slice_ref="Slice13",
        trigger_status="rollback_required_on_verifier_failure",
        trigger_conditions=("behavior_test_failure", "verifier_failure", "unexpected_git_status", "frozen_path_change"),
        backup_marker_ref="/home/nic/Downloads/AIWEB_SLICE13_BACKUP_LATEST.txt",
        rollback_script_ref="scripts/rollback_slice13.sh",
    )
