"""Fail-closed validation for the Slice 37C built-in registry."""

from __future__ import annotations

from collections import Counter
from typing import Any

from ..schema import (
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ControlledConceptIdentity,
)
from ..governed_lifecycle.collection import validate_governance_batch
from ..governed_lifecycle.identity import (
    expected_resource_lineage_id,
    recompute_resource_id,
)
from .authority import (
    BUILT_IN_CONCEPT_DEFINITIONS,
    BUILT_IN_CONCEPT_KEYS,
    SLICE37C_ADDITIONAL_AUTHORITY_LIMITATIONS,
    SLICE37C_COMMON_PROHIBITED_USES,
    SLICE37C_DECISION_OWNER_REF,
    SLICE37C_HUMAN_APPROVAL_REF,
    SLICE37C_NAMESPACE_DEFINITION,
    SLICE37C_NAMESPACE_KEY,
    SLICE37C_NAMESPACE_LABEL,
    SLICE37C_NAMESPACE_PERMITTED_USES,
    SLICE37C_NAMESPACE_SCOPE,
    SLICE37C_PROHIBITED_AUTHORITIES,
)
from .schema import (
    SLICE37C_EXPECTED_CONCEPT_COUNT,
    SLICE37C_EXPECTED_NAMESPACE_COUNT,
    SLICE37C_SCHEMA_VERSION,
    SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256,
    SLICE37C_SPEC_ID,
    SLICE37C_SPEC_VERSION,
    BuiltInConceptRegistry,
    BuiltInConceptRegistryManifest,
    BuiltInRegistryValidationCode,
    BuiltInRegistryValidationError,
    BuiltInRegistryValidationIssue,
    BuiltInRegistryValidationReport,
)


def _add(
    issues: list[BuiltInRegistryValidationIssue],
    path: str,
    code: BuiltInRegistryValidationCode,
    detail: str,
) -> None:
    issues.append(
        BuiltInRegistryValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def _report(
    issues: list[BuiltInRegistryValidationIssue],
) -> BuiltInRegistryValidationReport:
    ordered = tuple(
        sorted(
            issues,
            key=lambda item: (
                item.path,
                item.code.value,
                item.detail,
            ),
        )
    )
    return BuiltInRegistryValidationReport(
        ok=not ordered,
        issues=ordered,
    )


def validate_registry_manifest(
    manifest: BuiltInConceptRegistryManifest,
) -> BuiltInRegistryValidationReport:
    issues: list[BuiltInRegistryValidationIssue] = []

    if type(manifest) is not BuiltInConceptRegistryManifest:
        _add(
            issues,
            "$",
            BuiltInRegistryValidationCode.TYPE_MISMATCH,
            "exact BuiltInConceptRegistryManifest required",
        )
        return _report(issues)

    if manifest.manifest_id != manifest.expected_id():
        _add(
            issues,
            "manifest_id",
            BuiltInRegistryValidationCode.IDENTITY_MISMATCH,
            "manifest ID does not match the canonical body",
        )

    if manifest.schema_version != SLICE37C_SCHEMA_VERSION:
        _add(
            issues,
            "schema_version",
            BuiltInRegistryValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37C_SCHEMA_VERSION}",
        )

    if (
        manifest.spec_id != SLICE37C_SPEC_ID
        or manifest.spec_version != SLICE37C_SPEC_VERSION
    ):
        _add(
            issues,
            "spec",
            BuiltInRegistryValidationCode.MANIFEST_BOUNDARY_MISMATCH,
            "Slice 37C spec identity is not exact",
        )

    exact_values: tuple[tuple[str, Any, Any], ...] = (
        (
            "source_authority_packet_sha256",
            manifest.source_authority_packet_sha256,
            SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256,
        ),
        (
            "decision_owner_ref",
            manifest.decision_owner_ref,
            SLICE37C_DECISION_OWNER_REF,
        ),
        (
            "human_approval_ref",
            manifest.human_approval_ref,
            SLICE37C_HUMAN_APPROVAL_REF,
        ),
        ("human_approved", manifest.human_approved, True),
        (
            "registry_population_authorized",
            manifest.registry_population_authorized,
            True,
        ),
        ("read_only", manifest.read_only, True),
        ("closed_set", manifest.closed_set, True),
        ("authority_limitations", manifest.authority_limitations, SLICE37C_ADDITIONAL_AUTHORITY_LIMITATIONS),
        (
            "exact_identity_lookup_allowed",
            manifest.exact_identity_lookup_allowed,
            True,
        ),
        (
            "exact_internal_key_lookup_allowed",
            manifest.exact_internal_key_lookup_allowed,
            True,
        ),
        (
            "surface_form_lookup_allowed",
            manifest.surface_form_lookup_allowed,
            False,
        ),
        (
            "historical_slice8_preserved",
            manifest.historical_slice8_preserved,
            True,
        ),
        (
            "historical_slice8_superseded",
            manifest.historical_slice8_superseded,
            False,
        ),
    )

    for path, actual, expected in exact_values:
        if actual != expected:
            _add(
                issues,
                path,
                BuiltInRegistryValidationCode.MANIFEST_BOUNDARY_MISMATCH,
                f"expected exact value {expected!r}",
            )

    prohibited_true_fields = (
        "lexical_reference_population_installed",
        "term_mapping_installed",
        "occurrence_interpretation_installed",
        "sense_population_installed",
        "sense_selection_installed",
        "semantic_class_population_installed",
        "semantic_relation_population_installed",
        "structural_integration_installed",
        "candidate_meaning_creation_installed",
        "runtime_activation_installed",
        "route_registration_installed",
        "tool_activation_installed",
        "memory_access_installed",
        "action_execution_installed",
        "rendering_installed",
        "delivery_installed",
        "external_resource_loading_installed",
        "llm_authority_installed",
    )

    for field_name in prohibited_true_fields:
        if getattr(manifest, field_name) is not False:
            code = (
                BuiltInRegistryValidationCode.SURFACE_LOOKUP_PROHIBITED
                if field_name in {
                    "lexical_reference_population_installed",
                    "term_mapping_installed",
                }
                else BuiltInRegistryValidationCode.RUNTIME_AUTHORITY_PROHIBITED
            )
            _add(
                issues,
                field_name,
                code,
                "authority remains deferred or prohibited in Slice 37C",
            )

    deferred_fields = (
        "semantic_class_references_deferred_to_slice37e",
        "sense_references_deferred_to_slice37d",
        "relation_references_deferred_to_slice37e",
    )
    for field_name in deferred_fields:
        if getattr(manifest, field_name) is not True:
            _add(
                issues,
                field_name,
                BuiltInRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH,
                "the later-slice deferral must remain explicit",
            )

    if len(manifest.concept_refs) != SLICE37C_EXPECTED_CONCEPT_COUNT:
        _add(
            issues,
            "concept_refs",
            BuiltInRegistryValidationCode.REGISTRY_COUNT_MISMATCH,
            "manifest must name exactly four concepts",
        )

    if manifest.concept_keys != BUILT_IN_CONCEPT_KEYS:
        _add(
            issues,
            "concept_keys",
            BuiltInRegistryValidationCode.REGISTRY_NOT_CLOSED,
            "concept keys must equal the exact approved closed set",
        )

    for path, values in (
        ("concept_refs", manifest.concept_refs),
        ("concept_lineage_refs", manifest.concept_lineage_refs),
        ("concept_keys", manifest.concept_keys),
    ):
        if len(values) != len(set(values)):
            _add(
                issues,
                path,
                BuiltInRegistryValidationCode.REGISTRY_NOT_CLOSED,
                "values must be unique",
            )

    return _report(issues)


def validate_built_in_registry(
    registry: BuiltInConceptRegistry,
) -> BuiltInRegistryValidationReport:
    issues: list[BuiltInRegistryValidationIssue] = []

    if type(registry) is not BuiltInConceptRegistry:
        _add(
            issues,
            "$",
            BuiltInRegistryValidationCode.TYPE_MISMATCH,
            "exact BuiltInConceptRegistry required",
        )
        return _report(issues)

    manifest_report = validate_registry_manifest(registry.manifest)
    issues.extend(manifest_report.issues)

    governance_report = validate_governance_batch(
        registry.governance_batch
    )
    if not governance_report.ok:
        for item in governance_report.issues:
            _add(
                issues,
                f"governance_batch.{item.path}",
                BuiltInRegistryValidationCode.GOVERNANCE_BATCH_INVALID,
                f"{item.code.value}: {item.detail}",
            )

    if type(registry.current_namespace) is not ConceptNamespaceIdentity:
        _add(
            issues,
            "current_namespace",
            BuiltInRegistryValidationCode.TYPE_MISMATCH,
            "exact ConceptNamespaceIdentity required",
        )
        return _report(issues)

    namespace = registry.current_namespace
    namespace_expectations = (
        ("namespace_key", namespace.namespace_key, SLICE37C_NAMESPACE_KEY),
        ("label", namespace.label, SLICE37C_NAMESPACE_LABEL),
        ("definition", namespace.definition, SLICE37C_NAMESPACE_DEFINITION),
        ("version", namespace.version, "v3"),
        (
            "lifecycle_state",
            namespace.lifecycle_state,
            ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ),
        ("scope_tags", namespace.scope_tags, SLICE37C_NAMESPACE_SCOPE),
        (
            "permitted_uses",
            namespace.permitted_uses,
            SLICE37C_NAMESPACE_PERMITTED_USES,
        ),
        (
            "prohibited_uses",
            namespace.prohibited_uses,
            SLICE37C_COMMON_PROHIBITED_USES,
        ),
        (
            "prohibited_authorities",
            namespace.prohibited_authorities,
            SLICE37C_PROHIBITED_AUTHORITIES,
        ),
    )
    for field_name, actual, expected in namespace_expectations:
        if actual != expected:
            _add(
                issues,
                f"current_namespace.{field_name}",
                BuiltInRegistryValidationCode.NAMESPACE_MISMATCH,
                "namespace field does not match the approved Slice 37C record",
            )

    if namespace.namespace_id != recompute_resource_id(namespace):
        _add(
            issues,
            "current_namespace.namespace_id",
            BuiltInRegistryValidationCode.IDENTITY_MISMATCH,
            "namespace ID does not match its canonical body",
        )

    concepts = registry.admitted_concepts

    if not isinstance(concepts, tuple):
        _add(
            issues,
            "admitted_concepts",
            BuiltInRegistryValidationCode.TYPE_MISMATCH,
            "concept collection must be a tuple",
        )
        return _report(issues)

    if len(concepts) != SLICE37C_EXPECTED_CONCEPT_COUNT:
        _add(
            issues,
            "admitted_concepts",
            BuiltInRegistryValidationCode.REGISTRY_COUNT_MISMATCH,
            "registry must contain exactly four current concepts",
        )

    concept_ids = tuple(concept.concept_id for concept in concepts)
    concept_keys = tuple(concept.concept_key for concept in concepts)

    if len(concept_ids) != len(set(concept_ids)):
        _add(
            issues,
            "admitted_concepts",
            BuiltInRegistryValidationCode.DUPLICATE_CONCEPT_ID,
            "concept IDs must be unique",
        )

    if len(concept_keys) != len(set(concept_keys)):
        _add(
            issues,
            "admitted_concepts",
            BuiltInRegistryValidationCode.DUPLICATE_CONCEPT_KEY,
            "concept keys must be unique",
        )

    if concept_keys != BUILT_IN_CONCEPT_KEYS:
        _add(
            issues,
            "admitted_concepts",
            BuiltInRegistryValidationCode.REGISTRY_NOT_CLOSED,
            "registry concepts are not the exact approved closed set",
        )

    if registry.manifest.namespace_ref != namespace.namespace_id:
        _add(
            issues,
            "manifest.namespace_ref",
            BuiltInRegistryValidationCode.NAMESPACE_MISMATCH,
            "manifest does not name the current namespace",
        )

    if registry.manifest.concept_refs != concept_ids:
        _add(
            issues,
            "manifest.concept_refs",
            BuiltInRegistryValidationCode.IDENTITY_MISMATCH,
            "manifest concept references do not match the registry tuple",
        )

    lineage_ids = tuple(
        expected_resource_lineage_id(concept)
        for concept in concepts
    )
    if registry.manifest.concept_lineage_refs != lineage_ids:
        _add(
            issues,
            "manifest.concept_lineage_refs",
            BuiltInRegistryValidationCode.IDENTITY_MISMATCH,
            "manifest lineage references do not match current concepts",
        )

    provenance_ids = {
        record.provenance_id
        for record in registry.governance_batch.provenance_records
    }

    for index, (concept, definition) in enumerate(
        zip(
            concepts,
            BUILT_IN_CONCEPT_DEFINITIONS,
        )
    ):
        path = f"admitted_concepts[{index}]"

        if type(concept) is not ControlledConceptIdentity:
            _add(
                issues,
                path,
                BuiltInRegistryValidationCode.TYPE_MISMATCH,
                "exact ControlledConceptIdentity required",
            )
            continue

        expectations = (
            ("namespace_id", concept.namespace_id, namespace.namespace_id),
            ("concept_key", concept.concept_key, definition.concept_key),
            (
                "preferred_label",
                concept.preferred_label,
                definition.preferred_label,
            ),
            ("definition", concept.definition, definition.definition),
            ("version", concept.version, "v3"),
            (
                "lifecycle_state",
                concept.lifecycle_state,
                ConceptLifecycleState.ADMITTED,
            ),
            ("scope_tags", concept.scope_tags, definition.scope_tags),
            (
                "permitted_uses",
                concept.permitted_uses,
                definition.permitted_uses,
            ),
            (
                "prohibited_uses",
                concept.prohibited_uses,
                definition.prohibited_uses,
            ),
            (
                "prohibited_authorities",
                concept.prohibited_authorities,
                definition.prohibited_authorities,
            ),
        )

        for field_name, actual, expected in expectations:
            if actual != expected:
                _add(
                    issues,
                    f"{path}.{field_name}",
                    BuiltInRegistryValidationCode.MANIFEST_BOUNDARY_MISMATCH,
                    "concept field does not match the approved definition",
                )

        if concept.concept_id != recompute_resource_id(concept):
            _add(
                issues,
                f"{path}.concept_id",
                BuiltInRegistryValidationCode.IDENTITY_MISMATCH,
                "concept ID does not match its canonical body",
            )

        if concept.provenance_ref not in provenance_ids:
            _add(
                issues,
                f"{path}.provenance_ref",
                BuiltInRegistryValidationCode.PROVENANCE_MISMATCH,
                "concept provenance is absent from the governance batch",
            )

        if (
            concept.semantic_class_refs
            or concept.sense_refs
            or concept.relation_type_refs
        ):
            _add(
                issues,
                path,
                BuiltInRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH,
                "sense, semantic-class, and relation references must remain empty until their later slices",
            )

    current_resources = {
        (
            type(item),
            item.namespace_id
            if isinstance(item, ConceptNamespaceIdentity)
            else item.concept_id,
        )
        for item in registry.governance_batch.resources
        if (
            isinstance(item, ConceptNamespaceIdentity)
            and item.lifecycle_state
            is ConceptLifecycleState.ARCHITECTURE_ADMITTED
        )
        or (
            isinstance(item, ControlledConceptIdentity)
            and item.lifecycle_state is ConceptLifecycleState.ADMITTED
        )
    }
    expected_current = {
        (ConceptNamespaceIdentity, namespace.namespace_id),
        *(
            (ControlledConceptIdentity, concept.concept_id)
            for concept in concepts
        ),
    }
    if current_resources != expected_current:
        _add(
            issues,
            "governance_batch.resources",
            BuiltInRegistryValidationCode.HISTORY_MISSING,
            "current active resource set does not match the closed registry",
        )

    resource_type_counts = Counter(
        type(item)
        for item in registry.governance_batch.resources
    )
    if resource_type_counts != Counter(
        {
            ConceptNamespaceIdentity: 3,
            ControlledConceptIdentity: 12,
        }
    ):
        _add(
            issues,
            "governance_batch.resources",
            BuiltInRegistryValidationCode.REGISTRY_COUNT_MISMATCH,
            "governance history must contain one three-version namespace and four three-version concept lineages",
        )

    if registry.governance_batch.registry_population_installed is not False:
        _add(
            issues,
            "governance_batch.registry_population_installed",
            BuiltInRegistryValidationCode.MANIFEST_BOUNDARY_MISMATCH,
            "semantic lifecycle batch must not claim registry installation",
        )

    if registry.manifest.registry_population_authorized is not True:
        _add(
            issues,
            "manifest.registry_population_authorized",
            BuiltInRegistryValidationCode.MANIFEST_BOUNDARY_MISMATCH,
            "registry population must be authorized only by the Slice 37C manifest",
        )

    return _report(issues)


def assert_built_in_registry(
    registry: BuiltInConceptRegistry,
) -> BuiltInConceptRegistry:
    report = validate_built_in_registry(registry)
    if not report.ok:
        raise BuiltInRegistryValidationError(report)
    return registry
