"""Total fail-closed validation for the Slice 38D participant-role registry."""

from __future__ import annotations

from collections import Counter
from typing import Any, Callable
import re

from ..built_in_action_root_registry.registry import registry_manifest as action_root_manifest
from .authority import (
    ADMITTED_PARTICIPANT_ROLE_KEYS,
    ROLE_DEPENDENCY_REFS,
    ROLE_DISTINCTION_DEFINITIONS,
    SLICE38D_AUTHORITY_LIMITATIONS,
    SLICE38D_DECISION_OWNER_REF,
    SLICE38D_DEFERRED_ROLE_CANDIDATES,
    SLICE38D_HUMAN_APPROVAL_REF,
)
from .identity import expected_lineage_id, parse_version, record_id, version_advances
from .lifecycle import transition_allowed
from .records import (
    ADMISSION_AUTHORITY,
    ADMITTED_ROLES,
    CURRENT_NAMESPACE,
    DEPENDENCIES,
    PROVENANCE_RECORDS,
    RELATIONSHIPS,
    ROLE_HISTORIES,
    DEPENDENCY_HISTORIES,
    RELATIONSHIP_HISTORIES,
    TRANSITIONS,
)
from .schema import (
    SLICE38D_ACCEPTED_PARENT_HEAD,
    SLICE38D_ACCEPTED_PARENT_TREE,
    SLICE38D_SCHEMA_VERSION,
    SLICE38D_SLICE38C_R2_EVIDENCE_SHA256,
    SLICE38D_SOURCE_AUTHORITY_PACKET_SHA256,
    SLICE38D_SPEC_ID,
    SLICE38D_SPEC_VERSION,
    ParticipantRoleConflictRecord,
    ParticipantRoleCorrectionRecord,
    ParticipantRoleDependencyKind,
    ParticipantRoleDependencyRecord,
    ParticipantRoleGovernedResource,
    ParticipantRoleIdentity,
    ParticipantRoleLifecycleAuthorityRecord,
    ParticipantRoleLifecycleState,
    ParticipantRoleLifecycleTransitionRecord,
    ParticipantRoleNamespaceIdentity,
    ParticipantRoleProvenanceReference,
    ParticipantRoleRegistry,
    ParticipantRoleRegistryManifest,
    ParticipantRoleRelationshipKind,
    ParticipantRoleRelationshipRecord,
    ParticipantRoleResourceKind,
    ParticipantRoleValidationCode as C,
    ParticipantRoleValidationError,
    ParticipantRoleValidationIssue,
    ParticipantRoleValidationReport,
)

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]*(?::[a-z0-9:_-]+)?$")


def _issue(issues: list[ParticipantRoleValidationIssue], path: str, code: C, detail: str) -> None:
    issues.append(ParticipantRoleValidationIssue(path=path, code=code, detail=detail))


def _report(issues: list[ParticipantRoleValidationIssue]) -> ParticipantRoleValidationReport:
    ordered = tuple(sorted(issues, key=lambda item: (item.path, item.code.value, item.detail)))
    return ParticipantRoleValidationReport(ok=not ordered, issues=ordered)


def _safe_equal(actual: Any, expected: Any) -> bool:
    try:
        return type(actual) is type(expected) and actual == expected
    except Exception:
        return False


def _exact(issues: list[ParticipantRoleValidationIssue], path: str, actual: Any, expected: Any,
           code: C = C.MANIFEST_BOUNDARY_MISMATCH) -> None:
    if not _safe_equal(actual, expected):
        _issue(issues, path, code, f"expected exact value {expected!r}")


def _text(issues: list[ParticipantRoleValidationIssue], path: str, value: Any) -> bool:
    if type(value) is not str or not value or value != value.strip():
        _issue(issues, path, C.INVALID_TEXT, "trimmed non-empty exact str required")
        return False
    return True


def _identifier(issues: list[ParticipantRoleValidationIssue], path: str, value: Any) -> bool:
    if not _text(issues, path, value):
        return False
    if _IDENTIFIER.fullmatch(value) is None:
        _issue(issues, path, C.INVALID_IDENTIFIER, "controlled identifier required")
        return False
    return True


def _tuple_text(issues: list[ParticipantRoleValidationIssue], path: str, value: Any,
                *, allow_empty: bool = False) -> tuple[str, ...]:
    if type(value) is not tuple:
        _issue(issues, path, C.TYPE_MISMATCH, "exact tuple required")
        return ()
    safe: list[str] = []
    for index, item in enumerate(value):
        if _text(issues, f"{path}[{index}]", item):
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


def _enum_tuple(issues: list[ParticipantRoleValidationIssue], path: str, value: Any,
                enum_type: type, *, allow_empty: bool = False) -> tuple[Any, ...]:
    if type(value) is not tuple:
        _issue(issues, path, C.TYPE_MISMATCH, "exact tuple required")
        return ()
    safe: list[Any] = []
    for index, item in enumerate(value):
        if type(item) is not enum_type:
            _issue(issues, f"{path}[{index}]", C.INVALID_ENUM, f"exact {enum_type.__name__} required")
        else:
            safe.append(item)
    if len(safe) != len(set(safe)):
        _issue(issues, path, C.DUPLICATE_VALUE, "enum values must be unique")
    if not allow_empty and not safe:
        _issue(issues, path, C.REQUIRED_VALUE_MISSING, "tuple must not be empty")
    return tuple(safe)


def _scope(issues: list[ParticipantRoleValidationIssue], scope: Any, non_scope: Any, prefix: str) -> None:
    left = _tuple_text(issues, f"{prefix}.scope", scope)
    right = _tuple_text(issues, f"{prefix}.non_scope", non_scope)
    try:
        if set(left) & set(right):
            _issue(issues, prefix, C.SCOPE_OVERLAP, "scope and non-scope must not overlap")
    except Exception:
        _issue(issues, prefix, C.VALIDATOR_FAILED_CLOSED, "scope comparison failed closed")


def _version(issues: list[ParticipantRoleValidationIssue], path: str, value: Any) -> None:
    try:
        parse_version(value)
    except Exception:
        _issue(issues, path, C.INVALID_VERSION, "version must match vMAJOR.MINOR.PATCH")


def _identity(issues: list[ParticipantRoleValidationIssue], record: Any, field: str) -> None:
    try:
        expected = record.expected_id()
    except Exception as error:
        _issue(issues, field, C.IDENTITY_MISMATCH, f"canonical identity failed closed: {type(error).__name__}")
        return
    _exact(issues, field, getattr(record, field, None), expected, C.IDENTITY_MISMATCH)


def _common_resource(issues: list[ParticipantRoleValidationIssue], record: Any, prefix: str) -> None:
    _version(issues, f"{prefix}.version", getattr(record, "version", None))
    if type(getattr(record, "lifecycle_state", None)) is not ParticipantRoleLifecycleState:
        _issue(issues, f"{prefix}.lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle enum required")
    _tuple_text(issues, f"{prefix}.provenance_refs", getattr(record, "provenance_refs", None))
    _scope(issues, getattr(record, "scope", None), getattr(record, "non_scope", None), prefix)
    _exact(issues, f"{prefix}.schema_version", getattr(record, "schema_version", None), SLICE38D_SCHEMA_VERSION,
           C.SCHEMA_VERSION_MISMATCH)


def validate_provenance(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleProvenanceReference:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleProvenanceReference required")
            return _report(issues)
        _identity(issues, record, "provenance_id")
        for field in ("authority_document", "authority_section", "source_kind", "source_reference"):
            _text(issues, field, getattr(record, field))
        _version(issues, "version", record.version)
        _exact(issues, "non_llm_provenance", record.non_llm_provenance, True, C.NON_LLM_PROVENANCE_REQUIRED)
        _exact(issues, "external_resource_admitted", record.external_resource_admitted, False,
               C.EXTERNAL_RESOURCE_AUTHORITY_PROHIBITED)
        _exact(issues, "runtime_loaded", record.runtime_loaded, False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _exact(issues, "implementation_authorized", record.implementation_authorized, False,
               C.RUNTIME_AUTHORITY_PROHIBITED)
        _tuple_text(issues, "prohibited_authorities", record.prohibited_authorities)
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.PROVENANCE_REFERENCE, C.RESOURCE_KIND_MISMATCH)
        _exact(issues, "schema_version", record.schema_version, SLICE38D_SCHEMA_VERSION,
               C.SCHEMA_VERSION_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_namespace(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleNamespaceIdentity:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleNamespaceIdentity required")
            return _report(issues)
        _identity(issues, record, "namespace_id")
        _identifier(issues, "namespace_key", record.namespace_key)
        _text(issues, "preferred_label", record.preferred_label)
        _text(issues, "definition", record.definition)
        _common_resource(issues, record, "namespace")
        _tuple_text(issues, "permitted_uses", record.permitted_uses)
        _tuple_text(issues, "prohibited_uses", record.prohibited_uses)
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.NAMESPACE_IDENTITY, C.RESOURCE_KIND_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_role(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleIdentity:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleIdentity required")
            return _report(issues)
        _identity(issues, record, "role_id")
        _text(issues, "namespace_id", record.namespace_id)
        _identifier(issues, "role_key", record.role_key)
        _text(issues, "preferred_label", record.preferred_label)
        _identifier(issues, "role_category_key", record.role_category_key)
        _text(issues, "definition", record.definition)
        _common_resource(issues, record, "role")
        for field in (
            "frame_dependency_required", "action_root_dependency_required",
            "concept_compatibility_review_required", "semantic_relation_separation_required",
            "grammar_separation_required", "speech_act_separation_required",
            "effect_boundary_review_required", "authority_non_satisfaction_required",
        ):
            _exact(issues, field, getattr(record, field), True, C.DEPENDENCY_BOUNDARY_INVALID)
        _exact(issues, "occurrence_assignment_allowed", record.occurrence_assignment_allowed, False,
               C.ROLE_ASSIGNMENT_PROHIBITED)
        _exact(issues, "role_selection_allowed", record.role_selection_allowed, False,
               C.ROLE_ASSIGNMENT_PROHIBITED)
        for field in ("dependency_refs", "relationship_refs", "correction_refs", "conflict_refs"):
            _tuple_text(issues, field, getattr(record, field), allow_empty=True)
        _text(issues, "unknown_state_policy", record.unknown_state_policy)
        _tuple_text(issues, "permitted_uses", record.permitted_uses)
        _tuple_text(issues, "prohibited_uses", record.prohibited_uses)
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.PARTICIPANT_ROLE_IDENTITY, C.RESOURCE_KIND_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_dependency(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleDependencyRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleDependencyRecord required")
            return _report(issues)
        _identity(issues, record, "dependency_id")
        _identifier(issues, "dependency_key", record.dependency_key)
        _text(issues, "role_id", record.role_id)
        _enum_tuple(issues, "dependency_kinds", record.dependency_kinds, ParticipantRoleDependencyKind)
        _tuple_text(issues, "dependency_refs", record.dependency_refs)
        _text(issues, "definition", record.definition)
        _common_resource(issues, record, "dependency")
        for field in ("satisfied_by_role_identity", "satisfied_by_registry_membership", "runtime_authority_supplied"):
            _exact(issues, field, getattr(record, field), False, C.DEPENDENCY_BOUNDARY_INVALID)
        _tuple_text(issues, "permitted_uses", record.permitted_uses)
        _tuple_text(issues, "prohibited_uses", record.prohibited_uses)
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.ROLE_DEPENDENCY, C.RESOURCE_KIND_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_relationship(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleRelationshipRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleRelationshipRecord required")
            return _report(issues)
        _identity(issues, record, "relationship_id")
        _identifier(issues, "relationship_key", record.relationship_key)
        if type(record.relationship_kind) is not ParticipantRoleRelationshipKind:
            _issue(issues, "relationship_kind", C.INVALID_ENUM, "exact relationship enum required")
        _text(issues, "left_role_id", record.left_role_id)
        _text(issues, "right_role_id", record.right_role_id)
        if _safe_equal(record.left_role_id, record.right_role_id):
            _issue(issues, "right_role_id", C.RELATIONSHIP_BOUNDARY_INVALID, "relationship requires two roles")
        _text(issues, "definition", record.definition)
        _common_resource(issues, record, "relationship")
        _exact(issues, "role_assignment_performed", record.role_assignment_performed, False,
               C.ROLE_ASSIGNMENT_PROHIBITED)
        _exact(issues, "frame_constraint_created", record.frame_constraint_created, False,
               C.FRAME_COMPLETION_PROHIBITED)
        _tuple_text(issues, "permitted_uses", record.permitted_uses)
        _tuple_text(issues, "prohibited_uses", record.prohibited_uses)
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.ROLE_RELATIONSHIP, C.RESOURCE_KIND_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_correction(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleCorrectionRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleCorrectionRecord required")
            return _report(issues)
        _identity(issues, record, "correction_id")
        for field in ("role_lineage_id", "source_role_id", "target_role_id", "authority_record_ref"):
            _text(issues, field, getattr(record, field))
        _version(issues, "source_version", record.source_version)
        _version(issues, "target_version", record.target_version)
        if not version_advances(record.source_version, record.target_version):
            _issue(issues, "target_version", C.VERSION_NOT_ADVANCING, "correction target version must advance")
        _tuple_text(issues, "corrected_fields", record.corrected_fields)
        _text(issues, "reason", record.reason)
        _scope(issues, record.scope, record.non_scope, "correction")
        _tuple_text(issues, "provenance_refs", record.provenance_refs)
        _exact(issues, "prior_record_preserved", record.prior_record_preserved, True, C.PRIOR_RECORD_NOT_PRESERVED)
        _exact(issues, "in_place_mutation_performed", record.in_place_mutation_performed, False,
               C.IN_PLACE_MUTATION_PROHIBITED)
        _exact(issues, "runtime_authority_supplied", record.runtime_authority_supplied, False,
               C.RUNTIME_AUTHORITY_PROHIBITED)
        if type(record.lifecycle_state) is not ParticipantRoleLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle enum required")
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.ROLE_CORRECTION, C.RESOURCE_KIND_MISMATCH)
        _exact(issues, "schema_version", record.schema_version, SLICE38D_SCHEMA_VERSION,
               C.SCHEMA_VERSION_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_conflict(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleConflictRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleConflictRecord required")
            return _report(issues)
        _identity(issues, record, "conflict_id")
        _identifier(issues, "conflict_key", record.conflict_key)
        roles = _tuple_text(issues, "role_refs", record.role_refs)
        if len(roles) < 2:
            _issue(issues, "role_refs", C.CONFLICT_BOUNDARY_INVALID, "at least two roles required")
        _text(issues, "conflict_kind", record.conflict_kind)
        _text(issues, "definition", record.definition)
        _scope(issues, record.scope, record.non_scope, "conflict")
        _tuple_text(issues, "provenance_refs", record.provenance_refs)
        _text(issues, "authority_record_ref", record.authority_record_ref)
        if record.resolved is True:
            _text(issues, "resolution_ref", record.resolution_ref)
        elif record.resolution_ref is not None:
            _issue(issues, "resolution_ref", C.CONFLICT_BOUNDARY_INVALID, "unresolved conflict cannot have resolution")
        for field in ("role_assignment_allowed", "frame_use_allowed", "capability_binding_allowed", "runtime_authority_supplied"):
            _exact(issues, field, getattr(record, field), False, C.CONFLICT_BOUNDARY_INVALID)
        if type(record.lifecycle_state) is not ParticipantRoleLifecycleState:
            _issue(issues, "lifecycle_state", C.LIFECYCLE_STATE_INVALID, "exact lifecycle enum required")
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.ROLE_CONFLICT, C.RESOURCE_KIND_MISMATCH)
        _exact(issues, "schema_version", record.schema_version, SLICE38D_SCHEMA_VERSION,
               C.SCHEMA_VERSION_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_authority(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleLifecycleAuthorityRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact authority record required")
            return _report(issues)
        _identity(issues, record, "authority_id")
        _tuple_text(issues, "authority_provenance_refs", record.authority_provenance_refs)
        for field in ("decision_owner_ref", "human_approval_ref", "reason"):
            _text(issues, field, getattr(record, field))
        _exact(issues, "human_approved", record.human_approved, True, C.HUMAN_APPROVAL_REQUIRED)
        _tuple_text(issues, "scope", record.scope)
        _tuple_text(issues, "affected_record_refs", record.affected_record_refs)
        _tuple_text(issues, "prohibited_uses", record.prohibited_uses)
        _tuple_text(issues, "unresolved_dependency_refs", record.unresolved_dependency_refs)
        for field in (
            "conflict_review_complete", "unknown_state_review_complete", "version_review_complete",
            "scope_non_scope_review_complete", "provenance_review_complete",
            "semantic_relation_boundary_review_complete", "grammar_boundary_review_complete",
            "concept_assignment_boundary_review_complete", "source_span_actor_boundary_review_complete",
            "non_llm_provenance", "registry_population_authorized",
        ):
            _exact(issues, field, getattr(record, field), True, C.HUMAN_APPROVAL_REQUIRED)
        for field in ("role_assignment_authorized", "frame_completion_authorized", "runtime_authorized", "implementation_authorized"):
            _exact(issues, field, getattr(record, field), False, C.RUNTIME_AUTHORITY_PROHIBITED)
        _exact(issues, "resource_kind", record.resource_kind,
               ParticipantRoleResourceKind.LIFECYCLE_AUTHORITY, C.RESOURCE_KIND_MISMATCH)
        _exact(issues, "schema_version", record.schema_version, SLICE38D_SCHEMA_VERSION,
               C.SCHEMA_VERSION_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_transition(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleLifecycleTransitionRecord:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact transition record required")
            return _report(issues)
        _identity(issues, record, "transition_id")
        for field in ("lineage_id", "source_resource_id", "target_resource_id", "authority_record_ref", "reason"):
            _text(issues, field, getattr(record, field))
        if type(record.resource_kind) is not ParticipantRoleResourceKind:
            _issue(issues, "resource_kind", C.RESOURCE_KIND_MISMATCH, "exact resource kind required")
        _version(issues, "source_version", record.source_version)
        _version(issues, "target_version", record.target_version)
        if not version_advances(record.source_version, record.target_version):
            _issue(issues, "target_version", C.VERSION_NOT_ADVANCING, "target version must advance")
        if not transition_allowed(record.from_state, record.to_state, record.transition_kind):
            _issue(issues, "transition_kind", C.TRANSITION_NOT_PERMITTED, "transition is not allowed")
        _tuple_text(issues, "scope", record.scope)
        for field in ("affected_role_refs", "dependency_refs", "correction_refs", "conflict_refs"):
            _tuple_text(issues, field, getattr(record, field), allow_empty=True)
        _exact(issues, "prior_record_preserved", record.prior_record_preserved, True, C.PRIOR_RECORD_NOT_PRESERVED)
        for field, code in (
            ("automatic_transition", C.TRANSITION_NOT_PERMITTED),
            ("in_place_mutation_performed", C.IN_PLACE_MUTATION_PROHIBITED),
            ("nearest_known_substitution_performed", C.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED),
            ("similarity_authority_used", C.SIMILARITY_AUTHORITY_PROHIBITED),
            ("role_assignment_performed", C.ROLE_ASSIGNMENT_PROHIBITED),
            ("runtime_authority_supplied", C.RUNTIME_AUTHORITY_PROHIBITED),
        ):
            _exact(issues, field, getattr(record, field), False, code)
        _exact(issues, "schema_version", record.schema_version, SLICE38D_SCHEMA_VERSION,
               C.SCHEMA_VERSION_MISMATCH)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def validate_manifest(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleRegistryManifest:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleRegistryManifest required")
            return _report(issues)
        _identity(issues, record, "manifest_id")
        _exact(issues, "spec_id", record.spec_id, SLICE38D_SPEC_ID)
        _exact(issues, "spec_version", record.spec_version, SLICE38D_SPEC_VERSION)
        _exact(issues, "schema_version", record.schema_version, SLICE38D_SCHEMA_VERSION,
               C.SCHEMA_VERSION_MISMATCH)
        _exact(issues, "source_authority_packet_sha256", record.source_authority_packet_sha256,
               SLICE38D_SOURCE_AUTHORITY_PACKET_SHA256)
        _exact(issues, "slice38c_r2_evidence_sha256", record.slice38c_r2_evidence_sha256,
               SLICE38D_SLICE38C_R2_EVIDENCE_SHA256)
        _exact(issues, "accepted_parent_head", record.accepted_parent_head, SLICE38D_ACCEPTED_PARENT_HEAD)
        _exact(issues, "accepted_parent_tree", record.accepted_parent_tree, SLICE38D_ACCEPTED_PARENT_TREE)
        _exact(issues, "decision_owner_ref", record.decision_owner_ref, SLICE38D_DECISION_OWNER_REF)
        _exact(issues, "human_approval_ref", record.human_approval_ref, SLICE38D_HUMAN_APPROVAL_REF)
        for field in (
            "human_approved", "registry_population_authorized", "read_only", "closed_set",
            "exact_identity_lookup_allowed", "exact_internal_key_lookup_allowed",
            "correction_schema_supported", "conflict_schema_supported", "dependency_schema_supported",
            "relationship_schema_supported", "lifecycle_history_preserved",
            "predicate_frames_deferred_to_slice38e", "effect_and_capability_references_deferred_to_slice38f",
            "occurrence_candidate_proposal_deferred_to_slice38g", "disabled_integration_deferred_to_slice38h",
        ):
            _exact(issues, field, getattr(record, field), True,
                   C.REGISTRY_NOT_READ_ONLY if field == "read_only" else C.REGISTRY_NOT_CLOSED)
        for field in (
            "surface_form_lookup_allowed", "surface_normalization_allowed",
            "occurrence_role_assignment_installed", "concept_candidate_to_role_assignment_installed",
            "semantic_relation_to_role_conversion_installed", "source_span_to_actor_conversion_installed",
            "grammatical_position_to_role_conversion_installed", "nearest_known_role_substitution_installed",
            "semantic_similarity_installed", "predicate_frame_population_installed", "frame_completion_installed",
            "capability_reference_population_installed", "capability_routing_installed", "route_registration_installed",
            "tool_activation_installed", "action_execution_installed", "evidence_validation_installed",
            "memory_access_installed", "rendering_installed", "delivery_installed",
            "external_resource_loading_installed", "llm_authority_installed",
        ):
            code = C.RUNTIME_AUTHORITY_PROHIBITED
            if field == "occurrence_role_assignment_installed": code = C.ROLE_ASSIGNMENT_PROHIBITED
            elif field == "concept_candidate_to_role_assignment_installed": code = C.CONCEPT_ASSIGNMENT_COLLAPSE
            elif field == "semantic_relation_to_role_conversion_installed": code = C.SEMANTIC_RELATION_COLLAPSE
            elif field == "source_span_to_actor_conversion_installed": code = C.SOURCE_SPAN_ACTOR_COLLAPSE
            elif field == "grammatical_position_to_role_conversion_installed": code = C.GRAMMAR_ROLE_COLLAPSE
            elif field == "nearest_known_role_substitution_installed": code = C.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED
            elif field == "semantic_similarity_installed": code = C.SIMILARITY_AUTHORITY_PROHIBITED
            _exact(issues, field, getattr(record, field), False, code)
        for field in (
            "role_refs", "role_lineage_refs", "role_keys", "dependency_refs", "relationship_refs",
            "transition_refs", "deferred_role_candidates", "authority_limitations",
        ):
            _tuple_text(issues, field, getattr(record, field))
        _tuple_text(issues, "correction_refs", record.correction_refs, allow_empty=True)
        _tuple_text(issues, "conflict_refs", record.conflict_refs, allow_empty=True)
        _exact(issues, "role_keys", record.role_keys, ADMITTED_PARTICIPANT_ROLE_KEYS)
        _exact(issues, "deferred_role_candidates", record.deferred_role_candidates, SLICE38D_DEFERRED_ROLE_CANDIDATES)
        _exact(issues, "authority_limitations", record.authority_limitations, SLICE38D_AUTHORITY_LIMITATIONS)
        _exact(issues, "action_root_registry_manifest_ref", record.action_root_registry_manifest_ref,
               action_root_manifest().manifest_id)
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"validator failed closed: {type(error).__name__}")
    return _report(issues)


def _merge(issues: list[ParticipantRoleValidationIssue], report: ParticipantRoleValidationReport, prefix: str) -> None:
    for item in report.issues:
        _issue(issues, f"{prefix}.{item.path}", item.code, item.detail)


def validate_registry(record: object) -> ParticipantRoleValidationReport:
    issues: list[ParticipantRoleValidationIssue] = []
    try:
        if type(record) is not ParticipantRoleRegistry:
            _issue(issues, "$", C.TYPE_MISMATCH, "exact ParticipantRoleRegistry required")
            return _report(issues)
        _merge(issues, validate_manifest(record.manifest), "manifest")
        _merge(issues, validate_namespace(record.current_namespace), "current_namespace")
        for index, item in enumerate(record.provenance_records):
            _merge(issues, validate_provenance(item), f"provenance_records[{index}]")
        for index, item in enumerate(record.admitted_roles):
            _merge(issues, validate_role(item), f"admitted_roles[{index}]")
        for index, item in enumerate(record.dependencies):
            _merge(issues, validate_dependency(item), f"dependencies[{index}]")
        for index, item in enumerate(record.relationships):
            _merge(issues, validate_relationship(item), f"relationships[{index}]")
        for index, item in enumerate(record.corrections):
            _merge(issues, validate_correction(item), f"corrections[{index}]")
        for index, item in enumerate(record.conflicts):
            _merge(issues, validate_conflict(item), f"conflicts[{index}]")
        for index, item in enumerate(record.authority_records):
            _merge(issues, validate_authority(item), f"authority_records[{index}]")
        for index, item in enumerate(record.transitions):
            _merge(issues, validate_transition(item), f"transitions[{index}]")

        _exact(issues, "current_namespace", record.current_namespace, CURRENT_NAMESPACE)
        _exact(issues, "admitted_roles", record.admitted_roles, ADMITTED_ROLES)
        _exact(issues, "dependencies", record.dependencies, DEPENDENCIES)
        _exact(issues, "relationships", record.relationships, RELATIONSHIPS)
        _exact(issues, "role_histories", record.role_histories, ROLE_HISTORIES)
        _exact(issues, "dependency_histories", record.dependency_histories, DEPENDENCY_HISTORIES)
        _exact(issues, "relationship_histories", record.relationship_histories, RELATIONSHIP_HISTORIES)
        _exact(issues, "corrections", record.corrections, ())
        _exact(issues, "conflicts", record.conflicts, ())
        _exact(issues, "authority_records", record.authority_records, (ADMISSION_AUTHORITY,))
        _exact(issues, "transitions", record.transitions, TRANSITIONS)
        _exact(issues, "provenance_records", record.provenance_records, PROVENANCE_RECORDS)

        role_ids = tuple(role.role_id for role in record.admitted_roles)
        role_keys = tuple(role.role_key for role in record.admitted_roles)
        dependency_ids = tuple(item.dependency_id for item in record.dependencies)
        relationship_ids = tuple(item.relationship_id for item in record.relationships)
        transition_ids = tuple(item.transition_id for item in record.transitions)
        for path, values in (
            ("role_ids", role_ids), ("role_keys", role_keys), ("dependency_ids", dependency_ids),
            ("relationship_ids", relationship_ids), ("transition_ids", transition_ids),
        ):
            if len(values) != len(set(values)):
                _issue(issues, path, C.DUPLICATE_IDENTITY, "values must be unique")
        _exact(issues, "role_count", len(record.admitted_roles), 11)
        _exact(issues, "dependency_count", len(record.dependencies), 11)
        _exact(issues, "relationship_count", len(record.relationships), 5)
        _exact(issues, "correction_count", len(record.corrections), 0)
        _exact(issues, "conflict_count", len(record.conflicts), 0)
        _exact(issues, "transition_count", len(record.transitions), 28)
        _exact(issues, "manifest.role_refs", record.manifest.role_refs, role_ids)
        _exact(issues, "manifest.role_keys", record.manifest.role_keys, role_keys)
        _exact(issues, "manifest.dependency_refs", record.manifest.dependency_refs, dependency_ids)
        _exact(issues, "manifest.relationship_refs", record.manifest.relationship_refs, relationship_ids)
        _exact(issues, "manifest.transition_refs", record.manifest.transition_refs, transition_ids)

        role_by_id = {role.role_id: role for role in record.admitted_roles}
        provenance_ids = {item.provenance_id for item in record.provenance_records}
        authority_ids = {item.authority_id for item in record.authority_records}
        for index, role in enumerate(record.admitted_roles):
            if role.namespace_id != record.current_namespace.namespace_id:
                _issue(issues, f"admitted_roles[{index}].namespace_id", C.REFERENCE_NOT_FOUND,
                       "namespace reference mismatch")
            if not set(role.provenance_refs).issubset(provenance_ids):
                _issue(issues, f"admitted_roles[{index}].provenance_refs", C.PROVENANCE_INVALID,
                       "role provenance reference not found")
            if role.lifecycle_state is not ParticipantRoleLifecycleState.ARCHITECTURE_ADMITTED:
                _issue(issues, f"admitted_roles[{index}].lifecycle_state", C.LIFECYCLE_STATE_INVALID,
                       "current role must be architecture-admitted")
        for index, dependency in enumerate(record.dependencies):
            if dependency.role_id not in role_by_id:
                _issue(issues, f"dependencies[{index}].role_id", C.REFERENCE_NOT_FOUND,
                       "dependency role not found")
            _exact(issues, f"dependencies[{index}].dependency_refs", dependency.dependency_refs,
                   ROLE_DEPENDENCY_REFS, C.DEPENDENCY_BOUNDARY_INVALID)
        expected_relationship_keys = tuple(item.relationship_key for item in ROLE_DISTINCTION_DEFINITIONS)
        actual_relationship_keys = tuple(item.relationship_key for item in record.relationships)
        _exact(issues, "relationship_keys", actual_relationship_keys, expected_relationship_keys)
        for index, relationship in enumerate(record.relationships):
            if relationship.left_role_id not in role_by_id or relationship.right_role_id not in role_by_id:
                _issue(issues, f"relationships[{index}]", C.REFERENCE_NOT_FOUND,
                       "relationship role reference not found")
        for index, transition in enumerate(record.transitions):
            if transition.authority_record_ref not in authority_ids:
                _issue(issues, f"transitions[{index}].authority_record_ref", C.AUTHORITY_RECORD_NOT_FOUND,
                       "transition authority not found")
    except Exception as error:
        _issue(issues, "$", C.VALIDATOR_FAILED_CLOSED, f"registry validator failed closed: {type(error).__name__}")
    return _report(issues)


def assert_valid(report_or_record: object) -> None:
    report = report_or_record if type(report_or_record) is ParticipantRoleValidationReport else validate_registry(report_or_record)
    if type(report) is not ParticipantRoleValidationReport or not report.ok:
        raise ParticipantRoleValidationError(report if type(report) is ParticipantRoleValidationReport else _report([
            ParticipantRoleValidationIssue("$", C.TYPE_MISMATCH, "validation report required")
        ]))


PUBLIC_VALIDATORS: tuple[Callable[[object], ParticipantRoleValidationReport], ...] = (
    validate_provenance, validate_namespace, validate_role, validate_dependency,
    validate_relationship, validate_correction, validate_conflict, validate_authority,
    validate_transition, validate_manifest, validate_registry,
)
