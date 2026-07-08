from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_selection_id, tuple_of_text

ALLOWED_SELECTION_REFERENCE_STATUSES = (
    "candidate_referenced_for_selection_boundary",
    "candidate_selection_held_boundary",
    "candidate_selection_blocked_boundary",
)

ALLOWED_CANDIDATE_SELECTION_ROLES = (
    "selected_candidate_reference",
    "non_selected_candidate_reference",
    "held_candidate_reference",
)


@dataclass(frozen=True)
class CandidateSelectionReferenceRecord:
    selection_reference_id: str
    candidate_meaning_id: str
    candidate_group_id: str
    source_expression_ref: str
    candidate_role: str
    selection_reference_status: str
    upstream_boundary_refs: Tuple[str, ...]
    non_selected_candidate_refs: Tuple[str, ...]
    selection_reason_refs: Tuple[str, ...]
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
            "candidate_meaning_id": self.candidate_meaning_id,
            "candidate_group_id": self.candidate_group_id,
            "source_expression_ref": self.source_expression_ref,
            "candidate_role": self.candidate_role,
            "selection_reference_status": self.selection_reference_status,
            "upstream_boundary_refs": self.upstream_boundary_refs,
            "non_selected_candidate_refs": self.non_selected_candidate_refs,
            "selection_reason_refs": self.selection_reason_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_selection_id("candidate-selection-ref", self.canonical_body())


def build_candidate_selection_reference_record(
    *,
    candidate_meaning_id: str,
    candidate_group_id: str,
    source_expression_ref: str,
    candidate_role: str,
    selection_reference_status: str,
    upstream_boundary_refs: Tuple[str, ...],
    non_selected_candidate_refs: Tuple[str, ...],
    selection_reason_refs: Tuple[str, ...],
) -> CandidateSelectionReferenceRecord:
    body = {
        "candidate_meaning_id": candidate_meaning_id,
        "candidate_group_id": candidate_group_id,
        "source_expression_ref": source_expression_ref,
        "candidate_role": candidate_role,
        "selection_reference_status": selection_reference_status,
        "upstream_boundary_refs": upstream_boundary_refs,
        "non_selected_candidate_refs": non_selected_candidate_refs,
        "selection_reason_refs": selection_reason_refs,
        "version_tag": "v1",
    }
    return CandidateSelectionReferenceRecord(selection_reference_id=stable_selection_id("candidate-selection-ref", body), **body)


def validate_candidate_selection_reference_record(record: CandidateSelectionReferenceRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("selection_reference_id", "candidate_meaning_id", "candidate_group_id", "source_expression_ref", "candidate_role", "selection_reference_status"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.candidate_role not in ALLOWED_CANDIDATE_SELECTION_ROLES:
        issues.append(issue("candidate_role", "unsupported_candidate_role"))
    if record.selection_reference_status not in ALLOWED_SELECTION_REFERENCE_STATUSES:
        issues.append(issue("selection_reference_status", "unsupported_selection_reference_status"))
    if not tuple_of_text(record.upstream_boundary_refs, allow_empty=False):
        issues.append(issue("upstream_boundary_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.non_selected_candidate_refs):
        issues.append(issue("non_selected_candidate_refs", "must_be_tuple_of_text"))
    if not tuple_of_text(record.selection_reason_refs, allow_empty=False):
        issues.append(issue("selection_reason_refs", "must_be_nonempty_tuple_of_text"))
    if record.candidate_role == "selected_candidate_reference" and not record.non_selected_candidate_refs:
        issues.append(issue("non_selected_candidate_refs", "selected_candidate_requires_competition_context"))
    if record.selection_reference_id != record.expected_id():
        issues.append(issue("selection_reference_id", "stable_identifier_mismatch"))
    check_false_only(record, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "candidate_selection_reference")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_candidate_selection_reference_record() -> CandidateSelectionReferenceRecord:
    return build_candidate_selection_reference_record(
        candidate_meaning_id="candidate_meaning:reply_requires_clarification",
        candidate_group_id="candidate_competition:reply_group",
        source_expression_ref="source_expression:demo",
        candidate_role="selected_candidate_reference",
        selection_reference_status="candidate_referenced_for_selection_boundary",
        upstream_boundary_refs=("slice11_candidate_meaning_boundary", "slice12_ambiguity_clarification_boundary", "slice10_gate_boundary"),
        non_selected_candidate_refs=("candidate_meaning:unsupported_action_path",),
        selection_reason_refs=("basis:ambiguity_unresolved", "constraint:no_action_safe"),
    )


def demo_non_selected_candidate_reference_record() -> CandidateSelectionReferenceRecord:
    return build_candidate_selection_reference_record(
        candidate_meaning_id="candidate_meaning:unsupported_action_path",
        candidate_group_id="candidate_competition:reply_group",
        source_expression_ref="source_expression:demo",
        candidate_role="non_selected_candidate_reference",
        selection_reference_status="candidate_selection_held_boundary",
        upstream_boundary_refs=("slice11_candidate_meaning_boundary", "slice13_requirements_traceability_boundary"),
        non_selected_candidate_refs=(),
        selection_reason_refs=("basis:missing_permission",),
    )
