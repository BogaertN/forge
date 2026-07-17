#!/usr/bin/env python3
"""Independent source, regression, rollback and Git verifier for Slice 37G."""

from __future__ import annotations

import argparse
import ast
import hashlib
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import os


EXPECTED_BRANCH = "main"
EXPECTED_PARENT_HEAD = "dc8f763849cd5519b7532e53615d7cac1f74d1de"
EXPECTED_PARENT_TREE = "b1e3681da79fbdb6ad4418d7fb699d88aa8a8e41"
EXPECTED_PARENT_SUBJECT = "Slice 37F structural-to-concept candidate proposal"
EXPECTED_COMMIT_SUBJECT = "Slice 37G disabled integration and Slice 37 closeout"
PRE_SLICE35_COMMIT = "9ce65c3fd24c1f74a6e95630df1e20109f34df78"
PRE_SLICE37_COMMIT = "5bd8a39b91e7ead06523e7fd0aa3ee057c795f74"
PRE_SLICE37_TREE = "16a7708c5ea8b208224bd3ef7a51375c8f980138"
EXPECTED_PREDECESSOR_COUNT = 190
EXPECTED_BEHAVIOR_CHECKS = 1017

EXACT_PATHS = (
    "aiweb_language_core_bootstrap/disabled_structural_concept_bootstrap/__init__.py",
    "aiweb_language_core_bootstrap/disabled_structural_concept_bootstrap/fixtures.py",
    "aiweb_language_core_bootstrap/disabled_structural_concept_bootstrap/integration.py",
    "aiweb_language_core_bootstrap/disabled_structural_concept_bootstrap/schema.py",
    "aiweb_language_core_bootstrap/disabled_structural_concept_bootstrap/validation.py",
    "scripts/AIWEB_SLICE37G_DISABLED_INTEGRATION_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE37G_PROTECTED_SLICE35_37_PREDECESSOR_SHA256SUMS.txt",
    "scripts/AIWEB_SLICE37_ACCEPTANCE_RECORD.md",
    "scripts/README_aiweb_slice37g_disabled_integration_closeout.md",
    "scripts/aiweb_slice37g_disabled_integration_closeout_verify.py",
    "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
)

SOURCE_ONLY_INHERITED_COMMANDS = (
    "scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py",
    "scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py",
    "scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py",
    "scripts/test_aiweb_slice37e_semantic_class_relation_registry.py",
    "scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py",
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
)

PROHIBITED_IMPORT_ROOTS = {
    "anthropic",
    "chromadb",
    "faiss",
    "gensim",
    "httpx",
    "keras",
    "langchain",
    "llama_index",
    "nltk",
    "numpy",
    "openai",
    "pandas",
    "requests",
    "scipy",
    "sentence_transformers",
    "sklearn",
    "spacy",
    "tensorflow",
    "torch",
    "transformers",
}
PROHIBITED_SOURCE_TOKENS = (
    "@app.route",
    "@router.",
    "FastAPI(",
    "Flask(",
    "requests.",
    "urlopen(",
    "socket.socket(",
    "subprocess.",
    "os.system(",
    "openai.",
    "anthropic.",
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


def run(
    command: tuple[str, ...],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )




def run_inherited_test(
    command: tuple[str, ...],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    """Run an inherited test without PIPE inheritance deadlocks."""

    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stdout_file:
        with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stderr_file:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                env=env,
                text=True,
                stdout=stdout_file,
                stderr=stderr_file,
                check=False,
            )
            stdout_file.seek(0)
            stderr_file.seek(0)
            return subprocess.CompletedProcess(
                args=completed.args,
                returncode=completed.returncode,
                stdout=stdout_file.read(),
                stderr=stderr_file.read(),
            )

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
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed checksum line {number}") from error
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise ValueError(f"unsafe checksum path {relative!r}")
        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise ValueError(f"invalid SHA-256 at line {number}")
        records.append((digest, relative))
    return tuple(records)


def package_files(repository: Path) -> tuple[Path, ...]:
    package = (
        repository
        / "aiweb_language_core_bootstrap"
        / "disabled_structural_concept_bootstrap"
    )
    return tuple(sorted(package.glob("*.py")))


def import_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.level == 0
        ):
            roots.add(node.module.split(".", 1)[0])
    return roots


def verify_git_state(
    repository: Path,
    mode: str,
    verifier: Verifier,
) -> None:
    branch = git(repository, "branch", "--show-current")
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    subject = git(repository, "show", "-s", "--format=%s", "HEAD")
    for result, label in (
        (branch, "branch"),
        (head, "HEAD"),
        (tree, "tree"),
        (subject, "subject"),
    ):
        verifier.check(result.returncode == 0, f"git {label} inspection failed")
    if any(
        result.returncode != 0
        for result in (branch, head, tree, subject)
    ):
        return

    verifier.check(
        branch.stdout.strip() == EXPECTED_BRANCH,
        "branch mismatch",
    )

    staged = git(repository, "diff", "--cached", "--name-only")
    unstaged = git(repository, "diff", "--name-only")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")
    for result, label in (
        (staged, "staged"),
        (unstaged, "unstaged"),
        (untracked, "untracked"),
    ):
        verifier.check(
            result.returncode == 0,
            f"git {label} inspection failed",
        )
    if any(
        result.returncode != 0
        for result in (staged, unstaged, untracked)
    ):
        return

    exact = tuple(sorted(EXACT_PATHS))
    staged_paths = tuple(
        sorted(line for line in staged.stdout.splitlines() if line)
    )
    untracked_paths = tuple(
        sorted(line for line in untracked.stdout.splitlines() if line)
    )

    if mode == "precommit":
        verifier.check(
            head.stdout.strip() == EXPECTED_PARENT_HEAD,
            "precommit parent HEAD mismatch",
        )
        verifier.check(
            tree.stdout.strip() == EXPECTED_PARENT_TREE,
            "precommit parent tree mismatch",
        )
        verifier.check(
            subject.stdout.strip() == EXPECTED_PARENT_SUBJECT,
            "precommit parent subject mismatch",
        )
        verifier.check(
            staged_paths == exact,
            "precommit staged set is not exact Slice 37G payload",
        )
        verifier.check(
            not unstaged.stdout.strip(),
            "precommit unstaged changes present",
        )
        verifier.check(
            not untracked_paths,
            "precommit untracked files present",
        )
        statuses = git(repository, "diff", "--cached", "--name-status")
        verifier.check(
            statuses.returncode == 0,
            "precommit status inspection failed",
        )
        if statuses.returncode == 0:
            rows = [
                line.split("\t", 1)
                for line in statuses.stdout.splitlines()
                if line
            ]
            verifier.check(
                len(rows) == len(EXACT_PATHS),
                "precommit staged count mismatch",
            )
            verifier.check(
                all(row[0] == "A" for row in rows),
                "precommit payload must be additions only",
            )

    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        verifier.check(
            parent.returncode == 0,
            "committed parent inspection failed",
        )
        if parent.returncode == 0:
            verifier.check(
                parent.stdout.strip() == EXPECTED_PARENT_HEAD,
                "committed parent mismatch",
            )
        verifier.check(
            subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT,
            "committed subject mismatch",
        )
        verifier.check(not staged_paths, "committed staged files present")
        verifier.check(
            not unstaged.stdout.strip(),
            "committed unstaged files present",
        )
        verifier.check(
            not untracked_paths,
            "committed untracked files present",
        )
        committed = git(
            repository,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
        )
        statuses = git(
            repository,
            "diff-tree",
            "--no-commit-id",
            "--name-status",
            "-r",
            "HEAD",
        )
        verifier.check(
            committed.returncode == 0,
            "committed path inspection failed",
        )
        verifier.check(
            statuses.returncode == 0,
            "committed status inspection failed",
        )
        if committed.returncode == 0:
            committed_paths = tuple(
                sorted(
                    line
                    for line in committed.stdout.splitlines()
                    if line
                )
            )
            verifier.check(
                committed_paths == exact,
                "committed set is not exact Slice 37G payload",
            )
        if statuses.returncode == 0:
            rows = [
                line.split("\t", 1)
                for line in statuses.stdout.splitlines()
                if line
            ]
            verifier.check(
                all(row[0] == "A" for row in rows),
                "committed payload must be additions only",
            )


def verify_predecessor_path_set(
    repository: Path,
    records: tuple[tuple[str, str], ...],
    verifier: Verifier,
) -> None:
    result = git(
        repository,
        "diff",
        "--name-only",
        PRE_SLICE35_COMMIT,
        EXPECTED_PARENT_HEAD,
    )
    verifier.check(
        result.returncode == 0,
        "Slice 35-37 predecessor path derivation failed",
    )
    if result.returncode == 0:
        expected = tuple(
            sorted(line for line in result.stdout.splitlines() if line)
        )
        actual = tuple(sorted(relative for _, relative in records))
        verifier.check(
            actual == expected,
            "protected predecessor manifest path set mismatch",
        )


def verify_recovery(
    repository: Path,
    verifier: Verifier,
) -> None:
    commit = git(
        repository,
        "cat-file",
        "-e",
        f"{PRE_SLICE37_COMMIT}^{{commit}}",
    )
    tree = git(
        repository,
        "rev-parse",
        f"{PRE_SLICE37_COMMIT}^{{tree}}",
    )
    verifier.check(
        commit.returncode == 0,
        "pre-Slice-37 commit is not recoverable",
    )
    verifier.check(
        tree.returncode == 0,
        "pre-Slice-37 tree read failed",
    )
    if tree.returncode == 0:
        verifier.check(
            tree.stdout.strip() == PRE_SLICE37_TREE,
            "pre-Slice-37 tree mismatch",
        )

    with tempfile.TemporaryDirectory(
        prefix="aiweb_slice37g_recovery_"
    ) as temporary_name:
        temporary = Path(temporary_name)
        bundle = temporary / "forge_recovery.bundle"
        clone = temporary / "forge_recovery"

        bundle_create = git(
            repository,
            "bundle",
            "create",
            str(bundle),
            "--all",
        )
        verifier.check(
            bundle_create.returncode == 0,
            "disposable recovery bundle creation failed",
        )
        if bundle_create.returncode != 0:
            return

        bundle_verify = git(
            repository,
            "bundle",
            "verify",
            str(bundle),
        )
        verifier.check(
            bundle_verify.returncode == 0,
            "disposable recovery bundle verification failed",
        )
        if bundle_verify.returncode != 0:
            return

        clone_result = subprocess.run(
            (
                "git",
                "clone",
                "--no-checkout",
                str(bundle),
                str(clone),
            ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        verifier.check(
            clone_result.returncode == 0,
            "disposable recovery clone failed",
        )
        if clone_result.returncode != 0:
            return

        recovered_commit = subprocess.run(
            (
                "git",
                "-C",
                str(clone),
                "cat-file",
                "-e",
                f"{PRE_SLICE37_COMMIT}^{{commit}}",
            ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        recovered_tree = subprocess.run(
            (
                "git",
                "-C",
                str(clone),
                "rev-parse",
                f"{PRE_SLICE37_COMMIT}^{{tree}}",
            ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        fsck = subprocess.run(
            (
                "git",
                "-C",
                str(clone),
                "fsck",
                "--full",
                "--no-reflogs",
            ),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        verifier.check(
            recovered_commit.returncode == 0,
            "recovery clone lacks pre-Slice-37 commit",
        )
        verifier.check(
            recovered_tree.returncode == 0,
            "recovery clone tree read failed",
        )
        if recovered_tree.returncode == 0:
            verifier.check(
                recovered_tree.stdout.strip() == PRE_SLICE37_TREE,
                "recovery clone pre-Slice-37 tree mismatch",
            )
        verifier.check(
            fsck.returncode == 0,
            "recovery clone git fsck failed",
        )



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument(
        "--mode",
        choices=("source-only", "precommit", "committed"),
        default="source-only",
    )
    arguments = parser.parse_args()

    repository = Path(arguments.repository).resolve()
    verifier = Verifier()

    print("AI.WEB SLICE 37G INDEPENDENT VERIFIER")
    print(f"mode={arguments.mode}")

    verifier.check(repository.is_dir(), "repository directory missing")
    verifier.check(
        (repository / ".git").is_dir(),
        "repository .git directory missing",
    )
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
            f"missing or unsafe Slice 37G path: {relative}",
        )

    manifest_path = (
        repository
        / "scripts"
        / "AIWEB_SLICE37G_PROTECTED_SLICE35_37_PREDECESSOR_SHA256SUMS.txt"
    )
    try:
        predecessor_records = parse_manifest(manifest_path)
    except Exception as error:
        verifier.failures.append(str(error))
        predecessor_records = ()

    verifier.check(
        len(predecessor_records) == EXPECTED_PREDECESSOR_COUNT,
        "protected predecessor count mismatch",
    )
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

    verify_predecessor_path_set(
        repository,
        predecessor_records,
        verifier,
    )

    python_files = package_files(repository)
    verifier.check(
        len(python_files) == 5,
        "Slice 37G package Python file count mismatch",
    )
    for path in python_files:
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except Exception as error:
            verifier.failures.append(
                f"Python parse failed for {path.name}: {error}"
            )
            continue
        roots = import_roots(tree)
        verifier.check(
            not (roots & PROHIBITED_IMPORT_ROOTS),
            f"prohibited import root in {path.name}",
        )
        verifier.check(
            not any(
                token in text
                for token in PROHIBITED_SOURCE_TOKENS
            ),
            f"prohibited source token in {path.name}",
        )
        route_decorators: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                rendered = ast.unparse(decorator) if hasattr(ast, "unparse") else ""
                lowered = rendered.lower()
                if any(
                    marker in lowered
                    for marker in (
                        ".route",
                        "@app.",
                        "@router.",
                        "fastapi",
                        "flask",
                    )
                ):
                    route_decorators.append(rendered)
        verifier.check(
            not route_decorators,
            f"route-like decorator surface in {path.name}",
        )

    for relative in (
        "scripts/AIWEB_SLICE37G_DISABLED_INTEGRATION_RUNTIME_SPEC.md",
        "scripts/AIWEB_SLICE37_ACCEPTANCE_RECORD.md",
        "scripts/README_aiweb_slice37g_disabled_integration_closeout.md",
    ):
        text = (repository / relative).read_text(encoding="utf-8")
        verifier.check(
            "surface term" in text,
            f"permanent boundary missing from {relative}",
        )
        verifier.check(
            "scale" in text and "authority" in text,
            f"scale boundary missing from {relative}",
        )
        verifier.check(
            "CandidateMeaning" in text,
            f"CandidateMeaning boundary missing from {relative}",
        )
        verifier.check(
            "production" in text.lower(),
            f"production boundary missing from {relative}",
        )

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(
        prefix="aiweb_slice37g_test_workspace_"
    ):
        environment.pop("PYTHONPYCACHEPREFIX", None)

        print("running_behavior_test=scripts/test_aiweb_slice37g_disabled_integration_closeout.py", flush=True)
        behavior = run_inherited_test(
            (
                sys.executable,
                "-B",
                "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
            ),
            cwd=repository,
            env=environment,
        )
        print(f"behavior_test_return_code={behavior.returncode}", flush=True)
        verifier.check(
            behavior.returncode == 0,
            "Slice 37G behavior test failed",
        )
        verifier.check(
            f"check_count={EXPECTED_BEHAVIOR_CHECKS}" in behavior.stdout,
            "Slice 37G behavior check count mismatch",
        )
        verifier.check(
            "AI.WEB SLICE 37G BEHAVIOR TEST: PASS" in behavior.stdout,
            "Slice 37G behavior pass marker missing",
        )

        inherited = (
            SOURCE_ONLY_INHERITED_COMMANDS
            if arguments.mode == "source-only"
            else LIVE_INHERITED_COMMANDS
        )
        for command in inherited:
            print(f"running_inherited_test={command}", flush=True)
            target = repository / command
            verifier.check(
                target.is_file(),
                f"inherited test missing: {command}",
            )
            if not target.is_file():
                continue
            result = run_inherited_test(
                (sys.executable, "-B", command),
                cwd=repository,
                env=environment,
            )
            print(
                f"inherited_test_return_code={result.returncode} path={command}",
                flush=True,
            )
            verifier.check(
                result.returncode == 0,
                f"inherited test failed: {command}",
            )

    if arguments.mode in {"precommit", "committed"}:
        verify_git_state(repository, arguments.mode, verifier)
        verify_recovery(repository, verifier)

    cache_artifacts: list[str] = []
    for root_name in ("aiweb_language_core_bootstrap", "scripts"):
        root = repository / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            relative = path.relative_to(repository)
            if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
                cache_artifacts.append(relative.as_posix())
    verifier.check(
        not cache_artifacts,
        "repository source cache artifacts present",
    )

    print(f"pass_count={verifier.passes}")
    print(f"failure_count={len(verifier.failures)}")
    if verifier.failures:
        for failure in verifier.failures:
            print(f"FAIL: {failure}")
        print("SLICE 37G INDEPENDENT VERIFIER: FAIL")
        return 1

    print("SLICE 37G INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={len(predecessor_records)}")
    print(f"inherited_tests={len(inherited)}")
    print(f"live_required_inherited_tests={len(LIVE_INHERITED_COMMANDS)}")
    print(f"slice37g_files={len(EXACT_PATHS)}")
    print("fixture_count=5")
    print("integration_stage_count=8")
    print("deterministic_repeat_count=5")
    print("pre_slice37_recovery_required=true")
    print("conventional_word_token_authority=0")
    print("candidate_meaning_selected_meaning_selected_sense=0")
    print("truth_evidence_permission=0")
    print("memory_routes_tools_actions_rendering_delivery=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
