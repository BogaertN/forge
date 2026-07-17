#!/usr/bin/env python3
"""Independent source, Git, boundary and regression verifier for Slice 38A."""

from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile


EXPECTED_BRANCH = "main"
EXPECTED_PARENT_HEAD = "f891a33487ea8bc811243627f1d834be7a43f972"
EXPECTED_PARENT_TREE = "f087c3f6cec8caecc19539628b1d4ab08b4918c1"
EXPECTED_PARENT_SUBJECT = "Slice 37G disabled integration and Slice 37 closeout"
EXPECTED_COMMIT_SUBJECT = "Slice 38A action-root and predicate-identity core schema"
EXPECTED_PREDECESSOR_COUNT = 247
EXPECTED_BEHAVIOR_CHECKS = 431

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/__init__.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/authority.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/identity.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/schema.py",
    "aiweb_language_core_bootstrap/predicate_role_frame_registry/validation.py",
    "scripts/AIWEB_SLICE38A_ACTION_ROOT_PREDICATE_SCHEMA_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE38A_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/AIWEB_SLICE38A_SCHEMA_ONLY_AND_DEFERRED_SCOPE_DECISION.md",
    "scripts/README_aiweb_slice38a_action_root_predicate_schema.md",
    "scripts/aiweb_slice38a_action_root_predicate_schema_verify.py",
    "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
)

SOURCE_ONLY_INHERITED_COMMANDS = (
    "scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py",
    "scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
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
    "scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
)

PROHIBITED_IMPORT_ROOTS = {
    "anthropic", "chromadb", "faiss", "gensim", "httpx", "keras",
    "langchain", "llama_index", "nltk", "numpy", "openai", "pandas",
    "requests", "scipy", "sentence_transformers", "sklearn", "spacy",
    "tensorflow", "torch", "transformers", "urllib", "socket", "subprocess",
}
PROHIBITED_SOURCE_TOKENS = (
    "@app.route", "@router.", "FastAPI(", "Flask(", "requests.",
    "urlopen(", "socket.socket(", "subprocess.", "os.system(",
    "openai.", "anthropic.",
)
PROHIBITED_PUBLIC_NAME_FRAGMENTS = (
    "lookup", "resolve", "select", "populate", "assign", "complete_frame",
    "route", "dispatch", "invoke", "execute", "render", "deliver",
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


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(repository), *args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_test(
    command: tuple[str, ...],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    """Capture through temporary files to avoid descendant PIPE retention."""

    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stdout_file:
        with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stderr_file:
            try:
                completed = subprocess.run(
                    command,
                    cwd=str(cwd),
                    env=env,
                    text=True,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    check=False,
                    timeout=300,
                )
                returncode = completed.returncode
                arguments = completed.args
            except subprocess.TimeoutExpired:
                returncode = 124
                arguments = command
                stderr_file.write("test exceeded the 300-second fail-closed timeout\n")
            stdout_file.seek(0)
            stderr_file.seek(0)
            return subprocess.CompletedProcess(
                args=arguments,
                returncode=returncode,
                stdout=stdout_file.read(),
                stderr=stderr_file.read(),
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


def package_files(repository: Path) -> tuple[Path, ...]:
    package = repository / "aiweb_language_core_bootstrap" / "predicate_role_frame_registry"
    return tuple(sorted(package.glob("*.py")))


def import_roots(tree: ast.AST) -> set[str]:
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
    for result, label in ((branch, "branch"), (head, "HEAD"), (tree, "tree"), (subject, "subject")):
        verifier.check(result.returncode == 0, f"git {label} inspection failed")
    if any(result.returncode != 0 for result in (branch, head, tree, subject)):
        return

    verifier.check(branch.stdout.strip() == EXPECTED_BRANCH, "branch mismatch")

    staged = git(repository, "diff", "--cached", "--name-only")
    staged_status = git(repository, "diff", "--cached", "--name-status")
    unstaged = git(repository, "diff", "--name-only")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")
    for result, label in (
        (staged, "staged"), (staged_status, "staged status"),
        (unstaged, "unstaged"), (untracked, "untracked"),
    ):
        verifier.check(result.returncode == 0, f"git {label} inspection failed")
    if any(result.returncode != 0 for result in (staged, staged_status, unstaged, untracked)):
        return

    exact = tuple(sorted(EXACT_PATHS))
    staged_paths = tuple(sorted(line for line in staged.stdout.splitlines() if line))
    unstaged_paths = tuple(sorted(line for line in unstaged.stdout.splitlines() if line))
    untracked_paths = tuple(sorted(line for line in untracked.stdout.splitlines() if line))

    if mode in {"source-only", "applied"}:
        label = mode
        verifier.check(head.stdout.strip() == EXPECTED_PARENT_HEAD, f"{label} HEAD mismatch")
        verifier.check(tree.stdout.strip() == EXPECTED_PARENT_TREE, f"{label} tree mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_PARENT_SUBJECT, f"{label} subject mismatch")
        verifier.check(staged_paths == (), f"{label} staged paths present")
        verifier.check(unstaged_paths == (), f"{label} tracked modifications present")
        verifier.check(untracked_paths == exact, f"{label} untracked path set mismatch")
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
    else:
        parent = git(repository, "rev-parse", "HEAD^")
        status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
        verifier.check(parent.returncode == 0, "committed parent read failed")
        verifier.check(status.returncode == 0, "committed status read failed")
        if parent.returncode == 0:
            verifier.check(parent.stdout.strip() == EXPECTED_PARENT_HEAD, "committed parent mismatch")
        verifier.check(subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT, "committed subject mismatch")
        verifier.check(head.stdout.strip() != EXPECTED_PARENT_HEAD, "committed HEAD did not advance")
        verifier.check(tree.stdout.strip() != EXPECTED_PARENT_TREE, "committed tree did not advance")
        if status.returncode == 0:
            verifier.check(status.stdout.strip() == "", "committed repository is not clean")
        verifier.check(staged_paths == (), "committed staged paths present")
        verifier.check(unstaged_paths == (), "committed unstaged paths present")
        verifier.check(untracked_paths == (), "committed untracked paths present")
        tracked = git(repository, "ls-files", "--", *EXACT_PATHS)
        verifier.check(tracked.returncode == 0, "committed exact path tracking inspection failed")
        if tracked.returncode == 0:
            tracked_paths = tuple(sorted(line for line in tracked.stdout.splitlines() if line))
            verifier.check(tracked_paths == exact, "committed exact path set mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument(
        "--mode",
        choices=("source-only", "applied", "precommit", "committed"),
        default="source-only",
    )
    parser.add_argument("--inherited-shard-index", type=int, default=0)
    parser.add_argument("--inherited-shard-count", type=int, default=1)
    arguments = parser.parse_args()
    if arguments.inherited_shard_count < 1:
        parser.error("--inherited-shard-count must be at least 1")
    if not 0 <= arguments.inherited_shard_index < arguments.inherited_shard_count:
        parser.error("--inherited-shard-index must be within shard count")

    repository = Path(arguments.repository).resolve()
    verifier = Verifier()

    print("AI.WEB SLICE 38A INDEPENDENT VERIFIER")
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
        verifier.check(
            target.is_file() and not target.is_symlink(),
            f"missing or unsafe Slice 38A path: {relative}",
        )

    manifest_path = repository / "scripts/AIWEB_SLICE38A_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    try:
        predecessor_records = parse_manifest(manifest_path)
    except Exception as error:
        verifier.failures.append(str(error))
        predecessor_records = ()

    verifier.check(
        len(predecessor_records) == EXPECTED_PREDECESSOR_COUNT,
        "protected predecessor count mismatch",
    )
    predecessor_paths = tuple(relative for _, relative in predecessor_records)
    verifier.check(len(predecessor_paths) == len(set(predecessor_paths)), "duplicate predecessor paths")
    verifier.check(not (set(predecessor_paths) & set(EXACT_PATHS)), "new Slice 38A paths overlap predecessor manifest")
    for expected, relative in predecessor_records:
        target = repository / relative
        verifier.check(
            target.is_file() and not target.is_symlink(),
            f"protected predecessor missing: {relative}",
        )
        if target.is_file() and not target.is_symlink():
            verifier.check(
                sha256_file(target) == expected,
                f"protected predecessor hash mismatch: {relative}",
            )

    python_files = package_files(repository)
    verifier.check(len(python_files) == 5, "Slice 38A package Python file count mismatch")
    for path in python_files:
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except Exception as error:
            verifier.failures.append(f"Python parse failed for {path.name}: {error}")
            continue

        roots = import_roots(tree)
        verifier.check(not (roots & PROHIBITED_IMPORT_ROOTS), f"prohibited import root in {path.name}")
        verifier.check(not any(token in text for token in PROHIBITED_SOURCE_TOKENS),
                       f"prohibited source token in {path.name}")

        top_level_calls = [
            node for node in tree.body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        ]
        verifier.check(not top_level_calls, f"top-level effect call in {path.name}")

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lowered = node.name.lower()
                verifier.check(
                    not any(fragment in lowered for fragment in PROHIBITED_PUBLIC_NAME_FRAGMENTS),
                    f"authority-bearing public function in {path.name}: {node.name}",
                )

        route_decorators: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                rendered = ast.unparse(decorator).lower()
                if any(marker in rendered for marker in (".route", "@app.", "@router.", "fastapi", "flask")):
                    route_decorators.append(rendered)
        verifier.check(not route_decorators, f"route-like decorator in {path.name}")

    for relative in (
        "scripts/AIWEB_SLICE38A_ACTION_ROOT_PREDICATE_SCHEMA_RUNTIME_SPEC.md",
        "scripts/AIWEB_SLICE38A_SCHEMA_ONLY_AND_DEFERRED_SCOPE_DECISION.md",
        "scripts/README_aiweb_slice38a_action_root_predicate_schema.md",
    ):
        text = (repository / relative).read_text(encoding="utf-8")
        verifier.check("surface verb" in text, f"surface-verb boundary missing from {relative}")
        verifier.check("predicate identity" in text, f"predicate boundary missing from {relative}")
        verifier.check("action" in text and "authority" in text, f"action-authority boundary missing from {relative}")
        verifier.check("CandidateMeaning" in text, f"CandidateMeaning boundary missing from {relative}")
        verifier.check("scale" in text and "authority" in text, f"scale boundary missing from {relative}")

    verify_git_state(repository, arguments.mode, verifier)

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.pop("PYTHONPYCACHEPREFIX", None)

    behavior_path = "scripts/test_aiweb_slice38a_action_root_predicate_schema.py"
    print(f"running_behavior_test={behavior_path}", flush=True)
    behavior = run_test(
        (sys.executable, "-B", behavior_path),
        cwd=repository,
        env=environment,
    )
    print(f"behavior_test_return_code={behavior.returncode}", flush=True)
    verifier.check(behavior.returncode == 0, "Slice 38A behavior test failed")
    verifier.check(f"check_count={EXPECTED_BEHAVIOR_CHECKS}" in behavior.stdout,
                   "Slice 38A behavior check count mismatch")
    verifier.check("AI.WEB SLICE 38A BEHAVIOR TEST: PASS" in behavior.stdout,
                   "Slice 38A behavior pass marker missing")
    verifier.check("registry_entry_count=0" in behavior.stdout,
                   "zero registry marker missing")
    verifier.check("memory_routes_tools_actions_rendering_delivery=0" in behavior.stdout,
                   "zero downstream authority marker missing")

    full_inherited = (
        SOURCE_ONLY_INHERITED_COMMANDS
        if arguments.mode == "source-only"
        else LIVE_INHERITED_COMMANDS
    )
    inherited = tuple(
        command
        for index, command in enumerate(full_inherited)
        if index % arguments.inherited_shard_count == arguments.inherited_shard_index
    )
    print(
        f"inherited_shard={arguments.inherited_shard_index + 1}/"
        f"{arguments.inherited_shard_count}",
        flush=True,
    )
    inherited_batch_size = 4
    for offset in range(0, len(inherited), inherited_batch_size):
        batch = inherited[offset:offset + inherited_batch_size]
        for command in batch:
            print(f"running_inherited_test={command}", flush=True)
            verifier.check(
                (repository / command).is_file(),
                f"inherited test missing: {command}",
            )
        runnable = tuple(command for command in batch if (repository / command).is_file())
        with ThreadPoolExecutor(max_workers=len(runnable) or 1) as executor:
            futures = {
                command: executor.submit(
                    run_test,
                    (sys.executable, "-B", command),
                    cwd=repository,
                    env=environment,
                )
                for command in runnable
            }
            results = {command: futures[command].result() for command in runnable}
        for command in batch:
            if command not in results:
                continue
            result = results[command]
            print(
                f"inherited_test_return_code={result.returncode} path={command}",
                flush=True,
            )
            verifier.check(
                result.returncode == 0,
                f"inherited test failed: {command}",
            )

    cache_artifacts = tuple(
        sorted(
            path.relative_to(repository).as_posix()
            for root in (
                repository / "aiweb_language_core_bootstrap",
                repository / "scripts",
            )
            if root.exists()
            for path in root.rglob("*")
            if "__pycache__" in path.relative_to(repository).parts
            or path.suffix in {".pyc", ".pyo"}
        )
    )
    verifier.check(not cache_artifacts, "repository Python cache artifacts present")

    print(f"pass_count={verifier.passes}")
    print(f"failure_count={len(verifier.failures)}")
    if verifier.failures:
        for failure in verifier.failures:
            print(f"FAIL: {failure}")
        print("SLICE 38A INDEPENDENT VERIFIER: FAIL")
        return 1

    print("SLICE 38A INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(predecessor_records)}")
    print(f"inherited_tests={len(inherited)}")
    print(f"live_required_inherited_tests={len(LIVE_INHERITED_COMMANDS)}")
    print(f"slice38a_files={len(EXACT_PATHS)}")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
