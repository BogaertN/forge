"""Strict deterministic Slice 42B validation and consistency law."""

from __future__ import annotations

from dataclasses import fields
from enum import Enum
import re
from typing import Any, Callable, Iterable

from ..authority import (
    PERMANENT_OUTWARD_EXPRESSION_BOUNDARIES,
    PROHIBITED_AUTHORITY_PATHS,
)
from ..identity import (
    EXPRESSION_ELIGIBILITY_STATUS_SCHEMA_ID,
    EXPRESSION_PLAN_BOUNDARY_SCHEMA_ID,
    EXPRESSION_PRESERVATION_OBLIGATION_CUSTODY_SCHEMA_ID,
    EXPRESSION_RECEIPT_BOUNDARY_SCHEMA_ID,
    EXPRESSION_TRACE_BOUNDARY_SCHEMA_ID,
    GOVERNED_OUTWARD_MEANING_BOUNDARY_SCHEMA_ID,
    OUTWARD_EXPRESSION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
    OUTWARD_EXPRESSION_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
    REALIZED_EXPRESSION_BOUNDARY_SCHEMA_ID,
    SCHEMA_VERSION,
    SELECTED_MEANING_EXPRESSION_SOURCE_CUSTODY_SCHEMA_ID,
    SPEC_ID,
    SPEC_VERSION,
)
from ..schema import (
    ExpressionEligibilityCustodyState,
    ExpressionEligibilityStatusRecord,
    ExpressionPlanBoundaryRecord,
    ExpressionPlanCustodyState,
    ExpressionPreservationObligationCustodyRecord,
    ExpressionReceiptBoundaryRecord,
    ExpressionTraceBoundaryRecord,
    GovernedOutwardMeaningBoundaryRecord,
    OutwardExpressionAuthorityRequirementRecord,
    OutwardExpressionRuntimeSchemaRecord,
    OutwardMeaningCustodyState,
    RealizedExpressionBoundaryRecord,
    RealizedExpressionCustodyState,
    SelectedMeaningExpressionSourceCustodyRecord,
)
from .canonical import (
    CANONICAL_FIELD_ORDERS,
    OutwardExpressionCanonicalizationError,
    canonical_record_bytes,
    canonicalize_field_pairs,
)
from .identity import (
    expected_bundle_digest,
    expected_bundle_id,
    expected_lifecycle_record_id,
    expected_lifecycle_transition_id,
    expected_record_id,
    expected_version_custody_id,
    identity_field,
)
from .schema import (
    CANONICAL_FIELD_ORDER_VERSION,
    DIGEST_ALGORITHM,
    SLICE42B_ACCEPTED_PARENT_HEAD,
    SLICE42B_ACCEPTED_PARENT_SUBJECT,
    SLICE42B_ACCEPTED_PARENT_TREE,
    SLICE42B_SCHEMA_VERSION,
    SUPPORTED_RUNTIME_SCHEMA_VERSIONS,
    SUPPORTED_RUNTIME_SPEC_VERSIONS,
    SUPPORTED_VALIDATION_PROFILE_VERSIONS,
    VALIDATION_PROFILE_VERSION,
    OutwardExpressionGovernanceBundle,
    OutwardExpressionLifecycleRecord,
    OutwardExpressionLifecycleStage,
    OutwardExpressionLifecycleTransitionKind,
    OutwardExpressionLifecycleTransitionRecord,
    OutwardExpressionValidationCode,
    OutwardExpressionValidationError,
    OutwardExpressionValidationIssue,
    OutwardExpressionValidationReport,
    OutwardExpressionVersionCustody,
)


_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:+/-]*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

CORE_RECORD_TYPES = (
    SelectedMeaningExpressionSourceCustodyRecord,
    OutwardExpressionAuthorityRequirementRecord,
    ExpressionPreservationObligationCustodyRecord,
    ExpressionEligibilityStatusRecord,
    GovernedOutwardMeaningBoundaryRecord,
    ExpressionPlanBoundaryRecord,
    RealizedExpressionBoundaryRecord,
    ExpressionTraceBoundaryRecord,
    ExpressionReceiptBoundaryRecord,
    OutwardExpressionRuntimeSchemaRecord,
)

_STRING_IDENTIFIER_FIELDS: dict[type[Any], tuple[str, ...]] = {
    SelectedMeaningExpressionSourceCustodyRecord: (
        "source_custody_id",
        "slice41e_integration_input_ref",
        "slice41e_integration_result_ref",
        "slice41e_integration_receipt_ref",
        "source_manifest_ref",
        "successor_manifest_ref",
        "selected_governed_meaning_ref",
        "selected_candidate_ref",
        "selection_authority_reference_ref",
        "selection_eligibility_result_ref",
        "selection_decision_ref",
        "selection_trace_ref",
        "selection_receipt_ref",
        "content_proof_ref",
        "slice41f_acceptance_record_ref",
    ),
    OutwardExpressionAuthorityRequirementRecord: (
        "authority_requirement_id",
        "selected_meaning_source_custody_ref",
        "required_outward_expression_authority_ref",
    ),
    ExpressionPreservationObligationCustodyRecord: (
        "obligation_custody_id",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_requirement_ref",
    ),
    ExpressionEligibilityStatusRecord: (
        "expression_eligibility_status_id",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_requirement_ref",
        "preservation_obligation_custody_ref",
    ),
    GovernedOutwardMeaningBoundaryRecord: (
        "governed_outward_meaning_boundary_id",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_requirement_ref",
        "expression_eligibility_status_ref",
        "preservation_obligation_custody_ref",
    ),
    ExpressionPlanBoundaryRecord: (
        "expression_plan_boundary_id",
        "governed_outward_meaning_boundary_ref",
        "preservation_obligation_custody_ref",
    ),
    RealizedExpressionBoundaryRecord: (
        "realized_expression_boundary_id",
        "expression_plan_boundary_ref",
        "governed_outward_meaning_boundary_ref",
        "preservation_obligation_custody_ref",
    ),
    ExpressionTraceBoundaryRecord: (
        "expression_trace_boundary_id",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_requirement_ref",
        "preservation_obligation_custody_ref",
        "expression_eligibility_status_ref",
        "governed_outward_meaning_boundary_ref",
        "expression_plan_boundary_ref",
        "realized_expression_boundary_ref",
    ),
    ExpressionReceiptBoundaryRecord: (
        "expression_receipt_boundary_id",
        "selected_meaning_source_custody_ref",
        "outward_expression_authority_requirement_ref",
        "expression_eligibility_status_ref",
        "governed_outward_meaning_boundary_ref",
        "expression_plan_boundary_ref",
        "realized_expression_boundary_ref",
        "expression_trace_boundary_ref",
    ),
    OutwardExpressionRuntimeSchemaRecord: (
        "outward_expression_runtime_schema_record_id",
    ),
}

_TUPLE_IDENTIFIER_FIELDS: dict[type[Any], tuple[str, ...]] = {
    SelectedMeaningExpressionSourceCustodyRecord: (
        "preserved_alternative_refs",
        "unresolved_alternative_refs",
        "ambiguity_ancestry_refs",
        "clarification_ancestry_refs",
        "inherited_limitation_refs",
        "blocked_consequence_refs",
        "refusal_relevant_refs",
        "authority_sensitive_distinction_refs",
        "preservation_class_refs",
    ),
    OutwardExpressionAuthorityRequirementRecord: (
        "required_authority_scope_refs",
        "required_expression_purpose_refs",
        "required_predecessor_receipt_refs",
        "required_version_refs",
        "missing_authority_refs",
    ),
    ExpressionPreservationObligationCustodyRecord: (
        "active_scope_refs",
        "certainty_level_refs",
        "evidence_status_refs",
        "inherited_limitation_refs",
        "required_caveat_refs",
        "refusal_relevant_boundary_refs",
        "unresolved_condition_refs",
        "memory_authority_refs",
        "external_resource_status_refs",
        "delivery_authority_refs",
        "ambiguity_refs",
        "privacy_identity_boundary_refs",
        "preservation_class_refs",
    ),
    ExpressionEligibilityStatusRecord: ("status_reason_refs",),
    GovernedOutwardMeaningBoundaryRecord: (
        "permitted_claim_refs",
        "required_qualification_refs",
        "prohibited_enlargement_refs",
        "external_dependency_refs",
        "ancestry_refs",
    ),
    ExpressionPlanBoundaryRecord: (
        "ordering_constraint_refs",
        "modifier_custody_refs",
        "qualification_custody_refs",
        "caveat_custody_refs",
        "refusal_custody_refs",
        "unresolved_custody_refs",
        "ancestry_refs",
    ),
    RealizedExpressionBoundaryRecord: (
        "admitted_realization_rule_refs",
        "controlled_resource_refs",
    ),
    ExpressionTraceBoundaryRecord: (
        "predecessor_trace_refs",
        "predecessor_receipt_refs",
    ),
    ExpressionReceiptBoundaryRecord: (
        "required_law_refs",
        "prohibited_consequence_refs",
    ),
    OutwardExpressionRuntimeSchemaRecord: (
        "permanent_boundaries",
        "prohibited_authority_paths",
    ),
}

_OPTIONAL_IDENTIFIER_FIELDS: dict[type[Any], tuple[str, ...]] = {
    ExpressionEligibilityStatusRecord: ("later_evaluator_ref",),
    GovernedOutwardMeaningBoundaryRecord: ("later_constructor_ref",),
    ExpressionPlanBoundaryRecord: ("later_planner_ref",),
    RealizedExpressionBoundaryRecord: (
        "expression_candidate_ref",
        "realization_trace_ref",
        "realization_receipt_ref",
        "later_realizer_ref",
    ),
}

_PAIR_VERSION_FIELDS: dict[type[Any], tuple[str, ...]] = {
    ExpressionTraceBoundaryRecord: (
        "authority_version_refs",
        "schema_version_refs",
    ),
}

_ENUM_FIELDS: dict[type[Any], tuple[tuple[str, type[Enum]], ...]] = {
    ExpressionEligibilityStatusRecord: (
        ("custody_state", ExpressionEligibilityCustodyState),
    ),
    GovernedOutwardMeaningBoundaryRecord: (
        ("custody_state", OutwardMeaningCustodyState),
    ),
    ExpressionPlanBoundaryRecord: (
        ("custody_state", ExpressionPlanCustodyState),
    ),
    RealizedExpressionBoundaryRecord: (
        ("custody_state", RealizedExpressionCustodyState),
    ),
}

_SCHEMA_IDS: dict[type[Any], str] = {
    SelectedMeaningExpressionSourceCustodyRecord:
        SELECTED_MEANING_EXPRESSION_SOURCE_CUSTODY_SCHEMA_ID,
    OutwardExpressionAuthorityRequirementRecord:
        OUTWARD_EXPRESSION_AUTHORITY_REQUIREMENT_SCHEMA_ID,
    ExpressionPreservationObligationCustodyRecord:
        EXPRESSION_PRESERVATION_OBLIGATION_CUSTODY_SCHEMA_ID,
    ExpressionEligibilityStatusRecord: EXPRESSION_ELIGIBILITY_STATUS_SCHEMA_ID,
    GovernedOutwardMeaningBoundaryRecord:
        GOVERNED_OUTWARD_MEANING_BOUNDARY_SCHEMA_ID,
    ExpressionPlanBoundaryRecord: EXPRESSION_PLAN_BOUNDARY_SCHEMA_ID,
    RealizedExpressionBoundaryRecord: REALIZED_EXPRESSION_BOUNDARY_SCHEMA_ID,
    ExpressionTraceBoundaryRecord: EXPRESSION_TRACE_BOUNDARY_SCHEMA_ID,
    ExpressionReceiptBoundaryRecord: EXPRESSION_RECEIPT_BOUNDARY_SCHEMA_ID,
    OutwardExpressionRuntimeSchemaRecord:
        OUTWARD_EXPRESSION_RUNTIME_SCHEMA_RECORD_SCHEMA_ID,
}

_NESTED_FIELDS: tuple[tuple[str, type[Any]], ...] = (
    ("selected_meaning_source_custody", SelectedMeaningExpressionSourceCustodyRecord),
    ("outward_expression_authority_requirement", OutwardExpressionAuthorityRequirementRecord),
    ("preservation_obligation_custody", ExpressionPreservationObligationCustodyRecord),
    ("expression_eligibility_status", ExpressionEligibilityStatusRecord),
    ("governed_outward_meaning_boundary", GovernedOutwardMeaningBoundaryRecord),
    ("expression_plan_boundary", ExpressionPlanBoundaryRecord),
    ("realized_expression_boundary", RealizedExpressionBoundaryRecord),
    ("expression_trace_boundary", ExpressionTraceBoundaryRecord),
    ("expression_receipt_boundary", ExpressionReceiptBoundaryRecord),
)


def _issue(
    path: str,
    code: OutwardExpressionValidationCode,
    detail: str,
) -> OutwardExpressionValidationIssue:
    return OutwardExpressionValidationIssue(path=path, code=code, detail=detail)


def _report(
    issues: Iterable[OutwardExpressionValidationIssue],
) -> OutwardExpressionValidationReport:
    return OutwardExpressionValidationReport(issues=tuple(sorted(
        issues,
        key=lambda item: (item.path, item.code.value, item.detail),
    )))


def _text(
    value: Any,
    path: str,
    *,
    identifier: bool = True,
) -> list[OutwardExpressionValidationIssue]:
    if type(value) is not str:
        return [_issue(
            path,
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            "expected exact str",
        )]
    if not value or value.strip() != value:
        return [_issue(
            path,
            OutwardExpressionValidationCode.REQUIRED_VALUE_MISSING,
            "non-empty trimmed text required",
        )]
    if identifier and not _IDENTIFIER_RE.fullmatch(value):
        return [_issue(
            path,
            OutwardExpressionValidationCode.INVALID_IDENTIFIER,
            "invalid identifier token",
        )]
    return []


def _version(value: Any, path: str) -> list[OutwardExpressionValidationIssue]:
    if type(value) is not str or not _VERSION_RE.fullmatch(value):
        return [_issue(
            path,
            OutwardExpressionValidationCode.INVALID_VERSION,
            "invalid version token",
        )]
    return []


def _sha256(value: Any, path: str) -> list[OutwardExpressionValidationIssue]:
    if type(value) is not str or not _SHA256_RE.fullmatch(value):
        return [_issue(
            path,
            OutwardExpressionValidationCode.INVALID_SHA256,
            "expected lowercase SHA-256",
        )]
    return []


def _optional_identifier(
    value: Any,
    path: str,
) -> list[OutwardExpressionValidationIssue]:
    if value is None:
        return []
    return _text(value, path)


def _optional_sha256(
    value: Any,
    path: str,
) -> list[OutwardExpressionValidationIssue]:
    if value is None:
        return []
    return _sha256(value, path)


def _identifier_tuple(
    value: Any,
    path: str,
    *,
    allow_empty: bool = True,
) -> list[OutwardExpressionValidationIssue]:
    issues: list[OutwardExpressionValidationIssue] = []
    if type(value) is not tuple:
        return [_issue(
            path,
            OutwardExpressionValidationCode.INVALID_TUPLE,
            "expected exact tuple",
        )]
    if not allow_empty and not value:
        issues.append(_issue(
            path,
            OutwardExpressionValidationCode.REQUIRED_VALUE_MISSING,
            "tuple must not be empty",
        ))
    seen: set[str] = set()
    for index, item in enumerate(value):
        issues.extend(_text(item, f"{path}[{index}]"))
        if type(item) is str:
            if item in seen:
                issues.append(_issue(
                    f"{path}[{index}]",
                    OutwardExpressionValidationCode.DUPLICATE_TUPLE_VALUE,
                    f"duplicate value {item!r}",
                ))
            seen.add(item)
    return issues


def _pair_tuple(
    value: Any,
    path: str,
    *,
    value_validator: Callable[[Any, str], list[OutwardExpressionValidationIssue]],
) -> list[OutwardExpressionValidationIssue]:
    issues: list[OutwardExpressionValidationIssue] = []
    if type(value) is not tuple:
        return [_issue(
            path,
            OutwardExpressionValidationCode.INVALID_TUPLE,
            "expected exact tuple of pairs",
        )]
    keys: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    for index, pair in enumerate(value):
        item_path = f"{path}[{index}]"
        if type(pair) is not tuple or len(pair) != 2:
            issues.append(_issue(
                item_path,
                OutwardExpressionValidationCode.INVALID_TUPLE,
                "expected exact (key, value) pair",
            ))
            continue
        key, item = pair
        issues.extend(_text(key, f"{item_path}[0]"))
        issues.extend(value_validator(item, f"{item_path}[1]"))
        if type(key) is str:
            if key in keys:
                issues.append(_issue(
                    f"{item_path}[0]",
                    OutwardExpressionValidationCode.DUPLICATE_TUPLE_VALUE,
                    f"duplicate key {key!r}",
                ))
            keys.add(key)
        if type(key) is str and type(item) is str:
            normalized = (key, item)
            if normalized in pairs:
                issues.append(_issue(
                    item_path,
                    OutwardExpressionValidationCode.DUPLICATE_TUPLE_VALUE,
                    f"duplicate pair {normalized!r}",
                ))
            pairs.add(normalized)
    return issues


def _plain_text(value: Any, path: str) -> list[OutwardExpressionValidationIssue]:
    return _text(value, path, identifier=False)


def _fixed_dataclass_values(
    record: Any,
    path: str,
) -> list[OutwardExpressionValidationIssue]:
    issues: list[OutwardExpressionValidationIssue] = []
    for item in fields(type(record)):
        if item.init is not False:
            continue
        expected = item.default
        actual = getattr(record, item.name)
        if type(expected) is bool:
            if type(actual) is not bool:
                issues.append(_issue(
                    f"{path}.{item.name}",
                    OutwardExpressionValidationCode.TYPE_MISMATCH,
                    "expected exact bool",
                ))
            elif actual is not expected:
                name = item.name
                if "authority" in name or "authorized" in name:
                    code = OutwardExpressionValidationCode.EXPRESSION_AUTHORITY_PROHIBITED
                elif "eligibility" in name:
                    code = OutwardExpressionValidationCode.ELIGIBILITY_EVALUATION_PROHIBITED
                elif "obligation" in name or "projection" in name:
                    code = OutwardExpressionValidationCode.PRESERVATION_PROJECTION_PROHIBITED
                elif "outward_meaning" in name:
                    code = OutwardExpressionValidationCode.OUTWARD_MEANING_CONSTRUCTION_PROHIBITED
                elif "plan" in name:
                    code = OutwardExpressionValidationCode.EXPRESSION_PLAN_PROHIBITED
                elif any(token in name for token in ("realization", "realized", "text", "candidate")):
                    code = OutwardExpressionValidationCode.SURFACE_REALIZATION_PROHIBITED
                elif "msm" in name:
                    code = OutwardExpressionValidationCode.MSM_INTEGRATION_PROHIBITED
                elif "echo" in name:
                    code = OutwardExpressionValidationCode.ECHO_VALIDATION_PROHIBITED
                else:
                    code = OutwardExpressionValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
                issues.append(_issue(
                    f"{path}.{item.name}",
                    code,
                    f"must remain {expected!r} in Slice 42B",
                ))
    return issues


def _validate_core_record(
    record: Any,
    expected_type: type[Any],
    path: str,
) -> list[OutwardExpressionValidationIssue]:
    if type(record) is not expected_type:
        return [_issue(
            path,
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            f"expected exact {expected_type.__name__}",
        )]

    issues: list[OutwardExpressionValidationIssue] = []
    for name in _STRING_IDENTIFIER_FIELDS.get(expected_type, ()):
        issues.extend(_text(getattr(record, name), f"{path}.{name}"))
    for name in _TUPLE_IDENTIFIER_FIELDS.get(expected_type, ()):
        issues.extend(_identifier_tuple(getattr(record, name), f"{path}.{name}"))
    for name in _OPTIONAL_IDENTIFIER_FIELDS.get(expected_type, ()):
        issues.extend(_optional_identifier(getattr(record, name), f"{path}.{name}"))
    for name in _PAIR_VERSION_FIELDS.get(expected_type, ()):
        issues.extend(_pair_tuple(
            getattr(record, name),
            f"{path}.{name}",
            value_validator=_version,
        ))
    for name, enum_type in _ENUM_FIELDS.get(expected_type, ()):
        value = getattr(record, name)
        if type(value) is not enum_type:
            issues.append(_issue(
                f"{path}.{name}",
                OutwardExpressionValidationCode.INVALID_ENUM,
                f"expected exact {enum_type.__name__}",
            ))

    if expected_type is ExpressionReceiptBoundaryRecord:
        issues.extend(_plain_text(record.audit_note, f"{path}.audit_note"))
    if expected_type is RealizedExpressionBoundaryRecord:
        issues.extend(_optional_sha256(
            record.realized_text_sha256,
            f"{path}.realized_text_sha256",
        ))

    if record.schema_version != SCHEMA_VERSION:
        issues.append(_issue(
            f"{path}.schema_version",
            OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SCHEMA_VERSION!r}",
        ))
    if record.schema_id != _SCHEMA_IDS[expected_type]:
        issues.append(_issue(
            f"{path}.schema_id",
            OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {_SCHEMA_IDS[expected_type]!r}",
        ))
    if expected_type is OutwardExpressionRuntimeSchemaRecord:
        if record.spec_id != SPEC_ID:
            issues.append(_issue(
                f"{path}.spec_id",
                OutwardExpressionValidationCode.SPEC_VERSION_MISMATCH,
                f"expected {SPEC_ID!r}",
            ))
        if record.spec_version != SPEC_VERSION:
            issues.append(_issue(
                f"{path}.spec_version",
                OutwardExpressionValidationCode.SPEC_VERSION_MISMATCH,
                f"expected {SPEC_VERSION!r}",
            ))
        if record.permanent_boundaries != PERMANENT_OUTWARD_EXPRESSION_BOUNDARIES:
            issues.append(_issue(
                f"{path}.permanent_boundaries",
                OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISMATCH,
                "permanent Slice 42A boundaries must be preserved exactly",
            ))
        if record.prohibited_authority_paths != PROHIBITED_AUTHORITY_PATHS:
            issues.append(_issue(
                f"{path}.prohibited_authority_paths",
                OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISMATCH,
                "prohibited Slice 42A authority paths must be preserved exactly",
            ))

    issues.extend(_fixed_dataclass_values(record, path))
    try:
        actual_id = getattr(record, identity_field(expected_type))
        expected_id = expected_record_id(record)
        if actual_id != expected_id:
            issues.append(_issue(
                f"{path}.{identity_field(expected_type)}",
                OutwardExpressionValidationCode.IDENTITY_MISMATCH,
                "deterministic SHA-256 identity mismatch",
            ))
    except Exception as error:
        issues.append(_issue(
            f"{path}.identity",
            OutwardExpressionValidationCode.IDENTITY_MISMATCH,
            str(error),
        ))
    return issues


def validate_field_pairs(
    record_type: type[Any],
    field_pairs: Iterable[tuple[str, Any]],
) -> OutwardExpressionValidationReport:
    if record_type not in CANONICAL_FIELD_ORDERS:
        return _report((_issue(
            "record_type",
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            "unsupported record type",
        ),))
    expected = CANONICAL_FIELD_ORDERS[record_type]
    pairs = tuple(field_pairs)
    issues: list[OutwardExpressionValidationIssue] = []
    names: list[str] = []
    for index, pair in enumerate(pairs):
        if type(pair) is not tuple or len(pair) != 2 or type(pair[0]) is not str:
            issues.append(_issue(
                f"field_pairs[{index}]",
                OutwardExpressionValidationCode.INVALID_TUPLE,
                "expected exact (str, value) pair",
            ))
            continue
        name = pair[0]
        if name in names:
            issues.append(_issue(
                f"field_pairs[{index}]",
                OutwardExpressionValidationCode.DUPLICATE_FIELD,
                f"duplicate field {name!r}",
            ))
        names.append(name)
        if name not in expected:
            issues.append(_issue(
                f"field_pairs[{index}]",
                OutwardExpressionValidationCode.UNKNOWN_FIELD,
                f"unknown field {name!r}",
            ))
    for name in expected:
        if name not in names:
            issues.append(_issue(
                "field_pairs",
                OutwardExpressionValidationCode.MISSING_FIELD,
                f"missing field {name!r}",
            ))
    if tuple(names) != expected and not any(
        issue.code in {
            OutwardExpressionValidationCode.DUPLICATE_FIELD,
            OutwardExpressionValidationCode.UNKNOWN_FIELD,
            OutwardExpressionValidationCode.MISSING_FIELD,
        }
        for issue in issues
    ):
        issues.append(_issue(
            "field_pairs",
            OutwardExpressionValidationCode.FIELD_ORDER_MISMATCH,
            "field order is not canonical",
        ))
    if not issues:
        try:
            canonicalize_field_pairs(record_type, pairs)
        except OutwardExpressionCanonicalizationError as error:
            issues.append(_issue(
                "field_pairs",
                OutwardExpressionValidationCode.FIELD_ORDER_MISMATCH,
                str(error),
            ))
    return _report(issues)


def _individual_validator(expected_type: type[Any]):
    def validate(record: Any) -> OutwardExpressionValidationReport:
        return _report(_validate_core_record(
            record,
            expected_type,
            expected_type.__name__,
        ))
    return validate


validate_source_custody = _individual_validator(
    SelectedMeaningExpressionSourceCustodyRecord
)
validate_authority_requirement = _individual_validator(
    OutwardExpressionAuthorityRequirementRecord
)
validate_preservation_obligation_custody = _individual_validator(
    ExpressionPreservationObligationCustodyRecord
)
validate_expression_eligibility_status = _individual_validator(
    ExpressionEligibilityStatusRecord
)
validate_governed_outward_meaning_boundary = _individual_validator(
    GovernedOutwardMeaningBoundaryRecord
)
validate_expression_plan_boundary = _individual_validator(
    ExpressionPlanBoundaryRecord
)
validate_realized_expression_boundary = _individual_validator(
    RealizedExpressionBoundaryRecord
)
validate_expression_trace_boundary = _individual_validator(
    ExpressionTraceBoundaryRecord
)
validate_expression_receipt_boundary = _individual_validator(
    ExpressionReceiptBoundaryRecord
)


def _identity_records(
    record: OutwardExpressionRuntimeSchemaRecord,
) -> tuple[Any, ...]:
    return tuple(getattr(record, name) for name, _ in _NESTED_FIELDS) + (record,)


def validate_identity_collection(
    records: Iterable[Any],
) -> OutwardExpressionValidationReport:
    issues: list[OutwardExpressionValidationIssue] = []
    observed: dict[str, bytes] = {}
    for index, record in enumerate(tuple(records)):
        try:
            field_name = identity_field(type(record))
            record_id = getattr(record, field_name)
            canonical = canonical_record_bytes(record)
            expected = expected_record_id(record)
        except Exception as error:
            issues.append(_issue(
                f"records[{index}]",
                OutwardExpressionValidationCode.TYPE_MISMATCH,
                str(error),
            ))
            continue
        if record_id != expected:
            issues.append(_issue(
                f"records[{index}].{field_name}",
                OutwardExpressionValidationCode.IDENTITY_MISMATCH,
                "deterministic SHA-256 identity mismatch",
            ))
        if record_id in observed:
            code = (
                OutwardExpressionValidationCode.DUPLICATE_RECORD_ID
                if observed[record_id] == canonical
                else OutwardExpressionValidationCode.IDENTITY_COLLISION
            )
            issues.append(_issue(
                f"records[{index}].{field_name}",
                code,
                "record identity is not unique in the supplied collection",
            ))
        else:
            observed[record_id] = canonical
    return _report(issues)


def _expect_equal(
    issues: list[OutwardExpressionValidationIssue],
    path: str,
    actual: Any,
    expected: Any,
    detail: str,
) -> None:
    if actual != expected:
        issues.append(_issue(
            path,
            OutwardExpressionValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            detail,
        ))


def _expect_subset(
    issues: list[OutwardExpressionValidationIssue],
    path: str,
    required: tuple[str, ...],
    actual: tuple[str, ...],
    detail: str,
) -> None:
    missing = tuple(item for item in required if item not in actual)
    if missing:
        issues.append(_issue(
            path,
            OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISSING,
            detail + ": " + ", ".join(missing),
        ))


def validate_runtime_schema_record(
    record: Any,
) -> OutwardExpressionValidationReport:
    if type(record) is not OutwardExpressionRuntimeSchemaRecord:
        return _report((_issue(
            "record",
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            "expected exact OutwardExpressionRuntimeSchemaRecord",
        ),))

    issues = _validate_core_record(
        record,
        OutwardExpressionRuntimeSchemaRecord,
        "record",
    )
    for name, expected_type in _NESTED_FIELDS:
        issues.extend(_validate_core_record(
            getattr(record, name),
            expected_type,
            f"record.{name}",
        ))

    source = record.selected_meaning_source_custody
    authority = record.outward_expression_authority_requirement
    obligations = record.preservation_obligation_custody
    eligibility = record.expression_eligibility_status
    outward = record.governed_outward_meaning_boundary
    plan = record.expression_plan_boundary
    realized = record.realized_expression_boundary
    trace = record.expression_trace_boundary
    receipt = record.expression_receipt_boundary

    _expect_equal(issues, "record.outward_expression_authority_requirement.selected_meaning_source_custody_ref", authority.selected_meaning_source_custody_ref, source.source_custody_id, "authority requirement source reference mismatch")
    _expect_equal(issues, "record.preservation_obligation_custody.selected_meaning_source_custody_ref", obligations.selected_meaning_source_custody_ref, source.source_custody_id, "obligation source reference mismatch")
    _expect_equal(issues, "record.preservation_obligation_custody.outward_expression_authority_requirement_ref", obligations.outward_expression_authority_requirement_ref, authority.authority_requirement_id, "obligation authority reference mismatch")
    _expect_equal(issues, "record.expression_eligibility_status.selected_meaning_source_custody_ref", eligibility.selected_meaning_source_custody_ref, source.source_custody_id, "eligibility source reference mismatch")
    _expect_equal(issues, "record.expression_eligibility_status.outward_expression_authority_requirement_ref", eligibility.outward_expression_authority_requirement_ref, authority.authority_requirement_id, "eligibility authority reference mismatch")
    _expect_equal(issues, "record.expression_eligibility_status.preservation_obligation_custody_ref", eligibility.preservation_obligation_custody_ref, obligations.obligation_custody_id, "eligibility obligation reference mismatch")

    for path, actual, expected, detail in (
        ("record.governed_outward_meaning_boundary.selected_meaning_source_custody_ref", outward.selected_meaning_source_custody_ref, source.source_custody_id, "outward boundary source mismatch"),
        ("record.governed_outward_meaning_boundary.outward_expression_authority_requirement_ref", outward.outward_expression_authority_requirement_ref, authority.authority_requirement_id, "outward boundary authority mismatch"),
        ("record.governed_outward_meaning_boundary.expression_eligibility_status_ref", outward.expression_eligibility_status_ref, eligibility.expression_eligibility_status_id, "outward boundary eligibility mismatch"),
        ("record.governed_outward_meaning_boundary.preservation_obligation_custody_ref", outward.preservation_obligation_custody_ref, obligations.obligation_custody_id, "outward boundary obligation mismatch"),
        ("record.expression_plan_boundary.governed_outward_meaning_boundary_ref", plan.governed_outward_meaning_boundary_ref, outward.governed_outward_meaning_boundary_id, "plan outward boundary mismatch"),
        ("record.expression_plan_boundary.preservation_obligation_custody_ref", plan.preservation_obligation_custody_ref, obligations.obligation_custody_id, "plan obligation mismatch"),
        ("record.realized_expression_boundary.expression_plan_boundary_ref", realized.expression_plan_boundary_ref, plan.expression_plan_boundary_id, "realized boundary plan mismatch"),
        ("record.realized_expression_boundary.governed_outward_meaning_boundary_ref", realized.governed_outward_meaning_boundary_ref, outward.governed_outward_meaning_boundary_id, "realized boundary outward mismatch"),
        ("record.realized_expression_boundary.preservation_obligation_custody_ref", realized.preservation_obligation_custody_ref, obligations.obligation_custody_id, "realized boundary obligation mismatch"),
    ):
        _expect_equal(issues, path, actual, expected, detail)

    trace_expectations = (
        (trace.selected_meaning_source_custody_ref, source.source_custody_id, "source"),
        (trace.outward_expression_authority_requirement_ref, authority.authority_requirement_id, "authority"),
        (trace.preservation_obligation_custody_ref, obligations.obligation_custody_id, "obligation"),
        (trace.expression_eligibility_status_ref, eligibility.expression_eligibility_status_id, "eligibility"),
        (trace.governed_outward_meaning_boundary_ref, outward.governed_outward_meaning_boundary_id, "outward boundary"),
        (trace.expression_plan_boundary_ref, plan.expression_plan_boundary_id, "plan"),
        (trace.realized_expression_boundary_ref, realized.realized_expression_boundary_id, "realized boundary"),
    )
    for actual, expected, label in trace_expectations:
        _expect_equal(issues, f"record.expression_trace_boundary.{label.replace(' ', '_')}_ref", actual, expected, f"trace {label} reference mismatch")

    receipt_expectations = (
        (receipt.selected_meaning_source_custody_ref, source.source_custody_id, "source"),
        (receipt.outward_expression_authority_requirement_ref, authority.authority_requirement_id, "authority"),
        (receipt.expression_eligibility_status_ref, eligibility.expression_eligibility_status_id, "eligibility"),
        (receipt.governed_outward_meaning_boundary_ref, outward.governed_outward_meaning_boundary_id, "outward boundary"),
        (receipt.expression_plan_boundary_ref, plan.expression_plan_boundary_id, "plan"),
        (receipt.realized_expression_boundary_ref, realized.realized_expression_boundary_id, "realized boundary"),
        (receipt.expression_trace_boundary_ref, trace.expression_trace_boundary_id, "trace"),
    )
    for actual, expected, label in receipt_expectations:
        _expect_equal(issues, f"record.expression_receipt_boundary.{label.replace(' ', '_')}_ref", actual, expected, f"receipt {label} reference mismatch")

    _expect_subset(issues, "record.outward_expression_authority_requirement.required_predecessor_receipt_refs", (source.slice41e_integration_receipt_ref, source.selection_receipt_ref), authority.required_predecessor_receipt_refs, "required predecessor receipt omitted")
    if authority.required_outward_expression_authority_ref not in authority.missing_authority_refs:
        issues.append(_issue(
            "record.outward_expression_authority_requirement.missing_authority_refs",
            OutwardExpressionValidationCode.EXPRESSION_AUTHORITY_PROHIBITED,
            "Slice 42B must preserve the required authority as missing",
        ))
    _expect_subset(issues, "record.preservation_obligation_custody.inherited_limitation_refs", source.inherited_limitation_refs, obligations.inherited_limitation_refs, "inherited limitation custody lost")
    _expect_subset(issues, "record.preservation_obligation_custody.refusal_relevant_boundary_refs", source.refusal_relevant_refs, obligations.refusal_relevant_boundary_refs, "refusal-relevant custody lost")
    _expect_subset(issues, "record.preservation_obligation_custody.unresolved_condition_refs", source.unresolved_alternative_refs, obligations.unresolved_condition_refs, "unresolved custody lost")
    _expect_subset(issues, "record.preservation_obligation_custody.ambiguity_refs", source.ambiguity_ancestry_refs, obligations.ambiguity_refs, "ambiguity custody lost")
    _expect_subset(issues, "record.preservation_obligation_custody.preservation_class_refs", source.preservation_class_refs, obligations.preservation_class_refs, "preservation class custody lost")
    _expect_subset(issues, "record.governed_outward_meaning_boundary.required_qualification_refs", obligations.required_caveat_refs, outward.required_qualification_refs, "required caveat omitted from outward boundary")
    _expect_subset(issues, "record.expression_plan_boundary.qualification_custody_refs", outward.required_qualification_refs, plan.qualification_custody_refs, "qualification custody omitted from plan boundary")
    _expect_subset(issues, "record.expression_plan_boundary.caveat_custody_refs", obligations.required_caveat_refs, plan.caveat_custody_refs, "caveat custody omitted from plan boundary")
    _expect_subset(issues, "record.expression_plan_boundary.refusal_custody_refs", obligations.refusal_relevant_boundary_refs, plan.refusal_custody_refs, "refusal custody omitted from plan boundary")
    _expect_subset(issues, "record.expression_plan_boundary.unresolved_custody_refs", obligations.unresolved_condition_refs, plan.unresolved_custody_refs, "unresolved custody omitted from plan boundary")
    _expect_subset(issues, "record.expression_trace_boundary.predecessor_trace_refs", (source.selection_trace_ref,), trace.predecessor_trace_refs, "selected-meaning trace ancestry omitted")
    _expect_subset(issues, "record.expression_trace_boundary.predecessor_receipt_refs", (source.slice41e_integration_receipt_ref, source.selection_receipt_ref), trace.predecessor_receipt_refs, "selected-meaning receipt ancestry omitted")

    if receipt.prohibited_consequence_refs != PROHIBITED_AUTHORITY_PATHS:
        issues.append(_issue(
            "record.expression_receipt_boundary.prohibited_consequence_refs",
            OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISMATCH,
            "receipt must preserve all prohibited authority consequences exactly",
        ))

    issues.extend(validate_identity_collection(_identity_records(record)).issues)
    return _report(issues)


def expected_record_schema_versions(
    record: OutwardExpressionRuntimeSchemaRecord,
) -> tuple[tuple[str, str], ...]:
    versions = {
        item.schema_id: item.schema_version
        for item in _identity_records(record)
    }
    return tuple(sorted(versions.items()))


def expected_predecessor_references(
    record: OutwardExpressionRuntimeSchemaRecord,
) -> tuple[tuple[str, str], ...]:
    source = record.selected_meaning_source_custody
    return tuple(sorted((
        ("accepted_parent_head", SLICE42B_ACCEPTED_PARENT_HEAD),
        ("accepted_parent_tree", SLICE42B_ACCEPTED_PARENT_TREE),
        ("slice41e_integration_input", source.slice41e_integration_input_ref),
        ("slice41e_integration_result", source.slice41e_integration_result_ref),
        ("slice41e_integration_receipt", source.slice41e_integration_receipt_ref),
        ("source_manifest", source.source_manifest_ref),
        ("successor_manifest", source.successor_manifest_ref),
        ("selected_governed_meaning", source.selected_governed_meaning_ref),
        ("selected_candidate", source.selected_candidate_ref),
        ("selection_authority_reference", source.selection_authority_reference_ref),
        ("selection_eligibility_result", source.selection_eligibility_result_ref),
        ("selection_decision", source.selection_decision_ref),
        ("selection_trace", source.selection_trace_ref),
        ("selection_receipt", source.selection_receipt_ref),
        ("content_proof", source.content_proof_ref),
        ("slice41f_acceptance", source.slice41f_acceptance_record_ref),
        ("source_custody", source.source_custody_id),
        ("authority_requirement", record.outward_expression_authority_requirement.authority_requirement_id),
        ("preservation_obligation_custody", record.preservation_obligation_custody.obligation_custody_id),
        ("expression_eligibility_status", record.expression_eligibility_status.expression_eligibility_status_id),
        ("governed_outward_meaning_boundary", record.governed_outward_meaning_boundary.governed_outward_meaning_boundary_id),
        ("expression_plan_boundary", record.expression_plan_boundary.expression_plan_boundary_id),
        ("realized_expression_boundary", record.realized_expression_boundary.realized_expression_boundary_id),
        ("expression_trace_boundary", record.expression_trace_boundary.expression_trace_boundary_id),
        ("expression_receipt_boundary", record.expression_receipt_boundary.expression_receipt_boundary_id),
    )))


def validate_version_custody(
    record: Any,
    *,
    runtime_record: OutwardExpressionRuntimeSchemaRecord | None = None,
) -> OutwardExpressionValidationReport:
    if type(record) is not OutwardExpressionVersionCustody:
        return _report((_issue(
            "version_custody",
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            "expected exact OutwardExpressionVersionCustody",
        ),))
    issues: list[OutwardExpressionValidationIssue] = []
    identifier_fields = (
        "custody_id",
        "runtime_schema_record_id",
        "runtime_schema_id",
        "runtime_spec_id",
        "accepted_parent_head",
        "accepted_parent_tree",
        "canonical_field_order_version",
        "digest_algorithm",
        "governance_schema_version",
    )
    version_fields = (
        "runtime_schema_version",
        "runtime_spec_version",
        "validation_profile_version",
    )
    for name in identifier_fields:
        issues.extend(_text(getattr(record, name), f"version_custody.{name}"))
    for name in version_fields:
        issues.extend(_version(getattr(record, name), f"version_custody.{name}"))
    issues.extend(_plain_text(
        record.accepted_parent_subject,
        "version_custody.accepted_parent_subject",
    ))
    issues.extend(_pair_tuple(
        record.record_schema_versions,
        "version_custody.record_schema_versions",
        value_validator=_version,
    ))
    issues.extend(_pair_tuple(
        record.predecessor_references,
        "version_custody.predecessor_references",
        value_validator=_plain_text,
    ))

    if record.runtime_schema_version not in SUPPORTED_RUNTIME_SCHEMA_VERSIONS:
        issues.append(_issue(
            "version_custody.runtime_schema_version",
            OutwardExpressionValidationCode.UNKNOWN_VERSION,
            "runtime schema version is not admitted",
        ))
    if record.runtime_spec_version not in SUPPORTED_RUNTIME_SPEC_VERSIONS:
        issues.append(_issue(
            "version_custody.runtime_spec_version",
            OutwardExpressionValidationCode.UNKNOWN_VERSION,
            "runtime specification version is not admitted",
        ))
    if record.validation_profile_version not in SUPPORTED_VALIDATION_PROFILE_VERSIONS:
        issues.append(_issue(
            "version_custody.validation_profile_version",
            OutwardExpressionValidationCode.UNKNOWN_VERSION,
            "validation profile version is not admitted",
        ))

    exacts = (
        (record.runtime_schema_id, OUTWARD_EXPRESSION_RUNTIME_SCHEMA_RECORD_SCHEMA_ID, "runtime_schema_id", OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH),
        (record.runtime_spec_id, SPEC_ID, "runtime_spec_id", OutwardExpressionValidationCode.SPEC_VERSION_MISMATCH),
        (record.accepted_parent_head, SLICE42B_ACCEPTED_PARENT_HEAD, "accepted_parent_head", OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISMATCH),
        (record.accepted_parent_tree, SLICE42B_ACCEPTED_PARENT_TREE, "accepted_parent_tree", OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISMATCH),
        (record.accepted_parent_subject, SLICE42B_ACCEPTED_PARENT_SUBJECT, "accepted_parent_subject", OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISMATCH),
        (record.canonical_field_order_version, CANONICAL_FIELD_ORDER_VERSION, "canonical_field_order_version", OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH),
        (record.digest_algorithm, DIGEST_ALGORITHM, "digest_algorithm", OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH),
        (record.validation_profile_version, VALIDATION_PROFILE_VERSION, "validation_profile_version", OutwardExpressionValidationCode.PROFILE_VERSION_MISMATCH),
        (record.governance_schema_version, SLICE42B_SCHEMA_VERSION, "governance_schema_version", OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH),
    )
    for actual, expected, name, code in exacts:
        if actual != expected:
            issues.append(_issue(
                f"version_custody.{name}",
                code,
                f"expected {expected!r}",
            ))

    if record.non_llm_provenance is not True:
        issues.append(_issue(
            "version_custody.non_llm_provenance",
            OutwardExpressionValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED,
            "must be true",
        ))
    false_fields = tuple(
        item.name
        for item in fields(OutwardExpressionVersionCustody)
        if item.name.endswith("_authorized")
        or item.name in {
            "timestamps_in_identity",
            "randomness_in_identity",
            "process_identity_in_identity",
            "filesystem_state_in_identity",
            "environment_state_in_identity",
            "hash_table_order_in_identity",
            "external_resource_authority",
            "model_embedding_vector_rag_similarity_authority",
            "gp014_supersession_authorized",
        }
    )
    for name in false_fields:
        if getattr(record, name) is not False:
            code = (
                OutwardExpressionValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED
                if name.endswith("_in_identity")
                else OutwardExpressionValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            )
            issues.append(_issue(
                f"version_custody.{name}",
                code,
                "must remain false",
            ))
    try:
        if record.custody_id != expected_version_custody_id(record):
            issues.append(_issue(
                "version_custody.custody_id",
                OutwardExpressionValidationCode.IDENTITY_MISMATCH,
                "deterministic custody identity mismatch",
            ))
    except Exception as error:
        issues.append(_issue(
            "version_custody.custody_id",
            OutwardExpressionValidationCode.IDENTITY_MISMATCH,
            str(error),
        ))

    if runtime_record is not None:
        if type(runtime_record) is not OutwardExpressionRuntimeSchemaRecord:
            issues.append(_issue(
                "runtime_record",
                OutwardExpressionValidationCode.TYPE_MISMATCH,
                "expected exact OutwardExpressionRuntimeSchemaRecord",
            ))
        else:
            if record.runtime_schema_record_id != runtime_record.outward_expression_runtime_schema_record_id:
                issues.append(_issue(
                    "version_custody.runtime_schema_record_id",
                    OutwardExpressionValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "runtime schema record reference mismatch",
                ))
            if record.runtime_schema_version != runtime_record.schema_version:
                issues.append(_issue(
                    "version_custody.runtime_schema_version",
                    OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
                    "runtime schema version does not match runtime record",
                ))
            if record.runtime_schema_id != runtime_record.schema_id:
                issues.append(_issue(
                    "version_custody.runtime_schema_id",
                    OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
                    "runtime schema id does not match runtime record",
                ))
            if record.runtime_spec_id != runtime_record.spec_id:
                issues.append(_issue(
                    "version_custody.runtime_spec_id",
                    OutwardExpressionValidationCode.SPEC_VERSION_MISMATCH,
                    "runtime spec id does not match runtime record",
                ))
            if record.runtime_spec_version != runtime_record.spec_version:
                issues.append(_issue(
                    "version_custody.runtime_spec_version",
                    OutwardExpressionValidationCode.SPEC_VERSION_MISMATCH,
                    "runtime spec version does not match runtime record",
                ))
            if record.record_schema_versions != expected_record_schema_versions(runtime_record):
                issues.append(_issue(
                    "version_custody.record_schema_versions",
                    OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
                    "record schema versions do not match exact runtime records",
                ))
            if record.predecessor_references != expected_predecessor_references(runtime_record):
                issues.append(_issue(
                    "version_custody.predecessor_references",
                    OutwardExpressionValidationCode.PREDECESSOR_REFERENCE_MISMATCH,
                    "predecessor references do not match exact runtime custody",
                ))
    return _report(issues)


def _validate_governance_bool_fields(
    record: Any,
    path: str,
    *,
    true_fields: tuple[str, ...] = (),
) -> list[OutwardExpressionValidationIssue]:
    issues: list[OutwardExpressionValidationIssue] = []
    true_set = set(true_fields)
    for item in fields(type(record)):
        if item.type not in (bool, "bool"):
            continue
        actual = getattr(record, item.name)
        expected = item.name in true_set
        if type(actual) is not bool:
            issues.append(_issue(
                f"{path}.{item.name}",
                OutwardExpressionValidationCode.TYPE_MISMATCH,
                "expected exact bool",
            ))
        elif actual is not expected:
            code = (
                OutwardExpressionValidationCode.NONDETERMINISTIC_INPUT_PROHIBITED
                if "automatic" in item.name
                else OutwardExpressionValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED
            )
            issues.append(_issue(
                f"{path}.{item.name}",
                code,
                f"must remain {expected!r}",
            ))
    return issues


def validate_lifecycle_record(
    record: Any,
) -> OutwardExpressionValidationReport:
    if type(record) is not OutwardExpressionLifecycleRecord:
        return _report((_issue(
            "lifecycle_record",
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            "expected exact OutwardExpressionLifecycleRecord",
        ),))
    issues: list[OutwardExpressionValidationIssue] = []
    for name in (
        "lifecycle_record_id",
        "runtime_schema_record_id",
        "version_custody_ref",
        "schema_version",
    ):
        issues.extend(_text(getattr(record, name), f"lifecycle_record.{name}"))
    issues.extend(_version(
        record.validation_profile_version,
        "lifecycle_record.validation_profile_version",
    ))
    for name in (
        "predecessor_lifecycle_record_ids",
        "predecessor_reference_ids",
        "validation_issue_digest_refs",
        "reason_refs",
    ):
        issues.extend(_identifier_tuple(
            getattr(record, name),
            f"lifecycle_record.{name}",
        ))
    if type(record.stage) is not OutwardExpressionLifecycleStage:
        issues.append(_issue(
            "lifecycle_record.stage",
            OutwardExpressionValidationCode.INVALID_ENUM,
            "expected exact OutwardExpressionLifecycleStage",
        ))
    if record.validation_profile_version != VALIDATION_PROFILE_VERSION:
        issues.append(_issue(
            "lifecycle_record.validation_profile_version",
            OutwardExpressionValidationCode.PROFILE_VERSION_MISMATCH,
            f"expected {VALIDATION_PROFILE_VERSION!r}",
        ))
    if record.schema_version != SLICE42B_SCHEMA_VERSION:
        issues.append(_issue(
            "lifecycle_record.schema_version",
            OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE42B_SCHEMA_VERSION!r}",
        ))
    success_validation_stages = {
        OutwardExpressionLifecycleStage.RECORD_VALIDATED,
        OutwardExpressionLifecycleStage.RECORD_SEALED,
    }
    expected_true_bool_fields: set[str] = set()
    if record.stage in success_validation_stages:
        expected_true_bool_fields.update((
            "canonical_serialization_performed",
            "deterministic_identity_validated",
            "predecessor_references_validated",
            "cross_record_consistency_validated",
        ))
    elif record.stage is OutwardExpressionLifecycleStage.CROSS_RECORD_VALIDATED:
        expected_true_bool_fields.update((
            "predecessor_references_validated",
            "cross_record_consistency_validated",
        ))

    blocked_flag_by_stage = {
        OutwardExpressionLifecycleStage.UNKNOWN_VERSION_BLOCKED: "unknown_version_rejected",
        OutwardExpressionLifecycleStage.MALFORMED_RECORD_BLOCKED: "malformed_record_rejected",
        OutwardExpressionLifecycleStage.DUPLICATE_RECORD_BLOCKED: "duplicate_record_rejected",
        OutwardExpressionLifecycleStage.IDENTITY_COLLISION_BLOCKED: "identity_collision_rejected",
    }
    required_block_flag = blocked_flag_by_stage.get(record.stage)
    if required_block_flag is not None:
        expected_true_bool_fields.add(required_block_flag)

    issues.extend(_validate_governance_bool_fields(
        record,
        "lifecycle_record",
        true_fields=tuple(sorted(expected_true_bool_fields)),
    ))
    try:
        if record.lifecycle_record_id != expected_lifecycle_record_id(record):
            issues.append(_issue(
                "lifecycle_record.lifecycle_record_id",
                OutwardExpressionValidationCode.IDENTITY_MISMATCH,
                "deterministic lifecycle identity mismatch",
            ))
    except Exception as error:
        issues.append(_issue(
            "lifecycle_record.lifecycle_record_id",
            OutwardExpressionValidationCode.IDENTITY_MISMATCH,
            str(error),
        ))
    return _report(issues)


def validate_lifecycle_transition_record(
    record: Any,
) -> OutwardExpressionValidationReport:
    if type(record) is not OutwardExpressionLifecycleTransitionRecord:
        return _report((_issue(
            "transition",
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            "expected exact OutwardExpressionLifecycleTransitionRecord",
        ),))
    issues: list[OutwardExpressionValidationIssue] = []
    for name in (
        "transition_id",
        "runtime_schema_record_id",
        "source_lifecycle_record_id",
        "target_lifecycle_record_id",
        "version_custody_ref",
        "schema_version",
    ):
        issues.extend(_text(getattr(record, name), f"transition.{name}"))
    issues.extend(_version(
        record.validation_profile_version,
        "transition.validation_profile_version",
    ))
    issues.extend(_identifier_tuple(
        record.predecessor_transition_refs,
        "transition.predecessor_transition_refs",
    ))
    issues.extend(_identifier_tuple(
        record.reason_refs,
        "transition.reason_refs",
    ))
    if type(record.from_stage) is not OutwardExpressionLifecycleStage:
        issues.append(_issue(
            "transition.from_stage",
            OutwardExpressionValidationCode.INVALID_ENUM,
            "expected exact OutwardExpressionLifecycleStage",
        ))
    if type(record.to_stage) is not OutwardExpressionLifecycleStage:
        issues.append(_issue(
            "transition.to_stage",
            OutwardExpressionValidationCode.INVALID_ENUM,
            "expected exact OutwardExpressionLifecycleStage",
        ))
    if type(record.transition_kind) is not OutwardExpressionLifecycleTransitionKind:
        issues.append(_issue(
            "transition.transition_kind",
            OutwardExpressionValidationCode.INVALID_ENUM,
            "expected exact OutwardExpressionLifecycleTransitionKind",
        ))
    if record.validation_profile_version != VALIDATION_PROFILE_VERSION:
        issues.append(_issue(
            "transition.validation_profile_version",
            OutwardExpressionValidationCode.PROFILE_VERSION_MISMATCH,
            f"expected {VALIDATION_PROFILE_VERSION!r}",
        ))
    if record.schema_version != SLICE42B_SCHEMA_VERSION:
        issues.append(_issue(
            "transition.schema_version",
            OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE42B_SCHEMA_VERSION!r}",
        ))
    issues.extend(_validate_governance_bool_fields(record, "transition"))
    try:
        if record.transition_id != expected_lifecycle_transition_id(record):
            issues.append(_issue(
                "transition.transition_id",
                OutwardExpressionValidationCode.IDENTITY_MISMATCH,
                "deterministic transition identity mismatch",
            ))
    except Exception as error:
        issues.append(_issue(
            "transition.transition_id",
            OutwardExpressionValidationCode.IDENTITY_MISMATCH,
            str(error),
        ))
    return _report(issues)


def validate_governance_bundle(
    record: Any,
) -> OutwardExpressionValidationReport:
    if type(record) is not OutwardExpressionGovernanceBundle:
        return _report((_issue(
            "bundle",
            OutwardExpressionValidationCode.TYPE_MISMATCH,
            "expected exact OutwardExpressionGovernanceBundle",
        ),))
    issues: list[OutwardExpressionValidationIssue] = []
    issues.extend(_text(record.bundle_id, "bundle.bundle_id"))
    issues.extend(_sha256(record.bundle_digest, "bundle.bundle_digest"))
    issues.extend(validate_runtime_schema_record(record.runtime_schema_record).issues)
    issues.extend(validate_version_custody(
        record.version_custody,
        runtime_record=record.runtime_schema_record,
    ).issues)
    issues.extend(validate_lifecycle_record(record.lifecycle_record).issues)
    if type(record.lifecycle_transitions) is not tuple:
        issues.append(_issue(
            "bundle.lifecycle_transitions",
            OutwardExpressionValidationCode.INVALID_TUPLE,
            "expected exact tuple",
        ))
        transitions: tuple[Any, ...] = ()
    else:
        transitions = record.lifecycle_transitions
    for index, transition in enumerate(transitions):
        report = validate_lifecycle_transition_record(transition)
        for issue in report.issues:
            issues.append(_issue(
                f"bundle.lifecycle_transitions[{index}].{issue.path}",
                issue.code,
                issue.detail,
            ))

    runtime_id = record.runtime_schema_record.outward_expression_runtime_schema_record_id
    if record.version_custody.runtime_schema_record_id != runtime_id:
        issues.append(_issue(
            "bundle.version_custody.runtime_schema_record_id",
            OutwardExpressionValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "version custody does not reference the bundle runtime record",
        ))
    if record.lifecycle_record.runtime_schema_record_id != runtime_id:
        issues.append(_issue(
            "bundle.lifecycle_record.runtime_schema_record_id",
            OutwardExpressionValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "lifecycle record does not reference the bundle runtime record",
        ))
    if record.lifecycle_record.version_custody_ref != record.version_custody.custody_id:
        issues.append(_issue(
            "bundle.lifecycle_record.version_custody_ref",
            OutwardExpressionValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
            "lifecycle record does not reference exact version custody",
        ))
    for index, transition in enumerate(transitions):
        if type(transition) is not OutwardExpressionLifecycleTransitionRecord:
            continue
        if transition.runtime_schema_record_id != runtime_id:
            issues.append(_issue(
                f"bundle.lifecycle_transitions[{index}].runtime_schema_record_id",
                OutwardExpressionValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition runtime reference mismatch",
            ))
        if transition.version_custody_ref != record.version_custody.custody_id:
            issues.append(_issue(
                f"bundle.lifecycle_transitions[{index}].version_custody_ref",
                OutwardExpressionValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition version custody mismatch",
            ))

    issues.extend(_validate_governance_bool_fields(
        record,
        "bundle",
        true_fields=(
            "validation_only",
            "immutable_successor_records",
            "exact_predecessor_references_required",
            "duplicate_and_collision_rejection_required",
            "unknown_version_rejection_required",
            "malformed_record_rejection_required",
            "cross_record_consistency_required",
        ),
    ))
    if record.schema_version != SLICE42B_SCHEMA_VERSION:
        issues.append(_issue(
            "bundle.schema_version",
            OutwardExpressionValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE42B_SCHEMA_VERSION!r}",
        ))
    if record.profile_version != VALIDATION_PROFILE_VERSION:
        issues.append(_issue(
            "bundle.profile_version",
            OutwardExpressionValidationCode.PROFILE_VERSION_MISMATCH,
            f"expected {VALIDATION_PROFILE_VERSION!r}",
        ))

    identity_items = (
        record.version_custody,
        record.lifecycle_record,
        *transitions,
    )
    issues.extend(validate_identity_collection(identity_items).issues)
    try:
        expected_digest = expected_bundle_digest(record)
        if record.bundle_digest != expected_digest:
            issues.append(_issue(
                "bundle.bundle_digest",
                OutwardExpressionValidationCode.CANONICAL_DIGEST_MISMATCH,
                "bundle digest does not match canonical bytes",
            ))
        if record.bundle_id != expected_bundle_id(record):
            issues.append(_issue(
                "bundle.bundle_id",
                OutwardExpressionValidationCode.IDENTITY_MISMATCH,
                "bundle identity does not match canonical digest",
            ))
    except Exception as error:
        issues.append(_issue(
            "bundle.identity",
            OutwardExpressionValidationCode.IDENTITY_MISMATCH,
            str(error),
        ))
    return _report(issues)


def assert_valid_runtime_schema_record(
    record: OutwardExpressionRuntimeSchemaRecord,
) -> OutwardExpressionRuntimeSchemaRecord:
    report = validate_runtime_schema_record(record)
    if not report.ok:
        raise OutwardExpressionValidationError(report)
    return record


def assert_valid_version_custody(
    record: OutwardExpressionVersionCustody,
    *,
    runtime_record: OutwardExpressionRuntimeSchemaRecord | None = None,
) -> OutwardExpressionVersionCustody:
    report = validate_version_custody(record, runtime_record=runtime_record)
    if not report.ok:
        raise OutwardExpressionValidationError(report)
    return record


def assert_valid_governance_bundle(
    record: OutwardExpressionGovernanceBundle,
) -> OutwardExpressionGovernanceBundle:
    report = validate_governance_bundle(record)
    if not report.ok:
        raise OutwardExpressionValidationError(report)
    return record


__all__ = (
    "CORE_RECORD_TYPES",
    "assert_valid_governance_bundle",
    "assert_valid_runtime_schema_record",
    "assert_valid_version_custody",
    "expected_predecessor_references",
    "expected_record_schema_versions",
    "validate_authority_requirement",
    "validate_expression_eligibility_status",
    "validate_expression_plan_boundary",
    "validate_expression_receipt_boundary",
    "validate_expression_trace_boundary",
    "validate_field_pairs",
    "validate_governance_bundle",
    "validate_governed_outward_meaning_boundary",
    "validate_identity_collection",
    "validate_lifecycle_record",
    "validate_lifecycle_transition_record",
    "validate_preservation_obligation_custody",
    "validate_realized_expression_boundary",
    "validate_runtime_schema_record",
    "validate_source_custody",
    "validate_version_custody",
)
