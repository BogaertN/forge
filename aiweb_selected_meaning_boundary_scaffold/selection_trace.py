from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_selection_id, tuple_of_text

ALLOWED_TRACE_STATUSES = (
    "selection_trace_recorded_boundary",
    "selection_trace_held_boundary",
    "selection_trace_blocked_boundary",
)


@dataclass(frozen=True)
class SelectionTraceRecord:
    selection_trace_id: str
    selected_meaning_id: str
    candidate_group_id: str
    selection_step_refs: Tuple[str, ...]
    comparison_refs: Tuple[str, ...]
    non_selected_candidate_refs: Tuple[str, ...]
    trace_status: str
    trace_scope: str
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
            "candidate_group_id": self.candidate_group_id,
            "selection_step_refs": self.selection_step_refs,
            "comparison_refs": self.comparison_refs,
            "non_selected_candidate_refs": self.non_selected_candidate_refs,
            "trace_status": self.trace_status,
            "trace_scope": self.trace_scope,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_selection_id("selection-trace", self.canonical_body())


def build_selection_trace_record(
    *,
    selected_meaning_id: str,
    candidate_group_id: str,
    selection_step_refs: Tuple[str, ...],
    comparison_refs: Tuple[str, ...],
    non_selected_candidate_refs: Tuple[str, ...],
    trace_status: str,
    trace_scope: str,
) -> SelectionTraceRecord:
    body = {
        "selected_meaning_id": selected_meaning_id,
        "candidate_group_id": candidate_group_id,
        "selection_step_refs": selection_step_refs,
        "comparison_refs": comparison_refs,
        "non_selected_candidate_refs": non_selected_candidate_refs,
        "trace_status": trace_status,
        "trace_scope": trace_scope,
        "version_tag": "v1",
    }
    return SelectionTraceRecord(selection_trace_id=stable_selection_id("selection-trace", body), **body)


def validate_selection_trace_record(record: SelectionTraceRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("selection_trace_id", "selected_meaning_id", "candidate_group_id", "trace_status", "trace_scope"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.trace_status not in ALLOWED_TRACE_STATUSES:
        issues.append(issue("trace_status", "unsupported_trace_status"))
    if record.trace_scope != "trace_record_only_not_delivery_not_execution":
        issues.append(issue("trace_scope", "must_remain_record_only"))
    if not tuple_of_text(record.selection_step_refs, allow_empty=False):
        issues.append(issue("selection_step_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.comparison_refs, allow_empty=False):
        issues.append(issue("comparison_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.non_selected_candidate_refs):
        issues.append(issue("non_selected_candidate_refs", "must_be_tuple_of_text"))
    if record.selection_trace_id != record.expected_id():
        issues.append(issue("selection_trace_id", "stable_identifier_mismatch"))
    check_false_only(record, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "selection_trace")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_selection_trace_record() -> SelectionTraceRecord:
    return build_selection_trace_record(
        selected_meaning_id="selected-meaning:demo",
        candidate_group_id="candidate_competition:reply_group",
        selection_step_refs=("candidate-selection-ref:demo", "selection-basis:demo", "selection-constraint:demo"),
        comparison_refs=("candidate_meaning:reply_requires_clarification", "candidate_meaning:unsupported_action_path"),
        non_selected_candidate_refs=("candidate_meaning:unsupported_action_path",),
        trace_status="selection_trace_recorded_boundary",
        trace_scope="trace_record_only_not_delivery_not_execution",
    )
