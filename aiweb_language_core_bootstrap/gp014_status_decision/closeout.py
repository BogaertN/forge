"""Construct the bounded Phase D closeout record without runtime activation."""
from __future__ import annotations
from dataclasses import replace
from .authority import NEXT_LAWFUL_SLICE, PHASE_D_SLICES
from .schema import PhaseDCloseoutRecord, Slice47DecisionBundle
from .decision import build_gp014_status_decision
from .receipt import build_status_decision_receipt


def build_phase_d_closeout(*, decision_id: str) -> PhaseDCloseoutRecord:
    value = PhaseDCloseoutRecord(
        closeout_id="pending",
        decision_id=decision_id,
        completed_slices=PHASE_D_SLICES,
        phase_d_complete=True,
        gp014_preserved=True,
        gp014_protected=True,
        gp014_superseded=False,
        next_lawful_slice=NEXT_LAWFUL_SLICE,
        progression_status="phase_e_may_begin_after_slice47_acceptance",
        runtime_activation_authorized=False,
        route_or_api_authorized=False,
        production_ready=False,
        release_authorized=False,
    )
    return replace(value, closeout_id=value.expected_id())


def build_slice47_decision_bundle() -> Slice47DecisionBundle:
    decision = build_gp014_status_decision()
    receipt = build_status_decision_receipt(decision_id=decision.decision_id)
    closeout = build_phase_d_closeout(decision_id=decision.decision_id)
    value = Slice47DecisionBundle(
        bundle_id="pending",
        decision=decision,
        receipt=receipt,
        closeout=closeout,
    )
    return replace(value, bundle_id=value.expected_id())


__all__ = ("build_phase_d_closeout", "build_slice47_decision_bundle")
