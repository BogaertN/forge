"""Deterministic identities for Slice 39G integration-owned records."""

from __future__ import annotations

from dataclasses import asdict, replace

from .canonical import deterministic_digest, stable_identifier
from .schema import (
    CandidateAlternativeRelationshipV1,
    CandidateConstructionTraceReferenceV1,
    CandidateLimitationReferenceV1,
    CandidateMeaningManifestCompanionV1,
    CandidateProvenanceReferenceV1,
    ManifestCandidateIntegrationProfile,
    ManifestCandidateIntegrationResult,
)


def _without_id(record: object, field_name: str) -> dict[str, object]:
    return {
        key: value
        for key, value in asdict(record).items()
        if key != field_name
    }


def expected_profile_id(record: ManifestCandidateIntegrationProfile) -> str:
    return stable_identifier(
        "manifest_candidate_integration_profile",
        _without_id(record, "profile_id"),
    )


def expected_trace_reference_id(
    record: CandidateConstructionTraceReferenceV1,
) -> str:
    return stable_identifier(
        "candidate_construction_trace_reference",
        _without_id(record, "trace_reference_id"),
    )


def expected_provenance_reference_id(
    record: CandidateProvenanceReferenceV1,
) -> str:
    return stable_identifier(
        "candidate_provenance_reference",
        _without_id(record, "provenance_reference_id"),
    )


def expected_limitation_reference_id(
    record: CandidateLimitationReferenceV1,
) -> str:
    return stable_identifier(
        "candidate_limitation_reference",
        _without_id(record, "limitation_reference_id"),
    )


def expected_alternative_relationship_id(
    record: CandidateAlternativeRelationshipV1,
) -> str:
    return stable_identifier(
        "candidate_alternative_relationship",
        _without_id(record, "relationship_id"),
    )


def expected_companion_id(
    record: CandidateMeaningManifestCompanionV1,
) -> str:
    return stable_identifier(
        "candidate_meaning_manifest_companion",
        _without_id(record, "companion_id"),
    )


def result_identity_body(
    record: ManifestCandidateIntegrationResult,
) -> dict[str, object]:
    manifest_id = record.manifest.manifest_id if record.manifest is not None else None
    return {
        "status": record.status.value,
        "reason_code": record.reason_code,
        "profile_id": record.profile.profile_id,
        "constructor_result_id": record.constructor_result_id,
        "manifest_id": manifest_id,
        "companion_ids": tuple(item.companion_id for item in record.companions),
        "construction_trace_reference_ids": tuple(
            item.trace_reference_id
            for item in record.construction_trace_references
        ),
        "provenance_reference_ids": tuple(
            item.provenance_reference_id for item in record.provenance_references
        ),
        "limitation_reference_ids": tuple(
            item.limitation_reference_id for item in record.limitation_references
        ),
        "alternative_relationship_ids": tuple(
            item.relationship_id for item in record.alternative_relationships
        ),
        "issue_tuples": tuple(
            (item.path, item.code.value, item.detail) for item in record.issues
        ),
        "source_event_ids": record.source_event_ids,
        "source_sha256s": record.source_sha256s,
        "input_candidate_count": record.input_candidate_count,
        "manifest_candidate_count": record.manifest_candidate_count,
        "boundary_flags": (
            record.explicitly_invoked,
            record.exact_constructor_result_verified,
            record.exact_msm_v1_verified,
            record.versioned_companion_used,
            record.lossless_companion_custody,
            record.candidate_side_only,
            record.manifest_integrated,
            record.existing_msm_schema_modified,
            record.automatic_migration_performed,
            record.non_selection_outcome_created,
            record.selected_governed_meaning_created,
            record.governed_result_reference_created,
            record.governed_outward_meaning_created,
            record.expression_link_created,
            record.validation_link_created,
            record.delivery_link_created,
            record.gate_outcome_created,
            record.selected_meaning_created,
            record.truth_determined,
            record.evidence_validated,
            record.permission_granted,
            record.route_created,
            record.action_performed,
            record.memory_accessed,
            record.rendered,
            record.delivered,
            record.filesystem_read_performed,
            record.filesystem_write_performed,
            record.network_access_performed,
            record.external_resource_loaded,
            record.language_model_used,
            record.embedding_used,
            record.vector_used,
            record.rag_used,
            record.semantic_similarity_used,
            record.bootstrap_integrated,
            record.slice39_closeout_created,
        ),
        "schema_version": record.schema_version,
    }


def expected_result_digest(record: ManifestCandidateIntegrationResult) -> str:
    return deterministic_digest(result_identity_body(record))


def expected_result_id(record: ManifestCandidateIntegrationResult) -> str:
    return stable_identifier(
        "manifest_candidate_integration_result",
        result_identity_body(record),
    )


def with_expected_trace_reference_id(
    record: CandidateConstructionTraceReferenceV1,
) -> CandidateConstructionTraceReferenceV1:
    return replace(record, trace_reference_id=expected_trace_reference_id(record))


def with_expected_provenance_reference_id(
    record: CandidateProvenanceReferenceV1,
) -> CandidateProvenanceReferenceV1:
    return replace(
        record,
        provenance_reference_id=expected_provenance_reference_id(record),
    )


def with_expected_limitation_reference_id(
    record: CandidateLimitationReferenceV1,
) -> CandidateLimitationReferenceV1:
    return replace(
        record,
        limitation_reference_id=expected_limitation_reference_id(record),
    )


def with_expected_alternative_relationship_id(
    record: CandidateAlternativeRelationshipV1,
) -> CandidateAlternativeRelationshipV1:
    return replace(
        record,
        relationship_id=expected_alternative_relationship_id(record),
    )


def with_expected_companion_id(
    record: CandidateMeaningManifestCompanionV1,
) -> CandidateMeaningManifestCompanionV1:
    return replace(record, companion_id=expected_companion_id(record))


def with_expected_result_identity(
    record: ManifestCandidateIntegrationResult,
) -> ManifestCandidateIntegrationResult:
    digest = expected_result_digest(record)
    provisional = replace(record, canonical_digest=digest)
    return replace(provisional, result_id=expected_result_id(provisional))


__all__ = (
    "expected_alternative_relationship_id",
    "expected_companion_id",
    "expected_limitation_reference_id",
    "expected_profile_id",
    "expected_provenance_reference_id",
    "expected_result_digest",
    "expected_result_id",
    "expected_trace_reference_id",
    "result_identity_body",
    "with_expected_alternative_relationship_id",
    "with_expected_companion_id",
    "with_expected_limitation_reference_id",
    "with_expected_provenance_reference_id",
    "with_expected_result_identity",
    "with_expected_trace_reference_id",
)
