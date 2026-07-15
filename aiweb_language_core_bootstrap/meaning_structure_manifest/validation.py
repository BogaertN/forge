"""Deterministic validation for MeaningStructureManifest v1 Slice 35B.

This module validates constructor-populated MSM-v1 records without mutating
records, authorizing lifecycle transitions, serializing data, persisting state,
connecting runtime paths, or exercising any external authority.

Document 2 binds semantic responsibilities while leaving final identifiers and
storage representation open. Slice 35B therefore uses a transparent bounded
mapping:

* local manifest, lineage, and record identifiers use a conservative textual
  identifier grammar;
* external references remain opaque non-empty text;
* record identities, schema identities, lineage membership, uniqueness, and
  reference relationships are validated deterministically;
* no allowed-transition table or transition authorization exists here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any

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

_LOCAL_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]*\Z")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


class ManifestValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_ENUM = "invalid_enum"
    INVALID_TUPLE = "invalid_tuple"
    DUPLICATE_TUPLE_VALUE = "duplicate_tuple_value"
    IDENTITY_MISMATCH = "identity_mismatch"
    RECORD_KIND_MISMATCH = "record_kind_mismatch"
    LIFECYCLE_STATE_MISMATCH = "lifecycle_state_mismatch"
    LINEAGE_MISMATCH = "lineage_mismatch"
    ORIGIN_DIRECTION_MISMATCH = "origin_direction_mismatch"
    DUPLICATE_RECORD_ID = "duplicate_record_id"
    IDENTIFIER_COLLISION = "identifier_collision"
    UNRESOLVED_REFERENCE = "unresolved_reference"
    REFERENCE_KIND_MISMATCH = "reference_kind_mismatch"


@dataclass(frozen=True, slots=True)
class ManifestValidationIssue:
    path: str
    code: ManifestValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ManifestValidationReport:
    schema_version: str
    issues: tuple[ManifestValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


class MeaningStructureManifestValidationError(ValueError):
    """Raised by assert_valid_manifest when deterministic validation fails."""

    def __init__(self, report: ManifestValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "MeaningStructureManifest validation failed")


def _issue(
    issues: list[ManifestValidationIssue],
    path: str,
    code: ManifestValidationCode,
    detail: str,
) -> None:
    issues.append(ManifestValidationIssue(path=path, code=code, detail=detail))


def _require_text(
    value: Any,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> bool:
    if not isinstance(value, str):
        _issue(issues, path, ManifestValidationCode.TYPE_MISMATCH, "expected str")
        return False
    if not value or not value.strip():
        _issue(
            issues,
            path,
            ManifestValidationCode.REQUIRED_VALUE_MISSING,
            "text must be non-empty",
        )
        return False
    if value != value.strip() or _CONTROL_RE.search(value):
        _issue(
            issues,
            path,
            ManifestValidationCode.INVALID_TEXT,
            "text must be trimmed and contain no control characters",
        )
        return False
    return True


def _require_optional_text(
    value: Any,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> bool:
    if value is None:
        return True
    return _require_text(value, path=path, issues=issues)


def _require_local_identifier(
    value: Any,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> bool:
    if not _require_text(value, path=path, issues=issues):
        return False
    if _LOCAL_IDENTIFIER_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            ManifestValidationCode.INVALID_IDENTIFIER,
            "expected [A-Za-z0-9][A-Za-z0-9._:-]*",
        )
        return False
    return True


def _require_enum(
    value: Any,
    expected_type: type[Enum],
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> bool:
    if not isinstance(value, expected_type):
        _issue(
            issues,
            path,
            ManifestValidationCode.INVALID_ENUM,
            f"expected {expected_type.__name__}",
        )
        return False
    return True


def _require_tuple(
    value: Any,
    expected_item_type: type[Any],
    *,
    path: str,
    issues: list[ManifestValidationIssue],
    text_items: bool = False,
) -> tuple[Any, ...]:
    if not isinstance(value, tuple):
        _issue(
            issues,
            path,
            ManifestValidationCode.INVALID_TUPLE,
            "expected tuple",
        )
        return ()
    valid_items: list[Any] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if text_items:
            if _require_text(item, path=item_path, issues=issues):
                valid_items.append(item)
        elif not isinstance(item, expected_item_type):
            _issue(
                issues,
                item_path,
                ManifestValidationCode.TYPE_MISMATCH,
                f"expected {expected_item_type.__name__}",
            )
        else:
            valid_items.append(item)
    try:
        duplicate = len(value) != len(set(value))
    except TypeError:
        duplicate = False
    if duplicate:
        _issue(
            issues,
            path,
            ManifestValidationCode.DUPLICATE_TUPLE_VALUE,
            "tuple values must be unique",
        )
    return tuple(valid_items)


def _require_fixed(
    value: Any,
    expected: Any,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
    code: ManifestValidationCode = ManifestValidationCode.IDENTITY_MISMATCH,
) -> None:
    if value != expected or type(value) is not type(expected):
        _issue(issues, path, code, f"expected {expected!r}")


def _record_path(record: Any, fallback: str) -> str:
    record_id = getattr(record, "record_id", None)
    return f"records[{record_id}]" if isinstance(record_id, str) else fallback


def _validate_common_record_identity(
    record: Any,
    *,
    path: str,
    expected_kind: SemanticRecordKind,
    expected_state: SemanticLifecycleState | None,
    issues: list[ManifestValidationIssue],
) -> None:
    _require_local_identifier(record.record_id, path=f"{path}.record_id", issues=issues)
    _require_local_identifier(record.lineage_id, path=f"{path}.lineage_id", issues=issues)
    _require_fixed(
        record.record_kind,
        expected_kind,
        path=f"{path}.record_kind",
        issues=issues,
        code=ManifestValidationCode.RECORD_KIND_MISMATCH,
    )
    _require_fixed(
        record.schema_version,
        SCHEMA_VERSION,
        path=f"{path}.schema_version",
        issues=issues,
    )
    if expected_state is not None:
        _require_fixed(
            record.lifecycle_state,
            expected_state,
            path=f"{path}.lifecycle_state",
            issues=issues,
            code=ManifestValidationCode.LIFECYCLE_STATE_MISMATCH,
        )


def _validate_lineage_root(
    record: LineageRootRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _require_local_identifier(record.lineage_id, path=f"{path}.lineage_id", issues=issues)
    _require_enum(record.origin_kind, LineageOriginKind, path=f"{path}.origin_kind", issues=issues)
    _require_text(record.origin_ref, path=f"{path}.origin_ref", issues=issues)
    _require_enum(record.direction, SemanticDirection, path=f"{path}.direction", issues=issues)
    _require_fixed(
        record.record_kind,
        SemanticRecordKind.LINEAGE_ROOT,
        path=f"{path}.record_kind",
        issues=issues,
        code=ManifestValidationCode.RECORD_KIND_MISMATCH,
    )
    _require_fixed(
        record.lifecycle_state,
        SemanticLifecycleState.LINEAGE_ORIGIN,
        path=f"{path}.lifecycle_state",
        issues=issues,
        code=ManifestValidationCode.LIFECYCLE_STATE_MISMATCH,
    )
    _require_fixed(record.schema_version, SCHEMA_VERSION, path=f"{path}.schema_version", issues=issues)
    if isinstance(record.origin_kind, LineageOriginKind) and isinstance(record.direction, SemanticDirection):
        expected_direction = {
            LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION: SemanticDirection.INWARD,
            LineageOriginKind.AUTHORIZED_OUTWARD_EXPRESSION_PURPOSE: SemanticDirection.OUTWARD,
        }[record.origin_kind]
        if record.direction is not expected_direction:
            _issue(
                issues,
                f"{path}.direction",
                ManifestValidationCode.ORIGIN_DIRECTION_MISMATCH,
                f"{record.origin_kind.value} requires {expected_direction.value}",
            )


def _validate_candidate(
    record: CandidateMeaningRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.CANDIDATE_MEANING,
        expected_state=SemanticLifecycleState.CANDIDATE_MEANING,
        issues=issues,
    )
    _require_text(record.source_expression_ref, path=f"{path}.source_expression_ref", issues=issues)
    _require_text(record.communicative_act, path=f"{path}.communicative_act", issues=issues)
    for name in (
        "concept_refs",
        "relation_refs",
        "meaning_modifiers",
        "ambiguity_reasons",
        "unresolved_referents",
        "authority_sensitive_implications",
    ):
        _require_tuple(getattr(record, name), str, path=f"{path}.{name}", issues=issues, text_items=True)
    _require_tuple(
        record.preservation_classes,
        SemanticPreservationClass,
        path=f"{path}.preservation_classes",
        issues=issues,
    )


def _validate_non_selection(
    record: NonSelectionOutcomeRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    expected_state = None
    if isinstance(record.outcome_kind, NonSelectionOutcomeKind):
        expected_state = SemanticLifecycleState(record.outcome_kind.value)
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.NON_SELECTION_OUTCOME,
        expected_state=expected_state,
        issues=issues,
    )
    _require_enum(record.outcome_kind, NonSelectionOutcomeKind, path=f"{path}.outcome_kind", issues=issues)
    _require_tuple(record.candidate_refs, str, path=f"{path}.candidate_refs", issues=issues, text_items=True)
    reasons = _require_tuple(record.reasons, str, path=f"{path}.reasons", issues=issues, text_items=True)
    _require_tuple(
        record.required_clarifications,
        str,
        path=f"{path}.required_clarifications",
        issues=issues,
        text_items=True,
    )
    _require_tuple(
        record.external_authority_refs,
        str,
        path=f"{path}.external_authority_refs",
        issues=issues,
        text_items=True,
    )
    if not reasons:
        _issue(
            issues,
            f"{path}.reasons",
            ManifestValidationCode.REQUIRED_VALUE_MISSING,
            "non-selection requires at least one explicit reason",
        )
    if (
        record.outcome_kind is NonSelectionOutcomeKind.CLARIFICATION_REQUIRED
        and not record.required_clarifications
    ):
        _issue(
            issues,
            f"{path}.required_clarifications",
            ManifestValidationCode.REQUIRED_VALUE_MISSING,
            "clarification-required outcome requires clarification text",
        )


def _validate_selected(
    record: SelectedGovernedMeaningRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.SELECTED_GOVERNED_MEANING,
        expected_state=SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        issues=issues,
    )
    for name in ("selected_candidate_ref", "selection_authority_ref", "communicative_act"):
        _require_text(getattr(record, name), path=f"{path}.{name}", issues=issues)
    for name in (
        "concept_refs",
        "relation_refs",
        "meaning_modifiers",
        "inherited_limitations",
        "authority_sensitive_distinctions",
    ):
        _require_tuple(getattr(record, name), str, path=f"{path}.{name}", issues=issues, text_items=True)
    _require_tuple(
        record.preservation_classes,
        SemanticPreservationClass,
        path=f"{path}.preservation_classes",
        issues=issues,
    )


def _validate_governed_result(
    record: GovernedResultReferenceRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.GOVERNED_RESULT_REFERENCE,
        expected_state=SemanticLifecycleState.GOVERNED_RESULT_REFERENCED,
        issues=issues,
    )
    for name in ("selected_meaning_ref", "external_authority_ref", "semantic_relevance"):
        _require_text(getattr(record, name), path=f"{path}.{name}", issues=issues)


def _validate_outward(
    record: GovernedOutwardMeaningRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.GOVERNED_OUTWARD_MEANING,
        expected_state=SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        issues=issues,
    )
    bases = _require_tuple(
        record.outward_basis_refs,
        str,
        path=f"{path}.outward_basis_refs",
        issues=issues,
        text_items=True,
    )
    if not bases:
        _issue(
            issues,
            f"{path}.outward_basis_refs",
            ManifestValidationCode.REQUIRED_VALUE_MISSING,
            "governed outward meaning requires at least one outward basis",
        )
    _require_optional_text(
        record.prior_selected_meaning_ref,
        path=f"{path}.prior_selected_meaning_ref",
        issues=issues,
    )
    for name in (
        "permitted_claims",
        "required_qualifications",
        "prohibited_enlargements",
        "external_dependency_refs",
    ):
        _require_tuple(getattr(record, name), str, path=f"{path}.{name}", issues=issues, text_items=True)
    _require_tuple(
        record.preservation_classes,
        SemanticPreservationClass,
        path=f"{path}.preservation_classes",
        issues=issues,
    )


def _validate_expression(
    record: ExpressionLinkRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.EXPRESSION_LINK,
        expected_state=SemanticLifecycleState.EXPRESSION_LINKED,
        issues=issues,
    )
    _require_text(
        record.governed_outward_meaning_ref,
        path=f"{path}.governed_outward_meaning_ref",
        issues=issues,
    )
    _require_text(record.expression_candidate_ref, path=f"{path}.expression_candidate_ref", issues=issues)


def _validate_validation_link(
    record: ValidationLinkRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.VALIDATION_LINK,
        expected_state=SemanticLifecycleState.VALIDATION_LINKED,
        issues=issues,
    )
    for name in (
        "expression_link_ref",
        "external_validation_receipt_ref",
        "external_validation_disposition",
    ):
        _require_text(getattr(record, name), path=f"{path}.{name}", issues=issues)


def _validate_delivery(
    record: DeliveryContainmentLinkRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    expected_state = None
    if isinstance(record.disposition, DeliveryContainmentKind):
        expected_state = SemanticLifecycleState(record.disposition.value)
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.DELIVERY_OR_CONTAINMENT_LINK,
        expected_state=expected_state,
        issues=issues,
    )
    _require_text(record.prior_link_ref, path=f"{path}.prior_link_ref", issues=issues)
    _require_enum(record.disposition, DeliveryContainmentKind, path=f"{path}.disposition", issues=issues)
    _require_text(record.external_receipt_ref, path=f"{path}.external_receipt_ref", issues=issues)


def _validate_external_authority(
    record: ExternalAuthorityReferenceRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.EXTERNAL_AUTHORITY_REFERENCE,
        expected_state=None,
        issues=issues,
    )
    _require_enum(record.authority_kind, ExternalAuthorityKind, path=f"{path}.authority_kind", issues=issues)
    _require_text(record.external_object_ref, path=f"{path}.external_object_ref", issues=issues)
    _require_text(record.semantic_relevance, path=f"{path}.semantic_relevance", issues=issues)


def _validate_trace(
    record: SemanticTransitionTraceRecord,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    _validate_common_record_identity(
        record,
        path=path,
        expected_kind=SemanticRecordKind.SEMANTIC_TRANSITION_TRACE,
        expected_state=None,
        issues=issues,
    )
    for name in ("from_record_ref", "to_record_ref", "reason"):
        _require_text(getattr(record, name), path=f"{path}.{name}", issues=issues)
    _require_enum(record.from_state, SemanticLifecycleState, path=f"{path}.from_state", issues=issues)
    _require_enum(record.to_state, SemanticLifecycleState, path=f"{path}.to_state", issues=issues)
    _require_enum(record.transition_kind, SemanticTransitionKind, path=f"{path}.transition_kind", issues=issues)
    _require_optional_text(
        record.authority_reference_ref,
        path=f"{path}.authority_reference_ref",
        issues=issues,
    )


_RECORD_VALIDATORS: tuple[tuple[type[Any], Any], ...] = (
    (LineageRootRecord, _validate_lineage_root),
    (CandidateMeaningRecord, _validate_candidate),
    (NonSelectionOutcomeRecord, _validate_non_selection),
    (SelectedGovernedMeaningRecord, _validate_selected),
    (GovernedResultReferenceRecord, _validate_governed_result),
    (GovernedOutwardMeaningRecord, _validate_outward),
    (ExpressionLinkRecord, _validate_expression),
    (ValidationLinkRecord, _validate_validation_link),
    (DeliveryContainmentLinkRecord, _validate_delivery),
    (ExternalAuthorityReferenceRecord, _validate_external_authority),
    (SemanticTransitionTraceRecord, _validate_trace),
)


def _validate_record_into(
    record: Any,
    *,
    path: str,
    issues: list[ManifestValidationIssue],
) -> None:
    for expected_type, validator in _RECORD_VALIDATORS:
        if isinstance(record, expected_type):
            validator(record, path=path, issues=issues)
            return
    _issue(
        issues,
        path,
        ManifestValidationCode.TYPE_MISMATCH,
        "unsupported MSM-v1 record type",
    )


def validate_record(record: Any) -> ManifestValidationReport:
    """Validate one MSM-v1 record intrinsically, without manifest references."""

    issues: list[ManifestValidationIssue] = []
    _validate_record_into(record, path="record", issues=issues)
    return ManifestValidationReport(schema_version=SCHEMA_VERSION, issues=tuple(issues))


def _iter_manifest_collections(manifest: MeaningStructureManifestV1) -> tuple[tuple[str, tuple[Any, ...], type[Any]], ...]:
    return (
        ("candidate_meanings", manifest.candidate_meanings, CandidateMeaningRecord),
        ("non_selection_outcomes", manifest.non_selection_outcomes, NonSelectionOutcomeRecord),
        ("selected_governed_meanings", manifest.selected_governed_meanings, SelectedGovernedMeaningRecord),
        ("governed_result_references", manifest.governed_result_references, GovernedResultReferenceRecord),
        ("governed_outward_meanings", manifest.governed_outward_meanings, GovernedOutwardMeaningRecord),
        ("expression_links", manifest.expression_links, ExpressionLinkRecord),
        ("validation_links", manifest.validation_links, ValidationLinkRecord),
        ("delivery_or_containment_links", manifest.delivery_or_containment_links, DeliveryContainmentLinkRecord),
        ("external_authority_references", manifest.external_authority_references, ExternalAuthorityReferenceRecord),
        ("semantic_transition_traces", manifest.semantic_transition_traces, SemanticTransitionTraceRecord),
    )


def _resolve_reference(
    reference: str,
    *,
    path: str,
    index: dict[str, Any],
    allowed_types: tuple[type[Any], ...],
    issues: list[ManifestValidationIssue],
) -> Any | None:
    if not isinstance(reference, str):
        return None
    target = index.get(reference)
    if target is None:
        _issue(
            issues,
            path,
            ManifestValidationCode.UNRESOLVED_REFERENCE,
            f"no record found for {reference!r}",
        )
        return None
    if not isinstance(target, allowed_types):
        names = ", ".join(item.__name__ for item in allowed_types)
        _issue(
            issues,
            path,
            ManifestValidationCode.REFERENCE_KIND_MISMATCH,
            f"expected one of: {names}",
        )
        return None
    return target


def _state_for_record(record: Any) -> SemanticLifecycleState | None:
    state = getattr(record, "lifecycle_state", None)
    return state if isinstance(state, SemanticLifecycleState) else None


def validate_manifest(manifest: Any) -> ManifestValidationReport:
    """Validate one complete immutable MSM-v1 manifest without changing it."""

    issues: list[ManifestValidationIssue] = []
    if not isinstance(manifest, MeaningStructureManifestV1):
        _issue(
            issues,
            "manifest",
            ManifestValidationCode.TYPE_MISMATCH,
            "expected MeaningStructureManifestV1",
        )
        return ManifestValidationReport(schema_version=SCHEMA_VERSION, issues=tuple(issues))

    _require_local_identifier(manifest.manifest_id, path="manifest.manifest_id", issues=issues)
    _require_fixed(
        manifest.record_kind,
        SemanticRecordKind.MEANING_STRUCTURE_MANIFEST,
        path="manifest.record_kind",
        issues=issues,
        code=ManifestValidationCode.RECORD_KIND_MISMATCH,
    )
    _require_fixed(manifest.package_id, PACKAGE_ID, path="manifest.package_id", issues=issues)
    _require_fixed(manifest.schema_id, SCHEMA_ID, path="manifest.schema_id", issues=issues)
    _require_fixed(manifest.schema_version, SCHEMA_VERSION, path="manifest.schema_version", issues=issues)

    if not isinstance(manifest.lineage_root, LineageRootRecord):
        _issue(
            issues,
            "manifest.lineage_root",
            ManifestValidationCode.TYPE_MISMATCH,
            "expected LineageRootRecord",
        )
        lineage_id: str | None = None
    else:
        _validate_lineage_root(manifest.lineage_root, path="manifest.lineage_root", issues=issues)
        lineage_id = manifest.lineage_root.lineage_id

    index: dict[str, Any] = {}
    seen_paths: dict[str, str] = {}

    if lineage_id is not None:
        index[lineage_id] = manifest.lineage_root
        seen_paths[lineage_id] = "manifest.lineage_root.lineage_id"

    for collection_name, collection, expected_type in _iter_manifest_collections(manifest):
        collection_path = f"manifest.{collection_name}"
        if not isinstance(collection, tuple):
            _issue(
                issues,
                collection_path,
                ManifestValidationCode.INVALID_TUPLE,
                "expected tuple",
            )
            continue
        for item_index, record in enumerate(collection):
            path = f"{collection_path}[{item_index}]"
            if not isinstance(record, expected_type):
                _issue(
                    issues,
                    path,
                    ManifestValidationCode.TYPE_MISMATCH,
                    f"expected {expected_type.__name__}",
                )
                continue
            _validate_record_into(record, path=path, issues=issues)
            if lineage_id is not None and record.lineage_id != lineage_id:
                _issue(
                    issues,
                    f"{path}.lineage_id",
                    ManifestValidationCode.LINEAGE_MISMATCH,
                    f"expected {lineage_id!r}",
                )
            record_id = record.record_id
            if isinstance(record_id, str):
                if record_id in seen_paths:
                    _issue(
                        issues,
                        f"{path}.record_id",
                        ManifestValidationCode.DUPLICATE_RECORD_ID,
                        f"already used at {seen_paths[record_id]}",
                    )
                else:
                    index[record_id] = record
                    seen_paths[record_id] = f"{path}.record_id"

    for special_name, special_value in (
        ("manifest.manifest_id", manifest.manifest_id),
        ("manifest.lineage_root.lineage_id", lineage_id),
    ):
        if isinstance(special_value, str):
            collisions = [
                path for value, path in seen_paths.items()
                if value == special_value and path != special_name
            ]
            if collisions:
                _issue(
                    issues,
                    special_name,
                    ManifestValidationCode.IDENTIFIER_COLLISION,
                    f"identifier also used at {collisions[0]}",
                )

    if isinstance(manifest.lineage_root, LineageRootRecord):
        for index_value, candidate in enumerate(manifest.candidate_meanings if isinstance(manifest.candidate_meanings, tuple) else ()):
            if isinstance(candidate, CandidateMeaningRecord) and manifest.lineage_root.origin_kind is LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION:
                if candidate.source_expression_ref != manifest.lineage_root.origin_ref:
                    _issue(
                        issues,
                        f"manifest.candidate_meanings[{index_value}].source_expression_ref",
                        ManifestValidationCode.UNRESOLVED_REFERENCE,
                        "candidate source must match the inward lineage origin reference",
                    )

    for index_value, outcome in enumerate(manifest.non_selection_outcomes if isinstance(manifest.non_selection_outcomes, tuple) else ()):
        if not isinstance(outcome, NonSelectionOutcomeRecord):
            continue
        for ref_index, reference in enumerate(outcome.candidate_refs):
            _resolve_reference(
                reference,
                path=f"manifest.non_selection_outcomes[{index_value}].candidate_refs[{ref_index}]",
                index=index,
                allowed_types=(CandidateMeaningRecord,),
                issues=issues,
            )
        for ref_index, reference in enumerate(outcome.external_authority_refs):
            _resolve_reference(
                reference,
                path=f"manifest.non_selection_outcomes[{index_value}].external_authority_refs[{ref_index}]",
                index=index,
                allowed_types=(ExternalAuthorityReferenceRecord,),
                issues=issues,
            )

    for index_value, selected in enumerate(manifest.selected_governed_meanings if isinstance(manifest.selected_governed_meanings, tuple) else ()):
        if not isinstance(selected, SelectedGovernedMeaningRecord):
            continue
        _resolve_reference(
            selected.selected_candidate_ref,
            path=f"manifest.selected_governed_meanings[{index_value}].selected_candidate_ref",
            index=index,
            allowed_types=(CandidateMeaningRecord,),
            issues=issues,
        )

    for index_value, result in enumerate(manifest.governed_result_references if isinstance(manifest.governed_result_references, tuple) else ()):
        if not isinstance(result, GovernedResultReferenceRecord):
            continue
        _resolve_reference(
            result.selected_meaning_ref,
            path=f"manifest.governed_result_references[{index_value}].selected_meaning_ref",
            index=index,
            allowed_types=(SelectedGovernedMeaningRecord,),
            issues=issues,
        )
        _resolve_reference(
            result.external_authority_ref,
            path=f"manifest.governed_result_references[{index_value}].external_authority_ref",
            index=index,
            allowed_types=(ExternalAuthorityReferenceRecord,),
            issues=issues,
        )

    outward_basis_types = (
        GovernedResultReferenceRecord,
        NonSelectionOutcomeRecord,
        SelectedGovernedMeaningRecord,
        ExternalAuthorityReferenceRecord,
    )
    for index_value, outward in enumerate(manifest.governed_outward_meanings if isinstance(manifest.governed_outward_meanings, tuple) else ()):
        if not isinstance(outward, GovernedOutwardMeaningRecord):
            continue
        for ref_index, reference in enumerate(outward.outward_basis_refs):
            _resolve_reference(
                reference,
                path=f"manifest.governed_outward_meanings[{index_value}].outward_basis_refs[{ref_index}]",
                index=index,
                allowed_types=outward_basis_types,
                issues=issues,
            )
        if outward.prior_selected_meaning_ref is not None:
            _resolve_reference(
                outward.prior_selected_meaning_ref,
                path=f"manifest.governed_outward_meanings[{index_value}].prior_selected_meaning_ref",
                index=index,
                allowed_types=(SelectedGovernedMeaningRecord,),
                issues=issues,
            )
        for ref_index, reference in enumerate(outward.external_dependency_refs):
            _resolve_reference(
                reference,
                path=f"manifest.governed_outward_meanings[{index_value}].external_dependency_refs[{ref_index}]",
                index=index,
                allowed_types=(ExternalAuthorityReferenceRecord,),
                issues=issues,
            )

    for index_value, expression in enumerate(manifest.expression_links if isinstance(manifest.expression_links, tuple) else ()):
        if not isinstance(expression, ExpressionLinkRecord):
            continue
        _resolve_reference(
            expression.governed_outward_meaning_ref,
            path=f"manifest.expression_links[{index_value}].governed_outward_meaning_ref",
            index=index,
            allowed_types=(GovernedOutwardMeaningRecord,),
            issues=issues,
        )

    for index_value, validation in enumerate(manifest.validation_links if isinstance(manifest.validation_links, tuple) else ()):
        if not isinstance(validation, ValidationLinkRecord):
            continue
        _resolve_reference(
            validation.expression_link_ref,
            path=f"manifest.validation_links[{index_value}].expression_link_ref",
            index=index,
            allowed_types=(ExpressionLinkRecord,),
            issues=issues,
        )

    for index_value, delivery in enumerate(manifest.delivery_or_containment_links if isinstance(manifest.delivery_or_containment_links, tuple) else ()):
        if not isinstance(delivery, DeliveryContainmentLinkRecord):
            continue
        _resolve_reference(
            delivery.prior_link_ref,
            path=f"manifest.delivery_or_containment_links[{index_value}].prior_link_ref",
            index=index,
            allowed_types=(ExpressionLinkRecord, ValidationLinkRecord),
            issues=issues,
        )

    for index_value, trace in enumerate(manifest.semantic_transition_traces if isinstance(manifest.semantic_transition_traces, tuple) else ()):
        if not isinstance(trace, SemanticTransitionTraceRecord):
            continue
        from_record = _resolve_reference(
            trace.from_record_ref,
            path=f"manifest.semantic_transition_traces[{index_value}].from_record_ref",
            index=index,
            allowed_types=tuple(item[0] for item in _RECORD_VALIDATORS),
            issues=issues,
        )
        to_record = _resolve_reference(
            trace.to_record_ref,
            path=f"manifest.semantic_transition_traces[{index_value}].to_record_ref",
            index=index,
            allowed_types=tuple(item[0] for item in _RECORD_VALIDATORS),
            issues=issues,
        )
        from_state = _state_for_record(from_record)
        to_state = _state_for_record(to_record)
        if from_state is not None and trace.from_state is not from_state:
            _issue(
                issues,
                f"manifest.semantic_transition_traces[{index_value}].from_state",
                ManifestValidationCode.LIFECYCLE_STATE_MISMATCH,
                f"referenced record state is {from_state.value}",
            )
        if to_state is not None and trace.to_state is not to_state:
            _issue(
                issues,
                f"manifest.semantic_transition_traces[{index_value}].to_state",
                ManifestValidationCode.LIFECYCLE_STATE_MISMATCH,
                f"referenced record state is {to_state.value}",
            )

    return ManifestValidationReport(schema_version=SCHEMA_VERSION, issues=tuple(issues))


def assert_valid_manifest(manifest: Any) -> None:
    """Raise a bounded validation error when the manifest is not conforming."""

    report = validate_manifest(manifest)
    if not report.ok:
        raise MeaningStructureManifestValidationError(report)


__all__ = (
    "ManifestValidationCode",
    "ManifestValidationIssue",
    "ManifestValidationReport",
    "MeaningStructureManifestValidationError",
    "assert_valid_manifest",
    "validate_manifest",
    "validate_record",
)
