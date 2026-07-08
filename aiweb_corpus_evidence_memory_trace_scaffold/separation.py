from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, REQUIRED_SEPARATION_LAWS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_separation_id

ALLOWED_SEPARATION_KINDS = REQUIRED_SEPARATION_LAWS
ALLOWED_ASSERTION_STATUSES = ("separation_asserted", "collapse_blocked", "boundary_law_record_only")


@dataclass(frozen=True)
class SeparationAssertionRecord:
    separation_assertion_id: str
    assertion_key: str
    separation_kind: str
    left_category: str
    right_category: str
    assertion_status: str
    collapse_forbidden: bool
    enforcement_note: str
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
            "assertion_key": self.assertion_key,
            "separation_kind": self.separation_kind,
            "left_category": self.left_category,
            "right_category": self.right_category,
            "assertion_status": self.assertion_status,
            "collapse_forbidden": self.collapse_forbidden,
            "enforcement_note": self.enforcement_note,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("separation", self.canonical_body())


def build_separation_assertion_record(
    *,
    assertion_key: str,
    separation_kind: str,
    left_category: str,
    right_category: str,
    assertion_status: str,
    collapse_forbidden: bool,
    enforcement_note: str,
) -> SeparationAssertionRecord:
    body = {
        "assertion_key": assertion_key,
        "separation_kind": separation_kind,
        "left_category": left_category,
        "right_category": right_category,
        "assertion_status": assertion_status,
        "collapse_forbidden": collapse_forbidden,
        "enforcement_note": enforcement_note,
        "version_tag": "v1",
    }
    return SeparationAssertionRecord(separation_assertion_id=stable_separation_id("separation", body), **body)


def validate_separation_assertion_record(record: SeparationAssertionRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("separation_assertion_id", "assertion_key", "separation_kind", "left_category", "right_category", "assertion_status", "enforcement_note"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.separation_kind not in ALLOWED_SEPARATION_KINDS:
        issues.append(issue("separation_kind", "unsupported_separation_kind"))
    if record.assertion_status not in ALLOWED_ASSERTION_STATUSES:
        issues.append(issue("assertion_status", "unsupported_assertion_status"))
    if record.collapse_forbidden is not True:
        issues.append(issue("collapse_forbidden", "category_collapse_must_be_forbidden"))
    if record.separation_assertion_id != record.expected_id():
        issues.append(issue("separation_assertion_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "separation_assertion")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_source_mention_not_evidence_assertion() -> SeparationAssertionRecord:
    return build_separation_assertion_record(
        assertion_key="source-mention-not-evidence",
        separation_kind="source_mention_is_not_evidence",
        left_category="source_mention",
        right_category="evidence",
        assertion_status="collapse_blocked",
        collapse_forbidden=True,
        enforcement_note="A source may be mentioned without becoming evidence.",
    )


def demo_evidence_not_memory_assertion() -> SeparationAssertionRecord:
    return build_separation_assertion_record(
        assertion_key="evidence-not-memory",
        separation_kind="evidence_is_not_memory",
        left_category="evidence",
        right_category="memory",
        assertion_status="collapse_blocked",
        collapse_forbidden=True,
        enforcement_note="Evidence custody cannot create a memory record or memory write.",
    )


def demo_memory_not_external_truth_assertion() -> SeparationAssertionRecord:
    return build_separation_assertion_record(
        assertion_key="memory-not-external-truth",
        separation_kind="memory_is_not_external_truth",
        left_category="memory",
        right_category="external_truth",
        assertion_status="collapse_blocked",
        collapse_forbidden=True,
        enforcement_note="Remembered material remains memory custody, not truth about the world.",
    )


def demo_trace_not_unrestricted_corpus_assertion() -> SeparationAssertionRecord:
    return build_separation_assertion_record(
        assertion_key="trace-not-unrestricted-corpus",
        separation_kind="trace_is_not_unrestricted_corpus",
        left_category="trace",
        right_category="corpus_entry",
        assertion_status="collapse_blocked",
        collapse_forbidden=True,
        enforcement_note="Trace material may not be treated as unrestricted corpus.",
    )


def demo_memory_request_no_write_assertion() -> SeparationAssertionRecord:
    return build_separation_assertion_record(
        assertion_key="memory-request-no-write",
        separation_kind="memory_request_does_not_write_memory",
        left_category="memory_request",
        right_category="memory_write",
        assertion_status="collapse_blocked",
        collapse_forbidden=True,
        enforcement_note="A memory request is represented only and has no write effect.",
    )


def demo_required_separation_assertions() -> Tuple[SeparationAssertionRecord, ...]:
    return (
        demo_source_mention_not_evidence_assertion(),
        demo_evidence_not_memory_assertion(),
        demo_memory_not_external_truth_assertion(),
        demo_trace_not_unrestricted_corpus_assertion(),
        demo_memory_request_no_write_assertion(),
    )
