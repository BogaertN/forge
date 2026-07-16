#!/usr/bin/env python3
"""Behavior and authority-boundary test for Slice 37A."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


from aiweb_concept_boundary_scaffold import (
    concept_scope_record as historical_concept_scope_record,
    relation_scope_record as historical_relation_scope_record,
)

from aiweb_language_core_bootstrap.controlled_concept_sense_registry import (
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    HISTORICAL_SLICE8_COMMIT,
    SLICE37A_ACCEPTED_PARENT_HEAD,
    SLICE37A_DEFERRED_SCOPE,
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
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
    build_slice37a_authority_profile,
    build_slice37a_schema_contract,
    validate_concept_authority_profile,
    validate_concept_namespace_identity,
    validate_concept_provenance_reference,
    validate_concept_registry_schema_contract,
    validate_controlled_concept_identity,
    validate_controlled_lexical_reference,
    validate_controlled_sense_identity,
    validate_semantic_class_identity,
    validate_semantic_relation_family_identity,
    validate_semantic_relation_type_identity,
    validate_term_concept_mapping_identity,
    with_expected_resource_id,
)

checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


profile = build_slice37a_authority_profile()
contract = build_slice37a_schema_contract()

check(profile.profile_id == profile.expected_id(), "profile deterministic identity")
check(validate_concept_authority_profile(profile).ok, "profile validates")
check(contract.contract_id == contract.expected_id(), "contract deterministic identity")
check(validate_concept_registry_schema_contract(contract).ok, "contract validates")
check(contract.registry_entry_count == 0, "registry contains zero entries")
check(contract.concept_entry_count == 0, "zero concepts")
check(contract.sense_entry_count == 0, "zero senses")
check(contract.lexical_reference_entry_count == 0, "zero lexical references")
check(contract.term_mapping_entry_count == 0, "zero term mappings")
check(contract.semantic_class_entry_count == 0, "zero semantic classes")
check(contract.relation_family_entry_count == 0, "zero relation families")
check(contract.relation_type_entry_count == 0, "zero relation types")
check(contract.historical_slice8_preserved, "Slice 8 preserved")
check(not contract.historical_slice8_superseded, "Slice 8 not superseded")
check(HISTORICAL_SLICE8_COMMIT == "f55c3ff076cbb7e30344a82f51707fbd3997130c", "Slice 8 commit exact")
historical_concept_scope = historical_concept_scope_record()
historical_relation_scope = historical_relation_scope_record()
check(historical_concept_scope["scaffold_only"] is True, "historical Slice 8 concept scope remains scaffold-only")
check(historical_relation_scope["scaffold_only"] is True, "historical Slice 8 relation scope remains scaffold-only")
check(historical_concept_scope["runtime_effect"] == "none", "historical Slice 8 concept runtime remains none")
check(historical_relation_scope["runtime_effect"] == "none", "historical Slice 8 relation runtime remains none")
check(SLICE37A_ACCEPTED_PARENT_HEAD == "5bd8a39b91e7ead06523e7fd0aa3ee057c795f74", "parent head exact")
check(len(ConceptResourceKind) == 11, "eleven schema resource kinds")
check(len(ConceptLifecycleState) == 15, "fifteen explicit lifecycle states")
check(len(CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES) == 17, "seventeen permanent non-authority rules")
check(len(SLICE37A_DEFERRED_SCOPE) == 9, "nine exact deferred authorities")
check(tuple(ConceptResourceKind) == contract.resource_kinds, "resource kind order exact")

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
    "structural_result_consumption_allowed", "candidate_meaning_creation_allowed",
    "selected_meaning_allowed", "predicate_authority_allowed",
    "participant_role_authority_allowed", "evidence_validation_allowed",
    "memory_read_allowed", "memory_write_allowed",
    "external_resource_loading_allowed", "llm_allowed", "embedding_allowed",
    "vector_database_allowed", "semantic_similarity_allowed", "rag_allowed",
    "learned_parser_allowed", "neural_classifier_allowed", "api_route_allowed",
    "capability_route_allowed", "tool_activation_allowed",
    "action_execution_allowed", "outward_rendering_allowed",
    "delivery_authorization_allowed", "release_authorized", "production_ready",
)
for name in required_true:
    check(getattr(profile, name) is True, f"profile true {name}")
for name in required_false:
    check(getattr(profile, name) is False, f"profile false {name}")
    check(
        not validate_concept_authority_profile(replace(profile, **{name: True})).ok,
        f"profile rejects authority enlargement {name}",
    )

check(
    not validate_concept_registry_schema_contract(
        replace(contract, concept_entry_count=1)
    ).ok,
    "contract rejects concept population",
)
check(
    not validate_concept_registry_schema_contract(
        replace(contract, lookup_installed=True)
    ).ok,
    "contract rejects lookup installation",
)
check(
    not validate_concept_registry_schema_contract(
        replace(contract, historical_slice8_superseded=True)
    ).ok,
    "contract rejects Slice 8 supersession",
)

provenance = with_expected_resource_id(
    ConceptProvenanceReference(
        provenance_id="",
        authority_document="Document 4",
        authority_section="schema-only synthetic test",
        source_kind="architecture_authority",
        source_reference="RMC Concept Lexicon and Semantic Relation Graph v1",
        version="v1",
        non_llm_provenance=True,
        external_resource_admitted=False,
        runtime_loaded=False,
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
namespace = with_expected_resource_id(
    ConceptNamespaceIdentity(
        namespace_id="",
        namespace_key="aiweb:test:schema_only",
        label="Synthetic schema-only namespace",
        definition="A non-populated schema test namespace.",
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        scope_tags=("synthetic_test",),
        permitted_uses=("schema_validation",),
        prohibited_uses=("runtime_lookup",),
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
semantic_class = with_expected_resource_id(
    SemanticClassIdentity(
        semantic_class_id="",
        namespace_id=namespace.namespace_id,
        class_key="synthetic_class",
        label="Synthetic class",
        definition="A schema test class with no admitted membership.",
        parent_class_refs=(),
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
relation_family = with_expected_resource_id(
    SemanticRelationFamilyIdentity(
        relation_family_id="",
        namespace_id=namespace.namespace_id,
        family_key="synthetic_relation_family",
        label="Synthetic relation family",
        definition="A schema test family with no relation edges.",
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
relation_type = with_expected_resource_id(
    SemanticRelationTypeIdentity(
        relation_type_id="",
        relation_family_id=relation_family.relation_family_id,
        namespace_id=namespace.namespace_id,
        relation_key="synthetic_relation_type",
        label="Synthetic relation type",
        definition="A schema test relation type with no instances.",
        direction=RelationDirection.DIRECTED,
        domain_class_refs=(semantic_class.semantic_class_id,),
        range_class_refs=(semantic_class.semantic_class_id,),
        inverse_relation_type_ref=None,
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        relation_instances_populated=False,
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
concept = with_expected_resource_id(
    ControlledConceptIdentity(
        concept_id="",
        namespace_id=namespace.namespace_id,
        concept_key="synthetic_concept",
        preferred_label="Synthetic concept",
        definition="A schema-only concept identity not admitted to a registry.",
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        semantic_class_refs=(semantic_class.semantic_class_id,),
        sense_refs=(),
        relation_type_refs=(relation_type.relation_type_id,),
        scope_tags=("synthetic_test",),
        permitted_uses=("schema_validation",),
        prohibited_uses=("occurrence_interpretation",),
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
lexical_reference = with_expected_resource_id(
    ControlledLexicalReference(
        lexical_reference_id="",
        namespace_id=namespace.namespace_id,
        exact_form="synthetic term",
        reference_kind=LexicalReferenceKind.USER_DEFINED_BOUNDED_EXPRESSION,
        language_tag="en",
        case_sensitive=True,
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        scope_tags=("synthetic_test",),
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
sense = with_expected_resource_id(
    ControlledSenseIdentity(
        sense_id="",
        concept_id=concept.concept_id,
        namespace_id=namespace.namespace_id,
        sense_key="synthetic_sense",
        definition="A materially distinct synthetic schema sense.",
        differentiation_basis=("schema test distinction",),
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        lexical_reference_refs=(lexical_reference.lexical_reference_id,),
        scope_tags=("synthetic_test",),
        permitted_uses=("schema_validation",),
        prohibited_uses=("sense_selection",),
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
mapping = with_expected_resource_id(
    TermConceptMappingIdentity(
        mapping_id="",
        lexical_reference_id=lexical_reference.lexical_reference_id,
        namespace_scope=(namespace.namespace_id,),
        domain_scope=("synthetic_test",),
        concept_candidate_refs=(concept.concept_id,),
        sense_candidate_refs=(sense.sense_id,),
        version="v1",
        lifecycle_state=ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        occurrence_interpretation_selected=False,
        selected_concept_ref=None,
        selected_sense_ref=None,
        prohibited_authorities=CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)

records_and_validators = (
    (provenance, validate_concept_provenance_reference),
    (namespace, validate_concept_namespace_identity),
    (semantic_class, validate_semantic_class_identity),
    (relation_family, validate_semantic_relation_family_identity),
    (relation_type, validate_semantic_relation_type_identity),
    (concept, validate_controlled_concept_identity),
    (lexical_reference, validate_controlled_lexical_reference),
    (sense, validate_controlled_sense_identity),
    (mapping, validate_term_concept_mapping_identity),
)
for record, validator in records_and_validators:
    check(validator(record).ok, f"{type(record).__name__} validates")
    check(record.expected_id() in record.to_dict().values(), f"{type(record).__name__} identity preserved")

check(
    not validate_term_concept_mapping_identity(
        replace(mapping, occurrence_interpretation_selected=True)
    ).ok,
    "mapping cannot select occurrence interpretation",
)
check(
    not validate_term_concept_mapping_identity(
        replace(mapping, selected_sense_ref=sense.sense_id)
    ).ok,
    "mapping cannot carry selected sense",
)
check(
    not validate_semantic_relation_type_identity(
        replace(relation_type, relation_instances_populated=True)
    ).ok,
    "relation type cannot populate relation instances",
)
check(
    not validate_controlled_concept_identity(
        replace(concept, preferred_label=" altered")
    ).ok,
    "untrimmed concept label rejected",
)
check(
    not validate_controlled_lexical_reference(
        replace(lexical_reference, language_tag="not a tag")
    ).ok,
    "invalid language tag rejected",
)

try:
    profile.disabled_by_default = False  # type: ignore[misc]
except FrozenInstanceError:
    check(True, "profile frozen")
else:
    check(False, "profile mutable")

try:
    concept.definition = "changed"  # type: ignore[misc]
except FrozenInstanceError:
    check(True, "concept record frozen")
else:
    check(False, "concept record mutable")

package_root = REPO / "aiweb_language_core_bootstrap" / "controlled_concept_sense_registry"
prohibited_imports = {
    "rmc_engine_v1", "openai", "anthropic", "ollama", "chromadb",
    "langchain", "transformers", "torch", "tensorflow", "sklearn",
    "spacy", "nltk", "gensim", "sentence_transformers", "faiss",
    "qdrant", "pinecone", "weaviate", "requests", "httpx", "aiohttp",
    "socket", "urllib", "subprocess",
}
prohibited_calls = {
    "open", "eval", "exec", "compile", "__import__", "os.system",
    "os.popen", "subprocess.run", "subprocess.call", "subprocess.Popen",
    "Path.read_text", "Path.read_bytes", "Path.write_text",
    "Path.write_bytes", "Path.open", "Path.glob", "Path.rglob",
}
for source_path in sorted(package_root.glob("*.py")):
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                check(alias.name.split(".")[0] not in prohibited_imports, f"no prohibited import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            check(module.split(".")[0] not in prohibited_imports, f"no prohibited import {module}")
        elif isinstance(node, ast.Call):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            call_name = ".".join(reversed(parts))
            check(call_name not in prohibited_calls, f"no prohibited runtime call {call_name}")

public_names = set(__import__(
    "aiweb_language_core_bootstrap.controlled_concept_sense_registry",
    fromlist=["__all__"],
).__all__)
for forbidden_name_fragment in ("lookup", "resolve", "select", "populate", "traverse", "render", "route", "execute"):
    check(
        not any(forbidden_name_fragment in name.lower() for name in public_names),
        f"public surface contains no {forbidden_name_fragment} authority function",
    )

print("AI.WEB SLICE 37A CONTROLLED CONCEPT-AUTHORITY SCHEMA TEST")
print(f"checks={checks}")
print(f"resource_record_kinds={len(ConceptResourceKind)}")
print(f"lifecycle_states={len(ConceptLifecycleState)}")
print(f"schema_contract_registry_entries={contract.registry_entry_count}")
print("concept_lookup_functions=0")
print("selected_sense_authority=0")
print("external_resources_loaded=0")
print("routes_tools_actions_renderings_deliveries=0")
print("SLICE 37A BEHAVIOR TEST: PASS")
