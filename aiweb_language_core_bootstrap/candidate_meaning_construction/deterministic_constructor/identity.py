"""Deterministic identities for Slice 39F constructor-owned records."""

from __future__ import annotations

from dataclasses import asdict, replace

from .canonical import deterministic_digest, stable_identifier
from .schema import (
    CandidateMeaningConstructedRecord,
    CandidateMeaningConstructorProfile,
    CandidateMeaningConstructorResult,
)


def expected_profile_id(record: CandidateMeaningConstructorProfile) -> str:
    return stable_identifier(
        "candidate_meaning_constructor_profile",
        {key: value for key, value in asdict(record).items() if key != "profile_id"},
    )


def expected_constructed_record_id(record: CandidateMeaningConstructedRecord) -> str:
    return stable_identifier(
        "candidate_meaning_constructed_record",
        {
            "candidate_result_id": record.candidate_result_id,
            "predecessor_custody_id": record.predecessor_custody.custody_id,
            "semantic_content_assembly_id": record.semantic_content_assembly.assembly_id,
            "candidate_set_member_id": record.candidate_set_member.member_id,
            "candidate_meaning_state_id": record.candidate_meaning_state.state_id,
            "construction_receipt_id": record.construction_receipt.receipt_id,
            "deterministic_position": record.deterministic_position,
            "duplicate_occurrence_count": record.duplicate_occurrence_count,
            "exact_typed_predecessors_verified": record.exact_typed_predecessors_verified,
            "exact_ancestry_verified": record.exact_ancestry_verified,
            "exact_snapshots_verified": record.exact_snapshots_verified,
            "source_preserved": record.source_preserved,
            "schema_version": record.schema_version,
        },
    )


def result_identity_body(record: CandidateMeaningConstructorResult) -> dict[str, object]:
    return {
        "status": record.status.value,
        "reason_code": record.reason_code,
        "profile_id": record.profile.profile_id,
        "candidate_set_result_id": record.candidate_set_result.result_id,
        "constructed_record_ids": tuple(item.record_id for item in record.constructed_records),
        "construction_receipt_ids": tuple(item.receipt_id for item in record.construction_receipts),
        "issue_tuples": tuple((item.path, item.code.value, item.detail) for item in record.issues),
        "input_count": record.input_count,
        "unique_candidate_count": record.unique_candidate_count,
        "exact_duplicate_occurrence_count": record.exact_duplicate_occurrence_count,
        "source_event_ids": record.source_event_ids,
        "source_sha256s": record.source_sha256s,
        "boundary_flags": (
            record.explicitly_invoked,
            record.exact_input_types_verified,
            record.exact_ancestry_verified,
            record.exact_snapshots_verified,
            record.source_preserved,
            record.offline,
            record.standard_library_only,
            record.read_only,
            record.deterministic,
            record.in_memory_only,
            record.fail_closed,
            record.raw_text_inspected,
            record.similarity_used,
            record.nearest_known_fallback_used,
            record.hidden_repair_used,
            record.candidate_ranked,
            record.candidate_selected,
            record.ambiguity_resolved,
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
            record.manifest_integrated,
            record.bootstrap_integrated,
            record.slice39_closeout_created,
        ),
        "schema_version": record.schema_version,
    }


def expected_result_digest(record: CandidateMeaningConstructorResult) -> str:
    return deterministic_digest(result_identity_body(record))


def expected_result_id(record: CandidateMeaningConstructorResult) -> str:
    return stable_identifier("candidate_meaning_constructor_result", result_identity_body(record))


def with_expected_constructed_record_id(
    record: CandidateMeaningConstructedRecord,
) -> CandidateMeaningConstructedRecord:
    return replace(record, record_id=expected_constructed_record_id(record))


def with_expected_result_identity(
    record: CandidateMeaningConstructorResult,
) -> CandidateMeaningConstructorResult:
    digest = expected_result_digest(record)
    provisional = replace(record, canonical_digest=digest)
    return replace(provisional, result_id=expected_result_id(provisional))


__all__ = (
    "expected_constructed_record_id",
    "expected_profile_id",
    "expected_result_digest",
    "expected_result_id",
    "result_identity_body",
    "with_expected_constructed_record_id",
    "with_expected_result_identity",
)
