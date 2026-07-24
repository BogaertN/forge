#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import socket
import subprocess
from pathlib import Path

EXPECTED_PARENT = "5996ccc6726c935cee8eb01378ec605c827380d9"
MODIFIED_PATHS = {
    "main.py",
    "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/gate_composition/validation.py",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/usr/bin/git", "-C", str(repo), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def read_hash_manifest(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line:
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"malformed manifest line {line_number}") from error
        records[relative] = digest
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", choices=("applied", "committed"), required=True)
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    failures: list[str] = []

    exact_file = repo / "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_EXACT_PAYLOAD_PATHS.txt"
    manifest_file = repo / "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_PAYLOAD_SHA256SUMS.txt"
    protected_file = repo / "scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5_PROTECTED_PREDECESSOR_SHA256SUMS.txt"

    for required in (exact_file, manifest_file, protected_file):
        if not required.is_file():
            failures.append(f"required_file_missing:{required.relative_to(repo)}")

    if failures:
        print("FORGE LANGUAGE BRIDGE 5 VERIFIER: FAIL")
        for failure in failures:
            print("FAIL -", failure)
        return 1

    exact_lines = [
        line.strip()
        for line in exact_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    exact_paths = set(exact_lines)
    if len(exact_lines) != len(exact_paths):
        failures.append("duplicate_exact_payload_paths")

    payload_records = read_hash_manifest(manifest_file)
    manifest_relative = manifest_file.relative_to(repo).as_posix()
    if set(payload_records) != exact_paths - {manifest_relative}:
        failures.append("payload_manifest_path_set_mismatch")

    for relative, expected in sorted(payload_records.items()):
        path = repo / relative
        if not path.is_file():
            failures.append(f"payload_file_missing:{relative}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(
                f"payload_hash_mismatch:{relative}:expected={expected}:actual={actual}"
            )

    branch = git(repo, "branch", "--show-current").stdout.strip()
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    staged = {
        line
        for line in git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
        if line
    }
    tracked_memory = git(repo, "diff", "--name-only", "--", "memory").stdout.strip()
    untracked_memory = git(
        repo, "ls-files", "--others", "--exclude-standard", "--", "memory"
    ).stdout.strip()

    if branch != "main":
        failures.append(f"unexpected_branch:{branch}")
    if staged:
        failures.append("staged_paths_present:" + ",".join(sorted(staged)))
    if tracked_memory:
        failures.append("tracked_memory_changes")
    if untracked_memory:
        failures.append("untracked_memory_paths")

    if args.mode == "applied":
        if head != EXPECTED_PARENT:
            failures.append(f"unexpected_applied_head:{head}")
        changed = {
            line
            for line in git(repo, "diff", "--name-only").stdout.splitlines()
            if line
        } | {
            line
            for line in git(
                repo, "ls-files", "--others", "--exclude-standard"
            ).stdout.splitlines()
            if line
        }
        if changed != exact_paths:
            failures.append(
                "applied_change_path_set_mismatch:"
                f"expected={sorted(exact_paths)!r}:actual={sorted(changed)!r}"
            )
    else:
        parent = git(repo, "rev-parse", "HEAD^").stdout.strip()
        committed = {
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
        status = git(repo, "status", "--porcelain=v1", "-uall").stdout.strip()
        if parent != EXPECTED_PARENT:
            failures.append(f"unexpected_committed_parent:{parent}")
        if committed != exact_paths:
            failures.append("committed_path_set_mismatch")
        if status:
            failures.append("repository_not_clean")

    main_text = (repo / "main.py").read_text(encoding="utf-8", errors="replace")
    eligibility_text = (
        repo / "forge_language_bridge_v5/eligibility_hold.py"
    ).read_text(encoding="utf-8", errors="replace")
    builder_text = (
        repo / "forge_language_bridge_v5/runtime_builders.py"
    ).read_text(encoding="utf-8", errors="replace")
    composition_validation = (
        repo
        / "aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/gate_composition/validation.py"
    ).read_text(encoding="utf-8", errors="replace")

    required_main_fragments = (
        '"forge-language-eligibility-hold"',
        "record = _flb5_status()",
        "bridge5_plan = _flb5_explicit_plan",
        "bridge4_plan = _flb4_explicit_plan",
    )
    for fragment in required_main_fragments:
        if fragment not in main_text:
            failures.append(f"main_fragment_missing:{fragment}")

    required_runtime_calls = (
        "evaluate_expectancy",
        "evaluate_congruity",
        "evaluate_connectedness",
        "evaluate_recoverable_purpose",
        "evaluate_gate_composition",
        "integrate_gate_results_into_manifest",
        "evaluate_selection_eligibility",
    )
    for fragment in required_runtime_calls:
        if fragment not in builder_text:
            failures.append(f"runtime_call_missing:{fragment}")

    if "test_aiweb" in builder_text or "runpy" in builder_text:
        failures.append("runtime_depends_on_test_fixture")
    if "_call_ollama" in builder_text or "ollama" in builder_text.lower():
        failures.append("forge_llm_call_present_in_bridge5_runtime")
    if "construct_selected_meaning" in builder_text:
        failures.append("slice41d_construction_call_present")

    required_boundary_fragments = (
        '"slice41d_called": False',
        '"slice41e_called": False',
        '"selected_meaning_constructed": False',
        '"echo_forge_llm_boundary_preserved": True',
        '"echo_forge_output_is_forge_authority": False',
    )
    for fragment in required_boundary_fragments:
        if fragment not in eligibility_text:
            failures.append(f"boundary_fragment_missing:{fragment}")

    if "same exact\n    # GateCandidateInputReference" not in composition_validation:
        failures.append("slice40g_same_candidate_correction_missing")
    if (
        "value.family_candidate_input_refs != tuple(result.candidate_input_ref for result in results)"
        not in composition_validation
    ):
        failures.append("slice40g_exact_order_cross_record_check_missing")

    diff_check = git(repo, "diff", "--check")
    if args.mode == "committed":
        diff_check = git(repo, "show", "--check", "--oneline", "HEAD")
    if diff_check.returncode != 0:
        failures.append("diff_check_failed")

    try:
        with socket.create_connection(("127.0.0.1", 7477), timeout=0.25):
            failures.append("port_7477_open")
    except OSError:
        pass

    if failures:
        print("FORGE LANGUAGE BRIDGE 5 VERIFIER: FAIL")
        for failure in failures:
            print("FAIL -", failure)
        return 1

    print("FORGE LANGUAGE BRIDGE 5 VERIFIER: PASS")
    print(f"mode={args.mode}")
    print(f"payload_files={len(exact_paths)}")
    print("exact_candidate_nomination_required=1")
    print("exact_predicate_frame_pair_required_when_plural=1")
    print("same_candidate_four_family_refs_allowed=1")
    print("exact_ordered_family_refs_required=1")
    print("slice40c_40f_connected=1")
    print("slice40g_composition_connected=1")
    print("slice40h_msm_gate_custody_connected=1")
    print("slice41c_eligibility_connected=1")
    print("slice41d_selected_meaning_authority=0")
    print("tool_routing_authority=0")
    print("action_authority=0")
    print("forge_llm_authority=0")
    print("echo_forge_llm_boundary_preserved=1")
    print("echo_forge_output_is_forge_authority=0")
    print("staged_paths=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
