from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_separation_id, tuple_of_text

ALLOWED_EVIDENCE_KINDS = ("inspection_record", "packet_checksum", "test_output", "verifier_output", "human_supplied_record", "custody_note")
ALLOWED_EVIDENCE_CUSTODY_STATUSES = ("custody_record_only", "candidate_evidence_record", "not_validated")
ALLOWED_VALIDATION_STATUSES = ("not_validated", "validation_required_separate_process")
ALLOWED_MEMORY_STATUSES = ("not_memory", "memory_requires_separate_record")


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_record_id: str
    evidence_key: str
    evidence_kind: str
    evidence_custody_status: str
    evidence_ref: str
    source_mention_refs: Tuple[str, ...]
    claim_refs: Tuple[str, ...]
    validation_status: str
    memory_status: str
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
            "evidence_key": self.evidence_key,
            "evidence_kind": self.evidence_kind,
            "evidence_custody_status": self.evidence_custody_status,
            "evidence_ref": self.evidence_ref,
            "source_mention_refs": self.source_mention_refs,
            "claim_refs": self.claim_refs,
            "validation_status": self.validation_status,
            "memory_status": self.memory_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("evidence", self.canonical_body())


def build_evidence_record(
    *,
    evidence_key: str,
    evidence_kind: str,
    evidence_custody_status: str,
    evidence_ref: str,
    source_mention_refs: Tuple[str, ...],
    claim_refs: Tuple[str, ...],
    validation_status: str,
    memory_status: str,
) -> EvidenceRecord:
    body = {
        "evidence_key": evidence_key,
        "evidence_kind": evidence_kind,
        "evidence_custody_status": evidence_custody_status,
        "evidence_ref": evidence_ref,
        "source_mention_refs": source_mention_refs,
        "claim_refs": claim_refs,
        "validation_status": validation_status,
        "memory_status": memory_status,
        "version_tag": "v1",
    }
    return EvidenceRecord(evidence_record_id=stable_separation_id("evidence", body), **body)


def validate_evidence_record(record: EvidenceRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("evidence_record_id", "evidence_key", "evidence_kind", "evidence_custody_status", "evidence_ref", "validation_status", "memory_status"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.evidence_kind not in ALLOWED_EVIDENCE_KINDS:
        issues.append(issue("evidence_kind", "unsupported_evidence_kind"))
    if record.evidence_custody_status not in ALLOWED_EVIDENCE_CUSTODY_STATUSES:
        issues.append(issue("evidence_custody_status", "unsupported_evidence_custody_status"))
    if record.validation_status not in ALLOWED_VALIDATION_STATUSES:
        issues.append(issue("validation_status", "evidence_presence_must_not_validate_evidence"))
    if record.memory_status not in ALLOWED_MEMORY_STATUSES:
        issues.append(issue("memory_status", "evidence_must_not_be_memory"))
    if not tuple_of_text(record.source_mention_refs):
        issues.append(issue("source_mention_refs", "must_be_tuple_of_text"))
    if not tuple_of_text(record.claim_refs):
        issues.append(issue("claim_refs", "must_be_tuple_of_text"))
    if record.evidence_record_id != record.expected_id():
        issues.append(issue("evidence_record_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "evidence")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_evidence_record() -> EvidenceRecord:
    return build_evidence_record(
        evidence_key="slice14-closeout-record",
        evidence_kind="inspection_record",
        evidence_custody_status="custody_record_only",
        evidence_ref="AIWEB_POST_SLICE14_COMMITTED_STATE_INSPECTION_RECORD_20260708_160012_UTC.txt",
        source_mention_refs=("source-mention:policy-doc-mentioned",),
        claim_refs=("slice14_clean_head", "full_slice1_14_tests_passed"),
        validation_status="not_validated",
        memory_status="not_memory",
    )
