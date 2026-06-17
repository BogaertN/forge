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
    stable_traceability_id,
    tuple_of_text,
)

ALLOWED_REQUIREMENT_STATUS = (
    "approved_architecture_requirement",
    "approved_boundary_requirement",
    "pending_future_requirement",
    "hold_requirement",
)


@dataclass(frozen=True)
class RequirementIdentityRecord:
    requirement_identity_id: str
    requirement_key: str
    requirement_title: str
    requirement_status: str
    authority_document_refs: Tuple[str, ...]
    accepted_scope_ref: str
    slice_ref: str
    version_tag: str = "v1"
    live_runtime_behavior: bool = False
    capability_acceptance: bool = False
    verifier_gate_replacement: bool = False
    result_packet_bypass: bool = False
    accepted_scope_widening: bool = False
    release_authority: bool = False
    production_readiness: bool = False
    delivery_action: bool = False
    action_authorization: bool = False
    tool_invocation: bool = False
    capability_route: bool = False
    memory_write: bool = False
    evidence_validation: bool = False
    external_resource_admission: bool = False
    final_meaning_selection: bool = False
    selected_meaning: bool = False
    truth_decision: bool = False
    live_clarification: bool = False
    user_facing_question_emission: bool = False
    gp014_supersession: bool = False
    gp015_repair: bool = False
    gp015r1_installation: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "requirement_key": self.requirement_key,
            "requirement_title": self.requirement_title,
            "requirement_status": self.requirement_status,
            "authority_document_refs": self.authority_document_refs,
            "accepted_scope_ref": self.accepted_scope_ref,
            "slice_ref": self.slice_ref,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_traceability_id("requirement_identity", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["requirement_identity_id"] = self.requirement_identity_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_requirement_identity_record(
    *,
    requirement_key: str,
    requirement_title: str,
    requirement_status: str,
    authority_document_refs: Tuple[str, ...],
    accepted_scope_ref: str,
    slice_ref: str,
    version_tag: str = "v1",
) -> RequirementIdentityRecord:
    body = {
        "requirement_key": requirement_key,
        "requirement_title": requirement_title,
        "requirement_status": requirement_status,
        "authority_document_refs": authority_document_refs,
        "accepted_scope_ref": accepted_scope_ref,
        "slice_ref": slice_ref,
        "version_tag": version_tag,
    }
    return RequirementIdentityRecord(
        requirement_identity_id=stable_traceability_id("requirement_identity", body),
        **body,
    )


def validate_requirement_identity_record(record: RequirementIdentityRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record.requirement_key, str) or not record.requirement_key.strip():
        issues.append(issue("requirement_key", "required_non_empty_text"))
    if not isinstance(record.requirement_title, str) or not record.requirement_title.strip():
        issues.append(issue("requirement_title", "required_non_empty_text"))
    if record.requirement_status not in ALLOWED_REQUIREMENT_STATUS:
        issues.append(issue("requirement_status", "unsupported_requirement_status"))
    if not tuple_of_text(record.authority_document_refs, allow_empty=False):
        issues.append(issue("authority_document_refs", "required_non_empty_text_tuple"))
    if not isinstance(record.accepted_scope_ref, str) or not record.accepted_scope_ref.strip():
        issues.append(issue("accepted_scope_ref", "required_non_empty_text"))
    if not isinstance(record.slice_ref, str) or not record.slice_ref.strip():
        issues.append(issue("slice_ref", "required_non_empty_text"))
    if record.requirement_identity_id != record.expected_id():
        issues.append(issue("requirement_identity_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "requirement_identity")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_requirement_identity_record() -> RequirementIdentityRecord:
    return build_requirement_identity_record(
        requirement_key="REQ-S13-TRACEABILITY-001",
        requirement_title="Slice requirements map to approved tests and verifier gates",
        requirement_status="approved_boundary_requirement",
        authority_document_refs=("Document9:AppendixA", "BuildMap:Slice13"),
        accepted_scope_ref="accepted_scope:slice13-boundary-only",
        slice_ref="Slice13",
    )
