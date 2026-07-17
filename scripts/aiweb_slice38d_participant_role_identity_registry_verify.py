#!/usr/bin/env python3
"""Visible independent verifier for Slice 38D."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time

EXPECTED_BRANCH = "main"
EXPECTED_PARENT_HEAD = "2a1830041c0ed8fbff8aa6ca3129385fce8e68f4"
EXPECTED_PARENT_TREE = "020866a5ba8a41a2485a08cd0333d75ce246ac1a"
EXPECTED_PARENT_SUBJECT = "Slice 38C minimal built-in action-root registry"
EXPECTED_COMMIT_SUBJECT = "Slice 38D participant-role identity and registry"
EXPECTED_PREDECESSOR_COUNT = 290
EXPECTED_BEHAVIOR_CHECKS = 2102
EXPECTED_MALFORMED_CASES = 1539
EXPECTED_ROLES = 11
EXPECTED_DEPENDENCIES = 11
EXPECTED_RELATIONSHIPS = 5
EXPECTED_LIFECYCLE_RULES = 20
EXPECTED_TRANSITIONS = 28

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/__init__.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/authority.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/identity.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/lifecycle.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/records.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/registry.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/schema.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/participant_role_registry/validation.py",
    "scripts/AIWEB_SLICE38D_PARTICIPANT_ROLE_IDENTITY_REGISTRY_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE38D_ROLE_ADMISSION_AND_DEFERRED_SCOPE_DECISION.md",
    "scripts/AIWEB_SLICE38D_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/README_aiweb_slice38d_participant_role_identity_registry.md",
    "scripts/test_aiweb_slice38d_participant_role_identity_registry.py",
    "scripts/aiweb_slice38d_participant_role_identity_registry_verify.py",
)
CURRENT_BEHAVIOR_TEST = "scripts/test_aiweb_slice38d_participant_role_identity_registry.py"
SOURCE_ONLY_INHERITED_TESTS = (
    "scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py",
    "scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
    "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
    "scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py",
)
LIVE_INHERITED_TESTS = (
    "scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py",
    "scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py",
    "scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py",
    "scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py",
    "scripts/test_aiweb_slice32_accepted_boundary_component_loading.py",
    "scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py",
    "scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py",
    "scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py",
    "scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py",
    "scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py",
    "scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py",
    "scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py",
    "scripts/test_aiweb_slice36a_input_event_source_custody.py",
    "scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py",
    "scripts/test_aiweb_slice36b_deterministic_source_field_projection.py",
    "scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py",
    "scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py",
    "scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py",
    "scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py",
    "scripts/test_aiweb_slice36g_deterministic_structural_derivation.py",
    "scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py",
    "scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py",
    "scripts/test_aiweb_slice37b_deterministic_validation_identity_lifecycle.py",
    "scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py",
    "scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py",
    "scripts/test_aiweb_slice37e_semantic_class_relation_registry.py",
    "scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
    "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
    "scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py",
)
PROHIBITED_IMPORT_ROOTS = {
    "anthropic", "chromadb", "faiss", "gensim", "httpx", "langchain",
    "llama_index", "nltk", "numpy", "openai", "pandas", "requests", "scipy",
    "sentence_transformers", "sklearn", "spacy", "tensorflow", "torch",
    "transformers", "urllib", "socket", "subprocess",
}
PROHIBITED_CALLS = {
    "open", "eval", "exec", "compile", "__import__", "os.system", "os.popen",
    "subprocess.run", "subprocess.call", "subprocess.Popen", "Path.open",
    "Path.read_text", "Path.read_bytes", "Path.write_text", "Path.write_bytes",
    "Path.glob", "Path.rglob",
}


class Verifier:
    def __init__(self) -> None:
        self.passes = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        if condition is True:
            self.passes += 1
        else:
            self.failures.append(label)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(("git", "-C", str(repository), *args), text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    records: list[tuple[str, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        digest, relative = line.split("  ", 1)
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise ValueError(f"unsafe checksum path line {number}")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError(f"invalid digest line {number}")
        records.append((digest, relative))
    return tuple(records)


def run_visible_test(repository: Path, relative: str, number: int, total: int,
                     environment: dict[str, str]) -> int:
    command = (sys.executable, "-B", str(repository / relative), str(repository))
    print(f"\n=== VISIBLE TEST {number} OF {total} ===", flush=True)
    print(f"path={relative}", flush=True)
    print("command=" + " ".join(command), flush=True)
    print("output_begins_below", flush=True)
    started = time.monotonic()
    child_environment = dict(environment)
    child_environment["PYTHONPYCACHEPREFIX"] = (
        f"{environment.get('PYTHONPYCACHEPREFIX', '/tmp/aiweb_slice38d_visible')}_{number}"
    )
    try:
        result = subprocess.run(command, cwd=str(repository), env=child_environment,
                                check=False, timeout=300)
        rc = result.returncode
    except subprocess.TimeoutExpired:
        rc = 124
        print("FAIL: visible test exceeded 300-second timeout", flush=True)
    print("output_ended_above", flush=True)
    print(f"duration_seconds={time.monotonic() - started:.3f}", flush=True)
    print(f"return_code={rc}", flush=True)
    return rc


def verify_git_state(repository: Path, mode: str, verifier: Verifier) -> None:
    if mode == "source-only":
        return
    branch = git(repository, "branch", "--show-current")
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    subject = git(repository, "show", "-s", "--format=%s", "HEAD")
    for result, label in ((branch, "branch"), (head, "HEAD"), (tree, "tree"), (subject, "subject")):
        verifier.check(result.returncode == 0, f"git {label} inspection failed")
    if any(result.returncode != 0 for result in (branch, head, tree, subject)):
        return
    verifier.check(branch.stdout.strip() == EXPECTED_BRANCH, "branch mismatch")
    staged = git(repository, "diff", "--cached", "--name-status")
    unstaged = git(repository, "diff", "--name-only")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")
    exact = tuple(sorted(EXACT_PATHS))
    staged_entries = tuple(line.split("\t", 1) for line in staged.stdout.splitlines() if line)
    staged_paths = tuple(sorted(path for _, path in staged_entries))
    unstaged_paths = tuple(sorted(line for line in unstaged.stdout.splitlines() if line))
    untracked_paths = tuple(sorted(line for line in untracked.stdout.splitlines() if line))
    if mode == "applied":
        verifier.check(head.stdout.strip() == EXPECTED_PARENT_HEAD, "applied HEAD mismatch")
        verifier.check(tree.stdout.strip() == EXPECTED_PARENT_TREE, "applied tree mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_PARENT_SUBJECT, "applied subject mismatch")
        verifier.check(staged_paths == (), "applied staged paths present")
        verifier.check(unstaged_paths == (), "applied tracked changes present")
        verifier.check(untracked_paths == exact, "applied untracked path set mismatch")
    elif mode == "precommit":
        verifier.check(head.stdout.strip() == EXPECTED_PARENT_HEAD, "precommit HEAD mismatch")
        verifier.check(tree.stdout.strip() == EXPECTED_PARENT_TREE, "precommit tree mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_PARENT_SUBJECT, "precommit subject mismatch")
        verifier.check(staged_paths == exact, "precommit staged path set mismatch")
        verifier.check(all(status == "A" for status, _ in staged_entries), "precommit entries not additions")
        verifier.check(unstaged_paths == (), "precommit unstaged changes present")
        verifier.check(untracked_paths == (), "precommit untracked paths present")
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
        changed = git(repository, "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD")
        verifier.check(parent.returncode == 0 and parent.stdout.strip() == EXPECTED_PARENT_HEAD,
                       "committed parent mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT, "committed subject mismatch")
        verifier.check(status.returncode == 0 and status.stdout.strip() == "", "committed repo not clean")
        entries = tuple(line.split("\t", 1) for line in changed.stdout.splitlines() if line)
        verifier.check(tuple(sorted(path for _, path in entries)) == exact, "committed path set mismatch")
        verifier.check(all(status_code == "A" for status_code, _ in entries), "committed entries not additions")
    else:
        verifier.check(False, f"unsupported mode {mode}")


def verify_predecessors(repository: Path, verifier: Verifier) -> None:
    path = repository / "scripts" / "AIWEB_SLICE38D_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    verifier.check(path.is_file(), "protected predecessor manifest missing")
    if not path.is_file():
        return
    try:
        records = parse_manifest(path)
    except Exception as error:
        verifier.check(False, f"protected predecessor manifest invalid: {error}")
        return
    verifier.check(len(records) == EXPECTED_PREDECESSOR_COUNT, "predecessor count mismatch")
    verifier.check(len({relative for _, relative in records}) == len(records), "duplicate predecessor path")
    for expected, relative in records:
        target = repository / relative
        verifier.check(target.is_file(), f"protected predecessor missing: {relative}")
        verifier.check(not target.is_symlink(), f"protected predecessor symlink: {relative}")
        if target.is_file() and not target.is_symlink():
            verifier.check(sha256_file(target) == expected, f"predecessor hash mismatch: {relative}")


def verify_sources(repository: Path, verifier: Verifier) -> None:
    package = repository / "aiweb_language_core_bootstrap" / "predicate_role_frame_registry" / "participant_role_registry"
    files = tuple(sorted(package.glob("*.py")))
    verifier.check(tuple(path.name for path in files) == (
        "__init__.py", "authority.py", "identity.py", "lifecycle.py", "records.py",
        "registry.py", "schema.py", "validation.py",
    ), "Slice 38D source names mismatch")
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except Exception as error:
            verifier.check(False, f"source parse failed {path.name}: {error}")
            continue
        imported: set[str] = set()
        top_effects: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                top_effects.append(ast.unparse(node.value.func))
        verifier.check(not imported.intersection(PROHIBITED_IMPORT_ROOTS), f"prohibited import {path.name}")
        verifier.check(not top_effects, f"top-level effect call {path.name}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                verifier.check(ast.unparse(node.func) not in PROHIBITED_CALLS,
                               f"prohibited call {path.name}:{ast.unparse(node.func)}")


def verify_runtime(repository: Path, verifier: Verifier) -> None:
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))
    try:
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.participant_role_registry import (
            ADMITTED_PARTICIPANT_ROLE_KEYS, PARTICIPANT_ROLE_REGISTRY,
            ROLE_LIFECYCLE_RULES, SLICE38D_DEFERRED_ROLE_CANDIDATES,
            validate_registry,
        )
    except Exception as error:
        verifier.check(False, f"Slice 38D import failed: {error}")
        return
    report = validate_registry(PARTICIPANT_ROLE_REGISTRY)
    verifier.check(report.ok, "Slice 38D registry validation failed")
    verifier.check(ADMITTED_PARTICIPANT_ROLE_KEYS == (
        "initiator", "actor", "action_subject", "content", "source", "recipient",
        "instrument", "condition", "standard", "result", "output_target",
    ), "admitted role set mismatch")
    verifier.check(len(PARTICIPANT_ROLE_REGISTRY.admitted_roles) == EXPECTED_ROLES, "role count mismatch")
    verifier.check(len(PARTICIPANT_ROLE_REGISTRY.dependencies) == EXPECTED_DEPENDENCIES, "dependency count mismatch")
    verifier.check(len(PARTICIPANT_ROLE_REGISTRY.relationships) == EXPECTED_RELATIONSHIPS, "relationship count mismatch")
    verifier.check(len(PARTICIPANT_ROLE_REGISTRY.corrections) == 0, "active corrections present")
    verifier.check(len(PARTICIPANT_ROLE_REGISTRY.conflicts) == 0, "active conflicts present")
    verifier.check(len(ROLE_LIFECYCLE_RULES) == EXPECTED_LIFECYCLE_RULES, "lifecycle rule count mismatch")
    verifier.check(len(PARTICIPANT_ROLE_REGISTRY.transitions) == EXPECTED_TRANSITIONS, "transition count mismatch")
    verifier.check("affected_entity" in SLICE38D_DEFERRED_ROLE_CANDIDATES, "affected entity not deferred")
    verifier.check("location" in SLICE38D_DEFERRED_ROLE_CANDIDATES, "location not deferred")
    manifest = PARTICIPANT_ROLE_REGISTRY.manifest
    for field in (
        "surface_form_lookup_allowed", "surface_normalization_allowed",
        "occurrence_role_assignment_installed", "concept_candidate_to_role_assignment_installed",
        "semantic_relation_to_role_conversion_installed", "source_span_to_actor_conversion_installed",
        "grammatical_position_to_role_conversion_installed", "nearest_known_role_substitution_installed",
        "semantic_similarity_installed", "predicate_frame_population_installed", "frame_completion_installed",
        "capability_reference_population_installed", "capability_routing_installed", "route_registration_installed",
        "tool_activation_installed", "action_execution_installed", "evidence_validation_installed",
        "memory_access_installed", "rendering_installed", "delivery_installed",
        "external_resource_loading_installed", "llm_authority_installed",
    ):
        verifier.check(getattr(manifest, field) is False, f"authority field enabled: {field}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--mode", choices=("source-only", "applied", "precommit", "committed"),
                        default="source-only")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    verifier = Verifier()
    print("AI.WEB SLICE 38D VISIBLE INDEPENDENT VERIFIER", flush=True)
    print(f"repository={repository}", flush=True)
    print(f"mode={args.mode}", flush=True)
    print("hidden_test_workers=0", flush=True)
    print("test_output_suppression=0", flush=True)
    verifier.check(repository.is_dir(), "repository missing")
    for relative in EXACT_PATHS:
        target = repository / relative
        verifier.check(target.is_file(), f"Slice 38D path missing: {relative}")
        verifier.check(not target.is_symlink(), f"Slice 38D path symlink: {relative}")
    verify_git_state(repository, args.mode, verifier)
    verify_predecessors(repository, verifier)
    verify_sources(repository, verifier)
    verify_runtime(repository, verifier)
    inherited = SOURCE_ONLY_INHERITED_TESTS if args.mode == "source-only" else LIVE_INHERITED_TESTS
    tests = (CURRENT_BEHAVIOR_TEST, *inherited)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = f"/tmp/aiweb_slice38d_visible_{os.getpid()}"
    for number, relative in enumerate(tests, 1):
        target = repository / relative
        verifier.check(target.is_file(), f"visible test missing: {relative}")
        if target.is_file():
            verifier.check(run_visible_test(repository, relative, number, len(tests), environment) == 0,
                           f"visible test failed: {relative}")
    print("\n=== SLICE 38D VERIFIER SUMMARY ===")
    print(f"pass_count={verifier.passes}")
    print(f"failure_count={len(verifier.failures)}")
    for failure in verifier.failures:
        print(f"FAIL: {failure}")
    if verifier.failures:
        print("SLICE 38D VISIBLE INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 38D VISIBLE INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={EXPECTED_PREDECESSOR_COUNT}")
    print(f"inherited_tests={len(inherited)}")
    print(f"visible_total_tests={len(tests)}")
    print("slice38d_files=14")
    print(f"behavior_checks={EXPECTED_BEHAVIOR_CHECKS}")
    print(f"malformed_role_cases={EXPECTED_MALFORMED_CASES}")
    print(f"admitted_participant_roles={EXPECTED_ROLES}")
    print(f"role_dependencies={EXPECTED_DEPENDENCIES}")
    print(f"role_relationships={EXPECTED_RELATIONSHIPS}")
    print("active_corrections=0")
    print("active_conflicts=0")
    print(f"lifecycle_transition_rules={EXPECTED_LIFECYCLE_RULES}")
    print(f"lifecycle_transitions={EXPECTED_TRANSITIONS}")
    print("semantic_relation_to_role_conversion=0")
    print("concept_candidate_to_role_assignment=0")
    print("source_span_to_actor_conversion=0")
    print("grammatical_position_to_role_conversion=0")
    print("occurrence_role_assignment=0")
    print("predicate_frames_capabilities_routes_tools_actions=0")
    print("evidence_memory_rendering_delivery=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
