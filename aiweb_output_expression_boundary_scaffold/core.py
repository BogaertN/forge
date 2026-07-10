from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-output-expression-boundary-scaffold-v1"
SCOPE_STATUS = "output_expression_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"

REQUIRED_EXPRESSION_LAWS = (
    "readable_output_is_not_proof",
    "fluent_output_is_not_authority",
    "good_answer_is_not_acceptance",
    "expression_is_not_truth",
    "expression_is_not_permission",
    "expression_is_not_delivery",
    "expression_is_not_execution",
    "rendering_does_not_create_meaning",
    "rendering_must_not_alter_governed_meaning",
    "negation_must_be_preserved",
    "conditions_must_be_preserved",
    "modality_must_not_be_strengthened",
    "attribution_must_be_preserved",
    "scope_must_not_be_widened",
    "refusal_relevance_must_be_preserved",
    "uncertainty_must_be_preserved",
    "structural_validity_is_not_semantic_acceptance",
    "preview_eligibility_is_not_approval",
)

EXPRESSION_FALSE_ONLY_FIELDS = (
    "live_runtime_behavior",
    "live_runtime_interpretation",
    "truth_decision",
    "proof_claim",
    "authority_grant",
    "acceptance_effect",
    "permission_grant",
    "action_authorization",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "execution_authority",
    "output_approval",
    "user_facing_output_authorized",
    "memory_write",
    "memory_authority",
    "evidence_validation",
    "corpus_authority",
    "external_truth_authority",
    "external_resource_admission",
    "runtime_promotion",
    "resource_fetch",
    "resource_download",
    "resource_ingestion",
    "resource_parsing",
    "resource_indexing",
    "model_authority",
    "vector_authority",
    "retrieval_authority",
    "similarity_authority",
    "embedding_index_creation",
    "rag_execution",
    "training_authority",
    "gp014_supersession",
    "gp015_repair",
    "gp015r1_installation",
    "release_authority",
    "production_readiness",
)

NON_AUTHORITY_DISCLAIMER = (
    "Unapproved expression preview: not proof, authority, acceptance, permission, "
    "delivery, or execution."
)

ALLOWED_SELECTED_MEANING_STATUSES = (
    "selected_meaning_boundary_recorded",
    "selection_held_boundary",
    "selection_blocked_boundary",
    "selection_refused_boundary",
)

STATUS_ALLOWED_PREVIEW_KINDS = {
    "selected_meaning_boundary_recorded": (
        "explanation_preview",
        "status_preview",
        "clarification_preview",
    ),
    "selection_held_boundary": (
        "held_preview",
        "clarification_preview",
        "uncertainty_preview",
    ),
    "selection_blocked_boundary": (
        "blocked_preview",
        "refusal_preview",
    ),
    "selection_refused_boundary": ("refusal_preview",),
}

ALLOWED_DIMENSION_STATES = (
    "preserve_required",
    "explicit_not_applicable",
    "preserve_unknown",
)

ALLOWED_TEMPLATE_IDS = (
    "slice17.explanation.v1",
    "slice17.status.v1",
    "slice17.clarification.v1",
    "slice17.held.v1",
    "slice17.blocked.v1",
    "slice17.refusal.v1",
    "slice17.uncertainty.v1",
)

TEMPLATE_BY_PREVIEW_KIND = {
    "explanation_preview": "slice17.explanation.v1",
    "status_preview": "slice17.status.v1",
    "clarification_preview": "slice17.clarification.v1",
    "held_preview": "slice17.held.v1",
    "blocked_preview": "slice17.blocked.v1",
    "refusal_preview": "slice17.refusal.v1",
    "uncertainty_preview": "slice17.uncertainty.v1",
}

PREFIX_BY_PREVIEW_KIND = {
    "explanation_preview": "Explanation preview",
    "status_preview": "Status preview",
    "clarification_preview": "Clarification preview",
    "held_preview": "Held preview",
    "blocked_preview": "Blocked preview",
    "refusal_preview": "Refusal preview",
    "uncertainty_preview": "Uncertainty preview",
}


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def stable_expression_id(prefix: str, *parts: Any) -> str:
    body = {"prefix": prefix, "parts": [_canonicalize(part) for part in parts]}
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ValidationIssue:
    field: str
    reason: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    ok: bool
    issues: Tuple[ValidationIssue, ...] = ()

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def issue(field: str, reason: str) -> ValidationIssue:
    return ValidationIssue(field=field, reason=reason)


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def tuple_of_text(value: Any, *, allow_empty: bool = True) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    return all(isinstance(item, str) and bool(item.strip()) for item in value)


def unique_tuple(value: Tuple[str, ...]) -> bool:
    return len(value) == len(set(value))


def check_false_only(
    record: Any,
    issues: list[ValidationIssue],
    namespace: str,
) -> None:
    for field_name in EXPRESSION_FALSE_ONLY_FIELDS:
        if bool(getattr(record, field_name, False)):
            issues.append(issue(field_name, f"{namespace}:{field_name}_must_remain_false"))


def false_only_defaults() -> Dict[str, bool]:
    return {field_name: False for field_name in EXPRESSION_FALSE_ONLY_FIELDS}


def normalized_contains(text: str, marker: str) -> bool:
    return marker.casefold() in text.casefold()


def contains_word_or_phrase(text: str, phrase: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(phrase.casefold()) + r"(?!\w)"
    return re.search(pattern, text.casefold()) is not None


def all_required_markers_present(text: str, markers: Tuple[str, ...]) -> bool:
    return all(normalized_contains(text, marker) for marker in markers)


def no_forbidden_markers_present(text: str, markers: Tuple[str, ...]) -> bool:
    return all(not contains_word_or_phrase(text, marker) for marker in markers)


def expression_scope_record() -> Dict[str, object]:
    scope: Dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "inspection_boundary_only": True,
        "represents_expression_source_binding": True,
        "represents_preservation_contract": True,
        "represents_deterministic_expression_plan": True,
        "represents_unapproved_expression_preview": True,
        "represents_hard_fidelity_gate": True,
        "represents_structural_receipt": True,
        "required_expression_laws": REQUIRED_EXPRESSION_LAWS,
        "preservation_dimensions": (
            "negation",
            "condition",
            "modality",
            "attribution",
            "scope",
            "refusal_relevance",
            "uncertainty",
        ),
        "preview_status": "unapproved_boundary_preview_only",
        "truth_status": "not_truth_decision",
        "proof_status": "not_proof",
        "authority_status": "not_authority",
        "acceptance_status": "not_acceptance",
        "permission_status": "not_permission",
        "delivery_status": "not_delivery",
        "execution_status": "not_execution",
        "gp014_status": "protected_not_imported_not_superseded",
        "gp015_status": "failed_not_repaired",
        "frozen_legacy_status": "evidence_only_not_imported_not_called",
    }
    scope.update(false_only_defaults())
    return scope
