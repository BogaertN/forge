from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Dict, Tuple

from .core import (
    ALLOWED_SELECTED_MEANING_STATUSES,
    EXPRESSION_FALSE_ONLY_FIELDS,
    REQUIRED_EXPRESSION_LAWS,
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

_BINDING_RE = re.compile(r"^.+#sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class ExpressionSourceRecord:
    expression_source_id: str
    selected_meaning_id: str
    candidate_meaning_id: str
    selection_reference_id: str
    selection_basis_id: str
    selection_constraint_id: str
    selection_trace_id: str
    selection_receipt_id: str
    selected_meaning_status: str
    selection_scope: str
    confidence_boundary: str
    meaning_object_id: str
    meaning_content_hash: str
    normalized_text_snapshot: str
    source_expression_ref: str
    upstream_record_bindings: Tuple[str, ...]
    uncertainty_refs: Tuple[str, ...]
    required_law_refs: Tuple[str, ...]
    comparison_refs: Tuple[str, ...]
    non_selected_candidate_refs: Tuple[str, ...]
    downstream_block_refs: Tuple[str, ...]
    attribution_refs: Tuple[str, ...]
    scope_refs: Tuple[str, ...]
    refusal_refs: Tuple[str, ...]
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
            "selected_meaning_id": self.selected_meaning_id,
            "candidate_meaning_id": self.candidate_meaning_id,
            "selection_reference_id": self.selection_reference_id,
            "selection_basis_id": self.selection_basis_id,
            "selection_constraint_id": self.selection_constraint_id,
            "selection_trace_id": self.selection_trace_id,
            "selection_receipt_id": self.selection_receipt_id,
            "selected_meaning_status": self.selected_meaning_status,
            "selection_scope": self.selection_scope,
            "confidence_boundary": self.confidence_boundary,
            "meaning_object_id": self.meaning_object_id,
            "meaning_content_hash": self.meaning_content_hash,
            "normalized_text_snapshot": self.normalized_text_snapshot,
            "source_expression_ref": self.source_expression_ref,
            "upstream_record_bindings": self.upstream_record_bindings,
            "uncertainty_refs": self.uncertainty_refs,
            "required_law_refs": self.required_law_refs,
            "comparison_refs": self.comparison_refs,
            "non_selected_candidate_refs": self.non_selected_candidate_refs,
            "downstream_block_refs": self.downstream_block_refs,
            "attribution_refs": self.attribution_refs,
            "scope_refs": self.scope_refs,
            "refusal_refs": self.refusal_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_expression_id("expression-source", self.canonical_body())


def build_expression_source_record(
    *,
    selected_meaning_id: str,
    candidate_meaning_id: str,
    selection_reference_id: str,
    selection_basis_id: str,
    selection_constraint_id: str,
    selection_trace_id: str,
    selection_receipt_id: str,
    selected_meaning_status: str,
    selection_scope: str,
    confidence_boundary: str,
    meaning_object_id: str,
    normalized_text_snapshot: str,
    source_expression_ref: str,
    upstream_record_bindings: Tuple[str, ...],
    uncertainty_refs: Tuple[str, ...],
    required_law_refs: Tuple[str, ...] = REQUIRED_EXPRESSION_LAWS,
    comparison_refs: Tuple[str, ...] = (),
    non_selected_candidate_refs: Tuple[str, ...] = (),
    downstream_block_refs: Tuple[str, ...] = (),
    attribution_refs: Tuple[str, ...] = (),
    scope_refs: Tuple[str, ...] = (),
    refusal_refs: Tuple[str, ...] = (),
) -> ExpressionSourceRecord:
    meaning_content_hash = text_sha256(normalized_text_snapshot)
    body = {
        "selected_meaning_id": selected_meaning_id,
        "candidate_meaning_id": candidate_meaning_id,
        "selection_reference_id": selection_reference_id,
        "selection_basis_id": selection_basis_id,
        "selection_constraint_id": selection_constraint_id,
        "selection_trace_id": selection_trace_id,
        "selection_receipt_id": selection_receipt_id,
        "selected_meaning_status": selected_meaning_status,
        "selection_scope": selection_scope,
        "confidence_boundary": confidence_boundary,
        "meaning_object_id": meaning_object_id,
        "meaning_content_hash": meaning_content_hash,
        "normalized_text_snapshot": normalized_text_snapshot,
        "source_expression_ref": source_expression_ref,
        "upstream_record_bindings": upstream_record_bindings,
        "uncertainty_refs": uncertainty_refs,
        "required_law_refs": required_law_refs,
        "comparison_refs": comparison_refs,
        "non_selected_candidate_refs": non_selected_candidate_refs,
        "downstream_block_refs": downstream_block_refs,
        "attribution_refs": attribution_refs,
        "scope_refs": scope_refs,
        "refusal_refs": refusal_refs,
        "version_tag": "v1",
    }
    return ExpressionSourceRecord(
        expression_source_id=stable_expression_id("expression-source", body),
        **body,
    )


def validate_expression_source_record(record: ExpressionSourceRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    required_text = (
        "expression_source_id",
        "selected_meaning_id",
        "candidate_meaning_id",
        "selection_reference_id",
        "selection_basis_id",
        "selection_constraint_id",
        "selection_trace_id",
        "selection_receipt_id",
        "selected_meaning_status",
        "selection_scope",
        "confidence_boundary",
        "meaning_object_id",
        "meaning_content_hash",
        "normalized_text_snapshot",
        "source_expression_ref",
    )
    for field_name in required_text:
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.selected_meaning_status not in ALLOWED_SELECTED_MEANING_STATUSES:
        issues.append(issue("selected_meaning_status", "unsupported_selected_meaning_status"))
    if record.meaning_content_hash != text_sha256(record.normalized_text_snapshot):
        issues.append(issue("meaning_content_hash", "snapshot_hash_mismatch"))
    if not tuple_of_text(record.upstream_record_bindings, allow_empty=False):
        issues.append(issue("upstream_record_bindings", "nonempty_tuple_required"))
    else:
        for binding in record.upstream_record_bindings:
            if not _BINDING_RE.fullmatch(binding):
                issues.append(issue("upstream_record_bindings", "invalid_ref_sha256_binding"))
    tuple_fields = (
        "uncertainty_refs",
        "required_law_refs",
        "comparison_refs",
        "non_selected_candidate_refs",
        "downstream_block_refs",
        "attribution_refs",
        "scope_refs",
        "refusal_refs",
    )
    for field_name in tuple_fields:
        value = getattr(record, field_name)
        if not tuple_of_text(value):
            issues.append(issue(field_name, "must_be_tuple_of_text"))
        elif not unique_tuple(value):
            issues.append(issue(field_name, "duplicate_entries_not_allowed"))
    for law in REQUIRED_EXPRESSION_LAWS:
        if law not in record.required_law_refs:
            issues.append(issue("required_law_refs", f"missing_{law}"))
    if record.selected_meaning_status in {
        "selection_held_boundary",
        "selection_blocked_boundary",
        "selection_refused_boundary",
    } and not record.downstream_block_refs:
        issues.append(issue("downstream_block_refs", "required_for_non_positive_selection_status"))
    if record.selected_meaning_status == "selection_refused_boundary" and not record.refusal_refs:
        issues.append(issue("refusal_refs", "required_for_refused_selection"))
    if record.expression_source_id != record.expected_id():
        issues.append(issue("expression_source_id", "stable_identifier_mismatch"))
    check_false_only(record, issues, "expression_source")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_expression_source_record(
    *, selected_meaning_status: str = "selected_meaning_boundary_recorded"
) -> ExpressionSourceRecord:
    text = (
        "According to the operator, the system may proceed only if checksum "
        "verification passes; it is not authorized while uncertainty remains."
    )
    block_refs = ()
    refusal_refs = ("refusal:not_authorized",)
    if selected_meaning_status != "selected_meaning_boundary_recorded":
        block_refs = ("downstream-block:status-boundary",)
    return build_expression_source_record(
        selected_meaning_id="selected-meaning:demo",
        candidate_meaning_id="candidate-meaning:demo",
        selection_reference_id="candidate-selection-ref:demo",
        selection_basis_id="selection-basis:demo",
        selection_constraint_id="selection-constraint:demo",
        selection_trace_id="selection-trace:demo",
        selection_receipt_id="selection-receipt:demo",
        selected_meaning_status=selected_meaning_status,
        selection_scope="internal_boundary_only",
        confidence_boundary="bounded_confidence_not_truth",
        meaning_object_id="meaning-object:demo",
        normalized_text_snapshot=text,
        source_expression_ref="source-expression:demo",
        upstream_record_bindings=(
            "meaning-object:demo#sha256:" + text_sha256("meaning-object-snapshot"),
            "selection-receipt:demo#sha256:" + text_sha256("selection-receipt-snapshot"),
        ),
        uncertainty_refs=("uncertainty:remains",),
        comparison_refs=("comparison:demo",),
        non_selected_candidate_refs=("candidate-meaning:alternate",),
        downstream_block_refs=block_refs,
        attribution_refs=("attribution:operator",),
        scope_refs=("scope:the-system",),
        refusal_refs=refusal_refs,
    )
