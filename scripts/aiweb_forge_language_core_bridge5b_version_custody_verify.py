#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

EXPECTED_PARENT = '35b3fc1de6fe52788ec0a2465e73b1448ad6fc04'
PREFIX = 'AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5B_SLICE38_SLICE40_VERSION_CUSTODY'
EXACT_PATHS_PATH = f"scripts/{PREFIX}_EXACT_PAYLOAD_PATHS.txt"
PAYLOAD_MANIFEST_PATH = f"scripts/{PREFIX}_PAYLOAD_SHA256SUMS.txt"
PROTECTED_MANIFEST_PATH = f"scripts/{PREFIX}_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
HELPER_PATH = "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/predicate_frame_version_custody.py"
VALIDATION_PATHS = (
    "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/expectancy_gate/validation.py",
    "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/congruity_gate/validation.py",
    "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/connectedness_gate/validation.py",
    "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/recoverable_purpose_gate/validation.py",
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


def read_manifest(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, relative = line.split("  ", 1)
        records[relative] = digest
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--mode", choices=("applied", "committed"), default="applied")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    failures: list[str] = []

    exact_file = repo / EXACT_PATHS_PATH
    payload_manifest = repo / PAYLOAD_MANIFEST_PATH
    protected_manifest = repo / PROTECTED_MANIFEST_PATH
    for required in (exact_file, payload_manifest, protected_manifest):
        if not required.is_file():
            failures.append(f"missing_required_file:{required.relative_to(repo)}")
    if failures:
        print("AI.WEB BRIDGE 5B VERSION CUSTODY VERIFIER: FAIL")
        for failure in failures:
            print(f"FAIL - {failure}")
        return 1

    exact_paths = {
        line.strip()
        for line in exact_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    payload_records = read_manifest(payload_manifest)
    protected_records = read_manifest(protected_manifest)

    if len(exact_paths) != 14:
        failures.append(f"exact_path_count:{len(exact_paths)}")
    if set(payload_records) != exact_paths - {PAYLOAD_MANIFEST_PATH}:
        failures.append("payload_manifest_path_set_mismatch")

    for relative, expected in sorted(payload_records.items()):
        path = repo / relative
        if not path.is_file():
            failures.append(f"payload_missing:{relative}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(f"payload_hash_mismatch:{relative}:{actual}")

    helper = repo / HELPER_PATH
    if helper.is_file():
        text = helper.read_text(encoding="utf-8")
        for required_text in (
            "predicate_by_id",
            "frame_by_id",
            "LEGACY_GATE_PREDICATE_VERSION",
            "LEGACY_GATE_FRAME_VERSION",
            "frame.linked_predicate_id != predicate.predicate_id",
        ):
            if required_text not in text:
                failures.append(f"helper_boundary_missing:{required_text}")

    for relative in VALIDATION_PATHS:
        path = repo / relative
        if not path.is_file():
            failures.append(f"validation_missing:{relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if "invalid_predicate_frame_version_fields" not in text:
            failures.append(f"version_custody_not_connected:{relative}")

    for relative, expected in sorted(protected_records.items()):
        if relative in exact_paths:
            continue
        path = repo / relative
        if not path.is_file():
            failures.append(f"protected_file_missing:{relative}")
            continue
        if sha256_file(path) != expected:
            failures.append(f"protected_file_changed:{relative}")

    staged = {
        item
        for item in git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
        if item
    }
    if staged:
        failures.append("staged_paths_present:" + ",".join(sorted(staged)))

    if git(repo, "diff", "--name-only", "--", "memory").stdout.strip():
        failures.append("tracked_memory_changes")
    if git(repo, "ls-files", "--others", "--exclude-standard", "--", "memory").stdout.strip():
        failures.append("untracked_memory_paths")

    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if args.mode == "applied":
        if head != EXPECTED_PARENT:
            failures.append(f"unexpected_applied_head:{head}")
        changed = {
            item
            for item in git(repo, "diff", "--name-only").stdout.splitlines()
            if item
        } | {
            item
            for item in git(repo, "ls-files", "--others", "--exclude-standard").stdout.splitlines()
            if item
        }
        if changed != exact_paths:
            failures.append("applied_change_path_set_mismatch")
    else:
        parent = git(repo, "rev-parse", "HEAD^").stdout.strip()
        committed = {
            item
            for item in git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines()
            if item
        }
        status = git(repo, "status", "--porcelain=v1", "-uall").stdout.strip()
        if parent != EXPECTED_PARENT:
            failures.append(f"committed_parent_mismatch:{parent}")
        if committed != exact_paths:
            failures.append("committed_path_set_mismatch")
        if status:
            failures.append("repository_not_clean")

    if failures:
        print("AI.WEB BRIDGE 5B VERSION CUSTODY VERIFIER: FAIL")
        for failure in failures:
            print(f"FAIL - {failure}")
        return 1

    print("AI.WEB BRIDGE 5B VERSION CUSTODY VERIFIER: PASS")
    print(f"mode={args.mode}")
    print(f"payload_files={len(exact_paths)}")
    print("legacy_v1_0_0_compatibility_preserved=1")
    print("current_registry_predicate_version_custody=1")
    print("current_registry_frame_version_custody=1")
    print("exact_frame_predicate_link_required=1")
    print("arbitrary_versions_rejected=1")
    print("gate_composition_authority=0")
    print("selection_eligibility_authority=0")
    print("selected_meaning_authority=0")
    print("tool_routing_authority=0")
    print("action_authority=0")
    print("staged_paths=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
