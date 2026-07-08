from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_separation_id, tuple_of_text

ALLOWED_SOURCE_MENTION_STATUSES = ("mentioned_only", "locator_record_only", "citation_candidate_only")
ALLOWED_EVIDENCE_STATUSES = ("not_evidence", "evidence_required_separate_record")


@dataclass(frozen=True)
class SourceMentionRecord:
    source_mention_id: str
    mention_key: str
    source_ref: str
    source_locator_ref: str
    mention_context_ref: str
    mention_status: str
    evidence_status: str
    example_status: str
    note_refs: Tuple[str, ...]
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
            "mention_key": self.mention_key,
            "source_ref": self.source_ref,
            "source_locator_ref": self.source_locator_ref,
            "mention_context_ref": self.mention_context_ref,
            "mention_status": self.mention_status,
            "evidence_status": self.evidence_status,
            "example_status": self.example_status,
            "note_refs": self.note_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("source-mention", self.canonical_body())


def build_source_mention_record(
    *,
    mention_key: str,
    source_ref: str,
    source_locator_ref: str,
    mention_context_ref: str,
    mention_status: str,
    evidence_status: str,
    example_status: str,
    note_refs: Tuple[str, ...],
) -> SourceMentionRecord:
    body = {
        "mention_key": mention_key,
        "source_ref": source_ref,
        "source_locator_ref": source_locator_ref,
        "mention_context_ref": mention_context_ref,
        "mention_status": mention_status,
        "evidence_status": evidence_status,
        "example_status": example_status,
        "note_refs": note_refs,
        "version_tag": "v1",
    }
    return SourceMentionRecord(source_mention_id=stable_separation_id("source-mention", body), **body)


def validate_source_mention_record(record: SourceMentionRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("source_mention_id", "mention_key", "source_ref", "source_locator_ref", "mention_context_ref", "mention_status", "evidence_status", "example_status"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.mention_status not in ALLOWED_SOURCE_MENTION_STATUSES:
        issues.append(issue("mention_status", "unsupported_mention_status"))
    if record.evidence_status not in ALLOWED_EVIDENCE_STATUSES:
        issues.append(issue("evidence_status", "source_mention_must_not_be_evidence"))
    if record.example_status not in ("not_proof", "example_candidate_only"):
        issues.append(issue("example_status", "example_must_not_be_proof"))
    if not tuple_of_text(record.note_refs):
        issues.append(issue("note_refs", "must_be_tuple_of_text"))
    if record.source_mention_id != record.expected_id():
        issues.append(issue("source_mention_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "source_mention")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_source_mention_record() -> SourceMentionRecord:
    return build_source_mention_record(
        mention_key="policy-doc-mentioned",
        source_ref="Forge Language Corpus Evidence Corpus and Memory Governance Policy v1",
        source_locator_ref="drive-document-reference-only",
        mention_context_ref="slice15-source-authority-packet",
        mention_status="mentioned_only",
        evidence_status="not_evidence",
        example_status="not_proof",
        note_refs=("source mention is not evidence",),
    )
