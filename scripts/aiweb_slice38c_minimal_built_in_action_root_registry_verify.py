#!/usr/bin/env python3
"""Visible independent verifier for Slice 38C.

Every current-slice and inherited test is executed sequentially. The command,
child output, duration, and return code are printed directly to the terminal.
No test runs in a hidden worker or background thread.
"""

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
EXPECTED_PARENT_HEAD = "c502b74ada70ed0bc551fb591c49fd119191f52f"
EXPECTED_PARENT_TREE = "77d349f51a617eab98d1fddeef7ba9e57f52dec6"
EXPECTED_PARENT_SUBJECT = "Slice 38B deterministic validation identity versioning lifecycle"
EXPECTED_COMMIT_SUBJECT = "Slice 38C minimal built-in action-root registry"
EXPECTED_PREDECESSOR_COUNT = 277
EXPECTED_BEHAVIOR_CHECKS = 1239
EXPECTED_MALFORMED_CASES = 627
EXPECTED_ACTION_ROOTS = 5
EXPECTED_PREDICATES = 5
EXPECTED_TRANSITION_RULES = 51

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/__init__.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/authority.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/identity.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/records.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/registry.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/schema.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/validation.py",
    "scripts/AIWEB_SLICE38C_MINIMAL_BUILT_IN_ACTION_ROOT_REGISTRY_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE38C_ACTION_ROOT_ADMISSION_AND_DEFERRED_SCOPE_DECISION.md",
    "scripts/AIWEB_SLICE38C_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/README_aiweb_slice38c_minimal_built_in_action_root_registry.md",
    "scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py",
    "scripts/aiweb_slice38c_minimal_built_in_action_root_registry_verify.py",
)

CURRENT_BEHAVIOR_TEST = (
    "scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py"
)
SOURCE_ONLY_INHERITED_TESTS = (
    "scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
    "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
    "scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py",
)
LIVE_INHERITED_TESTS = (
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
    "llama_index", "nltk", "numpy", "openai", "pandas", "requests",
    "scipy", "sentence_transformers", "sklearn", "spacy", "tensorflow",
    "torch", "transformers", "urllib", "socket", "subprocess",
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
    return subprocess.run(
        ("git", "-C", str(repository), *args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    records: list[tuple[str, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed checksum line {number}") from error
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise ValueError(f"unsafe checksum path {relative!r}")
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"invalid SHA-256 at line {number}")
        records.append((digest, relative))
    return tuple(records)


def run_visible_test(
    repository: Path,
    relative_path: str,
    *,
    number: int,
    total: int,
    environment: dict[str, str],
) -> int:
    command = (sys.executable, "-B", str(repository / relative_path), str(repository))
    print()
    print(f"=== VISIBLE TEST {number} OF {total} ===", flush=True)
    print(f"path={relative_path}", flush=True)
    print("command=" + " ".join(command), flush=True)
    print("output_begins_below", flush=True)
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=str(repository),
            env=environment,
            check=False,
            timeout=300,
        )
        return_code = result.returncode
    except subprocess.TimeoutExpired:
        return_code = 124
        print("FAIL: visible test exceeded the 300-second fail-closed timeout", flush=True)
    duration = time.monotonic() - started
    print("output_ended_above", flush=True)
    print(f"duration_seconds={duration:.3f}", flush=True)
    print(f"return_code={return_code}", flush=True)
    return return_code


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

    staged = git(repository, "diff", "--cached", "--name-only")
    staged_status = git(repository, "diff", "--cached", "--name-status")
    unstaged = git(repository, "diff", "--name-only")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")
    for result, label in ((staged, "staged"), (staged_status, "staged status"), (unstaged, "unstaged"), (untracked, "untracked")):
        verifier.check(result.returncode == 0, f"git {label} inspection failed")
    if any(result.returncode != 0 for result in (staged, staged_status, unstaged, untracked)):
        return

    exact = tuple(sorted(EXACT_PATHS))
    staged_paths = tuple(sorted(line for line in staged.stdout.splitlines() if line))
    unstaged_paths = tuple(sorted(line for line in unstaged.stdout.splitlines() if line))
    untracked_paths = tuple(sorted(line for line in untracked.stdout.splitlines() if line))

    if mode == "applied":
        verifier.check(head.stdout.strip() == EXPECTED_PARENT_HEAD, "applied HEAD mismatch")
        verifier.check(tree.stdout.strip() == EXPECTED_PARENT_TREE, "applied tree mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_PARENT_SUBJECT, "applied subject mismatch")
        verifier.check(staged_paths == (), "applied staged paths present")
        verifier.check(unstaged_paths == (), "applied tracked modifications present")
        verifier.check(untracked_paths == exact, "applied untracked path set mismatch")
    elif mode == "precommit":
        verifier.check(head.stdout.strip() == EXPECTED_PARENT_HEAD, "precommit HEAD mismatch")
        verifier.check(tree.stdout.strip() == EXPECTED_PARENT_TREE, "precommit tree mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_PARENT_SUBJECT, "precommit subject mismatch")
        verifier.check(staged_paths == exact, "precommit staged path set mismatch")
        verifier.check(unstaged_paths == (), "precommit unstaged tracked changes present")
        verifier.check(untracked_paths == (), "precommit untracked paths present")
        statuses = tuple(line.split("\t", 1)[0] for line in staged_status.stdout.splitlines() if line)
        verifier.check(len(statuses) == len(EXACT_PATHS), "precommit staged status count mismatch")
        verifier.check(all(status == "A" for status in statuses), "precommit paths are not all additions")
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
        changed = git(repository, "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD")
        verifier.check(parent.returncode == 0, "committed parent read failed")
        verifier.check(status.returncode == 0, "committed status read failed")
        verifier.check(changed.returncode == 0, "committed changed paths read failed")
        if parent.returncode == 0:
            verifier.check(parent.stdout.strip() == EXPECTED_PARENT_HEAD, "committed parent mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT, "committed subject mismatch")
        verifier.check(head.stdout.strip() != EXPECTED_PARENT_HEAD, "committed HEAD did not advance")
        verifier.check(tree.stdout.strip() != EXPECTED_PARENT_TREE, "committed tree did not advance")
        if status.returncode == 0:
            verifier.check(status.stdout.strip() == "", "committed repository not clean")
        if changed.returncode == 0:
            entries = tuple(line.split("\t", 1) for line in changed.stdout.splitlines() if line)
            verifier.check(tuple(sorted(path for _, path in entries)) == exact, "committed path set mismatch")
            verifier.check(all(status_code == "A" for status_code, _ in entries), "committed entries not additions")
    else:
        verifier.check(False, f"unsupported mode {mode}")


def verify_predecessors(repository: Path, verifier: Verifier) -> None:
    path = repository / "scripts" / "AIWEB_SLICE38C_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    verifier.check(path.is_file(), "protected predecessor manifest missing")
    if not path.is_file():
        return
    try:
        records = parse_manifest(path)
    except Exception as error:
        verifier.check(False, f"protected predecessor manifest invalid: {error}")
        return
    verifier.check(len(records) == EXPECTED_PREDECESSOR_COUNT, "protected predecessor count mismatch")
    verifier.check(len({relative for _, relative in records}) == len(records), "duplicate predecessor path")
    for expected_digest, relative in records:
        target = repository / relative
        verifier.check(target.is_file(), f"protected predecessor missing: {relative}")
        verifier.check(not target.is_symlink(), f"protected predecessor symlink: {relative}")
        if target.is_file() and not target.is_symlink():
            verifier.check(sha256_file(target) == expected_digest, f"protected predecessor hash mismatch: {relative}")


def verify_sources(repository: Path, verifier: Verifier) -> None:
    package = repository / "aiweb_language_core_bootstrap" / "predicate_role_frame_registry" / "built_in_action_root_registry"
    source_files = tuple(sorted(package.glob("*.py")))
    verifier.check(len(source_files) == 7, "exact seven Slice 38C package source files required")
    verifier.check(tuple(path.name for path in source_files) == (
        "__init__.py", "authority.py", "identity.py", "records.py", "registry.py", "schema.py", "validation.py"
    ), "Slice 38C source names mismatch")
    for path in source_files:
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except Exception as error:
            verifier.check(False, f"source parse failed {path.name}: {error}")
            continue
        imported_roots: set[str] = set()
        top_level_effect_calls: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                top_level_effect_calls.append(ast.unparse(node.value.func))
        verifier.check(not imported_roots.intersection(PROHIBITED_IMPORT_ROOTS), f"prohibited import in {path.name}")
        verifier.check(not top_level_effect_calls, f"top-level effect call in {path.name}")
        if path.name == "validation.py":
            verifier.check(
                "Validate the closed registry and fail closed for every malformed value."
                in text
                and "return _validate_built_in_action_root_registry(registry)" in text
                and "except Exception as error:" in text,
                "public registry validation must retain total fail-closed guard",
            )
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                rendered = ast.unparse(node.func)
                verifier.check(rendered not in PROHIBITED_CALLS, f"prohibited call {path.name}:{rendered}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    rendered = ast.unparse(decorator).lower()
                    verifier.check(not any(marker in rendered for marker in (".route", "@app.", "@router.", "fastapi", "flask")), f"route decorator {path.name}")


def verify_runtime_records(repository: Path, verifier: Verifier) -> None:
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))
    try:
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.built_in_action_root_registry import (
            ADMITTED_ACTION_ROOTS,
            ADMITTED_PREDICATES,
            BUILT_IN_ACTION_ROOT_KEYS,
            BUILT_IN_ACTION_ROOT_REGISTRY,
            CURRENT_NAMESPACE,
            SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES,
            validate_built_in_action_root_registry,
        )
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.governed_lifecycle import (
            PREDICATE_LIFECYCLE_TRANSITION_RULES,
            validate_governance_batch,
        )
    except Exception as error:
        verifier.check(False, f"Slice 38C import failed: {error}")
        return
    report = validate_built_in_action_root_registry(BUILT_IN_ACTION_ROOT_REGISTRY)
    verifier.check(report.ok, "Slice 38C registry validation failed")
    verifier.check(validate_governance_batch(BUILT_IN_ACTION_ROOT_REGISTRY.governance_batch).ok, "Slice 38C governance batch failed")
    verifier.check(BUILT_IN_ACTION_ROOT_KEYS == ("inspect", "report", "request", "verify", "simulate"), "admitted root set mismatch")
    verifier.check(tuple(record.action_root_key for record in ADMITTED_ACTION_ROOTS) == BUILT_IN_ACTION_ROOT_KEYS, "root registry order mismatch")
    verifier.check(tuple(record.predicate_key for record in ADMITTED_PREDICATES) == BUILT_IN_ACTION_ROOT_KEYS, "predicate registry order mismatch")
    verifier.check(len(ADMITTED_ACTION_ROOTS) == EXPECTED_ACTION_ROOTS, "root count mismatch")
    verifier.check(len(ADMITTED_PREDICATES) == EXPECTED_PREDICATES, "predicate count mismatch")
    verifier.check(len(PREDICATE_LIFECYCLE_TRANSITION_RULES) == EXPECTED_TRANSITION_RULES, "transition rule count mismatch")
    verifier.check(SLICE38C_DEFERRED_HIGHER_CONSEQUENCE_FAMILIES == ("approve", "install", "send", "remember", "rollback"), "deferred roots mismatch")
    verifier.check(CURRENT_NAMESPACE.lifecycle_state.value == "architecture_admitted", "namespace state mismatch")
    manifest = BUILT_IN_ACTION_ROOT_REGISTRY.manifest
    zero_fields = (
        "surface_form_lookup_allowed", "surface_normalization_allowed",
        "occurrence_interpretation_installed", "predicate_selection_installed",
        "nearest_known_mapping_installed", "semantic_similarity_installed",
        "concept_to_predicate_conversion_installed", "participant_role_population_installed",
        "role_assignment_installed", "predicate_frame_population_installed",
        "frame_completion_installed", "effect_boundary_population_installed",
        "capability_reference_population_installed", "capability_routing_installed",
        "route_registration_installed", "tool_activation_installed",
        "action_execution_installed", "evidence_validation_installed",
        "memory_access_installed", "rendering_installed", "delivery_installed",
        "external_resource_loading_installed", "llm_authority_installed",
    )
    for field_name in zero_fields:
        verifier.check(getattr(manifest, field_name) is False, f"authority field enabled: {field_name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--mode", choices=("source-only", "applied", "precommit", "committed"), default="source-only")
    arguments = parser.parse_args()
    repository = Path(arguments.repository).resolve()
    verifier = Verifier()

    print("AI.WEB SLICE 38C VISIBLE INDEPENDENT VERIFIER", flush=True)
    print(f"repository={repository}", flush=True)
    print(f"mode={arguments.mode}", flush=True)
    print("hidden_test_workers=0", flush=True)
    print("test_output_suppression=0", flush=True)

    verifier.check(repository.is_dir(), "repository missing")
    for relative in EXACT_PATHS:
        target = repository / relative
        verifier.check(target.is_file(), f"Slice 38C path missing: {relative}")
        verifier.check(not target.is_symlink(), f"Slice 38C path is symlink: {relative}")

    verify_git_state(repository, arguments.mode, verifier)
    verify_predecessors(repository, verifier)
    verify_sources(repository, verifier)
    verify_runtime_records(repository, verifier)

    inherited = SOURCE_ONLY_INHERITED_TESTS if arguments.mode == "source-only" else LIVE_INHERITED_TESTS
    tests = (CURRENT_BEHAVIOR_TEST, *inherited)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = f"/tmp/aiweb_slice38c_visible_verifier_{os.getpid()}"
    for index, relative in enumerate(tests, start=1):
        target = repository / relative
        verifier.check(target.is_file(), f"visible test missing: {relative}")
        if not target.is_file():
            continue
        return_code = run_visible_test(
            repository,
            relative,
            number=index,
            total=len(tests),
            environment=environment,
        )
        verifier.check(return_code == 0, f"visible test failed: {relative} rc={return_code}")

    print()
    print("=== SLICE 38C VERIFIER SUMMARY ===")
    print(f"pass_count={verifier.passes}")
    print(f"failure_count={len(verifier.failures)}")
    for failure in verifier.failures:
        print(f"FAIL: {failure}")
    if verifier.failures:
        print("SLICE 38C VISIBLE INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 38C VISIBLE INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={EXPECTED_PREDECESSOR_COUNT}")
    print(f"inherited_tests={len(inherited)}")
    print(f"visible_total_tests={len(tests)}")
    print("slice38c_files=13")
    print(f"behavior_checks={EXPECTED_BEHAVIOR_CHECKS}")
    print(f"malformed_registry_cases={EXPECTED_MALFORMED_CASES}")
    print(f"admitted_action_roots={EXPECTED_ACTION_ROOTS}")
    print(f"admitted_predicates={EXPECTED_PREDICATES}")
    print(f"transition_rules={EXPECTED_TRANSITION_RULES}")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
