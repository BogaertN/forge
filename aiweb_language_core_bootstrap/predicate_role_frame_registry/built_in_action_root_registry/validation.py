"""Fail-closed validation for the Slice 38C action-root registry."""

from __future__ import annotations

from collections import Counter
from typing import Any

from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
)
from ..validation import (
    validate_action_root_identity,
    validate_predicate_identity,
    validate_predicate_namespace_identity,
)
from ..governed_lifecycle.collection import validate_governance_batch
from ..governed_lifecycle.identity import expected_resource_lineage_id
from .authority import (
    BUILT_IN_ACTION_ROOT_DEFINITIONS,
    BUILT_IN_ACTION_ROOT_KEYS,
    BUILT_IN_PREDICATE_KEYS,
    SLICE38C_ADDITIONAL_AUTHORITY_LIMITATIONS,
    SLICE38C_COMMON_PROHIBITED_USES,
    SLICE38C_DECISION_OWNER_REF,
    SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES,
    SLICE38C_HUMAN_APPROVAL_REF,
    SLICE38C_NAMESPACE_DEFINITION,
    SLICE38C_NAMESPACE_KEY,
    SLICE38C_NAMESPACE_LABEL,
    SLICE38C_NAMESPACE_NON_SCOPE,
    SLICE38C_NAMESPACE_PERMITTED_USES,
    SLICE38C_NAMESPACE_SCOPE,
    SLICE38C_PROHIBITED_AUTHORITIES,
)
from .records import (
    ACTION_ROOT_HISTORIES,
    ADMITTED_ACTION_ROOTS,
    ADMITTED_PREDICATES,
    ALL_AUTHORITIES,
    ALL_RESOURCES,
    ALL_TRANSITIONS,
    CURRENT_NAMESPACE,
    NAMESPACE_HISTORY,
    PREDICATE_HISTORIES,
    PROVENANCE_RECORDS,
)
from .schema import (
    SLICE38C_EXPECTED_ACTION_ROOT_COUNT,
    SLICE38C_EXPECTED_NAMESPACE_COUNT,
    SLICE38C_EXPECTED_PREDICATE_COUNT,
    SLICE38C_SCHEMA_VERSION,
    SLICE38C_SOURCE_AUTHORITY_PACKET_SHA256,
    SLICE38C_SPEC_ID,
    SLICE38C_SPEC_VERSION,
    BuiltInActionRootRegistry,
    BuiltInActionRootRegistryManifest,
    BuiltInActionRootRegistryValidationCode,
    BuiltInActionRootRegistryValidationError,
    BuiltInActionRootRegistryValidationIssue,
    BuiltInActionRootRegistryValidationReport,
)


def _add(
    issues: list[BuiltInActionRootRegistryValidationIssue],
    path: str,
    code: BuiltInActionRootRegistryValidationCode,
    detail: str,
) -> None:
    issues.append(
        BuiltInActionRootRegistryValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def _report(
    issues: list[BuiltInActionRootRegistryValidationIssue],
) -> BuiltInActionRootRegistryValidationReport:
    ordered = tuple(
        sorted(
            issues,
            key=lambda item: (item.path, item.code.value, item.detail),
        )
    )
    return BuiltInActionRootRegistryValidationReport(
        ok=not ordered,
        issues=ordered,
    )


def _safe_equal(actual: Any, expected: Any) -> bool:
    try:
        return type(actual) is type(expected) and actual == expected
    except Exception:
        return False


def _exact(
    issues: list[BuiltInActionRootRegistryValidationIssue],
    *,
    path: str,
    actual: Any,
    expected: Any,
    code: BuiltInActionRootRegistryValidationCode = (
        BuiltInActionRootRegistryValidationCode.MANIFEST_BOUNDARY_MISMATCH
    ),
) -> None:
    if not _safe_equal(actual, expected):
        _add(issues, path, code, f"expected exact value {expected!r}")


def _unique_exact_strings(
    issues: list[BuiltInActionRootRegistryValidationIssue],
    *,
    path: str,
    values: Any,
) -> tuple[str, ...]:
    if type(values) is not tuple:
        _add(
            issues,
            path,
            BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
            "exact tuple required",
        )
        return ()
    safe: list[str] = []
    for index, value in enumerate(values):
        if type(value) is not str or not value or value != value.strip():
            _add(
                issues,
                f"{path}[{index}]",
                BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
                "trimmed non-empty exact str required",
            )
        else:
            safe.append(value)
    if len(safe) != len(set(safe)):
        _add(
            issues,
            path,
            BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED,
            "values must be unique",
        )
    return tuple(safe)


def validate_registry_manifest(
    manifest: object,
) -> BuiltInActionRootRegistryValidationReport:
    issues: list[BuiltInActionRootRegistryValidationIssue] = []

    if type(manifest) is not BuiltInActionRootRegistryManifest:
        _add(
            issues,
            "$",
            BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
            "exact BuiltInActionRootRegistryManifest required",
        )
        return _report(issues)

    try:
        expected_id = manifest.expected_id()
    except Exception as error:
        _add(
            issues,
            "manifest_id",
            BuiltInActionRootRegistryValidationCode.IDENTITY_MISMATCH,
            f"canonical manifest identity failed closed: {type(error).__name__}",
        )
    else:
        _exact(
            issues,
            path="manifest_id",
            actual=manifest.manifest_id,
            expected=expected_id,
            code=BuiltInActionRootRegistryValidationCode.IDENTITY_MISMATCH,
        )

    _exact(issues, path="schema_version", actual=manifest.schema_version, expected=SLICE38C_SCHEMA_VERSION,
           code=BuiltInActionRootRegistryValidationCode.SCHEMA_VERSION_MISMATCH)
    _exact(issues, path="spec_id", actual=manifest.spec_id, expected=SLICE38C_SPEC_ID)
    _exact(issues, path="spec_version", actual=manifest.spec_version, expected=SLICE38C_SPEC_VERSION)
    _exact(issues, path="source_authority_packet_sha256",
           actual=manifest.source_authority_packet_sha256,
           expected=SLICE38C_SOURCE_AUTHORITY_PACKET_SHA256)
    _exact(issues, path="decision_owner_ref", actual=manifest.decision_owner_ref,
           expected=SLICE38C_DECISION_OWNER_REF)
    _exact(issues, path="human_approval_ref", actual=manifest.human_approval_ref,
           expected=SLICE38C_HUMAN_APPROVAL_REF)
    _exact(issues, path="human_approved", actual=manifest.human_approved, expected=True)
    _exact(issues, path="registry_population_authorized",
           actual=manifest.registry_population_authorized, expected=True)
    _exact(issues, path="read_only", actual=manifest.read_only, expected=True,
           code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_READ_ONLY)
    _exact(issues, path="closed_set", actual=manifest.closed_set, expected=True,
           code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)
    _exact(issues, path="authority_limitations", actual=manifest.authority_limitations,
           expected=SLICE38C_ADDITIONAL_AUTHORITY_LIMITATIONS,
           code=BuiltInActionRootRegistryValidationCode.AUTHORITY_LIMIT_MISMATCH)
    _exact(issues, path="deferred_higher_consequence_families",
           actual=manifest.deferred_higher_consequence_families,
           expected=SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES,
           code=BuiltInActionRootRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH)

    allowed_true = (
        "exact_identity_lookup_allowed",
        "exact_internal_key_lookup_allowed",
        "exact_action_root_to_predicate_link_allowed",
        "participant_roles_deferred_to_slice38d",
        "predicate_frames_deferred_to_slice38e",
        "effect_and_capability_references_deferred_to_slice38f",
        "occurrence_candidate_proposal_deferred_to_slice38g",
        "disabled_integration_deferred_to_slice38h",
        "slice38a_preserved",
        "slice38b_preserved",
    )
    for field_name in allowed_true:
        _exact(issues, path=field_name, actual=getattr(manifest, field_name), expected=True)

    prohibited_true = (
        "surface_form_lookup_allowed",
        "surface_normalization_allowed",
        "occurrence_interpretation_installed",
        "predicate_selection_installed",
        "nearest_known_mapping_installed",
        "semantic_similarity_installed",
        "concept_to_predicate_conversion_installed",
        "participant_role_population_installed",
        "role_assignment_installed",
        "predicate_frame_population_installed",
        "frame_completion_installed",
        "effect_boundary_population_installed",
        "capability_reference_population_installed",
        "capability_routing_installed",
        "route_registration_installed",
        "tool_activation_installed",
        "action_execution_installed",
        "evidence_validation_installed",
        "memory_access_installed",
        "rendering_installed",
        "delivery_installed",
        "external_resource_loading_installed",
        "llm_authority_installed",
        "slice38a_superseded",
        "slice38b_superseded",
    )
    for field_name in prohibited_true:
        code = BuiltInActionRootRegistryValidationCode.RUNTIME_AUTHORITY_PROHIBITED
        if field_name in {"surface_form_lookup_allowed", "surface_normalization_allowed"}:
            code = BuiltInActionRootRegistryValidationCode.SURFACE_LOOKUP_PROHIBITED
        elif field_name in {"occurrence_interpretation_installed", "predicate_selection_installed"}:
            code = BuiltInActionRootRegistryValidationCode.OCCURRENCE_SELECTION_PROHIBITED
        elif field_name == "nearest_known_mapping_installed":
            code = BuiltInActionRootRegistryValidationCode.NEAREST_MAPPING_PROHIBITED
        elif field_name == "semantic_similarity_installed":
            code = BuiltInActionRootRegistryValidationCode.SIMILARITY_AUTHORITY_PROHIBITED
        elif field_name in {
            "participant_role_population_installed", "role_assignment_installed",
            "predicate_frame_population_installed", "frame_completion_installed",
            "effect_boundary_population_installed",
        }:
            code = BuiltInActionRootRegistryValidationCode.ROLE_FRAME_AUTHORITY_PROHIBITED
        elif field_name in {
            "capability_reference_population_installed", "capability_routing_installed",
            "route_registration_installed", "tool_activation_installed",
            "action_execution_installed",
        }:
            code = BuiltInActionRootRegistryValidationCode.CAPABILITY_AUTHORITY_PROHIBITED
        elif field_name == "evidence_validation_installed":
            code = BuiltInActionRootRegistryValidationCode.EVIDENCE_AUTHORITY_PROHIBITED
        elif field_name == "memory_access_installed":
            code = BuiltInActionRootRegistryValidationCode.MEMORY_AUTHORITY_PROHIBITED
        elif field_name == "external_resource_loading_installed":
            code = BuiltInActionRootRegistryValidationCode.EXTERNAL_RESOURCE_PROHIBITED
        elif field_name == "llm_authority_installed":
            code = BuiltInActionRootRegistryValidationCode.LLM_AUTHORITY_PROHIBITED
        elif field_name in {"slice38a_superseded", "slice38b_superseded"}:
            code = BuiltInActionRootRegistryValidationCode.PREDECESSOR_BOUNDARY_MISMATCH
        _exact(issues, path=field_name, actual=getattr(manifest, field_name), expected=False, code=code)

    roots = _unique_exact_strings(issues, path="action_root_refs", values=manifest.action_root_refs)
    root_lineages = _unique_exact_strings(
        issues, path="action_root_lineage_refs", values=manifest.action_root_lineage_refs
    )
    root_keys = _unique_exact_strings(issues, path="action_root_keys", values=manifest.action_root_keys)
    predicates = _unique_exact_strings(issues, path="predicate_refs", values=manifest.predicate_refs)
    predicate_lineages = _unique_exact_strings(
        issues, path="predicate_lineage_refs", values=manifest.predicate_lineage_refs
    )
    predicate_keys = _unique_exact_strings(issues, path="predicate_keys", values=manifest.predicate_keys)

    for path, values, expected_count in (
        ("action_root_refs", roots, SLICE38C_EXPECTED_ACTION_ROOT_COUNT),
        ("action_root_lineage_refs", root_lineages, SLICE38C_EXPECTED_ACTION_ROOT_COUNT),
        ("action_root_keys", root_keys, SLICE38C_EXPECTED_ACTION_ROOT_COUNT),
        ("predicate_refs", predicates, SLICE38C_EXPECTED_PREDICATE_COUNT),
        ("predicate_lineage_refs", predicate_lineages, SLICE38C_EXPECTED_PREDICATE_COUNT),
        ("predicate_keys", predicate_keys, SLICE38C_EXPECTED_PREDICATE_COUNT),
    ):
        if len(values) != expected_count:
            _add(
                issues,
                path,
                BuiltInActionRootRegistryValidationCode.REGISTRY_COUNT_MISMATCH,
                f"expected exactly {expected_count} entries",
            )

    _exact(issues, path="action_root_keys", actual=manifest.action_root_keys,
           expected=BUILT_IN_ACTION_ROOT_KEYS,
           code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)
    _exact(issues, path="predicate_keys", actual=manifest.predicate_keys,
           expected=BUILT_IN_PREDICATE_KEYS,
           code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)
    return _report(issues)


def _resource_ids(records: tuple[object, ...]) -> tuple[str, ...]:
    result: list[str] = []
    for record in records:
        if type(record) is PredicateNamespaceIdentity:
            result.append(record.namespace_id)
        elif type(record) is ActionRootIdentity:
            result.append(record.action_root_id)
        elif type(record) is PredicateIdentity:
            result.append(record.predicate_id)
        else:
            result.append("")
    return tuple(result)


def _validate_built_in_action_root_registry(
    registry: object,
) -> BuiltInActionRootRegistryValidationReport:
    issues: list[BuiltInActionRootRegistryValidationIssue] = []

    if type(registry) is not BuiltInActionRootRegistry:
        _add(
            issues,
            "$",
            BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
            "exact BuiltInActionRootRegistry required",
        )
        return _report(issues)

    manifest_report = validate_registry_manifest(registry.manifest)
    for item in manifest_report.issues:
        _add(issues, f"manifest.{item.path}", item.code, item.detail)

    try:
        governance_report = validate_governance_batch(registry.governance_batch)
    except Exception as error:
        _add(
            issues,
            "governance_batch",
            BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID,
            f"governance validation raised {type(error).__name__}",
        )
    else:
        if not governance_report.ok:
            for item in governance_report.issues:
                _add(
                    issues,
                    f"governance_batch.{item.path}",
                    BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID,
                    f"{item.code.value}: {item.detail}",
                )

    if type(registry.current_namespace) is not PredicateNamespaceIdentity:
        _add(
            issues,
            "current_namespace",
            BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
            "exact PredicateNamespaceIdentity required",
        )
    else:
        namespace_report = validate_predicate_namespace_identity(registry.current_namespace)
        if not namespace_report.ok:
            _add(
                issues,
                "current_namespace",
                BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID,
                "namespace failed accepted Slice 38A validation",
            )
        for path, actual, expected in (
            ("namespace_key", registry.current_namespace.namespace_key, SLICE38C_NAMESPACE_KEY),
            ("label", registry.current_namespace.label, SLICE38C_NAMESPACE_LABEL),
            ("definition", registry.current_namespace.definition, SLICE38C_NAMESPACE_DEFINITION),
            ("scope", registry.current_namespace.scope, SLICE38C_NAMESPACE_SCOPE),
            ("non_scope", registry.current_namespace.non_scope, SLICE38C_NAMESPACE_NON_SCOPE),
            ("permitted_uses", registry.current_namespace.permitted_uses, SLICE38C_NAMESPACE_PERMITTED_USES),
            ("prohibited_uses", registry.current_namespace.prohibited_uses, SLICE38C_COMMON_PROHIBITED_USES),
            ("prohibited_authorities", registry.current_namespace.prohibited_authorities, SLICE38C_PROHIBITED_AUTHORITIES),
            ("lifecycle_state", registry.current_namespace.lifecycle_state, PredicateLifecycleState.ARCHITECTURE_ADMITTED),
        ):
            _exact(
                issues,
                path=f"current_namespace.{path}",
                actual=actual,
                expected=expected,
                code=(
                    BuiltInActionRootRegistryValidationCode.LIFECYCLE_STATE_MISMATCH
                    if path == "lifecycle_state"
                    else BuiltInActionRootRegistryValidationCode.NAMESPACE_MISMATCH
                ),
            )

    roots = registry.admitted_action_roots
    predicates = registry.admitted_predicates
    if type(roots) is not tuple:
        _add(issues, "admitted_action_roots", BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
             "exact tuple required")
        roots = ()
    if type(predicates) is not tuple:
        _add(issues, "admitted_predicates", BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
             "exact tuple required")
        predicates = ()

    if len(roots) != SLICE38C_EXPECTED_ACTION_ROOT_COUNT:
        _add(issues, "admitted_action_roots", BuiltInActionRootRegistryValidationCode.REGISTRY_COUNT_MISMATCH,
             f"expected exactly {SLICE38C_EXPECTED_ACTION_ROOT_COUNT} action roots")
    if len(predicates) != SLICE38C_EXPECTED_PREDICATE_COUNT:
        _add(issues, "admitted_predicates", BuiltInActionRootRegistryValidationCode.REGISTRY_COUNT_MISMATCH,
             f"expected exactly {SLICE38C_EXPECTED_PREDICATE_COUNT} predicates")

    root_ids: list[str] = []
    root_keys: list[str] = []
    predicate_ids: list[str] = []
    predicate_keys: list[str] = []

    definition_by_key = {
        definition.action_root_key: definition
        for definition in BUILT_IN_ACTION_ROOT_DEFINITIONS
    }
    provenance_by_reference = {
        record.source_reference: record.provenance_id
        for record in PROVENANCE_RECORDS
    }

    for index, root in enumerate(roots):
        path = f"admitted_action_roots[{index}]"
        if type(root) is not ActionRootIdentity:
            _add(issues, path, BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
                 "exact ActionRootIdentity required")
            continue
        root_ids.append(root.action_root_id)
        root_keys.append(root.action_root_key)
        report = validate_action_root_identity(root)
        if not report.ok:
            _add(issues, path, BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID,
                 "record failed accepted Slice 38A action-root validation")
        definition = definition_by_key.get(root.action_root_key)
        if definition is None:
            _add(issues, f"{path}.action_root_key", BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED,
                 "unapproved action-root key")
            continue
        expected_provenance = provenance_by_reference.get(definition.source_reference)
        expected_values = (
            ("namespace_id", root.namespace_id, CURRENT_NAMESPACE.namespace_id,
             BuiltInActionRootRegistryValidationCode.NAMESPACE_MISMATCH),
            ("preferred_label", root.preferred_label, definition.preferred_label,
             BuiltInActionRootRegistryValidationCode.AUTHORITY_LIMIT_MISMATCH),
            ("definition", root.definition, definition.definition,
             BuiltInActionRootRegistryValidationCode.AUTHORITY_LIMIT_MISMATCH),
            ("scope", root.scope, definition.scope,
             BuiltInActionRootRegistryValidationCode.SCOPE_MISMATCH),
            ("non_scope", root.non_scope, definition.non_scope,
             BuiltInActionRootRegistryValidationCode.NON_SCOPE_MISMATCH),
            ("provenance_ref", root.provenance_ref, expected_provenance,
             BuiltInActionRootRegistryValidationCode.PROVENANCE_MISMATCH),
            ("lifecycle_state", root.lifecycle_state, PredicateLifecycleState.ADMITTED,
             BuiltInActionRootRegistryValidationCode.LIFECYCLE_STATE_MISMATCH),
            ("concept_identity_refs", root.concept_identity_refs, (),
             BuiltInActionRootRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH),
            ("permitted_uses", root.permitted_uses, definition.permitted_uses,
             BuiltInActionRootRegistryValidationCode.PERMITTED_USE_MISMATCH),
            ("prohibited_uses", root.prohibited_uses, definition.prohibited_uses,
             BuiltInActionRootRegistryValidationCode.PROHIBITED_USE_MISMATCH),
            ("prohibited_authorities", root.prohibited_authorities, definition.prohibited_authorities,
             BuiltInActionRootRegistryValidationCode.AUTHORITY_LIMIT_MISMATCH),
        )
        for field_name, actual, expected, code in expected_values:
            _exact(issues, path=f"{path}.{field_name}", actual=actual, expected=expected, code=code)
        for field_name in (
            "frame_dependency_required", "participant_role_dependency_required",
            "speech_act_separation_required", "effect_boundary_dependency_required",
            "capability_non_invocation_required",
        ):
            _exact(issues, path=f"{path}.{field_name}", actual=getattr(root, field_name), expected=True,
                   code=BuiltInActionRootRegistryValidationCode.ROLE_FRAME_AUTHORITY_PROHIBITED)
        for field_name in ("occurrence_selection_allowed", "execution_authorized"):
            _exact(issues, path=f"{path}.{field_name}", actual=getattr(root, field_name), expected=False,
                   code=(BuiltInActionRootRegistryValidationCode.OCCURRENCE_SELECTION_PROHIBITED
                         if field_name == "occurrence_selection_allowed"
                         else BuiltInActionRootRegistryValidationCode.CAPABILITY_AUTHORITY_PROHIBITED))

    root_by_id = {record.action_root_id: record for record in roots if type(record) is ActionRootIdentity}
    definition_by_predicate_key = {
        definition.predicate_key: definition
        for definition in BUILT_IN_ACTION_ROOT_DEFINITIONS
    }
    for index, predicate in enumerate(predicates):
        path = f"admitted_predicates[{index}]"
        if type(predicate) is not PredicateIdentity:
            _add(issues, path, BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
                 "exact PredicateIdentity required")
            continue
        predicate_ids.append(predicate.predicate_id)
        predicate_keys.append(predicate.predicate_key)
        report = validate_predicate_identity(predicate)
        if not report.ok:
            _add(issues, path, BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID,
                 "record failed accepted Slice 38A predicate validation")
        definition = definition_by_predicate_key.get(predicate.predicate_key)
        if definition is None:
            _add(issues, f"{path}.predicate_key", BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED,
                 "unapproved predicate key")
            continue
        root = root_by_id.get(predicate.action_root_id)
        if root is None or root.action_root_key != definition.action_root_key:
            _add(issues, f"{path}.action_root_id", BuiltInActionRootRegistryValidationCode.ACTION_ROOT_LINK_MISMATCH,
                 "predicate must link to the exact corresponding admitted action root")
        expected_provenance = provenance_by_reference.get(definition.source_reference)
        expected_values = (
            ("namespace_id", predicate.namespace_id, CURRENT_NAMESPACE.namespace_id,
             BuiltInActionRootRegistryValidationCode.NAMESPACE_MISMATCH),
            ("provenance_ref", predicate.provenance_ref, expected_provenance,
             BuiltInActionRootRegistryValidationCode.PROVENANCE_MISMATCH),
            ("lifecycle_state", predicate.lifecycle_state, PredicateLifecycleState.ADMITTED,
             BuiltInActionRootRegistryValidationCode.LIFECYCLE_STATE_MISMATCH),
            ("concept_identity_refs", predicate.concept_identity_refs, (),
             BuiltInActionRootRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH),
            ("participant_role_schema_refs", predicate.participant_role_schema_refs, (),
             BuiltInActionRootRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH),
            ("predicate_frame_schema_refs", predicate.predicate_frame_schema_refs, (),
             BuiltInActionRootRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH),
            ("effect_boundary_refs", predicate.effect_boundary_refs, (),
             BuiltInActionRootRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH),
            ("capability_family_reference_refs", predicate.capability_family_reference_refs, (),
             BuiltInActionRootRegistryValidationCode.DEFERRED_REFERENCE_MISMATCH),
            ("permitted_uses", predicate.permitted_uses, definition.permitted_uses,
             BuiltInActionRootRegistryValidationCode.PERMITTED_USE_MISMATCH),
            ("prohibited_uses", predicate.prohibited_uses, definition.prohibited_uses,
             BuiltInActionRootRegistryValidationCode.PROHIBITED_USE_MISMATCH),
            ("prohibited_authorities", predicate.prohibited_authorities, definition.prohibited_authorities,
             BuiltInActionRootRegistryValidationCode.AUTHORITY_LIMIT_MISMATCH),
        )
        for field_name, actual, expected, code in expected_values:
            _exact(issues, path=f"{path}.{field_name}", actual=actual, expected=expected, code=code)
        for field_name in (
            "participant_role_dependency_required", "predicate_frame_dependency_required",
            "speech_act_separation_required", "capability_non_invocation_required",
        ):
            _exact(issues, path=f"{path}.{field_name}", actual=getattr(predicate, field_name), expected=True,
                   code=BuiltInActionRootRegistryValidationCode.ROLE_FRAME_AUTHORITY_PROHIBITED)
        for field_name in (
            "occurrence_selection_allowed", "selected_for_occurrence", "execution_authorized"
        ):
            _exact(issues, path=f"{path}.{field_name}", actual=getattr(predicate, field_name), expected=False,
                   code=(BuiltInActionRootRegistryValidationCode.OCCURRENCE_SELECTION_PROHIBITED
                         if field_name != "execution_authorized"
                         else BuiltInActionRootRegistryValidationCode.CAPABILITY_AUTHORITY_PROHIBITED))

    for values, code, path in (
        (root_ids, BuiltInActionRootRegistryValidationCode.DUPLICATE_ACTION_ROOT_ID, "admitted_action_roots"),
        (root_keys, BuiltInActionRootRegistryValidationCode.DUPLICATE_ACTION_ROOT_KEY, "admitted_action_roots"),
        (predicate_ids, BuiltInActionRootRegistryValidationCode.DUPLICATE_PREDICATE_ID, "admitted_predicates"),
        (predicate_keys, BuiltInActionRootRegistryValidationCode.DUPLICATE_PREDICATE_KEY, "admitted_predicates"),
    ):
        if any(count > 1 for count in Counter(values).values()):
            _add(issues, path, code, "registry identities and keys must be unique")

    _exact(issues, path="action_root_keys", actual=tuple(root_keys), expected=BUILT_IN_ACTION_ROOT_KEYS,
           code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)
    _exact(issues, path="predicate_keys", actual=tuple(predicate_keys), expected=BUILT_IN_PREDICATE_KEYS,
           code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)

    manifest = registry.manifest
    if type(manifest) is BuiltInActionRootRegistryManifest:
        _exact(issues, path="manifest.namespace_ref", actual=manifest.namespace_ref,
               expected=CURRENT_NAMESPACE.namespace_id,
               code=BuiltInActionRootRegistryValidationCode.NAMESPACE_MISMATCH)
        _exact(issues, path="manifest.action_root_refs", actual=manifest.action_root_refs,
               expected=tuple(root_ids),
               code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)
        _exact(issues, path="manifest.predicate_refs", actual=manifest.predicate_refs,
               expected=tuple(predicate_ids),
               code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)
        _exact(issues, path="manifest.action_root_lineage_refs",
               actual=manifest.action_root_lineage_refs,
               expected=tuple(expected_resource_lineage_id(record) for record in roots if type(record) is ActionRootIdentity),
               code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)
        _exact(issues, path="manifest.predicate_lineage_refs",
               actual=manifest.predicate_lineage_refs,
               expected=tuple(expected_resource_lineage_id(record) for record in predicates if type(record) is PredicateIdentity),
               code=BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED)

    batch = registry.governance_batch
    try:
        _exact(issues, path="governance_batch.resources", actual=_resource_ids(batch.resources),
               expected=_resource_ids(ALL_RESOURCES),
               code=BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID)
        _exact(issues, path="governance_batch.provenance_records",
               actual=tuple(record.provenance_id for record in batch.provenance_records),
               expected=tuple(record.provenance_id for record in PROVENANCE_RECORDS),
               code=BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID)
        _exact(issues, path="governance_batch.authority_records",
               actual=tuple(record.authority_id for record in batch.authority_records),
               expected=tuple(record.authority_id for record in ALL_AUTHORITIES),
               code=BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID)
        _exact(issues, path="governance_batch.transitions",
               actual=tuple(record.transition_id for record in batch.transitions),
               expected=tuple(record.transition_id for record in ALL_TRANSITIONS),
               code=BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID)
    except Exception as error:
        _add(issues, "governance_batch", BuiltInActionRootRegistryValidationCode.GOVERNANCE_BATCH_INVALID,
             f"exact governance custody comparison failed closed: {type(error).__name__}")

    expected_history_ids = {
        record.action_root_id
        for history in ACTION_ROOT_HISTORIES
        for record in history
    } | {
        record.predicate_id
        for history in PREDICATE_HISTORIES
        for record in history
    } | {record.namespace_id for record in NAMESPACE_HISTORY}
    actual_history_ids = set(_resource_ids(getattr(batch, "resources", ())))
    if expected_history_ids != actual_history_ids:
        _add(issues, "governance_batch.resources", BuiltInActionRootRegistryValidationCode.HISTORY_MISSING,
             "the exact namespace, action-root, and predicate lifecycle histories are required")

    excluded = set(SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES)
    if excluded.intersection(root_keys) or excluded.intersection(predicate_keys):
        _add(issues, "deferred_higher_consequence_families",
             BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED,
             "deferred higher-consequence candidates must not be admitted")

    return _report(issues)


def validate_built_in_action_root_registry(
    registry: object,
) -> BuiltInActionRootRegistryValidationReport:
    """Validate the closed registry and fail closed for every malformed value.

    Nested Slice 38A and Slice 38B records are immutable dataclasses, but Python
    callers can still construct malformed instances with ``dataclasses.replace``.
    No malformed nested field is allowed to escape this public validation
    boundary as an exception.  Internal validation faults therefore become a
    deterministic failed report rather than process failure or accidental
    acceptance.
    """

    if type(registry) is not BuiltInActionRootRegistry:
        issues: list[BuiltInActionRootRegistryValidationIssue] = []
        _add(
            issues,
            "$",
            BuiltInActionRootRegistryValidationCode.TYPE_MISMATCH,
            "exact BuiltInActionRootRegistry required",
        )
        return _report(issues)

    try:
        return _validate_built_in_action_root_registry(registry)
    except Exception as error:
        issues = []
        _add(
            issues,
            "$",
            BuiltInActionRootRegistryValidationCode.REGISTRY_NOT_CLOSED,
            (
                "registry validation failed closed without accepting malformed "
                f"custody: {type(error).__name__}"
            ),
        )
        return _report(issues)


def assert_built_in_action_root_registry(
    registry: object,
) -> BuiltInActionRootRegistry:
    report = validate_built_in_action_root_registry(registry)
    if not report.ok:
        raise BuiltInActionRootRegistryValidationError(report)
    assert type(registry) is BuiltInActionRootRegistry
    return registry
