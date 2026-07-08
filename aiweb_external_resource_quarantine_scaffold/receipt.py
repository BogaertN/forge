from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    _canonicalize,
    check_false_only,
    issue,
    nonempty_text,
    stable_quarantine_id,
    tuple_of_text,
)

ALLOWED_RECEIPT_STATUS = (
    "admission_receipt_represented_only",
    "hold_receipt_represented_only",
    "rejection_receipt_represented_only",
)

ALLOWED_AUTHORITY_EFFECT = ("none", "blocked", "held")


@dataclass(frozen=True)
class ResourceAdmissionReceiptRecord:
    admission_receipt_id: str
    resource_identity_ref: str
    quarantine_decision_ref: str
    accepted_scope_ref: str
    verifier_ref: str
    result_packet_ref: str
    receipt_status: str
    authority_effect: str
    receipt_notes: Tuple[str, ...]
    version_tag: str = "v1"
    live_runtime_behavior: bool = False
    resource_fetch: bool = False
    resource_ingestion: bool = False
    resource_parsing: bool = False
    resource_indexing: bool = False
    resource_download: bool = False
    license_runtime_permission: bool = False
    license_public_claim_permission: bool = False
    license_redistribution_permission: bool = False
    external_resource_admission: bool = False
    runtime_promotion: bool = False
    authority_grant: bool = False
    corpus_authority: bool = False
    evidence_validation: bool = False
    memory_write: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    delivery_action: bool = False
    action_authorization: bool = False
    selected_meaning: bool = False
    final_meaning_selection: bool = False
    truth_decision: bool = False
    live_clarification: bool = False
    user_facing_question_emission: bool = False
    concept_graph_replacement: bool = False
    predicate_registry_replacement: bool = False
    wordnet_concept_graph: bool = False
    verbnet_predicate_registry: bool = False
    sanskrit_runtime_support: bool = False
    paninian_parser_runtime: bool = False
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
            "resource_identity_ref": self.resource_identity_ref,
            "quarantine_decision_ref": self.quarantine_decision_ref,
            "accepted_scope_ref": self.accepted_scope_ref,
            "verifier_ref": self.verifier_ref,
            "result_packet_ref": self.result_packet_ref,
            "receipt_status": self.receipt_status,
            "authority_effect": self.authority_effect,
            "receipt_notes": self.receipt_notes,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_quarantine_id("resource_admission_receipt", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["admission_receipt_id"] = self.admission_receipt_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_resource_admission_receipt_record(
    *,
    resource_identity_ref: str,
    quarantine_decision_ref: str,
    accepted_scope_ref: str,
    verifier_ref: str,
    result_packet_ref: str,
    receipt_status: str,
    authority_effect: str,
    receipt_notes: Tuple[str, ...],
    version_tag: str = "v1",
) -> ResourceAdmissionReceiptRecord:
    body = {
        "resource_identity_ref": resource_identity_ref,
        "quarantine_decision_ref": quarantine_decision_ref,
        "accepted_scope_ref": accepted_scope_ref,
        "verifier_ref": verifier_ref,
        "result_packet_ref": result_packet_ref,
        "receipt_status": receipt_status,
        "authority_effect": authority_effect,
        "receipt_notes": receipt_notes,
        "version_tag": version_tag,
    }
    return ResourceAdmissionReceiptRecord(
        admission_receipt_id=stable_quarantine_id("resource_admission_receipt", body),
        **body,
    )


def validate_resource_admission_receipt_record(record: ResourceAdmissionReceiptRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "resource_identity_ref",
        "quarantine_decision_ref",
        "accepted_scope_ref",
        "verifier_ref",
        "result_packet_ref",
        "version_tag",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.receipt_status not in ALLOWED_RECEIPT_STATUS:
        issues.append(issue("receipt_status", "unsupported_receipt_status"))
    if record.authority_effect not in ALLOWED_AUTHORITY_EFFECT:
        issues.append(issue("authority_effect", "unsupported_authority_effect"))
    if not tuple_of_text(record.receipt_notes, allow_empty=False):
        issues.append(issue("receipt_notes", "required_non_empty_text_tuple"))
    if record.admission_receipt_id != record.expected_id():
        issues.append(issue("admission_receipt_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "resource_admission_receipt")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_resource_admission_receipt_record() -> ResourceAdmissionReceiptRecord:
    return build_resource_admission_receipt_record(
        resource_identity_ref="external_resource_identity:wordnet-demo-boundary",
        quarantine_decision_ref="resource_quarantine_decision:wordnet-demo-boundary",
        accepted_scope_ref="slice14_external_resource_quarantine_boundary_only",
        verifier_ref="scripts/aiweb_slice14_external_resource_quarantine_verify.py",
        result_packet_ref="future_slice14_result_packet_ref_required_before_acceptance",
        receipt_status="hold_receipt_represented_only",
        authority_effect="held",
        receipt_notes=("receipt records hold state only",),
    )
