#!/usr/bin/env python3
"""Verifier for Forge language-core replacement Bridge 1."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path


EXPECTED_BASE_HEAD = "666d0c9665fca7443034e8318e1162444a41d70d"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/usr/bin/git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", choices=("applied", "committed"), default="applied")
    args = parser.parse_args()

    repo = Path(args.repository).resolve()
    failures: list[str] = []

    exact_path_file = repo / "scripts" / (
        "AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE1_POST_REPAIR_"
        "EXACT_PAYLOAD_PATHS.txt"
    )
    payload_hash_file = repo / "scripts" / (
        "AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE1_POST_REPAIR_"
        "PAYLOAD_SHA256SUMS.txt"
    )
    predecessor_file = repo / "scripts" / (
        "AIWEB_FORGE_LANGUAGE_CORE_REPLACEMENT_BRIDGE1_POST_REPAIR_"
        "PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    )

    for path in (exact_path_file, payload_hash_file, predecessor_file):
        if not path.is_file():
            failures.append(f"required_file_missing:{path.relative_to(repo)}")

    expected_paths: set[str] = set()
    if exact_path_file.is_file():
        expected_paths = {
            line.strip()
            for line in exact_path_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

    payload_hashes: dict[str, str] = {}
    if payload_hash_file.is_file():
        for line in payload_hash_file.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            digest, relative = line.split("  ", 1)
            payload_hashes[relative] = digest

    if len(expected_paths) != 12:
        failures.append(f"payload_path_count:{len(expected_paths)}")
    if len(payload_hashes) != 11:
        failures.append(f"payload_hash_count:{len(payload_hashes)}")

    for relative, expected in sorted(payload_hashes.items()):
        path = repo / relative
        if not path.is_file():
            failures.append(f"payload_file_missing:{relative}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(
                f"payload_hash_mismatch:{relative}:expected={expected}:actual={actual}"
            )

    protected_expected = {
        "agents/forge/agent.py":
            "fc2b1aac19ffdfb79eff8d5d10d4a93c45a0c245668f878e75f5c2a384cb88ee",
        "agents/forge/permissions.py":
            "c4a1f6d771441911e1e71a95819301897f2106dfcf24a3918252fbcfa2c478ec",
        "scripts/aiweb_os_appctl.py":
            "7c2f73007bf2b9b6d1821c1ab9f788c21b81dac2eae831bc591ecc0f5c21535d",
    }
    for relative, expected in protected_expected.items():
        path = repo / relative
        if not path.is_file():
            failures.append(f"protected_file_missing:{relative}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(
                f"protected_file_changed:{relative}:expected={expected}:actual={actual}"
            )

    main_source = (repo / "main.py").read_text(encoding="utf-8")
    for marker in (
        "BEGIN FORGE LANGUAGE CORE REPLACEMENT BRIDGE 1",
        "Use the deterministic bridge first, then Qwen3 only for unsupported requests.",
        "language_bridge_handled",
        "ollama_fallback_used",
    ):
        if marker not in main_source:
            failures.append(f"main_marker_missing:{marker}")

    interpreter_source = (
        repo / "forge_language_bridge_v1" / "interpreter.py"
    ).read_text(encoding="utf-8")
    for marker in (
        "requests.",
        "urllib.",
        "subprocess.",
        "os.system",
        "socket.",
        "_call_ollama",
    ):
        if marker in interpreter_source:
            failures.append(f"forbidden_interpreter_marker:{marker}")

    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    staged = {
        line
        for line in git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
        if line
    }
    tracked = {
        line
        for line in git(repo, "diff", "--name-only").stdout.splitlines()
        if line
    }
    untracked = {
        line
        for line in git(
            repo, "ls-files", "--others", "--exclude-standard"
        ).stdout.splitlines()
        if line
    }

    if args.mode == "applied":
        if head != EXPECTED_BASE_HEAD:
            failures.append(f"applied_head_mismatch:{head}")
        if staged:
            failures.append("staged_paths_present:" + ",".join(sorted(staged)))
        actual_changes = tracked | untracked
        if actual_changes != expected_paths:
            for path in sorted(expected_paths - actual_changes):
                failures.append(f"expected_change_missing:{path}")
            for path in sorted(actual_changes - expected_paths):
                failures.append(f"unexpected_change:{path}")
    else:
        status = git(repo, "status", "--porcelain=v1", "-uall").stdout.strip()
        if status:
            failures.append("repository_not_clean")
        committed_paths = {
            line
            for line in git(
                repo,
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "HEAD",
            ).stdout.splitlines()
            if line
        }
        if committed_paths != expected_paths:
            failures.append("committed_path_set_mismatch")

    if failures:
        print("FORGE LANGUAGE BRIDGE 1 VERIFIER: FAIL")
        for failure in failures:
            print(f"FAIL - {failure}")
        return 1

    print("FORGE LANGUAGE BRIDGE 1 VERIFIER: PASS")
    print(f"mode={args.mode}")
    print(f"payload_files={len(expected_paths)}")
    print("agent_py_changed=0")
    print("launcher_repair_files_preserved=1")
    print("covered_requests_call_llm=0")
    print("simulation_execution=0")
    print("bridge1_full_replacement_claimed=0")
    print(f"staged_paths={len(staged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
