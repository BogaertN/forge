from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-selected-meaning-boundary-scaffold-v1"
SCOPE_STATUS = "selected_meaning_boundary_scaffold_only"
RUNTIME_EFFECT = "none"
DEPENDENCY_CHANGE = "none"


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonicalize(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(_canonicalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_selection_id(prefix: str, *parts: Any) -> str:
    body = {"prefix": prefix, "parts": [_canonicalize(part) for part in parts]}
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


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


def tuple_of_text(value: Tuple[str, ...], *, allow_empty: bool = True) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    return all(isinstance(item, str) and bool(item.strip()) for item in value)


def check_false_only(record: Any, fields: Tuple[str, ...], issues: list[ValidationIssue], namespace: str) -> None:
    for field_name in fields:
        if bool(getattr(record, field_name, False)):
            issues.append(issue(field_name, f"{namespace}:{field_name}_must_remain_false"))


SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS = (
    "live_runtime_behavior",
    "live_runtime_interpretation",
    "selection_as_truth",
    "selection_as_permission",
    "selection_as_delivery",
    "selection_as_execution",
    "selection_finalization",
    "final_meaning_selection",
    "truth_decision",
    "permission_grant",
    "action_authorization",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "execution_authority",
    "output_rendering",
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
    "live_clarification",
    "user_facing_question_emission",
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

REQUIRED_SELECTION_LAWS = (
    "selected_meaning_is_not_truth",
    "selected_meaning_is_not_permission",
    "selected_meaning_is_not_delivery",
    "selected_meaning_is_not_execution",
    "selected_meaning_is_not_final_meaning_selection",
    "selected_meaning_is_not_evidence_validation",
    "selected_meaning_is_not_memory_authority",
    "selected_meaning_is_not_tool_routing",
    "selected_meaning_is_not_output_rendering",
)

REQUIRED_PRIOR_BOUNDARIES = (
    "slice7_meaning_law_trace_boundary",
    "slice8_concept_boundary",
    "slice9_predicate_role_boundary",
    "slice10_verbal_cognition_gate_boundary",
    "slice11_candidate_meaning_boundary",
    "slice12_ambiguity_clarification_boundary",
    "slice13_requirements_traceability_boundary",
    "slice14_external_resource_quarantine_boundary",
    "slice15_corpus_evidence_memory_trace_boundary",
)


def selected_meaning_scope_record() -> Dict[str, object]:
    scope: Dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "represents_selected_meaning_boundary": True,
        "represents_candidate_selection_reference": True,
        "represents_selection_basis_reference": True,
        "represents_selection_constraint_reference": True,
        "represents_selection_trace_reference": True,
        "represents_non_selected_candidate_reference": True,
        "represents_selection_confidence_boundary": True,
        "represents_selection_uncertainty_boundary": True,
        "represents_selection_refusal_boundary": True,
        "represents_selection_blocked_boundary": True,
        "represents_selection_receipt": True,
        "required_selection_laws": REQUIRED_SELECTION_LAWS,
        "required_prior_boundaries": REQUIRED_PRIOR_BOUNDARIES,
        "selection_status": "internal_boundary_record_only",
        "candidate_status": "candidate_reference_only_not_created_or_modified",
        "truth_status": "not_truth_decision",
        "permission_status": "not_permission_grant",
        "delivery_status": "not_delivery",
        "execution_status": "not_execution",
        "memory_status": "not_memory_write_and_not_memory_authority",
        "evidence_status": "not_evidence_validation",
        "corpus_status": "not_corpus_authority",
        "external_resource_status": "unadmitted",
        "gp014_status": "protected_not_superseded",
        "gp015_status": "failed_not_repaired",
        "gp015r1_status": "uninstalled_not_live",
    }
    for key in SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS:
        scope[key] = False
    return scope
