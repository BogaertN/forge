"""Canonical MSM-v1 serialization and strict deserialization for Slice 35D.

This module defines one deterministic UTF-8 JSON representation for the
immutable MeaningStructureManifest v1 records accepted by Slices 35A-35C.
It performs no persistence, filesystem access, network access, migration,
automatic upgrade, bootstrap integration, route handling, tool invocation, or
action execution.

The canonical representation is intentionally strict:

* one versioned envelope;
* exact package, schema, record-kind, lifecycle-state, and enum identities;
* exact fields with no missing or unknown members;
* duplicate JSON object names rejected;
* non-canonical whitespace, ordering, escaping, or trailing data rejected;
* unknown format or schema versions rejected without migration;
* Slice 35B validation required before serialization and after decoding; and
* byte-for-byte round-trip equivalence required for accepted payloads.

Document 2 requires versioned, inspectable semantic ancestry while deferring
its final serialized representation. The constants and JSON mapping below are
the explicit Slice 35D runtime specification for that open implementation
choice. They do not claim to be verbatim field names from Document 2.
"""

from __future__ import annotations

from enum import Enum
import hashlib
import json
from typing import Any, NoReturn

from ._enums import (
    DeliveryContainmentKind,
    ExternalAuthorityKind,
    LineageOriginKind,
    NonSelectionOutcomeKind,
    SemanticDirection,
    SemanticLifecycleState,
    SemanticPreservationClass,
    SemanticRecordKind,
    SemanticTransitionKind,
)
from ._identity import PACKAGE_ID, SCHEMA_ID, SCHEMA_VERSION
from ._records import (
    CandidateMeaningRecord,
    DeliveryContainmentLinkRecord,
    ExpressionLinkRecord,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    GovernedResultReferenceRecord,
    LineageRootRecord,
    MeaningStructureManifestV1,
    NonSelectionOutcomeRecord,
    SelectedGovernedMeaningRecord,
    SemanticTransitionTraceRecord,
    ValidationLinkRecord,
)
from .lifecycle import LIFECYCLE_TRANSITION_RULES
from .validation import validate_manifest

SERIALIZATION_SPEC_ID = "aiweb-msm-v1-canonical-serialization"
SERIALIZATION_SPEC_VERSION = "aiweb-msm-v1-serialization-v1"
CANONICAL_FORMAT_ID = "aiweb-msm-v1-canonical-json"
CANONICAL_FORMAT_VERSION = "1"


class SerializationErrorCode(str, Enum):
    PAYLOAD_TYPE_INVALID = "payload_type_invalid"
    PAYLOAD_UTF8_INVALID = "payload_utf8_invalid"
    JSON_INVALID = "json_invalid"
    DUPLICATE_KEY = "duplicate_key"
    NON_CANONICAL_PAYLOAD = "non_canonical_payload"
    OBJECT_REQUIRED = "object_required"
    ARRAY_REQUIRED = "array_required"
    TEXT_REQUIRED = "text_required"
    NULL_OR_TEXT_REQUIRED = "null_or_text_required"
    MISSING_FIELD = "missing_field"
    UNKNOWN_FIELD = "unknown_field"
    FIXED_VALUE_MISMATCH = "fixed_value_mismatch"
    ENUM_VALUE_UNKNOWN = "enum_value_unknown"
    RECORD_TYPE_UNSUPPORTED = "record_type_unsupported"
    CANONICAL_FORMAT_UNSUPPORTED = "canonical_format_unsupported"
    CANONICAL_FORMAT_VERSION_UNSUPPORTED = (
        "canonical_format_version_unsupported"
    )
    PACKAGE_ID_INCOMPATIBLE = "package_id_incompatible"
    SCHEMA_ID_INCOMPATIBLE = "schema_id_incompatible"
    SCHEMA_VERSION_UNSUPPORTED = "schema_version_unsupported"
    MANIFEST_VALIDATION_FAILED = "manifest_validation_failed"
    LIFECYCLE_HISTORY_INVALID = "lifecycle_history_invalid"


class CanonicalSerializationError(ValueError):
    """Bounded fail-closed error for canonical serialization operations."""

    def __init__(
        self,
        code: SerializationErrorCode,
        *,
        path: str,
        detail: str,
    ) -> None:
        self.code = code
        self.path = path
        self.detail = detail
        super().__init__(f"{code.value} at {path}: {detail}")


def _fail(
    code: SerializationErrorCode,
    *,
    path: str,
    detail: str,
) -> NoReturn:
    raise CanonicalSerializationError(code, path=path, detail=detail)


def _enum_value(value: Any, expected_type: type[Enum], *, path: str) -> str:
    if type(value) is not expected_type:
        _fail(
            SerializationErrorCode.RECORD_TYPE_UNSUPPORTED,
            path=path,
            detail=f"expected {expected_type.__name__}",
        )
    assert isinstance(value.value, str)
    return value.value


def _text_tuple(values: Any, *, path: str) -> list[str]:
    if type(values) is not tuple:
        _fail(
            SerializationErrorCode.ARRAY_REQUIRED,
            path=path,
            detail="expected immutable tuple",
        )
    result: list[str] = []
    for index, value in enumerate(values):
        if type(value) is not str:
            _fail(
                SerializationErrorCode.TEXT_REQUIRED,
                path=f"{path}[{index}]",
                detail="expected text",
            )
        result.append(value)
    return result


def _enum_tuple(
    values: Any,
    expected_type: type[Enum],
    *,
    path: str,
) -> list[str]:
    if type(values) is not tuple:
        _fail(
            SerializationErrorCode.ARRAY_REQUIRED,
            path=path,
            detail="expected immutable tuple",
        )
    return [
        _enum_value(value, expected_type, path=f"{path}[{index}]")
        for index, value in enumerate(values)
    ]


def _encode_lineage_root(record: LineageRootRecord) -> dict[str, Any]:
    return {
        "direction": _enum_value(
            record.direction, SemanticDirection, path="lineage_root.direction"
        ),
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="lineage_root.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "origin_kind": _enum_value(
            record.origin_kind,
            LineageOriginKind,
            path="lineage_root.origin_kind",
        ),
        "origin_ref": record.origin_ref,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="lineage_root.record_kind",
        ),
        "schema_version": record.schema_version,
    }


def _encode_candidate(record: CandidateMeaningRecord) -> dict[str, Any]:
    return {
        "ambiguity_reasons": _text_tuple(
            record.ambiguity_reasons, path="candidate.ambiguity_reasons"
        ),
        "authority_sensitive_implications": _text_tuple(
            record.authority_sensitive_implications,
            path="candidate.authority_sensitive_implications",
        ),
        "communicative_act": record.communicative_act,
        "concept_refs": _text_tuple(record.concept_refs, path="candidate.concept_refs"),
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="candidate.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "meaning_modifiers": _text_tuple(
            record.meaning_modifiers, path="candidate.meaning_modifiers"
        ),
        "preservation_classes": _enum_tuple(
            record.preservation_classes,
            SemanticPreservationClass,
            path="candidate.preservation_classes",
        ),
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="candidate.record_kind",
        ),
        "relation_refs": _text_tuple(
            record.relation_refs, path="candidate.relation_refs"
        ),
        "schema_version": record.schema_version,
        "source_expression_ref": record.source_expression_ref,
        "unresolved_referents": _text_tuple(
            record.unresolved_referents, path="candidate.unresolved_referents"
        ),
    }


def _encode_non_selection(record: NonSelectionOutcomeRecord) -> dict[str, Any]:
    return {
        "candidate_refs": _text_tuple(
            record.candidate_refs, path="non_selection.candidate_refs"
        ),
        "external_authority_refs": _text_tuple(
            record.external_authority_refs,
            path="non_selection.external_authority_refs",
        ),
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="non_selection.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "outcome_kind": _enum_value(
            record.outcome_kind,
            NonSelectionOutcomeKind,
            path="non_selection.outcome_kind",
        ),
        "reasons": _text_tuple(record.reasons, path="non_selection.reasons"),
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="non_selection.record_kind",
        ),
        "required_clarifications": _text_tuple(
            record.required_clarifications,
            path="non_selection.required_clarifications",
        ),
        "schema_version": record.schema_version,
    }


def _encode_selected(record: SelectedGovernedMeaningRecord) -> dict[str, Any]:
    return {
        "authority_sensitive_distinctions": _text_tuple(
            record.authority_sensitive_distinctions,
            path="selected.authority_sensitive_distinctions",
        ),
        "communicative_act": record.communicative_act,
        "concept_refs": _text_tuple(record.concept_refs, path="selected.concept_refs"),
        "inherited_limitations": _text_tuple(
            record.inherited_limitations, path="selected.inherited_limitations"
        ),
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="selected.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "meaning_modifiers": _text_tuple(
            record.meaning_modifiers, path="selected.meaning_modifiers"
        ),
        "preservation_classes": _enum_tuple(
            record.preservation_classes,
            SemanticPreservationClass,
            path="selected.preservation_classes",
        ),
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="selected.record_kind",
        ),
        "relation_refs": _text_tuple(
            record.relation_refs, path="selected.relation_refs"
        ),
        "schema_version": record.schema_version,
        "selected_candidate_ref": record.selected_candidate_ref,
        "selection_authority_ref": record.selection_authority_ref,
    }


def _encode_result(record: GovernedResultReferenceRecord) -> dict[str, Any]:
    return {
        "external_authority_ref": record.external_authority_ref,
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="governed_result.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="governed_result.record_kind",
        ),
        "schema_version": record.schema_version,
        "selected_meaning_ref": record.selected_meaning_ref,
        "semantic_relevance": record.semantic_relevance,
    }


def _encode_outward(record: GovernedOutwardMeaningRecord) -> dict[str, Any]:
    return {
        "external_dependency_refs": _text_tuple(
            record.external_dependency_refs,
            path="outward.external_dependency_refs",
        ),
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="outward.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "outward_basis_refs": _text_tuple(
            record.outward_basis_refs, path="outward.outward_basis_refs"
        ),
        "permitted_claims": _text_tuple(
            record.permitted_claims, path="outward.permitted_claims"
        ),
        "preservation_classes": _enum_tuple(
            record.preservation_classes,
            SemanticPreservationClass,
            path="outward.preservation_classes",
        ),
        "prior_selected_meaning_ref": record.prior_selected_meaning_ref,
        "prohibited_enlargements": _text_tuple(
            record.prohibited_enlargements,
            path="outward.prohibited_enlargements",
        ),
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="outward.record_kind",
        ),
        "required_qualifications": _text_tuple(
            record.required_qualifications,
            path="outward.required_qualifications",
        ),
        "schema_version": record.schema_version,
    }


def _encode_expression(record: ExpressionLinkRecord) -> dict[str, Any]:
    return {
        "expression_candidate_ref": record.expression_candidate_ref,
        "governed_outward_meaning_ref": record.governed_outward_meaning_ref,
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="expression.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="expression.record_kind",
        ),
        "schema_version": record.schema_version,
    }


def _encode_validation(record: ValidationLinkRecord) -> dict[str, Any]:
    return {
        "expression_link_ref": record.expression_link_ref,
        "external_validation_disposition": record.external_validation_disposition,
        "external_validation_receipt_ref": record.external_validation_receipt_ref,
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="validation.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="validation.record_kind",
        ),
        "schema_version": record.schema_version,
    }


def _encode_delivery(record: DeliveryContainmentLinkRecord) -> dict[str, Any]:
    return {
        "disposition": _enum_value(
            record.disposition,
            DeliveryContainmentKind,
            path="delivery.disposition",
        ),
        "external_receipt_ref": record.external_receipt_ref,
        "lifecycle_state": _enum_value(
            record.lifecycle_state,
            SemanticLifecycleState,
            path="delivery.lifecycle_state",
        ),
        "lineage_id": record.lineage_id,
        "prior_link_ref": record.prior_link_ref,
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="delivery.record_kind",
        ),
        "schema_version": record.schema_version,
    }


def _encode_authority(record: ExternalAuthorityReferenceRecord) -> dict[str, Any]:
    return {
        "authority_kind": _enum_value(
            record.authority_kind,
            ExternalAuthorityKind,
            path="authority.authority_kind",
        ),
        "external_object_ref": record.external_object_ref,
        "lineage_id": record.lineage_id,
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="authority.record_kind",
        ),
        "schema_version": record.schema_version,
        "semantic_relevance": record.semantic_relevance,
    }


def _encode_trace(record: SemanticTransitionTraceRecord) -> dict[str, Any]:
    return {
        "authority_reference_ref": record.authority_reference_ref,
        "from_record_ref": record.from_record_ref,
        "from_state": _enum_value(
            record.from_state,
            SemanticLifecycleState,
            path="trace.from_state",
        ),
        "lineage_id": record.lineage_id,
        "reason": record.reason,
        "record_id": record.record_id,
        "record_kind": _enum_value(
            record.record_kind,
            SemanticRecordKind,
            path="trace.record_kind",
        ),
        "schema_version": record.schema_version,
        "to_record_ref": record.to_record_ref,
        "to_state": _enum_value(
            record.to_state,
            SemanticLifecycleState,
            path="trace.to_state",
        ),
        "transition_kind": _enum_value(
            record.transition_kind,
            SemanticTransitionKind,
            path="trace.transition_kind",
        ),
    }


def _encode_manifest(manifest: MeaningStructureManifestV1) -> dict[str, Any]:
    return {
        "candidate_meanings": [
            _encode_candidate(record) for record in manifest.candidate_meanings
        ],
        "delivery_or_containment_links": [
            _encode_delivery(record)
            for record in manifest.delivery_or_containment_links
        ],
        "expression_links": [
            _encode_expression(record) for record in manifest.expression_links
        ],
        "external_authority_references": [
            _encode_authority(record)
            for record in manifest.external_authority_references
        ],
        "governed_outward_meanings": [
            _encode_outward(record) for record in manifest.governed_outward_meanings
        ],
        "governed_result_references": [
            _encode_result(record) for record in manifest.governed_result_references
        ],
        "lineage_root": _encode_lineage_root(manifest.lineage_root),
        "manifest_id": manifest.manifest_id,
        "non_selection_outcomes": [
            _encode_non_selection(record)
            for record in manifest.non_selection_outcomes
        ],
        "package_id": manifest.package_id,
        "record_kind": _enum_value(
            manifest.record_kind,
            SemanticRecordKind,
            path="manifest.record_kind",
        ),
        "schema_id": manifest.schema_id,
        "schema_version": manifest.schema_version,
        "selected_governed_meanings": [
            _encode_selected(record)
            for record in manifest.selected_governed_meanings
        ],
        "semantic_transition_traces": [
            _encode_trace(record) for record in manifest.semantic_transition_traces
        ],
        "validation_links": [
            _encode_validation(record) for record in manifest.validation_links
        ],
    }


def _canonical_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        _fail(
            SerializationErrorCode.JSON_INVALID,
            path="$",
            detail=str(error),
        )
    return text.encode("ascii")


def _state_for_record(record: Any) -> SemanticLifecycleState | None:
    state = getattr(record, "lifecycle_state", None)
    return state if type(state) is SemanticLifecycleState else None


def _record_index(manifest: MeaningStructureManifestV1) -> dict[str, Any]:
    records: list[Any] = [manifest.lineage_root]
    records.extend(manifest.candidate_meanings)
    records.extend(manifest.non_selection_outcomes)
    records.extend(manifest.selected_governed_meanings)
    records.extend(manifest.governed_result_references)
    records.extend(manifest.governed_outward_meanings)
    records.extend(manifest.expression_links)
    records.extend(manifest.validation_links)
    records.extend(manifest.delivery_or_containment_links)
    records.extend(manifest.external_authority_references)
    index: dict[str, Any] = {manifest.lineage_root.lineage_id: manifest.lineage_root}
    for record in records[1:]:
        index[record.record_id] = record
    return index


def _authority_binding_matches(
    successor: Any,
    authority: ExternalAuthorityReferenceRecord | None,
) -> bool:
    if authority is None:
        return True
    authority_values = {authority.record_id, authority.external_object_ref}
    if type(successor) is NonSelectionOutcomeRecord:
        return authority.record_id in successor.external_authority_refs
    if type(successor) is SelectedGovernedMeaningRecord:
        return successor.selection_authority_ref in authority_values
    if type(successor) is GovernedResultReferenceRecord:
        return successor.external_authority_ref == authority.record_id
    if type(successor) is GovernedOutwardMeaningRecord:
        return (
            authority.record_id in successor.outward_basis_refs
            or authority.record_id in successor.external_dependency_refs
        )
    if type(successor) is ExpressionLinkRecord:
        return successor.expression_candidate_ref in authority_values
    if type(successor) is ValidationLinkRecord:
        return successor.external_validation_receipt_ref in authority_values
    if type(successor) is DeliveryContainmentLinkRecord:
        return successor.external_receipt_ref in authority_values
    return True


def _relationship_matches(source: Any, successor: Any) -> bool:
    if type(source) is LineageRootRecord:
        if type(successor) is CandidateMeaningRecord:
            return (
                source.origin_kind
                is LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION
                and successor.source_expression_ref == source.origin_ref
            )
        if type(successor) is NonSelectionOutcomeRecord:
            return (
                source.origin_kind
                is LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION
                and not successor.candidate_refs
            )
        if type(successor) is GovernedOutwardMeaningRecord:
            return (
                source.origin_kind
                is LineageOriginKind.AUTHORIZED_OUTWARD_EXPRESSION_PURPOSE
            )
        return False
    if type(source) is CandidateMeaningRecord:
        if type(successor) is NonSelectionOutcomeRecord:
            return source.record_id in successor.candidate_refs
        if type(successor) is SelectedGovernedMeaningRecord:
            return successor.selected_candidate_ref == source.record_id
    if type(source) is NonSelectionOutcomeRecord:
        if type(successor) is CandidateMeaningRecord:
            return True
        if type(successor) is SelectedGovernedMeaningRecord:
            return successor.selected_candidate_ref in source.candidate_refs
        if type(successor) is GovernedOutwardMeaningRecord:
            return source.record_id in successor.outward_basis_refs
    if type(source) is SelectedGovernedMeaningRecord:
        if type(successor) is NonSelectionOutcomeRecord:
            return source.selected_candidate_ref in successor.candidate_refs
        if type(successor) is GovernedResultReferenceRecord:
            return successor.selected_meaning_ref == source.record_id
        if type(successor) is GovernedOutwardMeaningRecord:
            return (
                source.record_id in successor.outward_basis_refs
                or successor.prior_selected_meaning_ref == source.record_id
            )
    if type(source) is GovernedResultReferenceRecord and type(successor) is GovernedOutwardMeaningRecord:
        return source.record_id in successor.outward_basis_refs
    if type(source) is GovernedOutwardMeaningRecord and type(successor) is ExpressionLinkRecord:
        return successor.governed_outward_meaning_ref == source.record_id
    if type(source) is ExpressionLinkRecord:
        if type(successor) is ValidationLinkRecord:
            return successor.expression_link_ref == source.record_id
        if type(successor) is DeliveryContainmentLinkRecord:
            return successor.prior_link_ref == source.record_id
    if type(source) is ValidationLinkRecord and type(successor) is DeliveryContainmentLinkRecord:
        return successor.prior_link_ref == source.record_id
    return False


def _assert_lifecycle_history(manifest: MeaningStructureManifestV1) -> None:
    rules = {
        (rule.from_state, rule.to_state): rule
        for rule in LIFECYCLE_TRANSITION_RULES
    }
    index = _record_index(manifest)
    substantive_types = (
        CandidateMeaningRecord,
        NonSelectionOutcomeRecord,
        SelectedGovernedMeaningRecord,
        GovernedResultReferenceRecord,
        GovernedOutwardMeaningRecord,
        ExpressionLinkRecord,
        ValidationLinkRecord,
        DeliveryContainmentLinkRecord,
    )
    for trace_index, trace in enumerate(manifest.semantic_transition_traces):
        path = f"manifest.semantic_transition_traces[{trace_index}]"
        source = index.get(trace.from_record_ref)
        successor = index.get(trace.to_record_ref)
        if source is None or successor is None:
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=path,
                detail="transition source or successor is absent",
            )
        if trace.from_record_ref == trace.to_record_ref:
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=path,
                detail="transition may not reference the same record as source and successor",
            )
        source_state = _state_for_record(source)
        successor_state = _state_for_record(successor)
        if source_state is not trace.from_state or successor_state is not trace.to_state:
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=path,
                detail="trace states do not match referenced record states",
            )
        authority: ExternalAuthorityReferenceRecord | None = None
        if trace.authority_reference_ref is not None:
            authority_record = index.get(trace.authority_reference_ref)
            if type(authority_record) is not ExternalAuthorityReferenceRecord:
                _fail(
                    SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                    path=f"{path}.authority_reference_ref",
                    detail="authority reference does not identify an external authority record",
                )
            authority = authority_record

        correction_overlay = trace.transition_kind in {
            SemanticTransitionKind.CORRECTION,
            SemanticTransitionKind.SUPERSESSION,
        }
        if correction_overlay:
            if (
                type(source) is LineageRootRecord
                or type(source) is not type(successor)
                or type(successor) not in substantive_types
                or source_state is not successor_state
                or authority is None
            ):
                _fail(
                    SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                    path=path,
                    detail="correction or supersession violates the accepted immutable-successor law",
                )
            continue

        if successor_state in {
            SemanticLifecycleState.CORRECTED,
            SemanticLifecycleState.SUPERSEDED,
        }:
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=path,
                detail="corrected and superseded are trace dispositions, not synthetic target records",
            )
        rule = rules.get((source_state, successor_state))
        if rule is None or trace.transition_kind not in rule.allowed_kinds:
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=path,
                detail=(
                    f"transition {source_state.value}->{successor_state.value} "
                    f"with kind {trace.transition_kind.value} is not admitted"
                ),
            )
        if rule.authority_required and authority is None:
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=f"{path}.authority_reference_ref",
                detail="accepted lifecycle rule requires external authority",
            )
        if authority is not None and not _authority_binding_matches(successor, authority):
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=f"{path}.authority_reference_ref",
                detail="successor does not carry the named authority or receipt",
            )
        if not _relationship_matches(source, successor):
            _fail(
                SerializationErrorCode.LIFECYCLE_HISTORY_INVALID,
                path=path,
                detail="successor fields do not prove the recorded direct ancestry",
            )


def _assert_valid_for_serialization(manifest: Any) -> MeaningStructureManifestV1:
    if type(manifest) is not MeaningStructureManifestV1:
        _fail(
            SerializationErrorCode.RECORD_TYPE_UNSUPPORTED,
            path="manifest",
            detail="expected exact MeaningStructureManifestV1",
        )
    report = validate_manifest(manifest)
    if not report.ok:
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}" for issue in report.issues
        )
        _fail(
            SerializationErrorCode.MANIFEST_VALIDATION_FAILED,
            path="manifest",
            detail=detail or "manifest validation failed",
        )
    _assert_lifecycle_history(manifest)
    return manifest


def serialize_manifest(manifest: Any) -> bytes:
    """Return the unique canonical UTF-8 JSON bytes for one valid MSM-v1."""

    accepted = _assert_valid_for_serialization(manifest)
    envelope = {
        "canonical_format": CANONICAL_FORMAT_ID,
        "canonical_format_version": CANONICAL_FORMAT_VERSION,
        "manifest": _encode_manifest(accepted),
        "package_id": PACKAGE_ID,
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
    }
    return _canonical_bytes(envelope)


def canonical_manifest_sha256(manifest: Any) -> str:
    """Return the SHA-256 of the canonical bytes without writing any file."""

    return hashlib.sha256(serialize_manifest(manifest)).hexdigest()


class _DuplicateKeyError(ValueError):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


def _object_pairs_no_duplicates(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _reject_json_constant(value: str) -> NoReturn:
    raise ValueError(f"non-standard JSON constant {value!r}")


def _payload_bytes(payload: Any) -> bytes:
    if type(payload) is bytes:
        return payload
    if type(payload) is str:
        try:
            return payload.encode("utf-8", errors="strict")
        except UnicodeEncodeError as error:
            _fail(
                SerializationErrorCode.PAYLOAD_UTF8_INVALID,
                path="$",
                detail=str(error),
            )
    _fail(
        SerializationErrorCode.PAYLOAD_TYPE_INVALID,
        path="$",
        detail="payload must be exact str or bytes",
    )


def _parse_payload(raw: bytes) -> Any:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        _fail(
            SerializationErrorCode.PAYLOAD_UTF8_INVALID,
            path="$",
            detail=str(error),
        )
    if text.startswith("\ufeff"):
        _fail(
            SerializationErrorCode.NON_CANONICAL_PAYLOAD,
            path="$",
            detail="UTF-8 BOM is not canonical",
        )
    try:
        return json.loads(
            text,
            object_pairs_hook=_object_pairs_no_duplicates,
            parse_constant=_reject_json_constant,
        )
    except _DuplicateKeyError as error:
        _fail(
            SerializationErrorCode.DUPLICATE_KEY,
            path="$",
            detail=f"duplicate object member {error.key!r}",
        )
    except (json.JSONDecodeError, ValueError) as error:
        _fail(
            SerializationErrorCode.JSON_INVALID,
            path="$",
            detail=str(error),
        )


def _object(value: Any, *, path: str) -> dict[str, Any]:
    if type(value) is not dict:
        _fail(
            SerializationErrorCode.OBJECT_REQUIRED,
            path=path,
            detail="expected JSON object",
        )
    return value


def _exact_fields(
    value: dict[str, Any],
    expected: tuple[str, ...],
    *,
    path: str,
) -> None:
    expected_set = set(expected)
    actual_set = set(value)
    missing = sorted(expected_set - actual_set)
    unknown = sorted(actual_set - expected_set)
    if missing:
        _fail(
            SerializationErrorCode.MISSING_FIELD,
            path=path,
            detail=f"missing fields: {', '.join(missing)}",
        )
    if unknown:
        _fail(
            SerializationErrorCode.UNKNOWN_FIELD,
            path=path,
            detail=f"unknown fields: {', '.join(unknown)}",
        )


def _text(value: Any, *, path: str) -> str:
    if type(value) is not str:
        _fail(
            SerializationErrorCode.TEXT_REQUIRED,
            path=path,
            detail="expected JSON string",
        )
    return value


def _optional_text(value: Any, *, path: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        _fail(
            SerializationErrorCode.NULL_OR_TEXT_REQUIRED,
            path=path,
            detail="expected null or JSON string",
        )
    return value


def _array(value: Any, *, path: str) -> list[Any]:
    if type(value) is not list:
        _fail(
            SerializationErrorCode.ARRAY_REQUIRED,
            path=path,
            detail="expected JSON array",
        )
    return value


def _decode_text_tuple(value: Any, *, path: str) -> tuple[str, ...]:
    items = _array(value, path=path)
    return tuple(_text(item, path=f"{path}[{index}]") for index, item in enumerate(items))


def _decode_enum(
    value: Any,
    enum_type: type[Enum],
    *,
    path: str,
) -> Any:
    text = _text(value, path=path)
    try:
        return enum_type(text)
    except ValueError:
        _fail(
            SerializationErrorCode.ENUM_VALUE_UNKNOWN,
            path=path,
            detail=f"unknown {enum_type.__name__} value {text!r}",
        )


def _decode_enum_tuple(
    value: Any,
    enum_type: type[Enum],
    *,
    path: str,
) -> tuple[Any, ...]:
    items = _array(value, path=path)
    return tuple(
        _decode_enum(item, enum_type, path=f"{path}[{index}]")
        for index, item in enumerate(items)
    )


def _fixed_text(value: Any, expected: str, *, path: str) -> None:
    actual = _text(value, path=path)
    if actual != expected:
        _fail(
            SerializationErrorCode.FIXED_VALUE_MISMATCH,
            path=path,
            detail=f"expected {expected!r}, received {actual!r}",
        )


def _fixed_enum(
    value: Any,
    expected: Enum,
    enum_type: type[Enum],
    *,
    path: str,
) -> None:
    actual = _decode_enum(value, enum_type, path=path)
    if actual is not expected:
        _fail(
            SerializationErrorCode.FIXED_VALUE_MISMATCH,
            path=path,
            detail=f"expected {expected.value!r}, received {actual.value!r}",
        )


def _fixed_schema_version(value: Any, *, path: str) -> None:
    actual = _text(value, path=path)
    if actual != SCHEMA_VERSION:
        _fail(
            SerializationErrorCode.SCHEMA_VERSION_UNSUPPORTED,
            path=path,
            detail=f"supported schema version is {SCHEMA_VERSION!r}; no migration is authorized",
        )


def _decode_lineage_root(value: Any, *, path: str) -> LineageRootRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "direction",
            "lifecycle_state",
            "lineage_id",
            "origin_kind",
            "origin_ref",
            "record_kind",
            "schema_version",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.LINEAGE_ROOT,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_enum(
        obj["lifecycle_state"],
        SemanticLifecycleState.LINEAGE_ORIGIN,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return LineageRootRecord(
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        origin_kind=_decode_enum(
            obj["origin_kind"], LineageOriginKind, path=f"{path}.origin_kind"
        ),
        origin_ref=_text(obj["origin_ref"], path=f"{path}.origin_ref"),
        direction=_decode_enum(
            obj["direction"], SemanticDirection, path=f"{path}.direction"
        ),
    )


def _decode_candidate(value: Any, *, path: str) -> CandidateMeaningRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "ambiguity_reasons",
            "authority_sensitive_implications",
            "communicative_act",
            "concept_refs",
            "lifecycle_state",
            "lineage_id",
            "meaning_modifiers",
            "preservation_classes",
            "record_id",
            "record_kind",
            "relation_refs",
            "schema_version",
            "source_expression_ref",
            "unresolved_referents",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.CANDIDATE_MEANING,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_enum(
        obj["lifecycle_state"],
        SemanticLifecycleState.CANDIDATE_MEANING,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return CandidateMeaningRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        source_expression_ref=_text(
            obj["source_expression_ref"], path=f"{path}.source_expression_ref"
        ),
        communicative_act=_text(
            obj["communicative_act"], path=f"{path}.communicative_act"
        ),
        concept_refs=_decode_text_tuple(
            obj["concept_refs"], path=f"{path}.concept_refs"
        ),
        relation_refs=_decode_text_tuple(
            obj["relation_refs"], path=f"{path}.relation_refs"
        ),
        meaning_modifiers=_decode_text_tuple(
            obj["meaning_modifiers"], path=f"{path}.meaning_modifiers"
        ),
        ambiguity_reasons=_decode_text_tuple(
            obj["ambiguity_reasons"], path=f"{path}.ambiguity_reasons"
        ),
        unresolved_referents=_decode_text_tuple(
            obj["unresolved_referents"], path=f"{path}.unresolved_referents"
        ),
        authority_sensitive_implications=_decode_text_tuple(
            obj["authority_sensitive_implications"],
            path=f"{path}.authority_sensitive_implications",
        ),
        preservation_classes=_decode_enum_tuple(
            obj["preservation_classes"],
            SemanticPreservationClass,
            path=f"{path}.preservation_classes",
        ),
    )


def _decode_non_selection(value: Any, *, path: str) -> NonSelectionOutcomeRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "candidate_refs",
            "external_authority_refs",
            "lifecycle_state",
            "lineage_id",
            "outcome_kind",
            "reasons",
            "record_id",
            "record_kind",
            "required_clarifications",
            "schema_version",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.NON_SELECTION_OUTCOME,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    outcome_kind = _decode_enum(
        obj["outcome_kind"],
        NonSelectionOutcomeKind,
        path=f"{path}.outcome_kind",
    )
    expected_state = SemanticLifecycleState(outcome_kind.value)
    _fixed_enum(
        obj["lifecycle_state"],
        expected_state,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return NonSelectionOutcomeRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        outcome_kind=outcome_kind,
        candidate_refs=_decode_text_tuple(
            obj["candidate_refs"], path=f"{path}.candidate_refs"
        ),
        reasons=_decode_text_tuple(obj["reasons"], path=f"{path}.reasons"),
        required_clarifications=_decode_text_tuple(
            obj["required_clarifications"],
            path=f"{path}.required_clarifications",
        ),
        external_authority_refs=_decode_text_tuple(
            obj["external_authority_refs"],
            path=f"{path}.external_authority_refs",
        ),
    )


def _decode_selected(value: Any, *, path: str) -> SelectedGovernedMeaningRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "authority_sensitive_distinctions",
            "communicative_act",
            "concept_refs",
            "inherited_limitations",
            "lifecycle_state",
            "lineage_id",
            "meaning_modifiers",
            "preservation_classes",
            "record_id",
            "record_kind",
            "relation_refs",
            "schema_version",
            "selected_candidate_ref",
            "selection_authority_ref",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.SELECTED_GOVERNED_MEANING,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_enum(
        obj["lifecycle_state"],
        SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return SelectedGovernedMeaningRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        selected_candidate_ref=_text(
            obj["selected_candidate_ref"], path=f"{path}.selected_candidate_ref"
        ),
        selection_authority_ref=_text(
            obj["selection_authority_ref"], path=f"{path}.selection_authority_ref"
        ),
        communicative_act=_text(
            obj["communicative_act"], path=f"{path}.communicative_act"
        ),
        concept_refs=_decode_text_tuple(
            obj["concept_refs"], path=f"{path}.concept_refs"
        ),
        relation_refs=_decode_text_tuple(
            obj["relation_refs"], path=f"{path}.relation_refs"
        ),
        meaning_modifiers=_decode_text_tuple(
            obj["meaning_modifiers"], path=f"{path}.meaning_modifiers"
        ),
        inherited_limitations=_decode_text_tuple(
            obj["inherited_limitations"], path=f"{path}.inherited_limitations"
        ),
        authority_sensitive_distinctions=_decode_text_tuple(
            obj["authority_sensitive_distinctions"],
            path=f"{path}.authority_sensitive_distinctions",
        ),
        preservation_classes=_decode_enum_tuple(
            obj["preservation_classes"],
            SemanticPreservationClass,
            path=f"{path}.preservation_classes",
        ),
    )


def _decode_result(value: Any, *, path: str) -> GovernedResultReferenceRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "external_authority_ref",
            "lifecycle_state",
            "lineage_id",
            "record_id",
            "record_kind",
            "schema_version",
            "selected_meaning_ref",
            "semantic_relevance",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.GOVERNED_RESULT_REFERENCE,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_enum(
        obj["lifecycle_state"],
        SemanticLifecycleState.GOVERNED_RESULT_REFERENCED,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return GovernedResultReferenceRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        selected_meaning_ref=_text(
            obj["selected_meaning_ref"], path=f"{path}.selected_meaning_ref"
        ),
        external_authority_ref=_text(
            obj["external_authority_ref"], path=f"{path}.external_authority_ref"
        ),
        semantic_relevance=_text(
            obj["semantic_relevance"], path=f"{path}.semantic_relevance"
        ),
    )


def _decode_outward(value: Any, *, path: str) -> GovernedOutwardMeaningRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "external_dependency_refs",
            "lifecycle_state",
            "lineage_id",
            "outward_basis_refs",
            "permitted_claims",
            "preservation_classes",
            "prior_selected_meaning_ref",
            "prohibited_enlargements",
            "record_id",
            "record_kind",
            "required_qualifications",
            "schema_version",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.GOVERNED_OUTWARD_MEANING,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_enum(
        obj["lifecycle_state"],
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return GovernedOutwardMeaningRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        outward_basis_refs=_decode_text_tuple(
            obj["outward_basis_refs"], path=f"{path}.outward_basis_refs"
        ),
        prior_selected_meaning_ref=_optional_text(
            obj["prior_selected_meaning_ref"],
            path=f"{path}.prior_selected_meaning_ref",
        ),
        permitted_claims=_decode_text_tuple(
            obj["permitted_claims"], path=f"{path}.permitted_claims"
        ),
        required_qualifications=_decode_text_tuple(
            obj["required_qualifications"],
            path=f"{path}.required_qualifications",
        ),
        prohibited_enlargements=_decode_text_tuple(
            obj["prohibited_enlargements"],
            path=f"{path}.prohibited_enlargements",
        ),
        external_dependency_refs=_decode_text_tuple(
            obj["external_dependency_refs"],
            path=f"{path}.external_dependency_refs",
        ),
        preservation_classes=_decode_enum_tuple(
            obj["preservation_classes"],
            SemanticPreservationClass,
            path=f"{path}.preservation_classes",
        ),
    )


def _decode_expression(value: Any, *, path: str) -> ExpressionLinkRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "expression_candidate_ref",
            "governed_outward_meaning_ref",
            "lifecycle_state",
            "lineage_id",
            "record_id",
            "record_kind",
            "schema_version",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.EXPRESSION_LINK,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_enum(
        obj["lifecycle_state"],
        SemanticLifecycleState.EXPRESSION_LINKED,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return ExpressionLinkRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        governed_outward_meaning_ref=_text(
            obj["governed_outward_meaning_ref"],
            path=f"{path}.governed_outward_meaning_ref",
        ),
        expression_candidate_ref=_text(
            obj["expression_candidate_ref"],
            path=f"{path}.expression_candidate_ref",
        ),
    )


def _decode_validation(value: Any, *, path: str) -> ValidationLinkRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "expression_link_ref",
            "external_validation_disposition",
            "external_validation_receipt_ref",
            "lifecycle_state",
            "lineage_id",
            "record_id",
            "record_kind",
            "schema_version",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.VALIDATION_LINK,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_enum(
        obj["lifecycle_state"],
        SemanticLifecycleState.VALIDATION_LINKED,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return ValidationLinkRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        expression_link_ref=_text(
            obj["expression_link_ref"], path=f"{path}.expression_link_ref"
        ),
        external_validation_receipt_ref=_text(
            obj["external_validation_receipt_ref"],
            path=f"{path}.external_validation_receipt_ref",
        ),
        external_validation_disposition=_text(
            obj["external_validation_disposition"],
            path=f"{path}.external_validation_disposition",
        ),
    )


def _decode_delivery(value: Any, *, path: str) -> DeliveryContainmentLinkRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "disposition",
            "external_receipt_ref",
            "lifecycle_state",
            "lineage_id",
            "prior_link_ref",
            "record_id",
            "record_kind",
            "schema_version",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.DELIVERY_OR_CONTAINMENT_LINK,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    disposition = _decode_enum(
        obj["disposition"],
        DeliveryContainmentKind,
        path=f"{path}.disposition",
    )
    expected_state = SemanticLifecycleState(disposition.value)
    _fixed_enum(
        obj["lifecycle_state"],
        expected_state,
        SemanticLifecycleState,
        path=f"{path}.lifecycle_state",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return DeliveryContainmentLinkRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        prior_link_ref=_text(
            obj["prior_link_ref"], path=f"{path}.prior_link_ref"
        ),
        disposition=disposition,
        external_receipt_ref=_text(
            obj["external_receipt_ref"], path=f"{path}.external_receipt_ref"
        ),
    )


def _decode_authority(value: Any, *, path: str) -> ExternalAuthorityReferenceRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "authority_kind",
            "external_object_ref",
            "lineage_id",
            "record_id",
            "record_kind",
            "schema_version",
            "semantic_relevance",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.EXTERNAL_AUTHORITY_REFERENCE,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return ExternalAuthorityReferenceRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        authority_kind=_decode_enum(
            obj["authority_kind"],
            ExternalAuthorityKind,
            path=f"{path}.authority_kind",
        ),
        external_object_ref=_text(
            obj["external_object_ref"], path=f"{path}.external_object_ref"
        ),
        semantic_relevance=_text(
            obj["semantic_relevance"], path=f"{path}.semantic_relevance"
        ),
    )


def _decode_trace(value: Any, *, path: str) -> SemanticTransitionTraceRecord:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "authority_reference_ref",
            "from_record_ref",
            "from_state",
            "lineage_id",
            "reason",
            "record_id",
            "record_kind",
            "schema_version",
            "to_record_ref",
            "to_state",
            "transition_kind",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.SEMANTIC_TRANSITION_TRACE,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return SemanticTransitionTraceRecord(
        record_id=_text(obj["record_id"], path=f"{path}.record_id"),
        lineage_id=_text(obj["lineage_id"], path=f"{path}.lineage_id"),
        from_record_ref=_text(
            obj["from_record_ref"], path=f"{path}.from_record_ref"
        ),
        to_record_ref=_text(obj["to_record_ref"], path=f"{path}.to_record_ref"),
        from_state=_decode_enum(
            obj["from_state"], SemanticLifecycleState, path=f"{path}.from_state"
        ),
        to_state=_decode_enum(
            obj["to_state"], SemanticLifecycleState, path=f"{path}.to_state"
        ),
        transition_kind=_decode_enum(
            obj["transition_kind"],
            SemanticTransitionKind,
            path=f"{path}.transition_kind",
        ),
        reason=_text(obj["reason"], path=f"{path}.reason"),
        authority_reference_ref=_optional_text(
            obj["authority_reference_ref"],
            path=f"{path}.authority_reference_ref",
        ),
    )


def _decode_record_array(
    value: Any,
    decoder: Any,
    *,
    path: str,
) -> tuple[Any, ...]:
    items = _array(value, path=path)
    return tuple(
        decoder(item, path=f"{path}[{index}]")
        for index, item in enumerate(items)
    )


def _decode_manifest(value: Any, *, path: str) -> MeaningStructureManifestV1:
    obj = _object(value, path=path)
    _exact_fields(
        obj,
        (
            "candidate_meanings",
            "delivery_or_containment_links",
            "expression_links",
            "external_authority_references",
            "governed_outward_meanings",
            "governed_result_references",
            "lineage_root",
            "manifest_id",
            "non_selection_outcomes",
            "package_id",
            "record_kind",
            "schema_id",
            "schema_version",
            "selected_governed_meanings",
            "semantic_transition_traces",
            "validation_links",
        ),
        path=path,
    )
    _fixed_enum(
        obj["record_kind"],
        SemanticRecordKind.MEANING_STRUCTURE_MANIFEST,
        SemanticRecordKind,
        path=f"{path}.record_kind",
    )
    package_id = _text(obj["package_id"], path=f"{path}.package_id")
    if package_id != PACKAGE_ID:
        _fail(
            SerializationErrorCode.PACKAGE_ID_INCOMPATIBLE,
            path=f"{path}.package_id",
            detail=f"expected {PACKAGE_ID!r}, received {package_id!r}",
        )
    schema_id = _text(obj["schema_id"], path=f"{path}.schema_id")
    if schema_id != SCHEMA_ID:
        _fail(
            SerializationErrorCode.SCHEMA_ID_INCOMPATIBLE,
            path=f"{path}.schema_id",
            detail=f"expected {SCHEMA_ID!r}, received {schema_id!r}",
        )
    _fixed_schema_version(obj["schema_version"], path=f"{path}.schema_version")
    return MeaningStructureManifestV1(
        manifest_id=_text(obj["manifest_id"], path=f"{path}.manifest_id"),
        lineage_root=_decode_lineage_root(
            obj["lineage_root"], path=f"{path}.lineage_root"
        ),
        candidate_meanings=_decode_record_array(
            obj["candidate_meanings"],
            _decode_candidate,
            path=f"{path}.candidate_meanings",
        ),
        non_selection_outcomes=_decode_record_array(
            obj["non_selection_outcomes"],
            _decode_non_selection,
            path=f"{path}.non_selection_outcomes",
        ),
        selected_governed_meanings=_decode_record_array(
            obj["selected_governed_meanings"],
            _decode_selected,
            path=f"{path}.selected_governed_meanings",
        ),
        governed_result_references=_decode_record_array(
            obj["governed_result_references"],
            _decode_result,
            path=f"{path}.governed_result_references",
        ),
        governed_outward_meanings=_decode_record_array(
            obj["governed_outward_meanings"],
            _decode_outward,
            path=f"{path}.governed_outward_meanings",
        ),
        expression_links=_decode_record_array(
            obj["expression_links"],
            _decode_expression,
            path=f"{path}.expression_links",
        ),
        validation_links=_decode_record_array(
            obj["validation_links"],
            _decode_validation,
            path=f"{path}.validation_links",
        ),
        delivery_or_containment_links=_decode_record_array(
            obj["delivery_or_containment_links"],
            _decode_delivery,
            path=f"{path}.delivery_or_containment_links",
        ),
        external_authority_references=_decode_record_array(
            obj["external_authority_references"],
            _decode_authority,
            path=f"{path}.external_authority_references",
        ),
        semantic_transition_traces=_decode_record_array(
            obj["semantic_transition_traces"],
            _decode_trace,
            path=f"{path}.semantic_transition_traces",
        ),
    )


def _decode_envelope(value: Any) -> MeaningStructureManifestV1:
    obj = _object(value, path="$")
    _exact_fields(
        obj,
        (
            "canonical_format",
            "canonical_format_version",
            "manifest",
            "package_id",
            "schema_id",
            "schema_version",
        ),
        path="$",
    )
    canonical_format = _text(obj["canonical_format"], path="$.canonical_format")
    if canonical_format != CANONICAL_FORMAT_ID:
        _fail(
            SerializationErrorCode.CANONICAL_FORMAT_UNSUPPORTED,
            path="$.canonical_format",
            detail=f"expected {CANONICAL_FORMAT_ID!r}, received {canonical_format!r}",
        )
    format_version = _text(
        obj["canonical_format_version"], path="$.canonical_format_version"
    )
    if format_version != CANONICAL_FORMAT_VERSION:
        _fail(
            SerializationErrorCode.CANONICAL_FORMAT_VERSION_UNSUPPORTED,
            path="$.canonical_format_version",
            detail=(
                f"supported format version is {CANONICAL_FORMAT_VERSION!r}; "
                "no automatic upgrade is authorized"
            ),
        )
    package_id = _text(obj["package_id"], path="$.package_id")
    if package_id != PACKAGE_ID:
        _fail(
            SerializationErrorCode.PACKAGE_ID_INCOMPATIBLE,
            path="$.package_id",
            detail=f"expected {PACKAGE_ID!r}, received {package_id!r}",
        )
    schema_id = _text(obj["schema_id"], path="$.schema_id")
    if schema_id != SCHEMA_ID:
        _fail(
            SerializationErrorCode.SCHEMA_ID_INCOMPATIBLE,
            path="$.schema_id",
            detail=f"expected {SCHEMA_ID!r}, received {schema_id!r}",
        )
    _fixed_schema_version(obj["schema_version"], path="$.schema_version")
    return _decode_manifest(obj["manifest"], path="$.manifest")


def deserialize_manifest(payload: Any) -> MeaningStructureManifestV1:
    """Decode only the exact canonical MSM-v1 representation.

    Unknown or incompatible versions fail closed. This function performs no
    migration, coercive upgrade, repair, or fallback interpretation.
    """

    raw = _payload_bytes(payload)
    parsed = _parse_payload(raw)
    manifest = _decode_envelope(parsed)
    report = validate_manifest(manifest)
    if not report.ok:
        detail = "; ".join(
            f"{issue.path}:{issue.code.value}" for issue in report.issues
        )
        _fail(
            SerializationErrorCode.MANIFEST_VALIDATION_FAILED,
            path="$.manifest",
            detail=detail or "manifest validation failed",
        )
    canonical = serialize_manifest(manifest)
    if raw != canonical:
        _fail(
            SerializationErrorCode.NON_CANONICAL_PAYLOAD,
            path="$",
            detail="payload is valid JSON data but not the unique canonical encoding",
        )
    return manifest


__all__ = (
    "CANONICAL_FORMAT_ID",
    "CANONICAL_FORMAT_VERSION",
    "SERIALIZATION_SPEC_ID",
    "SERIALIZATION_SPEC_VERSION",
    "CanonicalSerializationError",
    "SerializationErrorCode",
    "canonical_manifest_sha256",
    "deserialize_manifest",
    "serialize_manifest",
)
