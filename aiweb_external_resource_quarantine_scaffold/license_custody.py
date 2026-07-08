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

ALLOWED_LICENSE_STATUS = (
    "license_custody_represented_only",
    "license_unknown_hold",
    "license_review_required_hold",
    "license_rejected_boundary",
)


@dataclass(frozen=True)
class LicenseCustodyRecord:
    license_custody_id: str
    resource_identity_ref: str
    license_status: str
    license_name_boundary: str
    license_text_ref: str
    attribution_requirements: Tuple[str, ...]
    license_limitations: Tuple[str, ...]
    no_endorsement_boundary: bool
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
            "license_status": self.license_status,
            "license_name_boundary": self.license_name_boundary,
            "license_text_ref": self.license_text_ref,
            "attribution_requirements": self.attribution_requirements,
            "license_limitations": self.license_limitations,
            "no_endorsement_boundary": self.no_endorsement_boundary,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_quarantine_id("license_custody", self.canonical_body())

    def canonical_dict(self) -> Dict[str, Any]:
        data = self.canonical_body()
        data["license_custody_id"] = self.license_custody_id
        data["schema_version"] = SCHEMA_VERSION
        return _canonicalize(data)


def build_license_custody_record(
    *,
    resource_identity_ref: str,
    license_status: str,
    license_name_boundary: str,
    license_text_ref: str,
    attribution_requirements: Tuple[str, ...],
    license_limitations: Tuple[str, ...],
    no_endorsement_boundary: bool,
    version_tag: str = "v1",
) -> LicenseCustodyRecord:
    body = {
        "resource_identity_ref": resource_identity_ref,
        "license_status": license_status,
        "license_name_boundary": license_name_boundary,
        "license_text_ref": license_text_ref,
        "attribution_requirements": attribution_requirements,
        "license_limitations": license_limitations,
        "no_endorsement_boundary": no_endorsement_boundary,
        "version_tag": version_tag,
    }
    return LicenseCustodyRecord(license_custody_id=stable_quarantine_id("license_custody", body), **body)


def validate_license_custody_record(record: LicenseCustodyRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not nonempty_text(record.resource_identity_ref):
        issues.append(issue("resource_identity_ref", "required_non_empty_text"))
    if record.license_status not in ALLOWED_LICENSE_STATUS:
        issues.append(issue("license_status", "unsupported_license_status"))
    if not nonempty_text(record.license_name_boundary):
        issues.append(issue("license_name_boundary", "required_non_empty_text"))
    if not nonempty_text(record.license_text_ref):
        issues.append(issue("license_text_ref", "required_non_empty_text"))
    if not tuple_of_text(record.attribution_requirements, allow_empty=False):
        issues.append(issue("attribution_requirements", "required_non_empty_text_tuple"))
    if not tuple_of_text(record.license_limitations, allow_empty=False):
        issues.append(issue("license_limitations", "required_non_empty_text_tuple"))
    if not isinstance(record.no_endorsement_boundary, bool):
        issues.append(issue("no_endorsement_boundary", "required_bool"))
    if record.license_custody_id != record.expected_id():
        issues.append(issue("license_custody_id", "stable_identifier_mismatch"))
    check_false_only(record, DOWNSTREAM_FALSE_ONLY_FIELDS, issues, "license_custody")
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_license_custody_record() -> LicenseCustodyRecord:
    return build_license_custody_record(
        resource_identity_ref="external_resource_identity:wordnet-demo-boundary",
        license_status="license_custody_represented_only",
        license_name_boundary="license_name_recorded_for_review_only",
        license_text_ref="external_resource_dossier_license_boundary_ref",
        attribution_requirements=("attribution requirement preserved as review note",),
        license_limitations=("license note does not create runtime permission",),
        no_endorsement_boundary=True,
    )
