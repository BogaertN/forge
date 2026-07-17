#!/usr/bin/env python3
"""Behavior and permanent authority-boundary test for Slice 38A."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from aiweb_language_core_bootstrap.predicate_role_frame_registry import (
    PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    SLICE38A_ACCEPTED_PARENT_HEAD,
    SLICE38A_ACCEPTED_PARENT_SUBJECT,
    SLICE38A_ACCEPTED_PARENT_TREE,
    SLICE38A_DEFERRED_SCOPE,
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
    PredicateResourceKind,
    build_slice38a_authority_profile,
    build_slice38a_schema_contract,
    validate_action_root_identity,
    validate_predicate_authority_profile,
    validate_predicate_identity,
    validate_predicate_namespace_identity,
    validate_predicate_provenance_reference,
    validate_predicate_registry_schema_contract,
    with_expected_predicate_resource_id,
)


checks = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


profile = build_slice38a_authority_profile()
contract = build_slice38a_schema_contract()

check(profile.profile_id == profile.expected_id(), "profile deterministic identity")
check(validate_predicate_authority_profile(profile).ok, "profile validates")
check(contract.contract_id == contract.expected_id(), "contract deterministic identity")
check(validate_predicate_registry_schema_contract(contract).ok, "contract validates")
check(SLICE38A_ACCEPTED_PARENT_HEAD == "f891a33487ea8bc811243627f1d834be7a43f972", "parent HEAD exact")
check(SLICE38A_ACCEPTED_PARENT_TREE == "f087c3f6cec8caecc19539628b1d4ab08b4918c1", "parent tree exact")
check(SLICE38A_ACCEPTED_PARENT_SUBJECT == "Slice 37G disabled integration and Slice 37 closeout", "parent subject exact")
check(len(PredicateResourceKind) == 6, "six schema resource kinds")
check(len(PredicateLifecycleState) == 16, "sixteen explicit lifecycle states")
check(len(PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES) == 24, "twenty-four permanent boundaries")
check(len(SLICE38A_DEFERRED_SCOPE) == 9, "nine deferred authorities")
check(tuple(PredicateResourceKind) == contract.resource_kinds, "resource kind order exact")
check(contract.registry_entry_count == 0, "zero total registry entries")
check(contract.namespace_entry_count == 0, "zero namespaces")
check(contract.action_root_entry_count == 0, "zero action roots")
check(contract.predicate_entry_count == 0, "zero predicate identities")
check(contract.action_root_schema_defined, "action-root schema defined")
check(contract.predicate_identity_schema_defined, "predicate schema defined")
check(contract.slice37_boundaries_preserved, "Slice 37 boundaries preserved")
check(not contract.slice37_runtime_superseded, "Slice 37 runtime not superseded")

required_true = (
    "disabled_by_default", "explicit_invocation_required", "offline_only",
    "standard_library_only", "deterministic", "immutable_records",
    "exact_version_required", "provenance_required", "lifecycle_state_required",
    "scope_non_scope_required", "unknown_state_first_class",
    "unresolved_state_first_class", "unsupported_state_first_class",
    "ambiguity_preserved", "action_authority_separated",
    "predicate_frame_dependency_required", "participant_role_dependency_required",
    "speech_act_separation_required", "effect_boundary_dependency_required",
    "capability_non_invocation_required", "scale_is_not_authority",
)
required_false = (
    "registry_population_installed", "action_root_lookup_allowed",
    "predicate_selection_allowed", "occurrence_interpretation_allowed",
    "participant_role_population_allowed", "role_assignment_allowed",
    "predicate_frame_population_allowed", "frame_completion_allowed",
    "capability_family_reference_population_allowed",
    "candidate_meaning_creation_allowed", "selected_meaning_allowed",
    "selected_predicate_allowed", "selected_frame_allowed",
    "evidence_validation_allowed", "memory_read_allowed", "memory_write_allowed",
    "external_resource_loading_allowed", "llm_allowed", "embedding_allowed",
    "vector_database_allowed", "semantic_similarity_allowed", "rag_allowed",
    "learned_parser_allowed", "neural_classifier_allowed", "api_route_allowed",
    "capability_route_allowed", "tool_activation_allowed", "action_execution_allowed",
    "outward_rendering_allowed", "delivery_authorization_allowed",
    "release_authorized", "production_ready",
)
for name in required_true:
    check(getattr(profile, name) is True, f"profile true {name}")
    check(not validate_predicate_authority_profile(replace(profile, **{name: False})).ok,
          f"profile rejects weakened boundary {name}")
for name in required_false:
    check(getattr(profile, name) is False, f"profile false {name}")
    check(not validate_predicate_authority_profile(replace(profile, **{name: True})).ok,
          f"profile rejects authority enlargement {name}")

for field in (
    "registry_population_installed", "action_root_lookup_installed",
    "predicate_selection_installed", "participant_role_schema_installed",
    "predicate_frame_schema_installed", "capability_reference_schema_installed",
    "source_occurrence_integration_installed", "selected_predicate_installed",
    "action_authority_installed", "slice37_runtime_superseded",
):
    check(getattr(contract, field) is False, f"contract false {field}")
    check(not validate_predicate_registry_schema_contract(replace(contract, **{field: True})).ok,
          f"contract rejects authority enlargement {field}")
for field in (
    "registry_entry_count", "namespace_entry_count",
    "action_root_entry_count", "predicate_entry_count",
):
    check(not validate_predicate_registry_schema_contract(replace(contract, **{field: 1})).ok,
          f"contract rejects population {field}")

provenance = with_expected_predicate_resource_id(
    PredicateProvenanceReference(
        provenance_id="",
        authority_document="Document 5",
        authority_section="Sections 12 through 22 schema-only synthetic test",
        source_kind="architecture_authority",
        source_reference="RMC Predicate-Role Frame Registry v1",
        version="v1",
        non_llm_provenance=True,
        external_resource_admitted=False,
        runtime_loaded=False,
        implementation_authorized=False,
        prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
namespace = with_expected_predicate_resource_id(
    PredicateNamespaceIdentity(
        namespace_id="",
        namespace_key="aiweb:predicate:schema_only",
        label="Synthetic predicate schema namespace",
        definition="A schema-validation namespace with no admitted runtime entries.",
        scope=("schema_identity", "schema_validation"),
        non_scope=("runtime_lookup", "action_execution"),
        version="v1",
        lifecycle_state=PredicateLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        permitted_uses=("schema_validation",),
        prohibited_uses=("runtime_selection", "capability_routing"),
        unknown_state_policy="Preserve unknown and unsupported action-like expressions without nearest-root substitution.",
        prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
action_root = with_expected_predicate_resource_id(
    ActionRootIdentity(
        action_root_id="",
        namespace_id=namespace.namespace_id,
        action_root_key="synthetic_action_root",
        preferred_label="Synthetic action root",
        definition="A schema-only action-root identity that is not admitted to a live registry.",
        scope=("identity_shape", "dependency_declaration"),
        non_scope=("surface_matching", "occurrence_selection", "execution"),
        version="v1",
        lifecycle_state=PredicateLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        concept_identity_refs=("controlled_concept:synthetic",),
        frame_dependency_required=True,
        participant_role_dependency_required=True,
        speech_act_separation_required=True,
        effect_boundary_dependency_required=True,
        capability_non_invocation_required=True,
        occurrence_selection_allowed=False,
        execution_authorized=False,
        unknown_state_policy="Unknown expressions remain unresolved and are not coerced to this root.",
        permitted_uses=("schema_validation", "identity_reference"),
        prohibited_uses=("command_detection", "tool_dispatch", "action_execution"),
        prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)
predicate = with_expected_predicate_resource_id(
    PredicateIdentity(
        predicate_id="",
        action_root_id=action_root.action_root_id,
        namespace_id=namespace.namespace_id,
        predicate_key="synthetic_predicate",
        preferred_label="Synthetic predicate identity",
        definition="A schema-only predicate identity with no occurrence-level selection.",
        scope=("predicate_identity_shape", "action_root_dependency"),
        non_scope=("participant_assignment", "frame_completion", "execution"),
        version="v1",
        lifecycle_state=PredicateLifecycleState.IMPLEMENTATION_DEFERRED,
        provenance_ref=provenance.provenance_id,
        concept_identity_refs=("controlled_concept:synthetic",),
        participant_role_schema_refs=(),
        predicate_frame_schema_refs=(),
        effect_boundary_refs=(),
        capability_family_reference_refs=(),
        participant_role_dependency_required=True,
        predicate_frame_dependency_required=True,
        speech_act_separation_required=True,
        capability_non_invocation_required=True,
        occurrence_selection_allowed=False,
        selected_for_occurrence=False,
        execution_authorized=False,
        unknown_state_policy="Unknown or unsupported predicate use remains visible and unselected.",
        permitted_uses=("schema_validation", "identity_reference"),
        prohibited_uses=("selected_interpretation", "route_binding", "execution"),
        prohibited_authorities=PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    )
)

for record, validator, label in (
    (provenance, validate_predicate_provenance_reference, "provenance"),
    (namespace, validate_predicate_namespace_identity, "namespace"),
    (action_root, validate_action_root_identity, "action root"),
    (predicate, validate_predicate_identity, "predicate"),
):
    check(validator(record).ok, f"{label} validates")
    try:
        setattr(record, next(iter(record.__dataclass_fields__)), "mutated")
    except (FrozenInstanceError, AttributeError):
        check(True, f"{label} immutable")
    else:
        check(False, f"{label} mutation rejected")

check(provenance.provenance_id == provenance.expected_id(), "provenance ID exact")
check(namespace.namespace_id == namespace.expected_id(), "namespace ID exact")
check(action_root.action_root_id == action_root.expected_id(), "action-root ID exact")
check(predicate.predicate_id == predicate.expected_id(), "predicate ID exact")
check(with_expected_predicate_resource_id(replace(action_root, action_root_id="")) == action_root,
      "action-root identity construction repeatable")
check(with_expected_predicate_resource_id(replace(predicate, predicate_id="")) == predicate,
      "predicate identity construction repeatable")
check(replace(action_root, preferred_label="Different label").expected_id() != action_root.action_root_id,
      "action-root identity changes with canonical body")
check(replace(predicate, definition="Different definition").expected_id() != predicate.predicate_id,
      "predicate identity changes with canonical body")

invalid_records = (
    (replace(provenance, external_resource_admitted=True), validate_predicate_provenance_reference,
     "external provenance admission rejected"),
    (replace(provenance, runtime_loaded=True), validate_predicate_provenance_reference,
     "runtime-loaded provenance rejected"),
    (replace(provenance, implementation_authorized=True), validate_predicate_provenance_reference,
     "implementation authority rejected"),
    (replace(namespace, version="1"), validate_predicate_namespace_identity,
     "invalid version rejected"),
    (replace(namespace, scope=("same",), non_scope=("same",)), validate_predicate_namespace_identity,
     "scope overlap rejected"),
    (replace(namespace, unknown_state_policy=""), validate_predicate_namespace_identity,
     "missing namespace unknown policy rejected"),
    (replace(action_root, frame_dependency_required=False), validate_action_root_identity,
     "action-root frame dependency required"),
    (replace(action_root, participant_role_dependency_required=False), validate_action_root_identity,
     "action-root role dependency required"),
    (replace(action_root, speech_act_separation_required=False), validate_action_root_identity,
     "action-root speech-act separation required"),
    (replace(action_root, effect_boundary_dependency_required=False), validate_action_root_identity,
     "action-root effect boundary required"),
    (replace(action_root, capability_non_invocation_required=False), validate_action_root_identity,
     "action-root capability non-invocation required"),
    (replace(action_root, occurrence_selection_allowed=True), validate_action_root_identity,
     "action-root occurrence selection rejected"),
    (replace(action_root, execution_authorized=True), validate_action_root_identity,
     "action-root execution rejected"),
    (replace(action_root, scope=("duplicate", "duplicate")), validate_action_root_identity,
     "duplicate scope rejected"),
    (replace(predicate, participant_role_dependency_required=False), validate_predicate_identity,
     "predicate role dependency required"),
    (replace(predicate, predicate_frame_dependency_required=False), validate_predicate_identity,
     "predicate frame dependency required"),
    (replace(predicate, speech_act_separation_required=False), validate_predicate_identity,
     "predicate speech-act separation required"),
    (replace(predicate, capability_non_invocation_required=False), validate_predicate_identity,
     "predicate capability non-invocation required"),
    (replace(predicate, occurrence_selection_allowed=True), validate_predicate_identity,
     "predicate occurrence selection rejected"),
    (replace(predicate, selected_for_occurrence=True), validate_predicate_identity,
     "selected predicate rejected"),
    (replace(predicate, execution_authorized=True), validate_predicate_identity,
     "predicate execution rejected"),
    (replace(predicate, non_scope=("predicate_identity_shape",)), validate_predicate_identity,
     "predicate scope overlap rejected"),
    (replace(predicate, unknown_state_policy=" "), validate_predicate_identity,
     "predicate missing unknown policy rejected"),
    (replace(predicate, prohibited_authorities=()), validate_predicate_identity,
     "predicate authority-boundary removal rejected"),
)
for bad, validator, label in invalid_records:
    check(not validator(bad).ok, label)

# Exact resource-kind and linkage boundaries.
check(action_root.resource_kind is PredicateResourceKind.ACTION_ROOT_IDENTITY,
      "action-root resource kind exact")
check(predicate.resource_kind is PredicateResourceKind.PREDICATE_IDENTITY,
      "predicate resource kind exact")
check(predicate.action_root_id == action_root.action_root_id,
      "predicate references action-root identity")
check(predicate.participant_role_schema_refs == (), "roles remain unpopulated")
check(predicate.predicate_frame_schema_refs == (), "frames remain unpopulated")
check(predicate.effect_boundary_refs == (), "effect references remain unpopulated")
check(predicate.capability_family_reference_refs == (), "capability references remain unpopulated")
check(not predicate.selected_for_occurrence, "predicate remains unselected")
check(not predicate.execution_authorized, "predicate has no execution authority")

# Source-surface inspection: standard library only, no route/action/file/network effects.
package_root = REPO / "aiweb_language_core_bootstrap" / "predicate_role_frame_registry"
source_files = tuple(sorted(package_root.glob("*.py")))
check(len(source_files) == 5, "exact five package source files")
prohibited_import_roots = {
    "anthropic", "chromadb", "faiss", "gensim", "httpx", "langchain",
    "llama_index", "nltk", "numpy", "openai", "pandas", "requests",
    "scipy", "sentence_transformers", "sklearn", "spacy", "tensorflow",
    "torch", "transformers", "urllib", "socket", "subprocess",
}
prohibited_calls = {
    "open", "eval", "exec", "compile", "__import__", "os.system", "os.popen",
    "subprocess.run", "subprocess.call", "subprocess.Popen", "Path.open",
    "Path.read_text", "Path.read_bytes", "Path.write_text", "Path.write_bytes",
    "Path.glob", "Path.rglob",
}
for path in source_files:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    imported_roots: set[str] = set()
    top_level_calls: list[str] = []
    public_functions: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported_roots.add(node.module.split(".", 1)[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            public_functions.append(node.name)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            top_level_calls.append(ast.unparse(node.value.func))
    check(not (imported_roots & prohibited_import_roots), f"no prohibited imports {path.name}")
    check(not top_level_calls, f"no top-level effect calls {path.name}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = ast.unparse(node.func)
            check(call_name not in prohibited_calls, f"no prohibited call {path.name}:{call_name}")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                rendered = ast.unparse(decorator).lower()
                check(not any(marker in rendered for marker in (".route", "@app.", "@router.", "fastapi", "flask")),
                      f"no route decorator {path.name}")
    for name in public_functions:
        lowered = name.lower()
        check(not any(fragment in lowered for fragment in (
            "lookup", "resolve", "select", "populate", "assign", "complete_frame",
            "route", "dispatch", "invoke", "execute", "render", "deliver",
        )), f"no authority-bearing public function {name}")

print("AI.WEB SLICE 38A BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"resource_kind_count={len(PredicateResourceKind)}")
print(f"lifecycle_state_count={len(PredicateLifecycleState)}")
print("registry_entry_count=0")
print("action_root_entry_count=0")
print("predicate_entry_count=0")
print("participant_role_entry_count=0")
print("predicate_frame_entry_count=0")
print("capability_reference_entry_count=0")
print("conventional_word_token_authority=0")
print("predicate_selection_role_assignment_frame_completion=0")
print("candidate_meaning_selected_meaning=0")
print("truth_evidence_permission=0")
print("memory_routes_tools_actions_rendering_delivery=0")
