"""Deterministic Slice 40B identity functions.

All identifiers are derived only from explicit immutable record content. No
clock, randomness, process, filesystem, environment, hash-table iteration,
model, embedding, vector, similarity, or external-resource input participates.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TypeVar

from ..schema import (
    GateCandidateInputReference,
    GateLimitationReference,
    GateProvenanceReference,
    GateReasonGround,
    GateRequirementReference,
    GateTraceReference,
    VerbalCognitionGateIdentity,
    VerbalCognitionGateProfileIdentity,
    VerbalCognitionGateReviewRecord,
)
from .canonical import canonical_record_mapping, deterministic_record_digest, stable_identifier
from .schema import (
    GateGovernanceBundle,
    GateLifecycleRecord,
    GateLifecycleTransitionRecord,
    GateVersionCustody,
)


T = TypeVar("T")


def expected_gate_identity_id(record: VerbalCognitionGateIdentity) -> str:
    return stable_identifier(
        "verbal_cognition_gate",
        canonical_record_mapping(record, exclude_fields=("gate_id",)),
    )


def expected_gate_profile_id(
    record: VerbalCognitionGateProfileIdentity,
) -> str:
    return stable_identifier(
        "verbal_cognition_gate_profile",
        canonical_record_mapping(record, exclude_fields=("profile_id",)),
    )


def expected_candidate_input_reference_id(
    record: GateCandidateInputReference,
) -> str:
    return stable_identifier(
        "gate_candidate_input",
        canonical_record_mapping(
            record,
            exclude_fields=("candidate_input_ref_id",),
        ),
    )


def expected_requirement_reference_id(
    record: GateRequirementReference,
) -> str:
    return stable_identifier(
        "gate_requirement_reference",
        canonical_record_mapping(
            record,
            exclude_fields=("requirement_reference_id",),
        ),
    )


def expected_reason_ground_id(record: GateReasonGround) -> str:
    return stable_identifier(
        "gate_reason_ground",
        canonical_record_mapping(record, exclude_fields=("reason_ground_id",)),
    )


def expected_trace_reference_id(record: GateTraceReference) -> str:
    return stable_identifier(
        "gate_trace_reference",
        canonical_record_mapping(
            record,
            exclude_fields=("trace_reference_id",),
        ),
    )


def expected_provenance_reference_id(
    record: GateProvenanceReference,
) -> str:
    return stable_identifier(
        "gate_provenance_reference",
        canonical_record_mapping(
            record,
            exclude_fields=("provenance_reference_id",),
        ),
    )


def expected_limitation_reference_id(
    record: GateLimitationReference,
) -> str:
    return stable_identifier(
        "gate_limitation_reference",
        canonical_record_mapping(
            record,
            exclude_fields=("limitation_reference_id",),
        ),
    )


def expected_review_record_id(
    record: VerbalCognitionGateReviewRecord,
) -> str:
    return stable_identifier(
        "verbal_cognition_gate_review",
        canonical_record_mapping(record, exclude_fields=("review_record_id",)),
    )


def expected_version_custody_id(record: GateVersionCustody) -> str:
    return stable_identifier(
        "gate_version_custody",
        canonical_record_mapping(record, exclude_fields=("custody_id",)),
    )


def expected_lifecycle_record_id(record: GateLifecycleRecord) -> str:
    return stable_identifier(
        "gate_lifecycle_record",
        canonical_record_mapping(
            record,
            exclude_fields=("lifecycle_record_id",),
        ),
    )


def expected_lifecycle_transition_id(
    record: GateLifecycleTransitionRecord,
) -> str:
    return stable_identifier(
        "gate_lifecycle_transition",
        canonical_record_mapping(record, exclude_fields=("transition_id",)),
    )


def expected_bundle_digest(record: GateGovernanceBundle) -> str:
    return deterministic_record_digest(
        record,
        exclude_fields=("bundle_id", "canonical_digest"),
    )


def expected_bundle_id(record: GateGovernanceBundle) -> str:
    return stable_identifier(
        "gate_governance_bundle",
        canonical_record_mapping(record, exclude_fields=("bundle_id",)),
    )


def with_expected_gate_identity(
    record: VerbalCognitionGateIdentity,
) -> VerbalCognitionGateIdentity:
    return replace(record, gate_id=expected_gate_identity_id(record))


def with_expected_gate_profile_identity(
    record: VerbalCognitionGateProfileIdentity,
) -> VerbalCognitionGateProfileIdentity:
    return replace(record, profile_id=expected_gate_profile_id(record))


def with_expected_candidate_input_reference(
    record: GateCandidateInputReference,
) -> GateCandidateInputReference:
    return replace(
        record,
        candidate_input_ref_id=expected_candidate_input_reference_id(record),
    )


def with_expected_requirement_reference(
    record: GateRequirementReference,
) -> GateRequirementReference:
    return replace(
        record,
        requirement_reference_id=expected_requirement_reference_id(record),
    )


def with_expected_reason_ground(record: GateReasonGround) -> GateReasonGround:
    return replace(record, reason_ground_id=expected_reason_ground_id(record))


def with_expected_trace_reference(
    record: GateTraceReference,
) -> GateTraceReference:
    return replace(
        record,
        trace_reference_id=expected_trace_reference_id(record),
    )


def with_expected_provenance_reference(
    record: GateProvenanceReference,
) -> GateProvenanceReference:
    return replace(
        record,
        provenance_reference_id=expected_provenance_reference_id(record),
    )


def with_expected_limitation_reference(
    record: GateLimitationReference,
) -> GateLimitationReference:
    return replace(
        record,
        limitation_reference_id=expected_limitation_reference_id(record),
    )


def with_expected_review_record(
    record: VerbalCognitionGateReviewRecord,
) -> VerbalCognitionGateReviewRecord:
    return replace(record, review_record_id=expected_review_record_id(record))


def with_expected_version_custody(
    record: GateVersionCustody,
) -> GateVersionCustody:
    return replace(record, custody_id=expected_version_custody_id(record))


def with_expected_lifecycle_record(
    record: GateLifecycleRecord,
) -> GateLifecycleRecord:
    return replace(
        record,
        lifecycle_record_id=expected_lifecycle_record_id(record),
    )


def with_expected_lifecycle_transition(
    record: GateLifecycleTransitionRecord,
) -> GateLifecycleTransitionRecord:
    return replace(
        record,
        transition_id=expected_lifecycle_transition_id(record),
    )


def with_expected_bundle_identity(
    record: GateGovernanceBundle,
) -> GateGovernanceBundle:
    digest = expected_bundle_digest(record)
    provisional = replace(record, canonical_digest=digest)
    return replace(provisional, bundle_id=expected_bundle_id(provisional))


def with_expected_id(record: T) -> T:
    """Return a frozen-record copy with its supported deterministic ID."""

    if isinstance(record, VerbalCognitionGateIdentity):
        return with_expected_gate_identity(record)  # type: ignore[return-value]
    if isinstance(record, VerbalCognitionGateProfileIdentity):
        return with_expected_gate_profile_identity(record)  # type: ignore[return-value]
    if isinstance(record, GateCandidateInputReference):
        return with_expected_candidate_input_reference(record)  # type: ignore[return-value]
    if isinstance(record, GateRequirementReference):
        return with_expected_requirement_reference(record)  # type: ignore[return-value]
    if isinstance(record, GateReasonGround):
        return with_expected_reason_ground(record)  # type: ignore[return-value]
    if isinstance(record, GateTraceReference):
        return with_expected_trace_reference(record)  # type: ignore[return-value]
    if isinstance(record, GateProvenanceReference):
        return with_expected_provenance_reference(record)  # type: ignore[return-value]
    if isinstance(record, GateLimitationReference):
        return with_expected_limitation_reference(record)  # type: ignore[return-value]
    if isinstance(record, VerbalCognitionGateReviewRecord):
        return with_expected_review_record(record)  # type: ignore[return-value]
    if isinstance(record, GateVersionCustody):
        return with_expected_version_custody(record)  # type: ignore[return-value]
    if isinstance(record, GateLifecycleRecord):
        return with_expected_lifecycle_record(record)  # type: ignore[return-value]
    if isinstance(record, GateLifecycleTransitionRecord):
        return with_expected_lifecycle_transition(record)  # type: ignore[return-value]
    if isinstance(record, GateGovernanceBundle):
        return with_expected_bundle_identity(record)  # type: ignore[return-value]
    raise TypeError(f"unsupported Slice 40B record type: {type(record).__name__}")


__all__ = (
    "expected_bundle_digest",
    "expected_bundle_id",
    "expected_candidate_input_reference_id",
    "expected_gate_identity_id",
    "expected_gate_profile_id",
    "expected_lifecycle_record_id",
    "expected_lifecycle_transition_id",
    "expected_limitation_reference_id",
    "expected_provenance_reference_id",
    "expected_reason_ground_id",
    "expected_requirement_reference_id",
    "expected_review_record_id",
    "expected_trace_reference_id",
    "expected_version_custody_id",
    "with_expected_bundle_identity",
    "with_expected_candidate_input_reference",
    "with_expected_gate_identity",
    "with_expected_gate_profile_identity",
    "with_expected_id",
    "with_expected_lifecycle_record",
    "with_expected_lifecycle_transition",
    "with_expected_limitation_reference",
    "with_expected_provenance_reference",
    "with_expected_reason_ground",
    "with_expected_requirement_reference",
    "with_expected_review_record",
    "with_expected_trace_reference",
    "with_expected_version_custody",
)
