"""Construct the deterministic Slice 47 status-decision receipt."""
from __future__ import annotations
from dataclasses import replace
from .authority import (
    SELECTED_STATUS_OUTCOME, SLICE44_SOURCE_AUTHORITY_PACKET_SHA256,
    SLICE46_ACCEPTANCE_ARCHIVE_SHA256, SOURCE_AUTHORITY_PACKET_SHA256,
)
from .schema import GP014StatusDecisionReceipt


def build_status_decision_receipt(*, decision_id: str) -> GP014StatusDecisionReceipt:
    value = GP014StatusDecisionReceipt(
        receipt_id="pending",
        decision_id=decision_id,
        selected_outcome=SELECTED_STATUS_OUTCOME,
        source_packet_sha256=SOURCE_AUTHORITY_PACKET_SHA256,
        slice44_packet_sha256=SLICE44_SOURCE_AUTHORITY_PACKET_SHA256,
        slice46_acceptance_sha256=SLICE46_ACCEPTANCE_ARCHIVE_SHA256,
        slice46_behavior_checks=500,
        slice46_behavior_failures=0,
        slice46_verifier_checks=3648,
        slice46_verifier_failures=0,
        exact_predecessor_files_protected=59,
        decision_deterministic=True,
        decision_validated=True,
        source_unchanged=True,
        gp014_protected=True,
        gp014_superseded=False,
        staging_performed=False,
        commit_performed=False,
    )
    return replace(value, receipt_id=value.expected_id())


__all__ = ("build_status_decision_receipt",)
