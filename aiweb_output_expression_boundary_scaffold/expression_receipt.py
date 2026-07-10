from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    REQUIRED_EXPRESSION_LAWS,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    check_false_only,
    issue,
    nonempty_text,
    stable_expression_id,
    tuple_of_text,
)
from .fidelity import ExpressionFidelityRecord, validate_expression_fidelity_record

RECEIPT_EFFECT = (
    "record_only_unapproved_no_proof_no_authority_no_acceptance_no_permission_"
    "no_delivery_no_execution"
)
ALLOWED_RECEIPT_STATUSES = (
    "expression_receipt_recorded_boundary",
    "expression_receipt_blocked_boundary",
)


@dataclass(frozen=True)
class ExpressionReceiptRecord:
    expression_receipt_id: str
    expression_source_id: str
    expression_plan_id: str
    expression_preview_id: str
    expression_fidelity_id: str
    receipt_status: str
    receipt_effect: str
    fidelity_hard_gate_pass: bool
    preview_status: str
    required_law_refs: Tuple[str, ...]
    audit_note: str
    version_tag: str = "v1"

    live_runtime_behavior: bool = False
    live_runtime_interpretation: bool = False
    truth_decision: bool = False
    proof_claim: bool = False
    authority_grant: bool = False
    acceptance_effect: bool = False
    permission_grant: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    execution_authority: bool = False
    output_approval: bool = False
    user_facing_output_authorized: bool = False
    memory_write: bool = False
    memory_authority: bool = False
    evidence_validation: bool = False
    corpus_authority: bool = False
    external_truth_authority: bool = False
    external_resource_admission: bool = False
    runtime_promotion: bool = False
    resource_fetch: bool = False
    resource_download: bool = False
    resource_ingestion: bool = False
    resource_parsing: bool = False
    resource_indexing: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False
    similarity_authority: bool = False
    embedding_index_creation: bool = False
    rag_execution: bool = False
    training_authority: bool = False
    gp014_supersession: bool = False
    gp015_repair: bool = False
    gp015r1_installation: bool = False
    release_authority: bool = False
    production_readiness: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "expression_source_id": self.expression_source_id,
            "expression_plan_id": self.expression_plan_id,
            "expression_preview_id": self.expression_preview_id,
            "expression_fidelity_id": self.expression_fidelity_id,
            "receipt_status": self.receipt_status,
            "receipt_effect": self.receipt_effect,
            "fidelity_hard_gate_pass": self.fidelity_hard_gate_pass,
            "preview_status": self.preview_status,
            "required_law_refs": self.required_law_refs,
            "audit_note": self.audit_note,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_expression_id("expression-receipt", self.canonical_body())


def build_expression_receipt_record(
    fidelity: ExpressionFidelityRecord,
    *,
    preview_status: str,
    audit_note: str,
) -> ExpressionReceiptRecord:
    receipt_status = (
        "expression_receipt_recorded_boundary"
        if fidelity.hard_gate_pass
        else "expression_receipt_blocked_boundary"
    )
    body = {
        "expression_source_id": fidelity.expression_source_id,
        "expression_plan_id": fidelity.expression_plan_id,
        "expression_preview_id": fidelity.expression_preview_id,
        "expression_fidelity_id": fidelity.expression_fidelity_id,
        "receipt_status": receipt_status,
        "receipt_effect": RECEIPT_EFFECT,
        "fidelity_hard_gate_pass": fidelity.hard_gate_pass,
        "preview_status": preview_status,
        "required_law_refs": REQUIRED_EXPRESSION_LAWS,
        "audit_note": audit_note,
        "version_tag": "v1",
    }
    return ExpressionReceiptRecord(
        expression_receipt_id=stable_expression_id("expression-receipt", body), **body
    )


def validate_expression_receipt_record(record: ExpressionReceiptRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "expression_receipt_id",
        "expression_source_id",
        "expression_plan_id",
        "expression_preview_id",
        "expression_fidelity_id",
        "receipt_status",
        "receipt_effect",
        "preview_status",
        "audit_note",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.receipt_status not in ALLOWED_RECEIPT_STATUSES:
        issues.append(issue("receipt_status", "unsupported_receipt_status"))
    expected_status = (
        "expression_receipt_recorded_boundary"
        if record.fidelity_hard_gate_pass
        else "expression_receipt_blocked_boundary"
    )
    if record.receipt_status != expected_status:
        issues.append(issue("receipt_status", "must_follow_fidelity_hard_gate"))
    if record.receipt_effect != RECEIPT_EFFECT:
        issues.append(issue("receipt_effect", "must_remain_record_only_non_authority"))
    if record.preview_status != "unapproved_expression_preview_boundary":
        issues.append(issue("preview_status", "only_unapproved_preview_may_be_receipted"))
    if not tuple_of_text(record.required_law_refs, allow_empty=False):
        issues.append(issue("required_law_refs", "nonempty_tuple_required"))
    for law in REQUIRED_EXPRESSION_LAWS:
        if law not in record.required_law_refs:
            issues.append(issue("required_law_refs", f"missing_{law}"))
    if record.expression_receipt_id != record.expected_id():
        issues.append(issue("expression_receipt_id", "stable_identifier_mismatch"))
    check_false_only(record, issues, "expression_receipt")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))
