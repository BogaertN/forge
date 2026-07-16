"""Deterministic field, provenance, namespace, scope, and authority validation.

Validation is read-only and fail-closed.  It does not admit resources, perform
lifecycle transitions, populate a registry, interpret source language, select a
sense, access external resources, or create runtime effects.
"""

from __future__ import annotations

import re
from typing import Any, Final

from ..schema import (
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
    ControlledConceptIdentity,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
    TermConceptMappingIdentity,
)
from ..validation import (
    ConceptSchemaValidationReport,
    validate_concept_namespace_identity,
    validate_concept_provenance_reference,
    validate_controlled_concept_identity,
    validate_controlled_lexical_reference,
    validate_controlled_sense_identity,
    validate_semantic_class_identity,
    validate_semantic_relation_family_identity,
    validate_semantic_relation_type_identity,
    validate_term_concept_mapping_identity,
)
from .identity import (
    expected_resource_lineage_id,
    parse_resource_version,
    recompute_resource_id,
    resource_id,
)
from .schema import (
    SLICE37B_SCHEMA_VERSION,
    ConceptGovernanceBatch,
    ConceptGovernanceValidationCode,
    ConceptGovernanceValidationIssue,
    ConceptGovernanceValidationReport,
    ConceptLifecycleAuthorityRecord,
    ConceptLifecycleTransitionRecord,
    GovernedConceptResource,
)


_IDENTIFIER_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"
)
_NAMESPACE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9]*(?::[a-z0-9][a-z0-9._-]*)+$"
)

_ACTIVE_STATES: Final[frozenset[ConceptLifecycleState]] = frozenset(
    {
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
    }
)

_NONOPERATIVE_STATES: Final[frozenset[ConceptLifecycleState]] = frozenset(
    set(ConceptLifecycleState).difference(_ACTIVE_STATES)
)


def _issue(
    issues: list[ConceptGovernanceValidationIssue],
    path: str,
    code: ConceptGovernanceValidationCode,
    detail: str,
) -> None:
    issues.append(
        ConceptGovernanceValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def sorted_issues(
    issues: list[ConceptGovernanceValidationIssue],
) -> tuple[ConceptGovernanceValidationIssue, ...]:
    return tuple(
        sorted(
            issues,
            key=lambda item: (
                item.path,
                item.code.value,
                item.detail,
            ),
        )
    )


def report_from_issues(
    issues: list[ConceptGovernanceValidationIssue],
) -> ConceptGovernanceValidationReport:
    ordered = sorted_issues(issues)
    return ConceptGovernanceValidationReport(
        ok=not ordered,
        issues=ordered,
    )


def _text(
    value: Any,
    *,
    path: str,
    issues: list[ConceptGovernanceValidationIssue],
) -> bool:
    if not isinstance(value, str):
        _issue(
            issues,
            path,
            ConceptGovernanceValidationCode.TYPE_MISMATCH,
            "expected str",
        )
        return False

    if not value or not value.strip():
        _issue(
            issues,
            path,
            ConceptGovernanceValidationCode.REQUIRED_VALUE_MISSING,
            "text must be non-empty",
        )
        return False

    if value != value.strip() or any(
        ord(character) < 32
        for character in value
    ):
        _issue(
            issues,
            path,
            ConceptGovernanceValidationCode.INVALID_TEXT,
            "text must be trimmed and contain no control characters",
        )
        return False

    return True


def _optional_text(
    value: Any,
    *,
    path: str,
    issues: list[ConceptGovernanceValidationIssue],
) -> bool:
    if value is None:
        return True
    return _text(value, path=path, issues=issues)


def _identifier(
    value: Any,
    *,
    path: str,
    issues: list[ConceptGovernanceValidationIssue],
) -> bool:
    if not _text(value, path=path, issues=issues):
        return False

    if _IDENTIFIER_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            ConceptGovernanceValidationCode.INVALID_IDENTIFIER,
            "expected [A-Za-z0-9][A-Za-z0-9._:-]*",
        )
        return False

    return True


def _text_tuple(
    value: Any,
    *,
    path: str,
    issues: list[ConceptGovernanceValidationIssue],
    allow_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _issue(
            issues,
            path,
            ConceptGovernanceValidationCode.TYPE_MISMATCH,
            "expected tuple",
        )
        return ()

    valid: list[str] = []

    for index, item in enumerate(value):
        if _text(
            item,
            path=f"{path}[{index}]",
            issues=issues,
        ):
            valid.append(item)

    if not allow_empty and not valid:
        _issue(
            issues,
            path,
            ConceptGovernanceValidationCode.REQUIRED_VALUE_MISSING,
            "tuple must not be empty",
        )

    if len(value) != len(set(value)):
        _issue(
            issues,
            path,
            ConceptGovernanceValidationCode.DUPLICATE_VALUE,
            "tuple values must be unique",
        )

    return tuple(valid)


def _translate_slice37a_report(
    base_report: ConceptSchemaValidationReport,
    *,
    prefix: str,
    issues: list[ConceptGovernanceValidationIssue],
) -> None:
    for base_issue in base_report.issues:
        code = {
            "identity_mismatch": ConceptGovernanceValidationCode.IDENTITY_MISMATCH,
            "invalid_version": ConceptGovernanceValidationCode.INVALID_VERSION,
            "schema_version_mismatch": (
                ConceptGovernanceValidationCode.SCHEMA_VERSION_MISMATCH
            ),
            "invalid_identifier": (
                ConceptGovernanceValidationCode.INVALID_IDENTIFIER
            ),
            "required_value_missing": (
                ConceptGovernanceValidationCode.REQUIRED_VALUE_MISSING
            ),
            "type_mismatch": ConceptGovernanceValidationCode.TYPE_MISMATCH,
        }.get(
            base_issue.code.value,
            ConceptGovernanceValidationCode.INVALID_TEXT,
        )

        _issue(
            issues,
            f"{prefix}.{base_issue.path}",
            code,
            f"Slice 37A validation: {base_issue.detail}",
        )


def slice37a_validator(
    record: GovernedConceptResource,
):
    validator = {
        ConceptNamespaceIdentity: validate_concept_namespace_identity,
        ControlledConceptIdentity: validate_controlled_concept_identity,
        ControlledSenseIdentity: validate_controlled_sense_identity,
        ControlledLexicalReference: validate_controlled_lexical_reference,
        TermConceptMappingIdentity: validate_term_concept_mapping_identity,
        SemanticClassIdentity: validate_semantic_class_identity,
        SemanticRelationFamilyIdentity: (
            validate_semantic_relation_family_identity
        ),
        SemanticRelationTypeIdentity: validate_semantic_relation_type_identity,
    }.get(type(record))

    if validator is None:
        raise TypeError(
            "unsupported governed concept resource type: "
            f"{type(record).__name__}"
        )

    return validator


def resource_scope_tokens(
    record: GovernedConceptResource,
) -> tuple[str, ...]:
    if isinstance(
        record,
        (
            ConceptNamespaceIdentity,
            ControlledConceptIdentity,
            ControlledSenseIdentity,
            ControlledLexicalReference,
        ),
    ):
        return record.scope_tags

    if isinstance(record, TermConceptMappingIdentity):
        return tuple(
            dict.fromkeys(
                (
                    *record.namespace_scope,
                    *record.domain_scope,
                )
            )
        )

    if isinstance(
        record,
        (
            SemanticClassIdentity,
            SemanticRelationFamilyIdentity,
            SemanticRelationTypeIdentity,
        ),
    ):
        return (record.namespace_id,)

    raise TypeError(
        "unsupported governed concept resource type: "
        f"{type(record).__name__}"
    )


def validate_namespace_key(
    namespace_key: str,
) -> ConceptGovernanceValidationReport:
    issues: list[ConceptGovernanceValidationIssue] = []

    if _text(
        namespace_key,
        path="namespace_key",
        issues=issues,
    ):
        if _NAMESPACE_RE.fullmatch(namespace_key) is None:
            _issue(
                issues,
                "namespace_key",
                ConceptGovernanceValidationCode.INVALID_NAMESPACE,
                "namespace must be lowercase, colon-delimited, and contain "
                "at least two non-empty canonical segments",
            )

        if ".." in namespace_key or "::" in namespace_key:
            _issue(
                issues,
                "namespace_key",
                ConceptGovernanceValidationCode.INVALID_NAMESPACE,
                "namespace may not contain empty or parent-like segments",
            )

    return report_from_issues(issues)


def validate_provenance_record(
    record: ConceptProvenanceReference,
) -> ConceptGovernanceValidationReport:
    issues: list[ConceptGovernanceValidationIssue] = []

    base = validate_concept_provenance_reference(record)
    _translate_slice37a_report(
        base,
        prefix="provenance",
        issues=issues,
    )

    try:
        parse_resource_version(record.version)
    except (TypeError, ValueError) as error:
        _issue(
            issues,
            "provenance.version",
            ConceptGovernanceValidationCode.INVALID_VERSION,
            str(error),
        )

    if record.non_llm_provenance is not True:
        _issue(
            issues,
            "provenance.non_llm_provenance",
            ConceptGovernanceValidationCode.NON_LLM_PROVENANCE_REQUIRED,
            "provenance must remain explicitly non-LLM",
        )

    if (
        record.external_resource_admitted is not False
        or record.runtime_loaded is not False
    ):
        _issue(
            issues,
            "provenance",
            ConceptGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED,
            "Slice 37B provenance cannot admit or load external resources",
        )

    return report_from_issues(issues)


def validate_governed_resource(
    record: GovernedConceptResource,
    *,
    provenance_by_id: dict[str, ConceptProvenanceReference] | None = None,
) -> ConceptGovernanceValidationReport:
    issues: list[ConceptGovernanceValidationIssue] = []

    try:
        base = slice37a_validator(record)(record)
    except TypeError as error:
        _issue(
            issues,
            "$",
            ConceptGovernanceValidationCode.TYPE_MISMATCH,
            str(error),
        )
        return report_from_issues(issues)

    _translate_slice37a_report(
        base,
        prefix=type(record).__name__,
        issues=issues,
    )

    try:
        expected_id = recompute_resource_id(record)
    except (TypeError, ValueError) as error:
        _issue(
            issues,
            "resource_id",
            ConceptGovernanceValidationCode.IDENTITY_MISMATCH,
            str(error),
        )
    else:
        if resource_id(record) != expected_id:
            _issue(
                issues,
                "resource_id",
                ConceptGovernanceValidationCode.IDENTITY_MISMATCH,
                "record ID does not match the canonical version body",
            )

    try:
        expected_resource_lineage_id(record)
    except (TypeError, ValueError) as error:
        _issue(
            issues,
            "lineage_id",
            ConceptGovernanceValidationCode.LINEAGE_MISMATCH,
            str(error),
        )

    try:
        parse_resource_version(record.version)
    except (TypeError, ValueError) as error:
        _issue(
            issues,
            "version",
            ConceptGovernanceValidationCode.INVALID_VERSION,
            str(error),
        )

    if not isinstance(record.lifecycle_state, ConceptLifecycleState):
        _issue(
            issues,
            "lifecycle_state",
            ConceptGovernanceValidationCode.LIFECYCLE_STATE_INVALID,
            "explicit ConceptLifecycleState is required",
        )

    scope_tokens = resource_scope_tokens(record)
    _text_tuple(
        scope_tokens,
        path="scope",
        issues=issues,
        allow_empty=False,
    )

    if type(record) is ConceptNamespaceIdentity:
        namespace_report = validate_namespace_key(record.namespace_key)
        issues.extend(namespace_report.issues)

    if provenance_by_id is not None:
        provenance = provenance_by_id.get(record.provenance_ref)

        if provenance is None:
            _issue(
                issues,
                "provenance_ref",
                ConceptGovernanceValidationCode.PROVENANCE_NOT_FOUND,
                f"no provenance record found for {record.provenance_ref!r}",
            )
        else:
            provenance_report = validate_provenance_record(provenance)

            for item in provenance_report.issues:
                _issue(
                    issues,
                    f"provenance_ref.{item.path}",
                    item.code,
                    item.detail,
                )

    if record.lifecycle_state in _ACTIVE_STATES:
        if hasattr(record, "permitted_uses"):
            _text_tuple(
                getattr(record, "permitted_uses"),
                path="permitted_uses",
                issues=issues,
                allow_empty=False,
            )

        if hasattr(record, "prohibited_uses"):
            _text_tuple(
                getattr(record, "prohibited_uses"),
                path="prohibited_uses",
                issues=issues,
                allow_empty=False,
            )

    return report_from_issues(issues)


def validate_lifecycle_authority_record(
    record: ConceptLifecycleAuthorityRecord,
    *,
    provenance_by_id: dict[str, ConceptProvenanceReference] | None = None,
) -> ConceptGovernanceValidationReport:
    issues: list[ConceptGovernanceValidationIssue] = []

    if type(record) is not ConceptLifecycleAuthorityRecord:
        _issue(
            issues,
            "$",
            ConceptGovernanceValidationCode.TYPE_MISMATCH,
            "exact ConceptLifecycleAuthorityRecord required",
        )
        return report_from_issues(issues)

    _identifier(
        record.authority_id,
        path="authority_id",
        issues=issues,
    )

    if record.schema_version != SLICE37B_SCHEMA_VERSION:
        _issue(
            issues,
            "schema_version",
            ConceptGovernanceValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37B_SCHEMA_VERSION}",
        )

    if record.authority_id != record.expected_id():
        _issue(
            issues,
            "authority_id",
            ConceptGovernanceValidationCode.IDENTITY_MISMATCH,
            "authority identity does not match canonical body",
        )

    for field_name in (
        "authority_provenance_ref",
        "decision_owner_ref",
        "human_approval_ref",
        "reason",
    ):
        _text(
            getattr(record, field_name),
            path=field_name,
            issues=issues,
        )

    for field_name, allow_empty in (
        ("scope", False),
        ("affected_record_refs", False),
        ("prohibited_uses", False),
        ("unresolved_dependency_refs", True),
        ("missing_authority_refs", True),
    ):
        _text_tuple(
            getattr(record, field_name),
            path=field_name,
            issues=issues,
            allow_empty=allow_empty,
        )

    if record.human_approved is not True:
        _issue(
            issues,
            "human_approved",
            ConceptGovernanceValidationCode.HUMAN_APPROVAL_REQUIRED,
            "every material lifecycle decision requires explicit human approval",
        )

    if record.non_llm_provenance is not True:
        _issue(
            issues,
            "non_llm_provenance",
            ConceptGovernanceValidationCode.NON_LLM_PROVENANCE_REQUIRED,
            "lifecycle authority must remain explicitly non-LLM",
        )

    if (
        record.runtime_authorized is not False
        or record.implementation_authorized is not False
        or record.registry_population_authorized is not False
    ):
        _issue(
            issues,
            "authority",
            ConceptGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED,
            "Slice 37B authority cannot authorize runtime, implementation, "
            "or registry population",
        )

    _optional_text(
        record.external_resource_decision_ref,
        path="external_resource_decision_ref",
        issues=issues,
    )

    if record.external_resource_decision_ref is not None:
        _issue(
            issues,
            "external_resource_decision_ref",
            ConceptGovernanceValidationCode.EXTERNAL_RESOURCE_AUTHORITY_PROHIBITED,
            "Slice 37B does not incorporate Document 8 resource decisions",
        )

    if provenance_by_id is not None:
        provenance = provenance_by_id.get(
            record.authority_provenance_ref
        )

        if provenance is None:
            _issue(
                issues,
                "authority_provenance_ref",
                ConceptGovernanceValidationCode.PROVENANCE_NOT_FOUND,
                "authority provenance record is missing",
            )
        else:
            provenance_report = validate_provenance_record(provenance)

            for item in provenance_report.issues:
                _issue(
                    issues,
                    f"authority_provenance_ref.{item.path}",
                    item.code,
                    item.detail,
                )

    return report_from_issues(issues)


def validate_governance_batch_shape(
    batch: ConceptGovernanceBatch,
) -> ConceptGovernanceValidationReport:
    issues: list[ConceptGovernanceValidationIssue] = []

    if type(batch) is not ConceptGovernanceBatch:
        _issue(
            issues,
            "$",
            ConceptGovernanceValidationCode.TYPE_MISMATCH,
            "exact ConceptGovernanceBatch required",
        )
        return report_from_issues(issues)

    _identifier(
        batch.batch_id,
        path="batch_id",
        issues=issues,
    )

    if batch.batch_id != batch.expected_id():
        _issue(
            issues,
            "batch_id",
            ConceptGovernanceValidationCode.IDENTITY_MISMATCH,
            "batch identity does not match canonical body",
        )

    if batch.schema_version != SLICE37B_SCHEMA_VERSION:
        _issue(
            issues,
            "schema_version",
            ConceptGovernanceValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37B_SCHEMA_VERSION}",
        )

    for field_name in (
        "provenance_records",
        "resources",
        "authority_records",
        "transitions",
    ):
        if not isinstance(getattr(batch, field_name), tuple):
            _issue(
                issues,
                field_name,
                ConceptGovernanceValidationCode.TYPE_MISMATCH,
                "expected tuple",
            )

    for field_name in (
        "registry_population_installed",
        "lookup_installed",
        "occurrence_mapping_installed",
        "sense_selection_installed",
        "relation_instance_population_installed",
        "structural_integration_installed",
        "runtime_activation_installed",
    ):
        if getattr(batch, field_name) is not False:
            _issue(
                issues,
                field_name,
                ConceptGovernanceValidationCode.REGISTRY_POPULATION_PROHIBITED,
                "Slice 37B installs validation law only",
            )

    return report_from_issues(issues)


def active_lifecycle_states() -> frozenset[ConceptLifecycleState]:
    return _ACTIVE_STATES


def nonoperative_lifecycle_states() -> frozenset[ConceptLifecycleState]:
    return _NONOPERATIVE_STATES
