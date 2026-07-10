from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    NON_AUTHORITY_DISCLAIMER,
    PREFIX_BY_PREVIEW_KIND,
    STATUS_ALLOWED_PREVIEW_KINDS,
    TEMPLATE_BY_PREVIEW_KIND,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    check_false_only,
    issue,
    nonempty_text,
    stable_expression_id,
    text_sha256,
    tuple_of_text,
    unique_tuple,
)
from .expression_plan import ExpressionPlanRecord, validate_expression_plan_record


@dataclass(frozen=True)
class ExpressionPreviewRecord:
    expression_preview_id: str
    expression_source_id: str
    preservation_contract_id: str
    expression_plan_id: str
    selected_meaning_id: str
    selected_meaning_status: str
    preview_kind: str
    template_id: str
    preview_text: str
    preview_text_hash: str
    preserved_qualifier_markers: Tuple[str, ...]
    preview_status: str = "unapproved_expression_preview_boundary"
    disclaimer: str = NON_AUTHORITY_DISCLAIMER
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
            "preservation_contract_id": self.preservation_contract_id,
            "expression_plan_id": self.expression_plan_id,
            "selected_meaning_id": self.selected_meaning_id,
            "selected_meaning_status": self.selected_meaning_status,
            "preview_kind": self.preview_kind,
            "template_id": self.template_id,
            "preview_text": self.preview_text,
            "preview_text_hash": self.preview_text_hash,
            "preserved_qualifier_markers": self.preserved_qualifier_markers,
            "preview_status": self.preview_status,
            "disclaimer": self.disclaimer,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_expression_id("expression-preview", self.canonical_body())


def render_expression_preview(plan: ExpressionPlanRecord) -> ExpressionPreviewRecord:
    report = validate_expression_plan_record(plan)
    if not report.ok:
        reasons = ",".join(item.reason for item in report.issues)
        raise ValueError(f"invalid_expression_plan:{reasons}")
    prefix = PREFIX_BY_PREVIEW_KIND[plan.preview_kind]
    body = " ".join(clause.strip() for clause in plan.clause_sequence)
    preview_text = f"{prefix}: {body} {NON_AUTHORITY_DISCLAIMER}"
    body_record = {
        "expression_source_id": plan.expression_source_id,
        "preservation_contract_id": plan.preservation_contract_id,
        "expression_plan_id": plan.expression_plan_id,
        "selected_meaning_id": plan.selected_meaning_id,
        "selected_meaning_status": plan.selected_meaning_status,
        "preview_kind": plan.preview_kind,
        "template_id": plan.template_id,
        "preview_text": preview_text,
        "preview_text_hash": text_sha256(preview_text),
        "preserved_qualifier_markers": plan.required_qualifier_markers,
        "preview_status": "unapproved_expression_preview_boundary",
        "disclaimer": NON_AUTHORITY_DISCLAIMER,
        "version_tag": "v1",
    }
    return ExpressionPreviewRecord(
        expression_preview_id=stable_expression_id("expression-preview", body_record),
        **body_record,
    )


def validate_expression_preview_record(record: ExpressionPreviewRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "expression_preview_id",
        "expression_source_id",
        "preservation_contract_id",
        "expression_plan_id",
        "selected_meaning_id",
        "selected_meaning_status",
        "preview_kind",
        "template_id",
        "preview_text",
        "preview_text_hash",
        "preview_status",
        "disclaimer",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    allowed_kinds = STATUS_ALLOWED_PREVIEW_KINDS.get(record.selected_meaning_status, ())
    if record.preview_kind not in allowed_kinds:
        issues.append(issue("preview_kind", "preview_kind_not_allowed_for_selection_status"))
    if TEMPLATE_BY_PREVIEW_KIND.get(record.preview_kind) != record.template_id:
        issues.append(issue("template_id", "template_does_not_match_preview_kind"))
    if record.preview_status != "unapproved_expression_preview_boundary":
        issues.append(issue("preview_status", "must_remain_unapproved_boundary_preview"))
    if record.disclaimer != NON_AUTHORITY_DISCLAIMER:
        issues.append(issue("disclaimer", "exact_non_authority_disclaimer_required"))
    if record.disclaimer not in record.preview_text:
        issues.append(issue("preview_text", "non_authority_disclaimer_missing"))
    if record.preview_text_hash != text_sha256(record.preview_text):
        issues.append(issue("preview_text_hash", "preview_hash_mismatch"))
    if not tuple_of_text(record.preserved_qualifier_markers, allow_empty=False):
        issues.append(issue("preserved_qualifier_markers", "nonempty_tuple_required"))
    elif not unique_tuple(record.preserved_qualifier_markers):
        issues.append(issue("preserved_qualifier_markers", "duplicate_entries_not_allowed"))
    if record.expression_preview_id != record.expected_id():
        issues.append(issue("expression_preview_id", "stable_identifier_mismatch"))
    check_false_only(record, issues, "expression_preview")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))
