"""Deterministic structural validation for Slice 37A schema records.

Validation confirms immutable record shape, identity, version, provenance,
lifecycle visibility, exact non-authority declarations, and zero-population
contract state. It does not admit resources or perform semantic resolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any

from .schema import (
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    SLICE37A_DEFERRED_SCOPE,
    SLICE37A_SCHEMA_VERSION,
    SLICE37A_SPEC_ID,
    SLICE37A_SPEC_VERSION,
    ConceptAuthorityProfile,
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
    ConceptRegistrySchemaContract,
    ConceptResourceKind,
    ControlledConceptIdentity,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    LexicalReferenceKind,
    RelationDirection,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
    TermConceptMappingIdentity,
)


_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_VERSION_RE = re.compile(r"^v[0-9]+(?:\.[0-9]+){0,2}$")
_LANGUAGE_TAG_RE = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")


class ConceptSchemaValidationCode(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_VALUE_MISSING = "required_value_missing"
    INVALID_TEXT = "invalid_text"
    INVALID_IDENTIFIER = "invalid_identifier"
    INVALID_VERSION = "invalid_version"
    INVALID_ENUM = "invalid_enum"
    INVALID_TUPLE = "invalid_tuple"
    DUPLICATE_VALUE = "duplicate_value"
    IDENTITY_MISMATCH = "identity_mismatch"
    SCHEMA_VERSION_MISMATCH = "schema_version_mismatch"
    SPEC_MISMATCH = "spec_mismatch"
    PROHIBITED_AUTHORITY_MISMATCH = "prohibited_authority_mismatch"
    AUTHORITY_ENLARGEMENT = "authority_enlargement"
    NONZERO_REGISTRY_POPULATION = "nonzero_registry_population"
    HISTORICAL_BOUNDARY_MISMATCH = "historical_boundary_mismatch"
    SELECTED_MAPPING_PROHIBITED = "selected_mapping_prohibited"
    RELATION_INSTANCE_POPULATION_PROHIBITED = (
        "relation_instance_population_prohibited"
    )


@dataclass(frozen=True, slots=True)
class ConceptSchemaValidationIssue:
    path: str
    code: ConceptSchemaValidationCode
    detail: str


@dataclass(frozen=True, slots=True)
class ConceptSchemaValidationReport:
    ok: bool
    issues: tuple[ConceptSchemaValidationIssue, ...]
    schema_version: str = SLICE37A_SCHEMA_VERSION


class ConceptSchemaValidationError(ValueError):
    def __init__(self, report: ConceptSchemaValidationReport) -> None:
        self.report = report
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in report.issues
        )
        super().__init__(summary or "Slice 37A concept schema validation failed")


def _issue(
    issues: list[ConceptSchemaValidationIssue],
    path: str,
    code: ConceptSchemaValidationCode,
    detail: str,
) -> None:
    issues.append(ConceptSchemaValidationIssue(path=path, code=code, detail=detail))


def _text(
    value: Any,
    *,
    path: str,
    issues: list[ConceptSchemaValidationIssue],
) -> bool:
    if not isinstance(value, str):
        _issue(issues, path, ConceptSchemaValidationCode.TYPE_MISMATCH, "expected str")
        return False
    if not value or not value.strip():
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.REQUIRED_VALUE_MISSING,
            "text must be non-empty",
        )
        return False
    if value != value.strip() or any(ord(character) < 32 for character in value):
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.INVALID_TEXT,
            "text must be trimmed and contain no control characters",
        )
        return False
    return True


def _optional_text(
    value: Any,
    *,
    path: str,
    issues: list[ConceptSchemaValidationIssue],
) -> bool:
    if value is None:
        return True
    return _text(value, path=path, issues=issues)


def _identifier(
    value: Any,
    *,
    path: str,
    issues: list[ConceptSchemaValidationIssue],
) -> bool:
    if not _text(value, path=path, issues=issues):
        return False
    if _IDENTIFIER_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.INVALID_IDENTIFIER,
            "expected [A-Za-z0-9][A-Za-z0-9._:-]*",
        )
        return False
    return True


def _version(
    value: Any,
    *,
    path: str,
    issues: list[ConceptSchemaValidationIssue],
) -> bool:
    if not _text(value, path=path, issues=issues):
        return False
    if _VERSION_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.INVALID_VERSION,
            "expected vN, vN.N or vN.N.N",
        )
        return False
    return True


def _enum(
    value: Any,
    expected_type: type[Enum],
    *,
    path: str,
    issues: list[ConceptSchemaValidationIssue],
) -> bool:
    if not isinstance(value, expected_type):
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.INVALID_ENUM,
            f"expected {expected_type.__name__}",
        )
        return False
    return True


def _text_tuple(
    value: Any,
    *,
    path: str,
    issues: list[ConceptSchemaValidationIssue],
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.INVALID_TUPLE,
            "expected tuple",
        )
        return ()
    valid: list[str] = []
    for index, item in enumerate(value):
        if _text(item, path=f"{path}[{index}]", issues=issues):
            valid.append(item)
    if not allow_empty and not valid:
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.REQUIRED_VALUE_MISSING,
            "tuple must not be empty",
        )
    if len(value) != len(set(value)):
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.DUPLICATE_VALUE,
            "tuple values must be unique",
        )
    return tuple(valid)


def _enum_tuple(
    value: Any,
    expected_type: type[Enum],
    *,
    path: str,
    issues: list[ConceptSchemaValidationIssue],
) -> tuple[Enum, ...]:
    if not isinstance(value, tuple):
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.INVALID_TUPLE,
            "expected tuple",
        )
        return ()
    valid: list[Enum] = []
    for index, item in enumerate(value):
        if _enum(item, expected_type, path=f"{path}[{index}]", issues=issues):
            valid.append(item)
    if len(value) != len(set(value)):
        _issue(
            issues,
            path,
            ConceptSchemaValidationCode.DUPLICATE_VALUE,
            "tuple values must be unique",
        )
    return tuple(valid)


def _common(
    record: Any,
    *,
    identity_field: str,
    expected_kind: ConceptResourceKind,
    issues: list[ConceptSchemaValidationIssue],
) -> None:
    _identifier(getattr(record, identity_field), path=identity_field, issues=issues)
    _enum(record.resource_kind, ConceptResourceKind, path="resource_kind", issues=issues)
    if record.resource_kind is not expected_kind:
        _issue(
            issues,
            "resource_kind",
            ConceptSchemaValidationCode.INVALID_ENUM,
            f"expected {expected_kind.value}",
        )
    if record.schema_version != SLICE37A_SCHEMA_VERSION:
        _issue(
            issues,
            "schema_version",
            ConceptSchemaValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37A_SCHEMA_VERSION}",
        )
    if getattr(record, identity_field) != record.expected_id():
        _issue(
            issues,
            identity_field,
            ConceptSchemaValidationCode.IDENTITY_MISMATCH,
            "record identity does not match canonical body",
        )
    if record.prohibited_authorities != CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES:
        _issue(
            issues,
            "prohibited_authorities",
            ConceptSchemaValidationCode.PROHIBITED_AUTHORITY_MISMATCH,
            "exact Slice 37A non-authority declarations required",
        )


def _namespace_record_common(
    record: Any,
    *,
    identity_field: str,
    expected_kind: ConceptResourceKind,
    issues: list[ConceptSchemaValidationIssue],
) -> None:
    _common(
        record,
        identity_field=identity_field,
        expected_kind=expected_kind,
        issues=issues,
    )
    _identifier(record.namespace_id, path="namespace_id", issues=issues)
    _version(record.version, path="version", issues=issues)
    _enum(
        record.lifecycle_state,
        ConceptLifecycleState,
        path="lifecycle_state",
        issues=issues,
    )
    _identifier(record.provenance_ref, path="provenance_ref", issues=issues)


def validate_concept_authority_profile(
    profile: ConceptAuthorityProfile,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(profile) is not ConceptAuthorityProfile:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact profile type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _identifier(profile.profile_id, path="profile_id", issues=issues)
    if profile.profile_id != profile.expected_id():
        _issue(issues, "profile_id", ConceptSchemaValidationCode.IDENTITY_MISMATCH, "profile identity mismatch")
    if profile.spec_id != SLICE37A_SPEC_ID or profile.spec_version != SLICE37A_SPEC_VERSION:
        _issue(issues, "spec", ConceptSchemaValidationCode.SPEC_MISMATCH, "Slice 37A spec identity mismatch")
    if profile.schema_version != SLICE37A_SCHEMA_VERSION:
        _issue(issues, "schema_version", ConceptSchemaValidationCode.SCHEMA_VERSION_MISMATCH, "schema version mismatch")
    required_true = (
        "disabled_by_default", "explicit_invocation_required", "offline_only",
        "standard_library_only", "deterministic", "immutable_records",
        "exact_version_required", "provenance_required",
        "lifecycle_state_required", "unknown_state_first_class",
        "unresolved_state_first_class", "ambiguity_preserved",
        "scale_is_not_authority",
    )
    required_false = (
        "registry_population_installed", "concept_lookup_allowed",
        "source_occurrence_mapping_allowed", "sense_selection_allowed",
        "semantic_relation_edge_population_allowed",
        "structural_result_consumption_allowed",
        "candidate_meaning_creation_allowed", "selected_meaning_allowed",
        "predicate_authority_allowed", "participant_role_authority_allowed",
        "evidence_validation_allowed", "memory_read_allowed",
        "memory_write_allowed", "external_resource_loading_allowed",
        "llm_allowed", "embedding_allowed", "vector_database_allowed",
        "semantic_similarity_allowed", "rag_allowed", "learned_parser_allowed",
        "neural_classifier_allowed", "api_route_allowed",
        "capability_route_allowed", "tool_activation_allowed",
        "action_execution_allowed", "outward_rendering_allowed",
        "delivery_authorization_allowed", "release_authorized",
        "production_ready",
    )
    for field_name in required_true:
        if getattr(profile, field_name) is not True:
            _issue(issues, field_name, ConceptSchemaValidationCode.AUTHORITY_ENLARGEMENT, "must remain true")
    for field_name in required_false:
        if getattr(profile, field_name) is not False:
            _issue(issues, field_name, ConceptSchemaValidationCode.AUTHORITY_ENLARGEMENT, "must remain false")
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_concept_registry_schema_contract(
    contract: ConceptRegistrySchemaContract,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(contract) is not ConceptRegistrySchemaContract:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact contract type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _identifier(contract.contract_id, path="contract_id", issues=issues)
    if contract.contract_id != contract.expected_id():
        _issue(issues, "contract_id", ConceptSchemaValidationCode.IDENTITY_MISMATCH, "contract identity mismatch")
    if contract.spec_id != SLICE37A_SPEC_ID or contract.spec_version != SLICE37A_SPEC_VERSION:
        _issue(issues, "spec", ConceptSchemaValidationCode.SPEC_MISMATCH, "Slice 37A spec identity mismatch")
    if contract.schema_version != SLICE37A_SCHEMA_VERSION:
        _issue(issues, "schema_version", ConceptSchemaValidationCode.SCHEMA_VERSION_MISMATCH, "schema version mismatch")
    kinds = _enum_tuple(contract.resource_kinds, ConceptResourceKind, path="resource_kinds", issues=issues)
    if kinds != tuple(ConceptResourceKind):
        _issue(issues, "resource_kinds", ConceptSchemaValidationCode.INVALID_TUPLE, "exact resource-kind order required")
    _text_tuple(contract.required_record_families, path="required_record_families", issues=issues, allow_empty=False)
    if contract.prohibited_authorities != CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES:
        _issue(issues, "prohibited_authorities", ConceptSchemaValidationCode.PROHIBITED_AUTHORITY_MISMATCH, "exact boundaries required")
    if contract.deferred_scope != SLICE37A_DEFERRED_SCOPE:
        _issue(issues, "deferred_scope", ConceptSchemaValidationCode.SPEC_MISMATCH, "exact deferred scope required")
    count_fields = (
        "registry_entry_count", "concept_entry_count", "sense_entry_count",
        "lexical_reference_entry_count", "term_mapping_entry_count",
        "semantic_class_entry_count", "relation_family_entry_count",
        "relation_type_entry_count",
    )
    for field_name in count_fields:
        value = getattr(contract, field_name)
        if type(value) is not int or value != 0:
            _issue(issues, field_name, ConceptSchemaValidationCode.NONZERO_REGISTRY_POPULATION, "Slice 37A requires zero entries")
    for field_name in (
        "registry_population_installed", "lookup_installed", "mapping_installed",
        "sense_selection_installed", "relation_edge_population_installed",
        "structural_integration_installed",
    ):
        if getattr(contract, field_name) is not False:
            _issue(issues, field_name, ConceptSchemaValidationCode.AUTHORITY_ENLARGEMENT, "must remain false")
    if contract.historical_slice8_preserved is not True or contract.historical_slice8_superseded is not False:
        _issue(issues, "historical_slice8", ConceptSchemaValidationCode.HISTORICAL_BOUNDARY_MISMATCH, "Slice 8 must remain preserved and unsuperseded")
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_concept_provenance_reference(
    record: ConceptProvenanceReference,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not ConceptProvenanceReference:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact provenance type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _common(record, identity_field="provenance_id", expected_kind=ConceptResourceKind.PROVENANCE_REFERENCE, issues=issues)
    for name in ("authority_document", "authority_section", "source_kind", "source_reference"):
        _text(getattr(record, name), path=name, issues=issues)
    _version(record.version, path="version", issues=issues)
    if record.non_llm_provenance is not True:
        _issue(issues, "non_llm_provenance", ConceptSchemaValidationCode.AUTHORITY_ENLARGEMENT, "must remain true")
    for name in ("external_resource_admitted", "runtime_loaded"):
        if getattr(record, name) is not False:
            _issue(issues, name, ConceptSchemaValidationCode.AUTHORITY_ENLARGEMENT, "must remain false")
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_concept_namespace_identity(
    record: ConceptNamespaceIdentity,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not ConceptNamespaceIdentity:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact namespace type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _common(record, identity_field="namespace_id", expected_kind=ConceptResourceKind.NAMESPACE_IDENTITY, issues=issues)
    for name in ("namespace_key", "label", "definition", "provenance_ref"):
        _text(getattr(record, name), path=name, issues=issues)
    _version(record.version, path="version", issues=issues)
    _enum(record.lifecycle_state, ConceptLifecycleState, path="lifecycle_state", issues=issues)
    for name in ("scope_tags", "permitted_uses", "prohibited_uses"):
        _text_tuple(getattr(record, name), path=name, issues=issues)
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_controlled_concept_identity(
    record: ControlledConceptIdentity,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not ControlledConceptIdentity:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact concept type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _namespace_record_common(record, identity_field="concept_id", expected_kind=ConceptResourceKind.CONCEPT_IDENTITY, issues=issues)
    for name in ("concept_key", "preferred_label", "definition"):
        _text(getattr(record, name), path=name, issues=issues)
    for name in ("semantic_class_refs", "sense_refs", "relation_type_refs", "scope_tags", "permitted_uses", "prohibited_uses"):
        _text_tuple(getattr(record, name), path=name, issues=issues)
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_controlled_sense_identity(
    record: ControlledSenseIdentity,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not ControlledSenseIdentity:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact sense type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _namespace_record_common(record, identity_field="sense_id", expected_kind=ConceptResourceKind.SENSE_IDENTITY, issues=issues)
    for name in ("concept_id", "sense_key", "definition"):
        _text(getattr(record, name), path=name, issues=issues)
    _text_tuple(record.differentiation_basis, path="differentiation_basis", issues=issues, allow_empty=False)
    for name in ("lexical_reference_refs", "scope_tags", "permitted_uses", "prohibited_uses"):
        _text_tuple(getattr(record, name), path=name, issues=issues)
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_controlled_lexical_reference(
    record: ControlledLexicalReference,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not ControlledLexicalReference:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact lexical-reference type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _namespace_record_common(record, identity_field="lexical_reference_id", expected_kind=ConceptResourceKind.LEXICAL_REFERENCE, issues=issues)
    _text(record.exact_form, path="exact_form", issues=issues)
    _enum(record.reference_kind, LexicalReferenceKind, path="reference_kind", issues=issues)
    if not isinstance(record.language_tag, str) or _LANGUAGE_TAG_RE.fullmatch(record.language_tag) is None:
        _issue(issues, "language_tag", ConceptSchemaValidationCode.INVALID_TEXT, "invalid bounded language tag")
    if type(record.case_sensitive) is not bool:
        _issue(issues, "case_sensitive", ConceptSchemaValidationCode.TYPE_MISMATCH, "expected bool")
    _text_tuple(record.scope_tags, path="scope_tags", issues=issues)
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_term_concept_mapping_identity(
    record: TermConceptMappingIdentity,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not TermConceptMappingIdentity:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact mapping type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _common(record, identity_field="mapping_id", expected_kind=ConceptResourceKind.TERM_CONCEPT_MAPPING_IDENTITY, issues=issues)
    for name in ("lexical_reference_id", "provenance_ref"):
        _identifier(getattr(record, name), path=name, issues=issues)
    _version(record.version, path="version", issues=issues)
    _enum(record.lifecycle_state, ConceptLifecycleState, path="lifecycle_state", issues=issues)
    for name in ("namespace_scope", "domain_scope", "concept_candidate_refs", "sense_candidate_refs"):
        _text_tuple(getattr(record, name), path=name, issues=issues)
    if record.occurrence_interpretation_selected is not False or record.selected_concept_ref is not None or record.selected_sense_ref is not None:
        _issue(issues, "selection", ConceptSchemaValidationCode.SELECTED_MAPPING_PROHIBITED, "Slice 37A mapping identity cannot select occurrence meaning")
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_semantic_class_identity(
    record: SemanticClassIdentity,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not SemanticClassIdentity:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact semantic-class type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _namespace_record_common(record, identity_field="semantic_class_id", expected_kind=ConceptResourceKind.SEMANTIC_CLASS_IDENTITY, issues=issues)
    for name in ("class_key", "label", "definition"):
        _text(getattr(record, name), path=name, issues=issues)
    _text_tuple(record.parent_class_refs, path="parent_class_refs", issues=issues)
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_semantic_relation_family_identity(
    record: SemanticRelationFamilyIdentity,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not SemanticRelationFamilyIdentity:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact relation-family type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _namespace_record_common(record, identity_field="relation_family_id", expected_kind=ConceptResourceKind.SEMANTIC_RELATION_FAMILY_IDENTITY, issues=issues)
    for name in ("family_key", "label", "definition"):
        _text(getattr(record, name), path=name, issues=issues)
    return ConceptSchemaValidationReport(not issues, tuple(issues))


def validate_semantic_relation_type_identity(
    record: SemanticRelationTypeIdentity,
) -> ConceptSchemaValidationReport:
    issues: list[ConceptSchemaValidationIssue] = []
    if type(record) is not SemanticRelationTypeIdentity:
        _issue(issues, "$", ConceptSchemaValidationCode.TYPE_MISMATCH, "exact relation-type type required")
        return ConceptSchemaValidationReport(False, tuple(issues))
    _namespace_record_common(record, identity_field="relation_type_id", expected_kind=ConceptResourceKind.SEMANTIC_RELATION_TYPE_IDENTITY, issues=issues)
    for name in ("relation_family_id", "relation_key", "label", "definition"):
        _text(getattr(record, name), path=name, issues=issues)
    _enum(record.direction, RelationDirection, path="direction", issues=issues)
    for name in ("domain_class_refs", "range_class_refs"):
        _text_tuple(getattr(record, name), path=name, issues=issues)
    _optional_text(record.inverse_relation_type_ref, path="inverse_relation_type_ref", issues=issues)
    if record.relation_instances_populated is not False:
        _issue(issues, "relation_instances_populated", ConceptSchemaValidationCode.RELATION_INSTANCE_POPULATION_PROHIBITED, "Slice 37A creates no relation instances")
    return ConceptSchemaValidationReport(not issues, tuple(issues))
