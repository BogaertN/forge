"""Deterministic identities for Slice 41D records."""
from __future__ import annotations

from dataclasses import replace

from ...meaning_structure_manifest import SelectedGovernedMeaningRecord
from .canonical import canonical_json_bytes, deterministic_digest, stable_identifier
from .schema import (
    PreservedAlternativeCandidateRecord,
    SelectedMeaningConstructionInput,
    SelectedMeaningConstructionPackage,
    SelectedMeaningContentProof,
    SelectedMeaningDecisionRecord,
    SelectedMeaningSelectionReceiptRecord,
    SelectedMeaningSelectionTraceRecord,
)


def expected_construction_input_id(record: SelectedMeaningConstructionInput) -> str:
    return stable_identifier(
        "selected_meaning_construction_input",
        record,
        exclude_fields=("construction_input_id",),
    )


def with_expected_construction_input_id(
    record: SelectedMeaningConstructionInput,
) -> SelectedMeaningConstructionInput:
    return replace(record, construction_input_id=expected_construction_input_id(record))


def expected_decision_id(record: SelectedMeaningDecisionRecord) -> str:
    return stable_identifier(
        "selected_meaning_decision",
        record,
        exclude_fields=("decision_id",),
    )


def with_expected_decision_id(
    record: SelectedMeaningDecisionRecord,
) -> SelectedMeaningDecisionRecord:
    return replace(record, decision_id=expected_decision_id(record))


def expected_preservation_id(record: PreservedAlternativeCandidateRecord) -> str:
    return stable_identifier(
        "preserved_alternative_candidate",
        record,
        exclude_fields=("preservation_id",),
    )


def with_expected_preservation_id(
    record: PreservedAlternativeCandidateRecord,
) -> PreservedAlternativeCandidateRecord:
    return replace(record, preservation_id=expected_preservation_id(record))


def expected_content_proof_id(record: SelectedMeaningContentProof) -> str:
    return stable_identifier(
        "selected_meaning_content_proof",
        record,
        exclude_fields=("proof_id",),
    )


def with_expected_content_proof_id(
    record: SelectedMeaningContentProof,
) -> SelectedMeaningContentProof:
    return replace(record, proof_id=expected_content_proof_id(record))


def expected_trace_id(record: SelectedMeaningSelectionTraceRecord) -> str:
    return stable_identifier(
        "selected_meaning_selection_trace",
        record,
        exclude_fields=("trace_id",),
    )


def with_expected_trace_id(
    record: SelectedMeaningSelectionTraceRecord,
) -> SelectedMeaningSelectionTraceRecord:
    return replace(record, trace_id=expected_trace_id(record))


def expected_receipt_id(record: SelectedMeaningSelectionReceiptRecord) -> str:
    return stable_identifier(
        "selected_meaning_selection_receipt",
        record,
        exclude_fields=("receipt_id",),
    )


def with_expected_receipt_id(
    record: SelectedMeaningSelectionReceiptRecord,
) -> SelectedMeaningSelectionReceiptRecord:
    return replace(record, receipt_id=expected_receipt_id(record))


def selected_meaning_identity_body(record: SelectedGovernedMeaningRecord) -> dict[str, object]:
    return {
        "lineage_id": record.lineage_id,
        "selected_candidate_ref": record.selected_candidate_ref,
        "selection_authority_ref": record.selection_authority_ref,
        "communicative_act": record.communicative_act,
        "concept_refs": record.concept_refs,
        "relation_refs": record.relation_refs,
        "meaning_modifiers": record.meaning_modifiers,
        "inherited_limitations": record.inherited_limitations,
        "authority_sensitive_distinctions": record.authority_sensitive_distinctions,
        "preservation_classes": record.preservation_classes,
        "record_kind": record.record_kind,
        "lifecycle_state": record.lifecycle_state,
        "schema_version": record.schema_version,
    }


def expected_selected_meaning_record_id(record: SelectedGovernedMeaningRecord) -> str:
    digest = deterministic_digest(canonical_json_bytes(selected_meaning_identity_body(record)))
    return f"selected_governed_meaning:{digest}"


def with_expected_selected_meaning_record_id(
    record: SelectedGovernedMeaningRecord,
) -> SelectedGovernedMeaningRecord:
    return replace(record, record_id=expected_selected_meaning_record_id(record))


def expected_package_digest(record: SelectedMeaningConstructionPackage) -> str:
    return deterministic_digest(
        canonical_json_bytes(
            {
                name: getattr(record, name)
                for name in record.__dataclass_fields__
                if name not in {"package_id", "package_digest"}
            }
        )
    )


def expected_package_id(record: SelectedMeaningConstructionPackage) -> str:
    return f"selected_meaning_construction_package:{expected_package_digest(record)}"


def with_expected_package_identity(
    record: SelectedMeaningConstructionPackage,
) -> SelectedMeaningConstructionPackage:
    digest = expected_package_digest(record)
    return replace(
        record,
        package_digest=digest,
        package_id=f"selected_meaning_construction_package:{digest}",
    )


__all__ = (
    "expected_construction_input_id",
    "expected_content_proof_id",
    "expected_decision_id",
    "expected_package_digest",
    "expected_package_id",
    "expected_preservation_id",
    "expected_receipt_id",
    "expected_selected_meaning_record_id",
    "expected_trace_id",
    "selected_meaning_identity_body",
    "with_expected_construction_input_id",
    "with_expected_content_proof_id",
    "with_expected_decision_id",
    "with_expected_package_identity",
    "with_expected_preservation_id",
    "with_expected_receipt_id",
    "with_expected_selected_meaning_record_id",
    "with_expected_trace_id",
)
