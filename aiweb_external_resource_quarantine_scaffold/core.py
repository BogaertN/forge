from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-external-resource-quarantine-scaffold-v1"
SCOPE_STATUS = "external_resource_quarantine_scaffold_only"
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


def stable_quarantine_id(prefix: str, *parts: Any) -> str:
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


def tuple_of_text(value: Tuple[str, ...], *, allow_empty: bool = True) -> bool:
    if not isinstance(value, tuple):
        return False
    if not allow_empty and not value:
        return False
    return all(isinstance(item, str) and bool(item.strip()) for item in value)


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_false_only(record: Any, fields: Tuple[str, ...], issues: list[ValidationIssue], namespace: str) -> None:
    for field_name in fields:
        if bool(getattr(record, field_name, False)):
            issues.append(issue(field_name, f"{namespace}:{field_name}_must_remain_false"))


DOWNSTREAM_FALSE_ONLY_FIELDS = (
    "live_runtime_behavior",
    "resource_fetch",
    "resource_ingestion",
    "resource_parsing",
    "resource_indexing",
    "resource_download",
    "license_runtime_permission",
    "license_public_claim_permission",
    "license_redistribution_permission",
    "external_resource_admission",
    "runtime_promotion",
    "authority_grant",
    "corpus_authority",
    "evidence_validation",
    "memory_write",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "action_authorization",
    "selected_meaning",
    "final_meaning_selection",
    "truth_decision",
    "live_clarification",
    "user_facing_question_emission",
    "concept_graph_replacement",
    "predicate_registry_replacement",
    "wordnet_concept_graph",
    "verbnet_predicate_registry",
    "sanskrit_runtime_support",
    "paninian_parser_runtime",
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


def external_resource_quarantine_scope_record() -> Dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "represents_external_resource_identity": True,
        "represents_provenance_custody": True,
        "represents_license_custody": True,
        "represents_quarantine_status": True,
        "represents_hold_status": True,
        "represents_rejection_status": True,
        "represents_admission_candidate_status": True,
        "represents_permitted_purpose": True,
        "represents_blocked_purpose": True,
        "represents_source_custody": True,
        "represents_resource_scope": True,
        "represents_admission_receipt": True,
        "represents_resource_decision_boundary": True,
        "represents_resource_quarantine_trace": True,
        "represents_external_resource_authority_boundary": True,
        "live_runtime_behavior": False,
        "resource_fetch": False,
        "resource_ingestion": False,
        "resource_parsing": False,
        "resource_indexing": False,
        "resource_download": False,
        "license_runtime_permission": False,
        "license_public_claim_permission": False,
        "license_redistribution_permission": False,
        "external_resource_admission": False,
        "runtime_promotion": False,
        "authority_grant": False,
        "corpus_authority": False,
        "evidence_validation": False,
        "memory_write": False,
        "tool_invocation": False,
        "capability_route": False,
        "delivery_action": False,
        "action_authorization": False,
        "selected_meaning": False,
        "final_meaning_selection": False,
        "truth_decision": False,
        "live_clarification": False,
        "user_facing_question_emission": False,
        "concept_graph_replacement": False,
        "predicate_registry_replacement": False,
        "wordnet_concept_graph": False,
        "verbnet_predicate_registry": False,
        "sanskrit_runtime_support": False,
        "paninian_parser_runtime": False,
        "model_authority": False,
        "vector_authority": False,
        "retrieval_authority": False,
        "similarity_authority": False,
        "embedding_index_creation": False,
        "rag_execution": False,
        "training_authority": False,
        "gp014_supersession": False,
        "gp014_status": "protected_not_superseded",
        "gp015_repair": False,
        "gp015_status": "failed_not_repaired",
        "gp015r1_installation": False,
        "gp015r1_status": "uninstalled_not_live",
        "wordnet_status": "quarantined_candidate_only",
        "sanskrit_wordnet_status": "hold_unadmitted",
        "verbnet_status": "quarantined_candidate_only",
        "framenet_status": "quarantined_candidate_only",
        "paninian_resource_status": "hold_unadmitted",
        "release_authority": False,
        "production_readiness": False,
    }
