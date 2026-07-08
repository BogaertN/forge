from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_selection_id, tuple_of_text

ALLOWED_BASIS_KINDS = (
    "constraint_satisfied_boundary",
    "ambiguity_reduced_boundary",
    "gate_allowed_boundary",
    "support_preferred_boundary",
    "no_action_safe_boundary",
    "insufficient_support_boundary",
)

ALLOWED_BASIS_STATUSES = (
    "basis_recorded_boundary",
    "basis_insufficient_boundary",
    "basis_held_boundary",
)


@dataclass(frozen=True)
class SelectionBasisRecord:
    selection_basis_id: str
    basis_key: str
    selected_candidate_ref: str
    basis_kind: str
    basis_status: str
    support_refs: Tuple[str, ...]
    constraint_refs: Tuple[str, ...]
    rejected_basis_refs: Tuple[str, ...]
    uncertainty_refs: Tuple[str, ...]
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
            "basis_key": self.basis_key,
            "selected_candidate_ref": self.selected_candidate_ref,
            "basis_kind": self.basis_kind,
            "basis_status": self.basis_status,
            "support_refs": self.support_refs,
            "constraint_refs": self.constraint_refs,
            "rejected_basis_refs": self.rejected_basis_refs,
            "uncertainty_refs": self.uncertainty_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_selection_id("selection-basis", self.canonical_body())


def build_selection_basis_record(
    *,
    basis_key: str,
    selected_candidate_ref: str,
    basis_kind: str,
    basis_status: str,
    support_refs: Tuple[str, ...],
    constraint_refs: Tuple[str, ...],
    rejected_basis_refs: Tuple[str, ...],
    uncertainty_refs: Tuple[str, ...],
) -> SelectionBasisRecord:
    body = {
        "basis_key": basis_key,
        "selected_candidate_ref": selected_candidate_ref,
        "basis_kind": basis_kind,
        "basis_status": basis_status,
        "support_refs": support_refs,
        "constraint_refs": constraint_refs,
        "rejected_basis_refs": rejected_basis_refs,
        "uncertainty_refs": uncertainty_refs,
        "version_tag": "v1",
    }
    return SelectionBasisRecord(selection_basis_id=stable_selection_id("selection-basis", body), **body)


def validate_selection_basis_record(record: SelectionBasisRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("selection_basis_id", "basis_key", "selected_candidate_ref", "basis_kind", "basis_status"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.basis_kind not in ALLOWED_BASIS_KINDS:
        issues.append(issue("basis_kind", "unsupported_basis_kind"))
    if record.basis_status not in ALLOWED_BASIS_STATUSES:
        issues.append(issue("basis_status", "unsupported_basis_status"))
    if not tuple_of_text(record.support_refs, allow_empty=False):
        issues.append(issue("support_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.constraint_refs, allow_empty=False):
        issues.append(issue("constraint_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.rejected_basis_refs):
        issues.append(issue("rejected_basis_refs", "must_be_tuple_of_text"))
    if not tuple_of_text(record.uncertainty_refs):
        issues.append(issue("uncertainty_refs", "must_be_tuple_of_text"))
    if record.selection_basis_id != record.expected_id():
        issues.append(issue("selection_basis_id", "stable_identifier_mismatch"))
    check_false_only(record, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "selection_basis")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_selection_basis_record() -> SelectionBasisRecord:
    return build_selection_basis_record(
        basis_key="clarification_candidate_preferred_basis",
        selected_candidate_ref="candidate_meaning:reply_requires_clarification",
        basis_kind="no_action_safe_boundary",
        basis_status="basis_recorded_boundary",
        support_refs=("support:ambiguity_present", "gate:clarification_required"),
        constraint_refs=("constraint:no_delivery", "constraint:no_execution"),
        rejected_basis_refs=("candidate_meaning:unsupported_action_path",),
        uncertainty_refs=("uncertainty:user_intent_not_final",),
    )
