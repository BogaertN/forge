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

ALLOWED_DECISION_STATUS = (
    "quarantined_hold",
    "rejected_boundary",
    "admission_candidate_represented_only",
    "unreviewed_hold",
)

ALLOWED_QUARANTINE_STATUS = (
    "quarantine_required",
    "hold_required",
    "rejected_boundary",
    "candidate_only",
)


@dataclass(frozen=True)
class ResourceQuarantineDecisionRecord:
    quarantine_decision_id: str
    resource_identity_ref: str
    provenance_custody_ref: str
    license_custody_ref: str
    purpose_boundary_ref: str
    decision_status: str
    quarantine_status: str
    decision_reason_refs: Tuple[str, ...]
    hold_reason_refs: Tuple[str, ...]
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
            "provenance_custody_ref": self.provenance_custody_ref,
            "license_custody_ref": self.license_custody_ref,
            "purpose_boundary_ref": self.purpose_boundary_ref,
            "decision_status": self.decision_status,
            "quarantine_status": self.quarantine_status,
            "decision_reason_refs": self.decision_reason_refs,
            "hold_reason_refs": self.hold_reason_refs,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_quarantine_id("resource_quarantine_decision", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["quarantine_decision_id"] = self.quarantine_decision_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_resource_quarantine_decision_record(
    *,
    resource_identity_ref: str,
    provenance_custody_ref: str,
    license_custody_ref: str,
    purpose_boundary_ref: str,
    decision_status: str,
    quarantine_status: str,
    decision_reason_refs: Tuple[str, ...],
    hold_reason_refs: Tuple[str, ...],
    version_tag: str = "v1",
) -> ResourceQuarantineDecisionRecord:
    body = {
        "resource_identity_ref": resource_identity_ref,
        "provenance_custody_ref": provenance_custody_ref,
        "license_custody_ref": license_custody_ref,
        "purpose_boundary_ref": purpose_boundary_ref,
        "decision_status": decision_status,
        "quarantine_status": quarantine_status,
        "decision_reason_refs": decision_reason_refs,
        "hold_reason_refs": hold_reason_refs,
        "version_tag": version_tag,
    }
    return ResourceQuarantineDecisionRecord(
        quarantine_decision_id=stable_quarantine_id("resource_quarantine_decision", body),
        **body,
    )


def validate_resource_quarantine_decision_record(record: ResourceQuarantineDecisionRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "resource_identity_ref",
        "provenance_custody_ref",
        "license_custody_ref",
        "purpose_boundary_ref",
        "version_tag",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.decision_status not in ALLOWED_DECISION_STATUS:
        issues.append(issue("decision_status", "unsupported_decision_status"))
    if record.quarantine_status not in ALLOWED_QUARANTINE_STATUS:
        issues.append(issue("quarantine_status", "unsupported_quarantine_status"))
    if not tuple_of_text(record.decision_reason_refs, allow_empty=False):
        issues.append(issue("decision_reason_refs", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.hold_reason_refs, allow_empty=False):
        issues.append(issue("hold_reason_refs", "required_non_empty_text_tuple"))
    if record.quarantine_decision_id != record.expected_id():
        issues.append(issue("quarantine_decision_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "resource_quarantine_decision")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_resource_quarantine_decision_record() -> ResourceQuarantineDecisionRecord:
    return build_resource_quarantine_decision_record(
        resource_identity_ref="external_resource_identity:wordnet-demo-boundary",
        provenance_custody_ref="provenance_custody:wordnet-demo-boundary",
        license_custody_ref="license_custody:wordnet-demo-boundary",
        purpose_boundary_ref="resource_purpose_boundary:wordnet-demo-boundary",
        decision_status="quarantined_hold",
        quarantine_status="quarantine_required",
        decision_reason_refs=("external_resource_requires_review_before_use",),
        hold_reason_refs=("identity_and_license_notes_do_not_create_authority",),
    )
