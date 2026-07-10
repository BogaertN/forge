from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    ALLOWED_DIMENSION_STATES,
    NON_AUTHORITY_DISCLAIMER,
    REQUIRED_EXPRESSION_LAWS,
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
class ExpressionPreservationContractRecord:
    preservation_contract_id: str
    expression_source_id: str
    selected_meaning_id: str
    negation_state: str
    negation_markers: Tuple[str, ...]
    condition_state: str
    condition_markers: Tuple[str, ...]
    modality_state: str
    modality_markers: Tuple[str, ...]
    forbidden_modality_strengtheners: Tuple[str, ...]
    attribution_state: str
    attribution_markers: Tuple[str, ...]
    scope_state: str
    scope_markers: Tuple[str, ...]
    forbidden_scope_wideners: Tuple[str, ...]
    refusal_relevance_state: str
    refusal_relevance_markers: Tuple[str, ...]
    uncertainty_state: str
    uncertainty_markers: Tuple[str, ...]
    forbidden_claim_phrases: Tuple[str, ...]
    required_disclaimer: str
    required_law_refs: Tuple[str, ...]
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
            "selected_meaning_id": self.selected_meaning_id,
            "negation_state": self.negation_state,
            "negation_markers": self.negation_markers,
            "condition_state": self.condition_state,
            "condition_markers": self.condition_markers,
            "modality_state": self.modality_state,
            "modality_markers": self.modality_markers,
            "forbidden_modality_strengtheners": self.forbidden_modality_strengtheners,
            "attribution_state": self.attribution_state,
            "attribution_markers": self.attribution_markers,
            "scope_state": self.scope_state,
            "scope_markers": self.scope_markers,
            "forbidden_scope_wideners": self.forbidden_scope_wideners,
            "refusal_relevance_state": self.refusal_relevance_state,
            "refusal_relevance_markers": self.refusal_relevance_markers,
            "uncertainty_state": self.uncertainty_state,
            "uncertainty_markers": self.uncertainty_markers,
            "forbidden_claim_phrases": self.forbidden_claim_phrases,
            "required_disclaimer": self.required_disclaimer,
            "required_law_refs": self.required_law_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_expression_id("expression-preservation", self.canonical_body())


def build_expression_preservation_contract(
    *,
    expression_source_id: str,
    selected_meaning_id: str,
    negation_state: str,
    negation_markers: Tuple[str, ...],
    condition_state: str,
    condition_markers: Tuple[str, ...],
    modality_state: str,
    modality_markers: Tuple[str, ...],
    forbidden_modality_strengtheners: Tuple[str, ...],
    attribution_state: str,
    attribution_markers: Tuple[str, ...],
    scope_state: str,
    scope_markers: Tuple[str, ...],
    forbidden_scope_wideners: Tuple[str, ...],
    refusal_relevance_state: str,
    refusal_relevance_markers: Tuple[str, ...],
    uncertainty_state: str,
    uncertainty_markers: Tuple[str, ...],
    forbidden_claim_phrases: Tuple[str, ...],
    required_disclaimer: str = NON_AUTHORITY_DISCLAIMER,
    required_law_refs: Tuple[str, ...] = REQUIRED_EXPRESSION_LAWS,
) -> ExpressionPreservationContractRecord:
    body = {
        "expression_source_id": expression_source_id,
        "selected_meaning_id": selected_meaning_id,
        "negation_state": negation_state,
        "negation_markers": negation_markers,
        "condition_state": condition_state,
        "condition_markers": condition_markers,
        "modality_state": modality_state,
        "modality_markers": modality_markers,
        "forbidden_modality_strengtheners": forbidden_modality_strengtheners,
        "attribution_state": attribution_state,
        "attribution_markers": attribution_markers,
        "scope_state": scope_state,
        "scope_markers": scope_markers,
        "forbidden_scope_wideners": forbidden_scope_wideners,
        "refusal_relevance_state": refusal_relevance_state,
        "refusal_relevance_markers": refusal_relevance_markers,
        "uncertainty_state": uncertainty_state,
        "uncertainty_markers": uncertainty_markers,
        "forbidden_claim_phrases": forbidden_claim_phrases,
        "required_disclaimer": required_disclaimer,
        "required_law_refs": required_law_refs,
        "version_tag": "v1",
    }
    return ExpressionPreservationContractRecord(
        preservation_contract_id=stable_expression_id("expression-preservation", body),
        **body,
    )


def _validate_dimension(
    *, name: str, state: str, markers: Tuple[str, ...], issues: list[ValidationIssue]
) -> None:
    if state not in ALLOWED_DIMENSION_STATES:
        issues.append(issue(f"{name}_state", "unsupported_dimension_state"))
        return
    if not tuple_of_text(markers, allow_empty=False):
        issues.append(issue(f"{name}_markers", "explicit_nonempty_markers_required"))
        return
    if not unique_tuple(markers):
        issues.append(issue(f"{name}_markers", "duplicate_markers_not_allowed"))
    if state == "explicit_not_applicable" and not all(
        marker.startswith("reason:") for marker in markers
    ):
        issues.append(issue(f"{name}_markers", "not_applicable_requires_reason_markers"))


def validate_expression_preservation_contract(
    record: ExpressionPreservationContractRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "preservation_contract_id",
        "expression_source_id",
        "selected_meaning_id",
        "required_disclaimer",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    dimensions = (
        ("negation", record.negation_state, record.negation_markers),
        ("condition", record.condition_state, record.condition_markers),
        ("modality", record.modality_state, record.modality_markers),
        ("attribution", record.attribution_state, record.attribution_markers),
        ("scope", record.scope_state, record.scope_markers),
        (
            "refusal_relevance",
            record.refusal_relevance_state,
            record.refusal_relevance_markers,
        ),
        ("uncertainty", record.uncertainty_state, record.uncertainty_markers),
    )
    for name, state, markers in dimensions:
        _validate_dimension(name=name, state=state, markers=markers, issues=issues)
    for field_name in (
        "forbidden_modality_strengtheners",
        "forbidden_scope_wideners",
        "forbidden_claim_phrases",
        "required_law_refs",
    ):
        value = getattr(record, field_name)
        if not tuple_of_text(value, allow_empty=False):
            issues.append(issue(field_name, "nonempty_tuple_of_text_required"))
        elif not unique_tuple(value):
            issues.append(issue(field_name, "duplicate_entries_not_allowed"))
    for law in REQUIRED_EXPRESSION_LAWS:
        if law not in record.required_law_refs:
            issues.append(issue("required_law_refs", f"missing_{law}"))
    if record.required_disclaimer != NON_AUTHORITY_DISCLAIMER:
        issues.append(issue("required_disclaimer", "must_use_exact_non_authority_disclaimer"))
    if record.preservation_contract_id != record.expected_id():
        issues.append(issue("preservation_contract_id", "stable_identifier_mismatch"))
    check_false_only(record, issues, "expression_preservation_contract")
    return ValidationReport(SCHEMA_VERSION, not issues, tuple(issues))


def demo_expression_preservation_contract(
    expression_source_id: str = "expression-source:demo",
    selected_meaning_id: str = "selected-meaning:demo",
) -> ExpressionPreservationContractRecord:
    return build_expression_preservation_contract(
        expression_source_id=expression_source_id,
        selected_meaning_id=selected_meaning_id,
        negation_state="preserve_required",
        negation_markers=("not authorized",),
        condition_state="preserve_required",
        condition_markers=("only if checksum verification passes",),
        modality_state="preserve_required",
        modality_markers=("may proceed",),
        forbidden_modality_strengtheners=("definitely", "certainly", "will proceed"),
        attribution_state="preserve_required",
        attribution_markers=("According to the operator",),
        scope_state="preserve_required",
        scope_markers=("the system",),
        forbidden_scope_wideners=("every system", "all systems", "everyone"),
        refusal_relevance_state="preserve_required",
        refusal_relevance_markers=("not authorized",),
        uncertainty_state="preserve_required",
        uncertainty_markers=("uncertainty remains",),
        forbidden_claim_phrases=(
            "this proves",
            "authority granted",
            "accepted as true",
            "permission granted",
            "delivery completed",
            "execution completed",
        ),
    )
