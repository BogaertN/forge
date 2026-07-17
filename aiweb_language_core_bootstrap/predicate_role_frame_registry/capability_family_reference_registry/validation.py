"""Total fail-closed validation for Slice 38F records."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
import re

from ..predicate_frame_registry import PREDICATE_FRAME_REGISTRY
from .authority import (
    ADMITTED_CAPABILITY_FAMILY_KEYS,
    ADMITTED_EFFECT_BOUNDARY_KEYS,
    DEFERRED_CAPABILITY_FAMILY_KEYS,
    FRAMES_WITHOUT_CAPABILITY_REFERENCE,
    UNBOUND_CAPABILITY_FAMILY_KEYS,
)
from .identity import expected_lineage_id, parse_version, version_advances
from .lifecycle import transition_allowed
from .records import (
    ADMISSION_AUTHORITY,
    CAPABILITY_FAMILIES,
    CAPABILITY_FAMILY_HISTORIES,
    CAPABILITY_FAMILY_REFERENCE_REGISTRY,
    COMPATIBILITY_HISTORIES,
    COMPATIBILITY_RECORDS,
    CURRENT_NAMESPACE,
    EFFECT_BOUNDARIES,
    EFFECT_BOUNDARY_HISTORIES,
    FRAME_CAPABILITY_REFERENCE_HISTORIES,
    FRAME_CAPABILITY_REFERENCES,
    FRAME_EFFECT_REFERENCE_HISTORIES,
    FRAME_EFFECT_REFERENCES,
    MANIFEST,
    PROVENANCE_RECORDS,
    TRANSITIONS,
)
from .schema import (
    SLICE38F_SCHEMA_VERSION,
    CapabilityAvailabilityStatus,
    CapabilityEffectCompatibilityRecord,
    CapabilityFamilyIdentity,
    CapabilityFamilyReferenceRegistry,
    CapabilityFamilyReferenceRegistryManifest,
    CapabilityReferenceLifecycleAuthorityRecord,
    CapabilityReferenceLifecycleState,
    CapabilityReferenceLifecycleTransitionRecord,
    CapabilityReferenceMode,
    CapabilityReferenceNamespaceIdentity,
    CapabilityReferenceProvenanceReference,
    CapabilityReferenceResourceKind,
    CapabilityReferenceTransitionKind,
    CapabilityReferenceValidationCode as C,
    CapabilityReferenceValidationError,
    CapabilityReferenceValidationIssue,
    CapabilityReferenceValidationReport,
    EffectBoundaryClass,
    EffectBoundaryIdentity,
    FrameCapabilityFamilyReference,
    FrameEffectBoundaryReference,
)


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]*(?::[a-z0-9:_-]+)?$")


def _issue(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    code: C,
    detail: str,
) -> None:
    issues.append(CapabilityReferenceValidationIssue(path=path, code=code, detail=detail))


def _report(
    issues: list[CapabilityReferenceValidationIssue],
) -> CapabilityReferenceValidationReport:
    try:
        ordered = tuple(
            sorted(issues, key=lambda item: (item.path, item.code.value, item.detail))
        )
    except Exception:
        ordered = (
            CapabilityReferenceValidationIssue(
                path="$",
                code=C.VALIDATOR_FAILED_CLOSED,
                detail="validation issue ordering failed closed",
            ),
        )
    return CapabilityReferenceValidationReport(ok=not ordered, issues=ordered)


def _safe_equal(actual: Any, expected: Any) -> bool:
    try:
        return type(actual) is type(expected) and actual == expected
    except Exception:
        return False


def _exact(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    actual: Any,
    expected: Any,
    code: C = C.MANIFEST_BOUNDARY_MISMATCH,
) -> None:
    if not _safe_equal(actual, expected):
        _issue(issues, path, code, f"expected exact value {expected!r}")


def _bool(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    value: Any,
    expected: bool,
    code: C,
) -> None:
    if type(value) is not bool or value is not expected:
        _issue(issues, path, code, f"exact bool {expected!r} required")


def _none(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    value: Any,
    code: C,
) -> None:
    if value is not None:
        _issue(issues, path, code, "value must remain None in Slice 38F")


def _text(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    value: Any,
) -> bool:
    if type(value) is not str or not value or value != value.strip():
        _issue(issues, path, C.INVALID_TEXT, "trimmed non-empty exact str required")
        return False
    return True


def _identifier(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    value: Any,
) -> bool:
    if not _text(issues, path, value):
        return False
    if _IDENTIFIER.fullmatch(value) is None:
        _issue(issues, path, C.INVALID_IDENTIFIER, "controlled identifier required")
        return False
    return True


def _tuple_values(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    value: Any,
    *,
    item_type: type | None = str,
    allow_empty: bool = False,
) -> tuple[Any, ...]:
    if type(value) is not tuple:
        _issue(issues, path, C.TYPE_MISMATCH, "exact tuple required")
        return ()
    safe: list[Any] = []
    for index, item in enumerate(value):
        if item_type is str:
            if _text(issues, f"{path}[{index}]", item):
                safe.append(item)
        elif item_type is not None:
            if type(item) is not item_type:
                _issue(
                    issues,
                    f"{path}[{index}]",
                    C.INVALID_ENUM,
                    f"exact {item_type.__name__} required",
                )
            else:
                safe.append(item)
        else:
            safe.append(item)
    try:
        unique = len(safe) == len(set(safe))
    except Exception:
        unique = False
    if not unique:
        _issue(issues, path, C.DUPLICATE_VALUE, "tuple values must be unique")
    if not allow_empty and not safe:
        _issue(issues, path, C.REQUIRED_VALUE_MISSING, "tuple must not be empty")
    return tuple(safe)


def _scope(
    issues: list[CapabilityReferenceValidationIssue],
    scope: Any,
    non_scope: Any,
    prefix: str,
) -> None:
    left = _tuple_values(issues, f"{prefix}.scope", scope)
    right = _tuple_values(issues, f"{prefix}.non_scope", non_scope)
    try:
        if set(left) & set(right):
            _issue(issues, prefix, C.SCOPE_OVERLAP, "scope and non-scope must not overlap")
    except Exception:
        _issue(issues, prefix, C.VALIDATOR_FAILED_CLOSED, "scope comparison failed closed")


def _version(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    value: Any,
) -> None:
    try:
        parse_version(value)
    except Exception:
        _issue(issues, path, C.INVALID_VERSION, "version must match vMAJOR.MINOR.PATCH")


def _identity(
    issues: list[CapabilityReferenceValidationIssue],
    record: Any,
    field_name: str,
) -> None:
    try:
        expected = record.expected_id()
    except Exception as error:
        _issue(
            issues,
            field_name,
            C.IDENTITY_MISMATCH,
            f"canonical identity failed closed: {type(error).__name__}",
        )
        return
    _exact(
        issues,
        field_name,
        getattr(record, field_name, None),
        expected,
        C.IDENTITY_MISMATCH,
    )


def _schema(
    issues: list[CapabilityReferenceValidationIssue],
    record: Any,
    prefix: str,
) -> None:
    _exact(
        issues,
        f"{prefix}.schema_version",
        getattr(record, "schema_version", None),
        SLICE38F_SCHEMA_VERSION,
        C.SCHEMA_VERSION_MISMATCH,
    )


def _provenance_refs(
    issues: list[CapabilityReferenceValidationIssue],
    path: str,
    value: Any,
) -> tuple[str, ...]:
    return _tuple_values(issues, path, value)


def validate_provenance(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityReferenceProvenanceReference:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact provenance record required")
            return _report(issues)
        _identity(issues, record, "provenance_id")
        for field_name in (
            "authority_document",
            "authority_section",
            "source_kind",
            "source_reference",
        ):
            _text(issues, field_name, getattr(record, field_name))
        _version(issues, "version", record.version)
        _bool(
            issues,
            "non_llm_provenance",
            record.non_llm_provenance,
            True,
            C.NON_LLM_PROVENANCE_REQUIRED,
        )
        _bool(
            issues,
            "external_resource_admitted",
            record.external_resource_admitted,
            False,
            C.EXTERNAL_RESOURCE_AUTHORITY_COLLAPSE,
        )
        _bool(
            issues,
            "runtime_loaded",
            record.runtime_loaded,
            False,
            C.IMPLEMENTATION_AUTHORITY_COLLAPSE,
        )
        _bool(
            issues,
            "implementation_authorized",
            record.implementation_authorized,
            True,
            C.IMPLEMENTATION_AUTHORITY_COLLAPSE,
        )
        _tuple_values(issues, "prohibited_authorities", record.prohibited_authorities)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.PROVENANCE_REFERENCE,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "provenance")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_namespace(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityReferenceNamespaceIdentity:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact namespace identity required")
            return _report(issues)
        _identity(issues, record, "namespace_id")
        _identifier(issues, "namespace_key", record.namespace_key)
        _text(issues, "preferred_label", record.preferred_label)
        _text(issues, "definition", record.definition)
        _scope(issues, record.scope, record.non_scope, "namespace")
        _version(issues, "version", record.version)
        _exact(
            issues,
            "lifecycle_state",
            record.lifecycle_state,
            CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            C.LIFECYCLE_STATE_INVALID,
        )
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _tuple_values(issues, "permitted_uses", record.permitted_uses)
        _tuple_values(issues, "prohibited_uses", record.prohibited_uses)
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.NAMESPACE_IDENTITY,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "namespace")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_effect_boundary(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not EffectBoundaryIdentity:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact effect-boundary identity required")
            return _report(issues)
        _identity(issues, record, "effect_boundary_id")
        _text(issues, "namespace_id", record.namespace_id)
        _identifier(issues, "effect_boundary_key", record.effect_boundary_key)
        _text(issues, "preferred_label", record.preferred_label)
        if type(record.effect_class) is not EffectBoundaryClass:
            _issue(issues, "effect_class", C.INVALID_ENUM, "exact EffectBoundaryClass required")
        _text(issues, "definition", record.definition)
        _scope(issues, record.scope, record.non_scope, "effect_boundary")
        _tuple_values(issues, "allowed_consequence_descriptions", record.allowed_consequence_descriptions)
        _tuple_values(issues, "prohibited_escalations", record.prohibited_escalations)
        _tuple_values(issues, "authority_dependencies", record.authority_dependencies)
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _version(issues, "version", record.version)
        if type(record.lifecycle_state) is not CapabilityReferenceLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle state required")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        for field_name, code in (
            ("permission_satisfied", C.PERMISSION_COLLAPSE),
            ("capability_available", C.CAPABILITY_AVAILABILITY_COLLAPSE),
            ("route_resolved", C.ROUTE_COLLAPSE),
            ("capability_invoked", C.INVOCATION_COLLAPSE),
            ("execution_performed", C.EXECUTION_COLLAPSE),
            ("evidence_validated", C.RESULT_PROOF_COLLAPSE),
            ("memory_authority_supplied", C.MEMORY_AUTHORITY_COLLAPSE),
            ("delivery_authorized", C.DELIVERY_AUTHORITY_COLLAPSE),
            ("external_resource_admitted", C.EXTERNAL_RESOURCE_AUTHORITY_COLLAPSE),
            ("implementation_performed", C.IMPLEMENTATION_AUTHORITY_COLLAPSE),
        ):
            _bool(issues, field_name, getattr(record, field_name), False, code)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.EFFECT_BOUNDARY_IDENTITY,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "effect_boundary")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_capability_family(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityFamilyIdentity:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact capability-family identity required")
            return _report(issues)
        _identity(issues, record, "capability_family_id")
        _text(issues, "namespace_id", record.namespace_id)
        _identifier(issues, "capability_family_key", record.capability_family_key)
        _text(issues, "preferred_label", record.preferred_label)
        _text(issues, "definition", record.definition)
        _scope(issues, record.scope, record.non_scope, "capability_family")
        _tuple_values(issues, "supported_effect_boundary_refs", record.supported_effect_boundary_refs)
        _tuple_values(
            issues,
            "permitted_reference_modes",
            record.permitted_reference_modes,
            item_type=CapabilityReferenceMode,
        )
        for field_name in (
            "authority_dependencies",
            "availability_proof_dependencies",
            "route_proof_dependencies",
            "invocation_proof_dependencies",
            "prohibited_uses",
        ):
            _tuple_values(issues, field_name, getattr(record, field_name))
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _version(issues, "version", record.version)
        if type(record.lifecycle_state) is not CapabilityReferenceLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle state required")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        for field_name, code in (
            ("installed", C.IMPLEMENTATION_AUTHORITY_COLLAPSE),
            ("available", C.CAPABILITY_AVAILABILITY_COLLAPSE),
            ("route_registered", C.ROUTE_COLLAPSE),
            ("invocation_contract_installed", C.INVOCATION_COLLAPSE),
            ("runtime_loaded", C.IMPLEMENTATION_AUTHORITY_COLLAPSE),
            ("tool_bound", C.ROUTE_COLLAPSE),
            ("external_resource_loaded", C.EXTERNAL_RESOURCE_AUTHORITY_COLLAPSE),
            ("implementation_authorized", C.IMPLEMENTATION_AUTHORITY_COLLAPSE),
        ):
            _bool(issues, field_name, getattr(record, field_name), False, code)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.CAPABILITY_FAMILY_IDENTITY,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "capability_family")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_frame_effect_reference(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not FrameEffectBoundaryReference:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact frame-effect reference required")
            return _report(issues)
        _identity(issues, record, "frame_effect_reference_id")
        for field_name in (
            "frame_id",
            "frame_key",
            "frame_version",
            "effect_boundary_id",
            "effect_boundary_key",
            "effect_boundary_version",
        ):
            _text(issues, field_name, getattr(record, field_name))
        _tuple_values(issues, "classification_basis", record.classification_basis)
        _tuple_values(issues, "authority_dependencies", record.authority_dependencies)
        _scope(issues, record.scope, record.non_scope, "frame_effect_reference")
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _version(issues, "version", record.version)
        if type(record.lifecycle_state) is not CapabilityReferenceLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle state required")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        for field_name, code in (
            ("frame_selected", C.FRAME_COMPLETION_PERMISSION_COLLAPSE),
            ("effect_permission_satisfied", C.PERMISSION_COLLAPSE),
            ("capability_available", C.CAPABILITY_AVAILABILITY_COLLAPSE),
            ("route_resolved", C.ROUTE_COLLAPSE),
            ("invocation_proposed", C.INVOCATION_COLLAPSE),
            ("invocation_authorized", C.INVOCATION_COLLAPSE),
            ("execution_performed", C.EXECUTION_COLLAPSE),
            ("result_verified", C.RESULT_PROOF_COLLAPSE),
        ):
            _bool(issues, field_name, getattr(record, field_name), False, code)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.FRAME_EFFECT_BOUNDARY_REFERENCE,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "frame_effect_reference")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_frame_capability_reference(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not FrameCapabilityFamilyReference:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact frame-capability reference required")
            return _report(issues)
        _identity(issues, record, "frame_capability_reference_id")
        for field_name in (
            "frame_id",
            "frame_key",
            "frame_version",
            "capability_family_id",
            "capability_family_key",
            "capability_family_version",
            "frame_effect_reference_id",
            "effect_boundary_id",
            "effect_boundary_key",
        ):
            _text(issues, field_name, getattr(record, field_name))
        if type(record.relevance_mode) is not CapabilityReferenceMode:
            _issue(issues, "relevance_mode", C.INVALID_ENUM, "exact CapabilityReferenceMode required")
        _exact(
            issues,
            "availability_status",
            record.availability_status,
            CapabilityAvailabilityStatus.NOT_PROVEN,
            C.CAPABILITY_AVAILABILITY_COLLAPSE,
        )
        _tuple_values(issues, "relevance_basis", record.relevance_basis)
        _tuple_values(issues, "authority_dependencies", record.authority_dependencies)
        _scope(issues, record.scope, record.non_scope, "frame_capability_reference")
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _version(issues, "version", record.version)
        if type(record.lifecycle_state) is not CapabilityReferenceLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle state required")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _bool(issues, "capability_available", record.capability_available, False, C.CAPABILITY_AVAILABILITY_COLLAPSE)
        _none(issues, "route_identity", record.route_identity, C.ROUTE_COLLAPSE)
        _bool(issues, "route_available", record.route_available, False, C.ROUTE_COLLAPSE)
        _none(issues, "invocation_identity", record.invocation_identity, C.INVOCATION_COLLAPSE)
        _bool(issues, "invocation_proposed", record.invocation_proposed, False, C.INVOCATION_COLLAPSE)
        _bool(issues, "invocation_authorized", record.invocation_authorized, False, C.INVOCATION_COLLAPSE)
        _none(issues, "argument_bundle_id", record.argument_bundle_id, C.ARGUMENT_CONSTRUCTION_COLLAPSE)
        _bool(issues, "arguments_constructed", record.arguments_constructed, False, C.ARGUMENT_CONSTRUCTION_COLLAPSE)
        _none(issues, "permission_id", record.permission_id, C.PERMISSION_COLLAPSE)
        _bool(issues, "permission_granted", record.permission_granted, False, C.PERMISSION_COLLAPSE)
        _none(issues, "execution_receipt_id", record.execution_receipt_id, C.EXECUTION_COLLAPSE)
        _bool(issues, "execution_performed", record.execution_performed, False, C.EXECUTION_COLLAPSE)
        _bool(issues, "result_verified", record.result_verified, False, C.RESULT_PROOF_COLLAPSE)
        _bool(issues, "tool_bound", record.tool_bound, False, C.ROUTE_COLLAPSE)
        _bool(issues, "memory_operation_performed", record.memory_operation_performed, False, C.MEMORY_AUTHORITY_COLLAPSE)
        _bool(issues, "delivery_performed", record.delivery_performed, False, C.DELIVERY_AUTHORITY_COLLAPSE)
        _bool(issues, "external_resource_admitted", record.external_resource_admitted, False, C.EXTERNAL_RESOURCE_AUTHORITY_COLLAPSE)
        _bool(issues, "implementation_performed", record.implementation_performed, False, C.IMPLEMENTATION_AUTHORITY_COLLAPSE)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.FRAME_CAPABILITY_FAMILY_REFERENCE,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "frame_capability_reference")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_compatibility(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityEffectCompatibilityRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact compatibility record required")
            return _report(issues)
        _identity(issues, record, "compatibility_id")
        for field_name in (
            "capability_family_id",
            "capability_family_key",
            "effect_boundary_id",
            "effect_boundary_key",
        ):
            _text(issues, field_name, getattr(record, field_name))
        _tuple_values(
            issues,
            "permitted_reference_modes",
            record.permitted_reference_modes,
            item_type=CapabilityReferenceMode,
        )
        _tuple_values(issues, "compatibility_basis", record.compatibility_basis)
        _scope(issues, record.scope, record.non_scope, "compatibility")
        _version(issues, "version", record.version)
        if type(record.lifecycle_state) is not CapabilityReferenceLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle state required")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        for field_name, code in (
            ("proves_capability_availability", C.CAPABILITY_AVAILABILITY_COLLAPSE),
            ("creates_route", C.ROUTE_COLLAPSE),
            ("authorizes_invocation", C.INVOCATION_COLLAPSE),
            ("authorizes_execution", C.EXECUTION_COLLAPSE),
            ("satisfies_permission", C.PERMISSION_COLLAPSE),
        ):
            _bool(issues, field_name, getattr(record, field_name), False, code)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.CAPABILITY_EFFECT_COMPATIBILITY,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "compatibility")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_authority(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityReferenceLifecycleAuthorityRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact lifecycle authority record required")
            return _report(issues)
        _identity(issues, record, "authority_id")
        _identifier(issues, "authority_key", record.authority_key)
        _text(issues, "decision_owner", record.decision_owner)
        _tuple_values(issues, "authority_basis", record.authority_basis)
        _tuple_values(issues, "approved_scope", record.approved_scope)
        _tuple_values(issues, "prohibited_scope", record.prohibited_scope)
        _bool(issues, "human_approval", record.human_approval, True, C.HUMAN_APPROVAL_REQUIRED)
        _bool(issues, "non_llm_decision", record.non_llm_decision, True, C.NON_LLM_PROVENANCE_REQUIRED)
        _bool(issues, "automatic_transition_allowed", record.automatic_transition_allowed, False, C.TRANSITION_NOT_PERMITTED)
        for field_name, code in (
            ("implementation_authorized", C.IMPLEMENTATION_AUTHORITY_COLLAPSE),
            ("capability_availability_authorized", C.CAPABILITY_AVAILABILITY_COLLAPSE),
            ("route_authorized", C.ROUTE_COLLAPSE),
            ("invocation_authorized", C.INVOCATION_COLLAPSE),
            ("action_authorized", C.EXECUTION_COLLAPSE),
        ):
            _bool(issues, field_name, getattr(record, field_name), False, code)
        _version(issues, "version", record.version)
        _exact(
            issues,
            "lifecycle_state",
            record.lifecycle_state,
            CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            C.LIFECYCLE_STATE_INVALID,
        )
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.LIFECYCLE_AUTHORITY,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "authority")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_transition(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityReferenceLifecycleTransitionRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact lifecycle transition required")
            return _report(issues)
        _identity(issues, record, "transition_id")
        for field_name in (
            "resource_lineage_id",
            "source_resource_id",
            "target_resource_id",
            "reason",
            "authority_record_ref",
        ):
            _text(issues, field_name, getattr(record, field_name))
        _version(issues, "source_version", record.source_version)
        _version(issues, "target_version", record.target_version)
        if not version_advances(record.source_version, record.target_version):
            _issue(issues, "target_version", C.VERSION_NOT_ADVANCING, "target version must advance")
        if type(record.from_state) is not CapabilityReferenceLifecycleState or type(record.to_state) is not CapabilityReferenceLifecycleState:
            _issue(issues, "lifecycle", C.LIFECYCLE_STATE_INVALID, "exact lifecycle states required")
        if type(record.transition_kind) is not CapabilityReferenceTransitionKind:
            _issue(issues, "transition_kind", C.INVALID_ENUM, "exact transition kind required")
        elif not transition_allowed(record.from_state, record.to_state, record.transition_kind):
            _issue(issues, "transition_kind", C.TRANSITION_NOT_PERMITTED, "transition not permitted")
        _scope(issues, record.scope, record.non_scope, "transition")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _bool(issues, "human_approval", record.human_approval, True, C.HUMAN_APPROVAL_REQUIRED)
        _bool(issues, "prior_record_preserved", record.prior_record_preserved, True, C.PRIOR_RECORD_NOT_PRESERVED)
        for field_name, code in (
            ("automatic_transition", C.TRANSITION_NOT_PERMITTED),
            ("in_place_mutation_performed", C.IN_PLACE_MUTATION_PROHIBITED),
            ("capability_availability_created", C.CAPABILITY_AVAILABILITY_COLLAPSE),
            ("route_created", C.ROUTE_COLLAPSE),
            ("invocation_created", C.INVOCATION_COLLAPSE),
            ("permission_created", C.PERMISSION_COLLAPSE),
            ("execution_created", C.EXECUTION_COLLAPSE),
            ("result_proof_created", C.RESULT_PROOF_COLLAPSE),
        ):
            _bool(issues, field_name, getattr(record, field_name), False, code)
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.LIFECYCLE_TRANSITION,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "transition")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_manifest(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityFamilyReferenceRegistryManifest:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact registry manifest required")
            return _report(issues)
        _identity(issues, record, "manifest_id")
        for field_name in ("registry_id", "namespace_id"):
            _text(issues, field_name, getattr(record, field_name))
        for field_name in (
            "effect_boundary_refs",
            "effect_boundary_keys",
            "capability_family_refs",
            "capability_family_keys",
            "frame_effect_reference_refs",
            "frame_capability_reference_refs",
            "compatibility_refs",
            "transition_refs",
            "provenance_refs",
            "frames_without_capability_reference",
            "unbound_capability_family_keys",
            "deferred_capability_family_keys",
            "provenance_refs_manifest",
        ):
            _tuple_values(issues, field_name, getattr(record, field_name), allow_empty=False)
        for field_name in (
            "effect_boundary_count",
            "capability_family_count",
            "frame_effect_reference_count",
            "frame_capability_reference_count",
            "compatibility_count",
            "transition_count",
            "active_correction_count",
            "active_conflict_count",
        ):
            value = getattr(record, field_name)
            if type(value) is not int or value < 0:
                _issue(issues, field_name, C.TYPE_MISMATCH, "non-negative exact int required")
        false_fields = (
            "source_term_lookup_installed",
            "occurrence_frame_selection_installed",
            "occurrence_role_assignment_installed",
            "candidate_meaning_creation_installed",
            "selected_meaning_installed",
            "gate_outcome_installed",
            "capability_availability_registry_installed",
            "route_registry_installed",
            "invocation_registry_installed",
            "argument_builder_installed",
            "tool_activation_installed",
            "action_execution_installed",
            "evidence_validation_installed",
            "memory_access_installed",
            "rendering_installed",
            "delivery_installed",
            "external_resource_loading_installed",
            "implementation_installed",
            "nearest_known_substitution_installed",
            "semantic_similarity_installed",
            "llm_authority_installed",
            "default_capability_reference_installed",
        )
        for field_name in false_fields:
            code = C.MANIFEST_BOUNDARY_MISMATCH
            if "route" in field_name:
                code = C.ROUTE_COLLAPSE
            elif "invocation" in field_name:
                code = C.INVOCATION_COLLAPSE
            elif "capability_availability" in field_name:
                code = C.CAPABILITY_AVAILABILITY_COLLAPSE
            elif "argument" in field_name:
                code = C.ARGUMENT_CONSTRUCTION_COLLAPSE
            elif "action_execution" in field_name:
                code = C.EXECUTION_COLLAPSE
            elif "memory" in field_name:
                code = C.MEMORY_AUTHORITY_COLLAPSE
            elif "delivery" in field_name or "rendering" in field_name:
                code = C.DELIVERY_AUTHORITY_COLLAPSE
            elif "external_resource" in field_name:
                code = C.EXTERNAL_RESOURCE_AUTHORITY_COLLAPSE
            elif "implementation" in field_name:
                code = C.IMPLEMENTATION_AUTHORITY_COLLAPSE
            elif "similarity" in field_name:
                code = C.SIMILARITY_AUTHORITY_PROHIBITED
            elif "nearest" in field_name:
                code = C.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED
            elif "default" in field_name:
                code = C.DEFAULT_REFERENCE_PROHIBITED
            _bool(issues, field_name, getattr(record, field_name), False, code)
        _bool(issues, "registry_read_only", record.registry_read_only, True, C.REGISTRY_NOT_READ_ONLY)
        _bool(issues, "registry_closed", record.registry_closed, True, C.REGISTRY_NOT_CLOSED)
        _bool(issues, "exact_identity_lookup_only", record.exact_identity_lookup_only, True, C.REGISTRY_NOT_CLOSED)
        _version(issues, "version", record.version)
        _exact(
            issues,
            "lifecycle_state",
            record.lifecycle_state,
            CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED,
            C.LIFECYCLE_STATE_INVALID,
        )
        _exact(
            issues,
            "resource_kind",
            record.resource_kind,
            CapabilityReferenceResourceKind.REGISTRY_MANIFEST,
            C.RESOURCE_KIND_MISMATCH,
        )
        _schema(issues, record, "manifest")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def _merge_report(
    issues: list[CapabilityReferenceValidationIssue],
    prefix: str,
    report: CapabilityReferenceValidationReport,
) -> None:
    for issue in report.issues:
        path = prefix if issue.path == "$" else f"{prefix}.{issue.path}"
        _issue(issues, path, issue.code, issue.detail)


def validate_registry(record: object) -> CapabilityReferenceValidationReport:
    issues: list[CapabilityReferenceValidationIssue] = []
    try:
        if type(record) is not CapabilityFamilyReferenceRegistry:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact Slice 38F registry required")
            return _report(issues)

        _merge_report(issues, "manifest", validate_manifest(record.manifest))
        _merge_report(issues, "current_namespace", validate_namespace(record.current_namespace))
        for index, item in enumerate(record.effect_boundaries):
            _merge_report(issues, f"effect_boundaries[{index}]", validate_effect_boundary(item))
        for index, item in enumerate(record.capability_families):
            _merge_report(issues, f"capability_families[{index}]", validate_capability_family(item))
        for index, item in enumerate(record.frame_effect_references):
            _merge_report(issues, f"frame_effect_references[{index}]", validate_frame_effect_reference(item))
        for index, item in enumerate(record.frame_capability_references):
            _merge_report(issues, f"frame_capability_references[{index}]", validate_frame_capability_reference(item))
        for index, item in enumerate(record.compatibility_records):
            _merge_report(issues, f"compatibility_records[{index}]", validate_compatibility(item))
        for index, item in enumerate(record.authority_records):
            _merge_report(issues, f"authority_records[{index}]", validate_authority(item))
        for index, item in enumerate(record.transitions):
            _merge_report(issues, f"transitions[{index}]", validate_transition(item))
        for index, item in enumerate(record.provenance_records):
            _merge_report(issues, f"provenance_records[{index}]", validate_provenance(item))

        _exact(issues, "manifest", record.manifest, MANIFEST)
        _exact(issues, "current_namespace", record.current_namespace, CURRENT_NAMESPACE)
        _exact(issues, "effect_boundaries", record.effect_boundaries, EFFECT_BOUNDARIES)
        _exact(issues, "effect_boundary_histories", record.effect_boundary_histories, EFFECT_BOUNDARY_HISTORIES)
        _exact(issues, "capability_families", record.capability_families, CAPABILITY_FAMILIES)
        _exact(issues, "capability_family_histories", record.capability_family_histories, CAPABILITY_FAMILY_HISTORIES)
        _exact(issues, "frame_effect_references", record.frame_effect_references, FRAME_EFFECT_REFERENCES)
        _exact(issues, "frame_effect_reference_histories", record.frame_effect_reference_histories, FRAME_EFFECT_REFERENCE_HISTORIES)
        _exact(issues, "frame_capability_references", record.frame_capability_references, FRAME_CAPABILITY_REFERENCES)
        _exact(issues, "frame_capability_reference_histories", record.frame_capability_reference_histories, FRAME_CAPABILITY_REFERENCE_HISTORIES)
        _exact(issues, "compatibility_records", record.compatibility_records, COMPATIBILITY_RECORDS)
        _exact(issues, "compatibility_histories", record.compatibility_histories, COMPATIBILITY_HISTORIES)
        _exact(issues, "authority_records", record.authority_records, (ADMISSION_AUTHORITY,))
        _exact(issues, "transitions", record.transitions, TRANSITIONS)
        _exact(issues, "provenance_records", record.provenance_records, PROVENANCE_RECORDS)

        _exact(issues, "manifest.effect_boundary_keys", record.manifest.effect_boundary_keys, ADMITTED_EFFECT_BOUNDARY_KEYS)
        _exact(issues, "manifest.capability_family_keys", record.manifest.capability_family_keys, ADMITTED_CAPABILITY_FAMILY_KEYS)
        _exact(issues, "manifest.deferred_capability_family_keys", record.manifest.deferred_capability_family_keys, DEFERRED_CAPABILITY_FAMILY_KEYS)
        _exact(issues, "manifest.frames_without_capability_reference", record.manifest.frames_without_capability_reference, FRAMES_WITHOUT_CAPABILITY_REFERENCE)
        _exact(issues, "manifest.unbound_capability_family_keys", record.manifest.unbound_capability_family_keys, UNBOUND_CAPABILITY_FAMILY_KEYS)

        provenance_ids = {item.provenance_id for item in record.provenance_records}
        effect_by_id = {item.effect_boundary_id: item for item in record.effect_boundaries}
        effect_by_key = {item.effect_boundary_key: item for item in record.effect_boundaries}
        capability_by_id = {item.capability_family_id: item for item in record.capability_families}
        capability_by_key = {item.capability_family_key: item for item in record.capability_families}
        frame_by_id = {item.frame_id: item for item in PREDICATE_FRAME_REGISTRY.admitted_frames}
        frame_by_key = {item.frame_key: item for item in PREDICATE_FRAME_REGISTRY.admitted_frames}
        frame_effect_by_id = {item.frame_effect_reference_id: item for item in record.frame_effect_references}
        compatibility_by_family = {item.capability_family_id: item for item in record.compatibility_records}
        authority_ids = {item.authority_id for item in record.authority_records}

        for index, effect in enumerate(record.effect_boundaries):
            prefix = f"effect_boundaries[{index}]"
            if effect.namespace_id != record.current_namespace.namespace_id:
                _issue(issues, f"{prefix}.namespace_id", C.REFERENCE_NOT_FOUND, "namespace mismatch")
            if not set(effect.provenance_refs).issubset(provenance_ids):
                _issue(issues, f"{prefix}.provenance_refs", C.PROVENANCE_INVALID, "unknown provenance")

        for index, family in enumerate(record.capability_families):
            prefix = f"capability_families[{index}]"
            if family.namespace_id != record.current_namespace.namespace_id:
                _issue(issues, f"{prefix}.namespace_id", C.REFERENCE_NOT_FOUND, "namespace mismatch")
            if not set(family.supported_effect_boundary_refs).issubset(effect_by_id):
                _issue(issues, f"{prefix}.supported_effect_boundary_refs", C.EFFECT_REFERENCE_INVALID, "unknown effect reference")
            compatibility = compatibility_by_family.get(family.capability_family_id)
            if compatibility is None:
                _issue(issues, prefix, C.EFFECT_COMPATIBILITY_INVALID, "compatibility record missing")

        seen_frames: set[str] = set()
        for index, reference in enumerate(record.frame_effect_references):
            prefix = f"frame_effect_references[{index}]"
            frame = frame_by_id.get(reference.frame_id)
            effect = effect_by_id.get(reference.effect_boundary_id)
            if frame is None or frame.frame_key != reference.frame_key or frame.version != reference.frame_version:
                _issue(issues, f"{prefix}.frame_id", C.FRAME_REFERENCE_INVALID, "exact admitted frame required")
            if effect is None or effect.effect_boundary_key != reference.effect_boundary_key or effect.version != reference.effect_boundary_version:
                _issue(issues, f"{prefix}.effect_boundary_id", C.EFFECT_REFERENCE_INVALID, "exact effect boundary required")
            if reference.frame_id in seen_frames:
                _issue(issues, f"{prefix}.frame_id", C.DUPLICATE_KEY, "one effect reference per frame required")
            seen_frames.add(reference.frame_id)

        expected_frame_ids = {item.frame_id for item in PREDICATE_FRAME_REGISTRY.admitted_frames}
        if seen_frames != expected_frame_ids:
            _issue(issues, "frame_effect_references", C.FRAME_REFERENCE_INVALID, "every admitted frame requires one exact effect reference")

        capability_refs_by_frame: dict[str, list[FrameCapabilityFamilyReference]] = {}
        for index, reference in enumerate(record.frame_capability_references):
            prefix = f"frame_capability_references[{index}]"
            frame = frame_by_id.get(reference.frame_id)
            family = capability_by_id.get(reference.capability_family_id)
            effect = effect_by_id.get(reference.effect_boundary_id)
            frame_effect = frame_effect_by_id.get(reference.frame_effect_reference_id)
            if frame is None or frame.frame_key != reference.frame_key or frame.version != reference.frame_version:
                _issue(issues, f"{prefix}.frame_id", C.FRAME_REFERENCE_INVALID, "exact admitted frame required")
            if family is None or family.capability_family_key != reference.capability_family_key or family.version != reference.capability_family_version:
                _issue(issues, f"{prefix}.capability_family_id", C.CAPABILITY_REFERENCE_INVALID, "exact admitted capability family required")
            if effect is None or effect.effect_boundary_key != reference.effect_boundary_key:
                _issue(issues, f"{prefix}.effect_boundary_id", C.EFFECT_REFERENCE_INVALID, "exact effect boundary required")
            if frame_effect is None or frame_effect.frame_id != reference.frame_id or frame_effect.effect_boundary_id != reference.effect_boundary_id:
                _issue(issues, f"{prefix}.frame_effect_reference_id", C.EFFECT_REFERENCE_INVALID, "matching frame-effect reference required")
            if family is not None and reference.relevance_mode not in family.permitted_reference_modes:
                _issue(issues, f"{prefix}.relevance_mode", C.CAPABILITY_REFERENCE_INVALID, "mode not permitted by family")
            compatibility = compatibility_by_family.get(reference.capability_family_id)
            if compatibility is None or compatibility.effect_boundary_id != reference.effect_boundary_id or reference.relevance_mode not in compatibility.permitted_reference_modes:
                _issue(issues, prefix, C.EFFECT_COMPATIBILITY_INVALID, "exact compatibility required")
            capability_refs_by_frame.setdefault(reference.frame_key, []).append(reference)

        for frame_key in FRAMES_WITHOUT_CAPABILITY_REFERENCE:
            if capability_refs_by_frame.get(frame_key):
                _issue(issues, f"frame:{frame_key}", C.DEFAULT_REFERENCE_PROHIBITED, "frame must carry no capability reference")
        for family_key in UNBOUND_CAPABILITY_FAMILY_KEYS:
            if any(item.capability_family_key == family_key for item in record.frame_capability_references):
                _issue(issues, f"capability-family:{family_key}", C.DEFAULT_REFERENCE_PROHIBITED, "family must remain unbound")

        histories = (
            *record.effect_boundary_histories,
            *record.capability_family_histories,
            *record.frame_effect_reference_histories,
            *record.frame_capability_reference_histories,
            *record.compatibility_histories,
        )
        source_target_pairs: set[tuple[str, str]] = set()
        for index, history in enumerate(histories):
            if type(history) is not tuple or len(history) != 2:
                _issue(issues, f"histories[{index}]", C.ANCESTRY_REQUIRED, "two-version history required")
                continue
            source, target = history
            try:
                if expected_lineage_id(source) != expected_lineage_id(target):
                    _issue(issues, f"histories[{index}]", C.LINEAGE_MISMATCH, "stable lineage required")
                if not version_advances(source.version, target.version):
                    _issue(issues, f"histories[{index}]", C.VERSION_NOT_ADVANCING, "version must advance")
                if source.lifecycle_state is not CapabilityReferenceLifecycleState.CANDIDATE or target.lifecycle_state is not CapabilityReferenceLifecycleState.ARCHITECTURE_ADMITTED:
                    _issue(issues, f"histories[{index}]", C.LIFECYCLE_STATE_INVALID, "candidate to architecture-admitted history required")
                source_target_pairs.add((source.expected_id(), target.expected_id()))
            except Exception as error:
                _issue(issues, f"histories[{index}]", C.VALIDATOR_FAILED_CLOSED, f"history failed closed: {type(error).__name__}")

        transition_pairs = {(item.source_resource_id, item.target_resource_id) for item in record.transitions}
        if transition_pairs != source_target_pairs:
            _issue(issues, "transitions", C.ANCESTRY_REQUIRED, "one exact transition per history required")
        for index, transition in enumerate(record.transitions):
            if transition.authority_record_ref not in authority_ids:
                _issue(issues, f"transitions[{index}].authority_record_ref", C.AUTHORITY_RECORD_NOT_FOUND, "authority missing")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"registry validator failed closed: {type(error).__name__}")
    return _report(issues)


def assert_valid(report_or_record: object) -> None:
    report = (
        report_or_record
        if type(report_or_record) is CapabilityReferenceValidationReport
        else validate_registry(report_or_record)
    )
    if type(report) is not CapabilityReferenceValidationReport or not report.ok:
        if type(report) is CapabilityReferenceValidationReport:
            raise CapabilityReferenceValidationError(report)
        raise CapabilityReferenceValidationError(
            _report(
                [
                    CapabilityReferenceValidationIssue(
                        "$",
                        C.TYPE_MISMATCH,
                        "validation report required",
                    )
                ]
            )
        )


PUBLIC_VALIDATORS: tuple[
    Callable[[object], CapabilityReferenceValidationReport], ...
] = (
    validate_provenance,
    validate_namespace,
    validate_effect_boundary,
    validate_capability_family,
    validate_frame_effect_reference,
    validate_frame_capability_reference,
    validate_compatibility,
    validate_authority,
    validate_transition,
    validate_manifest,
    validate_registry,
)
