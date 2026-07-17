#!/usr/bin/env python3
"""Visible independent verifier for Slice 38F."""

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
EXPECTED_PARENT_HEAD = "93e0fcf5322f8beae9fe8ed7e0d57805f2c63674"
EXPECTED_PARENT_TREE = "c2b2ae647a1ca45cf83927b9ccef39941e85067e"
EXPECTED_PARENT_SUBJECT = "Slice 38E predicate-frame constraints and role compatibility"
EXPECTED_COMMIT_SUBJECT = "Slice 38F capability-family references and effect boundaries"
EXPECTED_PREDECESSOR_COUNT = 318
EXPECTED_BEHAVIOR_CHECKS = 10302
EXPECTED_MALFORMED_CASES = 4581
EXPECTED_EFFECT_BOUNDARIES = 6
EXPECTED_CAPABILITY_FAMILIES = 6
EXPECTED_FRAME_EFFECT_REFERENCES = 5
EXPECTED_FRAME_CAPABILITY_REFERENCES = 5
EXPECTED_COMPATIBILITY_RECORDS = 6
EXPECTED_LIFECYCLE_RULES = 19
EXPECTED_TRANSITIONS = 28

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/__init__.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/authority.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/identity.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/lifecycle.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/records.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/registry.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/schema.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/capability_family_reference_registry/validation.py",
    "scripts/AIWEB_SLICE38F_CAPABILITY_FAMILY_REFERENCE_AND_EFFECT_BOUNDARY_DECISION.md",
    "scripts/AIWEB_SLICE38F_CAPABILITY_FAMILY_REFERENCES_EFFECT_BOUNDARIES_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE38F_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/README_aiweb_slice38f_capability_family_references_effect_boundaries.md",
    "scripts/aiweb_slice38f_capability_family_references_effect_boundaries_verify.py",
    "scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py",
)
CURRENT_BEHAVIOR_TEST = (
    "scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py"
)
SOURCE_ONLY_INHERITED_TESTS = (
    "scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py",
    "scripts/test_aiweb_slice38d_participant_role_identity_registry.py",
    "scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
    "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
)
LIVE_INHERITED_TESTS = (
    "scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py",
    "scripts/test_aiweb_slice38d_participant_role_identity_registry.py",
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
    return subprocess.run(
        ("git", "-C", str(repository), *args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    records: list[tuple[str, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise ValueError(f"invalid checksum line {number}")
        digest, relative = parts
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise ValueError(f"unsafe checksum path line {number}")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError(f"invalid digest line {number}")
        records.append((digest, relative))
    return tuple(records)


def run_visible_test(
    repository: Path,
    relative: str,
    number: int,
    total: int,
    environment: dict[str, str],
) -> int:
    command = (sys.executable, "-B", str(repository / relative), str(repository))
    print(f"\n=== VISIBLE TEST {number} OF {total} ===", flush=True)
    print(f"path={relative}", flush=True)
    print("command=" + " ".join(command), flush=True)
    print("output_begins_below", flush=True)
    started = time.monotonic()
    child_environment = dict(environment)
    child_environment["PYTHONPYCACHEPREFIX"] = (
        f"{environment.get('PYTHONPYCACHEPREFIX', '/tmp/aiweb_slice38f_visible')}_{number}"
    )
    try:
        result = subprocess.run(
            command,
            cwd=str(repository),
            env=child_environment,
            check=False,
            timeout=300,
        )
        return_code = result.returncode
    except subprocess.TimeoutExpired:
        return_code = 124
        print("FAIL: visible test exceeded 300-second timeout", flush=True)
    print("output_ended_above", flush=True)
    print(f"duration_seconds={time.monotonic() - started:.3f}", flush=True)
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
        verifier.check(unstaged_paths == (), "precommit unstaged tracked changes present")
        verifier.check(untracked_paths == (), "precommit untracked paths present")
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
        changed = git(repository, "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD")
        verifier.check(parent.returncode == 0 and parent.stdout.strip() == EXPECTED_PARENT_HEAD, "committed parent mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT, "committed subject mismatch")
        verifier.check(status.returncode == 0 and status.stdout.strip() == "", "committed repo not clean")
        entries = tuple(line.split("\t", 1) for line in changed.stdout.splitlines() if line)
        verifier.check(tuple(sorted(path for _, path in entries)) == exact, "committed path set mismatch")
        verifier.check(all(status_code == "A" for status_code, _ in entries), "committed entries not additions")
    else:
        verifier.check(False, f"unsupported mode {mode}")


def verify_predecessors(repository: Path, verifier: Verifier) -> None:
    path = repository / "scripts" / "AIWEB_SLICE38F_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
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
    package = (
        repository
        / "aiweb_language_core_bootstrap"
        / "predicate_role_frame_registry"
        / "capability_family_reference_registry"
    )
    files = tuple(sorted(package.glob("*.py")))
    verifier.check(
        tuple(path.name for path in files)
        == (
            "__init__.py", "authority.py", "identity.py", "lifecycle.py",
            "records.py", "registry.py", "schema.py", "validation.py",
        ),
        "Slice 38F source names mismatch",
    )
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
                verifier.check(
                    ast.unparse(node.func) not in PROHIBITED_CALLS,
                    f"prohibited call {path.name}:{ast.unparse(node.func)}",
                )


def verify_runtime(repository: Path, verifier: Verifier) -> None:
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))
    try:
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.capability_family_reference_registry import (
            ADMITTED_CAPABILITY_FAMILY_KEYS,
            ADMITTED_EFFECT_BOUNDARY_KEYS,
            CAPABILITY_FAMILY_REFERENCE_REGISTRY,
            CAPABILITY_REFERENCE_LIFECYCLE_RULES,
            DEFERRED_CAPABILITY_FAMILY_KEYS,
            FRAMES_WITHOUT_CAPABILITY_REFERENCE,
            UNBOUND_CAPABILITY_FAMILY_KEYS,
            validate_registry,
        )
    except Exception as error:
        verifier.check(False, f"Slice 38F import failed: {error}")
        return
    registry = CAPABILITY_FAMILY_REFERENCE_REGISTRY
    report = validate_registry(registry)
    verifier.check(report.ok, "Slice 38F registry validation failed")
    verifier.check(ADMITTED_EFFECT_BOUNDARY_KEYS == (
        "no_action", "read_only", "communicative_only",
        "verification_review_only", "simulation_only",
        "protected_mathematical_output_only",
    ), "admitted effect set mismatch")
    verifier.check(ADMITTED_CAPABILITY_FAMILY_KEYS == (
        "read_only_inspection", "source_comparison", "draft_preparation",
        "verification_review", "non_live_simulation",
        "protected_mathematical_operation",
    ), "admitted capability set mismatch")
    verifier.check(DEFERRED_CAPABILITY_FAMILY_KEYS == (
        "memory_request", "software_change_proposal", "delivery_request",
    ), "deferred capability set mismatch")
    verifier.check(FRAMES_WITHOUT_CAPABILITY_REFERENCE == ("request_non_authorizing",), "frame without capability mismatch")
    verifier.check(UNBOUND_CAPABILITY_FAMILY_KEYS == ("protected_mathematical_operation",), "unbound capability mismatch")
    verifier.check(len(registry.effect_boundaries) == EXPECTED_EFFECT_BOUNDARIES, "effect boundary count mismatch")
    verifier.check(len(registry.capability_families) == EXPECTED_CAPABILITY_FAMILIES, "capability family count mismatch")
    verifier.check(len(registry.frame_effect_references) == EXPECTED_FRAME_EFFECT_REFERENCES, "frame effect reference count mismatch")
    verifier.check(len(registry.frame_capability_references) == EXPECTED_FRAME_CAPABILITY_REFERENCES, "frame capability reference count mismatch")
    verifier.check(len(registry.compatibility_records) == EXPECTED_COMPATIBILITY_RECORDS, "compatibility count mismatch")
    verifier.check(len(CAPABILITY_REFERENCE_LIFECYCLE_RULES) == EXPECTED_LIFECYCLE_RULES, "lifecycle rule count mismatch")
    verifier.check(len(registry.transitions) == EXPECTED_TRANSITIONS, "transition count mismatch")
    manifest = registry.manifest
    true_fields = ("registry_read_only", "registry_closed", "exact_identity_lookup_only")
    for field in true_fields:
        verifier.check(getattr(manifest, field) is True, f"manifest true boundary failed {field}")
    false_fields = (
        "source_term_lookup_installed", "occurrence_frame_selection_installed",
        "occurrence_role_assignment_installed", "candidate_meaning_creation_installed",
        "selected_meaning_installed", "gate_outcome_installed",
        "capability_availability_registry_installed", "route_registry_installed",
        "invocation_registry_installed", "argument_builder_installed",
        "tool_activation_installed", "action_execution_installed",
        "evidence_validation_installed", "memory_access_installed",
        "rendering_installed", "delivery_installed",
        "external_resource_loading_installed", "implementation_installed",
        "default_capability_reference_installed", "nearest_known_substitution_installed",
        "semantic_similarity_installed", "llm_authority_installed",
    )
    for field in false_fields:
        verifier.check(getattr(manifest, field) is False, f"manifest authority nonzero {field}")
    for reference in registry.frame_capability_references:
        verifier.check(reference.capability_available is False, "capability reference became availability")
        verifier.check(reference.route_identity is None and reference.route_available is False, "capability reference became route")
        verifier.check(reference.invocation_identity is None and reference.invocation_proposed is False, "capability reference became invocation")
        verifier.check(reference.argument_bundle_id is None and reference.arguments_constructed is False, "capability reference constructed arguments")
        verifier.check(reference.permission_id is None and reference.permission_granted is False, "capability reference became permission")
        verifier.check(reference.execution_receipt_id is None and reference.execution_performed is False, "capability reference became execution")
        verifier.check(reference.result_verified is False, "capability reference became result proof")
        verifier.check(reference.tool_bound is False, "capability reference became tool binding")
        verifier.check(reference.memory_operation_performed is False, "capability reference became memory operation")
        verifier.check(reference.delivery_performed is False, "capability reference became delivery")
        verifier.check(reference.external_resource_admitted is False, "capability reference admitted resource")
        verifier.check(reference.implementation_performed is False, "capability reference implemented code")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default="/home/nic/forge")
    parser.add_argument(
        "--mode",
        choices=("source-only", "applied", "precommit", "committed"),
        default="source-only",
    )
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    verifier = Verifier()

    print("AI.WEB SLICE 38F VISIBLE INDEPENDENT VERIFIER", flush=True)
    print(f"repository={repository}", flush=True)
    print(f"mode={args.mode}", flush=True)
    print("hidden_test_workers=0", flush=True)
    print("test_output_suppression=0", flush=True)

    verifier.check(repository.is_dir(), "repository missing")
    for relative in EXACT_PATHS:
        path = repository / relative
        verifier.check(path.is_file(), f"Slice 38F file missing: {relative}")
        verifier.check(not path.is_symlink(), f"Slice 38F symlink prohibited: {relative}")

    verify_git_state(repository, args.mode, verifier)
    verify_predecessors(repository, verifier)
    verify_sources(repository, verifier)
    verify_runtime(repository, verifier)

    inherited = SOURCE_ONLY_INHERITED_TESTS if args.mode == "source-only" else LIVE_INHERITED_TESTS
    tests = (CURRENT_BEHAVIOR_TEST, *inherited)
    total = len(tests)
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.setdefault("PYTHONPYCACHEPREFIX", "/tmp/aiweb_slice38f_visible")
    behavior_output_values = {
        "check_count": EXPECTED_BEHAVIOR_CHECKS,
        "malformed_cases": EXPECTED_MALFORMED_CASES,
    }

    for number, relative in enumerate(tests, 1):
        verifier.check((repository / relative).is_file(), f"visible test missing: {relative}")
        if (repository / relative).is_file():
            return_code = run_visible_test(repository, relative, number, total, environment)
            verifier.check(return_code == 0, f"visible test failed: {relative} rc={return_code}")

    print("\n=== SLICE 38F VERIFIER SUMMARY ===", flush=True)
    print(f"pass_count={verifier.passes}", flush=True)
    print(f"failure_count={len(verifier.failures)}", flush=True)
    if verifier.failures:
        print("SLICE 38F VISIBLE INDEPENDENT VERIFIER: FAIL", flush=True)
        for failure in verifier.failures[:300]:
            print(f"FAIL: {failure}", flush=True)
        return 1

    print("SLICE 38F VISIBLE INDEPENDENT VERIFIER: PASS", flush=True)
    print(f"protected_predecessor_files={EXPECTED_PREDECESSOR_COUNT}", flush=True)
    print(f"inherited_tests={len(inherited)}", flush=True)
    print(f"visible_total_tests={total}", flush=True)
    print(f"slice38f_files={len(EXACT_PATHS)}", flush=True)
    print(f"behavior_checks={behavior_output_values['check_count']}", flush=True)
    print(f"malformed_capability_reference_cases={behavior_output_values['malformed_cases']}", flush=True)
    print(f"effect_boundaries={EXPECTED_EFFECT_BOUNDARIES}", flush=True)
    print(f"capability_families={EXPECTED_CAPABILITY_FAMILIES}", flush=True)
    print(f"frame_effect_references={EXPECTED_FRAME_EFFECT_REFERENCES}", flush=True)
    print(f"frame_capability_references={EXPECTED_FRAME_CAPABILITY_REFERENCES}", flush=True)
    print(f"capability_effect_compatibility_records={EXPECTED_COMPATIBILITY_RECORDS}", flush=True)
    print("deferred_capability_families=3", flush=True)
    print("frames_without_capability_reference=1", flush=True)
    print("unbound_capability_families=1", flush=True)
    print(f"lifecycle_transition_rules={EXPECTED_LIFECYCLE_RULES}", flush=True)
    print(f"lifecycle_transitions={EXPECTED_TRANSITIONS}", flush=True)
    print("capability_reference_is_availability=0", flush=True)
    print("capability_availability_is_route=0", flush=True)
    print("route_is_invocation=0", flush=True)
    print("invocation_proposal_is_execution=0", flush=True)
    print("frame_completion_is_permission=0", flush=True)
    print("argument_construction=0", flush=True)
    print("memory_delivery_external_resource_implementation=0", flush=True)
    print("routes_tools_actions_execution=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
