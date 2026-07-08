from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import REQUIRED_SELECTION_LAWS, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_selection_id, tuple_of_text

ALLOWED_SELECTED_MEANING_STATUSES = (
    "selected_meaning_boundary_recorded",
    "selection_blocked_boundary",
    "selection_held_boundary",
    "selection_refused_boundary",
)

ALLOWED_SELECTION_SCOPES = (
    "internal_boundary_only",
    "held_boundary_only",
    "refusal_boundary_only",
)

ALLOWED_CONFIDENCE_BOUNDARIES = (
    "bounded_confidence_not_truth",
    "low_confidence_hold",
    "unknown_confidence_boundary",
)


@dataclass(frozen=True)
class SelectedMeaningStatusRecord:
    selected_meaning_id: str
    candidate_meaning_id: str
    selection_reference_id: str
    selection_basis_id: str
    selection_constraint_id: str
    selected_meaning_status: str
    selection_scope: str
    confidence_boundary: str
    uncertainty_refs: Tuple[str, ...]
    required_law_refs: Tuple[str, ...]
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
            "selection_reference_id": self.selection_reference_id,
            "selection_basis_id": self.selection_basis_id,
            "selection_constraint_id": self.selection_constraint_id,
            "selected_meaning_status": self.selected_meaning_status,
            "selection_scope": self.selection_scope,
            "confidence_boundary": self.confidence_boundary,
            "uncertainty_refs": self.uncertainty_refs,
            "required_law_refs": self.required_law_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_selection_id("selected-meaning", self.canonical_body())


def build_selected_meaning_status_record(
    *,
    candidate_meaning_id: str,
    selection_reference_id: str,
    selection_basis_id: str,
    selection_constraint_id: str,
    selected_meaning_status: str,
    selection_scope: str,
    confidence_boundary: str,
    uncertainty_refs: Tuple[str, ...],
    required_law_refs: Tuple[str, ...],
) -> SelectedMeaningStatusRecord:
    body = {
        "candidate_meaning_id": candidate_meaning_id,
        "selection_reference_id": selection_reference_id,
        "selection_basis_id": selection_basis_id,
        "selection_constraint_id": selection_constraint_id,
        "selected_meaning_status": selected_meaning_status,
        "selection_scope": selection_scope,
        "confidence_boundary": confidence_boundary,
        "uncertainty_refs": uncertainty_refs,
        "required_law_refs": required_law_refs,
        "version_tag": "v1",
    }
    return SelectedMeaningStatusRecord(selected_meaning_id=stable_selection_id("selected-meaning", body), **body)


def validate_selected_meaning_status_record(record: SelectedMeaningStatusRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("selected_meaning_id", "candidate_meaning_id", "selection_reference_id", "selection_basis_id", "selection_constraint_id", "selected_meaning_status", "selection_scope", "confidence_boundary"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.selected_meaning_status not in ALLOWED_SELECTED_MEANING_STATUSES:
        issues.append(issue("selected_meaning_status", "unsupported_selected_meaning_status"))
    if record.selection_scope not in ALLOWED_SELECTION_SCOPES:
        issues.append(issue("selection_scope", "unsupported_selection_scope"))
    if record.confidence_boundary not in ALLOWED_CONFIDENCE_BOUNDARIES:
        issues.append(issue("confidence_boundary", "unsupported_confidence_boundary"))
    if not tuple_of_text(record.uncertainty_refs):
        issues.append(issue("uncertainty_refs", "must_be_tuple_of_text"))
    if not tuple_of_text(record.required_law_refs, allow_empty=False):
        issues.append(issue("required_law_refs", "must_be_nonempty_tuple_of_text"))
    for law in REQUIRED_SELECTION_LAWS[:4]:
        if law not in record.required_law_refs:
            issues.append(issue("required_law_refs", f"missing_{law}"))
    if record.selected_meaning_id != record.expected_id():
        issues.append(issue("selected_meaning_id", "stable_identifier_mismatch"))
    check_false_only(record, SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "selected_meaning_status")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_selected_meaning_status_record() -> SelectedMeaningStatusRecord:
    return build_selected_meaning_status_record(
        candidate_meaning_id="candidate_meaning:reply_requires_clarification",
        selection_reference_id="candidate-selection-ref:demo",
        selection_basis_id="selection-basis:demo",
        selection_constraint_id="selection-constraint:demo",
        selected_meaning_status="selected_meaning_boundary_recorded",
        selection_scope="internal_boundary_only",
        confidence_boundary="bounded_confidence_not_truth",
        uncertainty_refs=("uncertainty:user_intent_not_final",),
        required_law_refs=REQUIRED_SELECTION_LAWS,
    )


def demo_selection_blocked_status_record() -> SelectedMeaningStatusRecord:
    return build_selected_meaning_status_record(
        candidate_meaning_id="candidate_meaning:unsupported_action_path",
        selection_reference_id="candidate-selection-ref:blocked-demo",
        selection_basis_id="selection-basis:insufficient-demo",
        selection_constraint_id="selection-constraint:no-action-demo",
        selected_meaning_status="selection_blocked_boundary",
        selection_scope="held_boundary_only",
        confidence_boundary="low_confidence_hold",
        uncertainty_refs=("uncertainty:missing_support",),
        required_law_refs=REQUIRED_SELECTION_LAWS,
    )
