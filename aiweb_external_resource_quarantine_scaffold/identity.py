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
)

ALLOWED_RESOURCE_FAMILIES = (
    "wordnet",
    "sanskrit_wordnet",
    "verbnet",
    "framenet",
    "paninian_resource",
    "lexical_resource",
    "linguistic_dataset",
    "paper",
    "file",
    "corpus_candidate",
    "unknown_external_resource",
)

ALLOWED_RESOURCE_KINDS = (
    "lexical_database",
    "semantic_network",
    "predicate_frame_dataset",
    "grammar_resource",
    "paper",
    "dataset",
    "archive",
    "unknown",
)

ALLOWED_IDENTITY_STATUS = (
    "identity_represented_only",
    "identity_unknown_hold",
    "identity_incomplete_hold",
)


@dataclass(frozen=True)
class ExternalResourceIdentityRecord:
    resource_identity_id: str
    resource_key: str
    resource_name: str
    resource_family: str
    resource_kind: str
    identity_status: str
    origin_ref: str
    source_locator_ref: str
    declared_version: str
    resource_scope_note: str
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
            "resource_key": self.resource_key,
            "resource_name": self.resource_name,
            "resource_family": self.resource_family,
            "resource_kind": self.resource_kind,
            "identity_status": self.identity_status,
            "origin_ref": self.origin_ref,
            "source_locator_ref": self.source_locator_ref,
            "declared_version": self.declared_version,
            "resource_scope_note": self.resource_scope_note,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_quarantine_id("external_resource_identity", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["resource_identity_id"] = self.resource_identity_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_external_resource_identity_record(
    *,
    resource_key: str,
    resource_name: str,
    resource_family: str,
    resource_kind: str,
    identity_status: str,
    origin_ref: str,
    source_locator_ref: str,
    declared_version: str,
    resource_scope_note: str,
    version_tag: str = "v1",
) -> ExternalResourceIdentityRecord:
    body = {
        "resource_key": resource_key,
        "resource_name": resource_name,
        "resource_family": resource_family,
        "resource_kind": resource_kind,
        "identity_status": identity_status,
        "origin_ref": origin_ref,
        "source_locator_ref": source_locator_ref,
        "declared_version": declared_version,
        "resource_scope_note": resource_scope_note,
        "version_tag": version_tag,
    }
    return ExternalResourceIdentityRecord(
        resource_identity_id=stable_quarantine_id("external_resource_identity", body),
        **body,
    )


def validate_external_resource_identity_record(record: ExternalResourceIdentityRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field_name in (
        "resource_key",
        "resource_name",
        "origin_ref",
        "source_locator_ref",
        "declared_version",
        "resource_scope_note",
        "version_tag",
    ):
        if not nonempty_text(getattr(record, field_name)):
            issues.append(issue(field_name, "required_non_empty_text"))
    if record.resource_family not in ALLOWED_RESOURCE_FAMILIES:
        issues.append(issue("resource_family", "unsupported_resource_family"))
    if record.resource_kind not in ALLOWED_RESOURCE_KINDS:
        issues.append(issue("resource_kind", "unsupported_resource_kind"))
    if record.identity_status not in ALLOWED_IDENTITY_STATUS:
        issues.append(issue("identity_status", "unsupported_identity_status"))
    if record.resource_identity_id != record.expected_id():
        issues.append(issue("resource_identity_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "external_resource_identity")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_wordnet_identity_record() -> ExternalResourceIdentityRecord:
    return build_external_resource_identity_record(
        resource_key="open-english-wordnet-boundary-candidate",
        resource_name="Open English WordNet / Princeton WordNet ancestry candidate",
        resource_family="wordnet",
        resource_kind="lexical_database",
        identity_status="identity_represented_only",
        origin_ref="external_resource_dossier_wordnet_identity_boundary",
        source_locator_ref="not_fetched_local_boundary_ref_only",
        declared_version="unverified_boundary_version",
        resource_scope_note="identity record only; no concept graph replacement",
    )


def demo_sanskrit_wordnet_identity_record() -> ExternalResourceIdentityRecord:
    return build_external_resource_identity_record(
        resource_key="sanskrit-wordnet-boundary-hold",
        resource_name="Sanskrit WordNet candidate",
        resource_family="sanskrit_wordnet",
        resource_kind="semantic_network",
        identity_status="identity_represented_only",
        origin_ref="external_resource_dossier_sanskrit_wordnet_boundary",
        source_locator_ref="not_fetched_local_boundary_ref_only",
        declared_version="unverified_boundary_version",
        resource_scope_note="hold record only; no Sanskrit runtime support",
    )
