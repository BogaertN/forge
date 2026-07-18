"""Deterministic identity generation for Slice 39E candidate sets."""

from __future__ import annotations

from dataclasses import replace
from typing import TypeVar

from .canonical import canonical_record_mapping_39e, deterministic_digest, stable_identifier
from .schema import (
    CandidateExactDuplicateGroup,
    CandidateMaterialAlternativeReference,
    CandidateMeaningSet,
    CandidateSetMember,
    CandidateSetPreservationResult,
    CandidateSetProfileIdentity,
    CandidateSharedAncestryReference,
)

T = TypeVar("T")


def expected_profile_id(record: CandidateSetProfileIdentity) -> str:
    return stable_identifier("candidate_set_profile", canonical_record_mapping_39e(record, exclude_fields=("profile_id",)))


def expected_member_id(record: CandidateSetMember) -> str:
    return stable_identifier("candidate_set_member", canonical_record_mapping_39e(record, exclude_fields=("member_id",)))


def expected_duplicate_group_id(record: CandidateExactDuplicateGroup) -> str:
    return stable_identifier("candidate_exact_duplicate_group", canonical_record_mapping_39e(record, exclude_fields=("duplicate_group_id",)))


def expected_shared_ancestry_id(record: CandidateSharedAncestryReference) -> str:
    return stable_identifier("candidate_shared_ancestry", canonical_record_mapping_39e(record, exclude_fields=("shared_ancestry_id",)))


def expected_alternative_reference_id(record: CandidateMaterialAlternativeReference) -> str:
    return stable_identifier("candidate_material_alternative", canonical_record_mapping_39e(record, exclude_fields=("alternative_reference_id",)))


def expected_candidate_set_digest(record: CandidateMeaningSet) -> str:
    return deterministic_digest(canonical_record_mapping_39e(record, exclude_fields=("candidate_set_id", "canonical_digest")))


def expected_candidate_set_id(record: CandidateMeaningSet) -> str:
    return stable_identifier("candidate_meaning_set", canonical_record_mapping_39e(record, exclude_fields=("candidate_set_id", "canonical_digest")))


def expected_result_id(record: CandidateSetPreservationResult) -> str:
    return stable_identifier("candidate_set_preservation_result", canonical_record_mapping_39e(record, exclude_fields=("result_id",)))


def with_expected_set_identity(record: CandidateMeaningSet) -> CandidateMeaningSet:
    with_digest = replace(record, canonical_digest=expected_candidate_set_digest(record))
    return replace(with_digest, candidate_set_id=expected_candidate_set_id(with_digest))


def with_expected_id(record: T) -> T:
    if type(record) is CandidateSetProfileIdentity:
        return replace(record, profile_id=expected_profile_id(record))
    if type(record) is CandidateSetMember:
        return replace(record, member_id=expected_member_id(record))
    if type(record) is CandidateExactDuplicateGroup:
        return replace(record, duplicate_group_id=expected_duplicate_group_id(record))
    if type(record) is CandidateSharedAncestryReference:
        return replace(record, shared_ancestry_id=expected_shared_ancestry_id(record))
    if type(record) is CandidateMaterialAlternativeReference:
        return replace(record, alternative_reference_id=expected_alternative_reference_id(record))
    if type(record) is CandidateMeaningSet:
        return with_expected_set_identity(record)
    if type(record) is CandidateSetPreservationResult:
        return replace(record, result_id=expected_result_id(record))
    raise TypeError(f"unsupported Slice 39E identity type: {type(record).__name__}")


__all__ = (
    "expected_alternative_reference_id",
    "expected_candidate_set_digest",
    "expected_candidate_set_id",
    "expected_duplicate_group_id",
    "expected_member_id",
    "expected_profile_id",
    "expected_result_id",
    "expected_shared_ancestry_id",
    "with_expected_id",
    "with_expected_set_identity",
)
