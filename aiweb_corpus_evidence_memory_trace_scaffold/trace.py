from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_separation_id, tuple_of_text

ALLOWED_TRACE_KINDS = ("decision_trace", "test_trace", "verifier_trace", "boundary_trace", "operator_trace")
ALLOWED_TRACE_STATUSES = ("trace_record_only", "custody_record_only", "not_unrestricted_corpus")
ALLOWED_CORPUS_STATUSES = ("not_corpus", "corpus_requires_separate_entry", "restricted_trace_reference_only")


@dataclass(frozen=True)
class TraceRecord:
    trace_record_id: str
    trace_key: str
    trace_kind: str
    trace_status: str
    trace_origin_ref: str
    trace_event_refs: Tuple[str, ...]
    corpus_status: str
    permission_status: str
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
            "trace_key": self.trace_key,
            "trace_kind": self.trace_kind,
            "trace_status": self.trace_status,
            "trace_origin_ref": self.trace_origin_ref,
            "trace_event_refs": self.trace_event_refs,
            "corpus_status": self.corpus_status,
            "permission_status": self.permission_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("trace", self.canonical_body())


def build_trace_record(
    *,
    trace_key: str,
    trace_kind: str,
    trace_status: str,
    trace_origin_ref: str,
    trace_event_refs: Tuple[str, ...],
    corpus_status: str,
    permission_status: str,
) -> TraceRecord:
    body = {
        "trace_key": trace_key,
        "trace_kind": trace_kind,
        "trace_status": trace_status,
        "trace_origin_ref": trace_origin_ref,
        "trace_event_refs": trace_event_refs,
        "corpus_status": corpus_status,
        "permission_status": permission_status,
        "version_tag": "v1",
    }
    return TraceRecord(trace_record_id=stable_separation_id("trace", body), **body)


def validate_trace_record(record: TraceRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("trace_record_id", "trace_key", "trace_kind", "trace_status", "trace_origin_ref", "corpus_status", "permission_status"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.trace_kind not in ALLOWED_TRACE_KINDS:
        issues.append(issue("trace_kind", "unsupported_trace_kind"))
    if record.trace_status not in ALLOWED_TRACE_STATUSES:
        issues.append(issue("trace_status", "unsupported_trace_status"))
    if record.corpus_status not in ALLOWED_CORPUS_STATUSES:
        issues.append(issue("corpus_status", "trace_must_not_be_unrestricted_corpus"))
    if record.permission_status not in ("not_permission", "permission_requires_separate_authorization"):
        issues.append(issue("permission_status", "trace_must_not_be_permission"))
    if not tuple_of_text(record.trace_event_refs, allow_empty=False):
        issues.append(issue("trace_event_refs", "must_be_nonempty_tuple_of_text"))
    if record.trace_record_id != record.expected_id():
        issues.append(issue("trace_record_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "trace")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_trace_record() -> TraceRecord:
    return build_trace_record(
        trace_key="slice15-design-trace",
        trace_kind="boundary_trace",
        trace_status="trace_record_only",
        trace_origin_ref="source-authority-packet-inspection",
        trace_event_refs=("packet-verified", "source-inspected", "patch-designed-after-inspection"),
        corpus_status="not_corpus",
        permission_status="not_permission",
    )
