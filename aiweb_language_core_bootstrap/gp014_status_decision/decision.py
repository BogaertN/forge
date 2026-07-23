"""Construct the single evidence-supported Slice 47 GP-014 status decision."""
from __future__ import annotations
from dataclasses import replace
from .authority import (
    ADAPTER_STATUS, EQUIVALENCE_STATUS, FUTURE_CHANGE_REQUIRES, GP014_BUILD_ID,
    GP014_STATUS, LAWFUL_STATUS_OUTCOMES, PHASE_D_STATUS, REJECTED_STATUS_OUTCOMES,
    SELECTED_STATUS_OUTCOME, SLICE18_COMMIT, SLICE44_SOURCE_AUTHORITY_PACKET_SHA256,
    SLICE45_COMMIT, SLICE46_ACCEPTANCE_ARCHIVE_SHA256, SLICE46_COMMIT,
    SOURCE_AUTHORITY_PACKET_SHA256, SUPERSESSION_REQUIRES,
)
from .canonical import stable_identifier
from .schema import GP014StatusDecisionRecord, StatusEvidenceReference


def _evidence(kind: str, identity: str, sha256: str | None, proves: tuple[str, ...]) -> StatusEvidenceReference:
    value = StatusEvidenceReference(
        reference_id="pending",
        evidence_kind=kind,
        identity=identity,
        sha256=sha256,
        accepted=True,
        proves=proves,
    )
    return replace(value, reference_id=value.expected_id())


def build_gp014_status_decision() -> GP014StatusDecisionRecord:
    evidence = (
        _evidence(
            "committed_preservation_decision",
            SLICE18_COMMIT,
            None,
            ("gp014_preserved", "gp014_protected", "gp014_not_superseded"),
        ),
        _evidence(
            "read_only_source_authority_packet",
            "slice44:" + SLICE44_SOURCE_AUTHORITY_PACKET_SHA256,
            SLICE44_SOURCE_AUTHORITY_PACKET_SHA256,
            ("exact_source_inspected", "regression_authority_collected", "repository_unchanged"),
        ),
        _evidence(
            "committed_bounded_adapter",
            SLICE45_COMMIT,
            None,
            ("separate_adapter_exists", "adapter_disabled_unregistered", "gp014_source_unchanged"),
        ),
        _evidence(
            "accepted_equivalence_and_regression_proof",
            SLICE46_COMMIT,
            SLICE46_ACCEPTANCE_ARCHIVE_SHA256,
            ("equivalence_accepted", "regression_protection_accepted", "gp014_not_modified"),
        ),
    )
    value = GP014StatusDecisionRecord(
        decision_id="pending",
        selected_outcome=SELECTED_STATUS_OUTCOME,
        lawful_outcomes=LAWFUL_STATUS_OUTCOMES,
        rejected_outcomes=REJECTED_STATUS_OUTCOMES,
        evidence_references=evidence,
        gp014_build_id=GP014_BUILD_ID,
        gp014_status=GP014_STATUS,
        adapter_status=ADAPTER_STATUS,
        equivalence_status=EQUIVALENCE_STATUS,
        phase_d_status=PHASE_D_STATUS,
        source_unchanged=True,
        bounded_lane_preserved=True,
        protected=True,
        adapter_exists=True,
        adapter_is_general_interface=False,
        adapter_registered=False,
        equivalence_proof_accepted=True,
        refactor_accepted=False,
        replacement_accepted=False,
        supersession_accepted=False,
        future_change_requires=FUTURE_CHANGE_REQUIRES,
        supersession_requires=SUPERSESSION_REQUIRES,
    )
    return replace(value, decision_id=value.expected_id())


__all__ = ("build_gp014_status_decision",)
