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

ALLOWED_PROVENANCE_STATUS = (
    "provenance_custody_represented_only",
    "provenance_unknown_hold",
    "provenance_incomplete_hold",
)

ALLOWED_ACQUISITION_BOUNDARIES = (
    "user_supplied_reference_only",
    "local_packet_reference_only",
    "future_download_candidate_only",
    "unknown_not_acquired",
)


@dataclass(frozen=True)
class ProvenanceCustodyRecord:
    provenance_custody_id: str
    resource_identity_ref: str
    provenance_status: str
    acquisition_boundary: str
    source_origin_refs: Tuple[str, ...]
    custody_chain_refs: Tuple[str, ...]
    provenance_notes: Tuple[str, ...]
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
            "provenance_status": self.provenance_status,
            "acquisition_boundary": self.acquisition_boundary,
            "source_origin_refs": self.source_origin_refs,
            "custody_chain_refs": self.custody_chain_refs,
            "provenance_notes": self.provenance_notes,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_quarantine_id("provenance_custody", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["provenance_custody_id"] = self.provenance_custody_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_provenance_custody_record(
    *,
    resource_identity_ref: str,
    provenance_status: str,
    acquisition_boundary: str,
    source_origin_refs: Tuple[str, ...],
    custody_chain_refs: Tuple[str, ...],
    provenance_notes: Tuple[str, ...],
    version_tag: str = "v1",
) -> ProvenanceCustodyRecord:
    body = {
        "resource_identity_ref": resource_identity_ref,
        "provenance_status": provenance_status,
        "acquisition_boundary": acquisition_boundary,
        "source_origin_refs": source_origin_refs,
        "custody_chain_refs": custody_chain_refs,
        "provenance_notes": provenance_notes,
        "version_tag": version_tag,
    }
    return ProvenanceCustodyRecord(provenance_custody_id=stable_quarantine_id("provenance_custody", body), **body)


def validate_provenance_custody_record(record: ProvenanceCustodyRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not nonempty_text(record.resource_identity_ref):
        issues.append(issue("resource_identity_ref", "required_non_empty_text"))
    if record.provenance_status not in ALLOWED_PROVENANCE_STATUS:
        issues.append(issue("provenance_status", "unsupported_provenance_status"))
    if record.acquisition_boundary not in ALLOWED_ACQUISITION_BOUNDARIES:
        issues.append(issue("acquisition_boundary", "unsupported_acquisition_boundary"))
    if not tuple_of_text(record.source_origin_refs, allow_empty=False):
        issues.append(issue("source_origin_refs", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.custody_chain_refs, allow_empty=False):
        issues.append(issue("custody_chain_refs", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.provenance_notes, allow_empty=False):
        issues.append(issue("provenance_notes", "required_non_empty_text_tuple"))
    if record.provenance_custody_id != record.expected_id():
        issues.append(issue("provenance_custody_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "provenance_custody")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_provenance_custody_record() -> ProvenanceCustodyRecord:
    return build_provenance_custody_record(
        resource_identity_ref="external_resource_identity:wordnet-demo-boundary",
        provenance_status="provenance_custody_represented_only",
        acquisition_boundary="local_packet_reference_only",
        source_origin_refs=("external_resource_dossier_wordnet_origin_boundary",),
        custody_chain_refs=("slice14_quarantine_chain_boundary",),
        provenance_notes=("provenance is represented for later review only",),
    )
