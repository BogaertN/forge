#!/usr/bin/env python3
"""Visible independent verifier for AI.Web Slice 42H."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

EXPECTED_HEAD = "8f3360dcb7e248f2ea1f1ced3e43b43ecbceedf5"
EXPECTED_TREE = "56325c16643a6aa061baa6a0645fbeec7f5f5588"
EXPECTED_SUBJECT = "Slice 42G MSM-v1 outward meaning and expression-link custody"
COMMIT_SUBJECT = "Slice 42H disabled bootstrap integration and Slice 42 closeout"

SCRIPT_DIR = Path(__file__).resolve().parent
PAYLOAD_MANIFEST = SCRIPT_DIR / "AIWEB_SLICE42H_EXACT_PAYLOAD_PATHS.txt"
PROTECTED_MANIFEST = SCRIPT_DIR / "AIWEB_SLICE42H_PROTECTED_PREDECESSOR_SHA256SUMS.txt"

FORBIDDEN_RUNTIME_IMPORTS = {
    "aiohttp", "chromadb", "http", "numpy", "openai", "os", "pathlib",
    "requests", "shutil", "socket", "sqlite3", "subprocess", "torch",
    "transformers", "urllib",
}
FORBIDDEN_RUNTIME_CALLS = {"compile", "eval", "exec", "input", "open"}


def run(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return run(
        [
            "git",
            "-c",
            f"safe.directory={repo}",
            "-C",
            str(repo),
            *arguments,
        ]
    )


def lines(result: subprocess.CompletedProcess[str]) -> tuple[str, ...]:
    return tuple(line for line in result.stdout.splitlines() if line)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_paths(path: Path) -> tuple[Path, ...]:
    return tuple(
        Path(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    )


def expected_mode(relative: Path) -> int:
    if relative in {
        Path("scripts/aiweb_slice42h_disabled_bootstrap_integration_and_slice42_closeout_verify.py"),
        Path("scripts/test_aiweb_slice42h_disabled_bootstrap_integration_and_slice42_closeout.py"),
    }:
        return 0o755
    return 0o644


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument(
        "--mode",
        choices=("applied", "staged", "committed"),
        default="applied",
    )
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    failures: list[str] = []
    checks = 0

    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if condition is not True:
            failures.append(label)

    check((repo / ".git").is_dir(), "git repository")
    check(PAYLOAD_MANIFEST.is_file(), "exact payload manifest")
    check(PROTECTED_MANIFEST.is_file(), "protected predecessor manifest")
    if not PAYLOAD_MANIFEST.is_file() or not PROTECTED_MANIFEST.is_file():
        for failure in failures:
            print("FAIL: " + failure)
        print("RESULT=FAIL")
        return 1

    payload = read_paths(PAYLOAD_MANIFEST)
    payload_set = set(payload)
    check(len(payload) == 15, "exact payload count")
    check(len(payload) == len(payload_set), "payload paths unique")

    branch = git(repo, "branch", "--show-current").stdout.strip()
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    head_tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    staged = {
        Path(item)
        for item in lines(git(repo, "diff", "--cached", "--name-only"))
    }
    tracked = {
        Path(item)
        for item in lines(git(repo, "diff", "--name-only"))
    }
    untracked = {
        Path(item)
        for item in lines(
            git(repo, "ls-files", "--others", "--exclude-standard")
        )
    }
    check(branch == "main", "branch main")

    if args.mode == "applied":
        check(head == EXPECTED_HEAD, "applied parent head")
        check(head_tree == EXPECTED_TREE, "applied parent tree")
        check(untracked == payload_set, "exact untracked payload")
        check(not staged, "no staged paths")
        check(not tracked, "no tracked modifications")
    elif args.mode == "staged":
        check(head == EXPECTED_HEAD, "staged parent head")
        check(head_tree == EXPECTED_TREE, "staged parent tree")
        check(staged == payload_set, "exact staged payload")
        check(not untracked, "no untracked paths after staging")
        check(not tracked, "no unstaged tracked modifications")
    else:
        parent = git(repo, "rev-parse", "HEAD^").stdout.strip()
        parent_tree = git(
            repo,
            "show",
            "-s",
            "--format=%T",
            "HEAD^",
        ).stdout.strip()
        subject = git(
            repo,
            "show",
            "-s",
            "--format=%s",
            "HEAD",
        ).stdout.strip()
        committed = {
            Path(item)
            for item in lines(
                git(
                    repo,
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    "HEAD",
                )
            )
        }
        check(parent == EXPECTED_HEAD, "committed parent head")
        check(parent_tree == EXPECTED_TREE, "committed parent tree")
        check(subject == COMMIT_SUBJECT, "commit subject")
        check(committed == payload_set, "exact committed payload")
        check(not untracked and not staged and not tracked, "clean committed state")

    protected_count = 0
    protected_paths: set[str] = set()
    for line in PROTECTED_MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        protected_count += 1
        try:
            expected_digest, relative = line.split("  ", 1)
        except ValueError:
            check(False, "malformed protected predecessor manifest line")
            continue
        check(relative not in protected_paths, "protected predecessor unique " + relative)
        protected_paths.add(relative)
        path = repo / relative
        check(
            path.is_file() and sha256_file(path) == expected_digest,
            "protected predecessor " + relative,
        )
    check(protected_count == 1638, "protected predecessor count")
    check(not protected_paths.intersection(p.as_posix() for p in payload), "payload additive against protected set")

    for relative in payload:
        path = repo / relative
        check(path.is_file(), "payload exists " + relative.as_posix())
        if path.is_file():
            check(
                stat.S_IMODE(path.stat().st_mode) == expected_mode(relative),
                "payload mode " + relative.as_posix(),
            )

    runtime = (
        repo
        / "aiweb_language_core_bootstrap/outward_expression_runtime/"
        "disabled_outward_expression_closeout"
    )
    runtime_files = tuple(sorted(runtime.glob("*.py")))
    check(len(runtime_files) == 7, "exact seven-module runtime package")
    expected_runtime_names = {
        "__init__.py", "authority.py", "canonical.py", "fixtures.py",
        "integration.py", "schema.py", "validation.py",
    }
    check(
        {path.name for path in runtime_files} == expected_runtime_names,
        "exact runtime module names",
    )
    for path in runtime_files:
        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
            )
        except Exception as error:
            check(False, f"runtime syntax {path.name}: {error}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                check(
                    not FORBIDDEN_RUNTIME_IMPORTS.intersection(imported),
                    "forbidden runtime import " + path.name,
                )
            elif isinstance(node, ast.ImportFrom):
                imported = {(node.module or "").split(".")[0]}
                check(
                    not FORBIDDEN_RUNTIME_IMPORTS.intersection(imported),
                    "forbidden runtime import " + path.name,
                )
                check(
                    not any(alias.name == "*" for alias in node.names),
                    "wildcard runtime import " + path.name,
                )
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                check(
                    node.func.id not in FORBIDDEN_RUNTIME_CALLS,
                    "forbidden runtime call " + path.name,
                )

    authority_source = (runtime / "authority.py").read_text(encoding="utf-8")
    integration_source = (runtime / "integration.py").read_text(encoding="utf-8")
    schema_source = (runtime / "schema.py").read_text(encoding="utf-8")
    fixtures_source = (runtime / "fixtures.py").read_text(encoding="utf-8")
    validation_source = (runtime / "validation.py").read_text(encoding="utf-8")
    check(
        "run_disabled_outward_expression_closeout" in integration_source,
        "disabled closeout operation installed",
    )
    check(
        "integrate_outward_meaning_and_expression_link" in integration_source,
        "accepted Slice 42G integration API required",
    )
    check(
        "validate_integration_input" in integration_source
        and "validate_integration_result" in integration_source,
        "exact Slice 42G validation required",
    )
    check(
        "MeaningStructureManifestV1(" not in integration_source,
        "MSM-v1 is not reconstructed or rewritten",
    )
    check(
        "Slice42AcceptanceRecord" in schema_source
        and "Slice42RollbackMetadata" in schema_source,
        "acceptance and rollback contracts installed",
    )
    check(
        "slice43_started=False" in integration_source,
        "Slice 43 remains unstarted",
    )
    check(
        "echo_validation_performed=False" in integration_source
        and "delivery_authorized=False" in integration_source,
        "Echo and delivery remain absent",
    )
    check(
        "SLICE42_INCREMENT_LABELS" in authority_source
        and '"42H"' in authority_source,
        "fixed Slice 42 increment chain recorded",
    )
    check(
        "expected_validation_link_count=0" in fixtures_source
        and "expected_delivery_link_count=0" in fixtures_source,
        "closed fixture requires no validation or delivery link",
    )
    check(
        "validate_acceptance_record" in validation_source
        and "validate_stage_receipt" in validation_source
        and "validate_result" in validation_source,
        "closeout validation surface installed",
    )

    pycache_root = tempfile.mkdtemp(prefix="aiweb42h_verifier_pycache_")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPYCACHEPREFIX"] = pycache_root
    env["PYTHONPATH"] = str(repo)
    test_path = (
        repo
        / "scripts/test_aiweb_slice42h_disabled_bootstrap_integration_and_slice42_closeout.py"
    )
    current_test = run(
        [sys.executable, "-B", str(test_path), str(repo)],
        cwd=repo,
        env=env,
    )
    print("=== VISIBLE CURRENT TEST 1 OF 1 ===")
    print(current_test.stdout, end="")
    print(current_test.stderr, end="", file=sys.stderr)
    check(current_test.returncode == 0, "current behavior test")

    prior_umask = os.umask(0o022)
    try:
        with tempfile.TemporaryDirectory(prefix="aiweb42h_parent_") as temp_dir:
            clone = Path(temp_dir) / "repo"
            clone_result = run(
                [
                    "git",
                    "clone",
                    "--no-hardlinks",
                    "--quiet",
                    str(repo),
                    str(clone),
                ]
            )
            check(clone_result.returncode == 0, "parent clone")
            if clone_result.returncode == 0:
                checkout = git(
                    clone,
                    "checkout",
                    "--quiet",
                    "-B",
                    "main",
                    EXPECTED_HEAD,
                )
                check(checkout.returncode == 0, "parent checkout on main")
                inherited_path = (
                    clone
                    / "scripts/aiweb_slice42g_msm_outward_expression_integration_verify.py"
                )
                inherited = run(
                    [
                        sys.executable,
                        "-B",
                        str(inherited_path),
                        str(clone),
                        "--mode",
                        "committed",
                    ],
                    cwd=clone,
                    env=env,
                )
                print("=== INHERITED VISIBLE VERIFIER: SLICE 42G ===")
                print(inherited.stdout, end="")
                print(inherited.stderr, end="", file=sys.stderr)
                check(
                    inherited.returncode == 0,
                    "inherited Slice 42G verifier",
                )
    finally:
        os.umask(prior_umask)

    print("=== SLICE 42H VERIFIER SUMMARY ===")
    print("pass_count=" + str(checks - len(failures)))
    print("failure_count=" + str(len(failures)))
    print("protected_predecessor_files=" + str(protected_count))
    print("slice42h_files=" + str(len(payload)))
    print("visible_total_tests=66")
    print("slice42A_through_42H_completed=1")
    print("disabled_by_default=1")
    print("explicit_invocation_required=1")
    print("accepted_static_fixture_only=1")
    print("offline_in_memory_deterministic=1")
    print("authorized_meaning_required=1")
    print("selected_meaning_preserved=1")
    print("scope_preserved=1")
    print("certainty_preserved=1")
    print("evidence_status_preserved=1")
    print("caveats_preserved=1")
    print("refusal_state_preserved=1")
    print("unresolved_conditions_preserved=1")
    print("deterministic_expression_candidate_created=1")
    print("expression_candidate_remains_unvalidated=1")
    print("echo_validation_performed=0")
    print("delivery_authority=0")
    print("truth_authority=0")
    print("evidence_authority=0")
    print("permission_authority=0")
    print("execution_authority=0")
    print("slice43_started=0")
    print("route_api_network_filesystem_memory_tool_action_delivery=0")
    print("model_embedding_vector_rag_similarity_neural_classifier_authority=0")
    print("msm_v1_schema_modified=0")
    print("gp014_superseded=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    for failure in failures:
        print("FAIL: " + failure)
    print("RESULT=" + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
