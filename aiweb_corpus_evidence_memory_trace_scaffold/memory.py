from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import DOWNSTREAM_FALSE_ONLY_FIELDS, SCHEMA_VERSION, ValidationIssue, ValidationReport, check_false_only, issue, nonempty_text, stable_separation_id, tuple_of_text

ALLOWED_MEMORY_STATUSES = ("memory_record_only", "candidate_memory_record", "custody_only_not_written")
ALLOWED_MEMORY_ORIGINS = ("user_supplied", "inspection_note", "operator_note", "system_boundary_note")
ALLOWED_EXTERNAL_TRUTH_STATUSES = ("not_external_truth", "external_truth_requires_separate_evidence_and_validation")
ALLOWED_REQUEST_STATUSES = ("request_record_only", "not_executed", "requires_separate_authorization")
ALLOWED_REQUESTED_OPERATIONS = ("remember_request", "update_request", "forget_request", "inspect_request")
ALLOWED_WRITE_EFFECTS = ("no_write", "no_memory_change")


@dataclass(frozen=True)
class MemoryRecord:
    memory_record_id: str
    memory_key: str
    memory_subject_ref: str
    memory_payload_ref: str
    memory_origin_kind: str
    memory_custody_status: str
    evidence_ref_status: str
    external_truth_status: str
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
            "memory_key": self.memory_key,
            "memory_subject_ref": self.memory_subject_ref,
            "memory_payload_ref": self.memory_payload_ref,
            "memory_origin_kind": self.memory_origin_kind,
            "memory_custody_status": self.memory_custody_status,
            "evidence_ref_status": self.evidence_ref_status,
            "external_truth_status": self.external_truth_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("memory", self.canonical_body())


@dataclass(frozen=True)
class MemoryRequestRecord:
    memory_request_id: str
    request_key: str
    request_ref: str
    requested_operation: str
    request_status: str
    write_effect: str
    required_authorization_ref: str
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
            "request_key": self.request_key,
            "request_ref": self.request_ref,
            "requested_operation": self.requested_operation,
            "request_status": self.request_status,
            "write_effect": self.write_effect,
            "required_authorization_ref": self.required_authorization_ref,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_separation_id("memory-request", self.canonical_body())


def build_memory_record(
    *,
    memory_key: str,
    memory_subject_ref: str,
    memory_payload_ref: str,
    memory_origin_kind: str,
    memory_custody_status: str,
    evidence_ref_status: str,
    external_truth_status: str,
) -> MemoryRecord:
    body = {
        "memory_key": memory_key,
        "memory_subject_ref": memory_subject_ref,
        "memory_payload_ref": memory_payload_ref,
        "memory_origin_kind": memory_origin_kind,
        "memory_custody_status": memory_custody_status,
        "evidence_ref_status": evidence_ref_status,
        "external_truth_status": external_truth_status,
        "version_tag": "v1",
    }
    return MemoryRecord(memory_record_id=stable_separation_id("memory", body), **body)


def build_memory_request_record(
    *,
    request_key: str,
    request_ref: str,
    requested_operation: str,
    request_status: str,
    write_effect: str,
    required_authorization_ref: str,
) -> MemoryRequestRecord:
    body = {
        "request_key": request_key,
        "request_ref": request_ref,
        "requested_operation": requested_operation,
        "request_status": request_status,
        "write_effect": write_effect,
        "required_authorization_ref": required_authorization_ref,
        "version_tag": "v1",
    }
    return MemoryRequestRecord(memory_request_id=stable_separation_id("memory-request", body), **body)


def validate_memory_record(record: MemoryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("memory_record_id", "memory_key", "memory_subject_ref", "memory_payload_ref", "memory_origin_kind", "memory_custody_status", "evidence_ref_status", "external_truth_status"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.memory_origin_kind not in ALLOWED_MEMORY_ORIGINS:
        issues.append(issue("memory_origin_kind", "unsupported_memory_origin_kind"))
    if record.memory_custody_status not in ALLOWED_MEMORY_STATUSES:
        issues.append(issue("memory_custody_status", "unsupported_memory_status"))
    if record.evidence_ref_status not in ("not_evidence", "evidence_requires_separate_record"):
        issues.append(issue("evidence_ref_status", "memory_must_not_be_evidence"))
    if record.external_truth_status not in ALLOWED_EXTERNAL_TRUTH_STATUSES:
        issues.append(issue("external_truth_status", "memory_must_not_be_external_truth"))
    if record.memory_record_id != record.expected_id():
        issues.append(issue("memory_record_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "memory")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def validate_memory_request_record(record: MemoryRequestRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in ("memory_request_id", "request_key", "request_ref", "requested_operation", "request_status", "write_effect", "required_authorization_ref"):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.requested_operation not in ALLOWED_REQUESTED_OPERATIONS:
        issues.append(issue("requested_operation", "unsupported_requested_operation"))
    if record.request_status not in ALLOWED_REQUEST_STATUSES:
        issues.append(issue("request_status", "unsupported_request_status"))
    if record.write_effect not in ALLOWED_WRITE_EFFECTS:
        issues.append(issue("write_effect", "memory_request_must_not_write_memory"))
    if record.memory_request_id != record.expected_id():
        issues.append(issue("memory_request_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "memory_request")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_memory_record() -> MemoryRecord:
    return build_memory_record(
        memory_key="operator-context-boundary-note",
        memory_subject_ref="slice15-hard-boundary",
        memory_payload_ref="memory is not external truth",
        memory_origin_kind="operator_note",
        memory_custody_status="custody_only_not_written",
        evidence_ref_status="not_evidence",
        external_truth_status="not_external_truth",
    )


def demo_memory_request_record() -> MemoryRequestRecord:
    return build_memory_request_record(
        request_key="remember-request-example",
        request_ref="user-said-remember-this",
        requested_operation="remember_request",
        request_status="request_record_only",
        write_effect="no_write",
        required_authorization_ref="future-memory-write-gate-not-slice15",
    )
