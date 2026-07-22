"""Fail-closed deterministic validation for Slice 43B."""

from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
import re
import types
from typing import Any, Iterable, Union, get_args, get_origin, get_type_hints

from .. import schema as core
from ..schema import (
    AuthorizedMeaningReferenceRecord,
    DriftFindingBoundaryRecord,
    EchoContainmentBoundaryRecord,
    EchoDispositionBoundaryRecord,
    EchoReceiptBoundaryRecord,
    EchoRejectionBoundaryRecord,
    EchoTraceBoundaryRecord,
    EchoValidationInputBoundaryRecord,
    PreservationDimension,
    PreservationDimensionRequirementRecord,
    ProposedExpressionReferenceRecord,
    RmcEchoRuntimeSchemaRecord,
    ValidationFindingBoundaryRecord,
)
from .canonical import (
    SUPPORTED_RECORD_TYPES,
    RmcEchoCanonicalizationError,
    canonical_field_order,
    canonical_record_bytes,
)
from .identity import (
    expected_bundle_digest,
    expected_bundle_id,
    expected_record_id,
    identity_field,
)
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    DIGEST_ALGORITHM,
    SLICE43B_ACCEPTED_PARENT_HEAD,
    SLICE43B_ACCEPTED_PARENT_SUBJECT,
    SLICE43B_ACCEPTED_PARENT_TREE,
    SLICE43B_SCHEMA_VERSION,
    SUPPORTED_RUNTIME_SCHEMA_VERSIONS,
    SUPPORTED_RUNTIME_SPEC_VERSIONS,
    SUPPORTED_VALIDATION_PROFILE_VERSIONS,
    VALIDATION_PROFILE_VERSION,
    RmcEchoGovernanceBundle,
    RmcEchoLifecycleRecord,
    RmcEchoLifecycleStage,
    RmcEchoLifecycleTransitionRecord,
    RmcEchoValidationCode,
    RmcEchoValidationError,
    RmcEchoValidationIssue,
    RmcEchoValidationReport,
    RmcEchoVersionCustody,
)


CORE_RECORD_TYPES = (
    AuthorizedMeaningReferenceRecord,
    ProposedExpressionReferenceRecord,
    EchoValidationInputBoundaryRecord,
    PreservationDimensionRequirementRecord,
    ValidationFindingBoundaryRecord,
    DriftFindingBoundaryRecord,
    EchoDispositionBoundaryRecord,
    EchoRejectionBoundaryRecord,
    EchoContainmentBoundaryRecord,
    EchoTraceBoundaryRecord,
    EchoReceiptBoundaryRecord,
    RmcEchoRuntimeSchemaRecord,
)

_IDENTIFIER_RE = re.compile(r"^[^\s\x00-\x1f\x7f]+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _issue(
    path: str,
    code: RmcEchoValidationCode,
    detail: str,
) -> RmcEchoValidationIssue:
    return RmcEchoValidationIssue(path=path, code=code, detail=detail)


def _report(
    issues: Iterable[RmcEchoValidationIssue],
) -> RmcEchoValidationReport:
    ordered = tuple(
        sorted(
            issues,
            key=lambda item: (item.path, item.code.value, item.detail),
        )
    )
    return RmcEchoValidationReport(issues=ordered)


def _is_valid_text(value: Any) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and "\x00" not in value
        and all(ord(character) >= 32 or character in "\t\n\r" for character in value)
    )


def _is_identifier(value: Any) -> bool:
    return type(value) is str and bool(_IDENTIFIER_RE.fullmatch(value))


def _matches_annotation(value: Any, annotation: Any) -> bool:
    if annotation is Any:
        return True
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (Union, types.UnionType):
        return any(_matches_annotation(value, item) for item in args)
    if origin is tuple:
        if type(value) is not tuple:
            return False
        if len(args) == 2 and args[1] is Ellipsis:
            return all(_matches_annotation(item, args[0]) for item in value)
        return (
            len(value) == len(args)
            and all(
                _matches_annotation(item, expected)
                for item, expected in zip(value, args)
            )
        )
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return type(value) is annotation
    if isinstance(annotation, type):
        return type(value) is annotation
    return False


def _default_for_field(item: Any) -> Any:
    if item.default is not MISSING:
        return item.default
    if item.default_factory is not MISSING:
        return item.default_factory()
    raise LookupError(item.name)


def _validate_tuple_contents(
    path: str,
    value: tuple[Any, ...],
    issues: list[RmcEchoValidationIssue],
) -> None:
    try:
        normalized = tuple(repr(item) for item in value)
        if len(normalized) != len(set(normalized)):
            issues.append(
                _issue(
                    path,
                    RmcEchoValidationCode.DUPLICATE_TUPLE_VALUE,
                    "tuple values must be unique",
                )
            )
    except TypeError:
        issues.append(
            _issue(
                path,
                RmcEchoValidationCode.INVALID_TUPLE,
                "tuple values could not be checked deterministically",
            )
        )


def _validate_dataclass_shape(
    record: Any,
    *,
    path: str,
) -> list[RmcEchoValidationIssue]:
    issues: list[RmcEchoValidationIssue] = []
    record_type = type(record)
    if record_type not in SUPPORTED_RECORD_TYPES:
        return [
            _issue(
                path,
                RmcEchoValidationCode.TYPE_MISMATCH,
                f"unsupported record type: {record_type.__name__}",
            )
        ]
    if not is_dataclass(record) or isinstance(record, type):
        return [
            _issue(
                path,
                RmcEchoValidationCode.TYPE_MISMATCH,
                "record must be an admitted dataclass instance",
            )
        ]
    hints = get_type_hints(record_type)
    for item in fields(record):
        value = getattr(record, item.name)
        field_path = f"{path}.{item.name}" if path else item.name
        annotation = hints.get(item.name, item.type)
        if not _matches_annotation(value, annotation):
            issues.append(
                _issue(
                    field_path,
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    f"value does not match {annotation!r}",
                )
            )
            continue
        if type(value) is str:
            if not _is_valid_text(value):
                issues.append(
                    _issue(
                        field_path,
                        RmcEchoValidationCode.INVALID_TEXT,
                        "text must be non-empty, trimmed, and control-free",
                    )
                )
            if (
                item.name.endswith("_id")
                or item.name.endswith("_ref")
                or item.name.endswith("_version")
                or item.name in {
                    "schema_id",
                    "spec_id",
                    "spec_version",
                    "lineage_id",
                    "realized_text_sha256",
                }
            ):
                if item.name == "realized_text_sha256":
                    if not _SHA256_RE.fullmatch(value):
                        issues.append(
                            _issue(
                                field_path,
                                RmcEchoValidationCode.INVALID_SHA256,
                                "expected lowercase SHA-256",
                            )
                        )
                elif not _is_identifier(value):
                    issues.append(
                        _issue(
                            field_path,
                            RmcEchoValidationCode.INVALID_IDENTIFIER,
                            "identifier may not contain whitespace or controls",
                        )
                    )
        elif type(value) is tuple:
            _validate_tuple_contents(field_path, value, issues)
            for index, member in enumerate(value):
                member_path = f"{field_path}[{index}]"
                if type(member) is str and not _is_identifier(member):
                    issues.append(
                        _issue(
                            member_path,
                            RmcEchoValidationCode.INVALID_IDENTIFIER,
                            "tuple reference must be a non-empty identifier",
                        )
                    )
                elif type(member) is tuple:
                    if (
                        len(member) != 2
                        or type(member[0]) is not str
                        or type(member[1]) is not str
                        or not _is_identifier(member[0])
                        or not _is_identifier(member[1])
                    ):
                        issues.append(
                            _issue(
                                member_path,
                                RmcEchoValidationCode.INVALID_TUPLE,
                                "pair must contain two valid identifier strings",
                            )
                        )
        if not item.init:
            try:
                expected = _default_for_field(item)
            except LookupError:
                continue
            if value != expected:
                issues.append(
                    _issue(
                        field_path,
                        RmcEchoValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                        "Slice 43A locked field differs from its non-authority default",
                    )
                )
    return issues


def _validate_identity(
    record: Any,
    *,
    path: str,
) -> list[RmcEchoValidationIssue]:
    issues: list[RmcEchoValidationIssue] = []
    try:
        field_name = identity_field(type(record))
        observed = getattr(record, field_name)
        expected = expected_record_id(record)
    except (TypeError, RmcEchoCanonicalizationError, AttributeError) as error:
        return [
            _issue(
                path,
                RmcEchoValidationCode.IDENTITY_MISMATCH,
                f"identity could not be calculated: {error}",
            )
        ]
    if observed != expected:
        issues.append(
            _issue(
                f"{path}.{field_name}",
                RmcEchoValidationCode.IDENTITY_MISMATCH,
                f"expected {expected}",
            )
        )
    return issues


def validate_record(record: Any) -> RmcEchoValidationReport:
    issues = _validate_dataclass_shape(record, path=type(record).__name__)
    if not issues:
        issues.extend(_validate_identity(record, path=type(record).__name__))
    return _report(issues)


def validate_field_pairs(
    record_type: type[Any],
    field_pairs: Iterable[tuple[str, Any]],
) -> RmcEchoValidationReport:
    issues: list[RmcEchoValidationIssue] = []
    try:
        expected = canonical_field_order(record_type)
    except RmcEchoCanonicalizationError as error:
        return _report(
            (
                _issue(
                    "record_type",
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    str(error),
                ),
            )
        )
    pairs = tuple(field_pairs)
    observed_names: list[str] = []
    observed: dict[str, Any] = {}
    for index, pair in enumerate(pairs):
        if (
            type(pair) is not tuple
            or len(pair) != 2
            or type(pair[0]) is not str
        ):
            issues.append(
                _issue(
                    f"field_pairs[{index}]",
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    "field pair must be exact (str, value)",
                )
            )
            continue
        name, value = pair
        observed_names.append(name)
        if name in observed:
            issues.append(
                _issue(
                    name,
                    RmcEchoValidationCode.DUPLICATE_FIELD,
                    "field appears more than once",
                )
            )
        else:
            observed[name] = value
        if name not in expected:
            issues.append(
                _issue(
                    name,
                    RmcEchoValidationCode.UNKNOWN_FIELD,
                    "field is not admitted for this record type",
                )
            )
    for name in expected:
        if name not in observed:
            issues.append(
                _issue(
                    name,
                    RmcEchoValidationCode.MISSING_FIELD,
                    "required canonical field is missing",
                )
            )
    if tuple(observed_names) != expected:
        issues.append(
            _issue(
                "field_pairs",
                RmcEchoValidationCode.FIELD_ORDER_MISMATCH,
                "field order must exactly match the admitted dataclass order",
            )
        )
    if not issues:
        hints = get_type_hints(record_type)
        for item in fields(record_type):
            if not _matches_annotation(
                observed[item.name],
                hints.get(item.name, item.type),
            ):
                issues.append(
                    _issue(
                        item.name,
                        RmcEchoValidationCode.TYPE_MISMATCH,
                        "field value has the wrong exact type",
                    )
                )
    return _report(issues)


def _core_records(
    record: RmcEchoRuntimeSchemaRecord,
) -> tuple[Any, ...]:
    return (
        record.authorized_meaning_reference,
        record.proposed_expression_reference,
        record.validation_input_boundary,
        *record.preservation_dimension_requirements,
        *record.validation_finding_boundaries,
        *record.drift_finding_boundaries,
        record.echo_disposition_boundary,
        record.rejection_boundary,
        record.containment_boundary,
        record.trace_boundary,
        record.receipt_boundary,
        record,
    )


def expected_record_schema_versions(
    record: RmcEchoRuntimeSchemaRecord,
) -> tuple[tuple[str, str], ...]:
    representatives = (
        record.authorized_meaning_reference,
        record.proposed_expression_reference,
        record.validation_input_boundary,
        record.preservation_dimension_requirements[0]
        if record.preservation_dimension_requirements
        else None,
        record.validation_finding_boundaries[0]
        if record.validation_finding_boundaries
        else None,
        record.drift_finding_boundaries[0]
        if record.drift_finding_boundaries
        else None,
        record.echo_disposition_boundary,
        record.rejection_boundary,
        record.containment_boundary,
        record.trace_boundary,
        record.receipt_boundary,
        record,
    )
    pairs = {
        (item.schema_id, item.schema_version)
        for item in representatives
        if item is not None
    }
    return tuple(sorted(pairs))


def expected_predecessor_references(
    record: RmcEchoRuntimeSchemaRecord,
) -> tuple[tuple[str, str], ...]:
    authorized = record.authorized_meaning_reference
    proposed = record.proposed_expression_reference
    validation_input = record.validation_input_boundary
    trace = record.trace_boundary
    pairs: list[tuple[str, str]] = [
        ("accepted_parent_head", SLICE43B_ACCEPTED_PARENT_HEAD),
        ("accepted_parent_tree", SLICE43B_ACCEPTED_PARENT_TREE),
        ("authorized.slice42g_input", authorized.slice42g_integration_input_ref),
        ("authorized.slice42g_result", authorized.slice42g_integration_result_ref),
        (
            "authorized.slice42g_receipt",
            authorized.slice42g_integration_receipt_ref,
        ),
        ("authorized.slice42h_acceptance", authorized.slice42h_acceptance_record_ref),
        ("authorized.source_manifest", authorized.source_manifest_ref),
        ("authorized.successor_manifest", authorized.successor_manifest_ref),
        ("proposed.slice42f_input", proposed.slice42f_realization_input_ref),
        ("proposed.slice42f_result", proposed.slice42f_realization_result_ref),
        ("proposed.slice42f_receipt", proposed.slice42f_realization_receipt_ref),
        ("proposed.slice42g_input", proposed.slice42g_integration_input_ref),
        ("proposed.slice42g_result", proposed.slice42g_integration_result_ref),
        ("proposed.slice42g_receipt", proposed.slice42g_integration_receipt_ref),
        ("proposed.successor_manifest", proposed.successor_manifest_ref),
        ("proposed.realization_trace", proposed.realization_trace_ref),
        ("proposed.realization_receipt", proposed.realization_receipt_ref),
    ]
    pairs.extend(
        (f"validation_input.predecessor_receipt[{index}]", value)
        for index, value in enumerate(validation_input.predecessor_receipt_refs)
    )
    pairs.extend(
        (f"trace.predecessor_trace[{index}]", value)
        for index, value in enumerate(trace.predecessor_trace_refs)
    )
    pairs.extend(
        (f"trace.predecessor_receipt[{index}]", value)
        for index, value in enumerate(trace.predecessor_receipt_refs)
    )
    return tuple(sorted(pairs))


def validate_identity_collection(
    records: Iterable[Any],
) -> RmcEchoValidationReport:
    issues: list[RmcEchoValidationIssue] = []
    observed: dict[str, tuple[bytes, int]] = {}
    for index, record in enumerate(tuple(records)):
        path = f"records[{index}]"
        if type(record) not in CORE_RECORD_TYPES:
            issues.append(
                _issue(
                    path,
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    "identity collection contains an unsupported record",
                )
            )
            continue
        try:
            field_name = identity_field(type(record))
            record_id = getattr(record, field_name)
            canonical = canonical_record_bytes(record)
        except (TypeError, AttributeError, RmcEchoCanonicalizationError) as error:
            issues.append(
                _issue(
                    path,
                    RmcEchoValidationCode.IDENTITY_MISMATCH,
                    f"record identity could not be inspected: {error}",
                )
            )
            continue
        if record_id in observed:
            prior_bytes, prior_index = observed[record_id]
            code = (
                RmcEchoValidationCode.DUPLICATE_RECORD_ID
                if prior_bytes == canonical
                else RmcEchoValidationCode.IDENTITY_COLLISION
            )
            detail = (
                f"identity repeats records[{prior_index}]"
                if code is RmcEchoValidationCode.DUPLICATE_RECORD_ID
                else f"identity collides with records[{prior_index}]"
            )
            issues.append(_issue(path, code, detail))
        else:
            observed[record_id] = (canonical, index)
    return _report(issues)


def _cross_record_issues(
    record: RmcEchoRuntimeSchemaRecord,
) -> list[RmcEchoValidationIssue]:
    issues: list[RmcEchoValidationIssue] = []
    authorized = record.authorized_meaning_reference
    proposed = record.proposed_expression_reference
    validation_input = record.validation_input_boundary
    requirements = record.preservation_dimension_requirements
    findings = record.validation_finding_boundaries
    drifts = record.drift_finding_boundaries
    disposition = record.echo_disposition_boundary
    rejection = record.rejection_boundary
    containment = record.containment_boundary
    trace = record.trace_boundary
    receipt = record.receipt_boundary

    def exact(path: str, observed: Any, expected: Any, detail: str) -> None:
        if observed != expected:
            issues.append(
                _issue(
                    path,
                    RmcEchoValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    detail,
                )
            )

    exact(
        "validation_input.authorized_meaning_reference",
        validation_input.authorized_meaning_reference,
        authorized,
        "validation input must embed the exact authorized-meaning record",
    )
    exact(
        "validation_input.proposed_expression_reference",
        validation_input.proposed_expression_reference,
        proposed,
        "validation input must embed the exact proposed-expression record",
    )

    shared_pairs = (
        (
            "lineage_id",
            authorized.lineage_id,
            proposed.lineage_id,
        ),
        (
            "slice42g_integration_input_ref",
            authorized.slice42g_integration_input_ref,
            proposed.slice42g_integration_input_ref,
        ),
        (
            "slice42g_integration_result_ref",
            authorized.slice42g_integration_result_ref,
            proposed.slice42g_integration_result_ref,
        ),
        (
            "slice42g_integration_receipt_ref",
            authorized.slice42g_integration_receipt_ref,
            proposed.slice42g_integration_receipt_ref,
        ),
        (
            "successor_manifest_ref",
            authorized.successor_manifest_ref,
            proposed.successor_manifest_ref,
        ),
        (
            "governed_outward_meaning_ref",
            authorized.governed_outward_meaning_ref,
            proposed.governed_outward_meaning_ref,
        ),
        (
            "expression_plan_ref",
            authorized.expression_plan_ref,
            proposed.expression_plan_ref,
        ),
        (
            "preservation_obligation_package_ref",
            authorized.preservation_obligation_package_ref,
            proposed.preservation_obligation_package_ref,
        ),
    )
    for name, left, right in shared_pairs:
        exact(
            f"authorized/proposed.{name}",
            left,
            right,
            f"authorized meaning and proposed expression must share {name}",
        )

    expected_dimensions = tuple(PreservationDimension)
    exact(
        "validation_input.required_preservation_dimensions",
        validation_input.required_preservation_dimensions,
        expected_dimensions,
        "all 22 preservation dimensions must appear once in canonical order",
    )
    if len(requirements) != len(expected_dimensions):
        issues.append(
            _issue(
                "preservation_dimension_requirements",
                RmcEchoValidationCode.PREDECESSOR_REFERENCE_MISSING,
                "exactly one requirement is required for every preservation dimension",
            )
        )
    if len(findings) != len(expected_dimensions):
        issues.append(
            _issue(
                "validation_finding_boundaries",
                RmcEchoValidationCode.PREDECESSOR_REFERENCE_MISSING,
                "exactly one finding boundary is required for every dimension",
            )
        )
    if len(drifts) != len(expected_dimensions):
        issues.append(
            _issue(
                "drift_finding_boundaries",
                RmcEchoValidationCode.PREDECESSOR_REFERENCE_MISSING,
                "exactly one drift boundary is required for every dimension",
            )
        )

    for index, dimension in enumerate(expected_dimensions):
        if index >= len(requirements):
            break
        requirement = requirements[index]
        exact(
            f"requirements[{index}].validation_input_boundary_ref",
            requirement.validation_input_boundary_ref,
            validation_input.validation_input_boundary_id,
            "dimension requirement must reference the exact validation input",
        )
        exact(
            f"requirements[{index}].dimension",
            requirement.dimension,
            dimension,
            "dimension requirement order or identity mismatch",
        )
        if not requirement.required_preservation_refs:
            issues.append(
                _issue(
                    f"requirements[{index}].required_preservation_refs",
                    RmcEchoValidationCode.REQUIRED_VALUE_MISSING,
                    "preservation requirement must state an exact obligation",
                )
            )
        if not requirement.prohibited_drift_refs:
            issues.append(
                _issue(
                    f"requirements[{index}].prohibited_drift_refs",
                    RmcEchoValidationCode.REQUIRED_VALUE_MISSING,
                    "preservation requirement must state prohibited drift",
                )
            )

    for index, dimension in enumerate(expected_dimensions):
        if index >= len(findings) or index >= len(requirements):
            break
        finding = findings[index]
        requirement = requirements[index]
        exact(
            f"findings[{index}].validation_input_boundary_ref",
            finding.validation_input_boundary_ref,
            validation_input.validation_input_boundary_id,
            "finding boundary must reference the exact validation input",
        )
        exact(
            f"findings[{index}].dimension_requirement_ref",
            finding.dimension_requirement_ref,
            requirement.dimension_requirement_id,
            "finding boundary must reference the matching requirement",
        )
        exact(
            f"findings[{index}].dimension",
            finding.dimension,
            dimension,
            "finding dimension mismatch",
        )
        exact(
            f"findings[{index}].authorized_meaning_feature_refs",
            finding.authorized_meaning_feature_refs,
            requirement.authorized_meaning_feature_refs,
            "finding custody must preserve authorized feature references",
        )
        exact(
            f"findings[{index}].proposed_expression_feature_refs",
            finding.proposed_expression_feature_refs,
            requirement.proposed_expression_feature_refs,
            "finding custody must preserve expression feature references",
        )

    for index, dimension in enumerate(expected_dimensions):
        if index >= len(drifts) or index >= len(findings):
            break
        drift = drifts[index]
        finding = findings[index]
        exact(
            f"drifts[{index}].validation_input_boundary_ref",
            drift.validation_input_boundary_ref,
            validation_input.validation_input_boundary_id,
            "drift boundary must reference the exact validation input",
        )
        exact(
            f"drifts[{index}].validation_finding_boundary_ref",
            drift.validation_finding_boundary_ref,
            finding.validation_finding_boundary_id,
            "drift boundary must reference the matching finding boundary",
        )
        exact(
            f"drifts[{index}].dimension",
            drift.dimension,
            dimension,
            "drift dimension mismatch",
        )

    finding_ids = tuple(
        item.validation_finding_boundary_id for item in findings
    )
    drift_ids = tuple(item.drift_finding_boundary_id for item in drifts)
    requirement_ids = tuple(item.dimension_requirement_id for item in requirements)

    exact(
        "disposition.validation_input_boundary_ref",
        disposition.validation_input_boundary_ref,
        validation_input.validation_input_boundary_id,
        "disposition boundary must reference exact validation input",
    )
    exact(
        "disposition.validation_finding_boundary_refs",
        disposition.validation_finding_boundary_refs,
        finding_ids,
        "disposition custody must preserve every finding boundary reference",
    )
    exact(
        "disposition.drift_finding_boundary_refs",
        disposition.drift_finding_boundary_refs,
        drift_ids,
        "disposition custody must preserve every drift boundary reference",
    )

    for label, boundary in (
        ("rejection", rejection),
        ("containment", containment),
    ):
        exact(
            f"{label}.validation_input_boundary_ref",
            boundary.validation_input_boundary_ref,
            validation_input.validation_input_boundary_id,
            f"{label} boundary must reference exact validation input",
        )
        exact(
            f"{label}.echo_disposition_boundary_ref",
            boundary.echo_disposition_boundary_ref,
            disposition.echo_disposition_boundary_id,
            f"{label} boundary must reference exact disposition boundary",
        )

    exact(
        "trace.authorized_meaning_reference_ref",
        trace.authorized_meaning_reference_ref,
        authorized.authorized_meaning_reference_id,
        "trace must reference exact authorized meaning",
    )
    exact(
        "trace.proposed_expression_reference_ref",
        trace.proposed_expression_reference_ref,
        proposed.proposed_expression_reference_id,
        "trace must reference exact proposed expression",
    )
    exact(
        "trace.validation_input_boundary_ref",
        trace.validation_input_boundary_ref,
        validation_input.validation_input_boundary_id,
        "trace must reference exact validation input",
    )
    exact(
        "trace.preservation_dimension_requirement_refs",
        trace.preservation_dimension_requirement_refs,
        requirement_ids,
        "trace must preserve every dimension requirement",
    )
    exact(
        "trace.validation_finding_boundary_refs",
        trace.validation_finding_boundary_refs,
        finding_ids,
        "trace must preserve every finding boundary",
    )
    exact(
        "trace.drift_finding_boundary_refs",
        trace.drift_finding_boundary_refs,
        drift_ids,
        "trace must preserve every drift boundary",
    )
    exact(
        "trace.echo_disposition_boundary_ref",
        trace.echo_disposition_boundary_ref,
        disposition.echo_disposition_boundary_id,
        "trace must reference exact disposition boundary",
    )
    exact(
        "trace.rejection_boundary_ref",
        trace.rejection_boundary_ref,
        rejection.echo_rejection_boundary_id,
        "trace must reference exact rejection boundary",
    )
    exact(
        "trace.containment_boundary_ref",
        trace.containment_boundary_ref,
        containment.echo_containment_boundary_id,
        "trace must reference exact containment boundary",
    )

    receipt_checks = (
        (
            "authorized_meaning_reference_ref",
            receipt.authorized_meaning_reference_ref,
            authorized.authorized_meaning_reference_id,
        ),
        (
            "proposed_expression_reference_ref",
            receipt.proposed_expression_reference_ref,
            proposed.proposed_expression_reference_id,
        ),
        (
            "validation_input_boundary_ref",
            receipt.validation_input_boundary_ref,
            validation_input.validation_input_boundary_id,
        ),
        (
            "echo_trace_boundary_ref",
            receipt.echo_trace_boundary_ref,
            trace.echo_trace_boundary_id,
        ),
        (
            "echo_disposition_boundary_ref",
            receipt.echo_disposition_boundary_ref,
            disposition.echo_disposition_boundary_id,
        ),
        (
            "rejection_boundary_ref",
            receipt.rejection_boundary_ref,
            rejection.echo_rejection_boundary_id,
        ),
        (
            "containment_boundary_ref",
            receipt.containment_boundary_ref,
            containment.echo_containment_boundary_id,
        ),
    )
    for name, observed, expected in receipt_checks:
        exact(
            f"receipt.{name}",
            observed,
            expected,
            f"receipt {name} mismatch",
        )

    if core.SCHEMA_VERSION not in {
        version for _, version in validation_input.schema_version_refs
    }:
        issues.append(
            _issue(
                "validation_input.schema_version_refs",
                RmcEchoValidationCode.SCHEMA_VERSION_MISMATCH,
                "validation input must preserve the Slice 43A schema version",
            )
        )
    if core.SCHEMA_VERSION not in {
        version for _, version in trace.schema_version_refs
    }:
        issues.append(
            _issue(
                "trace.schema_version_refs",
                RmcEchoValidationCode.SCHEMA_VERSION_MISMATCH,
                "trace must preserve the Slice 43A schema version",
            )
        )
    if any(
        value not in core.PRESERVATION_DIMENSION_VALUES
        for value in authorized.preservation_class_refs
    ):
        issues.append(
            _issue(
                "authorized.preservation_class_refs",
                RmcEchoValidationCode.INVALID_ENUM,
                "preservation classes must use admitted Slice 43A dimensions",
            )
        )
    return issues


def validate_runtime_schema_record(
    record: Any,
) -> RmcEchoValidationReport:
    if type(record) is not RmcEchoRuntimeSchemaRecord:
        return _report(
            (
                _issue(
                    "runtime_schema_record",
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    "expected exact RmcEchoRuntimeSchemaRecord",
                ),
            )
        )
    issues: list[RmcEchoValidationIssue] = []
    for index, item in enumerate(_core_records(record)):
        item_path = f"core_records[{index}]"
        issues.extend(_validate_dataclass_shape(item, path=item_path))
        if not any(issue.path.startswith(item_path) for issue in issues):
            issues.extend(_validate_identity(item, path=item_path))
    issues.extend(_cross_record_issues(record))
    identity_report = validate_identity_collection(_core_records(record))
    issues.extend(identity_report.issues)
    return _report(issues)


def validate_version_custody(
    custody: Any,
    *,
    runtime_schema_record: RmcEchoRuntimeSchemaRecord | None = None,
) -> RmcEchoValidationReport:
    if type(custody) is not RmcEchoVersionCustody:
        return _report(
            (
                _issue(
                    "version_custody",
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    "expected exact RmcEchoVersionCustody",
                ),
            )
        )
    issues = _validate_dataclass_shape(custody, path="version_custody")
    if not issues:
        issues.extend(_validate_identity(custody, path="version_custody"))
    exact_values = (
        (
            "runtime_schema_version",
            custody.runtime_schema_version,
            SUPPORTED_RUNTIME_SCHEMA_VERSIONS,
            RmcEchoValidationCode.UNKNOWN_VERSION,
        ),
        (
            "runtime_spec_version",
            custody.runtime_spec_version,
            SUPPORTED_RUNTIME_SPEC_VERSIONS,
            RmcEchoValidationCode.UNKNOWN_VERSION,
        ),
        (
            "validation_profile_version",
            custody.validation_profile_version,
            SUPPORTED_VALIDATION_PROFILE_VERSIONS,
            RmcEchoValidationCode.UNKNOWN_VERSION,
        ),
    )
    for path, value, supported, code in exact_values:
        if value not in supported:
            issues.append(
                _issue(
                    f"version_custody.{path}",
                    code,
                    f"unsupported value: {value!r}",
                )
            )
    fixed = (
        ("accepted_parent_head", custody.accepted_parent_head, SLICE43B_ACCEPTED_PARENT_HEAD),
        ("accepted_parent_tree", custody.accepted_parent_tree, SLICE43B_ACCEPTED_PARENT_TREE),
        (
            "accepted_parent_subject",
            custody.accepted_parent_subject,
            SLICE43B_ACCEPTED_PARENT_SUBJECT,
        ),
        (
            "canonical_field_order_version",
            custody.canonical_field_order_version,
            CANONICAL_FIELD_ORDER_VERSION,
        ),
        ("digest_algorithm", custody.digest_algorithm, DIGEST_ALGORITHM),
        ("governance_schema_version", custody.governance_schema_version, SLICE43B_SCHEMA_VERSION),
    )
    for name, observed, expected in fixed:
        if observed != expected:
            issues.append(
                _issue(
                    f"version_custody.{name}",
                    RmcEchoValidationCode.INVALID_VERSION,
                    f"expected {expected!r}",
                )
            )
    if custody.non_llm_provenance is not True:
        issues.append(
            _issue(
                "version_custody.non_llm_provenance",
                RmcEchoValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                "non-LLM provenance must be explicit",
            )
        )
    nondeterministic_flags = (
        custody.timestamps_in_identity,
        custody.randomness_in_identity,
        custody.process_identity_in_identity,
        custody.filesystem_state_in_identity,
        custody.environment_state_in_identity,
        custody.hash_table_order_in_identity,
    )
    if any(nondeterministic_flags):
        issues.append(
            _issue(
                "version_custody.identity_inputs",
                RmcEchoValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED,
                "identity may not depend on time, randomness, process, filesystem, environment, or hash order",
            )
        )
    authority_flags = (
        custody.slice42_source_admission_authorized,
        custody.meaning_preservation_comparison_authorized,
        custody.validation_finding_construction_authorized,
        custody.drift_classification_authorized,
        custody.materiality_decision_authorized,
        custody.echo_disposition_decision_authorized,
        custody.rejection_or_containment_issuance_authorized,
        custody.expression_repair_authorized,
        custody.msm_v1_mutation_or_integration_authorized,
        custody.bootstrap_integration_authorized,
        custody.delivery_authorized,
        custody.truth_evidence_permission_execution_authorized,
        custody.route_api_network_filesystem_memory_tool_action_authorized,
        custody.external_resource_authority,
        custody.model_embedding_vector_rag_similarity_authority,
        custody.gp014_supersession_authorized,
    )
    if any(authority_flags):
        issues.append(
            _issue(
                "version_custody.authority_flags",
                RmcEchoValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                "Slice 43B version custody may not grant later authority",
            )
        )
    if runtime_schema_record is not None:
        if custody.runtime_schema_record_id != (
            runtime_schema_record.rmc_echo_runtime_schema_record_id
        ):
            issues.append(
                _issue(
                    "version_custody.runtime_schema_record_id",
                    RmcEchoValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "version custody must govern the exact runtime record",
                )
            )
        expected_versions = expected_record_schema_versions(runtime_schema_record)
        if custody.record_schema_versions != expected_versions:
            issues.append(
                _issue(
                    "version_custody.record_schema_versions",
                    RmcEchoValidationCode.SCHEMA_VERSION_MISMATCH,
                    "record schema version custody mismatch",
                )
            )
        expected_predecessors = expected_predecessor_references(
            runtime_schema_record
        )
        if custody.predecessor_references != expected_predecessors:
            issues.append(
                _issue(
                    "version_custody.predecessor_references",
                    RmcEchoValidationCode.PREDECESSOR_REFERENCE_MISMATCH,
                    "exact predecessor-reference custody mismatch",
                )
            )
        fixed_runtime = (
            ("runtime_schema_version", custody.runtime_schema_version, runtime_schema_record.schema_version),
            ("runtime_schema_id", custody.runtime_schema_id, runtime_schema_record.schema_id),
            ("runtime_spec_id", custody.runtime_spec_id, runtime_schema_record.spec_id),
            ("runtime_spec_version", custody.runtime_spec_version, runtime_schema_record.spec_version),
        )
        for name, observed, expected in fixed_runtime:
            if observed != expected:
                issues.append(
                    _issue(
                        f"version_custody.{name}",
                        RmcEchoValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                        f"expected runtime value {expected!r}",
                    )
                )
    return _report(issues)


def validate_lifecycle_record(
    record: Any,
) -> RmcEchoValidationReport:
    if type(record) is not RmcEchoLifecycleRecord:
        return _report(
            (
                _issue(
                    "lifecycle_record",
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    "expected exact RmcEchoLifecycleRecord",
                ),
            )
        )
    issues = _validate_dataclass_shape(record, path="lifecycle_record")
    if not issues:
        issues.extend(_validate_identity(record, path="lifecycle_record"))
    if record.validation_profile_version not in SUPPORTED_VALIDATION_PROFILE_VERSIONS:
        issues.append(
            _issue(
                "lifecycle_record.validation_profile_version",
                RmcEchoValidationCode.PROFILE_VERSION_MISMATCH,
                "unsupported lifecycle validation profile",
            )
        )
    if record.schema_version != SLICE43B_SCHEMA_VERSION:
        issues.append(
            _issue(
                "lifecycle_record.schema_version",
                RmcEchoValidationCode.SCHEMA_VERSION_MISMATCH,
                "unsupported lifecycle schema version",
            )
        )
    if record.automatic_progression:
        issues.append(
            _issue(
                "lifecycle_record.automatic_progression",
                RmcEchoValidationCode.AUTOMATIC_TRANSITION_PROHIBITED,
                "lifecycle progression must be explicit",
            )
        )
    authority_flags = (
        record.structural_validity_grants_echo_authority,
        record.slice42_sources_admitted,
        record.meaning_preservation_comparison_performed,
        record.validation_findings_created,
        record.drift_findings_created,
        record.materiality_decided,
        record.echo_disposition_decided,
        record.rejection_issued,
        record.containment_issued,
        record.expression_repaired,
        record.msm_v1_modified_or_integrated,
        record.bootstrap_integration_enabled,
        record.delivered,
        record.truth_determined,
        record.evidence_validated,
        record.permission_granted,
        record.execution_authorized,
        record.route_or_api_created,
        record.tool_invoked,
        record.action_performed,
        record.memory_accessed_or_written,
        record.filesystem_or_network_accessed,
        record.external_resource_loaded,
        record.model_or_similarity_authority_used,
        record.gp014_superseded,
    )
    if any(authority_flags):
        issues.append(
            _issue(
                "lifecycle_record.authority_flags",
                RmcEchoValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                "lifecycle state may not imply Echo or downstream authority",
            )
        )
    if record.stage is RmcEchoLifecycleStage.RECORD_SEALED:
        if not all(
            (
                record.canonical_serialization_performed,
                record.deterministic_identity_validated,
                record.predecessor_references_validated,
                record.cross_record_consistency_validated,
            )
        ):
            issues.append(
                _issue(
                    "lifecycle_record.stage",
                    RmcEchoValidationCode.LIFECYCLE_STAGE_INVALID,
                    "sealed validation requires all structural checks",
                )
            )
        if record.validation_issue_digest_refs:
            issues.append(
                _issue(
                    "lifecycle_record.validation_issue_digest_refs",
                    RmcEchoValidationCode.LIFECYCLE_STAGE_INVALID,
                    "sealed validation may not retain unresolved issue digests",
                )
            )
    blocked_stages = {
        RmcEchoLifecycleStage.VALIDATION_INCOMPLETE,
        RmcEchoLifecycleStage.UNKNOWN_VERSION_BLOCKED,
        RmcEchoLifecycleStage.MALFORMED_RECORD_BLOCKED,
        RmcEchoLifecycleStage.PREDECESSOR_INVALID_BLOCKED,
        RmcEchoLifecycleStage.DUPLICATE_RECORD_BLOCKED,
        RmcEchoLifecycleStage.IDENTITY_COLLISION_BLOCKED,
    }
    if record.stage in blocked_stages and not record.validation_issue_digest_refs:
        issues.append(
            _issue(
                "lifecycle_record.validation_issue_digest_refs",
                RmcEchoValidationCode.REQUIRED_VALUE_MISSING,
                "blocked lifecycle state requires exact issue digest custody",
            )
        )
    return _report(issues)


def validate_lifecycle_transition_record(
    record: Any,
) -> RmcEchoValidationReport:
    if type(record) is not RmcEchoLifecycleTransitionRecord:
        return _report(
            (
                _issue(
                    "lifecycle_transition",
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    "expected exact RmcEchoLifecycleTransitionRecord",
                ),
            )
        )
    issues = _validate_dataclass_shape(record, path="lifecycle_transition")
    if not issues:
        issues.extend(_validate_identity(record, path="lifecycle_transition"))
    if record.validation_profile_version not in SUPPORTED_VALIDATION_PROFILE_VERSIONS:
        issues.append(
            _issue(
                "lifecycle_transition.validation_profile_version",
                RmcEchoValidationCode.PROFILE_VERSION_MISMATCH,
                "unsupported transition validation profile",
            )
        )
    if record.schema_version != SLICE43B_SCHEMA_VERSION:
        issues.append(
            _issue(
                "lifecycle_transition.schema_version",
                RmcEchoValidationCode.SCHEMA_VERSION_MISMATCH,
                "unsupported transition schema version",
            )
        )
    if record.automatic_transition:
        issues.append(
            _issue(
                "lifecycle_transition.automatic_transition",
                RmcEchoValidationCode.AUTOMATIC_TRANSITION_PROHIBITED,
                "automatic lifecycle transitions are prohibited",
            )
        )
    authority_flags = (
        record.structural_validity_grants_echo_authority,
        record.slice42_source_admission_authorized,
        record.meaning_preservation_comparison_authorized,
        record.drift_classification_authorized,
        record.disposition_decision_authorized,
        record.rejection_or_containment_authorized,
        record.expression_repair_authorized,
        record.msm_v1_integration_authorized,
        record.delivery_authorized,
        record.downstream_authority_authorized,
        record.model_or_similarity_authority_used,
        record.gp014_supersession_authorized,
    )
    if any(authority_flags):
        issues.append(
            _issue(
                "lifecycle_transition.authority_flags",
                RmcEchoValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                "transition may not grant Echo or downstream authority",
            )
        )
    return _report(issues)


def validate_governance_bundle(
    bundle: Any,
) -> RmcEchoValidationReport:
    if type(bundle) is not RmcEchoGovernanceBundle:
        return _report(
            (
                _issue(
                    "governance_bundle",
                    RmcEchoValidationCode.TYPE_MISMATCH,
                    "expected exact RmcEchoGovernanceBundle",
                ),
            )
        )
    issues = _validate_dataclass_shape(bundle, path="governance_bundle")
    runtime_report = validate_runtime_schema_record(bundle.runtime_schema_record)
    issues.extend(runtime_report.issues)
    version_report = validate_version_custody(
        bundle.version_custody,
        runtime_schema_record=bundle.runtime_schema_record,
    )
    issues.extend(version_report.issues)
    for index, lifecycle_record in enumerate(bundle.lifecycle_records):
        for issue in validate_lifecycle_record(lifecycle_record).issues:
            issues.append(
                _issue(
                    f"lifecycle_records[{index}].{issue.path}",
                    issue.code,
                    issue.detail,
                )
            )
    for index, transition in enumerate(bundle.lifecycle_transitions):
        for issue in validate_lifecycle_transition_record(transition).issues:
            issues.append(
                _issue(
                    f"lifecycle_transitions[{index}].{issue.path}",
                    issue.code,
                    issue.detail,
                )
            )
    try:
        expected_digest = expected_bundle_digest(bundle)
        expected_id = expected_bundle_id(bundle)
    except RmcEchoCanonicalizationError as error:
        issues.append(
            _issue(
                "governance_bundle",
                RmcEchoValidationCode.CANONICAL_DIGEST_MISMATCH,
                str(error),
            )
        )
    else:
        if bundle.bundle_digest != expected_digest:
            issues.append(
                _issue(
                    "governance_bundle.bundle_digest",
                    RmcEchoValidationCode.CANONICAL_DIGEST_MISMATCH,
                    f"expected {expected_digest}",
                )
            )
        if bundle.bundle_id != expected_id:
            issues.append(
                _issue(
                    "governance_bundle.bundle_id",
                    RmcEchoValidationCode.IDENTITY_MISMATCH,
                    f"expected {expected_id}",
                )
            )
    if bundle.version_custody.runtime_schema_record_id != (
        bundle.runtime_schema_record.rmc_echo_runtime_schema_record_id
    ):
        issues.append(
            _issue(
                "governance_bundle.version_custody",
                RmcEchoValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "version custody must govern the exact runtime record",
            )
        )
    if not bundle.lifecycle_records:
        issues.append(
            _issue(
                "governance_bundle.lifecycle_records",
                RmcEchoValidationCode.REQUIRED_VALUE_MISSING,
                "at least one lifecycle record is required",
            )
        )
    else:
        runtime_id = bundle.runtime_schema_record.rmc_echo_runtime_schema_record_id
        version_id = bundle.version_custody.custody_id
        for index, lifecycle_record in enumerate(bundle.lifecycle_records):
            if lifecycle_record.runtime_schema_record_id != runtime_id:
                issues.append(
                    _issue(
                        f"lifecycle_records[{index}].runtime_schema_record_id",
                        RmcEchoValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                        "lifecycle record governs the wrong runtime record",
                    )
                )
            if lifecycle_record.version_custody_ref != version_id:
                issues.append(
                    _issue(
                        f"lifecycle_records[{index}].version_custody_ref",
                        RmcEchoValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                        "lifecycle record uses the wrong version custody",
                    )
                )
        ids = tuple(item.lifecycle_record_id for item in bundle.lifecycle_records)
        if len(ids) != len(set(ids)):
            issues.append(
                _issue(
                    "governance_bundle.lifecycle_records",
                    RmcEchoValidationCode.DUPLICATE_RECORD_ID,
                    "lifecycle record identities must be unique",
                )
            )
        if bundle.lifecycle_records[0].stage is not RmcEchoLifecycleStage.SCHEMA_DECLARED:
            issues.append(
                _issue(
                    "governance_bundle.lifecycle_records[0].stage",
                    RmcEchoValidationCode.LIFECYCLE_STAGE_INVALID,
                    "successful chain must begin at schema_declared",
                )
            )
        if bundle.lifecycle_records[-1].stage is not RmcEchoLifecycleStage.RECORD_SEALED:
            issues.append(
                _issue(
                    "governance_bundle.lifecycle_records[-1].stage",
                    RmcEchoValidationCode.LIFECYCLE_STAGE_INVALID,
                    "successful chain must end at record_sealed",
                )
            )
        if len(bundle.lifecycle_transitions) != len(bundle.lifecycle_records) - 1:
            issues.append(
                _issue(
                    "governance_bundle.lifecycle_transitions",
                    RmcEchoValidationCode.PREDECESSOR_REFERENCE_MISMATCH,
                    "successful chain requires exactly one transition between adjacent records",
                )
            )
        else:
            from .lifecycle import evaluate_lifecycle_transition
            for index, transition in enumerate(bundle.lifecycle_transitions):
                source = bundle.lifecycle_records[index]
                target = bundle.lifecycle_records[index + 1]
                decision = evaluate_lifecycle_transition(
                    source,
                    target,
                    transition,
                    bundle=None,
                )
                for issue in decision.issues:
                    issues.append(
                        _issue(
                            f"lifecycle_transitions[{index}].{issue.path}",
                            issue.code,
                            issue.detail,
                        )
                    )
    required_true = (
        bundle.validation_only,
        bundle.immutable_successor_records,
        bundle.exact_predecessor_references_required,
        bundle.duplicate_and_collision_rejection_required,
        bundle.unknown_version_rejection_required,
        bundle.malformed_record_rejection_required,
        bundle.cross_record_consistency_required,
    )
    if not all(required_true):
        issues.append(
            _issue(
                "governance_bundle.validation_contract",
                RmcEchoValidationCode.REQUIRED_VALUE_MISSING,
                "all validation-only requirements must be explicit",
            )
        )
    authority_flags = (
        bundle.structural_validity_grants_echo_authority,
        bundle.slice42_sources_admitted,
        bundle.meaning_preservation_comparison_performed,
        bundle.validation_findings_created,
        bundle.drift_findings_created,
        bundle.materiality_decided,
        bundle.echo_disposition_decided,
        bundle.rejection_issued,
        bundle.containment_issued,
        bundle.expression_repaired,
        bundle.msm_v1_modified_or_integrated,
        bundle.bootstrap_integration_enabled,
        bundle.delivered,
        bundle.truth_determined,
        bundle.evidence_validated,
        bundle.permission_granted,
        bundle.execution_authorized,
        bundle.route_or_api_created,
        bundle.tool_invoked,
        bundle.action_performed,
        bundle.memory_accessed_or_written,
        bundle.filesystem_or_network_accessed,
        bundle.external_resource_loaded,
        bundle.model_or_similarity_authority_used,
        bundle.gp014_superseded,
    )
    if any(authority_flags):
        issues.append(
            _issue(
                "governance_bundle.authority_flags",
                RmcEchoValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
                "valid governance bundle may not grant Echo or downstream authority",
            )
        )
    if bundle.schema_version != SLICE43B_SCHEMA_VERSION:
        issues.append(
            _issue(
                "governance_bundle.schema_version",
                RmcEchoValidationCode.SCHEMA_VERSION_MISMATCH,
                "unsupported governance schema version",
            )
        )
    if bundle.profile_version != VALIDATION_PROFILE_VERSION:
        issues.append(
            _issue(
                "governance_bundle.profile_version",
                RmcEchoValidationCode.PROFILE_VERSION_MISMATCH,
                "unsupported governance profile version",
            )
        )
    return _report(issues)


def assert_valid_runtime_schema_record(
    record: RmcEchoRuntimeSchemaRecord,
) -> RmcEchoRuntimeSchemaRecord:
    report = validate_runtime_schema_record(record)
    if not report.ok:
        raise RmcEchoValidationError(report)
    return record


def assert_valid_version_custody(
    custody: RmcEchoVersionCustody,
    *,
    runtime_schema_record: RmcEchoRuntimeSchemaRecord | None = None,
) -> RmcEchoVersionCustody:
    report = validate_version_custody(
        custody,
        runtime_schema_record=runtime_schema_record,
    )
    if not report.ok:
        raise RmcEchoValidationError(report)
    return custody


def assert_valid_governance_bundle(
    bundle: RmcEchoGovernanceBundle,
) -> RmcEchoGovernanceBundle:
    report = validate_governance_bundle(bundle)
    if not report.ok:
        raise RmcEchoValidationError(report)
    return bundle


__all__ = (
    "CORE_RECORD_TYPES",
    "assert_valid_governance_bundle",
    "assert_valid_runtime_schema_record",
    "assert_valid_version_custody",
    "expected_predecessor_references",
    "expected_record_schema_versions",
    "validate_field_pairs",
    "validate_governance_bundle",
    "validate_identity_collection",
    "validate_lifecycle_record",
    "validate_lifecycle_transition_record",
    "validate_record",
    "validate_runtime_schema_record",
    "validate_version_custody",
)
