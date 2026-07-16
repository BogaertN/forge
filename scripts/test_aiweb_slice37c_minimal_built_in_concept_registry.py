#!/usr/bin/env python3
"""Behavior tests for Slice 37C minimal built-in concept registry."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys


REPOSITORY = Path(__file__).resolve().parents[1]
if str(REPOSITORY) not in sys.path:
    sys.path.insert(0, str(REPOSITORY))

from aiweb_language_core_bootstrap.controlled_concept_sense_registry import (
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ControlledConceptIdentity,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.built_in_registry import (
    ADMITTED_CONCEPTS,
    ALL_AUTHORITIES,
    ALL_RESOURCES,
    ALL_TRANSITIONS,
    BUILT_IN_CONCEPT_DEFINITIONS,
    BUILT_IN_CONCEPT_KEYS,
    BUILT_IN_REGISTRY,
    CONCEPT_HISTORIES,
    CURRENT_NAMESPACE,
    GOVERNANCE_BATCH,
    NAMESPACE_HISTORY,
    PROVENANCE_RECORDS,
    SLICE37C_EXPECTED_CONCEPT_COUNT,
    SLICE37C_EXPECTED_NAMESPACE_COUNT,
    SLICE37C_NAMESPACE_KEY,
    SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256,
    all_admitted_concepts,
    assert_built_in_registry,
    built_in_registry,
    concept_by_id,
    concept_by_key,
    contains_concept_id,
    current_namespace,
    registry_digest,
    registry_manifest,
    validate_built_in_registry,
    validate_registry_manifest,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.built_in_registry.authority import (
    SLICE37C_ADDITIONAL_AUTHORITY_LIMITATIONS,
    SLICE37C_COMMON_PROHIBITED_USES,
    SLICE37C_PROHIBITED_AUTHORITIES,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.built_in_registry.schema import (
    BuiltInConceptRegistry,
    BuiltInRegistryValidationCode,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.governed_lifecycle import (
    ConceptGovernanceBatch,
    ConceptLifecycleTransitionKind,
    expected_resource_lineage_id,
    recompute_resource_id,
    validate_governance_batch,
)


checks: list[str] = []
failures: list[str] = []


def check(name: str, condition: bool) -> None:
    if condition:
        checks.append(name)
    else:
        failures.append(name)


def issue_codes(report) -> set[str]:
    return {item.code.value for item in report.issues}


registry = built_in_registry()
manifest = registry_manifest()
namespace = current_namespace()
concepts = all_admitted_concepts()

check("registry_singleton", registry is BUILT_IN_REGISTRY)
check("registry_accessor_repeat", built_in_registry() is registry)
check("manifest_singleton", manifest is registry.manifest)
check("namespace_singleton", namespace is CURRENT_NAMESPACE)
check("concept_tuple_singleton", concepts is ADMITTED_CONCEPTS)
check("registry_type_exact", type(registry) is BuiltInConceptRegistry)
check("registry_read_only_manifest", manifest.read_only is True)
check("registry_closed_manifest", manifest.closed_set is True)
check("registry_population_authorized", manifest.registry_population_authorized is True)
check("manifest_human_approved", manifest.human_approved is True)
check("manifest_id_exact", manifest.manifest_id == manifest.expected_id())
check("manifest_packet_hash", manifest.source_authority_packet_sha256 == SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256)
check("manifest_authority_limitations", manifest.authority_limitations == SLICE37C_ADDITIONAL_AUTHORITY_LIMITATIONS)
check("manifest_namespace_ref", manifest.namespace_ref == namespace.namespace_id)
check("manifest_concept_refs", manifest.concept_refs == tuple(item.concept_id for item in concepts))
check("manifest_concept_keys", manifest.concept_keys == BUILT_IN_CONCEPT_KEYS)
check("manifest_lineage_refs", manifest.concept_lineage_refs == tuple(expected_resource_lineage_id(item) for item in concepts))
check("registry_digest_repeat", registry_digest(registry) == registry_digest(registry))
check("registry_digest_prefix", registry_digest(registry).startswith("slice37c_built_in_concept_registry:"))

manifest_report = validate_registry_manifest(manifest)
registry_report = validate_built_in_registry(registry)
governance_report = validate_governance_batch(GOVERNANCE_BATCH)
check("manifest_validation_pass", manifest_report.ok)
check("registry_validation_pass", registry_report.ok)
check("governance_batch_validation_pass", governance_report.ok)
check("assert_registry_identity", assert_built_in_registry(registry) is registry)

check("namespace_count_constant", SLICE37C_EXPECTED_NAMESPACE_COUNT == 1)
check("concept_count_constant", SLICE37C_EXPECTED_CONCEPT_COUNT == 4)
check("concept_count", len(concepts) == 4)
check("definition_count", len(BUILT_IN_CONCEPT_DEFINITIONS) == 4)
check("key_count", len(BUILT_IN_CONCEPT_KEYS) == 4)
check("namespace_history_count", len(NAMESPACE_HISTORY) == 3)
check("concept_history_count", len(CONCEPT_HISTORIES) == 4)
check("provenance_count", len(PROVENANCE_RECORDS) == 5)
check("resource_count", len(ALL_RESOURCES) == 15)
check("authority_count", len(ALL_AUTHORITIES) == 10)
check("transition_count", len(ALL_TRANSITIONS) == 10)
check("batch_resource_count", len(GOVERNANCE_BATCH.resources) == 15)
check("batch_authority_count", len(GOVERNANCE_BATCH.authority_records) == 10)
check("batch_transition_count", len(GOVERNANCE_BATCH.transitions) == 10)
check("batch_provenance_count", len(GOVERNANCE_BATCH.provenance_records) == 5)

check("namespace_type", type(namespace) is ConceptNamespaceIdentity)
check("namespace_key", namespace.namespace_key == SLICE37C_NAMESPACE_KEY)
check("namespace_version", namespace.version == "v3")
check("namespace_lifecycle", namespace.lifecycle_state is ConceptLifecycleState.ARCHITECTURE_ADMITTED)
check("namespace_id_exact", namespace.namespace_id == recompute_resource_id(namespace))
check("namespace_scope_nonempty", bool(namespace.scope_tags))
check("namespace_permitted_nonempty", bool(namespace.permitted_uses))
check("namespace_prohibited_nonempty", bool(namespace.prohibited_uses))
check("namespace_authority_exact", namespace.prohibited_authorities == SLICE37C_PROHIBITED_AUTHORITIES)

check("namespace_history_states", tuple(item.lifecycle_state for item in NAMESPACE_HISTORY) == (
    ConceptLifecycleState.OBSERVED,
    ConceptLifecycleState.CANDIDATE,
    ConceptLifecycleState.ARCHITECTURE_ADMITTED,
))
check("namespace_history_versions", tuple(item.version for item in NAMESPACE_HISTORY) == ("v1", "v2", "v3"))
check("namespace_lineage_stable", len({expected_resource_lineage_id(item) for item in NAMESPACE_HISTORY}) == 1)
check("namespace_ids_distinct", len({item.namespace_id for item in NAMESPACE_HISTORY}) == 3)

expected_keys = (
    "forge_controlled_concept_identity",
    "source_expression_form",
    "concept_admission",
    "unknown_concept_condition",
)
check("exact_approved_keys", BUILT_IN_CONCEPT_KEYS == expected_keys)
check("concept_keys_order", tuple(item.concept_key for item in concepts) == expected_keys)
check("concept_ids_unique", len({item.concept_id for item in concepts}) == 4)
check("concept_lineages_unique", len({expected_resource_lineage_id(item) for item in concepts}) == 4)
check("concept_namespace_exact", all(item.namespace_id == namespace.namespace_id for item in concepts))
check("concept_types_exact", all(type(item) is ControlledConceptIdentity for item in concepts))
check("concept_versions_exact", all(item.version == "v3" for item in concepts))
check("concept_states_admitted", all(item.lifecycle_state is ConceptLifecycleState.ADMITTED for item in concepts))
check("concept_ids_recompute", all(item.concept_id == recompute_resource_id(item) for item in concepts))
check("concept_scope_nonempty", all(bool(item.scope_tags) for item in concepts))
check("concept_permitted_nonempty", all(bool(item.permitted_uses) for item in concepts))
check("concept_prohibited_nonempty", all(bool(item.prohibited_uses) for item in concepts))
check("concept_authority_exact", all(item.prohibited_authorities == SLICE37C_PROHIBITED_AUTHORITIES for item in concepts))
check("sense_refs_empty", all(item.sense_refs == () for item in concepts))
check("class_refs_empty", all(item.semantic_class_refs == () for item in concepts))
check("relation_refs_empty", all(item.relation_type_refs == () for item in concepts))

for index, (concept, definition, history) in enumerate(
    zip(concepts, BUILT_IN_CONCEPT_DEFINITIONS, CONCEPT_HISTORIES, strict=True)
):
    prefix = f"concept_{index}"
    check(prefix + "_key", concept.concept_key == definition.concept_key)
    check(prefix + "_label", concept.preferred_label == definition.preferred_label)
    check(prefix + "_definition", concept.definition == definition.definition)
    check(prefix + "_scope", concept.scope_tags == definition.scope_tags)
    check(prefix + "_permitted", concept.permitted_uses == definition.permitted_uses)
    check(prefix + "_prohibited", concept.prohibited_uses == definition.prohibited_uses)
    check(prefix + "_explicit_exclusions", len(definition.explicit_exclusions) >= 3)
    check(prefix + "_authority_document", definition.authority_document.startswith("Document 4"))
    check(prefix + "_authority_section", bool(definition.authority_section))
    check(prefix + "_source_reference", definition.source_reference.startswith("document4:"))
    check(prefix + "_history_length", len(history) == 3)
    check(prefix + "_history_states", tuple(item.lifecycle_state for item in history) == (
        ConceptLifecycleState.OBSERVED,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.ADMITTED,
    ))
    check(prefix + "_history_versions", tuple(item.version for item in history) == ("v1", "v2", "v3"))
    check(prefix + "_history_lineage", len({expected_resource_lineage_id(item) for item in history}) == 1)
    check(prefix + "_history_ids_unique", len({item.concept_id for item in history}) == 3)
    check(prefix + "_history_current", history[-1] is concept)
    check(prefix + "_lookup_id", concept_by_id(concept.concept_id) is concept)
    check(prefix + "_lookup_key", concept_by_key(namespace.namespace_id, concept.concept_key) is concept)
    check(prefix + "_contains", contains_concept_id(concept.concept_id))
    check(prefix + "_lookup_repeat_id", concept_by_id(concept.concept_id) is concept_by_id(concept.concept_id))
    check(prefix + "_lookup_repeat_key", concept_by_key(namespace.namespace_id, concept.concept_key) is concept_by_key(namespace.namespace_id, concept.concept_key))

check("unknown_id_not_contained", contains_concept_id("controlled_concept:not-present") is False)
check("nontext_id_not_contained", contains_concept_id(123) is False)

for invalid_id in (
    "",
    "forge_controlled_concept_identity",
    concepts[0].concept_id.upper(),
    concepts[0].concept_id + " ",
):
    try:
        concept_by_id(invalid_id)
    except KeyError:
        check(f"invalid_id_rejected_{repr(invalid_id)}", True)
    else:
        check(f"invalid_id_rejected_{repr(invalid_id)}", False)

for invalid_key in (
    "",
    "Forge_Controlled_Concept_Identity",
    "forge controlled concept identity",
    "forge_controlled_concept_identity ",
    "water",
):
    try:
        concept_by_key(namespace.namespace_id, invalid_key)
    except KeyError:
        check(f"invalid_key_rejected_{repr(invalid_key)}", True)
    else:
        check(f"invalid_key_rejected_{repr(invalid_key)}", False)

try:
    concept_by_id(1)
except TypeError:
    check("concept_by_id_type_rejected", True)
else:
    check("concept_by_id_type_rejected", False)

try:
    concept_by_key(1, expected_keys[0])
except TypeError:
    check("namespace_type_rejected", True)
else:
    check("namespace_type_rejected", False)

try:
    concept_by_key(namespace.namespace_id, 1)
except TypeError:
    check("concept_key_type_rejected", True)
else:
    check("concept_key_type_rejected", False)

# Frozen dataclasses reject mutation.
for name, target, field_name, value in (
    ("manifest_frozen", manifest, "read_only", False),
    ("registry_frozen", registry, "admitted_concepts", ()),
    ("namespace_frozen", namespace, "label", "changed"),
    ("concept_frozen", concepts[0], "definition", "changed"),
):
    try:
        setattr(target, field_name, value)
    except (FrozenInstanceError, AttributeError):
        check(name, True)
    else:
        check(name, False)

# Manifest boundary tampering must fail closed.
manifest_false_fields = (
    "read_only",
    "closed_set",
    "human_approved",
    "registry_population_authorized",
    "exact_identity_lookup_allowed",
    "exact_internal_key_lookup_allowed",
    "semantic_class_references_deferred_to_slice37e",
    "sense_references_deferred_to_slice37d",
    "relation_references_deferred_to_slice37e",
    "historical_slice8_preserved",
)
for field_name in manifest_false_fields:
    tampered = replace(manifest, **{field_name: False})
    report = validate_registry_manifest(tampered)
    check("tamper_false_" + field_name, not report.ok)

manifest_true_fields = (
    "surface_form_lookup_allowed",
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
    "historical_slice8_superseded",
)
for field_name in manifest_true_fields:
    tampered = replace(manifest, **{field_name: True})
    report = validate_registry_manifest(tampered)
    check("tamper_true_" + field_name, not report.ok)

for name, tampered in (
    ("manifest_bad_id", replace(manifest, manifest_id="bad")),
    ("manifest_bad_packet", replace(manifest, source_authority_packet_sha256="0" * 64)),
    ("manifest_bad_owner", replace(manifest, decision_owner_ref="other")),
    ("manifest_bad_approval", replace(manifest, human_approval_ref="other")),
    ("manifest_bad_keys", replace(manifest, concept_keys=tuple(reversed(manifest.concept_keys)))),
    ("manifest_duplicate_refs", replace(manifest, concept_refs=(manifest.concept_refs[0],) * 4)),
    ("manifest_bad_limits", replace(manifest, authority_limitations=())),
):
    check(name, not validate_registry_manifest(tampered).ok)

# Registry content tampering must fail closed.
tampered_concept_cases = (
    ("concept_definition", replace(concepts[0], definition="Changed definition")),
    ("concept_state", replace(concepts[0], lifecycle_state=ConceptLifecycleState.CANDIDATE)),
    ("concept_version", replace(concepts[0], version="v4")),
    ("concept_namespace", replace(concepts[0], namespace_id=NAMESPACE_HISTORY[0].namespace_id)),
    ("concept_scope", replace(concepts[0], scope_tags=("expanded:scope",))),
    ("concept_permitted", replace(concepts[0], permitted_uses=("anything",))),
    ("concept_prohibited", replace(concepts[0], prohibited_uses=())),
    ("concept_class_ref", replace(concepts[0], semantic_class_refs=("class:premature",))),
    ("concept_sense_ref", replace(concepts[0], sense_refs=("sense:premature",))),
    ("concept_relation_ref", replace(concepts[0], relation_type_refs=("relation:premature",))),
)
for name, altered in tampered_concept_cases:
    tampered_registry = replace(
        registry,
        admitted_concepts=(altered, *concepts[1:]),
    )
    check("tamper_" + name, not validate_built_in_registry(tampered_registry).ok)

duplicate_registry = replace(
    registry,
    admitted_concepts=(concepts[0], concepts[0], concepts[2], concepts[3]),
)
check("duplicate_concept_rejected", not validate_built_in_registry(duplicate_registry).ok)

short_registry = replace(
    registry,
    admitted_concepts=concepts[:-1],
)
check("short_registry_rejected", not validate_built_in_registry(short_registry).ok)

tampered_batch = replace(
    GOVERNANCE_BATCH,
    registry_population_installed=True,
)
tampered_batch = replace(
    tampered_batch,
    batch_id=tampered_batch.expected_id(),
)
check(
    "governance_population_claim_rejected",
    not validate_built_in_registry(
        replace(registry, governance_batch=tampered_batch)
    ).ok,
)

# Lifecycle history kinds are exact and human-approved.
check("transition_kind_counts", {
    kind: sum(1 for item in ALL_TRANSITIONS if item.transition_kind is kind)
    for kind in (
        ConceptLifecycleTransitionKind.OBSERVATION_REVIEW,
        ConceptLifecycleTransitionKind.ADMISSION,
        ConceptLifecycleTransitionKind.ARCHITECTURE_ADMISSION,
    )
} == {
    ConceptLifecycleTransitionKind.OBSERVATION_REVIEW: 5,
    ConceptLifecycleTransitionKind.ADMISSION: 4,
    ConceptLifecycleTransitionKind.ARCHITECTURE_ADMISSION: 1,
})
check("all_transition_prior_preserved", all(item.prior_record_preserved is True for item in ALL_TRANSITIONS))
check("no_automatic_transitions", all(item.automatic_transition is False for item in ALL_TRANSITIONS))
check("all_authorities_human_approved", all(item.human_approved is True for item in ALL_AUTHORITIES))
check("all_authorities_non_llm", all(item.non_llm_provenance is True for item in ALL_AUTHORITIES))
check("no_runtime_authority", all(item.runtime_authorized is False for item in ALL_AUTHORITIES))
check("no_implementation_authority", all(item.implementation_authorized is False for item in ALL_AUTHORITIES))
check("no_batch_registry_authority", all(item.registry_population_authorized is False for item in ALL_AUTHORITIES))
check("no_external_resource_decisions", all(item.external_resource_decision_ref is None for item in ALL_AUTHORITIES))
check("all_provenance_non_llm", all(item.non_llm_provenance is True for item in PROVENANCE_RECORDS))
check("no_external_resources_admitted", all(item.external_resource_admitted is False for item in PROVENANCE_RECORDS))
check("no_external_resources_loaded", all(item.runtime_loaded is False for item in PROVENANCE_RECORDS))

if failures:
    print("AI.WEB SLICE 37C BEHAVIOR TEST: FAIL")
    print(f"check_count={len(checks) + len(failures)}")
    print(f"failure_count={len(failures)}")
    for failure in failures:
        print(f"- {failure}")
    raise SystemExit(1)

print("AI.WEB SLICE 37C BEHAVIOR TEST: PASS")
print(f"check_count={len(checks)}")
print(f"concept_count={len(concepts)}")
print(f"namespace_count={SLICE37C_EXPECTED_NAMESPACE_COUNT}")
print(f"governed_resource_versions={len(ALL_RESOURCES)}")
print(f"lifecycle_transitions={len(ALL_TRANSITIONS)}")
print(f"registry_digest={registry_digest(registry)}")
print("surface_lookup_installed=0")
print("term_mapping_installed=0")
print("sense_population_installed=0")
print("semantic_class_population_installed=0")
print("semantic_relation_population_installed=0")
print("structural_integration_installed=0")
print("runtime_routes_tools_memory_actions_rendering_delivery=0")
