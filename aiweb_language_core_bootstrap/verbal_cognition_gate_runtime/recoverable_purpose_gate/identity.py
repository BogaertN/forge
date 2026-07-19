"""Deterministic Slice 40F identity functions."""
from __future__ import annotations

from dataclasses import replace

from .canonical import deterministic_digest, with_expected_id
from .schema import (
    RecoverablePurposeAssertion,
    RecoverablePurposeEvaluationInput,
    RecoverablePurposeFinding,
    RecoverablePurposeGateResult,
    RecoverablePurposeGateRuntimeProfile,
    RecoverablePurposeObservation,
)


def with_expected_profile_id(
    value: RecoverablePurposeGateRuntimeProfile,
) -> RecoverablePurposeGateRuntimeProfile:
    return with_expected_id(value, "profile_id", "recoverable_purpose_profile")


def with_expected_assertion_id(
    value: RecoverablePurposeAssertion,
) -> RecoverablePurposeAssertion:
    return with_expected_id(
        value,
        "assertion_id",
        "recoverable_purpose_assertion",
    )


def with_expected_observation_id(
    value: RecoverablePurposeObservation,
) -> RecoverablePurposeObservation:
    return with_expected_id(
        value,
        "observation_id",
        "recoverable_purpose_observation",
    )


def with_expected_evaluation_input_id(
    value: RecoverablePurposeEvaluationInput,
) -> RecoverablePurposeEvaluationInput:
    return with_expected_id(
        value,
        "evaluation_input_id",
        "recoverable_purpose_evaluation_input",
    )


def with_expected_finding_id(
    value: RecoverablePurposeFinding,
) -> RecoverablePurposeFinding:
    return with_expected_id(
        value,
        "finding_id",
        "recoverable_purpose_finding",
    )


def expected_result_digest(value: RecoverablePurposeGateResult) -> str:
    return deterministic_digest(
        replace(value, result_id="", canonical_digest="")
    )


def with_expected_result_identity(
    value: RecoverablePurposeGateResult,
) -> RecoverablePurposeGateResult:
    digest = expected_result_digest(value)
    return replace(
        value,
        result_id=f"recoverable_purpose_result:sha256:{digest}",
        canonical_digest=digest,
    )
