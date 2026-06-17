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

ALLOWED_RECEIPT_STATUS = (
    "receipt_represented_only",
    "result_packet_required",
    "decision_record_required",
    "post_commit_packet_required",
)


@dataclass(frozen=True)
class TraceabilityReceiptRecord:
    receipt_id: str
    requirement_ref: str
    crosswalk_ref: str
    verifier_gate_ref: str
    result_packet_ref: str
    decision_record_ref: str
    evidence_receipt_refs: Tuple[str, ...]
    rollback_trigger_ref: str
    accepted_scope_ref: str
    receipt_status: str = "receipt_represented_only"
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
            "requirement_ref": self.requirement_ref,
            "crosswalk_ref": self.crosswalk_ref,
            "verifier_gate_ref": self.verifier_gate_ref,
            "result_packet_ref": self.result_packet_ref,
            "decision_record_ref": self.decision_record_ref,
            "evidence_receipt_refs": self.evidence_receipt_refs,
            "rollback_trigger_ref": self.rollback_trigger_ref,
            "accepted_scope_ref": self.accepted_scope_ref,
            "receipt_status": self.receipt_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_traceability_id("traceability_receipt", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["receipt_id"] = self.receipt_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_traceability_receipt_record(
    *,
    requirement_ref: str,
    crosswalk_ref: str,
    verifier_gate_ref: str,
    result_packet_ref: str,
    decision_record_ref: str,
    evidence_receipt_refs: Tuple[str, ...],
    rollback_trigger_ref: str,
    accepted_scope_ref: str,
    receipt_status: str = "receipt_represented_only",
    version_tag: str = "v1",
) -> TraceabilityReceiptRecord:
    body = {
        "requirement_ref": requirement_ref,
        "crosswalk_ref": crosswalk_ref,
        "verifier_gate_ref": verifier_gate_ref,
        "result_packet_ref": result_packet_ref,
        "decision_record_ref": decision_record_ref,
        "evidence_receipt_refs": evidence_receipt_refs,
        "rollback_trigger_ref": rollback_trigger_ref,
        "accepted_scope_ref": accepted_scope_ref,
        "receipt_status": receipt_status,
        "version_tag": version_tag,
    }
    return TraceabilityReceiptRecord(
        receipt_id=stable_traceability_id("traceability_receipt", body),
        **body,
    )


def validate_traceability_receipt_record(record: TraceabilityReceiptRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "requirement_ref",
        "crosswalk_ref",
        "verifier_gate_ref",
        "result_packet_ref",
        "decision_record_ref",
        "rollback_trigger_ref",
        "accepted_scope_ref",
    ):
        if not isinstance(getattr(record, field_name), str) or not getattr(record, field_name).strip():
            issues.append(issue(field_name, "required_non_empty_text"))
    if not tuple_of_text(record.evidence_receipt_refs, allow_empty=False):
        issues.append(issue("evidence_receipt_refs", "required_non_empty_text_tuple"))
    if record.receipt_status not in ALLOWED_RECEIPT_STATUS:
        issues.append(issue("receipt_status", "unsupported_receipt_status"))
    if record.receipt_id != record.expected_id():
        issues.append(issue("receipt_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "traceability_receipt")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_traceability_receipt_record() -> TraceabilityReceiptRecord:
    return build_traceability_receipt_record(
        requirement_ref="requirement_identity:demo-slice13",
        crosswalk_ref="requirement_test_crosswalk:demo-slice13",
        verifier_gate_ref="scripts/aiweb_slice13_requirements_traceability_verify.py",
        result_packet_ref="AIWEB_SLICE13_RESULT_PACKET_required_before_acceptance",
        decision_record_ref="AIWEB_SLICE13_DECISION_RECORD_required_before_commit",
        evidence_receipt_refs=("behavior_test_exit_status", "verifier_exit_status", "file_hash_receipt"),
        rollback_trigger_ref="rollback_trigger:slice13-failure",
        accepted_scope_ref="accepted_scope:slice13-boundary-only",
    )
