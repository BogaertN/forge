#!/usr/bin/env python3
"""Visible independent verifier for AI.Web Slice 42D."""

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


EXPECTED_HEAD = "b6f19dc58d56eb34044630efac2540306e855ffa"
EXPECTED_TREE = "7fd6ec02fce4a258bf4c3ed1347ae8ce7010992b"
EXPECTED_SUBJECT = (
    "Slice 42C authorized meaning admission and expression eligibility"
)
COMMIT_SUBJECT = "Slice 42D preservation obligation projection"

SCRIPT_DIR = Path(__file__).resolve().parent
PAYLOAD_MANIFEST = SCRIPT_DIR / "AIWEB_SLICE42D_EXACT_PAYLOAD_PATHS.txt"
PROTECTED_MANIFEST = (
    SCRIPT_DIR / "AIWEB_SLICE42D_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
)

FORBIDDEN_RUNTIME_IMPORTS = {
    "aiohttp",
    "chromadb",
    "http",
    "numpy",
    "openai",
    "os",
    "pathlib",
    "requests",
    "shutil",
    "socket",
    "sqlite3",
    "subprocess",
    "torch",
    "transformers",
    "urllib",
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
    check(len(payload) == 15, "exact payload count")
    check(len(payload) == len(set(payload)), "payload paths unique")

    branch = git(repo, "branch", "--show-current").stdout.strip()
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    head_tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    staged = set(Path(item) for item in lines(git(repo, "diff", "--cached", "--name-only")))
    tracked = set(Path(item) for item in lines(git(repo, "diff", "--name-only")))
    untracked = set(
        Path(item)
        for item in lines(
            git(repo, "ls-files", "--others", "--exclude-standard")
        )
    )

    check(branch == "main", "branch main")

    if args.mode == "applied":
        check(head == EXPECTED_HEAD, "applied parent head")
        check(head_tree == EXPECTED_TREE, "applied parent tree")
        check(untracked == set(payload), "exact untracked payload")
        check(not staged, "no staged paths")
        check(not tracked, "no tracked modifications")
    elif args.mode == "staged":
        check(head == EXPECTED_HEAD, "staged parent head")
        check(head_tree == EXPECTED_TREE, "staged parent tree")
        check(staged == set(payload), "exact staged payload")
        check(not untracked, "no untracked paths after staging")
        check(not tracked, "no unstaged tracked modifications")
    else:
        parent = git(repo, "rev-parse", "HEAD^").stdout.strip()
        parent_tree = git(repo, "show", "-s", "--format=%T", "HEAD^").stdout.strip()
        subject = git(repo, "show", "-s", "--format=%s", "HEAD").stdout.strip()
        committed = set(
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
        )
        check(parent == EXPECTED_HEAD, "committed parent head")
        check(parent_tree == EXPECTED_TREE, "committed parent tree")
        check(subject == COMMIT_SUBJECT, "commit subject")
        check(committed == set(payload), "exact committed payload")
        check(not untracked and not staged and not tracked, "clean committed state")

    protected_count = 0
    for line in PROTECTED_MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        protected_count += 1
        try:
            expected_digest, relative = line.split("  ", 1)
        except ValueError:
            check(False, "malformed protected predecessor manifest line")
            continue
        path = repo / relative
        check(
            path.is_file() and sha256_file(path) == expected_digest,
            "protected predecessor " + relative,
        )
    check(protected_count == 1578, "protected predecessor count")

    for relative in payload:
        path = repo / relative
        check(path.is_file(), "payload exists " + relative.as_posix())
        if not path.is_file():
            continue
        expected_mode = (
            0o755
            if relative.suffix == ".py"
            and relative.name.startswith(("test_", "aiweb_slice42d_"))
            else 0o644
        )
        check(
            stat.S_IMODE(path.stat().st_mode) == expected_mode,
            "payload mode " + relative.as_posix(),
        )

    runtime = (
        repo
        / "aiweb_language_core_bootstrap/outward_expression_runtime/"
        "preservation_obligation_projection"
    )
    runtime_files = tuple(sorted(runtime.glob("*.py")))
    check(len(runtime_files) == 7, "exact seven-module runtime package")

    for path in runtime_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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

    pycache_root = tempfile.mkdtemp(prefix="aiweb42d_verifier_pycache_")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPYCACHEPREFIX"] = pycache_root
    env["PYTHONPATH"] = str(repo)

    test_path = repo / "scripts/test_aiweb_slice42d_preservation_obligation_projection.py"
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
        with tempfile.TemporaryDirectory(prefix="aiweb42d_parent_") as temp_dir:
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
                checkout = git(clone, "checkout", "--quiet", "-B", "main", EXPECTED_HEAD)
                check(checkout.returncode == 0, "parent checkout on main")
                inherited_path = (
                    clone
                    / "scripts/aiweb_slice42c_authorized_meaning_admission_"
                    "expression_eligibility_verify.py"
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
                print("=== INHERITED VISIBLE VERIFIER: SLICE 42C ===")
                print(inherited.stdout, end="")
                print(inherited.stderr, end="", file=sys.stderr)
                check(
                    inherited.returncode == 0,
                    "inherited Slice 42C verifier",
                )
    finally:
        os.umask(prior_umask)

    print("=== SLICE 42D VERIFIER SUMMARY ===")
    print("pass_count=" + str(checks - len(failures)))
    print("failure_count=" + str(len(failures)))
    print("protected_predecessor_files=" + str(protected_count))
    print("slice42d_files=" + str(len(payload)))
    print("visible_total_tests=62")
    print("exact_slice42c_state_required=1")
    print("separate_projection_authority_required=1")
    print("preservation_obligations_projected=1")
    print("obligation_package_created=1")
    print("selected_meaning_scope_certainty_evidence_preserved=1")
    print("limitations_caveats_refusal_unresolved_preserved=1")
    print("ambiguity_and_unsupported_states_preserved=1")
    print("memory_resource_delivery_status_preserved=1")
    print("governed_outward_meaning_created=0")
    print("expression_plan_or_text_created=0")
    print("echo_validation_delivery_action=0")
    print("memory_or_external_resource_operation=0")
    print("model_or_similarity_authority=0")
    print("gp014_superseded=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    for failure in failures:
        print("FAIL: " + failure)
    print("RESULT=" + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
