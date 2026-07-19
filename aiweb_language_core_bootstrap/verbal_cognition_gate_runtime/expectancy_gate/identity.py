"""Deterministic Slice 40C identity functions."""

from __future__ import annotations

from dataclasses import replace

from .canonical import deterministic_digest, with_expected_id
from .schema import (
    ExpectancyEvaluationInput,
    ExpectancyFinding,
    ExpectancyGateResult,
    ExpectancyGateRuntimeProfile,
    ExpectancyObservation,
    ExpectancyRequirement,
)


def with_expected_profile_id(
    value: ExpectancyGateRuntimeProfile,
) -> ExpectancyGateRuntimeProfile:
    return with_expected_id(value, "profile_id", "expectancy_profile")


def with_expected_requirement_id(
    value: ExpectancyRequirement,
) -> ExpectancyRequirement:
    return with_expected_id(value, "requirement_id", "expectancy_requirement")


def with_expected_observation_id(
    value: ExpectancyObservation,
) -> ExpectancyObservation:
    return with_expected_id(value, "observation_id", "expectancy_observation")


def with_expected_evaluation_input_id(
    value: ExpectancyEvaluationInput,
) -> ExpectancyEvaluationInput:
    return with_expected_id(
        value,
        "evaluation_input_id",
        "expectancy_evaluation_input",
    )


def with_expected_finding_id(value: ExpectancyFinding) -> ExpectancyFinding:
    return with_expected_id(value, "finding_id", "expectancy_finding")


def expected_result_digest(value: ExpectancyGateResult) -> str:
    payload = replace(
        value,
        result_id="",
        canonical_digest="",
    )
    return deterministic_digest(payload)


def with_expected_result_identity(
    value: ExpectancyGateResult,
) -> ExpectancyGateResult:
    digest = expected_result_digest(value)
    return replace(
        value,
        result_id=f"expectancy_result:sha256:{digest}",
        canonical_digest=digest,
    )


__all__ = (
    "expected_result_digest",
    "with_expected_evaluation_input_id",
    "with_expected_finding_id",
    "with_expected_observation_id",
    "with_expected_profile_id",
    "with_expected_requirement_id",
    "with_expected_result_identity",
)
