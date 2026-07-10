from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    ALLOWED_SELECTED_MEANING_STATUSES,
    ALLOWED_TEMPLATE_IDS,
    STATUS_ALLOWED_PREVIEW_KINDS,
    TEMPLATE_BY_PREVIEW_KIND,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    check_false_only,
    issue,
    nonempty_text,
    stable_expression_id,
    tuple_of_text,
    unique_tuple,
)


@dataclass(frozen=True)
class ExpressionPlanRecord:
    expression_plan_id: str
    expression_source_id: str
    preservation_contract_id: str
    selected_meaning_id: str
    selected_meaning_status: str
    preview_kind: str
    template_id: str
    clause_sequence: Tuple[str, ...]
    source_refs: Tuple[str, ...]
    required_qualifier_markers: Tuple[str, ...]
    forbidden_transformations: Tuple[str, ...]
    plan_status: str = "deterministic_unapproved_expression_plan"
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
            "selected_meaning_id": self.selected_meaning_id,
            "selected_meaning_status": self.selected_meaning_status,
            "preview_kind": self.preview_kind,
            "template_id": self.template_id,
            "clause_sequence": self.clause_sequence,
            "source_refs": self.source_refs,
            "required_qualifier_markers": self.required_qualifier_markers,
            "forbidden_transformations": self.forbidden_transformations,
            "plan_status": self.plan_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_expression_id("expression-plan", self.canonical_body())


def build_expression_plan_record(
    *,
    expression_source_id: str,
    preservation_contract_id: str,
    selected_meaning_id: str,
    selected_meaning_status: str,
    preview_kind: str,
    clause_sequence: Tuple[str, ...],
    source_refs: Tuple[str, ...],
    required_qualifier_markers: Tuple[str, ...],
    forbidden_transformations: Tuple[str, ...],
) -> ExpressionPlanRecord:
    template_id = TEMPLATE_BY_PREVIEW_KIND.get(preview_kind, "unsupported-template")
    body = {
        "expression_source_id": expression_source_id,
        "preservation_contract_id": preservation_contract_id,
        "selected_meaning_id": selected_meaning_id,
        "selected_meaning_status": selected_meaning_status,
        "preview_kind": preview_kind,
        "template_id": template_id,
        "clause_sequence": clause_sequence,
        "source_refs": source_refs,
        "required_qualifier_markers": required_qualifier_markers,
        "forbidden_transformations": forbidden_transformations,
        "plan_status": "deterministic_unapproved_expression_plan",
        "version_tag": "v1",
    }
    return ExpressionPlanRecord(
        expression_plan_id=stable_expression_id("expression-plan", body), **body
    )


def validate_expression_plan_record(record: ExpressionPlanRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "expression_plan_id",
        "expression_source_id",
        "preservation_contract_id",
        "selected_meaning_id",
        "selected_meaning_status",
        "preview_kind",
        "template_id",
        "plan_status",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.selected_meaning_status not in ALLOWED_SELECTED_MEANING_STATUSES:
        issues.append(issue("selected_meaning_status", "unsupported_selected_meaning_status"))
    allowed = STATUS_ALLOWED_PREVIEW_KINDS.get(record.selected_meaning_status, ())
    if record.preview_kind not in allowed:
        issues.append(issue("preview_kind", "preview_kind_not_allowed_for_selection_status"))
    if record.template_id not in ALLOWED_TEMPLATE_IDS:
        issues.append(issue("template_id", "unsupported_template_id"))
    if TEMPLATE_BY_PREVIEW_KIND.get(record.preview_kind) != record.template_id:
        issues.append(issue("template_id", "template_does_not_match_preview_kind"))
    if record.plan_status != "deterministic_unapproved_expression_plan":
        issues.append(issue("plan_status", "must_remain_unapproved_plan"))
    for field_name in (
        "clause_sequence",
        "source_refs",
        "required_qualifier_markers",
        "forbidden_transformations",
    ):
        value = getattr(record, field_name)
        if not tuple_of_text(value, allow_empty=False):
            issues.append(issue(field_name, "nonempty_tuple_of_text_required"))
        elif not unique_tuple(value):
            issues.append(issue(field_name, "duplicate_entries_not_allowed"))
    if record.expression_plan_id != record.expected_id():
        issues.append(issue("expression_plan_id", "stable_identifier_mismatch"))
    check_false_only(record, issues, "expression_plan")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_expression_plan_record(
    *,
    expression_source_id: str = "expression-source:demo",
    preservation_contract_id: str = "expression-preservation:demo",
    selected_meaning_id: str = "selected-meaning:demo",
    selected_meaning_status: str = "selected_meaning_boundary_recorded",
    preview_kind: str = "explanation_preview",
) -> ExpressionPlanRecord:
    body = (
        "According to the operator, the system may proceed only if checksum "
        "verification passes; it is not authorized while uncertainty remains."
    )
    return build_expression_plan_record(
        expression_source_id=expression_source_id,
        preservation_contract_id=preservation_contract_id,
        selected_meaning_id=selected_meaning_id,
        selected_meaning_status=selected_meaning_status,
        preview_kind=preview_kind,
        clause_sequence=(body,),
        source_refs=("meaning-object:demo", "selected-meaning:demo"),
        required_qualifier_markers=(
            "According to the operator",
            "may proceed",
            "only if checksum verification passes",
            "not authorized",
            "uncertainty remains",
        ),
        forbidden_transformations=(
            "remove_negation",
            "remove_condition",
            "strengthen_modality",
            "erase_attribution",
            "widen_scope",
            "hide_refusal_relevance",
            "erase_uncertainty",
        ),
    )
