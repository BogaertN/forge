from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_separation_id, tuple_of_text

ALLOWED_AUTHORITY_REFERENCE_STATUSES = ("reference_only", "blocked_reference", "requires_separate_acceptance")
ALLOWED_AUTHORITY_EFFECTS = ("none", "no_authority_granted")


@dataclass(frozen=True)
class AuthorityReferenceRecord:
    authority_reference_id: str
    authority_key: str
    referenced_authority_ref: str
    authority_reference_status: str
    authority_effect: str
    allowed_scope_refs: Tuple[str, ...]
    blocked_scope_refs: Tuple[str, ...]
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
            "authority_key": self.authority_key,
            "referenced_authority_ref": self.referenced_authority_ref,
            "authority_reference_status": self.authority_reference_status,
            "authority_effect": self.authority_effect,
            "allowed_scope_refs": self.allowed_scope_refs,
            "blocked_scope_refs": self.blocked_scope_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("authority-reference", self.canonical_body())


def build_authority_reference_record(
    *,
    authority_key: str,
    referenced_authority_ref: str,
    authority_reference_status: str,
    authority_effect: str,
    allowed_scope_refs: Tuple[str, ...],
    blocked_scope_refs: Tuple[str, ...],
) -> AuthorityReferenceRecord:
    body = {
        "authority_key": authority_key,
        "referenced_authority_ref": referenced_authority_ref,
        "authority_reference_status": authority_reference_status,
        "authority_effect": authority_effect,
        "allowed_scope_refs": allowed_scope_refs,
        "blocked_scope_refs": blocked_scope_refs,
        "version_tag": "v1",
    }
    return AuthorityReferenceRecord(authority_reference_id=stable_separation_id("authority-reference", body), **body)


def validate_authority_reference_record(record: AuthorityReferenceRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("authority_reference_id", "authority_key", "referenced_authority_ref", "authority_reference_status", "authority_effect"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.authority_reference_status not in ALLOWED_AUTHORITY_REFERENCE_STATUSES:
        issues.append(issue("authority_reference_status", "unsupported_authority_reference_status"))
    if record.authority_effect not in ALLOWED_AUTHORITY_EFFECTS:
        issues.append(issue("authority_effect", "authority_reference_must_not_grant_authority"))
    if not tuple_of_text(record.allowed_scope_refs):
        issues.append(issue("allowed_scope_refs", "must_be_tuple_of_text"))
    if not tuple_of_text(record.blocked_scope_refs, allow_empty=False):
        issues.append(issue("blocked_scope_refs", "must_be_nonempty_tuple_of_text"))
    if record.authority_reference_id != record.expected_id():
        issues.append(issue("authority_reference_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "authority_reference")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_authority_reference_record() -> AuthorityReferenceRecord:
    return build_authority_reference_record(
        authority_key="slice15-boundary-authority-reference",
        referenced_authority_ref="post-slice14-inspection-record",
        authority_reference_status="reference_only",
        authority_effect="none",
        allowed_scope_refs=("may-reference-record",),
        blocked_scope_refs=("authority_grant", "corpus_authority", "external_truth_authority"),
    )
