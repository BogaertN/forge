#!/usr/bin/env python3
"""Visible behavior test for Slice 38C minimal built-in action-root registry."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
import sys
from typing import Any

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from aiweb_language_core_bootstrap.predicate_role_frame_registry import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.built_in_action_root_registry import (
    ACTION_ROOT_HISTORIES,
    ADMITTED_ACTION_ROOTS,
    ADMITTED_PREDICATES,
    ALL_AUTHORITIES,
    ALL_RESOURCES,
    ALL_TRANSITIONS,
    BUILT_IN_ACTION_ROOT_DEFINITIONS,
    BUILT_IN_ACTION_ROOT_KEYS,
    BUILT_IN_ACTION_ROOT_REGISTRY,
    BUILT_IN_PREDICATE_KEYS,
    CURRENT_NAMESPACE,
    GOVERNANCE_BATCH,
    NAMESPACE_HISTORY,
    PREDICATE_HISTORIES,
    PROVENANCE_RECORDS,
    SLICE38C_ACCEPTED_PARENT_HEAD,
    SLICE38C_ACCEPTED_PARENT_SUBJECT,
    SLICE38C_ACCEPTED_PARENT_TREE,
    SLICE38C_ADDITIONAL_AUTHORITY_LIMITATIONS,
    SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES,
    SLICE38C_EXPECTED_ACTION_ROOT_COUNT,
    SLICE38C_EXPECTED_NAMESPACE_COUNT,
    SLICE38C_EXPECTED_PREDICATE_COUNT,
    SLICE38C_SOURCE_AUTHORITY_PACKET_SHA256,
    action_root_by_id,
    action_root_by_key,
    all_admitted_action_roots,
    all_admitted_predicates,
    assert_built_in_action_root_registry,
    built_in_action_root_registry,
    contains_action_root_id,
    contains_predicate_id,
    predicate_by_id,
    predicate_by_key,
    predicate_for_action_root_id,
    registry_digest,
    registry_manifest,
    validate_built_in_action_root_registry,
    validate_registry_manifest,
)
from aiweb_language_core_bootstrap.predicate_role_frame_registry.governed_lifecycle import (
    PREDICATE_LIFECYCLE_TRANSITION_RULES,
    expected_resource_lineage_id,
    validate_governance_batch,
)

checks = 0
malformed_cases = 0


def check(condition: object, label: str) -> None:
    global checks
    checks += 1
    if condition is not True:
        raise AssertionError(label)


def expect_exception(expected: type[BaseException], function: Any, label: str) -> None:
    try:
        function()
    except expected:
        check(True, label)
    else:
        check(False, label)


def check_rejected_without_exception(record: object, label: str) -> None:
    global malformed_cases
    malformed_cases += 1
    try:
        report = validate_built_in_action_root_registry(record)
    except Exception as error:
        raise AssertionError(
            f"{label}: validator escaped with {type(error).__name__}: {error}"
        ) from error
    check(report.ok is False, label)


def check_manifest_rejected_without_exception(record: object, label: str) -> None:
    global malformed_cases
    malformed_cases += 1
    try:
        report = validate_registry_manifest(record)
    except Exception as error:
        raise AssertionError(
            f"{label}: manifest validator escaped with {type(error).__name__}: {error}"
        ) from error
    check(report.ok is False, label)


registry = built_in_action_root_registry()
manifest = registry_manifest()

check(registry is BUILT_IN_ACTION_ROOT_REGISTRY, "registry singleton exact")
check(registry is built_in_action_root_registry(), "registry repeatable")
check(registry.manifest is manifest, "manifest singleton exact")
check(manifest.manifest_id == manifest.expected_id(), "manifest identity exact")
check(registry_digest(registry) == registry.registry_digest(), "registry digest exact")
check(registry_digest(registry) == registry_digest(registry), "registry digest deterministic")
check(validate_registry_manifest(manifest).ok, "manifest validates")
check(validate_built_in_action_root_registry(registry).ok, "registry validates")
check(assert_built_in_action_root_registry(registry) is registry, "assert returns exact registry")

check(SLICE38C_ACCEPTED_PARENT_HEAD == "c502b74ada70ed0bc551fb591c49fd119191f52f", "parent HEAD exact")
check(SLICE38C_ACCEPTED_PARENT_TREE == "77d349f51a617eab98d1fddeef7ba9e57f52dec6", "parent tree exact")
check(SLICE38C_ACCEPTED_PARENT_SUBJECT == "Slice 38B deterministic validation identity versioning lifecycle", "parent subject exact")
check(SLICE38C_SOURCE_AUTHORITY_PACKET_SHA256 == "1e9d44dfbe256f2438baa24357b65741462b294b0ef120021a0cd73e8a59ee3e", "source packet exact")
check(SLICE38C_EXPECTED_NAMESPACE_COUNT == 1, "one namespace")
check(SLICE38C_EXPECTED_ACTION_ROOT_COUNT == 5, "five roots")
check(SLICE38C_EXPECTED_PREDICATE_COUNT == 5, "five predicates")
check(BUILT_IN_ACTION_ROOT_KEYS == ("inspect", "report", "request", "verify", "simulate"), "closed root set exact")
check(BUILT_IN_PREDICATE_KEYS == BUILT_IN_ACTION_ROOT_KEYS, "predicate keys one-to-one")
check(SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES == ("approve", "install", "send", "remember", "rollback"), "higher consequence set deferred")
check(len(SLICE38C_ADDITIONAL_AUTHORITY_LIMITATIONS) == 11, "authority limitations exact count")

check(len(PROVENANCE_RECORDS) == 6, "six provenance records")
check(len(NAMESPACE_HISTORY) == 4, "four namespace versions")
check(len(ACTION_ROOT_HISTORIES) == 5, "five action-root histories")
check(len(PREDICATE_HISTORIES) == 5, "five predicate histories")
check(len(ALL_RESOURCES) == 44, "forty-four governed resource versions")
check(len(ALL_AUTHORITIES) == 33, "thirty-three authority records")
check(len(ALL_TRANSITIONS) == 33, "thirty-three transitions")
check(len(PREDICATE_LIFECYCLE_TRANSITION_RULES) == 51, "fifty-one inherited transition rules")
check(validate_governance_batch(GOVERNANCE_BATCH).ok, "governance batch validates")
check(GOVERNANCE_BATCH.registry_population_installed is False, "governance batch population false")
check(GOVERNANCE_BATCH.action_root_lookup_installed is False, "governance batch lookup false")
check(GOVERNANCE_BATCH.predicate_selection_installed is False, "governance batch selection false")
check(GOVERNANCE_BATCH.nearest_known_mapping_installed is False, "governance batch nearest mapping false")
check(GOVERNANCE_BATCH.semantic_similarity_installed is False, "governance batch similarity false")
check(GOVERNANCE_BATCH.capability_routing_installed is False, "governance batch routing false")
check(GOVERNANCE_BATCH.runtime_activation_installed is False, "governance batch runtime false")

expected_history_states = (
    PredicateLifecycleState.OBSERVED,
    PredicateLifecycleState.CANDIDATE,
    PredicateLifecycleState.REVIEWED,
    PredicateLifecycleState.ADMITTED,
)
check(tuple(item.lifecycle_state for item in NAMESPACE_HISTORY) == (
    PredicateLifecycleState.OBSERVED,
    PredicateLifecycleState.CANDIDATE,
    PredicateLifecycleState.REVIEWED,
    PredicateLifecycleState.ARCHITECTURE_ADMITTED,
), "namespace lifecycle exact")
for index, history in enumerate(ACTION_ROOT_HISTORIES):
    check(tuple(item.lifecycle_state for item in history) == expected_history_states, f"root history states {index}")
    check(len({expected_resource_lineage_id(item) for item in history}) == 1, f"root lineage stable {index}")
    check(tuple(item.version for item in history) == ("v1.0.0", "v1.1.0", "v1.2.0", "v1.3.0"), f"root versions exact {index}")
for index, history in enumerate(PREDICATE_HISTORIES):
    check(tuple(item.lifecycle_state for item in history) == expected_history_states, f"predicate history states {index}")
    check(len({expected_resource_lineage_id(item) for item in history}) == 1, f"predicate lineage stable {index}")
    check(tuple(item.version for item in history) == ("v1.0.0", "v1.1.0", "v1.2.0", "v1.3.0"), f"predicate versions exact {index}")

roots = all_admitted_action_roots()
predicates = all_admitted_predicates()
check(roots == ADMITTED_ACTION_ROOTS, "root tuple exact")
check(predicates == ADMITTED_PREDICATES, "predicate tuple exact")
check(tuple(record.action_root_key for record in roots) == BUILT_IN_ACTION_ROOT_KEYS, "root order exact")
check(tuple(record.predicate_key for record in predicates) == BUILT_IN_PREDICATE_KEYS, "predicate order exact")
check(len({record.action_root_id for record in roots}) == 5, "root IDs unique")
check(len({record.predicate_id for record in predicates}) == 5, "predicate IDs unique")
check(len({expected_resource_lineage_id(record) for record in roots}) == 5, "root lineages unique")
check(len({expected_resource_lineage_id(record) for record in predicates}) == 5, "predicate lineages unique")

for definition, root, predicate in zip(BUILT_IN_ACTION_ROOT_DEFINITIONS, roots, predicates, strict=True):
    key = definition.action_root_key
    check(type(root) is ActionRootIdentity, f"exact root type {key}")
    check(type(predicate) is PredicateIdentity, f"exact predicate type {key}")
    check(root.action_root_id == root.expected_id(), f"root ID canonical {key}")
    check(predicate.predicate_id == predicate.expected_id(), f"predicate ID canonical {key}")
    check(root.namespace_id == CURRENT_NAMESPACE.namespace_id, f"root namespace {key}")
    check(predicate.namespace_id == CURRENT_NAMESPACE.namespace_id, f"predicate namespace {key}")
    check(predicate.action_root_id == root.action_root_id, f"predicate root link {key}")
    check(root.lifecycle_state is PredicateLifecycleState.ADMITTED, f"root admitted {key}")
    check(predicate.lifecycle_state is PredicateLifecycleState.ADMITTED, f"predicate admitted {key}")
    check(root.concept_identity_refs == (), f"root concept refs deferred {key}")
    check(predicate.concept_identity_refs == (), f"predicate concept refs deferred {key}")
    check(predicate.participant_role_schema_refs == (), f"roles deferred {key}")
    check(predicate.predicate_frame_schema_refs == (), f"frames deferred {key}")
    check(predicate.effect_boundary_refs == (), f"effects deferred {key}")
    check(predicate.capability_family_reference_refs == (), f"capabilities deferred {key}")
    check(root.occurrence_selection_allowed is False, f"root unselected {key}")
    check(predicate.occurrence_selection_allowed is False, f"predicate occurrence selection false {key}")
    check(predicate.selected_for_occurrence is False, f"predicate unselected {key}")
    check(root.execution_authorized is False, f"root execution false {key}")
    check(predicate.execution_authorized is False, f"predicate execution false {key}")
    check(action_root_by_id(root.action_root_id) is root, f"root exact ID retrieval {key}")
    check(action_root_by_key(CURRENT_NAMESPACE.namespace_id, key) is root, f"root exact key retrieval {key}")
    check(predicate_by_id(predicate.predicate_id) is predicate, f"predicate exact ID retrieval {key}")
    check(predicate_by_key(CURRENT_NAMESPACE.namespace_id, key) is predicate, f"predicate exact key retrieval {key}")
    check(predicate_for_action_root_id(root.action_root_id) is predicate, f"one-to-one link retrieval {key}")
    check(contains_action_root_id(root.action_root_id), f"contains root {key}")
    check(contains_predicate_id(predicate.predicate_id), f"contains predicate {key}")
    try:
        root.preferred_label = "mutated"  # type: ignore[misc]
    except (FrozenInstanceError, AttributeError):
        check(True, f"root immutable {key}")
    else:
        check(False, f"root mutation refused {key}")

for unknown in (
    "approve", "install", "send", "remember", "rollback", "summarize",
    "draft", "delete", "Inspect", " inspect", "inspect ", "INSPECT",
    "check", "review", "verify_status", "simulate-live", "",
):
    expect_exception(KeyError, lambda value=unknown: action_root_by_key(CURRENT_NAMESPACE.namespace_id, value), f"unknown root fails closed {unknown!r}")
    expect_exception(KeyError, lambda value=unknown: predicate_by_key(CURRENT_NAMESPACE.namespace_id, value), f"unknown predicate fails closed {unknown!r}")
check(contains_action_root_id(object()) is False, "non-string root containment false")
check(contains_predicate_id(object()) is False, "non-string predicate containment false")
for function, arguments, label in (
    (action_root_by_id, (object(),), "root ID exact str required"),
    (action_root_by_key, (object(), "inspect"), "root namespace exact str required"),
    (action_root_by_key, (CURRENT_NAMESPACE.namespace_id, object()), "root key exact str required"),
    (predicate_by_id, (object(),), "predicate ID exact str required"),
    (predicate_by_key, (object(), "inspect"), "predicate namespace exact str required"),
    (predicate_by_key, (CURRENT_NAMESPACE.namespace_id, object()), "predicate key exact str required"),
    (predicate_for_action_root_id, (object(),), "predicate link exact str required"),
):
    expect_exception(TypeError, lambda fn=function, args=arguments: fn(*args), label)

# Manifest authority fields must fail closed when enlarged or weakened.
for field_name in (
    "human_approved", "registry_population_authorized", "read_only", "closed_set",
    "exact_identity_lookup_allowed", "exact_internal_key_lookup_allowed",
    "exact_action_root_to_predicate_link_allowed",
    "participant_roles_deferred_to_slice38d", "predicate_frames_deferred_to_slice38e",
    "effect_and_capability_references_deferred_to_slice38f",
    "occurrence_candidate_proposal_deferred_to_slice38g",
    "disabled_integration_deferred_to_slice38h", "slice38a_preserved", "slice38b_preserved",
):
    check(not validate_registry_manifest(replace(manifest, **{field_name: False})).ok,
          f"manifest required true {field_name}")
for field_name in (
    "surface_form_lookup_allowed", "surface_normalization_allowed",
    "occurrence_interpretation_installed", "predicate_selection_installed",
    "nearest_known_mapping_installed", "semantic_similarity_installed",
    "concept_to_predicate_conversion_installed", "participant_role_population_installed",
    "role_assignment_installed", "predicate_frame_population_installed",
    "frame_completion_installed", "effect_boundary_population_installed",
    "capability_reference_population_installed", "capability_routing_installed",
    "route_registration_installed", "tool_activation_installed", "action_execution_installed",
    "evidence_validation_installed", "memory_access_installed", "rendering_installed",
    "delivery_installed", "external_resource_loading_installed", "llm_authority_installed",
    "slice38a_superseded", "slice38b_superseded",
):
    check(not validate_registry_manifest(replace(manifest, **{field_name: True})).ok,
          f"manifest authority false {field_name}")

# Malformed manifest fields and nested registry values may never escape as exceptions.
malformed_values: tuple[object, ...] = (
    None, object(), [], {}, set(), 0, 1, True, False, "", " ", ("duplicate", "duplicate"),
)
for field_info in fields(manifest):
    if field_info.name in {"manifest_id", "schema_version", "spec_id", "spec_version"}:
        continue
    for malformed in malformed_values:
        current = getattr(manifest, field_info.name)
        try:
            if type(current) is type(malformed) and current == malformed:
                continue
        except Exception:
            pass
        try:
            bad_manifest = replace(manifest, **{field_info.name: malformed})
            bad_registry = replace(registry, manifest=bad_manifest)
        except Exception:
            continue
        check_manifest_rejected_without_exception(bad_manifest, f"malformed manifest {field_info.name}:{type(malformed).__name__}")

for field_name, malformed in (
    ("admitted_action_roots", []),
    ("admitted_action_roots", (object(),)),
    ("admitted_predicates", []),
    ("admitted_predicates", (object(),)),
    ("current_namespace", object()),
    ("governance_batch", object()),
):
    check_rejected_without_exception(
        replace(registry, **{field_name: malformed}),
        f"malformed registry field {field_name}",
    )

first_root = roots[0]
first_predicate = predicates[0]
for field_name, malformed in (
    ("action_root_key", "Inspect"),
    ("action_root_key", "approve"),
    ("namespace_id", "wrong"),
    ("lifecycle_state", PredicateLifecycleState.CANDIDATE),
    ("concept_identity_refs", ("unauthorized",)),
    ("occurrence_selection_allowed", True),
    ("execution_authorized", True),
    ("permitted_uses", first_root.permitted_uses + ("new authority",)),
    ("prohibited_uses", ()),
):
    bad_root = replace(first_root, **{field_name: malformed})
    check_rejected_without_exception(
        replace(registry, admitted_action_roots=(bad_root, *roots[1:])),
        f"mutated root rejected {field_name}",
    )
# Public registry validation must be total and fail closed for malformed nested
# identity fields that would otherwise reach hashing, mapping, canonicalization,
# enum access, or equality operations.
for field_name, malformed in (
    ("action_root_id", []),
    ("action_root_id", {}),
    ("action_root_key", []),
    ("action_root_key", {}),
    ("namespace_id", object()),
    ("resource_kind", None),
    ("schema_version", object()),
):
    bad_root = replace(first_root, **{field_name: malformed})
    check_rejected_without_exception(
        replace(registry, admitted_action_roots=(bad_root, *roots[1:])),
        f"fail-closed malformed root {field_name}:{type(malformed).__name__}",
    )

for field_name, malformed in (
    ("predicate_id", []),
    ("predicate_id", {}),
    ("predicate_key", []),
    ("predicate_key", {}),
    ("action_root_id", []),
    ("action_root_id", {}),
    ("namespace_id", object()),
    ("resource_kind", None),
    ("schema_version", object()),
):
    bad_predicate = replace(first_predicate, **{field_name: malformed})
    check_rejected_without_exception(
        replace(registry, admitted_predicates=(bad_predicate, *predicates[1:])),
        f"fail-closed malformed predicate {field_name}:{type(malformed).__name__}",
    )

bad_namespace = replace(CURRENT_NAMESPACE, namespace_key=object())
check_rejected_without_exception(
    replace(registry, current_namespace=bad_namespace),
    "fail-closed malformed namespace canonical field",
)

for field_name, malformed in (
    ("predicate_key", "Inspect"),
    ("action_root_id", roots[1].action_root_id),
    ("namespace_id", "wrong"),
    ("lifecycle_state", PredicateLifecycleState.CANDIDATE),
    ("participant_role_schema_refs", ("unauthorized",)),
    ("predicate_frame_schema_refs", ("unauthorized",)),
    ("effect_boundary_refs", ("unauthorized",)),
    ("capability_family_reference_refs", ("unauthorized",)),
    ("selected_for_occurrence", True),
    ("execution_authorized", True),
):
    bad_predicate = replace(first_predicate, **{field_name: malformed})
    check_rejected_without_exception(
        replace(registry, admitted_predicates=(bad_predicate, *predicates[1:])),
        f"mutated predicate rejected {field_name}",
    )

# Source inspection: standard library, immutable in-memory construction, no effects.
package_root = REPO / "aiweb_language_core_bootstrap" / "predicate_role_frame_registry" / "built_in_action_root_registry"
source_files = tuple(sorted(package_root.glob("*.py")))
check(len(source_files) == 7, "exact seven package files")
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
    top_level_effect_calls: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported_roots.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            top_level_effect_calls.append(ast.unparse(node.value.func))
    check(not imported_roots.intersection(prohibited_import_roots), f"no prohibited import {path.name}")
    check(not top_level_effect_calls, f"no top-level effect call {path.name}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            rendered = ast.unparse(node.func)
            check(rendered not in prohibited_calls, f"no prohibited call {path.name}:{rendered}")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                rendered = ast.unparse(decorator).lower()
                check(not any(marker in rendered for marker in (".route", "@app.", "@router.", "fastapi", "flask")),
                      f"no route decorator {path.name}")

print("AI.WEB SLICE 38C BEHAVIOR TEST: PASS")
print(f"check_count={checks}")
print(f"malformed_registry_cases={malformed_cases}")
print("admitted_action_roots=5")
print("admitted_predicates=5")
print("deferred_higher_consequence_roots=5")
print("participant_role_registry_entries=0")
print("predicate_frame_registry_entries=0")
print("capability_reference_entries=0")
print("surface_form_lookup=0")
print("occurrence_interpretation=0")
print("predicate_selection=0")
print("nearest_known_substitution=0")
print("semantic_similarity_authority=0")
print("evidence_validation=0")
print("memory_routes_tools_actions_rendering_delivery=0")
