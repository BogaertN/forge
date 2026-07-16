"""Fail-closed Slice 37D registry and lookup validation."""

from __future__ import annotations

import re
from typing import Final

from ..built_in_registry.registry import BUILT_IN_REGISTRY
from ..governed_lifecycle.collection import validate_governance_batch
from ..schema import (
    ConceptLifecycleState,
    LexicalReferenceKind,
)
from .schema import (
    SLICE37D_EXPECTED_LEXICAL_REFERENCE_COUNT,
    SLICE37D_EXPECTED_MAPPING_COUNT,
    SLICE37D_EXPECTED_OUTWARD_ELIGIBILITY_COUNT,
    SLICE37D_EXPECTED_SENSE_COUNT,
    SLICE37D_SCHEMA_VERSION,
    ExactTermLookupRequest,
    ExactTermLookupResult,
    ExactTermLookupState,
    MappingExpansionRefusal,
    MappingMultiplicity,
    OutwardExpressionEligibilityReference,
    OutwardExpressionEligibilityState,
    ProhibitedExpansionKind,
    SenseTermMappingRegistry,
    SenseTermMappingValidationCode,
    SenseTermMappingValidationError,
    SenseTermMappingValidationIssue,
    SenseTermMappingValidationReport,
)


_LANGUAGE_TAG_RE: Final[re.Pattern[str]] = re.compile(
    r"^[a-z]{2,8}(?:-[a-z0-9]{1,8})*$"
)


def _add(
    issues: list[SenseTermMappingValidationIssue],
    path: str,
    code: SenseTermMappingValidationCode,
    detail: str,
) -> None:
    issues.append(
        SenseTermMappingValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def _report(
    issues: list[SenseTermMappingValidationIssue],
) -> SenseTermMappingValidationReport:
    ordered = tuple(
        sorted(
            issues,
            key=lambda issue: (
                issue.path,
                issue.code.value,
                issue.detail,
            ),
        )
    )
    return SenseTermMappingValidationReport(
        ok=not ordered,
        issues=ordered,
    )


def _text(
    value: object,
    *,
    path: str,
    issues: list[SenseTermMappingValidationIssue],
    permit_outer_whitespace: bool = False,
) -> bool:
    if not isinstance(value, str):
        _add(
            issues,
            path,
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "expected str",
        )
        return False

    if not value:
        _add(
            issues,
            path,
            SenseTermMappingValidationCode.REQUIRED_VALUE_MISSING,
            "text must be non-empty",
        )
        return False

    if any(ord(character) < 32 for character in value):
        _add(
            issues,
            path,
            SenseTermMappingValidationCode.INVALID_TEXT,
            "text may not contain control characters",
        )
        return False

    if not permit_outer_whitespace and value != value.strip():
        _add(
            issues,
            path,
            SenseTermMappingValidationCode.INVALID_TEXT,
            "text must be trimmed",
        )
        return False

    return True


def _unique_tuple(
    value: object,
    *,
    path: str,
    issues: list[SenseTermMappingValidationIssue],
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        _add(
            issues,
            path,
            SenseTermMappingValidationCode.TYPE_MISMATCH,
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
        _add(
            issues,
            path,
            SenseTermMappingValidationCode.REQUIRED_VALUE_MISSING,
            "tuple must not be empty",
        )

    if len(value) != len(set(value)):
        _add(
            issues,
            path,
            SenseTermMappingValidationCode.DUPLICATE_VALUE,
            "tuple values must be unique",
        )

    return tuple(valid)


def mapping_multiplicity(
    concept_candidate_refs: tuple[str, ...],
) -> MappingMultiplicity:
    if not concept_candidate_refs:
        return MappingMultiplicity.ZERO
    if len(concept_candidate_refs) == 1:
        return MappingMultiplicity.ONE_TO_ONE
    return MappingMultiplicity.ONE_TO_MANY


def validate_lookup_request(
    request: ExactTermLookupRequest,
) -> SenseTermMappingValidationReport:
    issues: list[SenseTermMappingValidationIssue] = []

    if type(request) is not ExactTermLookupRequest:
        _add(
            issues,
            "$",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "exact ExactTermLookupRequest required",
        )
        return _report(issues)

    if request.schema_version != SLICE37D_SCHEMA_VERSION:
        _add(
            issues,
            "schema_version",
            SenseTermMappingValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37D_SCHEMA_VERSION}",
        )

    if request.request_id != request.expected_id():
        _add(
            issues,
            "request_id",
            SenseTermMappingValidationCode.IDENTITY_MISMATCH,
            "request ID does not match exact caller-supplied fields",
        )

    _text(
        request.exact_form,
        path="exact_form",
        issues=issues,
        permit_outer_whitespace=True,
    )

    if (
        not isinstance(request.language_tag, str)
        or _LANGUAGE_TAG_RE.fullmatch(request.language_tag) is None
    ):
        _add(
            issues,
            "language_tag",
            SenseTermMappingValidationCode.INVALID_LANGUAGE_TAG,
            "language tag must be canonical lower-case bounded form",
        )

    _text(
        request.namespace_id,
        path="namespace_id",
        issues=issues,
    )
    _unique_tuple(
        request.namespace_scope,
        path="namespace_scope",
        issues=issues,
        allow_empty=False,
    )
    _unique_tuple(
        request.domain_scope,
        path="domain_scope",
        issues=issues,
        allow_empty=False,
    )

    return _report(issues)


def validate_lookup_result(
    result: ExactTermLookupResult,
) -> SenseTermMappingValidationReport:
    issues: list[SenseTermMappingValidationIssue] = []

    if type(result) is not ExactTermLookupResult:
        _add(
            issues,
            "$",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "exact ExactTermLookupResult required",
        )
        return _report(issues)

    if result.schema_version != SLICE37D_SCHEMA_VERSION:
        _add(
            issues,
            "schema_version",
            SenseTermMappingValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37D_SCHEMA_VERSION}",
        )

    if result.result_id != result.expected_id():
        _add(
            issues,
            "result_id",
            SenseTermMappingValidationCode.IDENTITY_MISMATCH,
            "result ID does not match its canonical body",
        )

    _text(result.request_ref, path="request_ref", issues=issues)
    _unique_tuple(
        result.lexical_reference_refs,
        path="lexical_reference_refs",
        issues=issues,
    )
    _unique_tuple(
        result.mapping_refs,
        path="mapping_refs",
        issues=issues,
    )
    _unique_tuple(
        result.concept_candidate_refs,
        path="concept_candidate_refs",
        issues=issues,
    )
    _unique_tuple(
        result.sense_candidate_refs,
        path="sense_candidate_refs",
        issues=issues,
    )
    _unique_tuple(
        result.outward_eligibility_refs,
        path="outward_eligibility_refs",
        issues=issues,
    )
    _text(result.reason, path="reason", issues=issues)

    if (
        result.candidate_order_is_ranked is not False
        or result.occurrence_interpretation_selected is not False
        or result.selected_concept_ref is not None
        or result.selected_sense_ref is not None
    ):
        _add(
            issues,
            "selection",
            SenseTermMappingValidationCode.OCCURRENCE_SELECTION_PROHIBITED,
            "lookup may not rank candidates or select occurrence meaning",
        )

    if not isinstance(result.state, ExactTermLookupState):
        _add(
            issues,
            "state",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "expected ExactTermLookupState",
        )
        return _report(issues)

    if not isinstance(result.multiplicity, MappingMultiplicity):
        _add(
            issues,
            "multiplicity",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "expected MappingMultiplicity",
        )
        return _report(issues)

    expected_multiplicity = mapping_multiplicity(
        result.concept_candidate_refs
    )
    if result.multiplicity is not expected_multiplicity:
        _add(
            issues,
            "multiplicity",
            SenseTermMappingValidationCode.MAPPING_MULTIPLICITY_MISMATCH,
            f"expected {expected_multiplicity.value}",
        )

    state_requirements = {
        ExactTermLookupState.NO_EXACT_LEXICAL_REFERENCE: (
            False,
            0,
            0,
        ),
        ExactTermLookupState.UNMAPPED_TERM: (
            True,
            1,
            0,
        ),
        ExactTermLookupState.MAPPED_ONE_TO_ONE: (
            True,
            1,
            1,
        ),
        ExactTermLookupState.MAPPED_ONE_TO_MANY: (
            True,
            1,
            1,
        ),
        ExactTermLookupState.AMBIGUOUS_MAPPING: (
            True,
            1,
            1,
        ),
        ExactTermLookupState.UNSUPPORTED_MAPPING: (
            True,
            1,
            1,
        ),
    }
    expected_exact, minimum_lexical, minimum_mappings = state_requirements[
        result.state
    ]

    if result.exact_match is not expected_exact:
        _add(
            issues,
            "exact_match",
            SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
            f"state {result.state.value} requires exact_match={expected_exact}",
        )
    if len(result.lexical_reference_refs) < minimum_lexical:
        _add(
            issues,
            "lexical_reference_refs",
            SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
            f"state {result.state.value} requires an exact lexical reference",
        )
    if len(result.mapping_refs) < minimum_mappings:
        _add(
            issues,
            "mapping_refs",
            SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
            f"state {result.state.value} requires a mapping record",
        )

    if (
        result.state is ExactTermLookupState.MAPPED_ONE_TO_ONE
        and result.multiplicity is not MappingMultiplicity.ONE_TO_ONE
    ):
        _add(
            issues,
            "state",
            SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
            "one-to-one state requires exactly one concept candidate",
        )
    if (
        result.state is ExactTermLookupState.MAPPED_ONE_TO_MANY
        and result.multiplicity is not MappingMultiplicity.ONE_TO_MANY
    ):
        _add(
            issues,
            "state",
            SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
            "one-to-many state requires multiple concept candidates",
        )
    if (
        result.state is ExactTermLookupState.AMBIGUOUS_MAPPING
        and result.multiplicity is not MappingMultiplicity.ONE_TO_MANY
    ):
        _add(
            issues,
            "state",
            SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
            "ambiguous mapping requires multiple concept candidates",
        )
    if (
        result.state is ExactTermLookupState.UNSUPPORTED_MAPPING
        and (
            result.multiplicity is not MappingMultiplicity.ZERO
            or result.sense_candidate_refs
        )
    ):
        _add(
            issues,
            "state",
            SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
            "unsupported mapping must preserve zero candidates",
        )

    return _report(issues)


def validate_outward_eligibility_reference(
    record: OutwardExpressionEligibilityReference,
) -> SenseTermMappingValidationReport:
    issues: list[SenseTermMappingValidationIssue] = []

    if type(record) is not OutwardExpressionEligibilityReference:
        _add(
            issues,
            "$",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "exact OutwardExpressionEligibilityReference required",
        )
        return _report(issues)

    if record.schema_version != SLICE37D_SCHEMA_VERSION:
        _add(
            issues,
            "schema_version",
            SenseTermMappingValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37D_SCHEMA_VERSION}",
        )

    if record.eligibility_id != record.expected_id():
        _add(
            issues,
            "eligibility_id",
            SenseTermMappingValidationCode.IDENTITY_MISMATCH,
            "eligibility ID does not match canonical body",
        )

    for field_name in (
        "lexical_reference_id",
        "concept_ref",
        "sense_ref",
        "reason",
        "version",
        "provenance_ref",
    ):
        _text(
            getattr(record, field_name),
            path=field_name,
            issues=issues,
        )

    if (
        record.eligibility_state
        is not OutwardExpressionEligibilityState.ELIGIBLE_REFERENCE_ONLY
        or record.rendering_authorized is not False
        or record.delivery_authorized is not False
        or record.runtime_authorized is not False
    ):
        _add(
            issues,
            "authority",
            SenseTermMappingValidationCode.OUTWARD_ELIGIBILITY_MISMATCH,
            "eligibility must remain reference-only with no rendering, delivery, or runtime authority",
        )

    _unique_tuple(
        record.prohibited_authorities,
        path="prohibited_authorities",
        issues=issues,
        allow_empty=False,
    )
    return _report(issues)


def validate_expansion_refusal(
    record: MappingExpansionRefusal,
) -> SenseTermMappingValidationReport:
    issues: list[SenseTermMappingValidationIssue] = []

    if type(record) is not MappingExpansionRefusal:
        _add(
            issues,
            "$",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "exact MappingExpansionRefusal required",
        )
        return _report(issues)

    if record.schema_version != SLICE37D_SCHEMA_VERSION:
        _add(
            issues,
            "schema_version",
            SenseTermMappingValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37D_SCHEMA_VERSION}",
        )

    if record.refusal_id != record.expected_id():
        _add(
            issues,
            "refusal_id",
            SenseTermMappingValidationCode.IDENTITY_MISMATCH,
            "refusal ID does not match canonical body",
        )

    if not isinstance(record.expansion_kind, ProhibitedExpansionKind):
        _add(
            issues,
            "expansion_kind",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "expected ProhibitedExpansionKind",
        )

    if record.allowed is not False:
        _add(
            issues,
            "allowed",
            SenseTermMappingValidationCode.EXPANSION_AUTHORITY_PROHIBITED,
            "mapping expansion must remain prohibited",
        )

    _text(record.reason, path="reason", issues=issues)
    _unique_tuple(
        record.prohibited_authorities,
        path="prohibited_authorities",
        issues=issues,
        allow_empty=False,
    )
    return _report(issues)


def validate_registry(
    registry: SenseTermMappingRegistry,
) -> SenseTermMappingValidationReport:
    issues: list[SenseTermMappingValidationIssue] = []

    if type(registry) is not SenseTermMappingRegistry:
        _add(
            issues,
            "$",
            SenseTermMappingValidationCode.TYPE_MISMATCH,
            "exact SenseTermMappingRegistry required",
        )
        return _report(issues)

    manifest = registry.manifest

    if manifest.schema_version != SLICE37D_SCHEMA_VERSION:
        _add(
            issues,
            "manifest.schema_version",
            SenseTermMappingValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37D_SCHEMA_VERSION}",
        )
    if manifest.manifest_id != manifest.expected_id():
        _add(
            issues,
            "manifest.manifest_id",
            SenseTermMappingValidationCode.IDENTITY_MISMATCH,
            "manifest ID does not match canonical body",
        )

    if registry.concept_registry.registry_digest() != BUILT_IN_REGISTRY.registry_digest():
        _add(
            issues,
            "concept_registry",
            SenseTermMappingValidationCode.CONCEPT_REGISTRY_MISMATCH,
            "registry must reference the exact accepted Slice 37C registry",
        )

    governance_report = validate_governance_batch(registry.governance_batch)
    if not governance_report.ok:
        _add(
            issues,
            "governance_batch",
            SenseTermMappingValidationCode.GOVERNANCE_BATCH_INVALID,
            f"{len(governance_report.issues)} governance issues",
        )

    expected_counts = (
        (
            "senses",
            len(registry.senses),
            SLICE37D_EXPECTED_SENSE_COUNT,
        ),
        (
            "lexical_references",
            len(registry.lexical_references),
            SLICE37D_EXPECTED_LEXICAL_REFERENCE_COUNT,
        ),
        (
            "mappings",
            len(registry.mappings),
            SLICE37D_EXPECTED_MAPPING_COUNT,
        ),
        (
            "outward_eligibility_references",
            len(registry.outward_eligibility_references),
            SLICE37D_EXPECTED_OUTWARD_ELIGIBILITY_COUNT,
        ),
        (
            "prohibited_expansion_refusals",
            len(registry.prohibited_expansion_refusals),
            len(ProhibitedExpansionKind),
        ),
    )
    for path, actual, expected in expected_counts:
        if actual != expected:
            _add(
                issues,
                path,
                SenseTermMappingValidationCode.REGISTRY_COUNT_MISMATCH,
                f"expected {expected}, found {actual}",
            )

    if (
        manifest.read_only is not True
        or manifest.closed_set is not True
        or manifest.human_approved is not True
        or manifest.registry_population_authorized is not True
        or manifest.sense_population_authorized is not True
        or manifest.lexical_reference_population_authorized is not True
        or manifest.mapping_population_authorized is not True
        or manifest.outward_eligibility_reference_population_authorized
        is not True
    ):
        _add(
            issues,
            "manifest",
            SenseTermMappingValidationCode.REGISTRY_NOT_CLOSED,
            "registry must be human-approved, closed, read-only, and explicitly populated",
        )

    required_true = (
        manifest.exact_term_lookup_allowed,
        manifest.exact_reference_id_lookup_allowed,
        manifest.exact_sense_id_lookup_allowed,
        manifest.exact_mapping_id_lookup_allowed,
        manifest.semantic_classes_deferred_to_slice37e,
        manifest.semantic_relations_deferred_to_slice37e,
        manifest.structural_candidate_integration_deferred_to_slice37f,
    )
    if not all(value is True for value in required_true):
        _add(
            issues,
            "manifest",
            SenseTermMappingValidationCode.REGISTRY_NOT_READ_ONLY,
            "required exact lookup and deferral boundaries must remain true",
        )

    prohibited_flags = (
        manifest.occurrence_interpretation_installed,
        manifest.sense_selection_installed,
        manifest.candidate_meaning_creation_installed,
        manifest.structural_integration_installed,
        manifest.case_fold_expansion_installed,
        manifest.spelling_correction_installed,
        manifest.stemming_installed,
        manifest.synonym_expansion_installed,
        manifest.nearest_match_installed,
        manifest.frequency_ranking_installed,
        manifest.semantic_similarity_installed,
        manifest.embedding_installed,
        manifest.model_inference_installed,
        manifest.ordinary_dictionary_fallback_installed,
        manifest.external_resource_loading_installed,
        manifest.runtime_activation_installed,
        manifest.route_registration_installed,
        manifest.tool_activation_installed,
        manifest.memory_access_installed,
        manifest.action_execution_installed,
        manifest.rendering_installed,
        manifest.delivery_installed,
    )
    if any(value is not False for value in prohibited_flags):
        _add(
            issues,
            "manifest",
            SenseTermMappingValidationCode.RUNTIME_AUTHORITY_PROHIBITED,
            "all interpretation, expansion, runtime, action, rendering, and delivery flags must remain false",
        )

    concept_by_id = {
        item.concept_id: item
        for item in registry.concept_registry.admitted_concepts
    }
    sense_by_id = {item.sense_id: item for item in registry.senses}
    lexical_by_id = {
        item.lexical_reference_id: item
        for item in registry.lexical_references
    }
    mapping_by_id = {item.mapping_id: item for item in registry.mappings}
    eligibility_by_id = {
        item.eligibility_id: item
        for item in registry.outward_eligibility_references
    }

    expected_manifest_refs = (
        (
            "manifest.sense_refs",
            manifest.sense_refs,
            tuple(item.sense_id for item in registry.senses),
        ),
        (
            "manifest.lexical_reference_refs",
            manifest.lexical_reference_refs,
            tuple(
                item.lexical_reference_id
                for item in registry.lexical_references
            ),
        ),
        (
            "manifest.mapping_refs",
            manifest.mapping_refs,
            tuple(item.mapping_id for item in registry.mappings),
        ),
        (
            "manifest.outward_eligibility_refs",
            manifest.outward_eligibility_refs,
            tuple(
                item.eligibility_id
                for item in registry.outward_eligibility_references
            ),
        ),
        (
            "manifest.prohibited_expansion_refusal_refs",
            manifest.prohibited_expansion_refusal_refs,
            tuple(
                item.refusal_id
                for item in registry.prohibited_expansion_refusals
            ),
        ),
    )
    for path, actual, expected in expected_manifest_refs:
        if actual != expected:
            _add(
                issues,
                path,
                SenseTermMappingValidationCode.CANDIDATE_ORDER_MISMATCH,
                "manifest reference order must match canonical registry order",
            )

    lexical_keys: set[tuple[object, ...]] = set()
    for index, lexical in enumerate(registry.lexical_references):
        key = (
            lexical.namespace_id,
            lexical.exact_form,
            lexical.language_tag,
            lexical.reference_kind,
            lexical.case_sensitive,
        )
        if key in lexical_keys:
            _add(
                issues,
                f"lexical_references[{index}]",
                SenseTermMappingValidationCode.DUPLICATE_VALUE,
                "duplicate exact lexical-reference key",
            )
        lexical_keys.add(key)

        if lexical.case_sensitive is not True:
            _add(
                issues,
                f"lexical_references[{index}].case_sensitive",
                SenseTermMappingValidationCode.EXPANSION_AUTHORITY_PROHIBITED,
                "initial Slice 37D references must remain case-sensitive",
            )

    for index, sense in enumerate(registry.senses):
        if sense.concept_id not in concept_by_id:
            _add(
                issues,
                f"senses[{index}].concept_id",
                SenseTermMappingValidationCode.REFERENCE_NOT_FOUND,
                "sense concept is absent from Slice 37C registry",
            )
        for reference in sense.lexical_reference_refs:
            if reference not in lexical_by_id:
                _add(
                    issues,
                    f"senses[{index}].lexical_reference_refs",
                    SenseTermMappingValidationCode.REFERENCE_NOT_FOUND,
                    f"lexical reference {reference!r} is absent",
                )

    for index, mapping in enumerate(registry.mappings):
        lexical = lexical_by_id.get(mapping.lexical_reference_id)
        if lexical is None:
            _add(
                issues,
                f"mappings[{index}].lexical_reference_id",
                SenseTermMappingValidationCode.REFERENCE_NOT_FOUND,
                "mapping lexical reference is absent",
            )

        if (
            mapping.occurrence_interpretation_selected is not False
            or mapping.selected_concept_ref is not None
            or mapping.selected_sense_ref is not None
        ):
            _add(
                issues,
                f"mappings[{index}].selection",
                SenseTermMappingValidationCode.OCCURRENCE_SELECTION_PROHIBITED,
                "mapping may not select occurrence meaning",
            )

        for reference in mapping.concept_candidate_refs:
            if reference not in concept_by_id:
                _add(
                    issues,
                    f"mappings[{index}].concept_candidate_refs",
                    SenseTermMappingValidationCode.REFERENCE_NOT_FOUND,
                    f"concept candidate {reference!r} is absent",
                )
        for reference in mapping.sense_candidate_refs:
            sense = sense_by_id.get(reference)
            if sense is None:
                _add(
                    issues,
                    f"mappings[{index}].sense_candidate_refs",
                    SenseTermMappingValidationCode.REFERENCE_NOT_FOUND,
                    f"sense candidate {reference!r} is absent",
                )
            elif sense.concept_id not in mapping.concept_candidate_refs:
                _add(
                    issues,
                    f"mappings[{index}].sense_candidate_refs",
                    SenseTermMappingValidationCode.REFERENCE_KIND_MISMATCH,
                    "sense candidate's concept is not in mapping concept candidates",
                )

        multiplicity = mapping_multiplicity(mapping.concept_candidate_refs)
        if mapping.lifecycle_state is ConceptLifecycleState.ADMITTED:
            if multiplicity is MappingMultiplicity.ZERO:
                _add(
                    issues,
                    f"mappings[{index}]",
                    SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
                    "admitted mapping requires concept candidates",
                )
            if not mapping.sense_candidate_refs:
                _add(
                    issues,
                    f"mappings[{index}]",
                    SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
                    "admitted mapping requires sense candidates",
                )
        elif mapping.lifecycle_state is ConceptLifecycleState.AMBIGUOUS:
            if (
                multiplicity is not MappingMultiplicity.ONE_TO_MANY
                or len(mapping.sense_candidate_refs) < 2
            ):
                _add(
                    issues,
                    f"mappings[{index}]",
                    SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
                    "ambiguous mapping must preserve multiple concept and sense candidates",
                )
        elif mapping.lifecycle_state is ConceptLifecycleState.UNSUPPORTED:
            if (
                multiplicity is not MappingMultiplicity.ZERO
                or mapping.sense_candidate_refs
            ):
                _add(
                    issues,
                    f"mappings[{index}]",
                    SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
                    "unsupported mapping must preserve zero candidates",
                )
        else:
            _add(
                issues,
                f"mappings[{index}].lifecycle_state",
                SenseTermMappingValidationCode.MAPPING_STATE_MISMATCH,
                "current mapping state must be admitted, ambiguous, or unsupported",
            )

    for index, eligibility in enumerate(
        registry.outward_eligibility_references
    ):
        report = validate_outward_eligibility_reference(eligibility)
        for issue in report.issues:
            _add(
                issues,
                f"outward_eligibility_references[{index}].{issue.path}",
                issue.code,
                issue.detail,
            )

        lexical = lexical_by_id.get(eligibility.lexical_reference_id)
        if (
            lexical is None
            or lexical.reference_kind
            is not LexicalReferenceKind.CONTROLLED_OUTWARD_EXPRESSION
        ):
            _add(
                issues,
                f"outward_eligibility_references[{index}].lexical_reference_id",
                SenseTermMappingValidationCode.OUTWARD_ELIGIBILITY_MISMATCH,
                "eligibility must reference an exact controlled outward expression",
            )
        if eligibility.concept_ref not in concept_by_id:
            _add(
                issues,
                f"outward_eligibility_references[{index}].concept_ref",
                SenseTermMappingValidationCode.REFERENCE_NOT_FOUND,
                "eligibility concept is absent",
            )
        sense = sense_by_id.get(eligibility.sense_ref)
        if sense is None or sense.concept_id != eligibility.concept_ref:
            _add(
                issues,
                f"outward_eligibility_references[{index}].sense_ref",
                SenseTermMappingValidationCode.REFERENCE_KIND_MISMATCH,
                "eligibility sense must belong to eligibility concept",
            )

    expansion_kinds: list[ProhibitedExpansionKind] = []
    for index, refusal in enumerate(registry.prohibited_expansion_refusals):
        report = validate_expansion_refusal(refusal)
        for issue in report.issues:
            _add(
                issues,
                f"prohibited_expansion_refusals[{index}].{issue.path}",
                issue.code,
                issue.detail,
            )
        expansion_kinds.append(refusal.expansion_kind)

    if tuple(expansion_kinds) != tuple(ProhibitedExpansionKind):
        _add(
            issues,
            "prohibited_expansion_refusals",
            SenseTermMappingValidationCode.CANDIDATE_ORDER_MISMATCH,
            "every prohibited expansion kind must appear once in enum order",
        )

    return _report(issues)


def assert_registry(
    registry: SenseTermMappingRegistry,
) -> SenseTermMappingRegistry:
    report = validate_registry(registry)
    if not report.ok:
        raise SenseTermMappingValidationError(report)
    return registry


def assert_lookup_request(
    request: ExactTermLookupRequest,
) -> ExactTermLookupRequest:
    report = validate_lookup_request(request)
    if not report.ok:
        raise SenseTermMappingValidationError(report)
    return request


def assert_lookup_result(
    result: ExactTermLookupResult,
) -> ExactTermLookupResult:
    report = validate_lookup_result(result)
    if not report.ok:
        raise SenseTermMappingValidationError(report)
    return result
