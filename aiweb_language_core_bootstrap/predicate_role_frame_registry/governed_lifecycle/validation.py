"""Fail-closed deterministic validation for Slice 38B governance records."""

from __future__ import annotations

import re
from typing import Any, Final

from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
    PredicateResourceKind,
)
from ..validation import (
    PredicateSchemaValidationReport,
    validate_action_root_identity,
    validate_predicate_identity,
    validate_predicate_namespace_identity,
    validate_predicate_provenance_reference,
)
from .identity import parse_resource_version, resource_id
from .schema import (
    SLICE38B_SCHEMA_VERSION,
    GovernedPredicateResource,
    PredicateGovernanceBatch,
    PredicateGovernanceValidationCode,
    PredicateGovernanceValidationIssue,
    PredicateGovernanceValidationReport,
    PredicateLifecycleAuthorityRecord,
    PredicateLifecycleTransitionKind,
    PredicateLifecycleTransitionRecord,
)


_IDENTIFIER_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"
)
_NAMESPACE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]*(?::[A-Za-z0-9._-]+)+$"
)

_ACTIVE_STATES: Final[frozenset[PredicateLifecycleState]] = frozenset(
    {
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
    }
)
_NONOPERATIVE_STATES: Final[frozenset[PredicateLifecycleState]] = frozenset(
    set(PredicateLifecycleState) - set(_ACTIVE_STATES)
)


def _issue(
    issues: list[PredicateGovernanceValidationIssue],
    path: str,
    code: PredicateGovernanceValidationCode,
    detail: str,
) -> None:
    issues.append(
        PredicateGovernanceValidationIssue(path=path, code=code, detail=detail)
    )


def sorted_issues(
    issues: list[PredicateGovernanceValidationIssue]
    | tuple[PredicateGovernanceValidationIssue, ...],
) -> tuple[PredicateGovernanceValidationIssue, ...]:
    return tuple(
        sorted(
            issues,
            key=lambda issue: (issue.path, issue.code.value, issue.detail),
        )
    )


def report_from_issues(
    issues: list[PredicateGovernanceValidationIssue]
    | tuple[PredicateGovernanceValidationIssue, ...],
) -> PredicateGovernanceValidationReport:
    ordered = sorted_issues(issues)
    return PredicateGovernanceValidationReport(ok=not ordered, issues=ordered)


def _text(
    value: Any,
    *,
    path: str,
    issues: list[PredicateGovernanceValidationIssue],
) -> bool:
    if type(value) is not str:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "expected str",
        )
        return False
    if not value or not value.strip():
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.REQUIRED_VALUE_MISSING,
            "text must be non-empty",
        )
        return False
    if value != value.strip() or any(ord(character) < 32 for character in value):
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.INVALID_TEXT,
            "text must be trimmed and contain no control characters",
        )
        return False
    return True


def _identifier(
    value: Any,
    *,
    path: str,
    issues: list[PredicateGovernanceValidationIssue],
) -> bool:
    if not _text(value, path=path, issues=issues):
        return False
    if _IDENTIFIER_RE.fullmatch(value) is None:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.INVALID_IDENTIFIER,
            "expected [A-Za-z0-9][A-Za-z0-9._:-]*",
        )
        return False
    return True


def _safe_expected_id(
    record: object,
    *,
    actual_id: object,
    path: str,
    label: str,
    issues: list[PredicateGovernanceValidationIssue],
) -> bool:
    try:
        expected_id = record.expected_id()  # type: ignore[attr-defined]
    except Exception as error:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            f"{label} canonical identity could not be computed: {error}",
        )
        return False
    if actual_id != expected_id:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.IDENTITY_MISMATCH,
            f"{label} identity does not match canonical body",
        )
        return False
    return True


def _exact_bool(
    value: Any,
    *,
    path: str,
    issues: list[PredicateGovernanceValidationIssue],
) -> bool:
    if type(value) is not bool:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "expected bool",
        )
        return False
    return True


def validate_namespace_key(value: Any) -> bool:
    return type(value) is str and _NAMESPACE_RE.fullmatch(value) is not None


def _tuple_text(
    value: Any,
    *,
    path: str,
    issues: list[PredicateGovernanceValidationIssue],
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if type(value) is not tuple:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "expected tuple",
        )
        return ()

    valid: list[str] = []
    seen: set[str] = set()
    duplicate_found = False
    for index, item in enumerate(value):
        if _text(item, path=f"{path}[{index}]", issues=issues):
            valid.append(item)
            if item in seen:
                duplicate_found = True
            else:
                seen.add(item)

    if not allow_empty and not valid:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.REQUIRED_VALUE_MISSING,
            "tuple must not be empty",
        )

    if duplicate_found:
        _issue(
            issues,
            path,
            PredicateGovernanceValidationCode.DUPLICATE_VALUE,
            "tuple values must be unique",
        )

    return tuple(valid)


def _translate_slice38a_report(
    base_report: PredicateSchemaValidationReport,
    *,
    prefix: str,
    issues: list[PredicateGovernanceValidationIssue],
) -> None:
    mapping = {
        "type_mismatch": PredicateGovernanceValidationCode.TYPE_MISMATCH,
        "required_value_missing": (
            PredicateGovernanceValidationCode.REQUIRED_VALUE_MISSING
        ),
        "invalid_text": PredicateGovernanceValidationCode.INVALID_TEXT,
        "invalid_identifier": (
            PredicateGovernanceValidationCode.INVALID_IDENTIFIER
        ),
        "invalid_version": PredicateGovernanceValidationCode.INVALID_VERSION,
        "invalid_enum": PredicateGovernanceValidationCode.LIFECYCLE_STATE_INVALID,
        "duplicate_value": PredicateGovernanceValidationCode.DUPLICATE_VALUE,
        "overlapping_scope": PredicateGovernanceValidationCode.SCOPE_OVERLAP,
        "identity_mismatch": PredicateGovernanceValidationCode.IDENTITY_MISMATCH,
        "schema_version_mismatch": (
            PredicateGovernanceValidationCode.SCHEMA_VERSION_MISMATCH
        ),
        "authority_enlargement": (
            PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED
        ),
        "dependency_boundary_mismatch": (
            PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED
        ),
        "occurrence_selection_prohibited": (
            PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED
        ),
        "execution_authority_prohibited": (
            PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED
        ),
    }
    for base_issue in base_report.issues:
        _issue(
            issues,
            f"{prefix}.{base_issue.path}",
            mapping.get(
                base_issue.code.value,
                PredicateGovernanceValidationCode.INVALID_TEXT,
            ),
            f"Slice 38A validation: {base_issue.detail}",
        )


def active_lifecycle_states() -> frozenset[PredicateLifecycleState]:
    return _ACTIVE_STATES


def nonoperative_lifecycle_states() -> frozenset[PredicateLifecycleState]:
    return _NONOPERATIVE_STATES


def resource_scope_tokens(record: GovernedPredicateResource) -> tuple[str, ...]:
    return tuple(record.scope)


def validate_provenance_record(
    record: object,
) -> PredicateGovernanceValidationReport:
    issues: list[PredicateGovernanceValidationIssue] = []
    try:
        base = validate_predicate_provenance_reference(record)
    except Exception as error:
        _issue(
            issues,
            "record",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            f"Slice 38A provenance validation could not inspect malformed input: {error}",
        )
    else:
        _translate_slice38a_report(base, prefix="record", issues=issues)
    if type(record) is not PredicateProvenanceReference:
        return report_from_issues(issues)

    if record.non_llm_provenance is not True:
        _issue(
            issues,
            "record.non_llm_provenance",
            PredicateGovernanceValidationCode.NON_LLM_PROVENANCE_REQUIRED,
            "exact non-LLM provenance is required",
        )
    if record.external_resource_admitted is not False:
        _issue(
            issues,
            "record.external_resource_admitted",
            PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED,
            "Slice 38B cannot admit an external resource",
        )
    if record.runtime_loaded is not False:
        _issue(
            issues,
            "record.runtime_loaded",
            PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED,
            "Slice 38B provenance cannot claim runtime load",
        )
    if record.implementation_authorized is not False:
        _issue(
            issues,
            "record.implementation_authorized",
            PredicateGovernanceValidationCode.IMPLEMENTATION_AUTHORITY_PROHIBITED,
            "Slice 38B provenance cannot authorize implementation",
        )
    return report_from_issues(issues)


def validate_governed_resource(
    record: object,
    *,
    provenance_by_id: dict[str, PredicateProvenanceReference] | None = None,
) -> PredicateGovernanceValidationReport:
    issues: list[PredicateGovernanceValidationIssue] = []

    validator = None
    if type(record) is PredicateNamespaceIdentity:
        validator = validate_predicate_namespace_identity
    elif type(record) is ActionRootIdentity:
        validator = validate_action_root_identity
    elif type(record) is PredicateIdentity:
        validator = validate_predicate_identity
    else:
        _issue(
            issues,
            "$",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "expected an exact Slice 38A namespace, action-root, or predicate record",
        )
        return report_from_issues(issues)

    try:
        base = validator(record)
    except Exception as error:
        _issue(
            issues,
            "record",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            f"Slice 38A resource validation could not inspect malformed input: {error}",
        )
    else:
        _translate_slice38a_report(base, prefix="record", issues=issues)

    try:
        parse_resource_version(record.version)
    except (TypeError, ValueError) as error:
        _issue(
            issues,
            "record.version",
            PredicateGovernanceValidationCode.INVALID_VERSION,
            str(error),
        )

    if not isinstance(record.lifecycle_state, PredicateLifecycleState):
        _issue(
            issues,
            "record.lifecycle_state",
            PredicateGovernanceValidationCode.LIFECYCLE_STATE_INVALID,
            "explicit PredicateLifecycleState required",
        )

    scope = _tuple_text(
        record.scope,
        path="record.scope",
        issues=issues,
        allow_empty=False,
    )
    non_scope = _tuple_text(
        record.non_scope,
        path="record.non_scope",
        issues=issues,
        allow_empty=False,
    )
    if not scope:
        _issue(
            issues,
            "record.scope",
            PredicateGovernanceValidationCode.SCOPE_REQUIRED,
            "governed resources require explicit scope",
        )
    if not non_scope:
        _issue(
            issues,
            "record.non_scope",
            PredicateGovernanceValidationCode.NON_SCOPE_REQUIRED,
            "governed resources require explicit non-scope",
        )
    overlap = frozenset(scope) & frozenset(non_scope)
    if overlap:
        _issue(
            issues,
            "record.scope/non_scope",
            PredicateGovernanceValidationCode.SCOPE_OVERLAP,
            f"scope and non-scope overlap: {sorted(overlap)}",
        )

    _tuple_text(
        record.prohibited_uses,
        path="record.prohibited_uses",
        issues=issues,
        allow_empty=False,
    )
    _identifier(
        record.provenance_ref,
        path="record.provenance_ref",
        issues=issues,
    )

    if provenance_by_id is not None and type(provenance_by_id) is not dict:
        _issue(
            issues,
            "provenance_by_id",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "provenance index must be an exact dict-like custody map",
        )
    elif provenance_by_id is not None and type(record.provenance_ref) is str:
        provenance = provenance_by_id.get(record.provenance_ref)
        if provenance is None:
            _issue(
                issues,
                "record.provenance_ref",
                PredicateGovernanceValidationCode.PROVENANCE_NOT_FOUND,
                "referenced provenance record is absent",
            )
        else:
            provenance_report = validate_provenance_record(provenance)
            if not provenance_report.ok:
                for issue in provenance_report.issues:
                    _issue(
                        issues,
                        f"provenance.{issue.path}",
                        PredicateGovernanceValidationCode.PROVENANCE_INVALID,
                        issue.detail,
                    )

    return report_from_issues(issues)


def validate_lifecycle_authority_record(
    record: object,
    *,
    provenance_by_id: dict[str, PredicateProvenanceReference] | None = None,
) -> PredicateGovernanceValidationReport:
    issues: list[PredicateGovernanceValidationIssue] = []

    if type(record) is not PredicateLifecycleAuthorityRecord:
        _issue(
            issues,
            "$",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "exact PredicateLifecycleAuthorityRecord required",
        )
        return report_from_issues(issues)

    _identifier(record.authority_id, path="authority_id", issues=issues)
    _safe_expected_id(
        record,
        actual_id=record.authority_id,
        path="authority_id",
        label="authority",
        issues=issues,
    )
    if record.schema_version != SLICE38B_SCHEMA_VERSION:
        _issue(
            issues,
            "schema_version",
            PredicateGovernanceValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE38B_SCHEMA_VERSION}",
        )

    for field in (
        "authority_provenance_ref",
        "decision_owner_ref",
        "human_approval_ref",
        "reason",
    ):
        _text(getattr(record, field), path=field, issues=issues)

    _tuple_text(record.scope, path="scope", issues=issues, allow_empty=False)
    _tuple_text(
        record.affected_record_refs,
        path="affected_record_refs",
        issues=issues,
        allow_empty=False,
    )
    _tuple_text(
        record.prohibited_uses,
        path="prohibited_uses",
        issues=issues,
        allow_empty=False,
    )
    _tuple_text(
        record.unresolved_dependency_refs,
        path="unresolved_dependency_refs",
        issues=issues,
    )
    _tuple_text(
        record.missing_authority_refs,
        path="missing_authority_refs",
        issues=issues,
    )

    if record.human_approved is not True:
        _issue(
            issues,
            "human_approved",
            PredicateGovernanceValidationCode.HUMAN_APPROVAL_REQUIRED,
            "explicit human approval is required",
        )
    if record.non_llm_provenance is not True:
        _issue(
            issues,
            "non_llm_provenance",
            PredicateGovernanceValidationCode.NON_LLM_PROVENANCE_REQUIRED,
            "authority must have non-LLM provenance",
        )

    exact_boolean_fields = (
        "human_approved",
        "conflict_review_complete",
        "unknown_state_review_complete",
        "later_dependency_review_complete",
        "version_compatibility_review_complete",
        "scope_non_scope_review_complete",
        "provenance_review_complete",
        "lifecycle_review_complete",
        "non_llm_provenance",
        "nearest_known_substitution_allowed",
        "semantic_similarity_authority_allowed",
        "runtime_authorized",
        "implementation_authorized",
        "registry_population_authorized",
    )
    for field in exact_boolean_fields:
        _exact_bool(getattr(record, field), path=field, issues=issues)

    for field in (
        "version_compatibility_review_complete",
        "scope_non_scope_review_complete",
        "provenance_review_complete",
        "lifecycle_review_complete",
    ):
        if getattr(record, field) is not True:
            _issue(
                issues,
                field,
                PredicateGovernanceValidationCode.REVIEW_INCOMPLETE,
                "mandatory Slice 38B review must be complete",
            )

    if record.nearest_known_substitution_allowed is not False:
        _issue(
            issues,
            "nearest_known_substitution_allowed",
            PredicateGovernanceValidationCode.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED,
            "nearest-known substitution authority is permanently false",
        )
    if record.semantic_similarity_authority_allowed is not False:
        _issue(
            issues,
            "semantic_similarity_authority_allowed",
            PredicateGovernanceValidationCode.SIMILARITY_AUTHORITY_PROHIBITED,
            "semantic similarity cannot become predicate authority",
        )
    if record.runtime_authorized is not False:
        _issue(
            issues,
            "runtime_authorized",
            PredicateGovernanceValidationCode.RUNTIME_AUTHORITY_PROHIBITED,
            "lifecycle authority is not runtime authority",
        )
    if record.implementation_authorized is not False:
        _issue(
            issues,
            "implementation_authorized",
            PredicateGovernanceValidationCode.IMPLEMENTATION_AUTHORITY_PROHIBITED,
            "lifecycle authority cannot authorize implementation",
        )
    if record.registry_population_authorized is not False:
        _issue(
            issues,
            "registry_population_authorized",
            PredicateGovernanceValidationCode.REGISTRY_POPULATION_PROHIBITED,
            "Slice 38B cannot authorize registry population",
        )

    if provenance_by_id is not None and type(provenance_by_id) is not dict:
        _issue(
            issues,
            "provenance_by_id",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "provenance index must be an exact dict-like custody map",
        )
    elif provenance_by_id is not None and type(
        record.authority_provenance_ref
    ) is str:
        provenance = provenance_by_id.get(record.authority_provenance_ref)
        if provenance is None:
            _issue(
                issues,
                "authority_provenance_ref",
                PredicateGovernanceValidationCode.PROVENANCE_NOT_FOUND,
                "authority provenance record is absent",
            )
        else:
            provenance_report = validate_provenance_record(provenance)
            if not provenance_report.ok:
                _issue(
                    issues,
                    "authority_provenance_ref",
                    PredicateGovernanceValidationCode.PROVENANCE_INVALID,
                    "authority provenance record failed validation",
                )

    return report_from_issues(issues)


def validate_lifecycle_transition_record_shape(
    record: object,
) -> PredicateGovernanceValidationReport:
    issues: list[PredicateGovernanceValidationIssue] = []

    if type(record) is not PredicateLifecycleTransitionRecord:
        _issue(
            issues,
            "$",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "exact PredicateLifecycleTransitionRecord required",
        )
        return report_from_issues(issues)

    _identifier(record.transition_id, path="transition_id", issues=issues)
    _safe_expected_id(
        record,
        actual_id=record.transition_id,
        path="transition_id",
        label="transition",
        issues=issues,
    )
    if record.schema_version != SLICE38B_SCHEMA_VERSION:
        _issue(
            issues,
            "schema_version",
            PredicateGovernanceValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE38B_SCHEMA_VERSION}",
        )

    for field in (
        "lineage_id",
        "source_resource_id",
        "target_resource_id",
        "authority_record_ref",
    ):
        _identifier(getattr(record, field), path=field, issues=issues)

    for field in ("source_version", "target_version"):
        value = getattr(record, field)
        try:
            parse_resource_version(value)
        except (TypeError, ValueError) as error:
            _issue(
                issues,
                field,
                PredicateGovernanceValidationCode.INVALID_VERSION,
                str(error),
            )

    if not isinstance(record.resource_kind, PredicateResourceKind):
        _issue(
            issues,
            "resource_kind",
            PredicateGovernanceValidationCode.RESOURCE_KIND_MISMATCH,
            "explicit PredicateResourceKind required",
        )
    for field in ("from_state", "to_state"):
        if not isinstance(getattr(record, field), PredicateLifecycleState):
            _issue(
                issues,
                field,
                PredicateGovernanceValidationCode.LIFECYCLE_STATE_INVALID,
                "explicit PredicateLifecycleState required",
            )
    if not isinstance(
        record.transition_kind, PredicateLifecycleTransitionKind
    ):
        _issue(
            issues,
            "transition_kind",
            PredicateGovernanceValidationCode.TRANSITION_KIND_MISMATCH,
            "explicit PredicateLifecycleTransitionKind required",
        )

    for field in (
        "quarantine_cause_refs",
        "quarantine_release_requirement_refs",
        "resolved_quarantine_cause_refs",
        "blocked_reentry_keys",
    ):
        _tuple_text(getattr(record, field), path=field, issues=issues)

    for field in ("superseding_resource_ref", "prior_disposition_transition_ref"):
        value = getattr(record, field)
        if value is not None:
            _identifier(value, path=field, issues=issues)

    for field in (
        "prior_record_preserved",
        "automatic_transition",
        "in_place_mutation_performed",
        "nearest_known_substitution_performed",
        "similarity_authority_used",
    ):
        _exact_bool(getattr(record, field), path=field, issues=issues)

    return report_from_issues(issues)


def validate_governance_batch_shape(
    batch: object,
) -> PredicateGovernanceValidationReport:
    issues: list[PredicateGovernanceValidationIssue] = []

    if type(batch) is not PredicateGovernanceBatch:
        _issue(
            issues,
            "$",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "exact PredicateGovernanceBatch required",
        )
        return report_from_issues(issues)

    _identifier(batch.batch_id, path="batch_id", issues=issues)
    _safe_expected_id(
        batch,
        actual_id=batch.batch_id,
        path="batch_id",
        label="batch",
        issues=issues,
    )
    if batch.schema_version != SLICE38B_SCHEMA_VERSION:
        _issue(
            issues,
            "schema_version",
            PredicateGovernanceValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE38B_SCHEMA_VERSION}",
        )

    for field in (
        "provenance_records",
        "resources",
        "authority_records",
        "transitions",
    ):
        if type(getattr(batch, field)) is not tuple:
            _issue(
                issues,
                field,
                PredicateGovernanceValidationCode.TYPE_MISMATCH,
                "batch collections must be tuples",
            )

    zero_authority_fields = (
        "registry_population_installed",
        "action_root_lookup_installed",
        "predicate_selection_installed",
        "nearest_known_mapping_installed",
        "semantic_similarity_installed",
        "capability_routing_installed",
        "runtime_activation_installed",
    )
    for field in zero_authority_fields:
        if getattr(batch, field) is not False:
            code = (
                PredicateGovernanceValidationCode.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED
                if field == "nearest_known_mapping_installed"
                else PredicateGovernanceValidationCode.SIMILARITY_AUTHORITY_PROHIBITED
                if field == "semantic_similarity_installed"
                else PredicateGovernanceValidationCode.REGISTRY_POPULATION_PROHIBITED
            )
            _issue(
                issues,
                field,
                code,
                "all Slice 38B runtime and population flags must remain false",
            )

    return report_from_issues(issues)
