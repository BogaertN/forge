"""Deterministic Slice 40E identity functions."""
from __future__ import annotations

from dataclasses import replace

from .canonical import deterministic_digest, with_expected_id
from .schema import (
    ConnectednessAssertion,
    ConnectednessEvaluationInput,
    ConnectednessFinding,
    ConnectednessGateResult,
    ConnectednessGateRuntimeProfile,
    ConnectednessObservation,
)


def with_expected_profile_id(
    value: ConnectednessGateRuntimeProfile,
) -> ConnectednessGateRuntimeProfile:
    return with_expected_id(value, "profile_id", "connectedness_profile")


def with_expected_assertion_id(
    value: ConnectednessAssertion,
) -> ConnectednessAssertion:
    return with_expected_id(value, "assertion_id", "connectedness_assertion")


def with_expected_observation_id(
    value: ConnectednessObservation,
) -> ConnectednessObservation:
    return with_expected_id(value, "observation_id", "connectedness_observation")


def with_expected_evaluation_input_id(
    value: ConnectednessEvaluationInput,
) -> ConnectednessEvaluationInput:
    return with_expected_id(
        value,
        "evaluation_input_id",
        "connectedness_evaluation_input",
    )


def with_expected_finding_id(
    value: ConnectednessFinding,
) -> ConnectednessFinding:
    return with_expected_id(value, "finding_id", "connectedness_finding")


def expected_result_digest(value: ConnectednessGateResult) -> str:
    return deterministic_digest(
        replace(value, result_id="", canonical_digest="")
    )


def with_expected_result_identity(
    value: ConnectednessGateResult,
) -> ConnectednessGateResult:
    digest = expected_result_digest(value)
    return replace(
        value,
        result_id=f"connectedness_result:sha256:{digest}",
        canonical_digest=digest,
    )
