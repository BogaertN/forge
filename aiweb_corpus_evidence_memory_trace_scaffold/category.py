from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    check_false_only,
    issue,
    nonempty_text,
    stable_separation_id,
    tuple_of_text,
)

ALLOWED_CATEGORY_KINDS = (
    "source_mention",
    "example",
    "evidence",
    "memory",
    "memory_request",
    "trace",
    "corpus_entry",
    "authority_reference",
)

ALLOWED_CATEGORY_STATUSES = (
    "category_boundary_only",
    "custody_record_only",
    "reference_record_only",
    "request_record_only",
)


@dataclass(frozen=True)
class CategoryBoundaryRecord:
    category_boundary_id: str
    category_key: str
    category_kind: str
    category_status: str
    category_description: str
    allowed_relation_refs: Tuple[str, ...]
    blocked_relation_refs: Tuple[str, ...]
    version_tag: str = "v1"
    live_runtime_behavior: bool = False
    source_mention_promotion: bool = False
    source_mention_as_evidence: bool = False
    example_as_proof: bool = False
    evidence_validation: bool = False
    evidence_as_memory: bool = False
    memory_write: bool = False
    memory_request_execution: bool = False
    memory_as_external_truth: bool = False
    trace_unrestricted_corpus: bool = False
    trace_to_corpus_promotion: bool = False
    corpus_authority: bool = False
    corpus_as_truth: bool = False
    authority_grant: bool = False
    external_truth_authority: bool = False
    external_resource_admission: bool = False
    runtime_promotion: bool = False
    resource_fetch: bool = False
    resource_download: bool = False
    resource_ingestion: bool = False
    resource_parsing: bool = False
    resource_indexing: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    action_authorization: bool = False
    selected_meaning: bool = False
    final_meaning_selection: bool = False
    truth_decision: bool = False
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
            "category_key": self.category_key,
            "category_kind": self.category_kind,
            "category_status": self.category_status,
            "category_description": self.category_description,
            "allowed_relation_refs": self.allowed_relation_refs,
            "blocked_relation_refs": self.blocked_relation_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("category", self.canonical_body())


def build_category_boundary_record(
    *,
    category_key: str,
    category_kind: str,
    category_status: str,
    category_description: str,
    allowed_relation_refs: Tuple[str, ...],
    blocked_relation_refs: Tuple[str, ...],
) -> CategoryBoundaryRecord:
    body = {
        "category_key": category_key,
        "category_kind": category_kind,
        "category_status": category_status,
        "category_description": category_description,
        "allowed_relation_refs": allowed_relation_refs,
        "blocked_relation_refs": blocked_relation_refs,
        "version_tag": "v1",
    }
    return CategoryBoundaryRecord(category_boundary_id=stable_separation_id("category", body), **body)


def validate_category_boundary_record(record: CategoryBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("category_boundary_id", "category_key", "category_kind", "category_status", "category_description"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.category_kind not in ALLOWED_CATEGORY_KINDS:
        issues.append(issue("category_kind", "unsupported_category_kind"))
    if record.category_status not in ALLOWED_CATEGORY_STATUSES:
        issues.append(issue("category_status", "unsupported_category_status"))
    if not tuple_of_text(record.allowed_relation_refs):
        issues.append(issue("allowed_relation_refs", "must_be_tuple_of_text"))
    if not tuple_of_text(record.blocked_relation_refs, allow_empty=False):
        issues.append(issue("blocked_relation_refs", "must_be_nonempty_tuple_of_text"))
    if record.category_boundary_id != record.expected_id():
        issues.append(issue("category_boundary_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "category_boundary")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_category_boundary_record() -> CategoryBoundaryRecord:
    return build_category_boundary_record(
        category_key="source-mention-category",
        category_kind="source_mention",
        category_status="category_boundary_only",
        category_description="A source mention can reference a source but cannot validate evidence or create memory.",
        allowed_relation_refs=("may_reference_source_locator",),
        blocked_relation_refs=("source_mention_is_not_evidence", "source_mention_promotion"),
    )
