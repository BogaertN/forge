from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import REQUIRED_SELECTION_LAWS, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_selection_id, tuple_of_text

ALLOWED_RECEIPT_STATUSES = (
    "selection_receipt_recorded_boundary",
    "selection_receipt_held_boundary",
    "selection_receipt_blocked_boundary",
)

ALLOWED_RECEIPT_EFFECTS = (
    "record_only_no_truth_no_permission_no_delivery_no_execution",
    "held_only_no_downstream_authority",
)


@dataclass(frozen=True)
class SelectionReceiptRecord:
    selection_receipt_id: str
    selected_meaning_id: str
    selection_trace_id: str
    receipt_status: str
    receipt_effect: str
    required_law_refs: Tuple[str, ...]
    downstream_block_refs: Tuple[str, ...]
    audit_note: str
    version_tag: str = "v1"

    live_runtime_behavior: bool = False
    live_runtime_interpretation: bool = False
    selection_as_truth: bool = False
    selection_as_permission: bool = False
    selection_as_delivery: bool = False
    selection_as_execution: bool = False
    selection_finalization: bool = False
    final_meaning_selection: bool = False
    truth_decision: bool = False
    permission_grant: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    execution_authority: bool = False
    output_rendering: bool = False
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
    live_clarification: bool = False
    user_facing_question_emission: bool = False
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
            "selected_meaning_id": self.selected_meaning_id,
            "selection_trace_id": self.selection_trace_id,
            "receipt_status": self.receipt_status,
            "receipt_effect": self.receipt_effect,
            "required_law_refs": self.required_law_refs,
            "downstream_block_refs": self.downstream_block_refs,
            "audit_note": self.audit_note,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_selection_id("selection-receipt", self.canonical_body())


def build_selection_receipt_record(
    *,
    selected_meaning_id: str,
    selection_trace_id: str,
    receipt_status: str,
    receipt_effect: str,
    required_law_refs: Tuple[str, ...],
    downstream_block_refs: Tuple[str, ...],
    audit_note: str,
) -> SelectionReceiptRecord:
    body = {
        "selected_meaning_id": selected_meaning_id,
        "selection_trace_id": selection_trace_id,
        "receipt_status": receipt_status,
        "receipt_effect": receipt_effect,
        "required_law_refs": required_law_refs,
        "downstream_block_refs": downstream_block_refs,
        "audit_note": audit_note,
        "version_tag": "v1",
    }
    return SelectionReceiptRecord(selection_receipt_id=stable_selection_id("selection-receipt", body), **body)


def validate_selection_receipt_record(record: SelectionReceiptRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("selection_receipt_id", "selected_meaning_id", "selection_trace_id", "receipt_status", "receipt_effect", "audit_note"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.receipt_status not in ALLOWED_RECEIPT_STATUSES:
        issues.append(issue("receipt_status", "unsupported_receipt_status"))
    if record.receipt_effect not in ALLOWED_RECEIPT_EFFECTS:
        issues.append(issue("receipt_effect", "unsupported_receipt_effect"))
    if not tuple_of_text(record.required_law_refs, allow_empty=False):
        issues.append(issue("required_law_refs", "must_be_nonempty_tuple_of_text"))
    for law in REQUIRED_SELECTION_LAWS[:4]:
        if law not in record.required_law_refs:
            issues.append(issue("required_law_refs", f"missing_{law}"))
    if not tuple_of_text(record.downstream_block_refs, allow_empty=False):
        issues.append(issue("downstream_block_refs", "must_be_nonempty_tuple_of_text"))
    for required_block in ("truth_decision", "permission_grant", "delivery_action", "execution_authority"):
        if required_block not in record.downstream_block_refs:
            issues.append(issue("downstream_block_refs", f"missing_{required_block}"))
    if record.selection_receipt_id != record.expected_id():
        issues.append(issue("selection_receipt_id", "stable_identifier_mismatch"))
    check_false_only(record, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "selection_receipt")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_selection_receipt_record() -> SelectionReceiptRecord:
    return build_selection_receipt_record(
        selected_meaning_id="selected-meaning:demo",
        selection_trace_id="selection-trace:demo",
        receipt_status="selection_receipt_recorded_boundary",
        receipt_effect="record_only_no_truth_no_permission_no_delivery_no_execution",
        required_law_refs=REQUIRED_SELECTION_LAWS,
        downstream_block_refs=("truth_decision", "permission_grant", "delivery_action", "execution_authority", "memory_write", "evidence_validation", "tool_invocation"),
        audit_note="Receipt records selected-meaning boundary custody only and has no downstream effect.",
    )
