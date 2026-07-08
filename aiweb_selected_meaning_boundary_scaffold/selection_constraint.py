from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import REQUIRED_PRIOR_BOUNDARIES, REQUIRED_SELECTION_LAWS, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_selection_id, tuple_of_text

ALLOWED_CONSTRAINT_STATUSES = (
    "constraint_boundary_only",
    "constraint_satisfied_for_selection_record_only",
    "constraint_blocked_boundary",
)

ALLOWED_CONSTRAINT_KINDS = (
    "prior_boundary_dependency",
    "downstream_authority_block",
    "selection_law_enforcement",
    "no_action_safe_constraint",
)


@dataclass(frozen=True)
class SelectionConstraintRecord:
    selection_constraint_id: str
    constraint_key: str
    constraint_kind: str
    constraint_status: str
    required_prior_boundary_refs: Tuple[str, ...]
    required_law_refs: Tuple[str, ...]
    blocked_downstream_refs: Tuple[str, ...]
    enforcement_note: str
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
            "constraint_key": self.constraint_key,
            "constraint_kind": self.constraint_kind,
            "constraint_status": self.constraint_status,
            "required_prior_boundary_refs": self.required_prior_boundary_refs,
            "required_law_refs": self.required_law_refs,
            "blocked_downstream_refs": self.blocked_downstream_refs,
            "enforcement_note": self.enforcement_note,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_selection_id("selection-constraint", self.canonical_body())


def build_selection_constraint_record(
    *,
    constraint_key: str,
    constraint_kind: str,
    constraint_status: str,
    required_prior_boundary_refs: Tuple[str, ...],
    required_law_refs: Tuple[str, ...],
    blocked_downstream_refs: Tuple[str, ...],
    enforcement_note: str,
) -> SelectionConstraintRecord:
    body = {
        "constraint_key": constraint_key,
        "constraint_kind": constraint_kind,
        "constraint_status": constraint_status,
        "required_prior_boundary_refs": required_prior_boundary_refs,
        "required_law_refs": required_law_refs,
        "blocked_downstream_refs": blocked_downstream_refs,
        "enforcement_note": enforcement_note,
        "version_tag": "v1",
    }
    return SelectionConstraintRecord(selection_constraint_id=stable_selection_id("selection-constraint", body), **body)


def validate_selection_constraint_record(record: SelectionConstraintRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("selection_constraint_id", "constraint_key", "constraint_kind", "constraint_status", "enforcement_note"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.constraint_kind not in ALLOWED_CONSTRAINT_KINDS:
        issues.append(issue("constraint_kind", "unsupported_constraint_kind"))
    if record.constraint_status not in ALLOWED_CONSTRAINT_STATUSES:
        issues.append(issue("constraint_status", "unsupported_constraint_status"))
    if not tuple_of_text(record.required_prior_boundary_refs, allow_empty=False):
        issues.append(issue("required_prior_boundary_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.required_law_refs, allow_empty=False):
        issues.append(issue("required_law_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.blocked_downstream_refs, allow_empty=False):
        issues.append(issue("blocked_downstream_refs", "must_be_nonempty_tuple_of_text"))
    missing_prior = [item for item in REQUIRED_PRIOR_BOUNDARIES if item not in record.required_prior_boundary_refs]
    if missing_prior:
        issues.append(issue("required_prior_boundary_refs", "missing_required_prior_boundary"))
    missing_law = [item for item in REQUIRED_SELECTION_LAWS[:4] if item not in record.required_law_refs]
    if missing_law:
        issues.append(issue("required_law_refs", "missing_core_selection_law"))
    for required_block in ("truth_decision", "permission_grant", "delivery_action", "execution_authority"):
        if required_block not in record.blocked_downstream_refs:
            issues.append(issue("blocked_downstream_refs", f"missing_{required_block}"))
    if record.selection_constraint_id != record.expected_id():
        issues.append(issue("selection_constraint_id", "stable_identifier_mismatch"))
    check_false_only(record, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "selection_constraint")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_selection_constraint_record() -> SelectionConstraintRecord:
    return build_selection_constraint_record(
        constraint_key="selected-meaning-no-downstream-authority",
        constraint_kind="downstream_authority_block",
        constraint_status="constraint_satisfied_for_selection_record_only",
        required_prior_boundary_refs=REQUIRED_PRIOR_BOUNDARIES,
        required_law_refs=REQUIRED_SELECTION_LAWS,
        blocked_downstream_refs=("truth_decision", "permission_grant", "delivery_action", "execution_authority", "memory_write", "evidence_validation", "tool_invocation"),
        enforcement_note="Selected meaning can be recorded as a boundary state without becoming truth, permission, delivery, or execution.",
    )
