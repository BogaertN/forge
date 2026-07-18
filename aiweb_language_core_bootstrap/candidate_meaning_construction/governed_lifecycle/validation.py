"""Pure fail-closed Slice 39B candidate-meaning validation."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
import re
from typing import Any, Iterable

from ..identity import (
    ALTERNATIVE_REFERENCE_SCHEMA_ID,
    CONSTRUCTION_RECEIPT_SCHEMA_ID,
    CONTENT_SCHEMA_ID,
    IDENTITY_SCHEMA_ID,
    PROVENANCE_SCHEMA_ID,
    SCHEMA_VERSION,
    STATE_SCHEMA_ID,
)
from ..schema import (
    CandidateMeaningAlternativeReference,
    CandidateMeaningConstructionReceipt,
    CandidateMeaningConstructionStatus,
    CandidateMeaningContent,
    CandidateMeaningIdentity,
    CandidateMeaningProvenance,
    CandidateMeaningState,
)
from .canonical import (
    CANONICAL_FIELD_ORDERS,
    CandidateMeaningCanonicalizationError,
    canonical_field_order,
    canonicalize_field_pairs,
)
from .identity import (
    expected_alternative_reference_id,
    expected_bundle_digest,
    expected_bundle_id,
    expected_candidate_key,
    expected_candidate_lineage_id,
    expected_candidate_meaning_id,
    expected_construction_receipt_id,
    expected_content_id,
    expected_lifecycle_record_id,
    expected_lifecycle_transition_id,
    expected_provenance_id,
    expected_state_id,
    expected_version_custody_id,
)
from .rules import lifecycle_transition_allowed
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    DIGEST_ALGORITHM,
    SLICE39B_SCHEMA_VERSION,
    CandidateMeaningGovernanceBundle,
    CandidateMeaningLifecycleRecord,
    CandidateMeaningLifecycleStage,
    CandidateMeaningLifecycleTransitionKind,
    CandidateMeaningLifecycleTransitionRecord,
    CandidateMeaningValidationCode,
    CandidateMeaningValidationError,
    CandidateMeaningValidationIssue,
    CandidateMeaningValidationReport,
    CandidateMeaningVersionCustody,
)


_IDENTIFIER_RE = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:/-]*\Z"
)
_VERSION_RE = re.compile(
    r"v(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){0,2}\Z"
)
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
_IDENTITY_SUFFIXES = ("_id", "_ref")
_TUPLE_REFERENCE_SUFFIXES = ("_ids", "_refs")
_REQUIRED_ANCESTRY_FIELDS = (
    "source_span_ids",
    "structural_candidate_ids",
    "structural_ancestry_ids",
    "constrained_trail_ids",
    "phase_trail_ids",
    "operator_graph_ids",
    "operator_node_ids",
    "operator_definition_ids",
    "operator_keys_and_versions",
    "scope_occurrence_ids",
    "predecessor_receipt_ids",
)
_FALSE_BOUNDARY_FIELDS = (
    "accepted_meaning_created",
    "selected_meaning_created",
    "gate_outcome_created",
    "evidence_validity_determined",
    "truth_determined",
    "permission_inferred",
    "capability_availability_created",
    "route_created",
    "invocation_proposed",
    "tool_invoked",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
)
_LIFECYCLE_FALSE_FIELDS = (
    "automatic_progression",
    "gate_progression_created",
    "selected_meaning_created",
    "ambiguity_disposition_created",
    "clarification_required_created",
    "refusal_created",
    "blocked_progression_created",
    "truth_determined",
    "evidence_validated",
    "permission_granted",
    "route_created",
    "invocation_created",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
)
_TRANSITION_FALSE_FIELDS = (
    "automatic_transition",
    "gate_progression_created",
    "selected_meaning_created",
    "ambiguity_disposition_created",
    "clarification_required_created",
    "refusal_created",
    "blocked_progression_created",
    "permission_granted",
    "route_created",
    "invocation_created",
    "action_performed",
    "memory_accessed",
    "rendered",
    "delivered",
)
_BUNDLE_FALSE_FIELDS = (
    "runtime_constructor_installed",
    "candidate_ranking_installed",
    "gate_engine_installed",
    "selected_meaning_installed",
    "route_installed",
    "invocation_installed",
    "action_installed",
    "memory_installed",
    "rendering_installed",
    "delivery_installed",
)


def _issue(
    issues: list[CandidateMeaningValidationIssue],
    path: str,
    code: CandidateMeaningValidationCode,
    detail: str,
) -> None:
    issues.append(
        CandidateMeaningValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def _report(
    issues: list[CandidateMeaningValidationIssue],
) -> CandidateMeaningValidationReport:
    return CandidateMeaningValidationReport(issues=tuple(issues))


def _require_exact_type(
    value: Any,
    expected_type: type[Any],
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
) -> bool:
    if type(value) is not expected_type:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.TYPE_MISMATCH,
            f"expected exact {expected_type.__name__}",
        )
        return False
    return True


def _require_text(
    value: Any,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
) -> bool:
    if type(value) is not str:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.TYPE_MISMATCH,
            "expected str",
        )
        return False
    if not value or not value.strip():
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.REQUIRED_VALUE_MISSING,
            "text must be non-empty",
        )
        return False
    if value != value.strip() or _CONTROL_RE.search(value):
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.INVALID_TEXT,
            "text must be trimmed and contain no control characters",
        )
        return False
    return True


def _require_identifier(
    value: Any,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
) -> bool:
    if not _require_text(value, path=path, issues=issues):
        return False
    if _IDENTIFIER_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.INVALID_IDENTIFIER,
            "identifier contains unsupported characters",
        )
        return False
    return True


def _require_version(
    value: Any,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
) -> bool:
    if not _require_text(value, path=path, issues=issues):
        return False
    if _VERSION_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.INVALID_VERSION,
            "expected canonical vN, vN.N, or vN.N.N",
        )
        return False
    return True


def _require_sha256(
    value: Any,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
) -> bool:
    if type(value) is not str or _SHA256_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.INVALID_SHA256,
            "expected 64 lower-case hexadecimal characters",
        )
        return False
    return True


def _require_bool(
    value: Any,
    expected: bool,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
    code: CandidateMeaningValidationCode = (
        CandidateMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
    ),
) -> bool:
    if type(value) is not bool:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.TYPE_MISMATCH,
            "expected exact bool",
        )
        return False
    if value is not expected:
        _issue(issues, path, code, f"expected {expected!r}")
        return False
    return True


def _require_enum(
    value: Any,
    expected_type: type[Enum],
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
) -> bool:
    if not isinstance(value, expected_type):
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.INVALID_ENUM,
            f"expected {expected_type.__name__}",
        )
        return False
    return True


def _require_tuple(
    value: Any,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
    item_kind: str = "text",
    nonempty: bool = False,
) -> tuple[Any, ...]:
    if type(value) is not tuple:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.INVALID_TUPLE,
            "expected tuple",
        )
        return ()
    if nonempty and not value:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.ANCESTRY_REQUIRED,
            "required ancestry tuple must be non-empty",
        )
    normalized: list[Any] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if item_kind == "identifier":
            if _require_identifier(item, path=item_path, issues=issues):
                normalized.append(item)
        elif item_kind == "version_pair":
            if type(item) is not tuple or len(item) != 2:
                _issue(
                    issues,
                    item_path,
                    CandidateMeaningValidationCode.TYPE_MISMATCH,
                    "expected (identifier, version) tuple",
                )
                continue
            ok_id = _require_identifier(
                item[0], path=f"{item_path}[0]", issues=issues
            )
            ok_ver = _require_version(
                item[1], path=f"{item_path}[1]", issues=issues
            )
            if ok_id and ok_ver:
                normalized.append(item)
        else:
            if _require_text(item, path=item_path, issues=issues):
                normalized.append(item)
    try:
        duplicate = len(value) != len(set(value))
    except TypeError:
        duplicate = True
    if duplicate:
        _issue(
            issues,
            path,
            CandidateMeaningValidationCode.DUPLICATE_TUPLE_VALUE,
            "tuple values must be unique and hashable",
        )
    return tuple(normalized)


def _require_fixed(
    value: Any,
    expected: Any,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
    code: CandidateMeaningValidationCode = (
        CandidateMeaningValidationCode.IDENTITY_MISMATCH
    ),
) -> bool:
    if type(value) is not type(expected) or value != expected:
        _issue(issues, path, code, f"expected {expected!r}")
        return False
    return True


def validate_field_pairs(
    record_type: type[Any],
    field_pairs: Iterable[tuple[str, Any]],
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    expected = CANONICAL_FIELD_ORDERS.get(record_type)
    if expected is None:
        _issue(
            issues,
            "record_type",
            CandidateMeaningValidationCode.TYPE_MISMATCH,
            "unsupported record type",
        )
        return _report(issues)

    observed: set[str] = set()
    for index, pair in enumerate(field_pairs):
        path = f"field_pairs[{index}]"
        if type(pair) is not tuple or len(pair) != 2 or type(pair[0]) is not str:
            _issue(
                issues,
                path,
                CandidateMeaningValidationCode.TYPE_MISMATCH,
                "expected (str, value) tuple",
            )
            continue
        name = pair[0]
        if name in observed:
            _issue(
                issues,
                path,
                CandidateMeaningValidationCode.DUPLICATE_FIELD,
                f"duplicate field {name}",
            )
        elif name not in expected:
            _issue(
                issues,
                path,
                CandidateMeaningValidationCode.UNKNOWN_FIELD,
                f"unknown field {name}",
            )
        observed.add(name)

    for name in expected:
        if name not in observed:
            _issue(
                issues,
                f"field_pairs.{name}",
                CandidateMeaningValidationCode.MISSING_FIELD,
                "required field absent",
            )

    if not issues:
        try:
            ordered = canonicalize_field_pairs(record_type, field_pairs)
        except CandidateMeaningCanonicalizationError as error:
            _issue(
                issues,
                "field_pairs",
                CandidateMeaningValidationCode.FIELD_ORDER_MISMATCH,
                str(error),
            )
        else:
            if tuple(ordered) != canonical_field_order(record_type):
                _issue(
                    issues,
                    "field_pairs",
                    CandidateMeaningValidationCode.FIELD_ORDER_MISMATCH,
                    "canonical ordering mismatch",
                )
    return _report(issues)


def _validate_identifier_fields(
    record: Any,
    *,
    path: str,
    issues: list[CandidateMeaningValidationIssue],
) -> None:
    try:
        record_fields = fields(record)
    except TypeError:
        return
    for item in record_fields:
        name = item.name
        value = getattr(record, name, None)
        field_path = f"{path}.{name}"
        if name.endswith(_IDENTITY_SUFFIXES):
            _require_identifier(value, path=field_path, issues=issues)
        elif name.endswith(_TUPLE_REFERENCE_SUFFIXES):
            _require_tuple(
                value,
                path=field_path,
                issues=issues,
                item_kind="identifier",
            )


def validate_identity_record(
    record: Any,
    *,
    content: Any,
    provenance: Any,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningIdentity,
        path="identity",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(record, path="identity", issues=issues)
    _require_version(
        record.candidate_version,
        path="identity.candidate_version",
        issues=issues,
    )
    _require_version(
        record.construction_profile_version,
        path="identity.construction_profile_version",
        issues=issues,
    )
    _require_fixed(
        record.schema_version,
        SCHEMA_VERSION,
        path="identity.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    _require_fixed(
        record.identity_schema_id,
        IDENTITY_SCHEMA_ID,
        path="identity.identity_schema_id",
        issues=issues,
    )
    if type(content) is CandidateMeaningContent and type(provenance) is CandidateMeaningProvenance:
        expected_id = expected_candidate_meaning_id(content, provenance)
        _require_fixed(
            record.candidate_meaning_id,
            expected_id,
            path="identity.candidate_meaning_id",
            issues=issues,
        )
        _require_fixed(
            record.candidate_key,
            expected_candidate_key(expected_id),
            path="identity.candidate_key",
            issues=issues,
        )
        _require_fixed(
            record.lineage_id,
            expected_candidate_lineage_id(provenance),
            path="identity.lineage_id",
            issues=issues,
        )
    return _report(issues)


def validate_content_record(
    record: Any,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningContent,
        path="content",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(record, path="content", issues=issues)
    if record.communicative_act_candidate is not None:
        _require_identifier(
            record.communicative_act_candidate,
            path="content.communicative_act_candidate",
            issues=issues,
        )
    for item in fields(record):
        value = getattr(record, item.name)
        if type(value) is tuple and not item.name.endswith("_versions"):
            _require_tuple(
                value,
                path=f"content.{item.name}",
                issues=issues,
                item_kind="identifier",
            )
    _require_bool(
        record.candidate_only, True, path="content.candidate_only", issues=issues
    )
    for name in (
        "selected_content",
        "evidence_validity_determined",
        "truth_determined",
        "permission_inferred",
    ):
        _require_bool(
            getattr(record, name),
            False,
            path=f"content.{name}",
            issues=issues,
        )
    _require_fixed(
        record.schema_version,
        SCHEMA_VERSION,
        path="content.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    _require_fixed(
        record.content_schema_id,
        CONTENT_SCHEMA_ID,
        path="content.content_schema_id",
        issues=issues,
    )
    try:
        expected = expected_content_id(record)
    except Exception as error:
        _issue(
            issues,
            "content",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.content_id,
            expected,
            path="content.content_id",
            issues=issues,
        )
    return _report(issues)


def validate_provenance_record(
    record: Any,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningProvenance,
        path="provenance",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(record, path="provenance", issues=issues)
    _require_sha256(
        record.source_sha256,
        path="provenance.source_sha256",
        issues=issues,
    )
    for item in fields(record):
        name = item.name
        value = getattr(record, name)
        if name == "operator_keys_and_versions":
            _require_tuple(
                value,
                path=f"provenance.{name}",
                issues=issues,
                item_kind="version_pair",
                nonempty=True,
            )
        elif name in ("concept_ids_and_versions", "sense_ids_and_versions"):
            _require_tuple(
                value,
                path=f"provenance.{name}",
                issues=issues,
                item_kind="version_pair",
            )
        elif type(value) is tuple:
            _require_tuple(
                value,
                path=f"provenance.{name}",
                issues=issues,
                item_kind="identifier",
                nonempty=name in _REQUIRED_ANCESTRY_FIELDS,
            )
    for name in (
        "source_ancestry_preserved",
        "operator_ancestry_preserved",
        "phase_trail_ancestry_preserved",
        "scope_attachment_ancestry_preserved",
        "registry_snapshots_preserved",
        "candidate_only",
    ):
        _require_bool(
            getattr(record, name),
            True,
            path=f"provenance.{name}",
            issues=issues,
        )
    _require_bool(
        record.selected_ancestry,
        False,
        path="provenance.selected_ancestry",
        issues=issues,
    )
    _require_bool(
        record.external_resource_loaded,
        False,
        path="provenance.external_resource_loaded",
        issues=issues,
    )
    _require_fixed(
        record.schema_version,
        SCHEMA_VERSION,
        path="provenance.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    _require_fixed(
        record.provenance_schema_id,
        PROVENANCE_SCHEMA_ID,
        path="provenance.provenance_schema_id",
        issues=issues,
    )
    try:
        expected = expected_provenance_id(record)
    except Exception as error:
        _issue(
            issues,
            "provenance",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.provenance_id,
            expected,
            path="provenance.provenance_id",
            issues=issues,
        )
    return _report(issues)


def validate_alternative_reference(
    record: Any,
    *,
    candidate_meaning_id: str | None = None,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningAlternativeReference,
        path="alternative_reference",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(
        record, path="alternative_reference", issues=issues
    )
    _require_identifier(
        record.alternative_kind,
        path="alternative_reference.alternative_kind",
        issues=issues,
    )
    for name in (
        "shared_ancestry_refs",
        "differing_content_refs",
        "unresolved_reason_refs",
    ):
        _require_tuple(
            getattr(record, name),
            path=f"alternative_reference.{name}",
            issues=issues,
            item_kind="identifier",
            nonempty=True,
        )
    _require_bool(
        record.candidate_only,
        True,
        path="alternative_reference.candidate_only",
        issues=issues,
    )
    for name in (
        "ranking_assigned",
        "preferred_candidate_assigned",
        "selected_alternative",
        "ambiguous_gate_disposition_created",
    ):
        _require_bool(
            getattr(record, name),
            False,
            path=f"alternative_reference.{name}",
            issues=issues,
        )
    _require_fixed(
        record.schema_version,
        SCHEMA_VERSION,
        path="alternative_reference.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    _require_fixed(
        record.alternative_reference_schema_id,
        ALTERNATIVE_REFERENCE_SCHEMA_ID,
        path="alternative_reference.alternative_reference_schema_id",
        issues=issues,
    )
    if candidate_meaning_id is not None:
        _require_fixed(
            record.source_candidate_meaning_id,
            candidate_meaning_id,
            path="alternative_reference.source_candidate_meaning_id",
            issues=issues,
            code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
        )
    if (
        type(record.source_candidate_meaning_id) is str
        and record.source_candidate_meaning_id
        == record.alternative_candidate_meaning_id
    ):
        _issue(
            issues,
            "alternative_reference.alternative_candidate_meaning_id",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "candidate cannot be its own alternative",
        )
    try:
        expected = expected_alternative_reference_id(record)
    except Exception as error:
        _issue(
            issues,
            "alternative_reference",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.alternative_reference_id,
            expected,
            path="alternative_reference.alternative_reference_id",
            issues=issues,
        )
    return _report(issues)


def validate_construction_receipt(
    record: Any,
    *,
    identity: Any | None = None,
    content: Any | None = None,
    provenance: Any | None = None,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningConstructionReceipt,
        path="construction_receipt",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(
        record, path="construction_receipt", issues=issues
    )
    _require_enum(
        record.status,
        CandidateMeaningConstructionStatus,
        path="construction_receipt.status",
        issues=issues,
    )
    _require_tuple(
        record.alternative_reference_ids,
        path="construction_receipt.alternative_reference_ids",
        issues=issues,
        item_kind="identifier",
    )
    _require_tuple(
        record.predecessor_record_ids,
        path="construction_receipt.predecessor_record_ids",
        issues=issues,
        item_kind="identifier",
        nonempty=True,
    )
    _require_tuple(
        record.status_reason_refs,
        path="construction_receipt.status_reason_refs",
        issues=issues,
        item_kind="identifier",
        nonempty=True,
    )
    _require_version(
        record.construction_profile_version,
        path="construction_receipt.construction_profile_version",
        issues=issues,
    )
    for name in (
        "deterministic_construction_required",
        "source_preservation_required",
        "immutable_record_set_required",
        "candidate_only",
    ):
        _require_bool(
            getattr(record, name),
            True,
            path=f"construction_receipt.{name}",
            issues=issues,
        )
    for name in _FALSE_BOUNDARY_FIELDS:
        _require_bool(
            getattr(record, name),
            False,
            path=f"construction_receipt.{name}",
            issues=issues,
        )
    _require_fixed(
        record.schema_version,
        SCHEMA_VERSION,
        path="construction_receipt.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    _require_fixed(
        record.construction_receipt_schema_id,
        CONSTRUCTION_RECEIPT_SCHEMA_ID,
        path="construction_receipt.construction_receipt_schema_id",
        issues=issues,
    )
    if type(identity) is CandidateMeaningIdentity:
        for name, value in (
            ("candidate_meaning_id", identity.candidate_meaning_id),
            ("identity_ref", identity.candidate_meaning_id),
            ("construction_profile_id", identity.construction_profile_id),
            (
                "construction_profile_version",
                identity.construction_profile_version,
            ),
        ):
            _require_fixed(
                getattr(record, name),
                value,
                path=f"construction_receipt.{name}",
                issues=issues,
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            )
    if type(content) is CandidateMeaningContent:
        _require_fixed(
            record.content_ref,
            content.content_id,
            path="construction_receipt.content_ref",
            issues=issues,
            code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
        )
    if type(provenance) is CandidateMeaningProvenance:
        _require_fixed(
            record.provenance_ref,
            provenance.provenance_id,
            path="construction_receipt.provenance_ref",
            issues=issues,
            code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
        )
    try:
        expected = expected_construction_receipt_id(record)
    except Exception as error:
        _issue(
            issues,
            "construction_receipt",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.receipt_id,
            expected,
            path="construction_receipt.receipt_id",
            issues=issues,
        )
    return _report(issues)


def validate_state_record(
    record: Any,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningState,
        path="state",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(record, path="state", issues=issues)
    if type(record.identity) is not CandidateMeaningIdentity:
        _issue(
            issues,
            "state.identity",
            CandidateMeaningValidationCode.TYPE_MISMATCH,
            "expected CandidateMeaningIdentity",
        )
    if type(record.content) is not CandidateMeaningContent:
        _issue(
            issues,
            "state.content",
            CandidateMeaningValidationCode.TYPE_MISMATCH,
            "expected CandidateMeaningContent",
        )
    if type(record.provenance) is not CandidateMeaningProvenance:
        _issue(
            issues,
            "state.provenance",
            CandidateMeaningValidationCode.TYPE_MISMATCH,
            "expected CandidateMeaningProvenance",
        )
    if type(record.alternative_references) is not tuple:
        _issue(
            issues,
            "state.alternative_references",
            CandidateMeaningValidationCode.INVALID_TUPLE,
            "expected tuple",
        )
    else:
        for index, item in enumerate(record.alternative_references):
            if type(item) is not CandidateMeaningAlternativeReference:
                _issue(
                    issues,
                    f"state.alternative_references[{index}]",
                    CandidateMeaningValidationCode.TYPE_MISMATCH,
                    "expected CandidateMeaningAlternativeReference",
                )
    _require_enum(
        record.construction_status,
        CandidateMeaningConstructionStatus,
        path="state.construction_status",
        issues=issues,
    )
    _require_tuple(
        record.status_reason_refs,
        path="state.status_reason_refs",
        issues=issues,
        item_kind="identifier",
        nonempty=True,
    )
    for name in (
        "unresolved_alternative_refs",
        "missing_role_refs",
        "conflicting_role_refs",
        "limitations",
        "permanent_boundaries",
    ):
        _require_tuple(
            getattr(record, name),
            path=f"state.{name}",
            issues=issues,
            item_kind="identifier",
            nonempty=name in ("limitations", "permanent_boundaries"),
        )
    for name in ("schema_only", "candidate_only"):
        _require_bool(
            getattr(record, name),
            True,
            path=f"state.{name}",
            issues=issues,
        )
    for name in (
        "runtime_constructor_installed",
        "accepted_meaning",
        "selected_meaning",
        "selected_sense",
        "selected_predicate",
        "selected_frame",
        "participant_assignment",
        "resolved_referent",
        "ambiguous_gate_disposition",
        "clarification_required",
        "refusal",
        "blocked_progression",
        "rejection",
        "evidence_validity",
        "truth",
        "verified_status",
        "permission",
        "capability_availability",
        "route",
        "invocation",
        "action",
        "memory_access",
        "rendering",
        "delivery",
        "external_resource_loading",
        "language_model_authority",
        "embedding_authority",
        "semantic_similarity_authority",
    ):
        _require_bool(
            getattr(record, name),
            False,
            path=f"state.{name}",
            issues=issues,
        )
    _require_fixed(
        record.schema_version,
        SCHEMA_VERSION,
        path="state.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    _require_fixed(
        record.state_schema_id,
        STATE_SCHEMA_ID,
        path="state.state_schema_id",
        issues=issues,
    )
    try:
        expected = expected_state_id(record)
    except Exception as error:
        _issue(
            issues,
            "state",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.state_id,
            expected,
            path="state.state_id",
            issues=issues,
        )
    return _report(issues)


def validate_version_custody(
    record: Any,
    *,
    identity: Any | None = None,
    provenance: Any | None = None,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningVersionCustody,
        path="version_custody",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(record, path="version_custody", issues=issues)
    for name in (
        "candidate_version",
        "construction_profile_version",
        "slice37_registry_snapshot_version",
        "slice38_registry_snapshot_version",
        "compatibility_registry_snapshot_version",
    ):
        _require_version(
            getattr(record, name),
            path=f"version_custody.{name}",
            issues=issues,
        )
    for name, expected in (
        ("schema_version", SCHEMA_VERSION),
        ("identity_schema_id", IDENTITY_SCHEMA_ID),
        ("content_schema_id", CONTENT_SCHEMA_ID),
        ("provenance_schema_id", PROVENANCE_SCHEMA_ID),
        (
            "alternative_reference_schema_id",
            ALTERNATIVE_REFERENCE_SCHEMA_ID,
        ),
        (
            "construction_receipt_schema_id",
            CONSTRUCTION_RECEIPT_SCHEMA_ID,
        ),
        ("state_schema_id", STATE_SCHEMA_ID),
        (
            "canonical_field_order_version",
            CANONICAL_FIELD_ORDER_VERSION,
        ),
        ("digest_algorithm", DIGEST_ALGORITHM),
        ("governance_schema_version", SLICE39B_SCHEMA_VERSION),
    ):
        _require_fixed(
            getattr(record, name),
            expected,
            path=f"version_custody.{name}",
            issues=issues,
            code=(
                CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH
                if "schema" in name or "field_order" in name
                else CandidateMeaningValidationCode.IDENTITY_MISMATCH
            ),
        )
    _require_bool(
        record.non_llm_provenance,
        True,
        path="version_custody.non_llm_provenance",
        issues=issues,
    )
    for name in (
        "timestamps_in_identity",
        "randomness_in_identity",
        "process_identity_in_identity",
        "filesystem_state_in_identity",
        "environment_state_in_identity",
        "hash_table_order_in_identity",
    ):
        _require_bool(
            getattr(record, name),
            False,
            path=f"version_custody.{name}",
            issues=issues,
            code=CandidateMeaningValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED,
        )
    for name in (
        "runtime_authorized",
        "gate_progression_authorized",
        "action_authorized",
        "memory_authorized",
        "rendering_authorized",
        "delivery_authorized",
    ):
        _require_bool(
            getattr(record, name),
            False,
            path=f"version_custody.{name}",
            issues=issues,
        )
    if type(identity) is CandidateMeaningIdentity:
        for name, expected in (
            ("candidate_meaning_id", identity.candidate_meaning_id),
            ("candidate_version", identity.candidate_version),
            ("construction_profile_id", identity.construction_profile_id),
            (
                "construction_profile_version",
                identity.construction_profile_version,
            ),
        ):
            _require_fixed(
                getattr(record, name),
                expected,
                path=f"version_custody.{name}",
                issues=issues,
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            )
    if type(provenance) is CandidateMeaningProvenance:
        for name, expected in (
            (
                "slice37_registry_snapshot_id",
                provenance.slice37_registry_snapshot_id,
            ),
            (
                "slice38_registry_snapshot_id",
                provenance.slice38_registry_snapshot_id,
            ),
            (
                "compatibility_registry_snapshot_id",
                provenance.compatibility_registry_snapshot_id,
            ),
        ):
            _require_fixed(
                getattr(record, name),
                expected,
                path=f"version_custody.{name}",
                issues=issues,
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            )
    try:
        expected = expected_version_custody_id(record)
    except Exception as error:
        _issue(
            issues,
            "version_custody",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.custody_id,
            expected,
            path="version_custody.custody_id",
            issues=issues,
        )
    return _report(issues)


def _stage_status_allowed(
    stage: CandidateMeaningLifecycleStage,
    status: CandidateMeaningConstructionStatus,
) -> bool:
    if stage in (
        CandidateMeaningLifecycleStage.SCHEMA_DECLARED,
        CandidateMeaningLifecycleStage.PROVENANCE_BOUND,
    ):
        return status is CandidateMeaningConstructionStatus.CONSTRUCTION_INCOMPLETE
    if stage in (
        CandidateMeaningLifecycleStage.CONTENT_CONSTRUCTED,
        CandidateMeaningLifecycleStage.CANDIDATE_SEALED,
        CandidateMeaningLifecycleStage.CANDIDATE_SET_REFERENCED,
    ):
        return status is CandidateMeaningConstructionStatus.CONSTRUCTED
    if stage is CandidateMeaningLifecycleStage.CONSTRUCTION_INCOMPLETE:
        return status in (
            CandidateMeaningConstructionStatus.CONSTRUCTION_INCOMPLETE,
            CandidateMeaningConstructionStatus.CONSTRUCTION_UNKNOWN,
            CandidateMeaningConstructionStatus.CONSTRUCTION_UNSUPPORTED,
            CandidateMeaningConstructionStatus.CONSTRUCTION_CONFLICTED,
        )
    if stage is CandidateMeaningLifecycleStage.PREDECESSOR_INVALID:
        return status is CandidateMeaningConstructionStatus.PREDECESSOR_INVALID
    return False


def validate_lifecycle_record(
    record: Any,
    *,
    bundle: Any | None = None,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningLifecycleRecord,
        path="lifecycle_record",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(
        record, path="lifecycle_record", issues=issues
    )
    stage_ok = _require_enum(
        record.stage,
        CandidateMeaningLifecycleStage,
        path="lifecycle_record.stage",
        issues=issues,
    )
    status_ok = _require_enum(
        record.construction_status,
        CandidateMeaningConstructionStatus,
        path="lifecycle_record.construction_status",
        issues=issues,
    )
    for name in (
        "candidate_set_reference_ids",
        "predecessor_lifecycle_record_ids",
        "reason_refs",
    ):
        _require_tuple(
            getattr(record, name),
            path=f"lifecycle_record.{name}",
            issues=issues,
            item_kind="identifier",
            nonempty=name == "reason_refs",
        )
    if (
        stage_ok
        and status_ok
        and not _stage_status_allowed(record.stage, record.construction_status)
    ):
        _issue(
            issues,
            "lifecycle_record.construction_status",
            CandidateMeaningValidationCode.STATUS_MISMATCH,
            "construction status is incompatible with lifecycle stage",
        )
    if (
        record.stage
        is CandidateMeaningLifecycleStage.CANDIDATE_SET_REFERENCED
        and not record.candidate_set_reference_ids
    ):
        _issue(
            issues,
            "lifecycle_record.candidate_set_reference_ids",
            CandidateMeaningValidationCode.REFERENCE_NOT_FOUND,
            "candidate-set reference is required for this stage",
        )
    for name in _LIFECYCLE_FALSE_FIELDS:
        _require_bool(
            getattr(record, name),
            False,
            path=f"lifecycle_record.{name}",
            issues=issues,
            code=(
                CandidateMeaningValidationCode.AUTOMATIC_TRANSITION_PROHIBITED
                if name == "automatic_progression"
                else CandidateMeaningValidationCode.GATE_PROGRESSION_PROHIBITED
                if name in (
                    "gate_progression_created",
                    "selected_meaning_created",
                    "ambiguity_disposition_created",
                    "clarification_required_created",
                    "refusal_created",
                    "blocked_progression_created",
                )
                else CandidateMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            ),
        )
    _require_fixed(
        record.schema_version,
        SLICE39B_SCHEMA_VERSION,
        path="lifecycle_record.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    if type(bundle) is CandidateMeaningGovernanceBundle:
        expected_refs = (
            ("candidate_meaning_id", bundle.identity.candidate_meaning_id),
            ("identity_ref", bundle.identity.candidate_meaning_id),
            ("content_ref", bundle.content.content_id),
            ("provenance_ref", bundle.provenance.provenance_id),
            ("receipt_ref", bundle.construction_receipt.receipt_id),
            ("state_ref", bundle.state.state_id),
            ("version_custody_ref", bundle.version_custody.custody_id),
        )
        for name, expected in expected_refs:
            _require_fixed(
                getattr(record, name),
                expected,
                path=f"lifecycle_record.{name}",
                issues=issues,
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            )
    try:
        expected = expected_lifecycle_record_id(record)
    except Exception as error:
        _issue(
            issues,
            "lifecycle_record",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.lifecycle_record_id,
            expected,
            path="lifecycle_record.lifecycle_record_id",
            issues=issues,
        )
    return _report(issues)


def validate_lifecycle_transition_record(
    record: Any,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningLifecycleTransitionRecord,
        path="lifecycle_transition",
        issues=issues,
    ):
        return _report(issues)
    _validate_identifier_fields(
        record, path="lifecycle_transition", issues=issues
    )
    from_ok = _require_enum(
        record.from_stage,
        CandidateMeaningLifecycleStage,
        path="lifecycle_transition.from_stage",
        issues=issues,
    )
    to_ok = _require_enum(
        record.to_stage,
        CandidateMeaningLifecycleStage,
        path="lifecycle_transition.to_stage",
        issues=issues,
    )
    kind_ok = _require_enum(
        record.transition_kind,
        CandidateMeaningLifecycleTransitionKind,
        path="lifecycle_transition.transition_kind",
        issues=issues,
    )
    for name in ("reason_refs", "predecessor_transition_refs"):
        _require_tuple(
            getattr(record, name),
            path=f"lifecycle_transition.{name}",
            issues=issues,
            item_kind="identifier",
            nonempty=name == "reason_refs",
        )
    for name in _TRANSITION_FALSE_FIELDS:
        _require_bool(
            getattr(record, name),
            False,
            path=f"lifecycle_transition.{name}",
            issues=issues,
            code=(
                CandidateMeaningValidationCode.AUTOMATIC_TRANSITION_PROHIBITED
                if name == "automatic_transition"
                else CandidateMeaningValidationCode.GATE_PROGRESSION_PROHIBITED
                if name in (
                    "gate_progression_created",
                    "selected_meaning_created",
                    "ambiguity_disposition_created",
                    "clarification_required_created",
                    "refusal_created",
                    "blocked_progression_created",
                )
                else CandidateMeaningValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            ),
        )
    _require_fixed(
        record.schema_version,
        SLICE39B_SCHEMA_VERSION,
        path="lifecycle_transition.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )
    if (
        from_ok
        and to_ok
        and kind_ok
        and not lifecycle_transition_allowed(
            record.from_stage,
            record.to_stage,
            record.transition_kind,
        )
    ):
        _issue(
            issues,
            "lifecycle_transition",
            CandidateMeaningValidationCode.LIFECYCLE_TRANSITION_NOT_PERMITTED,
            "transition is outside the closed Slice 39B lifecycle matrix",
        )
    try:
        expected = expected_lifecycle_transition_id(record)
    except Exception as error:
        _issue(
            issues,
            "lifecycle_transition",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.transition_id,
            expected,
            path="lifecycle_transition.transition_id",
            issues=issues,
        )
    return _report(issues)


def _extend(
    issues: list[CandidateMeaningValidationIssue],
    report: CandidateMeaningValidationReport,
    prefix: str,
) -> None:
    for issue in report.issues:
        issues.append(
            CandidateMeaningValidationIssue(
                path=f"{prefix}.{issue.path}",
                code=issue.code,
                detail=issue.detail,
            )
        )


def validate_governance_bundle(
    record: Any,
) -> CandidateMeaningValidationReport:
    issues: list[CandidateMeaningValidationIssue] = []
    if not _require_exact_type(
        record,
        CandidateMeaningGovernanceBundle,
        path="bundle",
        issues=issues,
    ):
        return _report(issues)

    _extend(
        issues,
        validate_content_record(record.content),
        "bundle",
    )
    _extend(
        issues,
        validate_provenance_record(record.provenance),
        "bundle",
    )
    _extend(
        issues,
        validate_identity_record(
            record.identity,
            content=record.content,
            provenance=record.provenance,
        ),
        "bundle",
    )
    _extend(
        issues,
        validate_construction_receipt(
            record.construction_receipt,
            identity=record.identity,
            content=record.content,
            provenance=record.provenance,
        ),
        "bundle",
    )
    _extend(
        issues,
        validate_state_record(record.state),
        "bundle",
    )
    _extend(
        issues,
        validate_version_custody(
            record.version_custody,
            identity=record.identity,
            provenance=record.provenance,
        ),
        "bundle",
    )

    if record.state.identity != record.identity:
        _issue(
            issues,
            "bundle.state.identity",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "state identity must equal bundle identity",
        )
    if record.state.content != record.content:
        _issue(
            issues,
            "bundle.state.content",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "state content must equal bundle content",
        )
    if record.state.provenance != record.provenance:
        _issue(
            issues,
            "bundle.state.provenance",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "state provenance must equal bundle provenance",
        )
    if record.state.construction_receipt != record.construction_receipt:
        _issue(
            issues,
            "bundle.state.construction_receipt",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "state receipt must equal bundle receipt",
        )
    if record.state.construction_status != record.construction_receipt.status:
        _issue(
            issues,
            "bundle.state.construction_status",
            CandidateMeaningValidationCode.STATUS_MISMATCH,
            "state and receipt construction statuses differ",
        )

    alternative_ids: list[str] = []
    alternative_targets: list[str] = []
    for index, item in enumerate(record.alternative_references):
        _extend(
            issues,
            validate_alternative_reference(
                item,
                candidate_meaning_id=record.identity.candidate_meaning_id,
            ),
            f"bundle.alternative_references[{index}]",
        )
        alternative_ids.append(item.alternative_reference_id)
        alternative_targets.append(item.alternative_candidate_meaning_id)
    if len(alternative_ids) != len(set(alternative_ids)):
        _issue(
            issues,
            "bundle.alternative_references",
            CandidateMeaningValidationCode.DUPLICATE_RECORD_ID,
            "alternative reference IDs must be unique",
        )
    if len(alternative_targets) != len(set(alternative_targets)):
        _issue(
            issues,
            "bundle.alternative_references",
            CandidateMeaningValidationCode.DUPLICATE_RECORD_ID,
            "alternative candidate IDs must be unique",
        )
    if tuple(alternative_ids) != record.construction_receipt.alternative_reference_ids:
        _issue(
            issues,
            "bundle.construction_receipt.alternative_reference_ids",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "receipt alternative IDs must match exact bundle order",
        )
    if tuple(record.state.alternative_references) != tuple(record.alternative_references):
        _issue(
            issues,
            "bundle.state.alternative_references",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "state alternatives must match exact bundle alternatives",
        )
    if set(record.state.unresolved_alternative_refs) != set(alternative_targets):
        _issue(
            issues,
            "bundle.state.unresolved_alternative_refs",
            CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "state unresolved alternatives must match alternative targets",
        )

    lifecycle_ids: list[str] = []
    lifecycle_by_id: dict[str, CandidateMeaningLifecycleRecord] = {}
    for index, item in enumerate(record.lifecycle_records):
        _extend(
            issues,
            validate_lifecycle_record(item, bundle=record),
            f"bundle.lifecycle_records[{index}]",
        )
        lifecycle_ids.append(item.lifecycle_record_id)
        lifecycle_by_id[item.lifecycle_record_id] = item
    if len(lifecycle_ids) != len(set(lifecycle_ids)):
        _issue(
            issues,
            "bundle.lifecycle_records",
            CandidateMeaningValidationCode.DUPLICATE_LIFECYCLE_RECORD,
            "lifecycle record IDs must be unique",
        )

    transition_ids: list[str] = []
    for index, item in enumerate(record.lifecycle_transitions):
        _extend(
            issues,
            validate_lifecycle_transition_record(item),
            f"bundle.lifecycle_transitions[{index}]",
        )
        transition_ids.append(item.transition_id)
        source = lifecycle_by_id.get(item.source_lifecycle_record_id)
        target = lifecycle_by_id.get(item.target_lifecycle_record_id)
        if source is None:
            _issue(
                issues,
                f"bundle.lifecycle_transitions[{index}].source_lifecycle_record_id",
                CandidateMeaningValidationCode.REFERENCE_NOT_FOUND,
                "source lifecycle record not found",
            )
        if target is None:
            _issue(
                issues,
                f"bundle.lifecycle_transitions[{index}].target_lifecycle_record_id",
                CandidateMeaningValidationCode.REFERENCE_NOT_FOUND,
                "target lifecycle record not found",
            )
        if source is not None and target is not None:
            if item.candidate_meaning_id != record.identity.candidate_meaning_id:
                _issue(
                    issues,
                    f"bundle.lifecycle_transitions[{index}].candidate_meaning_id",
                    CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "transition candidate identity mismatch",
                )
            if item.from_stage is not source.stage:
                _issue(
                    issues,
                    f"bundle.lifecycle_transitions[{index}].from_stage",
                    CandidateMeaningValidationCode.LIFECYCLE_STAGE_INVALID,
                    "transition source stage mismatch",
                )
            if item.to_stage is not target.stage:
                _issue(
                    issues,
                    f"bundle.lifecycle_transitions[{index}].to_stage",
                    CandidateMeaningValidationCode.LIFECYCLE_STAGE_INVALID,
                    "transition target stage mismatch",
                )
            if item.version_custody_ref != record.version_custody.custody_id:
                _issue(
                    issues,
                    f"bundle.lifecycle_transitions[{index}].version_custody_ref",
                    CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "transition version-custody reference mismatch",
                )
            if target.predecessor_lifecycle_record_ids != (
                source.lifecycle_record_id,
            ):
                _issue(
                    issues,
                    f"bundle.lifecycle_records[{lifecycle_ids.index(target.lifecycle_record_id)}].predecessor_lifecycle_record_ids",
                    CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "target must preserve exact single source lifecycle ancestry",
                )
    if len(transition_ids) != len(set(transition_ids)):
        _issue(
            issues,
            "bundle.lifecycle_transitions",
            CandidateMeaningValidationCode.DUPLICATE_TRANSITION_ID,
            "lifecycle transition IDs must be unique",
        )

    _require_identifier(
        record.bundle_id, path="bundle.bundle_id", issues=issues
    )
    _require_sha256(
        record.canonical_digest,
        path="bundle.canonical_digest",
        issues=issues,
    )
    for name in _BUNDLE_FALSE_FIELDS:
        _require_bool(
            getattr(record, name),
            False,
            path=f"bundle.{name}",
            issues=issues,
        )
    _require_fixed(
        record.schema_version,
        SLICE39B_SCHEMA_VERSION,
        path="bundle.schema_version",
        issues=issues,
        code=CandidateMeaningValidationCode.SCHEMA_VERSION_MISMATCH,
    )

    try:
        expected_digest = expected_bundle_digest(record)
        expected_id = expected_bundle_id(record)
    except Exception as error:
        _issue(
            issues,
            "bundle",
            CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
            f"canonicalization failed: {type(error).__name__}",
        )
    else:
        _require_fixed(
            record.canonical_digest,
            expected_digest,
            path="bundle.canonical_digest",
            issues=issues,
            code=CandidateMeaningValidationCode.CANONICAL_DIGEST_MISMATCH,
        )
        _require_fixed(
            record.bundle_id,
            expected_id,
            path="bundle.bundle_id",
            issues=issues,
        )

    return _report(issues)


def assert_valid_governance_bundle(
    record: CandidateMeaningGovernanceBundle,
) -> CandidateMeaningGovernanceBundle:
    report = validate_governance_bundle(record)
    if not report.ok:
        raise CandidateMeaningValidationError(report)
    return record


def assert_valid_version_custody(
    record: CandidateMeaningVersionCustody,
    *,
    identity: CandidateMeaningIdentity,
    provenance: CandidateMeaningProvenance,
) -> CandidateMeaningVersionCustody:
    report = validate_version_custody(
        record,
        identity=identity,
        provenance=provenance,
    )
    if not report.ok:
        raise CandidateMeaningValidationError(report)
    return record


__all__ = (
    "assert_valid_governance_bundle",
    "assert_valid_version_custody",
    "validate_alternative_reference",
    "validate_construction_receipt",
    "validate_content_record",
    "validate_field_pairs",
    "validate_governance_bundle",
    "validate_identity_record",
    "validate_lifecycle_record",
    "validate_lifecycle_transition_record",
    "validate_provenance_record",
    "validate_state_record",
    "validate_version_custody",
)
