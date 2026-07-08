from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Mapping, Tuple

SCHEMA_VERSION = "aiweb-corpus-evidence-memory-trace-separation-scaffold-v1"
SCOPE_STATUS = "corpus_evidence_memory_trace_separation_scaffold_only"
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


def stable_separation_id(prefix: str, *parts: Any) -> str:
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


DOWNSTREAM_FALSE_ONLY_FIELDS = (
    "live_runtime_behavior",
    "source_mention_promotion",
    "source_mention_as_evidence",
    "example_as_proof",
    "evidence_validation",
    "evidence_as_memory",
    "memory_write",
    "memory_request_execution",
    "memory_as_external_truth",
    "trace_unrestricted_corpus",
    "trace_to_corpus_promotion",
    "corpus_authority",
    "corpus_as_truth",
    "authority_grant",
    "external_truth_authority",
    "external_resource_admission",
    "runtime_promotion",
    "resource_fetch",
    "resource_download",
    "resource_ingestion",
    "resource_parsing",
    "resource_indexing",
    "tool_invocation",
    "capability_route",
    "delivery_action",
    "action_authorization",
    "selected_meaning",
    "final_meaning_selection",
    "truth_decision",
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

REQUIRED_SEPARATION_LAWS = (
    "source_mention_is_not_evidence",
    "evidence_is_not_memory",
    "memory_is_not_external_truth",
    "trace_is_not_unrestricted_corpus",
    "memory_request_does_not_write_memory",
    "corpus_presence_is_not_authority",
    "example_is_not_proof",
    "trace_is_not_permission",
    "evidence_custody_is_not_evidence_validation",
    "memory_custody_is_not_memory_write_authority",
)


def corpus_evidence_memory_trace_scope_record() -> Dict[str, object]:
    scope: Dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "status": SCOPE_STATUS,
        "runtime_effect": RUNTIME_EFFECT,
        "dependency_change": DEPENDENCY_CHANGE,
        "scaffold_only": True,
        "represents_category_boundary": True,
        "represents_source_mention_record": True,
        "represents_example_record": True,
        "represents_evidence_record": True,
        "represents_evidence_custody": True,
        "represents_memory_record": True,
        "represents_memory_request": True,
        "represents_trace_record": True,
        "represents_corpus_entry": True,
        "represents_authority_reference": True,
        "represents_separation_assertion": True,
        "required_separation_laws": REQUIRED_SEPARATION_LAWS,
        "gp014_status": "protected_not_superseded",
        "gp015_status": "failed_not_repaired",
        "gp015r1_status": "uninstalled_not_live",
        "external_resources_status": "unadmitted",
        "sanskrit_wordnet_status": "hold_unadmitted",
        "wordnet_status": "quarantined_candidate_only_not_concept_graph",
        "verbnet_status": "quarantined_candidate_only_not_predicate_registry",
        "trace_status": "trace_records_not_unrestricted_corpus",
        "memory_status": "memory_records_not_external_truth",
        "evidence_status": "evidence_records_not_memory_and_not_validated_by_presence",
        "corpus_status": "corpus_entries_not_authority",
    }
    for key in DOWNSTREAM_FALSE_ONLY_FIELDS:
        scope[key] = False
    return scope
