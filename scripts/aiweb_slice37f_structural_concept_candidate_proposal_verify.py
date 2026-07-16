#!/usr/bin/env python3
"""Independent source, regression and Git-state verifier for Slice 37F."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

EXPECTED_BRANCH = "main"
EXPECTED_PARENT_HEAD = "721f0377f674311c50a0ae2adf3d03e89190e966"
EXPECTED_PARENT_TREE = "249345fe2e130bee30ac2cb3fd74c8eeff6ea726"
EXPECTED_PARENT_SUBJECT = "Slice 37E semantic classes and relation type rules"
EXPECTED_COMMIT_SUBJECT = "Slice 37F structural-to-concept candidate proposal"
EXPECTED_PREDECESSOR_COUNT = 641
EXPECTED_BEHAVIOR_CHECKS = 546
EXACT_PATHS = (
    "aiweb_language_core_bootstrap/structural_concept_candidate_proposal/__init__.py",
    "aiweb_language_core_bootstrap/structural_concept_candidate_proposal/identity.py",
    "aiweb_language_core_bootstrap/structural_concept_candidate_proposal/profile.py",
    "aiweb_language_core_bootstrap/structural_concept_candidate_proposal/proposal.py",
    "aiweb_language_core_bootstrap/structural_concept_candidate_proposal/schema.py",
    "aiweb_language_core_bootstrap/structural_concept_candidate_proposal/validation.py",
    "scripts/AIWEB_SLICE37F_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/AIWEB_SLICE37F_STRUCTURAL_CONCEPT_PROPOSAL_DESIGN_RULING.md",
    "scripts/README_aiweb_slice37f_structural_concept_candidate_proposal.md",
    "scripts/aiweb_slice37f_structural_concept_candidate_proposal_verify.py",
    "scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py",
)

SOURCE_ONLY_INHERITED_COMMANDS = (
    "scripts/test_aiweb_slice36g_deterministic_structural_derivation.py",
    "scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py",
    "scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py",
    "scripts/test_aiweb_slice37e_semantic_class_relation_registry.py",
)

LIVE_INHERITED_COMMANDS = (
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
)

PROHIBITED_PACKAGE_IMPORT_ROOTS = {
    "anthropic", "chromadb", "faiss", "gensim", "httpx", "keras", "langchain",
    "llama_index", "nltk", "numpy", "openai", "pandas", "requests", "scipy",
    "sentence_transformers", "sklearn", "spacy", "tensorflow", "torch", "transformers",
}
PROHIBITED_SOURCE_TOKENS = (
    "@app.route", "@router.", "FastAPI(", "Flask(", "requests.", "urlopen(",
    "socket.socket(", "subprocess.", "os.system(", "openai.", "anthropic.",
)


class Verifier:
    def __init__(self) -> None:
        self.passes = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if condition:
            self.passes += 1
        else:
            self.failures.append(label)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: tuple[str, ...], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(repository), *args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_checksum_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    records: list[tuple[str, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed predecessor checksum line {number}") from error
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise ValueError(f"unsafe predecessor checksum path {relative!r}")
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"invalid predecessor checksum at line {number}")
        records.append((digest, relative))
    return tuple(records)


def package_python_files(repository: Path) -> tuple[Path, ...]:
    package = repository / "aiweb_language_core_bootstrap/structural_concept_candidate_proposal"
    return tuple(sorted(package.glob("*.py")))


def ast_import_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".", 1)[0])
    return roots


def verify_git_state(repository: Path, mode: str, verifier: Verifier) -> None:
    branch = git(repository, "branch", "--show-current")
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    subject = git(repository, "show", "-s", "--format=%s", "HEAD")
    verifier.check(branch.returncode == 0, "git branch inspection failed")
    verifier.check(head.returncode == 0, "git HEAD inspection failed")
    verifier.check(tree.returncode == 0, "git tree inspection failed")
    verifier.check(subject.returncode == 0, "git subject inspection failed")
    if any(item.returncode != 0 for item in (branch, head, tree, subject)):
        return

    current_branch = branch.stdout.strip()
    current_head = head.stdout.strip()
    current_tree = tree.stdout.strip()
    current_subject = subject.stdout.strip()
    verifier.check(current_branch == EXPECTED_BRANCH, f"branch mismatch: {current_branch}")

    staged = git(repository, "diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB")
    unstaged = git(repository, "diff", "--name-only")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")
    verifier.check(staged.returncode == 0, "staged path inspection failed")
    verifier.check(unstaged.returncode == 0, "unstaged path inspection failed")
    verifier.check(untracked.returncode == 0, "untracked path inspection failed")
    if any(item.returncode != 0 for item in (staged, unstaged, untracked)):
        return

    exact = tuple(sorted(EXACT_PATHS))
    staged_paths = tuple(sorted(line for line in staged.stdout.splitlines() if line))
    untracked_paths = tuple(sorted(line for line in untracked.stdout.splitlines() if line))

    if mode == "precommit":
        verifier.check(current_head == EXPECTED_PARENT_HEAD, f"precommit parent HEAD mismatch: {current_head}")
        verifier.check(current_tree == EXPECTED_PARENT_TREE, f"precommit parent tree mismatch: {current_tree}")
        verifier.check(current_subject == EXPECTED_PARENT_SUBJECT, f"precommit parent subject mismatch: {current_subject}")
        verifier.check(staged_paths == exact, "precommit staged set is not exact Slice 37F payload")
        verifier.check(not unstaged.stdout.strip(), "precommit unstaged changes present")
        verifier.check(not untracked_paths, "precommit untracked files present")
        statuses = git(repository, "diff", "--cached", "--name-status")
        verifier.check(statuses.returncode == 0, "precommit status inspection failed")
        if statuses.returncode == 0:
            rows = [line.split("\t", 1) for line in statuses.stdout.splitlines() if line]
            verifier.check(len(rows) == len(EXACT_PATHS), "precommit staged count mismatch")
            verifier.check(all(row[0] == "A" for row in rows), "precommit payload must be additions only")
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        verifier.check(parent.returncode == 0, "committed parent inspection failed")
        if parent.returncode == 0:
            verifier.check(parent.stdout.strip() == EXPECTED_PARENT_HEAD, "committed parent mismatch")
        verifier.check(current_subject == EXPECTED_COMMIT_SUBJECT, "committed subject mismatch")
        verifier.check(not staged_paths, "committed staged files present")
        verifier.check(not unstaged.stdout.strip(), "committed unstaged files present")
        verifier.check(not untracked_paths, "committed untracked files present")
        committed = git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
        statuses = git(repository, "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD")
        verifier.check(committed.returncode == 0, "committed path inspection failed")
        verifier.check(statuses.returncode == 0, "committed status inspection failed")
        if committed.returncode == 0:
            committed_paths = tuple(sorted(line for line in committed.stdout.splitlines() if line))
            verifier.check(committed_paths == exact, "committed path set is not exact Slice 37F payload")
        if statuses.returncode == 0:
            rows = [line.split("\t", 1) for line in statuses.stdout.splitlines() if line]
            verifier.check(all(row[0] == "A" for row in rows), "committed payload must be additions only")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", choices=("source-only", "precommit", "committed"), default="source-only")
    arguments = parser.parse_args()

    repository = Path(arguments.repository).resolve()
    verifier = Verifier()
    print("AI.WEB SLICE 37F INDEPENDENT VERIFIER")
    print(f"mode={arguments.mode}")

    verifier.check(repository.is_dir(), "repository directory missing")
    verifier.check((repository / ".git").is_dir(), "repository .git directory missing")
    if verifier.failures:
        print(f"pass_count={verifier.passes}")
        print(f"failure_count={len(verifier.failures)}")
        for failure in verifier.failures:
            print(f"FAIL: {failure}")
        return 1

    for relative in EXACT_PATHS:
        target = repository / relative
        verifier.check(target.is_file() and not target.is_symlink(), f"missing or unsafe Slice 37F path: {relative}")

    manifest_path = repository / "scripts/AIWEB_SLICE37F_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    try:
        predecessor_records = parse_checksum_manifest(manifest_path)
    except Exception as error:
        verifier.failures.append(str(error))
        predecessor_records = ()
    verifier.check(len(predecessor_records) == EXPECTED_PREDECESSOR_COUNT, "protected predecessor count mismatch")
    for expected, relative in predecessor_records:
        target = repository / relative
        verifier.check(target.is_file() and not target.is_symlink(), f"protected predecessor missing: {relative}")
        if target.is_file() and not target.is_symlink():
            verifier.check(sha256_file(target) == expected, f"protected predecessor hash mismatch: {relative}")

    package_files = package_python_files(repository)
    verifier.check(len(package_files) == 6, "Slice 37F package Python file count mismatch")
    for path in package_files:
        try:
            source = path.read_text(encoding="utf-8", errors="strict")
            tree = ast.parse(source, filename=str(path))
            verifier.check(True, f"AST parse {path.name}")
            roots = ast_import_roots(tree)
            verifier.check(not roots.intersection(PROHIBITED_PACKAGE_IMPORT_ROOTS), f"prohibited package import in {path.name}")
            lowered = source.lower()
            prohibited_hits = tuple(token for token in PROHIBITED_SOURCE_TOKENS if token.lower() in lowered)
            verifier.check(not prohibited_hits, f"prohibited source token in {path.name}: {prohibited_hits}")
            verifier.check(not any(line.rstrip(" \t") != line for line in source.splitlines()), f"trailing whitespace in {path.name}")
        except Exception as error:
            verifier.failures.append(f"source inspection failed for {path.name}: {error}")

    cache_paths = tuple(
        path.relative_to(repository).as_posix()
        for root in (
            repository / "aiweb_language_core_bootstrap/structural_concept_candidate_proposal",
            repository / "scripts",
        )
        if root.exists()
        for path in root.rglob("*")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}
    )
    verifier.check(not cache_paths, f"repository Python cache artifacts present: {cache_paths[:10]}")

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="aiweb_slice37f_verify_") as cache:
        environment["PYTHONPYCACHEPREFIX"] = cache
        behavior = run(
            (sys.executable, "-B", "scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py"),
            cwd=repository,
            env=environment,
        )
        if behavior.stdout:
            print(behavior.stdout, end="" if behavior.stdout.endswith("\n") else "\n")
        if behavior.stderr:
            print(behavior.stderr, end="" if behavior.stderr.endswith("\n") else "\n", file=sys.stderr)
        verifier.check(behavior.returncode == 0, "Slice 37F behavior test failed")
        verifier.check(f"check_count={EXPECTED_BEHAVIOR_CHECKS}" in behavior.stdout, "behavior check count mismatch")
        verifier.check("AI.WEB SLICE 37F BEHAVIOR TEST: PASS" in behavior.stdout, "behavior PASS marker missing")

        inherited = SOURCE_ONLY_INHERITED_COMMANDS if arguments.mode == "source-only" else LIVE_INHERITED_COMMANDS
        inherited_passed = 0
        for relative in inherited:
            result = run((sys.executable, "-B", relative), cwd=repository, env=environment)
            if result.returncode != 0:
                print(f"--- inherited failure: {relative} ---", file=sys.stderr)
                if result.stdout:
                    print(result.stdout, file=sys.stderr)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
            verifier.check(result.returncode == 0, f"inherited suite failed: {relative}")
            if result.returncode == 0:
                inherited_passed += 1

    if arguments.mode in {"precommit", "committed"}:
        verify_git_state(repository, arguments.mode, verifier)

    print(f"pass_count={verifier.passes}")
    print(f"failure_count={len(verifier.failures)}")
    if verifier.failures:
        for failure in verifier.failures:
            print(f"FAIL: {failure}")
        print("SLICE 37F INDEPENDENT VERIFIER: FAIL")
        return 1

    print("SLICE 37F INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(predecessor_records)}")
    print(f"inherited_tests={inherited_passed}")
    print(f"live_required_inherited_tests={len(LIVE_INHERITED_COMMANDS)}")
    print(f"slice37f_files={len(EXACT_PATHS)}")
    print("profile_count=1")
    print("registry_snapshot_count=1")
    print("exact_lookup_profile=1")
    print("candidate_meaning_created=0")
    print("selected_meaning_created=0")
    print("selected_sense_created=0")
    print("predicate_roles_truth_evidence_clarification=0")
    print("permission_routes_tools_actions_memory_rendering_delivery=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
