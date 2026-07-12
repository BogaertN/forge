#!/usr/bin/env python3
"""Verify Slice 19 RMC Echo Boundary Scaffold.

The verifier accepts two lawful repository contexts:
1. Pre-commit patch context at accepted Slice 18R1 HEAD with dirty status limited
   to the Slice 19 payload paths.
2. Clean committed context where the accepted Slice 18R1 HEAD is an ancestor and
   a commit with the Slice 19 subject introduces exactly the Slice 19 payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

EXPECTED_BASE_HEAD = "9af49a428c9fd87f16a1a03b98947aada6c55b6c"
EXPECTED_BASE_SUBJECT = "Slice 18R1 verifier context correction"
EXPECTED_SLICE19_SUBJECT = "Slice 19 RMC Echo boundary scaffold"

PAYLOAD_PATHS = (
    "aiweb_rmc_echo_boundary_scaffold/__init__.py",
    "aiweb_rmc_echo_boundary_scaffold/authority.py",
    "aiweb_rmc_echo_boundary_scaffold/boundary.py",
    "aiweb_rmc_echo_boundary_scaffold/core.py",
    "aiweb_rmc_echo_boundary_scaffold/receipt.py",
    "aiweb_rmc_echo_boundary_scaffold/verify.py",
    "scripts/README_aiweb_slice19_rmc_echo_boundary_scaffold.md",
    "scripts/aiweb_slice19_rmc_echo_boundary_verify.py",
    "scripts/test_aiweb_slice19_rmc_echo_boundary_scaffold.py",
)

PACKAGE_DIR = "aiweb_rmc_echo_boundary_scaffold"
FORBIDDEN_REPO_PATH_PREFIXES = (
    "aiweb_gp014",
    "gp014",
    "gp015",
    "renderer",
    "delivery",
    "release",
)


def run_git(repo: Path, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode, result.stdout.rstrip("\n"), result.stderr.rstrip("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def status_paths(repo: Path) -> tuple[list[tuple[str, str]], list[str]]:
    code, out, err = run_git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if code != 0:
        return [], ["git status failed: " + err]
    parsed: list[tuple[str, str]] = []
    for line in out.splitlines():
        if not line:
            continue
        parsed.append((line[:2], line[3:]))
    return parsed, []


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    code, _, _ = run_git(repo, "merge-base", "--is-ancestor", ancestor, descendant)
    return code == 0


def find_slice19_commit(repo: Path, head: str) -> tuple[str | None, list[str]]:
    code, out, err = run_git(repo, "rev-list", "--reverse", f"{EXPECTED_BASE_HEAD}..{head}")
    if code != 0:
        return None, ["could not list commits after Slice 18R1 base: " + err]

    failures: list[str] = []
    for commit in [line for line in out.splitlines() if line.strip()]:
        code_subject, subject, err_subject = run_git(repo, "log", "-1", "--pretty=%s", commit)
        if code_subject != 0:
            failures.append("could not read subject for commit " + commit + ": " + err_subject)
            continue
        if subject != EXPECTED_SLICE19_SUBJECT:
            continue

        code_paths, paths, err_paths = run_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit)
        if code_paths != 0:
            failures.append("could not read Slice 19 commit paths: " + err_paths)
            continue
        if tuple(sorted(paths.splitlines())) == tuple(sorted(PAYLOAD_PATHS)):
            return commit, failures
        failures.append("Slice 19 subject commit exists but paths did not match exact payload")

    return None, failures


def classify_repo_context(repo: Path) -> tuple[str, list[str]]:
    failures: list[str] = []

    code_root, root, err_root = run_git(repo, "rev-parse", "--show-toplevel")
    if code_root != 0:
        return "invalid_repository", ["could not resolve repository root: " + err_root]
    if Path(root).resolve() != repo.resolve():
        failures.append("repository root mismatch")

    code_branch, branch, err_branch = run_git(repo, "branch", "--show-current")
    if code_branch != 0:
        failures.append("could not read branch: " + err_branch)
    elif branch != "main":
        failures.append("branch is not main")

    code_head, head, err_head = run_git(repo, "rev-parse", "HEAD")
    if code_head != 0:
        return "invalid_repository", failures + ["could not read HEAD: " + err_head]

    statuses, status_failures = status_paths(repo)
    failures.extend(status_failures)
    status_path_set = {path for _, path in statuses}
    payload_set = set(PAYLOAD_PATHS)

    for _, path in statuses:
        if path not in payload_set:
            failures.append("status path outside Slice 19 payload: " + path)

    if head == EXPECTED_BASE_HEAD:
        code_subject, subject, err_subject = run_git(repo, "log", "-1", "--pretty=%s")
        if code_subject != 0:
            failures.append("could not read base subject: " + err_subject)
        elif subject != EXPECTED_BASE_SUBJECT:
            failures.append("base subject mismatch")

        missing_files = [rel for rel in PAYLOAD_PATHS if not (repo / rel).is_file()]
        if missing_files:
            failures.append("missing Slice 19 payload files: " + ", ".join(missing_files))

        if statuses:
            if not status_path_set.issubset(payload_set):
                failures.append("dirty paths are not limited to Slice 19 payload")
            return "slice19_precommit_patch_context", failures

        return "slice18r1_clean_base_without_slice19_payload", failures + [
            "Slice 19 payload is not applied yet"
        ]

    if not is_ancestor(repo, EXPECTED_BASE_HEAD, head):
        failures.append("Slice 18R1 base is not an ancestor of HEAD")
        return "unexpected_history", failures

    if statuses:
        failures.append("post-Slice19 descendant working tree is not clean")
        return "post_slice19_dirty_descendant", failures

    slice19_commit, find_failures = find_slice19_commit(repo, head)
    failures.extend(find_failures)
    if slice19_commit is None:
        failures.append("no exact Slice 19 commit found after Slice 18R1 base")
        return "post_slice18r1_clean_without_slice19_commit", failures

    return "slice19_or_later_clean_committed_context", failures


def import_and_verify(repo: Path) -> list[str]:
    failures: list[str] = []
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    try:
        from aiweb_rmc_echo_boundary_scaffold.verify import verify_slice19_invariants
    except Exception as exc:
        return ["could not import Slice 19 verifier: " + repr(exc)]

    package_root = repo / PACKAGE_DIR
    failures.extend(verify_slice19_invariants(package_root=package_root))
    return failures


def repo_payload_file_checks(repo: Path) -> list[str]:
    failures: list[str] = []
    for rel in PAYLOAD_PATHS:
        path = repo / rel
        if not path.is_file():
            failures.append("missing payload path: " + rel)
            continue
        if rel.endswith(".py"):
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except Exception as exc:
                failures.append("payload syntax failure: " + rel + ": " + repr(exc))

    for rel in PAYLOAD_PATHS:
        for prefix in FORBIDDEN_REPO_PATH_PREFIXES:
            if rel.startswith(prefix + "/") or rel == prefix:
                failures.append("payload path violates boundary prefix: " + rel)
    return failures


def build_report(repo: Path) -> dict[str, object]:
    failures: list[str] = []
    context_label, context_failures = classify_repo_context(repo)
    failures.extend(context_failures)
    failures.extend(repo_payload_file_checks(repo))
    failures.extend(import_and_verify(repo))

    return {
        "verifier": "scripts/aiweb_slice19_rmc_echo_boundary_verify.py",
        "expected_base_head": EXPECTED_BASE_HEAD,
        "expected_slice19_subject": EXPECTED_SLICE19_SUBJECT,
        "context_label": context_label,
        "payload_path_count": len(PAYLOAD_PATHS),
        "failure_count": len(failures),
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Slice 19 RMC Echo Boundary Scaffold")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    report = build_report(repo)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("=== AI.WEB SLICE 19 RMC ECHO BOUNDARY VERIFY ===")
        print("context_label=" + str(report["context_label"]))
        print("payload_path_count=" + str(report["payload_path_count"]))
        print("failure_count=" + str(report["failure_count"]))
        for failure in report["failures"]:
            print("FAIL - " + str(failure))
        print("VERDICT: " + str(report["verdict"]))

    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
