"""Deterministic identity generation for Slice 39D candidate content."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, TypeVar

from .canonical import canonical_record_mapping_39d, deterministic_digest, stable_identifier
from .schema import (
    CandidateCommunicativePurpose,
    CandidateReferentReference,
    CandidateRequestedActDescription,
    CandidateSemanticContentAssembly,
    CandidateSemanticContentAssemblyResult,
    CandidateSemanticContentPayload,
    CandidateSemanticContentProfileIdentity,
    CandidateSemanticDistinction,
    CandidateSemanticRelationReference,
)

T = TypeVar("T")


def expected_profile_id(record: CandidateSemanticContentProfileIdentity) -> str:
    return stable_identifier(
        "candidate_semantic_content_profile",
        canonical_record_mapping_39d(record, exclude_fields=("profile_id",)),
    )


def expected_communicative_purpose_id(record: CandidateCommunicativePurpose) -> str:
    return stable_identifier(
        "candidate_communicative_purpose",
        canonical_record_mapping_39d(record, exclude_fields=("purpose_id",)),
    )


def expected_requested_act_id(record: CandidateRequestedActDescription) -> str:
    return stable_identifier(
        "candidate_requested_act_description",
        canonical_record_mapping_39d(record, exclude_fields=("requested_act_id",)),
    )


def expected_semantic_relation_reference_id(
    record: CandidateSemanticRelationReference,
) -> str:
    return stable_identifier(
        "candidate_semantic_relation_reference",
        canonical_record_mapping_39d(record, exclude_fields=("reference_id",)),
    )


def expected_referent_id(record: CandidateReferentReference) -> str:
    return stable_identifier(
        "candidate_referent_reference",
        canonical_record_mapping_39d(record, exclude_fields=("referent_id",)),
    )


def expected_distinction_id(record: CandidateSemanticDistinction) -> str:
    return stable_identifier(
        "candidate_semantic_distinction",
        canonical_record_mapping_39d(record, exclude_fields=("distinction_id",)),
    )


def expected_payload_id(record: CandidateSemanticContentPayload) -> str:
    return stable_identifier(
        "candidate_semantic_content_payload",
        canonical_record_mapping_39d(record, exclude_fields=("payload_id",)),
    )


def expected_assembly_digest(record: CandidateSemanticContentAssembly) -> str:
    return deterministic_digest(
        canonical_record_mapping_39d(
            record,
            exclude_fields=("assembly_id", "canonical_digest"),
        )
    )


def expected_assembly_id(record: CandidateSemanticContentAssembly) -> str:
    return stable_identifier(
        "candidate_semantic_content_assembly",
        canonical_record_mapping_39d(
            record,
            exclude_fields=("assembly_id", "canonical_digest"),
        ),
    )


def expected_result_id(record: CandidateSemanticContentAssemblyResult) -> str:
    return stable_identifier(
        "candidate_semantic_content_result",
        canonical_record_mapping_39d(record, exclude_fields=("result_id",)),
    )


def with_expected_assembly_identity(
    record: CandidateSemanticContentAssembly,
) -> CandidateSemanticContentAssembly:
    digest = expected_assembly_digest(record)
    with_digest = replace(record, canonical_digest=digest)
    return replace(with_digest, assembly_id=expected_assembly_id(with_digest))


def with_expected_id(record: T) -> T:
    if type(record) is CandidateSemanticContentProfileIdentity:
        return replace(record, profile_id=expected_profile_id(record))
    if type(record) is CandidateCommunicativePurpose:
        return replace(record, purpose_id=expected_communicative_purpose_id(record))
    if type(record) is CandidateRequestedActDescription:
        return replace(record, requested_act_id=expected_requested_act_id(record))
    if type(record) is CandidateSemanticRelationReference:
        return replace(
            record,
            reference_id=expected_semantic_relation_reference_id(record),
        )
    if type(record) is CandidateReferentReference:
        return replace(record, referent_id=expected_referent_id(record))
    if type(record) is CandidateSemanticDistinction:
        return replace(record, distinction_id=expected_distinction_id(record))
    if type(record) is CandidateSemanticContentPayload:
        return replace(record, payload_id=expected_payload_id(record))
    if type(record) is CandidateSemanticContentAssembly:
        return with_expected_assembly_identity(record)
    if type(record) is CandidateSemanticContentAssemblyResult:
        return replace(record, result_id=expected_result_id(record))
    raise TypeError(f"unsupported Slice 39D identity type: {type(record).__name__}")


__all__ = (
    "expected_assembly_digest",
    "expected_assembly_id",
    "expected_communicative_purpose_id",
    "expected_distinction_id",
    "expected_payload_id",
    "expected_profile_id",
    "expected_referent_id",
    "expected_requested_act_id",
    "expected_result_id",
    "expected_semantic_relation_reference_id",
    "with_expected_assembly_identity",
    "with_expected_id",
)
