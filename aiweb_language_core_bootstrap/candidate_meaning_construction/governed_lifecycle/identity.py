"""Deterministic Slice 39B identity generation.

Candidate semantic identity is derived only from the exact governed content and
exact provenance bodies.  Timestamps, random values, process identifiers,
filesystem state, environment state, and hash-table ordering are not read.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, TypeVar

from ..schema import (
    CandidateMeaningAlternativeReference,
    CandidateMeaningConstructionReceipt,
    CandidateMeaningContent,
    CandidateMeaningIdentity,
    CandidateMeaningProvenance,
    CandidateMeaningState,
)
from .canonical import (
    canonical_record_mapping,
    deterministic_digest,
    deterministic_record_digest,
    stable_identifier,
)
from .schema import (
    CandidateMeaningGovernanceBundle,
    CandidateMeaningLifecycleRecord,
    CandidateMeaningLifecycleTransitionRecord,
    CandidateMeaningVersionCustody,
)


T = TypeVar("T")


def _semantic_body(
    content: CandidateMeaningContent,
    provenance: CandidateMeaningProvenance,
) -> dict[str, Any]:
    return {
        "content": canonical_record_mapping(
            content,
            exclude_fields=("content_id",),
        ),
        "provenance": canonical_record_mapping(
            provenance,
            exclude_fields=("provenance_id",),
        ),
    }


def expected_candidate_meaning_id(
    content: CandidateMeaningContent,
    provenance: CandidateMeaningProvenance,
) -> str:
    return stable_identifier(
        "candidate_meaning",
        _semantic_body(content, provenance),
    )


def expected_candidate_key(candidate_meaning_id: str) -> str:
    digest = candidate_meaning_id.rsplit(":", 1)[-1]
    return f"candidate_key:sha256:{digest}"


def expected_candidate_lineage_id(
    provenance: CandidateMeaningProvenance,
) -> str:
    body = {
        "source_event_id": provenance.source_event_id,
        "input_event_id": provenance.input_event_id,
        "root_source_span_id": provenance.root_source_span_id,
        "slice37_registry_snapshot_id": (
            provenance.slice37_registry_snapshot_id
        ),
        "slice38_registry_snapshot_id": (
            provenance.slice38_registry_snapshot_id
        ),
        "compatibility_registry_snapshot_id": (
            provenance.compatibility_registry_snapshot_id
        ),
    }
    return stable_identifier("candidate_lineage", body)


def expected_content_id(record: CandidateMeaningContent) -> str:
    return stable_identifier(
        "candidate_content",
        canonical_record_mapping(record, exclude_fields=("content_id",)),
    )


def expected_provenance_id(record: CandidateMeaningProvenance) -> str:
    return stable_identifier(
        "candidate_provenance",
        canonical_record_mapping(record, exclude_fields=("provenance_id",)),
    )


def expected_alternative_reference_id(
    record: CandidateMeaningAlternativeReference,
) -> str:
    return stable_identifier(
        "candidate_alternative",
        canonical_record_mapping(
            record,
            exclude_fields=("alternative_reference_id",),
        ),
    )


def expected_construction_receipt_id(
    record: CandidateMeaningConstructionReceipt,
) -> str:
    return stable_identifier(
        "candidate_receipt",
        canonical_record_mapping(record, exclude_fields=("receipt_id",)),
    )


def expected_state_id(record: CandidateMeaningState) -> str:
    return stable_identifier(
        "candidate_state",
        canonical_record_mapping(record, exclude_fields=("state_id",)),
    )


def expected_version_custody_id(
    record: CandidateMeaningVersionCustody,
) -> str:
    return stable_identifier(
        "candidate_version_custody",
        canonical_record_mapping(record, exclude_fields=("custody_id",)),
    )


def expected_lifecycle_record_id(
    record: CandidateMeaningLifecycleRecord,
) -> str:
    return stable_identifier(
        "candidate_lifecycle",
        canonical_record_mapping(
            record,
            exclude_fields=("lifecycle_record_id",),
        ),
    )


def expected_lifecycle_transition_id(
    record: CandidateMeaningLifecycleTransitionRecord,
) -> str:
    return stable_identifier(
        "candidate_lifecycle_transition",
        canonical_record_mapping(record, exclude_fields=("transition_id",)),
    )


def expected_bundle_digest(
    record: CandidateMeaningGovernanceBundle,
) -> str:
    body = canonical_record_mapping(
        record,
        exclude_fields=("bundle_id", "canonical_digest"),
    )
    return deterministic_digest(body)


def expected_bundle_id(record: CandidateMeaningGovernanceBundle) -> str:
    body = canonical_record_mapping(
        record,
        exclude_fields=("bundle_id", "canonical_digest"),
    )
    return stable_identifier("candidate_governance_bundle", body)


def with_expected_content_id(
    record: CandidateMeaningContent,
) -> CandidateMeaningContent:
    return replace(record, content_id=expected_content_id(record))


def with_expected_provenance_id(
    record: CandidateMeaningProvenance,
) -> CandidateMeaningProvenance:
    return replace(record, provenance_id=expected_provenance_id(record))


def with_expected_candidate_identity(
    record: CandidateMeaningIdentity,
    *,
    content: CandidateMeaningContent,
    provenance: CandidateMeaningProvenance,
) -> CandidateMeaningIdentity:
    candidate_id = expected_candidate_meaning_id(content, provenance)
    return replace(
        record,
        candidate_meaning_id=candidate_id,
        candidate_key=expected_candidate_key(candidate_id),
        lineage_id=expected_candidate_lineage_id(provenance),
    )


def with_expected_alternative_reference_id(
    record: CandidateMeaningAlternativeReference,
) -> CandidateMeaningAlternativeReference:
    return replace(
        record,
        alternative_reference_id=expected_alternative_reference_id(record),
    )


def with_expected_construction_receipt_id(
    record: CandidateMeaningConstructionReceipt,
) -> CandidateMeaningConstructionReceipt:
    return replace(record, receipt_id=expected_construction_receipt_id(record))


def with_expected_state_id(
    record: CandidateMeaningState,
) -> CandidateMeaningState:
    return replace(record, state_id=expected_state_id(record))


def with_expected_version_custody_id(
    record: CandidateMeaningVersionCustody,
) -> CandidateMeaningVersionCustody:
    return replace(record, custody_id=expected_version_custody_id(record))


def with_expected_lifecycle_record_id(
    record: CandidateMeaningLifecycleRecord,
) -> CandidateMeaningLifecycleRecord:
    return replace(
        record,
        lifecycle_record_id=expected_lifecycle_record_id(record),
    )


def with_expected_lifecycle_transition_id(
    record: CandidateMeaningLifecycleTransitionRecord,
) -> CandidateMeaningLifecycleTransitionRecord:
    return replace(
        record,
        transition_id=expected_lifecycle_transition_id(record),
    )


def with_expected_bundle_identity(
    record: CandidateMeaningGovernanceBundle,
) -> CandidateMeaningGovernanceBundle:
    digest = expected_bundle_digest(record)
    provisional = replace(record, canonical_digest=digest)
    return replace(provisional, bundle_id=expected_bundle_id(provisional))


def with_expected_id(record: T) -> T:
    """Return a frozen-record copy with its supported deterministic ID."""

    if isinstance(record, CandidateMeaningContent):
        return with_expected_content_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningProvenance):
        return with_expected_provenance_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningAlternativeReference):
        return with_expected_alternative_reference_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningConstructionReceipt):
        return with_expected_construction_receipt_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningState):
        return with_expected_state_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningVersionCustody):
        return with_expected_version_custody_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningLifecycleRecord):
        return with_expected_lifecycle_record_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningLifecycleTransitionRecord):
        return with_expected_lifecycle_transition_id(record)  # type: ignore[return-value]
    if isinstance(record, CandidateMeaningGovernanceBundle):
        return with_expected_bundle_identity(record)  # type: ignore[return-value]
    raise TypeError(f"unsupported Slice 39B record type: {type(record).__name__}")


__all__ = (
    "expected_alternative_reference_id",
    "expected_bundle_digest",
    "expected_bundle_id",
    "expected_candidate_key",
    "expected_candidate_lineage_id",
    "expected_candidate_meaning_id",
    "expected_construction_receipt_id",
    "expected_content_id",
    "expected_lifecycle_record_id",
    "expected_lifecycle_transition_id",
    "expected_provenance_id",
    "expected_state_id",
    "expected_version_custody_id",
    "with_expected_bundle_identity",
    "with_expected_candidate_identity",
    "with_expected_content_id",
    "with_expected_id",
    "with_expected_lifecycle_record_id",
    "with_expected_lifecycle_transition_id",
    "with_expected_provenance_id",
    "with_expected_state_id",
    "with_expected_version_custody_id",
)
