#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 37E semantic classes and relation types."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import subprocess
import sys

REPOSITORY = Path(__file__).resolve().parents[1]
if str(REPOSITORY) not in sys.path:
    sys.path.insert(0, str(REPOSITORY))

from aiweb_language_core_bootstrap.controlled_concept_sense_registry.governed_lifecycle import (
    validate_governance_batch,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.semantic_class_relation_registry import (
    CLASS_DEFINITIONS,
    CURRENT_RELATION_FAMILIES,
    CURRENT_RELATION_TYPES,
    CURRENT_SEMANTIC_CLASSES,
    GOVERNANCE_BATCH,
    INVERSE_DECLARATIONS,
    MEMBERSHIPS,
    PROHIBITED_IMPLICATIONS,
    RELATION_STATE_POLICIES,
    RELATION_TYPE_RULES,
    RELATION_VERSIONS,
    SEMANTIC_CLASS_RELATION_REGISTRY,
    SLICE37E_EXPECTED_CLASS_COUNT,
    SLICE37E_EXPECTED_INVERSE_DECLARATION_COUNT,
    SLICE37E_EXPECTED_MEMBERSHIP_COUNT,
    SLICE37E_EXPECTED_PROHIBITED_IMPLICATION_COUNT,
    SLICE37E_EXPECTED_RELATION_FAMILY_COUNT,
    SLICE37E_EXPECTED_RELATION_STATE_POLICY_COUNT,
    SLICE37E_EXPECTED_RELATION_TYPE_COUNT,
    SLICE37E_EXPECTED_RELATION_VERSION_COUNT,
    SLICE37E_SCOPE_TAGS,
    RelationEligibilityState,
    RelationStateKind,
    SemanticClassRelationValidationError,
    assert_eligibility_request,
    assert_eligibility_result,
    assert_registry,
    evaluate_relation_type_eligibility,
    make_relation_eligibility_request,
    membership_by_id,
    memberships_for_concept,
    relation_family_by_id,
    relation_state_policy,
    relation_type_by_id,
    semantic_class_by_id,
    validate_eligibility_request,
    validate_eligibility_result,
    validate_registry,
)


checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def check_raises(expected, operation, message: str) -> None:
    global checks
    checks += 1
    try:
        operation()
    except expected:
        return
    raise AssertionError(message)


registry = SEMANTIC_CLASS_RELATION_REGISTRY
report = validate_registry(registry)
check(report.ok, f"registry validation failed: {report.issues}")
check(assert_registry(registry) is registry, "assert_registry must return registry")
check(validate_governance_batch(GOVERNANCE_BATCH).ok, "governance batch must validate")

check(len(CURRENT_SEMANTIC_CLASSES) == SLICE37E_EXPECTED_CLASS_COUNT, "class count")
check(len(CLASS_DEFINITIONS) == SLICE37E_EXPECTED_CLASS_COUNT, "class definition count")
check(len(MEMBERSHIPS) == SLICE37E_EXPECTED_MEMBERSHIP_COUNT, "membership count")
check(len(CURRENT_RELATION_FAMILIES) == SLICE37E_EXPECTED_RELATION_FAMILY_COUNT, "family count")
check(len(CURRENT_RELATION_TYPES) == SLICE37E_EXPECTED_RELATION_TYPE_COUNT, "type count")
check(len(RELATION_TYPE_RULES) == SLICE37E_EXPECTED_RELATION_TYPE_COUNT, "type-rule count")
check(len(INVERSE_DECLARATIONS) == SLICE37E_EXPECTED_INVERSE_DECLARATION_COUNT, "inverse count")
check(len(RELATION_VERSIONS) == SLICE37E_EXPECTED_RELATION_VERSION_COUNT, "version count")
check(len(RELATION_STATE_POLICIES) == SLICE37E_EXPECTED_RELATION_STATE_POLICY_COUNT, "state count")
check(len(PROHIBITED_IMPLICATIONS) == SLICE37E_EXPECTED_PROHIBITED_IMPLICATION_COUNT, "implication count")

for item in CURRENT_SEMANTIC_CLASSES:
    check(item.semantic_class_id == item.expected_id(), "class identity")
    check(semantic_class_by_id(item.semantic_class_id) is item, "exact class lookup")
    check(item.version == "v3", "class current version")
    check(item.lifecycle_state.value == "architecture_admitted", "class lifecycle")
    check(not any("authority class" == value for value in item.prohibited_authorities), "prohibited tuple is explicit text")

for item in CLASS_DEFINITIONS:
    check(item.definition_id == item.expected_id(), "class-definition identity")
    check(not item.class_membership_creates_authority, "class membership authority false")
    check(not item.class_membership_creates_relation_instance, "class membership relation false")
    check(tuple(item.scope_tags) == SLICE37E_SCOPE_TAGS, "class scope exact")
    check(len(item.prohibited_implication_refs) == 8, "class implication refusals")

for item in MEMBERSHIPS:
    check(item.membership_id == item.expected_id(), "membership identity")
    check(membership_by_id(item.membership_id) is item, "exact membership lookup")
    check(item in memberships_for_concept(item.concept_ref), "membership-by-concept")
    check(item.lifecycle_state.value == "architecture_admitted", "membership lifecycle")
    for field in (
        "creates_evidence_authority",
        "creates_memory_authority",
        "creates_permission_authority",
        "creates_action_authority",
        "creates_delivery_authority",
        "creates_identity_authority",
        "creates_runtime_authority",
        "creates_economic_authority",
        "creates_relation_instance",
    ):
        check(getattr(item, field) is False, f"membership {field} must be false")
    check(len(item.prohibited_implication_refs) == 8, "membership implication refusals")

for item in CURRENT_RELATION_FAMILIES:
    check(item.relation_family_id == item.expected_id(), "family identity")
    check(relation_family_by_id(item.relation_family_id) is item, "family lookup")
    check(item.version == "v3", "family version")

family_by_key = {item.family_key: item for item in CURRENT_RELATION_FAMILIES}
check(
    set(family_by_key)
    == {
        "controlled_semantic_distinction",
        "bounded_non_equivalence",
        "conceptual_component",
        "conceptual_composition",
        "state_relevance",
        "representation_relevance",
    },
    "exact relation-family keys",
)

for item in CURRENT_RELATION_TYPES:
    check(item.relation_type_id == item.expected_id(), "type identity")
    check(relation_type_by_id(item.relation_type_id) is item, "type lookup")
    check(item.version == "v3", "type version")
    check(not item.relation_instances_populated, "no relation instances")
    check(item.inverse_relation_type_ref is None, "inverse is separate declaration")
    check(bool(item.domain_class_refs), "domain classes required")
    check(bool(item.range_class_refs), "range classes required")

for item in RELATION_TYPE_RULES:
    check(item.rule_id == item.expected_id(), "type-rule identity")
    check(not item.relation_instances_admitted, "no relation instance admission")
    check(not item.truth_determined, "no truth authority")
    check(not item.evidence_sufficiency_determined, "no evidence authority")
    check(not item.verified_status_applied, "no status authority")
    check(not item.implementation_determined, "no implementation authority")
    check(len(item.prohibited_implication_refs) == 8, "relation implication refusals")

inverse = INVERSE_DECLARATIONS[0]
check(inverse.declaration_id == inverse.expected_id(), "inverse identity")
check(inverse.explicitly_authorized, "inverse explicitly authorized")
check(inverse.reciprocal_pair, "inverse reciprocal pair")
check(not inverse.creates_relation_instance, "inverse creates no instance")
component_rule = next(
    item for item in RELATION_TYPE_RULES
    if relation_type_by_id(item.relation_type_ref).relation_key == "conceptual_component_of"
)
composition_rule = next(
    item for item in RELATION_TYPE_RULES
    if relation_type_by_id(item.relation_type_ref).relation_key == "conceptually_composed_of"
)
check(component_rule.inverse_declaration_ref == inverse.declaration_id, "component inverse reference")
check(composition_rule.inverse_declaration_ref == inverse.declaration_id, "composition inverse reference")

for item in RELATION_VERSIONS:
    check(item.relation_version_id == item.expected_id(), "version identity")
    check(item.current, "version current")
    check(item.current_version == "v3", "version v3")
    check(len(item.predecessor_version_refs) == 2, "two predecessor versions")

check(
    tuple(item.state_kind for item in RELATION_STATE_POLICIES)
    == tuple(RelationStateKind),
    "exact relation-state policies",
)
for item in RELATION_STATE_POLICIES:
    check(item.state_policy_id == item.expected_id(), "state identity")
    check(relation_state_policy(item.state_kind) is item, "state lookup")
    check(not item.creates_relation_instance, "state no instance")
    check(not item.determines_truth, "state no truth")
    check(not item.authorizes_consequence, "state no consequence")

for item in PROHIBITED_IMPLICATIONS:
    check(item.implication_rule_id == item.expected_id(), "implication identity")
    check(not item.allowed, "implication refusal")

concepts = registry.predecessor_registry.concept_registry.admitted_concepts
concept_by_key = {item.concept_key: item for item in concepts}
type_by_key = {item.relation_key: item for item in CURRENT_RELATION_TYPES}
check(
    type_by_key["conceptual_component_of"].relation_family_id
    == family_by_key["conceptual_component"].relation_family_id,
    "component type must use the Document 4 Section 30.18 family",
)
check(
    type_by_key["conceptually_composed_of"].relation_family_id
    == family_by_key["conceptual_composition"].relation_family_id,
    "composition type must use the Document 4 Section 30.19 family",
)
check(
    type_by_key["conceptual_component_of"].relation_family_id
    != type_by_key["conceptually_composed_of"].relation_family_id,
    "component and composition family identities must remain distinct",
)

positive_cases = (
    ("materially_distinct_from", "forge_controlled_concept_identity", "source_expression_form"),
    ("not_equivalent_within_scope", "concept_admission", "unknown_concept_condition"),
    ("conceptual_component_of", "source_expression_form", "forge_controlled_concept_identity"),
    ("conceptually_composed_of", "forge_controlled_concept_identity", "source_expression_form"),
    ("state_relevant_to", "unknown_concept_condition", "forge_controlled_concept_identity"),
    ("representation_relevant_to", "source_expression_form", "concept_admission"),
)
for relation_key, domain_key, range_key in positive_cases:
    request = make_relation_eligibility_request(
        relation_type_id=type_by_key[relation_key].relation_type_id,
        domain_concept_id=concept_by_key[domain_key].concept_id,
        range_concept_id=concept_by_key[range_key].concept_id,
        requested_scope_tags=SLICE37E_SCOPE_TAGS,
    )
    check(validate_eligibility_request(request).ok, "request validation")
    check(assert_eligibility_request(request) is request, "request assertion")
    result = evaluate_relation_type_eligibility(request)
    check(result.state is RelationEligibilityState.ELIGIBLE_TYPE_ONLY, "eligible state")
    check(result.eligible_for_later_instance_review, "eligible flag")
    check(not result.relation_instance_created, "no instance")
    check(not result.relation_fact_asserted, "no fact")
    check(not result.truth_determined, "no truth")
    check(validate_eligibility_result(result).ok, "result validation")
    check(assert_eligibility_result(result) is result, "result assertion")

unknown_type = make_relation_eligibility_request(
    relation_type_id="semantic_relation_type:missing",
    domain_concept_id=concepts[0].concept_id,
    range_concept_id=concepts[1].concept_id,
    requested_scope_tags=SLICE37E_SCOPE_TAGS,
)
check(evaluate_relation_type_eligibility(unknown_type).state is RelationEligibilityState.UNKNOWN_RELATION_TYPE, "unknown type")

unknown_domain = make_relation_eligibility_request(
    relation_type_id=type_by_key["materially_distinct_from"].relation_type_id,
    domain_concept_id="controlled_concept:missing",
    range_concept_id=concepts[0].concept_id,
    requested_scope_tags=SLICE37E_SCOPE_TAGS,
)
check(evaluate_relation_type_eligibility(unknown_domain).state is RelationEligibilityState.UNKNOWN_DOMAIN_CONCEPT, "unknown domain")

unknown_range = make_relation_eligibility_request(
    relation_type_id=type_by_key["materially_distinct_from"].relation_type_id,
    domain_concept_id=concepts[0].concept_id,
    range_concept_id="controlled_concept:missing",
    requested_scope_tags=SLICE37E_SCOPE_TAGS,
)
check(evaluate_relation_type_eligibility(unknown_range).state is RelationEligibilityState.UNKNOWN_RANGE_CONCEPT, "unknown range")

expanded_scope = make_relation_eligibility_request(
    relation_type_id=type_by_key["materially_distinct_from"].relation_type_id,
    domain_concept_id=concepts[0].concept_id,
    range_concept_id=concepts[1].concept_id,
    requested_scope_tags=(*SLICE37E_SCOPE_TAGS, "domain:unauthorized"),
)
check(evaluate_relation_type_eligibility(expanded_scope).state is RelationEligibilityState.PROHIBITED_SCOPE_EXPANSION, "scope expansion")

bad_state_domain = make_relation_eligibility_request(
    relation_type_id=type_by_key["state_relevant_to"].relation_type_id,
    domain_concept_id=concept_by_key["forge_controlled_concept_identity"].concept_id,
    range_concept_id=concept_by_key["source_expression_form"].concept_id,
    requested_scope_tags=SLICE37E_SCOPE_TAGS,
)
check(evaluate_relation_type_eligibility(bad_state_domain).state is RelationEligibilityState.DOMAIN_CLASS_NOT_PERMITTED, "domain class refusal")

# Explicit parent class metadata never generates implicit membership.
action_class = next(item for item in CURRENT_SEMANTIC_CLASSES if item.class_key == "action_type_concept")
action_definition = next(item for item in CLASS_DEFINITIONS if item.semantic_class_ref == action_class.semantic_class_id)
check(len(action_definition.parent_class_refs) == 1, "action class parent metadata")
concept_memberships = memberships_for_concept(concept_by_key["concept_admission"].concept_id)
check(len(concept_memberships) == 2, "only explicit dual membership")
check(
    {item.semantic_class_ref for item in concept_memberships}
    == {
        next(item.semantic_class_id for item in CURRENT_SEMANTIC_CLASSES if item.class_key == "occurrence_event_or_change_concept"),
        action_class.semantic_class_id,
    },
    "no automatic parent inheritance",
)

# Tamper tests must fail closed.
bad_manifest_registry = replace(
    registry,
    manifest=replace(registry.manifest, relation_instance_population_installed=True),
)
check(not validate_registry(bad_manifest_registry).ok, "manifest authority tamper rejected")

bad_membership = replace(MEMBERSHIPS[0], creates_evidence_authority=True)
bad_membership_registry = replace(
    registry,
    memberships=(bad_membership, *MEMBERSHIPS[1:]),
)
check(not validate_registry(bad_membership_registry).ok, "membership authority tamper rejected")

bad_rule = replace(RELATION_TYPE_RULES[0], truth_determined=True)
bad_rule_registry = replace(
    registry,
    relation_type_rules=(bad_rule, *RELATION_TYPE_RULES[1:]),
)
check(not validate_registry(bad_rule_registry).ok, "truth authority tamper rejected")

bad_inverse = replace(inverse, creates_relation_instance=True)
bad_inverse_registry = replace(registry, inverse_declarations=(bad_inverse,))
check(not validate_registry(bad_inverse_registry).ok, "inverse instance tamper rejected")

bad_request = replace(unknown_type, request_id="wrong")
check(not validate_eligibility_request(bad_request).ok, "bad request ID rejected")
check_raises(
    SemanticClassRelationValidationError,
    lambda: assert_eligibility_request(bad_request),
    "bad request assertion must fail",
)

positive_request = make_relation_eligibility_request(
    relation_type_id=type_by_key["materially_distinct_from"].relation_type_id,
    domain_concept_id=concepts[0].concept_id,
    range_concept_id=concepts[1].concept_id,
    requested_scope_tags=SLICE37E_SCOPE_TAGS,
)
positive_result = evaluate_relation_type_eligibility(positive_request)
bad_result = replace(positive_result, relation_fact_asserted=True)
check(not validate_eligibility_result(bad_result).ok, "relation fact tamper rejected")

check_raises(
    FrozenInstanceError,
    lambda: setattr(CURRENT_SEMANTIC_CLASSES[0], "label", "changed"),
    "class must be immutable",
)
check_raises(
    FrozenInstanceError,
    lambda: setattr(RELATION_TYPE_RULES[0], "truth_determined", True),
    "rule must be immutable",
)

# Repeated clean interpreter imports must produce the exact same digest.
command = (
    sys.executable,
    "-B",
    "-c",
    "from aiweb_language_core_bootstrap.controlled_concept_sense_registry.semantic_class_relation_registry import SEMANTIC_CLASS_RELATION_REGISTRY as r; print(r.registry_digest())",
)
digests = []
for _ in range(3):
    completed = subprocess.run(
        command,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env={**dict(__import__("os").environ), "PYTHONDONTWRITEBYTECODE": "1"},
    )
    check(completed.returncode == 0, f"repeat import failed: {completed.stderr}")
    digests.append(completed.stdout.strip())
check(len(set(digests)) == 1, "registry digest must be deterministic")
check(digests[0] == registry.registry_digest(), "subprocess digest must match")

print("AI.WEB SLICE 37E BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"semantic_class_count={len(CURRENT_SEMANTIC_CLASSES)}")
print(f"class_membership_count={len(MEMBERSHIPS)}")
print(f"relation_family_count={len(CURRENT_RELATION_FAMILIES)}")
print(f"relation_type_count={len(CURRENT_RELATION_TYPES)}")
print(f"inverse_declaration_count={len(INVERSE_DECLARATIONS)}")
print(f"relation_version_count={len(RELATION_VERSIONS)}")
print(f"relation_state_policy_count={len(RELATION_STATE_POLICIES)}")
print(f"prohibited_implication_count={len(PROHIBITED_IMPLICATIONS)}")
print(f"relation_instance_count=0")
print(f"registry_digest={registry.registry_digest()}")
print("class_membership_authority=0")
print("relation_fact_truth_evidence_status_implementation_authority=0")
print("occurrence_selection_candidate_meaning_structural_integration=0")
print("external_resources_routes_tools_memory_actions_rendering_delivery=0")
