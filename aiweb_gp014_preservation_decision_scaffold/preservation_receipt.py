from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .core import (
    BASE_HEAD,
    GP014_PROTECTED_PATH_HASHES,
    GP014_STATUS,
    GP015_PROTECTED_PATH_HASHES,
    GP015_STATUS,
    SCHEMA_VERSION,
    SLICE17_STATUS,
    SOURCE_AUTHORITY_PACKET_SHA256,
    FALSE_ONLY_AUTHORITY_FIELDS,
    ValidationIssue,
    ValidationReport,
    check_false_only,
    issue,
    nonempty_text,
    stable_decision_id,
    tuple_of_path_hashes,
)

RECEIPT_EFFECT = "preservation_receipt_only_not_authority_not_wrapper_not_execution"


@dataclass(frozen=True)
class GP014PreservationReceiptRecord:
    gp014_preservation_receipt_id: str
    gp014_reference_id: str
    gp014_wrapper_decision_id: str
    base_head: str
    source_authority_packet_sha256: str
    gp014_status: str
    gp014_relationship: str
    wrapper_decision: str
    protected_gp014_path_hashes: Tuple[Tuple[str, str], ...]
    gp015_status: str
    protected_gp015_path_hashes: Tuple[Tuple[str, str], ...]
    slice17_status: str
    protected_hashes_verified: bool
    gp014_files_untouched: bool
    gp015_not_repaired: bool
    slice17_not_gp014_wrapper: bool
    receipt_effect: str = RECEIPT_EFFECT
    receipt_status: str = "slice18_gp014_preservation_decision_receipt_recorded"
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
            "gp014_reference_id": self.gp014_reference_id,
            "gp014_wrapper_decision_id": self.gp014_wrapper_decision_id,
            "base_head": self.base_head,
            "source_authority_packet_sha256": self.source_authority_packet_sha256,
            "gp014_status": self.gp014_status,
            "gp014_relationship": self.gp014_relationship,
            "wrapper_decision": self.wrapper_decision,
            "protected_gp014_path_hashes": self.protected_gp014_path_hashes,
            "gp015_status": self.gp015_status,
            "protected_gp015_path_hashes": self.protected_gp015_path_hashes,
            "slice17_status": self.slice17_status,
            "protected_hashes_verified": self.protected_hashes_verified,
            "gp014_files_untouched": self.gp014_files_untouched,
            "gp015_not_repaired": self.gp015_not_repaired,
            "slice17_not_gp014_wrapper": self.slice17_not_gp014_wrapper,
            "receipt_effect": self.receipt_effect,
            "receipt_status": self.receipt_status,
            "version_tag": self.version_tag,
        }

    def expected_id(self) -> str:
        return stable_decision_id("gp014-preservation-receipt", self.canonical_body())


def build_gp014_preservation_receipt_record(
    *,
    gp014_reference_id: str,
    gp014_wrapper_decision_id: str,
    protected_hashes_verified: bool = True,
    gp014_files_untouched: bool = True,
    gp015_not_repaired: bool = True,
    slice17_not_gp014_wrapper: bool = True,
) -> GP014PreservationReceiptRecord:
    body = {
        "gp014_reference_id": gp014_reference_id,
        "gp014_wrapper_decision_id": gp014_wrapper_decision_id,
        "base_head": BASE_HEAD,
        "source_authority_packet_sha256": SOURCE_AUTHORITY_PACKET_SHA256,
        "gp014_status": GP014_STATUS,
        "gp014_relationship": "referenced_only",
        "wrapper_decision": "no_wrapper_at_slice18",
        "protected_gp014_path_hashes": GP014_PROTECTED_PATH_HASHES,
        "gp015_status": GP015_STATUS,
        "protected_gp015_path_hashes": GP015_PROTECTED_PATH_HASHES,
        "slice17_status": SLICE17_STATUS,
        "protected_hashes_verified": protected_hashes_verified,
        "gp014_files_untouched": gp014_files_untouched,
        "gp015_not_repaired": gp015_not_repaired,
        "slice17_not_gp014_wrapper": slice17_not_gp014_wrapper,
        "receipt_effect": RECEIPT_EFFECT,
        "receipt_status": "slice18_gp014_preservation_decision_receipt_recorded",
        "version_tag": "v1",
    }
    return GP014PreservationReceiptRecord(
        gp014_preservation_receipt_id=stable_decision_id("gp014-preservation-receipt", body),
        **body,
    )


def validate_gp014_preservation_receipt_record(record: GP014PreservationReceiptRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.gp014_preservation_receipt_id != record.expected_id():
        issues.append(issue("gp014_preservation_receipt_id", "unstable_or_incorrect_id"))
    for field in ("gp014_reference_id", "gp014_wrapper_decision_id"):
        if not nonempty_text(getattr(record, field)):
            issues.append(issue(field, "required"))
    if record.base_head != BASE_HEAD:
        issues.append(issue("base_head", "must_match_slice17_base_head"))
    if record.source_authority_packet_sha256 != SOURCE_AUTHORITY_PACKET_SHA256:
        issues.append(issue("source_authority_packet_sha256", "source_authority_packet_mismatch"))
    if record.gp014_status != GP014_STATUS:
        issues.append(issue("gp014_status", "must_remain_preserved_protected_unsuperseded"))
    if record.gp014_relationship != "referenced_only":
        issues.append(issue("gp014_relationship", "must_be_referenced_only"))
    if record.wrapper_decision != "no_wrapper_at_slice18":
        issues.append(issue("wrapper_decision", "must_be_no_wrapper_at_slice18"))
    if record.gp015_status != GP015_STATUS:
        issues.append(issue("gp015_status", "must_remain_failed_not_repaired"))
    if record.slice17_status != SLICE17_STATUS:
        issues.append(issue("slice17_status", "slice17_must_not_be_gp014_wrapper"))
    if not tuple_of_path_hashes(record.protected_gp014_path_hashes):
        issues.append(issue("protected_gp014_path_hashes", "required"))
    elif tuple(record.protected_gp014_path_hashes) != GP014_PROTECTED_PATH_HASHES:
        issues.append(issue("protected_gp014_path_hashes", "must_match_accepted_gp014_hashes"))
    if not tuple_of_path_hashes(record.protected_gp015_path_hashes):
        issues.append(issue("protected_gp015_path_hashes", "required"))
    elif tuple(record.protected_gp015_path_hashes) != GP015_PROTECTED_PATH_HASHES:
        issues.append(issue("protected_gp015_path_hashes", "must_match_accepted_gp015_hashes"))
    for field in (
        "protected_hashes_verified",
        "gp014_files_untouched",
        "gp015_not_repaired",
        "slice17_not_gp014_wrapper",
    ):
        if getattr(record, field) is not True:
            issues.append(issue(field, "must_be_true_for_preservation_receipt"))
    if record.receipt_effect != RECEIPT_EFFECT:
        issues.append(issue("receipt_effect", "must_be_receipt_only"))
    if record.receipt_status != "slice18_gp014_preservation_decision_receipt_recorded":
        issues.append(issue("receipt_status", "unsupported_receipt_status"))
    check_false_only(record, FALSE_ONLY_AUTHORITY_FIELDS, issues)
    return ValidationReport(schema_version=SCHEMA_VERSION, ok=not issues, issues=tuple(issues))


def demo_gp014_preservation_receipt_record() -> GP014PreservationReceiptRecord:
    return build_gp014_preservation_receipt_record(
        gp014_reference_id="gp014-reference:demo",
        gp014_wrapper_decision_id="gp014-wrapper-decision:demo",
    )
