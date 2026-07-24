#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

EXPECTED_PARENT_HEAD = "05e758949c279f570ffa87adf7ad39efafe01412"
EXPECTED_PARENT_TREE = "b10c625a0165142e19e7e722e64b04b72cde819d"
EXPECTED_PARENT_SUBJECT = "Slice 48 local runtime service boundary"
EXPECTED_COMMIT_SUBJECT = "Forge workshop runtime state and launcher repair"

EXACT_PATH_LIST = (
    "scripts/"
    "AIWEB_FORGE_WORKSHOP_RUNTIME_STATE_AND_LAUNCHER_REPAIR_EXACT_PAYLOAD_PATHS.txt"
)
PAYLOAD_MANIFEST = (
    "scripts/"
    "AIWEB_FORGE_WORKSHOP_RUNTIME_STATE_AND_LAUNCHER_REPAIR_PAYLOAD_SHA256SUMS.txt"
)
BEHAVIOR_TEST = (
    "scripts/"
    "test_aiweb_forge_workshop_runtime_state_and_launcher_repair.py"
)

EXPECTED_TRACKED_PATHS = {
    "agents/forge/permissions.py",
    "main.py",
    "scripts/aiweb_os_appctl.py",
}
EXPECTED_PAYLOAD_COUNT = 12

FORBIDDEN_SOURCE_RUNTIME_PATHS = (
    "memory/forge_build_sequence_v1/20260723_230841_forge_build_sequence_v1.json",
    "memory/forge_build_sequence_v1/20260724_071942_forge_build_sequence_v1.json",
    "memory/forge_build_sequence_v1/20260724_071943_forge_build_sequence_v1.json",
)

RESTORED_TRACKED_REPORTS = (
    "memory/aiweb_patch239_protoforge_connector_v1/latest_protoforge_status.json",
    "memory/aiweb_patch239_protoforge_connector_v1/latest_protoforge_status.md",
)

MIGRATED_RUNTIME_PATHS = (
    "config/approved_paths.json",
    "config/session_scope.json",
    "memory/forge_build_sequence_v1/20260723_230841_forge_build_sequence_v1.json",
    "memory/forge_build_sequence_v1/20260724_071942_forge_build_sequence_v1.json",
    "memory/forge_build_sequence_v1/20260724_071943_forge_build_sequence_v1.json",
    "memory/aiweb_patch239_protoforge_connector_v1/latest_protoforge_status.json",
    "memory/aiweb_patch239_protoforge_connector_v1/latest_protoforge_status.md",
)


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


def selected_python(repo: Path) -> Path:
    candidate = repo / ".venv" / "bin" / "python"
    return candidate if candidate.is_file() else Path("/usr/bin/python3")


def parse_exact_paths(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def parse_manifest(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        try:
            digest, relative_path = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed_manifest_line:{line_number}") from error
        if relative_path.startswith("/") or ".." in Path(relative_path).parts:
            raise ValueError(f"unsafe_manifest_path:{relative_path}")
        rows[relative_path] = digest
    return rows


def verify_runtime_status(runtime_root: Path, failures: list[str]) -> None:
    for relative_path in MIGRATED_RUNTIME_PATHS:
        target = runtime_root / relative_path
        if not target.is_file():
            failures.append(f"runtime_migration_missing:{target}")

    status_path = (
        runtime_root
        / "memory"
        / "aiweb_patch239_protoforge_connector_v1"
        / "latest_protoforge_status.json"
    )
    if status_path.is_file():
        try:
            payload = json.loads(status_path.read_text(encoding="utf-8"))
        except Exception as error:
            failures.append(
                "runtime_protoforge_status_invalid:"
                f"{type(error).__name__}:{error}"
            )
        else:
            if payload.get("verdict") != "PROTOFORGE_STATUS_OK":
                failures.append(
                    "runtime_protoforge_status_verdict:"
                    f"{payload.get('verdict')}"
                )
            if bool(payload.get("simulation_executed", True)):
                failures.append("runtime_protoforge_status_claims_simulation")
            if bool(payload.get("identity_vault_written", True)):
                failures.append("runtime_protoforge_status_claims_identity_write")
            if bool(payload.get("rmc_live_memory_written", True)):
                failures.append("runtime_protoforge_status_claims_rmc_write")


def verify_git_state(
    repo: Path,
    mode: str,
    exact_paths: list[str],
    failures: list[str],
) -> None:
    branch = git(repo, "branch", "--show-current").stdout.strip()
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    subject = git(repo, "show", "-s", "--format=%s", "HEAD").stdout.strip()
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
            repo,
            "ls-files",
            "--others",
            "--exclude-standard",
        ).stdout.splitlines()
        if line
    }

    if branch != "main":
        failures.append(f"branch_mismatch:{branch}")
    if staged:
        failures.append("staged_paths_present:" + ",".join(sorted(staged)))

    if mode == "applied":
        if head != EXPECTED_PARENT_HEAD:
            failures.append(f"applied_head_mismatch:{head}")
        if tree != EXPECTED_PARENT_TREE:
            failures.append(f"applied_tree_mismatch:{tree}")
        if subject != EXPECTED_PARENT_SUBJECT:
            failures.append(f"applied_subject_mismatch:{subject}")

        expected_untracked = set(exact_paths) - EXPECTED_TRACKED_PATHS
        if tracked != EXPECTED_TRACKED_PATHS:
            failures.append(
                "tracked_change_set_mismatch:"
                + ",".join(sorted(tracked))
            )
        if untracked != expected_untracked:
            failures.append(
                "untracked_path_set_mismatch:"
                + ",".join(sorted(untracked))
            )
    else:
        parent = git(repo, "rev-parse", "HEAD^").stdout.strip()
        changed = {
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
        if parent != EXPECTED_PARENT_HEAD:
            failures.append(f"committed_parent_mismatch:{parent}")
        if subject != EXPECTED_COMMIT_SUBJECT:
            failures.append(f"committed_subject_mismatch:{subject}")
        if changed != set(exact_paths):
            failures.append(
                "committed_path_set_mismatch:"
                + ",".join(sorted(changed))
            )
        if tracked:
            failures.append(
                "tracked_changes_after_commit:"
                + ",".join(sorted(tracked))
            )
        if untracked:
            failures.append(
                "untracked_paths_after_commit:"
                + ",".join(sorted(untracked))
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument(
        "--mode",
        choices=("applied", "committed"),
        default="applied",
    )
    parser.add_argument("--skip-behavior", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repository).resolve()
    failures: list[str] = []

    exact_path_file = repo / EXACT_PATH_LIST
    payload_manifest_file = repo / PAYLOAD_MANIFEST

    if not exact_path_file.is_file():
        failures.append(f"exact_path_file_missing:{EXACT_PATH_LIST}")
        exact_paths: list[str] = []
    else:
        exact_paths = parse_exact_paths(exact_path_file)

    if len(exact_paths) != EXPECTED_PAYLOAD_COUNT:
        failures.append(f"payload_count:{len(exact_paths)}")
    if len(set(exact_paths)) != len(exact_paths):
        failures.append("duplicate_payload_paths")

    if not payload_manifest_file.is_file():
        failures.append(f"payload_manifest_missing:{PAYLOAD_MANIFEST}")
        expected_hashes: dict[str, str] = {}
    else:
        try:
            expected_hashes = parse_manifest(payload_manifest_file)
        except ValueError as error:
            failures.append(str(error))
            expected_hashes = {}

    verify_git_state(repo, args.mode, exact_paths, failures)

    for relative_path in exact_paths:
        target = repo / relative_path
        if not target.is_file():
            failures.append(f"payload_file_missing:{relative_path}")
            continue
        if relative_path == PAYLOAD_MANIFEST:
            continue
        expected_digest = expected_hashes.get(relative_path)
        if expected_digest is None:
            failures.append(f"payload_hash_missing:{relative_path}")
            continue
        actual_digest = sha256_file(target)
        if actual_digest != expected_digest:
            failures.append(
                "payload_hash_mismatch:"
                f"{relative_path}:"
                f"expected={expected_digest}:actual={actual_digest}"
            )

    for relative_path in FORBIDDEN_SOURCE_RUNTIME_PATHS:
        if (repo / relative_path).exists():
            failures.append(f"runtime_record_left_in_source:{relative_path}")

    for relative_path in RESTORED_TRACKED_REPORTS:
        result = git(repo, "diff", "--quiet", "--", relative_path)
        if result.returncode != 0:
            failures.append(f"tracked_runtime_report_not_restored:{relative_path}")

    runtime_root = (
        Path(
            os.environ.get(
                "XDG_STATE_HOME",
                str(Path.home() / ".local" / "state"),
            )
        )
        / "aiweb-forge"
        / "legacy-workshop-v1"
    )
    verify_runtime_status(runtime_root, failures)

    main_text = (repo / "main.py").read_text(encoding="utf-8")
    required_markers = (
        'FORGE_BUILD_SEQUENCE_DIR = RUNTIME_MEMORY_DIR / "forge_build_sequence_v1"',
        '_P198_EXTRA_SEQUENCE_SOURCE_FILE = (',
        'P239_PROTOFORGE_SOURCE_DIR = MEMORY_DIR / "aiweb_patch239_protoforge_connector_v1"',
        'RUNTIME_MEMORY_DIR / "aiweb_patch239_protoforge_connector_v1"',
        'def _p239_read_report_path(runtime_path: Path) -> Path:',
    )
    for marker in required_markers:
        if marker not in main_text:
            failures.append(f"main_marker_missing:{marker}")

    forbidden_markers = (
        '_P198_EXTRA_SEQUENCE_FILE = MEMORY_DIR / "forge_build_sequence_v1"',
        'P239_PROTOFORGE_CONNECTOR_DIR = MEMORY_DIR / "aiweb_patch239_protoforge_connector_v1"',
        '_p198_bsdir = MEMORY_DIR / "forge_build_sequence_v1"',
    )
    for marker in forbidden_markers:
        if marker in main_text:
            failures.append(f"forbidden_source_write_marker:{marker}")

    try:
        compile(main_text, str(repo / "main.py"), "exec")
    except SyntaxError as error:
        failures.append(f"main_syntax_error:{error}")

    if failures:
        print("FORGE WORKSHOP RUNTIME/LAUNCHER R2 VERIFIER: FAIL")
        for failure in failures:
            print(f"FAIL - {failure}")
        return 1

    if not args.skip_behavior:
        result = subprocess.run(
            [
                str(selected_python(repo)),
                "-B",
                str(repo / BEHAVIOR_TEST),
                str(repo),
            ],
            cwd=str(repo),
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=300,
        )
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.returncode != 0:
            print(f"FAIL - behavior_test_exit_code:{result.returncode}")
            return 1

    print("FORGE WORKSHOP RUNTIME/LAUNCHER R2 VERIFIER: PASS")
    print(f"mode={args.mode}")
    print(f"payload_files={len(exact_paths)}")
    print("tracked_runtime_config_clean=1")
    print("tracked_protoforge_reports_clean=1")
    print("runtime_build_sequence_residue_in_source=0")
    print("runtime_protoforge_reports_in_source=0")
    print("source_runtime_separation=1")
    print("staged_paths=0")
    print("bridge1_applied=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
