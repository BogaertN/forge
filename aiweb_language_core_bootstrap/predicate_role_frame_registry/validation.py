"""Fail-closed deterministic validation for Slice 38A schema records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any

from .schema import (
    PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    SLICE38A_DEFERRED_SCOPE,
    SLICE38A_SCHEMA_VERSION,
    SLICE38A_SPEC_ID,
    SLICE38A_SPEC_VERSION,
    ActionRootIdentity,
    PredicateAuthorityProfile,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
    PredicateRegistrySchemaContract,
    PredicateResourceKind,
)


_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_VERSION_RE = re.compile(r"^v[0-9]+(?:\.[0-9]+){0,2}$")


class PredicateSchemaValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_ENUM = "invalid_enum"
    INVALID_TUPLE = "invalid_tuple"
    DUPLICATE_VALUE = "duplicate_value"
    OVERLAPPING_SCOPE = "overlapping_scope"
    IDENTITY_MISMATCH = "identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    SPEC_MISMATCH = "spec_mismatch"
    PROHIBITED_AUTHORITY_MISMATCH = "prohibited_authority_mismatch"
    AUTHORITY_ENLARGEMENT = "authority_enlargement"
    NONZERO_REGISTRY_POPULATION = "nonzero_registry_population"
    DEPENDENCY_BOUNDARY_MISMATCH = "dependency_boundary_mismatch"
    OCCURRENCE_SELECTION_PROHIBITED = "occurrence_selection_prohibited"
    EXECUTION_AUTHORITY_PROHIBITED = "execution_authority_prohibited"
    SLICE37_BOUNDARY_MISMATCH = "slice37_boundary_mismatch"


@dataclass(frozen=True, slots=True)
class PredicateSchemaValidationIssue:
    path: str
    code: PredicateSchemaValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class PredicateSchemaValidationReport:
    ok: bool
    issues: tuple[PredicateSchemaValidationIssue, ...]
    schema_version: str = SLICE38A_SCHEMA_VERSION


class PredicateSchemaValidationError(ValueError):
    def __init__(self, report: PredicateSchemaValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 38A predicate schema validation failed")


def _issue(issues: list[PredicateSchemaValidationIssue], path: str,
           code: PredicateSchemaValidationCode, detail: str) -> None:
    issues.append(PredicateSchemaValidationIssue(path=path, code=code, detail=detail))


def _report(issues: list[PredicateSchemaValidationIssue]) -> PredicateSchemaValidationReport:
    return PredicateSchemaValidationReport(ok=not issues, issues=tuple(issues))


def _text(value: Any, *, path: str,
          issues: list[PredicateSchemaValidationIssue]) -> bool:
    if not isinstance(value, str):
        _issue(issues, path, PredicateSchemaValidationCode.TYPE_MISMATCH, "expected str")
        return False
    if not value or not value.strip():
        _issue(issues, path, PredicateSchemaValidationCode.REQUIRED_VALUE_MISSING,
               "text must be non-empty")
        return False
    if value != value.strip() or any(ord(character) < 32 for character in value):
        _issue(issues, path, PredicateSchemaValidationCode.INVALID_TEXT,
               "text must be trimmed and contain no control characters")
        return False
    return True


def _identifier(value: Any, *, path: str,
                issues: list[PredicateSchemaValidationIssue]) -> bool:
    if not _text(value, path=path, issues=issues):
        return False
    if _IDENTIFIER_RE.fullmatch(value) is None:
        _issue(issues, path, PredicateSchemaValidationCode.INVALID_IDENTIFIER,
               "expected [A-Za-z0-9][A-Za-z0-9._:-]*")
        return False
    return True


def _version(value: Any, *, path: str,
             issues: list[PredicateSchemaValidationIssue]) -> bool:
    if not _text(value, path=path, issues=issues):
        return False
    if _VERSION_RE.fullmatch(value) is None:
        _issue(issues, path, PredicateSchemaValidationCode.INVALID_VERSION,
               "expected vN, vN.N or vN.N.N")
        return False
    return True


def _enum(value: Any, expected: type[Enum], *, path: str,
          issues: list[PredicateSchemaValidationIssue]) -> bool:
    if not isinstance(value, expected):
        _issue(issues, path, PredicateSchemaValidationCode.INVALID_ENUM,
               f"expected {expected.__name__}")
        return False
    return True


def _text_tuple(value: Any, *, path: str,
                issues: list[PredicateSchemaValidationIssue],
                allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _issue(issues, path, PredicateSchemaValidationCode.INVALID_TUPLE, "expected tuple")
        return ()
    valid: list[str] = []
    for index, item in enumerate(value):
        if _text(item, path=f"{path}[{index}]", issues=issues):
            valid.append(item)
    if not allow_empty and not valid:
        _issue(issues, path, PredicateSchemaValidationCode.REQUIRED_VALUE_MISSING,
               "tuple must not be empty")
    if len(value) != len(set(value)):
        _issue(issues, path, PredicateSchemaValidationCode.DUPLICATE_VALUE,
               "tuple values must be unique")
    return tuple(valid)


def _scope_pair(scope: Any, non_scope: Any, *,
                issues: list[PredicateSchemaValidationIssue]) -> None:
    valid_scope = _text_tuple(scope, path="scope", issues=issues, allow_empty=False)
    valid_non_scope = _text_tuple(non_scope, path="non_scope", issues=issues, allow_empty=False)
    overlap = set(valid_scope) & set(valid_non_scope)
    if overlap:
        _issue(issues, "scope/non_scope", PredicateSchemaValidationCode.OVERLAPPING_SCOPE,
               f"overlap prohibited: {sorted(overlap)}")


def _common(record: Any, *, identity_field: str,
            expected_kind: PredicateResourceKind,
            issues: list[PredicateSchemaValidationIssue]) -> None:
    _identifier(getattr(record, identity_field), path=identity_field, issues=issues)
    _enum(record.resource_kind, PredicateResourceKind, path="resource_kind", issues=issues)
    if record.resource_kind is not expected_kind:
        _issue(issues, "resource_kind", PredicateSchemaValidationCode.INVALID_ENUM,
               f"expected {expected_kind.value}")
    if record.schema_version != SLICE38A_SCHEMA_VERSION:
        _issue(issues, "schema_version", PredicateSchemaValidationCode.SCHEMA_VERSION_MISMATCH,
               f"expected {SLICE38A_SCHEMA_VERSION}")
    if getattr(record, identity_field) != record.expected_id():
        _issue(issues, identity_field, PredicateSchemaValidationCode.IDENTITY_MISMATCH,
               "record identity does not match canonical body")
    if record.prohibited_authorities != PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES:
        _issue(issues, "prohibited_authorities",
               PredicateSchemaValidationCode.PROHIBITED_AUTHORITY_MISMATCH,
               "exact Slice 38A non-authority declarations required")


def validate_predicate_authority_profile(record: object) -> PredicateSchemaValidationReport:
    issues: list[PredicateSchemaValidationIssue] = []
    if not isinstance(record, PredicateAuthorityProfile):
        _issue(issues, "$", PredicateSchemaValidationCode.TYPE_MISMATCH,
               "expected PredicateAuthorityProfile")
        return _report(issues)
    _identifier(record.profile_id, path="profile_id", issues=issues)
    if record.profile_id != record.expected_id():
        _issue(issues, "profile_id", PredicateSchemaValidationCode.IDENTITY_MISMATCH,
               "profile identity does not match canonical body")
    if record.spec_id != SLICE38A_SPEC_ID or record.spec_version != SLICE38A_SPEC_VERSION:
        _issue(issues, "spec", PredicateSchemaValidationCode.SPEC_MISMATCH,
               "exact Slice 38A specification identity required")
    if record.schema_version != SLICE38A_SCHEMA_VERSION:
        _issue(issues, "schema_version", PredicateSchemaValidationCode.SCHEMA_VERSION_MISMATCH,
               "exact Slice 38A schema version required")

    required_true = (
        "disabled_by_default", "explicit_invocation_required", "offline_only",
        "standard_library_only", "deterministic", "immutable_records",
        "exact_version_required", "provenance_required", "lifecycle_state_required",
        "scope_non_scope_required", "unknown_state_first_class",
        "unresolved_state_first_class", "unsupported_state_first_class",
        "ambiguity_preserved", "action_authority_separated",
        "predicate_frame_dependency_required", "participant_role_dependency_required",
        "speech_act_separation_required", "effect_boundary_dependency_required",
        "capability_non_invocation_required", "scale_is_not_authority",
    )
    required_false = (
        "registry_population_installed", "action_root_lookup_allowed",
        "predicate_selection_allowed", "occurrence_interpretation_allowed",
        "participant_role_population_allowed", "role_assignment_allowed",
        "predicate_frame_population_allowed", "frame_completion_allowed",
        "capability_family_reference_population_allowed",
        "candidate_meaning_creation_allowed", "selected_meaning_allowed",
        "selected_predicate_allowed", "selected_frame_allowed",
        "evidence_validation_allowed", "memory_read_allowed", "memory_write_allowed",
        "external_resource_loading_allowed", "llm_allowed", "embedding_allowed",
        "vector_database_allowed", "semantic_similarity_allowed", "rag_allowed",
        "learned_parser_allowed", "neural_classifier_allowed", "api_route_allowed",
        "capability_route_allowed", "tool_activation_allowed", "action_execution_allowed",
        "outward_rendering_allowed", "delivery_authorization_allowed",
        "release_authorized", "production_ready",
    )
    for field in required_true:
        if getattr(record, field) is not True:
            _issue(issues, field, PredicateSchemaValidationCode.AUTHORITY_ENLARGEMENT,
                   "required preservation boundary must remain true")
    for field in required_false:
        if getattr(record, field) is not False:
            _issue(issues, field, PredicateSchemaValidationCode.AUTHORITY_ENLARGEMENT,
                   "authority-bearing field must remain false")
    return _report(issues)


def validate_predicate_registry_schema_contract(record: object) -> PredicateSchemaValidationReport:
    issues: list[PredicateSchemaValidationIssue] = []
    if not isinstance(record, PredicateRegistrySchemaContract):
        _issue(issues, "$", PredicateSchemaValidationCode.TYPE_MISMATCH,
               "expected PredicateRegistrySchemaContract")
        return _report(issues)
    _identifier(record.contract_id, path="contract_id", issues=issues)
    if record.contract_id != record.expected_id():
        _issue(issues, "contract_id", PredicateSchemaValidationCode.IDENTITY_MISMATCH,
               "contract identity does not match canonical body")
    if record.resource_kinds != tuple(PredicateResourceKind):
        _issue(issues, "resource_kinds", PredicateSchemaValidationCode.INVALID_TUPLE,
               "exact resource-kind order required")
    if record.prohibited_authorities != PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES:
        _issue(issues, "prohibited_authorities",
               PredicateSchemaValidationCode.PROHIBITED_AUTHORITY_MISMATCH,
               "exact Slice 38A non-authority declarations required")
    if record.deferred_scope != SLICE38A_DEFERRED_SCOPE:
        _issue(issues, "deferred_scope", PredicateSchemaValidationCode.SPEC_MISMATCH,
               "exact Slice 38A deferred scope required")
    for field in (
        "registry_entry_count", "namespace_entry_count",
        "action_root_entry_count", "predicate_entry_count",
    ):
        value = getattr(record, field)
        if type(value) is not int or value != 0:
            _issue(issues, field, PredicateSchemaValidationCode.NONZERO_REGISTRY_POPULATION,
                   "schema-only contract requires zero entries")
    for field in ("action_root_schema_defined", "predicate_identity_schema_defined",
                  "slice37_boundaries_preserved"):
        if getattr(record, field) is not True:
            _issue(issues, field, PredicateSchemaValidationCode.SLICE37_BOUNDARY_MISMATCH,
                   "required schema/preservation flag must remain true")
    for field in (
        "registry_population_installed", "action_root_lookup_installed",
        "predicate_selection_installed", "participant_role_schema_installed",
        "predicate_frame_schema_installed", "capability_reference_schema_installed",
        "source_occurrence_integration_installed", "selected_predicate_installed",
        "action_authority_installed", "slice37_runtime_superseded",
    ):
        if getattr(record, field) is not False:
            _issue(issues, field, PredicateSchemaValidationCode.AUTHORITY_ENLARGEMENT,
                   "deferred or authority-bearing flag must remain false")
    if record.spec_id != SLICE38A_SPEC_ID or record.spec_version != SLICE38A_SPEC_VERSION:
        _issue(issues, "spec", PredicateSchemaValidationCode.SPEC_MISMATCH,
               "exact Slice 38A specification identity required")
    if record.schema_version != SLICE38A_SCHEMA_VERSION:
        _issue(issues, "schema_version", PredicateSchemaValidationCode.SCHEMA_VERSION_MISMATCH,
               "exact Slice 38A schema version required")
    return _report(issues)


def validate_predicate_provenance_reference(record: object) -> PredicateSchemaValidationReport:
    issues: list[PredicateSchemaValidationIssue] = []
    if not isinstance(record, PredicateProvenanceReference):
        _issue(issues, "$", PredicateSchemaValidationCode.TYPE_MISMATCH,
               "expected PredicateProvenanceReference")
        return _report(issues)
    _common(record, identity_field="provenance_id",
            expected_kind=PredicateResourceKind.PROVENANCE_REFERENCE, issues=issues)
    for field in ("authority_document", "authority_section", "source_kind", "source_reference"):
        _text(getattr(record, field), path=field, issues=issues)
    _version(record.version, path="version", issues=issues)
    if record.non_llm_provenance is not True:
        _issue(issues, "non_llm_provenance", PredicateSchemaValidationCode.AUTHORITY_ENLARGEMENT,
               "non-LLM provenance is required")
    for field in ("external_resource_admitted", "runtime_loaded", "implementation_authorized"):
        if getattr(record, field) is not False:
            _issue(issues, field, PredicateSchemaValidationCode.AUTHORITY_ENLARGEMENT,
                   "schema provenance cannot admit or activate implementation")
    return _report(issues)


def validate_predicate_namespace_identity(record: object) -> PredicateSchemaValidationReport:
    issues: list[PredicateSchemaValidationIssue] = []
    if not isinstance(record, PredicateNamespaceIdentity):
        _issue(issues, "$", PredicateSchemaValidationCode.TYPE_MISMATCH,
               "expected PredicateNamespaceIdentity")
        return _report(issues)
    _common(record, identity_field="namespace_id",
            expected_kind=PredicateResourceKind.NAMESPACE_IDENTITY, issues=issues)
    _identifier(record.namespace_key, path="namespace_key", issues=issues)
    for field in ("label", "definition", "unknown_state_policy"):
        _text(getattr(record, field), path=field, issues=issues)
    _scope_pair(record.scope, record.non_scope, issues=issues)
    _version(record.version, path="version", issues=issues)
    _enum(record.lifecycle_state, PredicateLifecycleState,
          path="lifecycle_state", issues=issues)
    _identifier(record.provenance_ref, path="provenance_ref", issues=issues)
    _text_tuple(record.permitted_uses, path="permitted_uses", issues=issues,
                allow_empty=False)
    _text_tuple(record.prohibited_uses, path="prohibited_uses", issues=issues,
                allow_empty=False)
    return _report(issues)


def validate_action_root_identity(record: object) -> PredicateSchemaValidationReport:
    issues: list[PredicateSchemaValidationIssue] = []
    if not isinstance(record, ActionRootIdentity):
        _issue(issues, "$", PredicateSchemaValidationCode.TYPE_MISMATCH,
               "expected ActionRootIdentity")
        return _report(issues)
    _common(record, identity_field="action_root_id",
            expected_kind=PredicateResourceKind.ACTION_ROOT_IDENTITY, issues=issues)
    _identifier(record.namespace_id, path="namespace_id", issues=issues)
    _identifier(record.action_root_key, path="action_root_key", issues=issues)
    for field in ("preferred_label", "definition", "unknown_state_policy"):
        _text(getattr(record, field), path=field, issues=issues)
    _scope_pair(record.scope, record.non_scope, issues=issues)
    _version(record.version, path="version", issues=issues)
    _enum(record.lifecycle_state, PredicateLifecycleState,
          path="lifecycle_state", issues=issues)
    _identifier(record.provenance_ref, path="provenance_ref", issues=issues)
    _text_tuple(record.concept_identity_refs, path="concept_identity_refs", issues=issues)
    _text_tuple(record.permitted_uses, path="permitted_uses", issues=issues,
                allow_empty=False)
    _text_tuple(record.prohibited_uses, path="prohibited_uses", issues=issues,
                allow_empty=False)
    for field in (
        "frame_dependency_required", "participant_role_dependency_required",
        "speech_act_separation_required", "effect_boundary_dependency_required",
        "capability_non_invocation_required",
    ):
        if getattr(record, field) is not True:
            _issue(issues, field, PredicateSchemaValidationCode.DEPENDENCY_BOUNDARY_MISMATCH,
                   "required predicate architecture dependency must remain true")
    if record.occurrence_selection_allowed is not False:
        _issue(issues, "occurrence_selection_allowed",
               PredicateSchemaValidationCode.OCCURRENCE_SELECTION_PROHIBITED,
               "Slice 38A cannot select an occurrence-level action root")
    if record.execution_authorized is not False:
        _issue(issues, "execution_authorized",
               PredicateSchemaValidationCode.EXECUTION_AUTHORITY_PROHIBITED,
               "action-root identity cannot authorize execution")
    return _report(issues)


def validate_predicate_identity(record: object) -> PredicateSchemaValidationReport:
    issues: list[PredicateSchemaValidationIssue] = []
    if not isinstance(record, PredicateIdentity):
        _issue(issues, "$", PredicateSchemaValidationCode.TYPE_MISMATCH,
               "expected PredicateIdentity")
        return _report(issues)
    _common(record, identity_field="predicate_id",
            expected_kind=PredicateResourceKind.PREDICATE_IDENTITY, issues=issues)
    for field in ("action_root_id", "namespace_id", "predicate_key", "provenance_ref"):
        _identifier(getattr(record, field), path=field, issues=issues)
    for field in ("preferred_label", "definition", "unknown_state_policy"):
        _text(getattr(record, field), path=field, issues=issues)
    _scope_pair(record.scope, record.non_scope, issues=issues)
    _version(record.version, path="version", issues=issues)
    _enum(record.lifecycle_state, PredicateLifecycleState,
          path="lifecycle_state", issues=issues)
    for field in (
        "concept_identity_refs", "participant_role_schema_refs",
        "predicate_frame_schema_refs", "effect_boundary_refs",
        "capability_family_reference_refs",
    ):
        _text_tuple(getattr(record, field), path=field, issues=issues)
    _text_tuple(record.permitted_uses, path="permitted_uses", issues=issues,
                allow_empty=False)
    _text_tuple(record.prohibited_uses, path="prohibited_uses", issues=issues,
                allow_empty=False)
    for field in (
        "participant_role_dependency_required", "predicate_frame_dependency_required",
        "speech_act_separation_required", "capability_non_invocation_required",
    ):
        if getattr(record, field) is not True:
            _issue(issues, field, PredicateSchemaValidationCode.DEPENDENCY_BOUNDARY_MISMATCH,
                   "required predicate dependency must remain true")
    if record.occurrence_selection_allowed is not False or record.selected_for_occurrence is not False:
        _issue(issues, "occurrence_selection",
               PredicateSchemaValidationCode.OCCURRENCE_SELECTION_PROHIBITED,
               "Slice 38A cannot select a predicate for a source occurrence")
    if record.execution_authorized is not False:
        _issue(issues, "execution_authorized",
               PredicateSchemaValidationCode.EXECUTION_AUTHORITY_PROHIBITED,
               "predicate identity cannot authorize execution")
    return _report(issues)
