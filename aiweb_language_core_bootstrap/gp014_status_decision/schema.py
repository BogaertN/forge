"""Immutable Slice 47 decision, receipt, and Phase D closeout records."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .authority import SLICE47_SCHEMA_VERSION
from .canonical import canonical_value, stable_identifier


@dataclass(frozen=True, slots=True)
class StatusEvidenceReference:
    reference_id: str
    evidence_kind: str
    identity: str
    sha256: str | None
    accepted: bool
    proves: tuple[str, ...]
    schema_version: str = SLICE47_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice47_evidence", self, excluded_fields=("reference_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class GP014StatusDecisionRecord:
    decision_id: str
    selected_outcome: str
    lawful_outcomes: tuple[str, ...]
    rejected_outcomes: tuple[str, ...]
    evidence_references: tuple[StatusEvidenceReference, ...]
    gp014_build_id: str
    gp014_status: str
    adapter_status: str
    equivalence_status: str
    phase_d_status: str
    source_unchanged: bool
    bounded_lane_preserved: bool
    protected: bool
    adapter_exists: bool
    adapter_is_general_interface: bool
    adapter_registered: bool
    equivalence_proof_accepted: bool
    refactor_accepted: bool
    replacement_accepted: bool
    supersession_accepted: bool
    future_change_requires: tuple[str, ...]
    supersession_requires: tuple[str, ...]
    gp014_modified: bool = False
    gp014_refactored: bool = False
    gp014_replaced: bool = False
    gp014_superseded: bool = False
    gp015_used: bool = False
    general_language_authority: bool = False
    concept_authority: bool = False
    predicate_authority: bool = False
    selected_meaning_authority: bool = False
    truth_authority: bool = False
    evidence_authority: bool = False
    permission_authority: bool = False
    route_authority: bool = False
    api_authority: bool = False
    ui_authority: bool = False
    network_authority: bool = False
    filesystem_write_authority: bool = False
    memory_authority: bool = False
    resource_authority: bool = False
    tool_authority: bool = False
    action_authority: bool = False
    delivery_authority: bool = False
    release_authority: bool = False
    production_authority: bool = False
    schema_version: str = SLICE47_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice47_gp014_status_decision", self, excluded_fields=("decision_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class GP014StatusDecisionReceipt:
    receipt_id: str
    decision_id: str
    selected_outcome: str
    source_packet_sha256: str
    slice44_packet_sha256: str
    slice46_acceptance_sha256: str
    slice46_behavior_checks: int
    slice46_behavior_failures: int
    slice46_verifier_checks: int
    slice46_verifier_failures: int
    exact_predecessor_files_protected: int
    decision_deterministic: bool
    decision_validated: bool
    source_unchanged: bool
    gp014_protected: bool
    gp014_superseded: bool
    staging_performed: bool
    commit_performed: bool
    schema_version: str = SLICE47_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice47_gp014_status_receipt", self, excluded_fields=("receipt_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class PhaseDCloseoutRecord:
    closeout_id: str
    decision_id: str
    completed_slices: tuple[str, ...]
    phase_d_complete: bool
    gp014_preserved: bool
    gp014_protected: bool
    gp014_superseded: bool
    next_lawful_slice: str
    progression_status: str
    runtime_activation_authorized: bool
    route_or_api_authorized: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = SLICE47_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice47_phase_d_closeout", self, excluded_fields=("closeout_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class Slice47DecisionBundle:
    bundle_id: str
    decision: GP014StatusDecisionRecord
    receipt: GP014StatusDecisionReceipt
    closeout: PhaseDCloseoutRecord
    schema_version: str = SLICE47_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice47_decision_bundle", self, excluded_fields=("bundle_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


__all__ = (
    "StatusEvidenceReference", "GP014StatusDecisionRecord",
    "GP014StatusDecisionReceipt", "PhaseDCloseoutRecord", "Slice47DecisionBundle",
)
