"""Deterministic identity generation for Slice 39C custody records."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, TypeVar

from .canonical import (
    canonical_record_mapping_39c,
    deterministic_digest,
    stable_identifier,
)
from .schema import (
    CandidateMeaningConstructionProfileIdentity,
    CandidateMeaningPredecessorBindingResult,
    CandidateMeaningPredecessorCustody,
    OperatorCustodyReference,
    PredecessorCustodyReceipt,
    RegistryResourceCustodyReference,
    SourceSpanCustodyReference,
    StructuralRuleCustodyReference,
)


T = TypeVar("T")


def expected_profile_id(
    record: CandidateMeaningConstructionProfileIdentity,
) -> str:
    return stable_identifier(
        "candidate_construction_profile",
        canonical_record_mapping_39c(record, exclude_fields=("profile_id",)),
    )


def expected_source_span_reference_id(
    record: SourceSpanCustodyReference,
) -> str:
    return stable_identifier(
        "candidate_source_span_custody",
        canonical_record_mapping_39c(record, exclude_fields=("reference_id",)),
    )


def expected_structural_rule_reference_id(
    record: StructuralRuleCustodyReference,
) -> str:
    return stable_identifier(
        "candidate_structural_rule_custody",
        canonical_record_mapping_39c(record, exclude_fields=("reference_id",)),
    )


def expected_operator_reference_id(
    record: OperatorCustodyReference,
) -> str:
    return stable_identifier(
        "candidate_operator_custody",
        canonical_record_mapping_39c(record, exclude_fields=("reference_id",)),
    )


def expected_registry_resource_reference_id(
    record: RegistryResourceCustodyReference,
) -> str:
    return stable_identifier(
        "candidate_registry_resource_custody",
        canonical_record_mapping_39c(record, exclude_fields=("reference_id",)),
    )


def expected_receipt_id(record: PredecessorCustodyReceipt) -> str:
    return stable_identifier(
        "candidate_predecessor_receipt",
        canonical_record_mapping_39c(record, exclude_fields=("receipt_id",)),
    )


def expected_lineage_id(
    *,
    source_event_id: str,
    source_sha256: str,
    slice37_registry_snapshot_id: str,
    slice38_registry_snapshot_id: str,
    compatibility_registry_snapshot_id: str,
    construction_profile_id: str,
    construction_profile_version: str,
) -> str:
    return stable_identifier(
        "candidate_predecessor_lineage",
        {
            "source_event_id": source_event_id,
            "source_sha256": source_sha256,
            "slice37_registry_snapshot_id": slice37_registry_snapshot_id,
            "slice38_registry_snapshot_id": slice38_registry_snapshot_id,
            "compatibility_registry_snapshot_id": (
                compatibility_registry_snapshot_id
            ),
            "construction_profile_id": construction_profile_id,
            "construction_profile_version": construction_profile_version,
        },
    )


def expected_custody_digest(
    record: CandidateMeaningPredecessorCustody,
) -> str:
    return deterministic_digest(
        canonical_record_mapping_39c(
            record,
            exclude_fields=("custody_id", "canonical_digest"),
        )
    )


def expected_custody_id(
    record: CandidateMeaningPredecessorCustody,
) -> str:
    return stable_identifier(
        "candidate_predecessor_custody",
        canonical_record_mapping_39c(
            record,
            exclude_fields=("custody_id", "canonical_digest"),
        ),
    )


def expected_binding_result_id(
    record: CandidateMeaningPredecessorBindingResult,
) -> str:
    return stable_identifier(
        "candidate_predecessor_binding_result",
        canonical_record_mapping_39c(record, exclude_fields=("result_id",)),
    )


def with_expected_custody_identity(
    record: CandidateMeaningPredecessorCustody,
) -> CandidateMeaningPredecessorCustody:
    digest = expected_custody_digest(record)
    provisional = replace(record, canonical_digest=digest)
    return replace(provisional, custody_id=expected_custody_id(provisional))


def with_expected_id(record: T) -> T:
    if isinstance(record, CandidateMeaningConstructionProfileIdentity):
        return replace(
            record,
            profile_id=expected_profile_id(record),
        )  # type: ignore[return-value]
    if isinstance(record, SourceSpanCustodyReference):
        return replace(
            record,
            reference_id=expected_source_span_reference_id(record),
        )  # type: ignore[return-value]
    if isinstance(record, StructuralRuleCustodyReference):
        return replace(
            record,
            reference_id=expected_structural_rule_reference_id(record),
        )  # type: ignore[return-value]
    if isinstance(record, OperatorCustodyReference):
        return replace(
            record,
            reference_id=expected_operator_reference_id(record),
        )  # type: ignore[return-value]
    if isinstance(record, RegistryResourceCustodyReference):
        return replace(
            record,
            reference_id=expected_registry_resource_reference_id(record),
        )  # type: ignore[return-value]
    if isinstance(record, PredecessorCustodyReceipt):
        return replace(
            record,
            receipt_id=expected_receipt_id(record),
        )  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningPredecessorCustody):
        return with_expected_custody_identity(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningPredecessorBindingResult):
        return replace(
            record,
            result_id=expected_binding_result_id(record),
        )  # type: ignore[return-value]
    raise TypeError(f"unsupported Slice 39C record: {type(record).__name__}")


__all__ = (
    "expected_binding_result_id",
    "expected_custody_digest",
    "expected_custody_id",
    "expected_lineage_id",
    "expected_operator_reference_id",
    "expected_profile_id",
    "expected_receipt_id",
    "expected_registry_resource_reference_id",
    "expected_source_span_reference_id",
    "expected_structural_rule_reference_id",
    "with_expected_custody_identity",
    "with_expected_id",
)
