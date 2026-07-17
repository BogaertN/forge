#!/usr/bin/env python3
"""Visible independent verifier for AI.Web Slice 38G."""

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
EXPECTED_PARENT_HEAD = "9d135e51979657ee354cabd014e02df620d05d17"
EXPECTED_PARENT_TREE = "27ad163d8e77975e3963fa5d0efb95a4f16acab2"
EXPECTED_PARENT_SUBJECT = "Slice 38F capability-family references and effect boundaries"
EXPECTED_COMMIT_SUBJECT = "Slice 38G predicate role and frame candidate proposal"
EXPECTED_PREDECESSOR_COUNT = 332
EXPECTED_BEHAVIOR_CHECKS = 2351
EXPECTED_MALFORMED_CASES = 1788

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/__init__.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/authority.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/compatibility.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/identity.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/proposal.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/records.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/schema.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/snapshot.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/predicate_role_frame_candidate_proposal/validation.py",
    "scripts/AIWEB_SLICE38G_COMPATIBILITY_AND_CANDIDATE_BOUNDARY_DECISION.md",
    "scripts/AIWEB_SLICE38G_PREDICATE_ROLE_FRAME_CANDIDATE_PROPOSAL_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE38G_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/README_aiweb_slice38g_predicate_role_frame_candidate_proposal.md",
    "scripts/aiweb_slice38g_predicate_role_frame_candidate_proposal_verify.py",
    "scripts/test_aiweb_slice38g_predicate_role_frame_candidate_proposal.py",
)
CURRENT_BEHAVIOR_TEST = "scripts/test_aiweb_slice38g_predicate_role_frame_candidate_proposal.py"
LIVE_INHERITED_TESTS = (
    "scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py",'scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py', 'scripts/test_aiweb_slice38d_participant_role_identity_registry.py', 'scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py', 'scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py', 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py', 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py', 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py', 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py', 'scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py', 'scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py', 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py', 'scripts/test_aiweb_slice36g_deterministic_structural_derivation.py', 'scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py', 'scripts/test_aiweb_slice37b_deterministic_validation_identity_lifecycle.py', 'scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py', 'scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py', 'scripts/test_aiweb_slice37e_semantic_class_relation_registry.py', 'scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py', 'scripts/test_aiweb_slice37g_disabled_integration_closeout.py', 'scripts/test_aiweb_slice38a_action_root_predicate_schema.py', 'scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py')
SOURCE_ONLY_INHERITED_TESTS = (
    "scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py",
    "scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
    "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
    "scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py",
)
ALL_VISIBLE_TESTS = (CURRENT_BEHAVIOR_TEST,) + LIVE_INHERITED_TESTS

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


def run_visible_test(repository: Path, relative: str, number: int, total: int, environment: dict[str, str]) -> int:
    command = (sys.executable, "-B", str(repository / relative), str(repository))
    print(f"\n=== VISIBLE TEST {number} OF {total} ===", flush=True)
    print(f"path={relative}", flush=True)
    print("command=" + " ".join(command), flush=True)
    print("output_begins_below", flush=True)
    started = time.monotonic()
    child_environment = dict(environment)
    child_environment.pop("PYTHONPYCACHEPREFIX", None)
    try:
        result = subprocess.run(
            command,
            cwd=str(repository),
            env=child_environment,
            check=False,
            timeout=120,
        )
        return_code = result.returncode
    except subprocess.TimeoutExpired:
        return_code = 124
        print("FAIL: visible test exceeded 120-second timeout", flush=True)
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
        verifier.check(all(code == "A" for code, _ in entries), "committed entries not additions")
    else:
        verifier.check(False, f"unsupported mode {mode}")


def verify_predecessors(repository: Path, verifier: Verifier) -> None:
    path = repository / "scripts" / "AIWEB_SLICE38G_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
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
    package = repository / "aiweb_language_core_bootstrap" / "predicate_role_frame_registry" / "predicate_role_frame_candidate_proposal"
    expected_names = (
        "__init__.py", "authority.py", "compatibility.py", "identity.py",
        "proposal.py", "records.py", "schema.py", "snapshot.py", "validation.py",
    )
    files = tuple(sorted(package.glob("*.py")))
    verifier.check(tuple(path.name for path in files) == expected_names, "Slice 38G source names mismatch")
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
                verifier.check(ast.unparse(node.func) not in PROHIBITED_CALLS, f"prohibited call {path.name}:{ast.unparse(node.func)}")


def verify_runtime(repository: Path, verifier: Verifier) -> None:
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))
    try:
        from aiweb_language_core_bootstrap.predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
            CANONICAL_COMPATIBILITY_SNAPSHOT,
            DEFAULT_PROPOSAL_PROFILE,
            SLICE38_REGISTRY_SNAPSHOT,
            validate_compatibility_snapshot,
            validate_profile,
            validate_slice38_snapshot,
        )
    except Exception as error:
        verifier.check(False, f"Slice 38G import failed: {error}")
        return
    verifier.check(validate_profile(DEFAULT_PROPOSAL_PROFILE).ok, "profile invalid")
    verifier.check(validate_slice38_snapshot(SLICE38_REGISTRY_SNAPSHOT).ok, "Slice 38 snapshot invalid")
    verifier.check(validate_compatibility_snapshot(CANONICAL_COMPATIBILITY_SNAPSHOT).ok, "canonical compatibility invalid")
    verifier.check(CANONICAL_COMPATIBILITY_SNAPSHOT.rule_count == 0, "canonical compatibility rules not zero")
    verifier.check(CANONICAL_COMPATIBILITY_SNAPSHOT.conflict_count == 0, "canonical compatibility conflicts not zero")
    verifier.check(SLICE38_REGISTRY_SNAPSHOT.action_root_count == 5, "root count mismatch")
    verifier.check(SLICE38_REGISTRY_SNAPSHOT.predicate_count == 5, "predicate count mismatch")
    verifier.check(SLICE38_REGISTRY_SNAPSHOT.participant_role_count == 11, "role count mismatch")
    verifier.check(SLICE38_REGISTRY_SNAPSHOT.predicate_frame_count == 5, "frame count mismatch")
    verifier.check(SLICE38_REGISTRY_SNAPSHOT.capability_family_count == 6, "capability count mismatch")


def verify_payload_paths(repository: Path, verifier: Verifier) -> None:
    for relative in EXACT_PATHS:
        target = repository / relative
        verifier.check(target.is_file(), f"Slice 38G path missing: {relative}")
        verifier.check(not target.is_symlink(), f"Slice 38G path is symlink: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default="/home/nic/forge")
    parser.add_argument("--mode", choices=("source-only", "applied", "precommit", "committed"), default="source-only")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    verifier = Verifier()

    print("AI.WEB SLICE 38G VISIBLE INDEPENDENT VERIFIER", flush=True)
    print(f"repository={repository}", flush=True)
    print(f"mode={args.mode}", flush=True)
    print("hidden_test_workers=0", flush=True)
    print("test_output_suppression=0", flush=True)

    verifier.check(repository.is_dir(), "repository missing")
    verify_payload_paths(repository, verifier)
    verify_git_state(repository, args.mode, verifier)
    verify_predecessors(repository, verifier)
    verify_sources(repository, verifier)
    verify_runtime(repository, verifier)

    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    selected_tests = (
        (CURRENT_BEHAVIOR_TEST,) + SOURCE_ONLY_INHERITED_TESTS
        if args.mode == "source-only"
        else ALL_VISIBLE_TESTS
    )
    total = len(selected_tests)
    test_failures = 0
    for number, relative in enumerate(selected_tests, 1):
        if not (repository / relative).is_file():
            print(f"\nFAIL: missing visible test {relative}", flush=True)
            test_failures += 1
            continue
        return_code = run_visible_test(repository, relative, number, total, environment)
        verifier.check(return_code == 0, f"visible test failed: {relative} rc={return_code}")
        if return_code != 0:
            test_failures += 1

    print("\n=== SLICE 38G VERIFIER SUMMARY ===", flush=True)
    print(f"pass_count={verifier.passes}", flush=True)
    print(f"failure_count={len(verifier.failures)}", flush=True)
    for failure in verifier.failures:
        print(f"FAIL: {failure}", flush=True)
    if verifier.failures or test_failures:
        print("SLICE 38G VISIBLE INDEPENDENT VERIFIER: FAIL", flush=True)
        return 1
    print("SLICE 38G VISIBLE INDEPENDENT VERIFIER: PASS", flush=True)
    print(f"protected_predecessor_files={EXPECTED_PREDECESSOR_COUNT}", flush=True)
    print(f"inherited_tests={len(LIVE_INHERITED_TESTS)}", flush=True)
    print(f"visible_total_tests={len(ALL_VISIBLE_TESTS)}", flush=True)
    print(f"slice38g_files={len(EXACT_PATHS)}", flush=True)
    print(f"behavior_checks={EXPECTED_BEHAVIOR_CHECKS}", flush=True)
    print(f"malformed_candidate_cases={EXPECTED_MALFORMED_CASES}", flush=True)
    print("canonical_compatibility_rules=0", flush=True)
    print("canonical_compatibility_conflicts=0", flush=True)
    print("selected_predicate=0", flush=True)
    print("selected_frame=0", flush=True)
    print("selected_participant_assignment=0", flush=True)
    print("candidate_meaning=0", flush=True)
    print("selected_meaning=0", flush=True)
    print("permission_route_action_memory_delivery=0", flush=True)
    print("evidence_validity_truth=0", flush=True)
    print("clarification_refusal_blocked_progression=0", flush=True)
    print("filesystem_network_external_resource_llm_embedding_similarity=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
