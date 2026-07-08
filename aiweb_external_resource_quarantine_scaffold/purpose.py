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

ALLOWED_PURPOSE_STATUS = (
    "purpose_boundary_represented_only",
    "hold_boundary",
    "rejected_boundary",
)

ALLOWED_PERMITTED_PURPOSES = (
    "license_review_only",
    "architecture_reference_only",
    "future_candidate_mapping_only",
    "manual_inspection_only",
    "source_gap_analysis_only",
)

ALLOWED_BLOCKED_PURPOSES = (
    "runtime_authority",
    "concept_graph_replacement",
    "predicate_registry_replacement",
    "evidence_validation",
    "memory_write",
    "tool_routing",
    "model_training",
    "embedding_indexing",
    "rag_execution",
    "public_endorsement_claim",
)


@dataclass(frozen=True)
class ResourcePurposeBoundaryRecord:
    purpose_boundary_id: str
    resource_identity_ref: str
    purpose_status: str
    permitted_purpose_refs: Tuple[str, ...]
    blocked_purpose_refs: Tuple[str, ...]
    purpose_notes: Tuple[str, ...]
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
            "purpose_status": self.purpose_status,
            "permitted_purpose_refs": self.permitted_purpose_refs,
            "blocked_purpose_refs": self.blocked_purpose_refs,
            "purpose_notes": self.purpose_notes,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_quarantine_id("resource_purpose_boundary", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["purpose_boundary_id"] = self.purpose_boundary_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_resource_purpose_boundary_record(
    *,
    resource_identity_ref: str,
    purpose_status: str,
    permitted_purpose_refs: Tuple[str, ...],
    blocked_purpose_refs: Tuple[str, ...],
    purpose_notes: Tuple[str, ...],
    version_tag: str = "v1",
) -> ResourcePurposeBoundaryRecord:
    body = {
        "resource_identity_ref": resource_identity_ref,
        "purpose_status": purpose_status,
        "permitted_purpose_refs": permitted_purpose_refs,
        "blocked_purpose_refs": blocked_purpose_refs,
        "purpose_notes": purpose_notes,
        "version_tag": version_tag,
    }
    return ResourcePurposeBoundaryRecord(
        purpose_boundary_id=stable_quarantine_id("resource_purpose_boundary", body),
        **body,
    )


def validate_resource_purpose_boundary_record(record: ResourcePurposeBoundaryRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not nonempty_text(record.resource_identity_ref):
        issues.append(issue("resource_identity_ref", "required_non_empty_text"))
    if record.purpose_status not in ALLOWED_PURPOSE_STATUS:
        issues.append(issue("purpose_status", "unsupported_purpose_status"))
    if not tuple_of_text(record.permitted_purpose_refs, allow_empty=False):
        issues.append(issue("permitted_purpose_refs", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.blocked_purpose_refs, allow_empty=False):
        issues.append(issue("blocked_purpose_refs", "required_non_empty_text_tuple"))
    if tuple_of_text(record.permitted_purpose_refs):
        for purpose in record.permitted_purpose_refs:
            if purpose not in ALLOWED_PERMITTED_PURPOSES:
                issues.append(issue("permitted_purpose_refs", "unsupported_permitted_purpose"))
                break
    if tuple_of_text(record.blocked_purpose_refs):
        for purpose in record.blocked_purpose_refs:
            if purpose not in ALLOWED_BLOCKED_PURPOSES:
                issues.append(issue("blocked_purpose_refs", "unsupported_blocked_purpose"))
                break
    if not tuple_of_text(record.purpose_notes, allow_empty=False):
        issues.append(issue("purpose_notes", "required_non_empty_text_tuple"))
    if record.purpose_boundary_id != record.expected_id():
        issues.append(issue("purpose_boundary_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "resource_purpose_boundary")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_resource_purpose_boundary_record() -> ResourcePurposeBoundaryRecord:
    return build_resource_purpose_boundary_record(
        resource_identity_ref="external_resource_identity:wordnet-demo-boundary",
        purpose_status="purpose_boundary_represented_only",
        permitted_purpose_refs=("license_review_only", "architecture_reference_only"),
        blocked_purpose_refs=(
            "runtime_authority",
            "concept_graph_replacement",
            "predicate_registry_replacement",
            "evidence_validation",
            "memory_write",
            "tool_routing",
            "model_training",
            "embedding_indexing",
            "rag_execution",
            "public_endorsement_claim",
        ),
        purpose_notes=("useful reference remains separate from Forge authority",),
    )
