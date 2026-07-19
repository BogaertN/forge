"""Deterministic Slice 40G identity functions."""
from __future__ import annotations

from dataclasses import replace

from .canonical import deterministic_digest, with_expected_id
from .schema import (
    CandidateNonSelectionDisposition,
    GateCompositionDispositionAssertion,
    GateCompositionEvaluationInput,
    GateCompositionFinding,
    GateCompositionResult,
    GateCompositionRuntimeProfile,
)


def with_expected_profile_id(value: GateCompositionRuntimeProfile) -> GateCompositionRuntimeProfile:
    return with_expected_id(value, "profile_id", "gate_composition_profile")


def with_expected_assertion_id(
    value: GateCompositionDispositionAssertion,
) -> GateCompositionDispositionAssertion:
    return with_expected_id(value, "assertion_id", "gate_composition_assertion")


def with_expected_evaluation_input_id(
    value: GateCompositionEvaluationInput,
) -> GateCompositionEvaluationInput:
    return with_expected_id(
        value,
        "evaluation_input_id",
        "gate_composition_evaluation_input",
    )


def with_expected_finding_id(value: GateCompositionFinding) -> GateCompositionFinding:
    return with_expected_id(value, "finding_id", "gate_composition_finding")


def with_expected_disposition_id(
    value: CandidateNonSelectionDisposition,
) -> CandidateNonSelectionDisposition:
    return with_expected_id(
        value,
        "disposition_id",
        "candidate_non_selection_disposition",
    )


def expected_result_digest(value: GateCompositionResult) -> str:
    return deterministic_digest(replace(value, result_id="", canonical_digest=""))


def with_expected_result_identity(value: GateCompositionResult) -> GateCompositionResult:
    digest = expected_result_digest(value)
    return replace(
        value,
        result_id=f"gate_composition_result:sha256:{digest}",
        canonical_digest=digest,
    )
