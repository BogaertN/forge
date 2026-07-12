from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    GP014_CALL_DECISION,
    GP014_IMPORT_DECISION,
    GP014_MODIFICATION_DECISION,
    GP014_PROMOTION_DECISION,
    GP014_SUPERSESSION_DECISION,
    GP014_WRAPPER_DECISION,
    REJECTED_GP014_ACTIONS,
    REQUIRED_DECISION_LAWS,
    SCHEMA_VERSION,
    FALSE_ONLY_AUTHORITY_FIELDS,
    ValidationIssue,
    ValidationReport,
    check_false_only,
    issue,
    nonempty_text,
    stable_decision_id,
    tuple_of_text,
    unique_tuple,
)


@dataclass(frozen=True)
class GP014WrapperDecisionRecord:
    gp014_wrapper_decision_id: str
    gp014_reference_id: str
    wrapper_decision: str
    import_decision: str
    call_decision: str
    modification_decision: str
    supersession_decision: str
    promotion_decision: str
    rejected_actions: Tuple[str, ...]
    required_decision_laws: Tuple[str, ...]
    future_change_requires: Tuple[str, ...]
    decision_status: str = "slice18_no_wrapper_reference_only_decision_recorded"
    version_tag: str = "v1"

    general_language_authority: bool = False
    concept_authority: bool = False
    predicate_authority: bool = False
    source_authority: bool = False
    selected_meaning_authority: bool = False
    full_rmc_authority: bool = False
    renderer_authority: bool = False
    output_approval: bool = False
    delivery_authority: bool = False
    execution_authority: bool = False
    runtime_authority: bool = False
    echo_authority: bool = False
    production_authority: bool = False
    route_authority: bool = False
    ui_authority: bool = False
    memory_authority: bool = False
    corpus_authority: bool = False
    external_truth_authority: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False
    training_authority: bool = False
    gp014_modification: bool = False
    gp014_import: bool = False
    gp014_call: bool = False
    gp014_wrapper_created: bool = False
    gp014_supersession: bool = False
    gp014_promotion: bool = False
    gp015_repair: bool = False
    release_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "gp014_reference_id": self.gp014_reference_id,
            "wrapper_decision": self.wrapper_decision,
            "import_decision": self.import_decision,
            "call_decision": self.call_decision,
            "modification_decision": self.modification_decision,
            "supersession_decision": self.supersession_decision,
            "promotion_decision": self.promotion_decision,
            "rejected_actions": self.rejected_actions,
            "required_decision_laws": self.required_decision_laws,
            "future_change_requires": self.future_change_requires,
            "decision_status": self.decision_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_decision_id("gp014-wrapper-decision", self.canonical_body())


def build_gp014_wrapper_decision_record(*, gp014_reference_id: str) -> GP014WrapperDecisionRecord:
    body = {
        "gp014_reference_id": gp014_reference_id,
        "wrapper_decision": GP014_WRAPPER_DECISION,
        "import_decision": GP014_IMPORT_DECISION,
        "call_decision": GP014_CALL_DECISION,
        "modification_decision": GP014_MODIFICATION_DECISION,
        "supersession_decision": GP014_SUPERSESSION_DECISION,
        "promotion_decision": GP014_PROMOTION_DECISION,
        "rejected_actions": REJECTED_GP014_ACTIONS,
        "required_decision_laws": REQUIRED_DECISION_LAWS,
        "future_change_requires": (
            "separate_future_formal_wrapper_authorization",
            "separate_future_source_authority_packet",
            "separate_future_supersession_path_if_supersession_is_proposed",
            "explicit_hash_protection_for_gp014_before_any_targeted_change",
        ),
        "decision_status": "slice18_no_wrapper_reference_only_decision_recorded",
        "version_tag": "v1",
    }
    return GP014WrapperDecisionRecord(
        gp014_wrapper_decision_id=stable_decision_id("gp014-wrapper-decision", body), **body
    )


def validate_gp014_wrapper_decision_record(record: GP014WrapperDecisionRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.gp014_wrapper_decision_id != record.expected_id():
        issues.append(issue("gp014_wrapper_decision_id", "unstable_or_incorrect_id"))
    if not nonempty_text(record.gp014_reference_id):
        issues.append(issue("gp014_reference_id", "required"))
    expected = {
        "wrapper_decision": GP014_WRAPPER_DECISION,
        "import_decision": GP014_IMPORT_DECISION,
        "call_decision": GP014_CALL_DECISION,
        "modification_decision": GP014_MODIFICATION_DECISION,
        "supersession_decision": GP014_SUPERSESSION_DECISION,
        "promotion_decision": GP014_PROMOTION_DECISION,
        "decision_status": "slice18_no_wrapper_reference_only_decision_recorded",
    }
    for field, value in expected.items():
        if getattr(record, field) != value:
            issues.append(issue(field, f"must_be_{value}"))
    if not tuple_of_text(record.rejected_actions) or not unique_tuple(record.rejected_actions):
        issues.append(issue("rejected_actions", "must_be_unique_nonempty_text_tuple"))
    elif tuple(record.rejected_actions) != REJECTED_GP014_ACTIONS:
        issues.append(issue("rejected_actions", "must_match_required_rejected_gp014_actions"))
    if not tuple_of_text(record.required_decision_laws) or not unique_tuple(record.required_decision_laws):
        issues.append(issue("required_decision_laws", "must_be_unique_nonempty_text_tuple"))
    elif tuple(record.required_decision_laws) != REQUIRED_DECISION_LAWS:
        issues.append(issue("required_decision_laws", "must_match_slice18_design_laws"))
    if not tuple_of_text(record.future_change_requires):
        issues.append(issue("future_change_requires", "future_change_controls_required"))
    check_false_only(record, FALSE_ONLY_AUTHORITY_FIELDS, issues)
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_gp014_wrapper_decision_record(gp014_reference_id: str = "gp014-reference:demo") -> GP014WrapperDecisionRecord:
    return build_gp014_wrapper_decision_record(gp014_reference_id=gp014_reference_id)
