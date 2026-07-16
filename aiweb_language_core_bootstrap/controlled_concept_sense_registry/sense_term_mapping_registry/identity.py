"""Deterministic Slice 37D record identity helpers."""

from __future__ import annotations

from dataclasses import replace

from .schema import (
    ExactTermLookupRequest,
    ExactTermLookupResult,
    MappingExpansionRefusal,
    OutwardExpressionEligibilityReference,
    SenseTermMappingRegistryManifest,
)


def with_expected_eligibility_id(
    record: OutwardExpressionEligibilityReference,
) -> OutwardExpressionEligibilityReference:
    return replace(record, eligibility_id=record.expected_id())


def with_expected_expansion_refusal_id(
    record: MappingExpansionRefusal,
) -> MappingExpansionRefusal:
    return replace(record, refusal_id=record.expected_id())


def with_expected_lookup_request_id(
    record: ExactTermLookupRequest,
) -> ExactTermLookupRequest:
    return replace(record, request_id=record.expected_id())


def with_expected_lookup_result_id(
    record: ExactTermLookupResult,
) -> ExactTermLookupResult:
    return replace(record, result_id=record.expected_id())


def with_expected_manifest_id(
    record: SenseTermMappingRegistryManifest,
) -> SenseTermMappingRegistryManifest:
    return replace(record, manifest_id=record.expected_id())
