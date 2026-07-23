"""Strict deterministic validation for Slice 47 records."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .authority import (
    ADAPTER_STATUS, EQUIVALENCE_STATUS, FUTURE_CHANGE_REQUIRES, GP014_BUILD_ID,
    GP014_STATUS, LAWFUL_STATUS_OUTCOMES, NEXT_LAWFUL_SLICE, PHASE_D_SLICES,
    PHASE_D_STATUS, PROHIBITED_AUTHORITY_FIELDS, REJECTED_STATUS_OUTCOMES,
    SELECTED_STATUS_OUTCOME, SLICE44_SOURCE_AUTHORITY_PACKET_SHA256,
    SLICE46_ACCEPTANCE_ARCHIVE_SHA256, SOURCE_AUTHORITY_PACKET_SHA256,
    SUPERSESSION_REQUIRES,
)
from .schema import (
    GP014StatusDecisionRecord, GP014StatusDecisionReceipt, PhaseDCloseoutRecord,
    Slice47DecisionBundle, StatusEvidenceReference,
)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    field: str
    code: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    ok: bool
    issues: tuple[ValidationIssue, ...]


def _issue(field: str, code: str) -> ValidationIssue:
    return ValidationIssue(field=field, code=code)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _tuple_text(value: Any) -> bool:
    return isinstance(value, tuple) and bool(value) and all(_text(item) for item in value)


def _false_authority(record: Any, issues: list[ValidationIssue]) -> None:
    for field in PROHIBITED_AUTHORITY_FIELDS:
        if getattr(record, field, False) is not False:
            issues.append(_issue(field, "must_be_false"))


def validate_evidence_reference(record: Any) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record, StatusEvidenceReference):
        return ValidationReport(False, (_issue("record", "wrong_type"),))
    if record.reference_id != record.expected_id(): issues.append(_issue("reference_id", "identity_mismatch"))
    if not _text(record.evidence_kind): issues.append(_issue("evidence_kind", "required"))
    if not _text(record.identity): issues.append(_issue("identity", "required"))
    if record.sha256 is not None and (not isinstance(record.sha256, str) or len(record.sha256) != 64): issues.append(_issue("sha256", "must_be_sha256_or_none"))
    if record.accepted is not True: issues.append(_issue("accepted", "must_be_true"))
    if not _tuple_text(record.proves) or len(set(record.proves)) != len(record.proves): issues.append(_issue("proves", "must_be_unique_nonempty_text_tuple"))
    return ValidationReport(not issues, tuple(issues))


def validate_decision(record: Any) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record, GP014StatusDecisionRecord):
        return ValidationReport(False, (_issue("record", "wrong_type"),))
    if record.decision_id != record.expected_id(): issues.append(_issue("decision_id", "identity_mismatch"))
    expected = {
        "selected_outcome": SELECTED_STATUS_OUTCOME,
        "lawful_outcomes": LAWFUL_STATUS_OUTCOMES,
        "rejected_outcomes": REJECTED_STATUS_OUTCOMES,
        "gp014_build_id": GP014_BUILD_ID,
        "gp014_status": GP014_STATUS,
        "adapter_status": ADAPTER_STATUS,
        "equivalence_status": EQUIVALENCE_STATUS,
        "phase_d_status": PHASE_D_STATUS,
        "future_change_requires": FUTURE_CHANGE_REQUIRES,
        "supersession_requires": SUPERSESSION_REQUIRES,
    }
    for field, value in expected.items():
        if getattr(record, field) != value: issues.append(_issue(field, "exact_value_required"))
    if len(record.evidence_references) != 4: issues.append(_issue("evidence_references", "exactly_four_required"))
    identities = set()
    for item in record.evidence_references:
        report = validate_evidence_reference(item)
        if not report.ok: issues.extend(_issue(f"evidence_references.{issue.field}", issue.code) for issue in report.issues)
        identities.add(item.identity)
    if len(identities) != len(record.evidence_references): issues.append(_issue("evidence_references", "duplicate_identity"))
    required_true = (
        "source_unchanged", "bounded_lane_preserved", "protected", "adapter_exists",
        "equivalence_proof_accepted",
    )
    for field in required_true:
        if getattr(record, field) is not True: issues.append(_issue(field, "must_be_true"))
    required_false = (
        "adapter_is_general_interface", "adapter_registered", "refactor_accepted",
        "replacement_accepted", "supersession_accepted",
    )
    for field in required_false:
        if getattr(record, field) is not False: issues.append(_issue(field, "must_be_false"))
    _false_authority(record, issues)
    return ValidationReport(not issues, tuple(issues))


def validate_receipt(record: Any) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record, GP014StatusDecisionReceipt):
        return ValidationReport(False, (_issue("record", "wrong_type"),))
    if record.receipt_id != record.expected_id(): issues.append(_issue("receipt_id", "identity_mismatch"))
    if record.selected_outcome != SELECTED_STATUS_OUTCOME: issues.append(_issue("selected_outcome", "exact_value_required"))
    expected_hashes = {
        "source_packet_sha256": SOURCE_AUTHORITY_PACKET_SHA256,
        "slice44_packet_sha256": SLICE44_SOURCE_AUTHORITY_PACKET_SHA256,
        "slice46_acceptance_sha256": SLICE46_ACCEPTANCE_ARCHIVE_SHA256,
    }
    for field, value in expected_hashes.items():
        if getattr(record, field) != value: issues.append(_issue(field, "exact_value_required"))
    if (record.slice46_behavior_checks, record.slice46_behavior_failures) != (500, 0): issues.append(_issue("slice46_behavior", "accepted_500_of_500_required"))
    if (record.slice46_verifier_checks, record.slice46_verifier_failures) != (3648, 0): issues.append(_issue("slice46_verifier", "accepted_3648_of_3648_required"))
    if record.exact_predecessor_files_protected != 59: issues.append(_issue("exact_predecessor_files_protected", "must_equal_59"))
    for field in ("decision_deterministic", "decision_validated", "source_unchanged", "gp014_protected"):
        if getattr(record, field) is not True: issues.append(_issue(field, "must_be_true"))
    for field in ("gp014_superseded", "staging_performed", "commit_performed"):
        if getattr(record, field) is not False: issues.append(_issue(field, "must_be_false"))
    return ValidationReport(not issues, tuple(issues))


def validate_closeout(record: Any) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record, PhaseDCloseoutRecord):
        return ValidationReport(False, (_issue("record", "wrong_type"),))
    if record.closeout_id != record.expected_id(): issues.append(_issue("closeout_id", "identity_mismatch"))
    if record.completed_slices != PHASE_D_SLICES: issues.append(_issue("completed_slices", "exact_phase_d_sequence_required"))
    if record.next_lawful_slice != NEXT_LAWFUL_SLICE: issues.append(_issue("next_lawful_slice", "exact_value_required"))
    if record.progression_status != "phase_e_may_begin_after_slice47_acceptance": issues.append(_issue("progression_status", "exact_value_required"))
    for field in ("phase_d_complete", "gp014_preserved", "gp014_protected"):
        if getattr(record, field) is not True: issues.append(_issue(field, "must_be_true"))
    for field in ("gp014_superseded", "runtime_activation_authorized", "route_or_api_authorized", "production_ready", "release_authorized"):
        if getattr(record, field) is not False: issues.append(_issue(field, "must_be_false"))
    return ValidationReport(not issues, tuple(issues))


def validate_bundle(record: Any) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if not isinstance(record, Slice47DecisionBundle):
        return ValidationReport(False, (_issue("record", "wrong_type"),))
    if record.bundle_id != record.expected_id(): issues.append(_issue("bundle_id", "identity_mismatch"))
    for prefix, report in (
        ("decision", validate_decision(record.decision)),
        ("receipt", validate_receipt(record.receipt)),
        ("closeout", validate_closeout(record.closeout)),
    ):
        if not report.ok: issues.extend(_issue(f"{prefix}.{item.field}", item.code) for item in report.issues)
    if record.receipt.decision_id != record.decision.decision_id: issues.append(_issue("receipt.decision_id", "cross_record_mismatch"))
    if record.closeout.decision_id != record.decision.decision_id: issues.append(_issue("closeout.decision_id", "cross_record_mismatch"))
    return ValidationReport(not issues, tuple(issues))


__all__ = (
    "ValidationIssue", "ValidationReport", "validate_evidence_reference",
    "validate_decision", "validate_receipt", "validate_closeout", "validate_bundle",
)
