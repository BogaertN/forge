from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from .core import (
    BASE_HEAD,
    GP014_IDENTITY,
    GP014_PROTECTED_PATH_HASHES,
    GP014_RELATIONSHIP,
    GP014_STATUS,
    SCHEMA_VERSION,
    SOURCE_AUTHORITY_PACKET_SHA256,
    FALSE_ONLY_AUTHORITY_FIELDS,
    ValidationIssue,
    ValidationReport,
    check_false_only,
    issue,
    nonempty_text,
    sha256_file,
    stable_decision_id,
    tuple_of_path_hashes,
)


@dataclass(frozen=True)
class GP014ReferenceRecord:
    gp014_reference_id: str
    gp014_identity: str
    reference_relationship: str
    preservation_status: str
    base_head: str
    source_authority_packet_sha256: str
    protected_path_hashes: Tuple[Tuple[str, str], ...]
    reference_scope: str = "protected_reference_only_not_import_not_call_not_wrapper"
    version_tag: str = "v1"

    general_language_authority: bool = False
    concept_authority: bool = False
    predicate_authority: bool = False
    source_authority: bool = False
    selected_meaning_authority: bool = False
    full_rmc_authority: bool = False
    renderer_authority: bool = False
    output_approval: bool = False
    delivery_authority: bool = False
    execution_authority: bool = False
    runtime_authority: bool = False
    echo_authority: bool = False
    production_authority: bool = False
    route_authority: bool = False
    ui_authority: bool = False
    memory_authority: bool = False
    corpus_authority: bool = False
    external_truth_authority: bool = False
    model_authority: bool = False
    vector_authority: bool = False
    retrieval_authority: bool = False
    training_authority: bool = False
    gp014_modification: bool = False
    gp014_import: bool = False
    gp014_call: bool = False
    gp014_wrapper_created: bool = False
    gp014_supersession: bool = False
    gp014_promotion: bool = False
    gp015_repair: bool = False
    release_authority: bool = False

    def canonical_body(self) -> Dict[str, Any]:
        return {
            "gp014_identity": self.gp014_identity,
            "reference_relationship": self.reference_relationship,
            "preservation_status": self.preservation_status,
            "base_head": self.base_head,
            "source_authority_packet_sha256": self.source_authority_packet_sha256,
            "protected_path_hashes": self.protected_path_hashes,
            "reference_scope": self.reference_scope,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_decision_id("gp014-reference", self.canonical_body())


def build_gp014_reference_record(
    *,
    protected_path_hashes: Tuple[Tuple[str, str], ...] = GP014_PROTECTED_PATH_HASHES,
    base_head: str = BASE_HEAD,
    source_authority_packet_sha256: str = SOURCE_AUTHORITY_PACKET_SHA256,
) -> GP014ReferenceRecord:
    body = {
        "gp014_identity": GP014_IDENTITY,
        "reference_relationship": GP014_RELATIONSHIP,
        "preservation_status": GP014_STATUS,
        "base_head": base_head,
        "source_authority_packet_sha256": source_authority_packet_sha256,
        "protected_path_hashes": protected_path_hashes,
        "reference_scope": "protected_reference_only_not_import_not_call_not_wrapper",
        "version_tag": "v1",
    }
    return GP014ReferenceRecord(gp014_reference_id=stable_decision_id("gp014-reference", body), **body)


def validate_gp014_reference_record(record: GP014ReferenceRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.gp014_reference_id != record.expected_id():
        issues.append(issue("gp014_reference_id", "unstable_or_incorrect_id"))
    if record.gp014_identity != GP014_IDENTITY:
        issues.append(issue("gp014_identity", "unsupported_gp014_identity"))
    if record.reference_relationship != GP014_RELATIONSHIP:
        issues.append(issue("reference_relationship", "must_be_referenced_only"))
    if record.preservation_status != GP014_STATUS:
        issues.append(issue("preservation_status", "must_be_preserved_protected_unsuperseded"))
    if record.reference_scope != "protected_reference_only_not_import_not_call_not_wrapper":
        issues.append(issue("reference_scope", "must_be_reference_only_scope"))
    if not nonempty_text(record.base_head) or len(record.base_head) != 40:
        issues.append(issue("base_head", "expected_git_sha"))
    if record.source_authority_packet_sha256 != SOURCE_AUTHORITY_PACKET_SHA256:
        issues.append(issue("source_authority_packet_sha256", "source_authority_packet_mismatch"))
    if not tuple_of_path_hashes(record.protected_path_hashes):
        issues.append(issue("protected_path_hashes", "expected_nonempty_path_hash_pairs"))
    elif tuple(record.protected_path_hashes) != GP014_PROTECTED_PATH_HASHES:
        issues.append(issue("protected_path_hashes", "must_match_accepted_gp014_authority_paths"))
    check_false_only(record, FALSE_ONLY_AUTHORITY_FIELDS, issues)
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def verify_gp014_reference_hashes(repo: str | Path, record: GP014ReferenceRecord) -> Tuple[Tuple[str, str], ...]:
    """Return mismatches as (path, reason) without importing or executing GP-014."""

    root = Path(repo).resolve()
    mismatches: list[Tuple[str, str]] = []
    for rel_path, expected_hash in record.protected_path_hashes:
        target = root / rel_path
        if not target.is_file():
            mismatches.append((rel_path, "missing"))
            continue
        actual = sha256_file(target)
        if actual != expected_hash:
            mismatches.append((rel_path, f"sha256_mismatch:{actual}"))
    return tuple(mismatches)


def demo_gp014_reference_record() -> GP014ReferenceRecord:
    return build_gp014_reference_record()
