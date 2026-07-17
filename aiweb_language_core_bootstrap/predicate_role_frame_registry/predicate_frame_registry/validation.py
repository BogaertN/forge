"""Total fail-closed validation for Slice 38E predicate-frame records."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import fields
from typing import Any
import re

from ..built_in_action_root_registry import BUILT_IN_ACTION_ROOT_REGISTRY
from ..participant_role_registry import PARTICIPANT_ROLE_REGISTRY
from ...controlled_concept_sense_registry.semantic_class_relation_registry import SEMANTIC_CLASS_RELATION_REGISTRY
from .authority import ADMITTED_PREDICATE_FRAME_KEYS, FRAME_DEFINITIONS
from .identity import expected_lineage_id, parse_version, version_advances
from .lifecycle import transition_allowed
from .records import (
    ADMISSION_AUTHORITY,
    ADMITTED_FRAMES,
    COMPATIBILITY_RULES,
    CURRENT_NAMESPACE,
    FRAME_HISTORIES,
    MANIFEST,
    PREDICATE_FRAME_REGISTRY,
    PROVENANCE_RECORDS,
    ROLE_CONSTRAINTS,
    STRUCTURAL_STATE_POLICIES,
    TRANSITIONS,
)
from .schema import (
    FrameCapabilityReferenceStatus,
    FrameEffectClassification,
    FrameRoleCardinality,
    FrameRoleConstraint,
    FrameRoleRequirement,
    FrameSpeechAct,
    FrameStructuralStatePolicy,
    PredicateFrameIdentity,
    PredicateFrameLifecycleAuthorityRecord,
    PredicateFrameLifecycleState,
    PredicateFrameLifecycleTransitionRecord,
    PredicateFrameNamespaceIdentity,
    PredicateFrameProvenanceReference,
    PredicateFrameRegistry,
    PredicateFrameRegistryManifest,
    PredicateFrameResourceKind,
    PredicateFrameStructuralState,
    PredicateFrameTransitionKind,
    PredicateFrameValidationCode as C,
    PredicateFrameValidationError,
    PredicateFrameValidationIssue,
    PredicateFrameValidationReport,
    RoleConceptCompatibilityMode,
    RoleConceptCompatibilityRule,
    SLICE38E_SCHEMA_VERSION,
)


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]*(?::[a-z0-9:_-]+)?$")


def _issue(issues: list[PredicateFrameValidationIssue], path: str, code: C, detail: str) -> None:
    issues.append(PredicateFrameValidationIssue(path=path, code=code, detail=detail))


def _report(issues: list[PredicateFrameValidationIssue]) -> PredicateFrameValidationReport:
    try:
        ordered = tuple(sorted(issues, key=lambda item: (item.path, item.code.value, item.detail)))
    except Exception:
        ordered = (
            PredicateFrameValidationIssue(
                path="$",
                code=C.VALIDATOR_FAILED_CLOSED,
                detail="validation issue ordering failed closed",
            ),
        )
    return PredicateFrameValidationReport(ok=not ordered, issues=ordered)


def _safe_equal(actual: Any, expected: Any) -> bool:
    try:
        return type(actual) is type(expected) and actual == expected
    except Exception:
        return False


def _exact(
    issues: list[PredicateFrameValidationIssue],
    path: str,
    actual: Any,
    expected: Any,
    code: C = C.MANIFEST_BOUNDARY_MISMATCH,
) -> None:
    if not _safe_equal(actual, expected):
        _issue(issues, path, code, f"expected exact value {expected!r}")


def _bool(
    issues: list[PredicateFrameValidationIssue],
    path: str,
    value: Any,
    expected: bool,
    code: C,
) -> None:
    if type(value) is not bool or value is not expected:
        _issue(issues, path, code, f"exact bool {expected!r} required")


def _text(issues: list[PredicateFrameValidationIssue], path: str, value: Any) -> bool:
    if type(value) is not str or not value or value != value.strip():
        _issue(issues, path, C.INVALID_TEXT, "trimmed non-empty exact str required")
        return False
    return True


def _identifier(issues: list[PredicateFrameValidationIssue], path: str, value: Any) -> bool:
    if not _text(issues, path, value):
        return False
    if _IDENTIFIER.fullmatch(value) is None:
        _issue(issues, path, C.INVALID_IDENTIFIER, "controlled identifier required")
        return False
    return True


def _tuple_values(
    issues: list[PredicateFrameValidationIssue],
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
                _issue(issues, f"{path}[{index}]", C.INVALID_ENUM, f"exact {item_type.__name__} required")
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


def _scope(issues: list[PredicateFrameValidationIssue], scope: Any, non_scope: Any, prefix: str) -> None:
    left = _tuple_values(issues, f"{prefix}.scope", scope)
    right = _tuple_values(issues, f"{prefix}.non_scope", non_scope)
    try:
        if set(left) & set(right):
            _issue(issues, prefix, C.SCOPE_OVERLAP, "scope and non-scope must not overlap")
    except Exception:
        _issue(issues, prefix, C.VALIDATOR_FAILED_CLOSED, "scope comparison failed closed")


def _version(issues: list[PredicateFrameValidationIssue], path: str, value: Any) -> None:
    try:
        parse_version(value)
    except Exception:
        _issue(issues, path, C.INVALID_VERSION, "version must match vMAJOR.MINOR.PATCH")


def _identity(issues: list[PredicateFrameValidationIssue], record: Any, field_name: str) -> None:
    try:
        expected = record.expected_id()
    except Exception as error:
        _issue(issues, field_name, C.IDENTITY_MISMATCH, f"canonical identity failed closed: {type(error).__name__}")
        return
    _exact(issues, field_name, getattr(record, field_name, None), expected, C.IDENTITY_MISMATCH)


def _schema(issues: list[PredicateFrameValidationIssue], record: Any, prefix: str) -> None:
    _exact(issues, f"{prefix}.schema_version", getattr(record, "schema_version", None), SLICE38E_SCHEMA_VERSION, C.SCHEMA_VERSION_MISMATCH)


def _provenance_refs(issues: list[PredicateFrameValidationIssue], path: str, value: Any) -> tuple[str, ...]:
    return _tuple_values(issues, path, value)


def validate_provenance(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not PredicateFrameProvenanceReference:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact PredicateFrameProvenanceReference required")
            return _report(issues)
        _identity(issues, record, "provenance_id")
        for field_name in ("authority_document", "authority_section", "source_kind", "source_reference"):
            _text(issues, field_name, getattr(record, field_name))
        _version(issues, "version", record.version)
        _bool(issues, "non_llm_provenance", record.non_llm_provenance, True, C.NON_LLM_PROVENANCE_REQUIRED)
        _bool(issues, "external_resource_admitted", record.external_resource_admitted, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "runtime_loaded", record.runtime_loaded, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "implementation_authorized", record.implementation_authorized, True, C.RUNTIME_AUTHORITY_PROHIBITED)
        _tuple_values(issues, "prohibited_authorities", record.prohibited_authorities)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.PROVENANCE_REFERENCE, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "provenance")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_namespace(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not PredicateFrameNamespaceIdentity:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact PredicateFrameNamespaceIdentity required")
            return _report(issues)
        _identity(issues, record, "namespace_id")
        _identifier(issues, "namespace_key", record.namespace_key)
        _text(issues, "preferred_label", record.preferred_label)
        _text(issues, "definition", record.definition)
        _scope(issues, record.scope, record.non_scope, "namespace")
        _version(issues, "version", record.version)
        _exact(issues, "lifecycle_state", record.lifecycle_state, PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED, C.LIFECYCLE_STATE_INVALID)
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _tuple_values(issues, "permitted_uses", record.permitted_uses)
        _tuple_values(issues, "prohibited_uses", record.prohibited_uses)
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.NAMESPACE_IDENTITY, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "namespace")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_compatibility(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not RoleConceptCompatibilityRule:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact RoleConceptCompatibilityRule required")
            return _report(issues)
        _identity(issues, record, "compatibility_id")
        _identifier(issues, "frame_key", record.frame_key)
        _text(issues, "role_id", record.role_id)
        _identifier(issues, "role_key", record.role_key)
        _exact(issues, "mode", record.mode, RoleConceptCompatibilityMode.EXACT_ADMITTED_SUPPORT_REQUIRED, C.CONCEPT_COMPATIBILITY_INVALID)
        _tuple_values(issues, "allowed_concept_refs", record.allowed_concept_refs, allow_empty=True)
        _tuple_values(issues, "allowed_semantic_class_refs", record.allowed_semantic_class_refs)
        _tuple_values(issues, "prohibited_concept_refs", record.prohibited_concept_refs, allow_empty=True)
        _bool(issues, "semantic_class_membership_sufficient", record.semantic_class_membership_sufficient, False, C.CONCEPT_COMPATIBILITY_INVALID)
        _bool(issues, "exact_concept_allowlist_required", record.exact_concept_allowlist_required, True, C.CONCEPT_COMPATIBILITY_INVALID)
        _bool(issues, "unknown_if_exact_support_absent", record.unknown_if_exact_support_absent, True, C.CONCEPT_COMPATIBILITY_INVALID)
        _bool(issues, "external_only_support_allowed", record.external_only_support_allowed, False, C.CONCEPT_COMPATIBILITY_INVALID)
        _bool(issues, "quarantined_support_allowed", record.quarantined_support_allowed, False, C.CONCEPT_COMPATIBILITY_INVALID)
        _bool(issues, "similarity_support_allowed", record.similarity_support_allowed, False, C.SIMILARITY_AUTHORITY_PROHIBITED)
        _bool(issues, "occurrence_assignment_allowed", record.occurrence_assignment_allowed, False, C.OCCURRENCE_ASSIGNMENT_PROHIBITED)
        _scope(issues, record.scope, record.non_scope, "compatibility")
        _version(issues, "version", record.version)
        _exact(issues, "lifecycle_state", record.lifecycle_state, PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED, C.LIFECYCLE_STATE_INVALID)
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.ROLE_CONCEPT_COMPATIBILITY, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "compatibility")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_role_constraint(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not FrameRoleConstraint:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact FrameRoleConstraint required")
            return _report(issues)
        _identity(issues, record, "constraint_id")
        _identifier(issues, "frame_key", record.frame_key)
        _text(issues, "role_id", record.role_id)
        _identifier(issues, "role_key", record.role_key)
        if type(record.requirement) is not FrameRoleRequirement:
            _issue(issues, "requirement", C.ROLE_REQUIREMENT_INVALID, "exact FrameRoleRequirement required")
        if type(record.cardinality) is not FrameRoleCardinality:
            _issue(issues, "cardinality", C.ROLE_CARDINALITY_INVALID, "exact FrameRoleCardinality required")
        if record.requirement is FrameRoleRequirement.CONDITIONAL:
            _identifier(issues, "condition_key", record.condition_key)
        elif record.condition_key is not None:
            _issue(issues, "condition_key", C.ROLE_REQUIREMENT_INVALID, "condition_key permitted only for conditional roles")
        _tuple_values(issues, "co_required_role_ids", record.co_required_role_ids, allow_empty=True)
        _tuple_values(issues, "conflicting_role_ids", record.conflicting_role_ids, allow_empty=True)
        _text(issues, "concept_compatibility_ref", record.concept_compatibility_ref)
        _scope(issues, record.scope, record.non_scope, "constraint")
        _version(issues, "version", record.version)
        _exact(issues, "lifecycle_state", record.lifecycle_state, PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED, C.LIFECYCLE_STATE_INVALID)
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _bool(issues, "occurrence_assignment_allowed", record.occurrence_assignment_allowed, False, C.OCCURRENCE_ASSIGNMENT_PROHIBITED)
        _bool(issues, "gate_outcome_created", record.gate_outcome_created, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "authority_satisfied", record.authority_satisfied, False, C.FRAME_COMPLETION_PERMISSION_COLLAPSE)
        _bool(issues, "capability_argument_created", record.capability_argument_created, False, C.CAPABILITY_REFERENCE_PROHIBITED)
        _bool(issues, "execution_authorized", record.execution_authorized, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        if record.requirement is FrameRoleRequirement.REQUIRED and record.cardinality in (
            FrameRoleCardinality.ZERO_OR_ONE,
            FrameRoleCardinality.ZERO_OR_MORE,
        ):
            _issue(issues, "cardinality", C.ROLE_CARDINALITY_INVALID, "required role cardinality must require at least one")
        if record.requirement is FrameRoleRequirement.PROHIBITED and record.cardinality not in (
            FrameRoleCardinality.ZERO_OR_ONE,
            FrameRoleCardinality.ZERO_OR_MORE,
        ):
            _issue(issues, "cardinality", C.ROLE_CARDINALITY_INVALID, "prohibited role cardinality must permit zero")
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.FRAME_ROLE_CONSTRAINT, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "constraint")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_frame(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not PredicateFrameIdentity:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact PredicateFrameIdentity required")
            return _report(issues)
        _identity(issues, record, "frame_id")
        _text(issues, "namespace_id", record.namespace_id)
        _identifier(issues, "frame_key", record.frame_key)
        _text(issues, "preferred_label", record.preferred_label)
        _text(issues, "definition", record.definition)
        _text(issues, "linked_action_root_id", record.linked_action_root_id)
        _identifier(issues, "linked_action_root_key", record.linked_action_root_key)
        _text(issues, "linked_predicate_id", record.linked_predicate_id)
        _identifier(issues, "linked_predicate_key", record.linked_predicate_key)
        _text(issues, "purpose", record.purpose)
        _scope(issues, record.scope, record.non_scope, "frame")
        _version(issues, "version", record.version)
        if type(record.lifecycle_state) is not PredicateFrameLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle enum required")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        for field_name in (
            "required_role_constraint_refs", "optional_role_constraint_refs",
            "prohibited_role_constraint_refs", "conditional_role_constraint_refs",
            "role_cardinality_constraint_refs", "role_co_requirement_refs",
            "role_conflict_refs", "role_concept_compatibility_refs",
            "scope_constraint_refs", "authority_dependencies", "evidence_boundaries",
            "memory_boundaries", "delivery_boundaries", "runtime_boundaries",
            "external_resource_boundaries",
        ):
            _tuple_values(issues, field_name, getattr(record, field_name), allow_empty=field_name in (
                "conditional_role_constraint_refs", "role_co_requirement_refs", "role_conflict_refs"
            ))
        _tuple_values(issues, "permitted_speech_acts", record.permitted_speech_acts, item_type=FrameSpeechAct)
        if type(record.effect_classification) is not FrameEffectClassification:
            _issue(issues, "effect_classification", C.EFFECT_CLASSIFICATION_INVALID, "exact effect classification required")
        _exact(issues, "capability_reference_status", record.capability_reference_status, FrameCapabilityReferenceStatus.DEFERRED_TO_SLICE38F, C.CAPABILITY_REFERENCE_PROHIBITED)
        _exact(issues, "capability_reference_refs", record.capability_reference_refs, (), C.CAPABILITY_REFERENCE_PROHIBITED)
        for field_name in (
            "unknown_frame_policy", "incomplete_frame_policy", "ambiguous_frame_policy",
            "conflicted_frame_policy", "unsupported_frame_policy",
        ):
            _text(issues, field_name, getattr(record, field_name))
        _bool(issues, "structurally_complete_is_permission", record.structurally_complete_is_permission, False, C.FRAME_COMPLETION_PERMISSION_COLLAPSE)
        _bool(issues, "occurrence_frame_selection_allowed", record.occurrence_frame_selection_allowed, False, C.FRAME_SELECTION_PROHIBITED)
        _bool(issues, "occurrence_role_assignment_allowed", record.occurrence_role_assignment_allowed, False, C.OCCURRENCE_ASSIGNMENT_PROHIBITED)
        _bool(issues, "frame_completion_allowed", record.frame_completion_allowed, False, C.FRAME_SELECTION_PROHIBITED)
        _bool(issues, "capability_binding_allowed", record.capability_binding_allowed, False, C.CAPABILITY_REFERENCE_PROHIBITED)
        _bool(issues, "gate_outcome_created", record.gate_outcome_created, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "execution_authorized", record.execution_authorized, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.PREDICATE_FRAME_IDENTITY, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "frame")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_state_policy(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not FrameStructuralStatePolicy:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact FrameStructuralStatePolicy required")
            return _report(issues)
        _identity(issues, record, "policy_id")
        if type(record.state) is not PredicateFrameStructuralState:
            _issue(issues, "state", C.STRUCTURAL_STATE_POLICY_INVALID, "exact structural-state enum required")
        _text(issues, "definition", record.definition)
        _tuple_values(issues, "trigger_conditions", record.trigger_conditions)
        _tuple_values(issues, "preserved_obligations", record.preserved_obligations)
        _tuple_values(issues, "prohibited_consequences", record.prohibited_consequences)
        _bool(issues, "gate_outcome_created", record.gate_outcome_created, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "permission_created", record.permission_created, False, C.FRAME_COMPLETION_PERMISSION_COLLAPSE)
        _bool(issues, "capability_binding_created", record.capability_binding_created, False, C.CAPABILITY_REFERENCE_PROHIBITED)
        _bool(issues, "execution_authorized", record.execution_authorized, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _version(issues, "version", record.version)
        _exact(issues, "lifecycle_state", record.lifecycle_state, PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED, C.LIFECYCLE_STATE_INVALID)
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.STRUCTURAL_STATE_POLICY, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "state_policy")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_authority(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not PredicateFrameLifecycleAuthorityRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact PredicateFrameLifecycleAuthorityRecord required")
            return _report(issues)
        _identity(issues, record, "authority_id")
        _identifier(issues, "authority_key", record.authority_key)
        _text(issues, "decision_owner", record.decision_owner)
        _tuple_values(issues, "authority_basis", record.authority_basis)
        _tuple_values(issues, "approved_scope", record.approved_scope)
        _tuple_values(issues, "prohibited_scope", record.prohibited_scope)
        _bool(issues, "human_approval", record.human_approval, True, C.HUMAN_APPROVAL_REQUIRED)
        _bool(issues, "non_llm_decision", record.non_llm_decision, True, C.NON_LLM_PROVENANCE_REQUIRED)
        _bool(issues, "automatic_transition_allowed", record.automatic_transition_allowed, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "implementation_authorized", record.implementation_authorized, True, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "capability_authorized", record.capability_authorized, False, C.CAPABILITY_REFERENCE_PROHIBITED)
        _bool(issues, "action_authorized", record.action_authorized, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _version(issues, "version", record.version)
        _exact(issues, "lifecycle_state", record.lifecycle_state, PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED, C.LIFECYCLE_STATE_INVALID)
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.LIFECYCLE_AUTHORITY, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "authority")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_transition(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not PredicateFrameLifecycleTransitionRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact PredicateFrameLifecycleTransitionRecord required")
            return _report(issues)
        _identity(issues, record, "transition_id")
        for field_name in (
            "frame_lineage_id", "source_frame_id", "target_frame_id", "reason", "authority_record_ref"
        ):
            _text(issues, field_name, getattr(record, field_name))
        _version(issues, "source_version", record.source_version)
        _version(issues, "target_version", record.target_version)
        if not version_advances(record.source_version, record.target_version):
            _issue(issues, "target_version", C.VERSION_NOT_ADVANCING, "target version must advance")
        if not transition_allowed(record.from_state, record.to_state, record.transition_kind):
            _issue(issues, "transition", C.TRANSITION_NOT_PERMITTED, "transition not in closed law")
        _scope(issues, record.scope, record.non_scope, "transition")
        _provenance_refs(issues, "provenance_refs", record.provenance_refs)
        _bool(issues, "human_approval", record.human_approval, True, C.HUMAN_APPROVAL_REQUIRED)
        _bool(issues, "prior_record_preserved", record.prior_record_preserved, True, C.PRIOR_RECORD_NOT_PRESERVED)
        _bool(issues, "automatic_transition", record.automatic_transition, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "in_place_mutation_performed", record.in_place_mutation_performed, False, C.IN_PLACE_MUTATION_PROHIBITED)
        _bool(issues, "frame_selection_performed", record.frame_selection_performed, False, C.FRAME_SELECTION_PROHIBITED)
        _bool(issues, "role_assignment_performed", record.role_assignment_performed, False, C.OCCURRENCE_ASSIGNMENT_PROHIBITED)
        _bool(issues, "capability_binding_performed", record.capability_binding_performed, False, C.CAPABILITY_REFERENCE_PROHIBITED)
        _bool(issues, "gate_outcome_created", record.gate_outcome_created, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "runtime_authority_supplied", record.runtime_authority_supplied, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.LIFECYCLE_TRANSITION, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "transition")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_manifest(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not PredicateFrameRegistryManifest:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact PredicateFrameRegistryManifest required")
            return _report(issues)
        _identity(issues, record, "manifest_id")
        _identifier(issues, "registry_id", record.registry_id)
        _text(issues, "namespace_id", record.namespace_id)
        for field_name in (
            "frame_refs", "frame_keys", "role_constraint_refs", "compatibility_refs",
            "structural_state_policy_refs", "transition_refs", "provenance_refs",
            "provenance_refs_manifest",
        ):
            _tuple_values(issues, field_name, getattr(record, field_name))
        for field_name, expected in (
            ("admitted_frame_count", 5),
            ("role_constraint_count", 55),
            ("compatibility_rule_count", 55),
            ("structural_state_policy_count", 6),
            ("transition_count", 5),
            ("active_correction_count", 0),
            ("active_conflict_count", 0),
        ):
            _exact(issues, field_name, getattr(record, field_name), expected)
        false_fields = (
            "source_term_lookup_installed", "occurrence_frame_selection_installed",
            "occurrence_role_assignment_installed", "candidate_meaning_creation_installed",
            "selected_meaning_installed", "gate_outcome_installed",
            "capability_reference_population_installed", "capability_routing_installed",
            "route_registration_installed", "tool_activation_installed",
            "action_execution_installed", "evidence_validation_installed",
            "memory_access_installed", "rendering_installed", "delivery_installed",
            "external_resource_loading_installed", "nearest_known_frame_substitution_installed",
            "semantic_similarity_installed", "llm_authority_installed",
        )
        for field_name in false_fields:
            _bool(issues, field_name, getattr(record, field_name), False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _bool(issues, "registry_read_only", record.registry_read_only, True, C.REGISTRY_NOT_READ_ONLY)
        _bool(issues, "registry_closed", record.registry_closed, True, C.REGISTRY_NOT_CLOSED)
        _bool(issues, "exact_identity_lookup_only", record.exact_identity_lookup_only, True, C.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED)
        _version(issues, "version", record.version)
        _exact(issues, "lifecycle_state", record.lifecycle_state, PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED, C.LIFECYCLE_STATE_INVALID)
        _exact(issues, "resource_kind", record.resource_kind, PredicateFrameResourceKind.REGISTRY_MANIFEST, C.RESOURCE_KIND_MISMATCH)
        _schema(issues, record, "manifest")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_registry(record: object) -> PredicateFrameValidationReport:
    issues: list[PredicateFrameValidationIssue] = []
    try:
        if type(record) is not PredicateFrameRegistry:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact PredicateFrameRegistry required")
            return _report(issues)
        _exact(issues, "manifest", record.manifest, MANIFEST)
        _exact(issues, "current_namespace", record.current_namespace, CURRENT_NAMESPACE)
        _exact(issues, "admitted_frames", record.admitted_frames, ADMITTED_FRAMES)
        _exact(issues, "frame_histories", record.frame_histories, FRAME_HISTORIES)
        _exact(issues, "role_constraints", record.role_constraints, ROLE_CONSTRAINTS)
        _exact(issues, "compatibility_rules", record.compatibility_rules, COMPATIBILITY_RULES)
        _exact(issues, "structural_state_policies", record.structural_state_policies, STRUCTURAL_STATE_POLICIES)
        _exact(issues, "authority_records", record.authority_records, (ADMISSION_AUTHORITY,))
        _exact(issues, "transitions", record.transitions, TRANSITIONS)
        _exact(issues, "provenance_records", record.provenance_records, PROVENANCE_RECORDS)

        frame_ids = tuple(item.frame_id for item in record.admitted_frames)
        frame_keys = tuple(item.frame_key for item in record.admitted_frames)
        constraint_ids = tuple(item.constraint_id for item in record.role_constraints)
        compatibility_ids = tuple(item.compatibility_id for item in record.compatibility_rules)
        state_policy_ids = tuple(item.policy_id for item in record.structural_state_policies)
        transition_ids = tuple(item.transition_id for item in record.transitions)
        for path, values in (
            ("frame_ids", frame_ids), ("frame_keys", frame_keys),
            ("constraint_ids", constraint_ids), ("compatibility_ids", compatibility_ids),
            ("state_policy_ids", state_policy_ids), ("transition_ids", transition_ids),
        ):
            if len(values) != len(set(values)):
                _issue(issues, path, C.DUPLICATE_IDENTITY, "values must be unique")
        _exact(issues, "frame_keys", frame_keys, ADMITTED_PREDICATE_FRAME_KEYS)
        _exact(issues, "manifest.frame_refs", record.manifest.frame_refs, frame_ids)
        _exact(issues, "manifest.frame_keys", record.manifest.frame_keys, frame_keys)
        _exact(issues, "manifest.role_constraint_refs", record.manifest.role_constraint_refs, constraint_ids)
        _exact(issues, "manifest.compatibility_refs", record.manifest.compatibility_refs, compatibility_ids)
        _exact(issues, "manifest.structural_state_policy_refs", record.manifest.structural_state_policy_refs, state_policy_ids)
        _exact(issues, "manifest.transition_refs", record.manifest.transition_refs, transition_ids)

        action_roots = {item.action_root_id: item for item in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_action_roots}
        predicates = {item.predicate_id: item for item in BUILT_IN_ACTION_ROOT_REGISTRY.admitted_predicates}
        roles = {item.role_id: item for item in PARTICIPANT_ROLE_REGISTRY.admitted_roles}
        classes = {item.semantic_class_id: item for item in SEMANTIC_CLASS_RELATION_REGISTRY.semantic_classes}
        provenance_ids = {item.provenance_id for item in record.provenance_records}
        authority_ids = {item.authority_id for item in record.authority_records}
        compatibility_by_id = {item.compatibility_id: item for item in record.compatibility_rules}
        constraints_by_id = {item.constraint_id: item for item in record.role_constraints}

        for index, frame in enumerate(record.admitted_frames):
            prefix = f"admitted_frames[{index}]"
            if frame.namespace_id != record.current_namespace.namespace_id:
                _issue(issues, f"{prefix}.namespace_id", C.REFERENCE_NOT_FOUND, "namespace reference mismatch")
            root = action_roots.get(frame.linked_action_root_id)
            predicate = predicates.get(frame.linked_predicate_id)
            if root is None or root.action_root_key != frame.linked_action_root_key:
                _issue(issues, f"{prefix}.linked_action_root_id", C.ACTION_ROOT_REFERENCE_INVALID, "exact admitted root reference required")
            if predicate is None or predicate.predicate_key != frame.linked_predicate_key:
                _issue(issues, f"{prefix}.linked_predicate_id", C.PREDICATE_REFERENCE_INVALID, "exact admitted predicate reference required")
            if frame.linked_action_root_key != frame.linked_predicate_key:
                _issue(issues, prefix, C.PREDICATE_REFERENCE_INVALID, "root and predicate keys must match")
            if frame.lifecycle_state is not PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED:
                _issue(issues, f"{prefix}.lifecycle_state", C.LIFECYCLE_STATE_INVALID, "current frame must be architecture-admitted")
            if not set(frame.provenance_refs).issubset(provenance_ids):
                _issue(issues, f"{prefix}.provenance_refs", C.PROVENANCE_INVALID, "unknown provenance reference")
            partition_refs = (
                frame.required_role_constraint_refs
                + frame.optional_role_constraint_refs
                + frame.prohibited_role_constraint_refs
                + frame.conditional_role_constraint_refs
            )
            expected_constraints = tuple(
                item.constraint_id for item in record.role_constraints if item.frame_key == frame.frame_key
            )
            if set(partition_refs) != set(expected_constraints) or len(partition_refs) != len(expected_constraints):
                _issue(issues, f"{prefix}.role_constraint_partition", C.ROLE_SET_PARTITION_INVALID, "role constraints must form an exact partition")
            if set(frame.role_cardinality_constraint_refs) != set(expected_constraints):
                _issue(issues, f"{prefix}.role_cardinality_constraint_refs", C.ROLE_CARDINALITY_INVALID, "every role constraint must carry cardinality")
            expected_compatibilities = tuple(
                item.compatibility_id for item in record.compatibility_rules if item.frame_key == frame.frame_key
            )
            if frame.role_concept_compatibility_refs != expected_compatibilities:
                _issue(issues, f"{prefix}.role_concept_compatibility_refs", C.CONCEPT_COMPATIBILITY_INVALID, "exact compatibility set required")

        for index, constraint in enumerate(record.role_constraints):
            prefix = f"role_constraints[{index}]"
            role = roles.get(constraint.role_id)
            if role is None or role.role_key != constraint.role_key:
                _issue(issues, f"{prefix}.role_id", C.ROLE_REFERENCE_INVALID, "exact admitted role reference required")
            compatibility = compatibility_by_id.get(constraint.concept_compatibility_ref)
            if compatibility is None or compatibility.frame_key != constraint.frame_key or compatibility.role_id != constraint.role_id:
                _issue(issues, f"{prefix}.concept_compatibility_ref", C.CONCEPT_COMPATIBILITY_INVALID, "matching compatibility reference required")
            for ref in constraint.co_required_role_ids:
                if ref not in roles or ref == constraint.role_id:
                    _issue(issues, f"{prefix}.co_required_role_ids", C.ROLE_CO_REQUIREMENT_INVALID, "co-required roles must be distinct admitted roles")
            for ref in constraint.conflicting_role_ids:
                if ref not in roles or ref == constraint.role_id:
                    _issue(issues, f"{prefix}.conflicting_role_ids", C.ROLE_CONFLICT_INVALID, "conflicting roles must be distinct admitted roles")

        for index, compatibility in enumerate(record.compatibility_rules):
            prefix = f"compatibility_rules[{index}]"
            role = roles.get(compatibility.role_id)
            if role is None or role.role_key != compatibility.role_key:
                _issue(issues, f"{prefix}.role_id", C.ROLE_REFERENCE_INVALID, "exact admitted role reference required")
            for ref in compatibility.allowed_semantic_class_refs:
                if ref not in classes:
                    _issue(issues, f"{prefix}.allowed_semantic_class_refs", C.CONCEPT_COMPATIBILITY_INVALID, "semantic class reference not admitted")
            if compatibility.allowed_concept_refs:
                _issue(issues, f"{prefix}.allowed_concept_refs", C.CONCEPT_COMPATIBILITY_INVALID, "Slice 38E exact concept allowlists must remain unpopulated")

        expected_states = tuple(PredicateFrameStructuralState)
        actual_states = tuple(item.state for item in record.structural_state_policies)
        _exact(issues, "structural_state_policies.states", actual_states, expected_states, C.STRUCTURAL_STATE_POLICY_INVALID)

        for index, history in enumerate(record.frame_histories):
            if type(history) is not tuple or len(history) != 2:
                _issue(issues, f"frame_histories[{index}]", C.ANCESTRY_REQUIRED, "two-version history required")
                continue
            source, target = history
            if type(source) is not PredicateFrameIdentity or type(target) is not PredicateFrameIdentity:
                _issue(issues, f"frame_histories[{index}]", C.TYPE_MISMATCH, "frame identities required")
                continue
            if expected_lineage_id(source) != expected_lineage_id(target):
                _issue(issues, f"frame_histories[{index}]", C.LINEAGE_MISMATCH, "frame lineage must remain stable")
            if not version_advances(source.version, target.version):
                _issue(issues, f"frame_histories[{index}]", C.VERSION_NOT_ADVANCING, "frame version must advance")
            if source.lifecycle_state is not PredicateFrameLifecycleState.CANDIDATE or target.lifecycle_state is not PredicateFrameLifecycleState.ARCHITECTURE_ADMITTED:
                _issue(issues, f"frame_histories[{index}]", C.LIFECYCLE_STATE_INVALID, "candidate to architecture-admitted history required")

        for index, transition in enumerate(record.transitions):
            if transition.authority_record_ref not in authority_ids:
                _issue(issues, f"transitions[{index}].authority_record_ref", C.AUTHORITY_RECORD_NOT_FOUND, "transition authority missing")
            if not transition.prior_record_preserved:
                _issue(issues, f"transitions[{index}].prior_record_preserved", C.PRIOR_RECORD_NOT_PRESERVED, "prior record must be preserved")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"registry validator failed closed: {type(error).__name__}")
    return _report(issues)


def assert_valid(report_or_record: object) -> None:
    report = report_or_record if type(report_or_record) is PredicateFrameValidationReport else validate_registry(report_or_record)
    if type(report) is not PredicateFrameValidationReport or not report.ok:
        if type(report) is PredicateFrameValidationReport:
            raise PredicateFrameValidationError(report)
        raise PredicateFrameValidationError(
            _report([PredicateFrameValidationIssue("$", C.TYPE_MISMATCH, "validation report required")])
        )


PUBLIC_VALIDATORS: tuple[Callable[[object], PredicateFrameValidationReport], ...] = (
    validate_provenance,
    validate_namespace,
    validate_compatibility,
    validate_role_constraint,
    validate_frame,
    validate_state_policy,
    validate_authority,
    validate_transition,
    validate_manifest,
    validate_registry,
)
