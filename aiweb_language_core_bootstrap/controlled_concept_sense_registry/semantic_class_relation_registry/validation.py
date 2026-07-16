"""Fail-closed validation for Slice 37E semantic classes and relations."""

from __future__ import annotations

from collections import Counter

from ..governed_lifecycle import validate_governance_batch
from ..schema import (
    ConceptLifecycleState,
    RelationDirection,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
)
from .authority import (
    MEMBERSHIP_DEFINITIONS,
    PROHIBITED_IMPLICATION_KINDS,
    RELATION_FAMILY_DEFINITIONS,
    RELATION_STATE_DEFINITIONS,
    RELATION_TYPE_DEFINITIONS,
    SEMANTIC_CLASS_DEFINITIONS,
)
from .schema import (
    SLICE37E_EXPECTED_CLASS_COUNT,
    SLICE37E_EXPECTED_INVERSE_DECLARATION_COUNT,
    SLICE37E_EXPECTED_MEMBERSHIP_COUNT,
    SLICE37E_EXPECTED_PROHIBITED_IMPLICATION_COUNT,
    SLICE37E_EXPECTED_RELATION_FAMILY_COUNT,
    SLICE37E_EXPECTED_RELATION_STATE_POLICY_COUNT,
    SLICE37E_EXPECTED_RELATION_TYPE_COUNT,
    SLICE37E_EXPECTED_RELATION_VERSION_COUNT,
    SLICE37E_SCHEMA_VERSION,
    ConceptClassMembershipRule,
    InverseRelationDeclaration,
    ProhibitedImplicationRule,
    RelationEligibilityRequest,
    RelationEligibilityResult,
    RelationEligibilityState,
    RelationFamilyDefinition,
    RelationStatePolicy,
    RelationSymmetry,
    RelationTypeRule,
    RelationVersionIdentity,
    SemanticClassDefinition,
    SemanticClassRelationRegistry,
    SemanticClassRelationValidationCode,
    SemanticClassRelationValidationError,
    SemanticClassRelationValidationIssue,
    SemanticClassRelationValidationReport,
)


EXPECTED_PREDECESSOR_DIGEST = (
    "slice37d_sense_term_mapping_registry:"
    "f276c9b13cb9bb1e1394e87ecb01a6e9aa0b786617e9f90129c13500fac6e4c5"
)


def _add(issues, path, code, detail):
    issues.append(
        SemanticClassRelationValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def _report(issues):
    ordered = tuple(
        sorted(
            issues,
            key=lambda item: (item.path, item.code.value, item.detail),
        )
    )
    return SemanticClassRelationValidationReport(ok=not ordered, issues=ordered)


def _text(value, *, path, issues, allow_outer_whitespace=False):
    if not isinstance(value, str):
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.TYPE_MISMATCH,
            "expected str",
        )
        return False
    if not value:
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.REQUIRED_VALUE_MISSING,
            "text must be non-empty",
        )
        return False
    if any(ord(character) < 32 for character in value):
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.INVALID_TEXT,
            "control characters are prohibited",
        )
        return False
    if not allow_outer_whitespace and value != value.strip():
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.INVALID_TEXT,
            "text must be trimmed",
        )
        return False
    return True


def _tuple_of_text(value, *, path, issues, allow_empty=True):
    if not isinstance(value, tuple):
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.TYPE_MISMATCH,
            "expected tuple",
        )
        return ()
    for index, item in enumerate(value):
        _text(item, path=f"{path}[{index}]", issues=issues)
    if not allow_empty and not value:
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.REQUIRED_VALUE_MISSING,
            "tuple must not be empty",
        )
    if len(value) != len(set(value)):
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.DUPLICATE_VALUE,
            "tuple values must be unique",
        )
    return value


def _exact_type(value, expected, *, path, issues):
    if type(value) is not expected:
        _add(
            issues,
            path,
            SemanticClassRelationValidationCode.TYPE_MISMATCH,
            f"exact {expected.__name__} required",
        )
        return False
    return True


def _identity(record, *, field, path, issues):
    if getattr(record, field) != record.expected_id():
        _add(
            issues,
            f"{path}.{field}",
            SemanticClassRelationValidationCode.IDENTITY_MISMATCH,
            "record identity does not match canonical body",
        )


def _duplicates(values):
    return tuple(sorted(key for key, count in Counter(values).items() if count > 1))


def validate_eligibility_request(request):
    issues = []
    if not _exact_type(
        request,
        RelationEligibilityRequest,
        path="$",
        issues=issues,
    ):
        return _report(issues)
    if request.schema_version != SLICE37E_SCHEMA_VERSION:
        _add(
            issues,
            "schema_version",
            SemanticClassRelationValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37E_SCHEMA_VERSION}",
        )
    _identity(request, field="request_id", path="$", issues=issues)
    _text(request.relation_type_id, path="relation_type_id", issues=issues)
    _text(request.domain_concept_id, path="domain_concept_id", issues=issues)
    _text(request.range_concept_id, path="range_concept_id", issues=issues)
    _tuple_of_text(
        request.requested_scope_tags,
        path="requested_scope_tags",
        issues=issues,
        allow_empty=False,
    )
    return _report(issues)


def assert_eligibility_request(request):
    report = validate_eligibility_request(request)
    if not report.ok:
        raise SemanticClassRelationValidationError(report)
    return request


def validate_eligibility_result(result):
    issues = []
    if not _exact_type(
        result,
        RelationEligibilityResult,
        path="$",
        issues=issues,
    ):
        return _report(issues)
    if result.schema_version != SLICE37E_SCHEMA_VERSION:
        _add(
            issues,
            "schema_version",
            SemanticClassRelationValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37E_SCHEMA_VERSION}",
        )
    _identity(result, field="result_id", path="$", issues=issues)
    _text(result.request_ref, path="request_ref", issues=issues)
    if not isinstance(result.state, RelationEligibilityState):
        _add(
            issues,
            "state",
            SemanticClassRelationValidationCode.INVALID_ENUM,
            "expected RelationEligibilityState",
        )
    _tuple_of_text(
        result.matched_domain_membership_refs,
        path="matched_domain_membership_refs",
        issues=issues,
    )
    _tuple_of_text(
        result.matched_range_membership_refs,
        path="matched_range_membership_refs",
        issues=issues,
    )
    _text(result.reason, path="reason", issues=issues)
    _tuple_of_text(
        result.prohibited_implication_refs,
        path="prohibited_implication_refs",
        issues=issues,
        allow_empty=False,
    )
    false_fields = (
        "relation_instance_created",
        "relation_fact_asserted",
        "truth_determined",
        "evidence_sufficiency_determined",
        "verified_status_applied",
        "implementation_determined",
    )
    for field in false_fields:
        if getattr(result, field) is not False:
            _add(
                issues,
                field,
                SemanticClassRelationValidationCode.RELATION_TRUTH_AUTHORITY_PROHIBITED,
                "must remain false",
            )
    expected_eligible = result.state is RelationEligibilityState.ELIGIBLE_TYPE_ONLY
    if result.eligible_for_later_instance_review is not expected_eligible:
        _add(
            issues,
            "eligible_for_later_instance_review",
            SemanticClassRelationValidationCode.DOMAIN_RANGE_RULE_MISMATCH,
            "eligibility flag must match exact result state",
        )
    return _report(issues)


def assert_eligibility_result(result):
    report = validate_eligibility_result(result)
    if not report.ok:
        raise SemanticClassRelationValidationError(report)
    return result


def validate_registry(registry):
    issues = []
    if not _exact_type(
        registry,
        SemanticClassRelationRegistry,
        path="$",
        issues=issues,
    ):
        return _report(issues)

    manifest = registry.manifest
    if manifest.schema_version != SLICE37E_SCHEMA_VERSION:
        _add(
            issues,
            "manifest.schema_version",
            SemanticClassRelationValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37E_SCHEMA_VERSION}",
        )
    _identity(manifest, field="manifest_id", path="manifest", issues=issues)

    if registry.predecessor_registry.registry_digest() != EXPECTED_PREDECESSOR_DIGEST:
        _add(
            issues,
            "predecessor_registry",
            SemanticClassRelationValidationCode.PREDECESSOR_REGISTRY_MISMATCH,
            "exact committed Slice 37D registry digest required",
        )

    governance = validate_governance_batch(registry.governance_batch)
    if not governance.ok:
        for item in governance.issues:
            _add(
                issues,
                f"governance_batch.{item.path}",
                SemanticClassRelationValidationCode.GOVERNANCE_BATCH_INVALID,
                f"{item.code.value}: {item.detail}",
            )

    count_pairs = (
        ("semantic_classes", len(registry.semantic_classes), SLICE37E_EXPECTED_CLASS_COUNT),
        ("class_definitions", len(registry.class_definitions), SLICE37E_EXPECTED_CLASS_COUNT),
        ("memberships", len(registry.memberships), SLICE37E_EXPECTED_MEMBERSHIP_COUNT),
        ("relation_families", len(registry.relation_families), SLICE37E_EXPECTED_RELATION_FAMILY_COUNT),
        ("relation_family_definitions", len(registry.relation_family_definitions), SLICE37E_EXPECTED_RELATION_FAMILY_COUNT),
        ("relation_types", len(registry.relation_types), SLICE37E_EXPECTED_RELATION_TYPE_COUNT),
        ("relation_type_rules", len(registry.relation_type_rules), SLICE37E_EXPECTED_RELATION_TYPE_COUNT),
        ("inverse_declarations", len(registry.inverse_declarations), SLICE37E_EXPECTED_INVERSE_DECLARATION_COUNT),
        ("relation_versions", len(registry.relation_versions), SLICE37E_EXPECTED_RELATION_VERSION_COUNT),
        ("relation_state_policies", len(registry.relation_state_policies), SLICE37E_EXPECTED_RELATION_STATE_POLICY_COUNT),
        ("prohibited_implications", len(registry.prohibited_implications), SLICE37E_EXPECTED_PROHIBITED_IMPLICATION_COUNT),
    )
    for path, actual, expected in count_pairs:
        if actual != expected:
            _add(
                issues,
                path,
                SemanticClassRelationValidationCode.REGISTRY_COUNT_MISMATCH,
                f"expected {expected}, found {actual}",
            )

    class_ids = tuple(item.semantic_class_id for item in registry.semantic_classes)
    family_ids = tuple(item.relation_family_id for item in registry.relation_families)
    type_ids = tuple(item.relation_type_id for item in registry.relation_types)
    concept_ids = {
        item.concept_id
        for item in registry.predecessor_registry.concept_registry.admitted_concepts
    }
    provenance_ids = {
        item.provenance_id for item in registry.governance_batch.provenance_records
    }
    implication_ids = tuple(
        item.implication_rule_id for item in registry.prohibited_implications
    )

    for path, values in (
        ("semantic_classes", class_ids),
        ("relation_families", family_ids),
        ("relation_types", type_ids),
        ("memberships", tuple(item.membership_id for item in registry.memberships)),
        ("prohibited_implications", implication_ids),
    ):
        duplicate = _duplicates(values)
        if duplicate:
            _add(
                issues,
                path,
                SemanticClassRelationValidationCode.DUPLICATE_VALUE,
                f"duplicate identities: {duplicate}",
            )

    expected_class_keys = tuple(item.class_key for item in SEMANTIC_CLASS_DEFINITIONS)
    if tuple(item.class_key for item in registry.semantic_classes) != expected_class_keys:
        _add(
            issues,
            "semantic_classes",
            SemanticClassRelationValidationCode.REGISTRY_NOT_CLOSED,
            "class-key order/set differs from approved closed set",
        )
    expected_family_keys = tuple(item.family_key for item in RELATION_FAMILY_DEFINITIONS)
    if tuple(item.family_key for item in registry.relation_families) != expected_family_keys:
        _add(
            issues,
            "relation_families",
            SemanticClassRelationValidationCode.REGISTRY_NOT_CLOSED,
            "family-key order/set differs from approved closed set",
        )
    expected_type_keys = tuple(item.relation_key for item in RELATION_TYPE_DEFINITIONS)
    if tuple(item.relation_key for item in registry.relation_types) != expected_type_keys:
        _add(
            issues,
            "relation_types",
            SemanticClassRelationValidationCode.REGISTRY_NOT_CLOSED,
            "relation-key order/set differs from approved closed set",
        )

    for index, item in enumerate(registry.semantic_classes):
        path = f"semantic_classes[{index}]"
        if type(item) is not SemanticClassIdentity:
            _add(issues, path, SemanticClassRelationValidationCode.TYPE_MISMATCH, "exact SemanticClassIdentity required")
            continue
        if item.semantic_class_id != item.expected_id():
            _add(issues, f"{path}.semantic_class_id", SemanticClassRelationValidationCode.IDENTITY_MISMATCH, "identity mismatch")
        if item.lifecycle_state is not ConceptLifecycleState.ARCHITECTURE_ADMITTED:
            _add(issues, f"{path}.lifecycle_state", SemanticClassRelationValidationCode.INVALID_ENUM, "architecture_admitted required")
        if item.provenance_ref not in provenance_ids:
            _add(issues, f"{path}.provenance_ref", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "provenance not found")

    class_definition_by_ref = {}
    for index, item in enumerate(registry.class_definitions):
        path = f"class_definitions[{index}]"
        if not _exact_type(item, SemanticClassDefinition, path=path, issues=issues):
            continue
        _identity(item, field="definition_id", path=path, issues=issues)
        class_definition_by_ref[item.semantic_class_ref] = item
        if item.semantic_class_ref not in class_ids:
            _add(issues, f"{path}.semantic_class_ref", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "class not found")
        if any(parent not in class_ids for parent in item.parent_class_refs):
            _add(issues, f"{path}.parent_class_refs", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "parent class not found")
        if item.class_membership_creates_authority or item.class_membership_creates_relation_instance:
            _add(issues, path, SemanticClassRelationValidationCode.CLASS_MEMBERSHIP_AUTHORITY_PROHIBITED, "class definition may not grant authority or create relation instances")
        if set(item.prohibited_implication_refs) != set(implication_ids[:8]):
            _add(issues, f"{path}.prohibited_implication_refs", SemanticClassRelationValidationCode.PROHIBITED_IMPLICATION_MISMATCH, "exact class-membership implication refusals required")

    expected_membership_pairs = tuple(
        (
            next(x.concept_id for x in registry.predecessor_registry.concept_registry.admitted_concepts if x.concept_key == item.concept_key),
            next(x.semantic_class_id for x in registry.semantic_classes if x.class_key == item.class_key),
        )
        for item in MEMBERSHIP_DEFINITIONS
    )
    actual_membership_pairs = tuple(
        (item.concept_ref, item.semantic_class_ref) for item in registry.memberships
    )
    if actual_membership_pairs != expected_membership_pairs:
        _add(issues, "memberships", SemanticClassRelationValidationCode.REGISTRY_NOT_CLOSED, "membership set/order differs from approved closed set")

    for index, item in enumerate(registry.memberships):
        path = f"memberships[{index}]"
        if not _exact_type(item, ConceptClassMembershipRule, path=path, issues=issues):
            continue
        _identity(item, field="membership_id", path=path, issues=issues)
        if item.concept_ref not in concept_ids:
            _add(issues, f"{path}.concept_ref", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "concept not found")
        if item.semantic_class_ref not in class_ids:
            _add(issues, f"{path}.semantic_class_ref", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "class not found")
        if item.lifecycle_state is not ConceptLifecycleState.ARCHITECTURE_ADMITTED:
            _add(issues, f"{path}.lifecycle_state", SemanticClassRelationValidationCode.INVALID_ENUM, "architecture_admitted required")
        authority_flags = (
            item.creates_evidence_authority,
            item.creates_memory_authority,
            item.creates_permission_authority,
            item.creates_action_authority,
            item.creates_delivery_authority,
            item.creates_identity_authority,
            item.creates_runtime_authority,
            item.creates_economic_authority,
            item.creates_relation_instance,
        )
        if any(authority_flags):
            _add(issues, path, SemanticClassRelationValidationCode.CLASS_MEMBERSHIP_AUTHORITY_PROHIBITED, "all class-membership authority fields must remain false")
        if set(item.prohibited_implication_refs) != set(implication_ids[:8]):
            _add(issues, f"{path}.prohibited_implication_refs", SemanticClassRelationValidationCode.PROHIBITED_IMPLICATION_MISMATCH, "exact class-membership implication refusals required")

    family_definition_by_ref = {}
    for index, item in enumerate(registry.relation_family_definitions):
        path = f"relation_family_definitions[{index}]"
        if not _exact_type(item, RelationFamilyDefinition, path=path, issues=issues):
            continue
        _identity(item, field="definition_id", path=path, issues=issues)
        family_definition_by_ref[item.relation_family_ref] = item
        if item.relation_family_ref not in family_ids:
            _add(issues, f"{path}.relation_family_ref", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "family not found")
        if any(ref not in type_ids for ref in item.relation_type_refs):
            _add(issues, f"{path}.relation_type_refs", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "relation type not found")
        if item.relation_instances_admitted:
            _add(issues, f"{path}.relation_instances_admitted", SemanticClassRelationValidationCode.RELATION_INSTANCE_POPULATION_PROHIBITED, "must remain false")

    rule_by_type = {}
    for index, item in enumerate(registry.relation_type_rules):
        path = f"relation_type_rules[{index}]"
        if not _exact_type(item, RelationTypeRule, path=path, issues=issues):
            continue
        _identity(item, field="rule_id", path=path, issues=issues)
        rule_by_type[item.relation_type_ref] = item
        if item.relation_type_ref not in type_ids:
            _add(issues, f"{path}.relation_type_ref", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "relation type not found")
        if any(ref not in class_ids for ref in (*item.permitted_domain_class_refs, *item.permitted_range_class_refs)):
            _add(issues, path, SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "domain or range class not found")
        if item.direction is RelationDirection.SYMMETRIC and item.symmetry is not RelationSymmetry.SYMMETRIC:
            _add(issues, path, SemanticClassRelationValidationCode.DIRECTION_SYMMETRY_MISMATCH, "symmetric direction requires symmetric declaration")
        if item.direction is RelationDirection.DIRECTED and item.symmetry is not RelationSymmetry.ASYMMETRIC:
            _add(issues, path, SemanticClassRelationValidationCode.DIRECTION_SYMMETRY_MISMATCH, "directed relation requires asymmetric declaration")
        forbidden_true = (
            item.relation_instances_admitted,
            item.truth_determined,
            item.evidence_sufficiency_determined,
            item.verified_status_applied,
            item.implementation_determined,
        )
        if any(forbidden_true):
            _add(issues, path, SemanticClassRelationValidationCode.RELATION_TRUTH_AUTHORITY_PROHIBITED, "relation rule may not create facts, truth, evidence, status, or implementation")
        if set(item.prohibited_implication_refs) != set(implication_ids[8:]):
            _add(issues, f"{path}.prohibited_implication_refs", SemanticClassRelationValidationCode.PROHIBITED_IMPLICATION_MISMATCH, "exact relation implication refusals required")

    for index, relation_type in enumerate(registry.relation_types):
        path = f"relation_types[{index}]"
        if type(relation_type) is not SemanticRelationTypeIdentity:
            _add(issues, path, SemanticClassRelationValidationCode.TYPE_MISMATCH, "exact SemanticRelationTypeIdentity required")
            continue
        if relation_type.relation_type_id != relation_type.expected_id():
            _add(issues, f"{path}.relation_type_id", SemanticClassRelationValidationCode.IDENTITY_MISMATCH, "identity mismatch")
        if relation_type.relation_family_id not in family_ids:
            _add(issues, f"{path}.relation_family_id", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "family not found")
        if relation_type.relation_instances_populated:
            _add(issues, f"{path}.relation_instances_populated", SemanticClassRelationValidationCode.RELATION_INSTANCE_POPULATION_PROHIBITED, "must remain false")
        rule = rule_by_type.get(relation_type.relation_type_id)
        if rule is None:
            _add(issues, path, SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "type rule missing")
        elif (
            rule.permitted_domain_class_refs != relation_type.domain_class_refs
            or rule.permitted_range_class_refs != relation_type.range_class_refs
            or rule.direction is not relation_type.direction
        ):
            _add(issues, path, SemanticClassRelationValidationCode.DOMAIN_RANGE_RULE_MISMATCH, "identity and rule domain/range/direction differ")

    if len(registry.inverse_declarations) == 1:
        declaration = registry.inverse_declarations[0]
        path = "inverse_declarations[0]"
        if _exact_type(declaration, InverseRelationDeclaration, path=path, issues=issues):
            _identity(declaration, field="declaration_id", path=path, issues=issues)
            keys_by_id = {item.relation_type_id: item.relation_key for item in registry.relation_types}
            actual_pair = (
                keys_by_id.get(declaration.relation_type_ref),
                keys_by_id.get(declaration.inverse_relation_type_ref),
            )
            if actual_pair != ("conceptual_component_of", "conceptually_composed_of"):
                _add(issues, path, SemanticClassRelationValidationCode.INVERSE_DECLARATION_MISMATCH, "only exact component/composition inverse pair is authorized")
            if not declaration.explicitly_authorized or not declaration.reciprocal_pair or declaration.creates_relation_instance:
                _add(issues, path, SemanticClassRelationValidationCode.INVERSE_DECLARATION_MISMATCH, "explicit reciprocal non-instantiating declaration required")
            for type_ref in (declaration.relation_type_ref, declaration.inverse_relation_type_ref):
                rule = rule_by_type.get(type_ref)
                if rule is None or rule.inverse_declaration_ref != declaration.declaration_id:
                    _add(issues, path, SemanticClassRelationValidationCode.INVERSE_DECLARATION_MISMATCH, "both inverse-facing type rules must cite the declaration")

    for index, item in enumerate(registry.relation_versions):
        path = f"relation_versions[{index}]"
        if not _exact_type(item, RelationVersionIdentity, path=path, issues=issues):
            continue
        _identity(item, field="relation_version_id", path=path, issues=issues)
        if item.relation_type_ref not in type_ids or item.current_version != "v3" or len(item.predecessor_version_refs) != 2 or not item.current:
            _add(issues, path, SemanticClassRelationValidationCode.VERSION_IDENTITY_MISMATCH, "current v3 identity with two predecessors required")

    expected_state_kinds = tuple(item.state_kind for item in RELATION_STATE_DEFINITIONS)
    if tuple(item.state_kind for item in registry.relation_state_policies) != expected_state_kinds:
        _add(issues, "relation_state_policies", SemanticClassRelationValidationCode.RELATION_STATE_POLICY_MISMATCH, "exact four-state policy set required")
    for index, item in enumerate(registry.relation_state_policies):
        path = f"relation_state_policies[{index}]"
        if not _exact_type(item, RelationStatePolicy, path=path, issues=issues):
            continue
        _identity(item, field="state_policy_id", path=path, issues=issues)
        if item.creates_relation_instance or item.determines_truth or item.authorizes_consequence:
            _add(issues, path, SemanticClassRelationValidationCode.RELATION_STATE_POLICY_MISMATCH, "state policy must be non-instantiating and non-authorizing")

    expected_implications = tuple(PROHIBITED_IMPLICATION_KINDS)
    if tuple(item.implication_kind for item in registry.prohibited_implications) != expected_implications:
        _add(issues, "prohibited_implications", SemanticClassRelationValidationCode.PROHIBITED_IMPLICATION_MISMATCH, "exact sixteen implication refusals required")
    for index, item in enumerate(registry.prohibited_implications):
        path = f"prohibited_implications[{index}]"
        if not _exact_type(item, ProhibitedImplicationRule, path=path, issues=issues):
            continue
        _identity(item, field="implication_rule_id", path=path, issues=issues)
        if item.allowed:
            _add(issues, f"{path}.allowed", SemanticClassRelationValidationCode.PROHIBITED_IMPLICATION_MISMATCH, "must remain false")

    expected_manifest_refs = {
        "semantic_class_refs": class_ids,
        "class_definition_refs": tuple(item.definition_id for item in registry.class_definitions),
        "membership_refs": tuple(item.membership_id for item in registry.memberships),
        "relation_family_refs": family_ids,
        "relation_family_definition_refs": tuple(item.definition_id for item in registry.relation_family_definitions),
        "relation_type_refs": type_ids,
        "relation_type_rule_refs": tuple(item.rule_id for item in registry.relation_type_rules),
        "inverse_declaration_refs": tuple(item.declaration_id for item in registry.inverse_declarations),
        "relation_version_refs": tuple(item.relation_version_id for item in registry.relation_versions),
        "relation_state_policy_refs": tuple(item.state_policy_id for item in registry.relation_state_policies),
        "prohibited_implication_refs": implication_ids,
    }
    for field, expected in expected_manifest_refs.items():
        if getattr(manifest, field) != expected:
            _add(issues, f"manifest.{field}", SemanticClassRelationValidationCode.REFERENCE_NOT_FOUND, "manifest references do not equal registry records")

    required_true = (
        "human_approved",
        "read_only",
        "closed_set",
        "exact_class_id_lookup_allowed",
        "exact_relation_family_id_lookup_allowed",
        "exact_relation_type_id_lookup_allowed",
        "exact_membership_lookup_allowed",
        "type_eligibility_evaluation_allowed",
        "registry_population_authorized",
        "semantic_class_population_authorized",
        "class_membership_population_authorized",
        "relation_family_population_authorized",
        "relation_type_population_authorized",
        "inverse_declaration_population_authorized",
        "structural_candidate_integration_deferred_to_slice37f",
    )
    for field in required_true:
        if getattr(manifest, field) is not True:
            _add(issues, f"manifest.{field}", SemanticClassRelationValidationCode.REGISTRY_NOT_READ_ONLY, "must be true")

    required_false = (
        "relation_instance_population_installed",
        "relation_fact_assertion_installed",
        "source_occurrence_interpretation_installed",
        "sense_selection_installed",
        "candidate_meaning_creation_installed",
        "structural_integration_installed",
        "truth_evaluation_installed",
        "evidence_validation_installed",
        "verified_status_application_installed",
        "permission_authority_installed",
        "action_authority_installed",
        "memory_authority_installed",
        "identity_authority_installed",
        "economic_authority_installed",
        "runtime_activation_installed",
        "route_registration_installed",
        "tool_activation_installed",
        "rendering_installed",
        "delivery_installed",
        "external_resource_loading_installed",
        "llm_authority_installed",
        "embedding_installed",
        "semantic_similarity_installed",
    )
    for field in required_false:
        if getattr(manifest, field) is not False:
            _add(issues, f"manifest.{field}", SemanticClassRelationValidationCode.LATER_AUTHORITY_INSTALLED, "must remain false")

    return _report(issues)


def assert_registry(registry):
    report = validate_registry(registry)
    if not report.ok:
        raise SemanticClassRelationValidationError(report)
    return registry
