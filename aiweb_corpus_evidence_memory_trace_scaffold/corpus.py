from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_separation_id, tuple_of_text

ALLOWED_CORPUS_KINDS = ("language_example", "test_fixture", "restricted_trace_reference", "candidate_material", "operator_supplied_example")
ALLOWED_CORPUS_STATUSES = ("corpus_entry_record_only", "candidate_corpus_entry", "restricted_not_authority")
ALLOWED_AUTHORITY_STATUSES = ("not_authority", "authority_requires_separate_record")


@dataclass(frozen=True)
class CorpusEntryRecord:
    corpus_entry_id: str
    corpus_key: str
    corpus_kind: str
    corpus_status: str
    material_ref: str
    source_category_refs: Tuple[str, ...]
    use_constraint_refs: Tuple[str, ...]
    authority_status: str
    truth_status: str
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
            "corpus_key": self.corpus_key,
            "corpus_kind": self.corpus_kind,
            "corpus_status": self.corpus_status,
            "material_ref": self.material_ref,
            "source_category_refs": self.source_category_refs,
            "use_constraint_refs": self.use_constraint_refs,
            "authority_status": self.authority_status,
            "truth_status": self.truth_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("corpus-entry", self.canonical_body())


def build_corpus_entry_record(
    *,
    corpus_key: str,
    corpus_kind: str,
    corpus_status: str,
    material_ref: str,
    source_category_refs: Tuple[str, ...],
    use_constraint_refs: Tuple[str, ...],
    authority_status: str,
    truth_status: str,
) -> CorpusEntryRecord:
    body = {
        "corpus_key": corpus_key,
        "corpus_kind": corpus_kind,
        "corpus_status": corpus_status,
        "material_ref": material_ref,
        "source_category_refs": source_category_refs,
        "use_constraint_refs": use_constraint_refs,
        "authority_status": authority_status,
        "truth_status": truth_status,
        "version_tag": "v1",
    }
    return CorpusEntryRecord(corpus_entry_id=stable_separation_id("corpus-entry", body), **body)


def validate_corpus_entry_record(record: CorpusEntryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("corpus_entry_id", "corpus_key", "corpus_kind", "corpus_status", "material_ref", "authority_status", "truth_status"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.corpus_kind not in ALLOWED_CORPUS_KINDS:
        issues.append(issue("corpus_kind", "unsupported_corpus_kind"))
    if record.corpus_status not in ALLOWED_CORPUS_STATUSES:
        issues.append(issue("corpus_status", "unsupported_corpus_status"))
    if record.authority_status not in ALLOWED_AUTHORITY_STATUSES:
        issues.append(issue("authority_status", "corpus_presence_must_not_be_authority"))
    if record.truth_status not in ("not_truth", "truth_requires_separate_validation"):
        issues.append(issue("truth_status", "corpus_must_not_be_truth"))
    if not tuple_of_text(record.source_category_refs, allow_empty=False):
        issues.append(issue("source_category_refs", "must_be_nonempty_tuple_of_text"))
    if not tuple_of_text(record.use_constraint_refs, allow_empty=False):
        issues.append(issue("use_constraint_refs", "must_be_nonempty_tuple_of_text"))
    if record.corpus_entry_id != record.expected_id():
        issues.append(issue("corpus_entry_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "corpus")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_corpus_entry_record() -> CorpusEntryRecord:
    return build_corpus_entry_record(
        corpus_key="example-language-material",
        corpus_kind="language_example",
        corpus_status="corpus_entry_record_only",
        material_ref="example sentence fixture reference only",
        source_category_refs=("example",),
        use_constraint_refs=("example_is_not_proof", "corpus_presence_is_not_authority"),
        authority_status="not_authority",
        truth_status="not_truth",
    )
