#!/usr/bin/env python3
"""Visible sequential verifier for the Slice 39B-E roadmap correction."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import selectors
import stat
import subprocess
import sys
import tempfile
import time


EXPECTED_BRANCH = "main"
EXPECTED_HEAD = "f34f2f65151ac15dc07e7e49b63394bb23899efe"
EXPECTED_TREE = "c2f9be75457e69520925c171cf3b81ca98aad0c3"
EXPECTED_SUBJECT = "Slice 39E candidate set and alternative preservation"
EXPECTED_COMMITTED_SUBJECT = "Slice 39B-E roadmap continuity correction"
EXPECTED_PROTECTED_COUNT = 419
EXPECTED_PAYLOAD_COUNT = 20
EXPECTED_MODIFIED_COUNT = 11
EXPECTED_ADDED_COUNT = 9
EXPECTED_BEHAVIOR_CHECKS = 126
EXPECTED_CRITICAL_RUNTIME_FILES = 22
EXPECTED_SLICE38H_SOURCE_BEHAVIOR_CHECKS = 2655
EXPECTED_SLICE38H_MALFORMED_CASES = 420

MODIFIED_PATHS = (
    "aiweb_language_core_bootstrap/candidate_meaning_construction/predecessor_custody/authority.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_semantic_content/authority.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/candidate_set_preservation/authority.py",
    "scripts/AIWEB_SLICE39B_LIFECYCLE_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md",
    "scripts/AIWEB_SLICE39B_DETERMINISTIC_VALIDATION_IDENTITY_VERSIONING_LIFECYCLE_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE39C_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md",
    "scripts/AIWEB_SLICE39C_COMPLETE_PROVENANCE_PREDECESSOR_CUSTODY_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE39D_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md",
    "scripts/AIWEB_SLICE39D_CANDIDATE_SEMANTIC_CONTENT_ASSEMBLY_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE39E_AUTHORITY_AND_DEFERRED_SCOPE_DECISION.md",
    "scripts/AIWEB_SLICE39E_CANDIDATE_SET_ALTERNATIVE_PRESERVATION_RUNTIME_SPEC.md",
)

ADDED_PATHS = (
    "aiweb_language_core_bootstrap/candidate_meaning_construction/roadmap_continuity/__init__.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/roadmap_continuity/authority.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/roadmap_continuity/validation.py",
    "scripts/AIWEB_SLICE39B_39E_ROADMAP_CONTINUITY_CORRECTION_DECISION.md",
    "scripts/AIWEB_SLICE39B_39E_ROADMAP_CONTINUITY_CORRECTION_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE39B_39E_ROADMAP_CONTINUITY_CORRECTION_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/README_aiweb_slice39b_39e_roadmap_continuity_correction.md",
    "scripts/aiweb_slice39b_39e_roadmap_continuity_correction_verify.py",
    "scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py",
)

PAYLOAD_PATHS = tuple(sorted((*MODIFIED_PATHS, *ADDED_PATHS)))

INHERITED_TESTS = (
    "scripts/test_aiweb_slice39e_candidate_set_alternative_preservation.py",
    "scripts/test_aiweb_slice39d_candidate_semantic_content_assembly.py",
    "scripts/test_aiweb_slice39c_complete_provenance_predecessor_custody.py",
    "scripts/test_aiweb_slice39b_deterministic_validation_identity_versioning_lifecycle.py",
    "scripts/test_aiweb_slice39a_candidate_meaning_core_schema.py",
    "scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py",
    "scripts/test_aiweb_slice38g_predicate_role_frame_candidate_proposal.py",
    "scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py",
    "scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py",
    "scripts/test_aiweb_slice38d_participant_role_identity_registry.py",
    "scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py",
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
    "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
    "scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py",
)

SLICE38H_INHERITED_TEST = (
    "scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py"
)

PROHIBITED_IMPORT_ROOTS = {
    "anthropic", "chromadb", "datetime", "faiss", "httpx", "keras",
    "langchain", "llama_index", "nltk", "numpy", "openai", "os", "pandas",
    "pathlib", "platform", "random", "requests", "scipy", "secrets",
    "sentence_transformers", "sklearn", "socket", "spacy", "subprocess",
    "tensorflow", "time", "torch", "transformers", "uuid",
}
PROHIBITED_TOKENS = (
    "@app.route", "@router.", "FastAPI(", "Flask(", "requests.",
    "urlopen(", "socket.socket(", "os.system(", "subprocess.", "open(",
    "Path(", "read_text(", "write_text(", "os.environ", "time.time(",
    "datetime.now(", "uuid.", "random.", "secrets.",
)


class Verification:
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


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    records: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        digest, relative = line.split("  ", 1)
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise ValueError(f"unsafe path line {number}")
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError(f"invalid digest line {number}")
        if relative in seen:
            raise ValueError(f"duplicate path line {number}")
        seen.add(relative)
        records.append((digest, relative))
    return tuple(records)


def git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def verify_git_state(repository: Path, mode: str, verification: Verification) -> None:
    if mode == "source":
        return

    branch = git(repository, "branch", "--show-current")
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    subject = git(repository, "show", "-s", "--format=%s", "HEAD")
    staged = git(repository, "diff", "--cached", "--name-only")
    tracked = git(repository, "diff", "--name-only")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")

    for result, label in (
        (branch, "branch"), (head, "HEAD"), (tree, "tree"),
        (subject, "subject"), (staged, "staged"),
        (tracked, "tracked"), (untracked, "untracked"),
    ):
        verification.check(result.returncode == 0, f"git {label} inspection")

    if mode == "applied":
        verification.check(branch.stdout.strip() == EXPECTED_BRANCH, "applied branch")
        verification.check(head.stdout.strip() == EXPECTED_HEAD, "applied HEAD")
        verification.check(tree.stdout.strip() == EXPECTED_TREE, "applied tree")
        verification.check(subject.stdout.strip() == EXPECTED_SUBJECT, "applied subject")
        verification.check(not staged.stdout.strip(), "applied staged paths zero")
        actual_modified = tuple(sorted(line for line in tracked.stdout.splitlines() if line))
        actual_added = tuple(sorted(line for line in untracked.stdout.splitlines() if line))
        verification.check(actual_modified == tuple(sorted(MODIFIED_PATHS)), "applied exact modified paths")
        verification.check(actual_added == tuple(sorted(ADDED_PATHS)), "applied exact added paths")
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        verification.check(parent.returncode == 0 and parent.stdout.strip() == EXPECTED_HEAD, "committed parent")
        verification.check(subject.stdout.strip() == EXPECTED_COMMITTED_SUBJECT, "committed subject")
        verification.check(not staged.stdout.strip(), "committed staged paths zero")
        verification.check(not tracked.stdout.strip(), "committed tracked modifications zero")
        verification.check(not untracked.stdout.strip(), "committed untracked paths zero")
        committed = git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
        actual = tuple(sorted(line for line in committed.stdout.splitlines() if line))
        verification.check(committed.returncode == 0 and actual == PAYLOAD_PATHS, "committed exact payload paths")


def static_source_checks(repository: Path, verification: Verification) -> None:
    package = repository / "aiweb_language_core_bootstrap" / "candidate_meaning_construction" / "roadmap_continuity"
    files = tuple(sorted(package.glob("*.py")))
    verification.check(tuple(path.name for path in files) == ("__init__.py", "authority.py", "validation.py"), "exact correction package files")

    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except Exception:
            verification.check(False, f"parse {path.name}")
            continue
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split(".", 1)[0])
        verification.check(not (roots & PROHIBITED_IMPORT_ROOTS), f"standard-library boundary {path.name}")
        for token in PROHIBITED_TOKENS:
            verification.check(token not in text, f"no effect token {path.name} {token}")


def parse_single_integer_marker(output: str, marker: str) -> int | None:
    prefix = f"{marker}="
    values: list[int] = []
    for line in output.splitlines():
        if line.startswith(prefix):
            try:
                values.append(int(line[len(prefix):]))
            except ValueError:
                return None
    return values[0] if len(values) == 1 else None


def stream_test(command: list[str], *, cwd: Path, env: dict[str, str]) -> tuple[int, str]:
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        start_new_session=True,
    )
    lines: list[str] = []
    assert process.stdout is not None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    parent_exit_deadline: float | None = None
    try:
        while True:
            events = selector.select(timeout=0.25)
            saw_eof = False
            for key, _ in events:
                line = key.fileobj.readline()
                if line:
                    print(line, end="")
                    lines.append(line)
                else:
                    saw_eof = True
            return_code = process.poll()
            if return_code is not None and saw_eof:
                break
            if return_code is None:
                parent_exit_deadline = None
                continue
            if parent_exit_deadline is None:
                parent_exit_deadline = time.monotonic() + 2.0
            if not events and time.monotonic() >= parent_exit_deadline:
                break
    finally:
        selector.close()
        process.stdout.close()
    return process.wait(), "".join(lines)


def stream_source_only_inherited_test(repository: Path, relative: str, *, env: dict[str, str], verification: Verification) -> tuple[int, str]:
    required_roots = ("aiweb_language_core_bootstrap", "scripts")
    for root_name in required_roots:
        source_root = repository / root_name
        verification.check(source_root.is_dir() and not source_root.is_symlink(), f"source-only inherited root {root_name}")
        if not source_root.is_dir() or source_root.is_symlink():
            return 1, f"FAIL: unsafe or missing root: {source_root}\n"

    with tempfile.TemporaryDirectory(prefix="aiweb_slice39be_correction_inherited_") as temporary:
        source_only_repository = Path(temporary)
        try:
            for root_name in required_roots:
                os.symlink(repository / root_name, source_only_repository / root_name, target_is_directory=True)
        except OSError as error:
            verification.check(False, "source-only inherited view creation")
            return 1, f"FAIL: source-only view creation: {error}\n"
        verification.check(not (source_only_repository / ".git").exists(), "source-only inherited Git metadata absent")
        command = [sys.executable, "-B", str(source_only_repository / relative), str(source_only_repository)]
        print("execution_context=source_only_inherited")
        print(f"source_only_repository={source_only_repository}")
        print(f"command={' '.join(command)}")
        return stream_test(command, cwd=source_only_repository, env=env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", choices=("source", "applied", "committed"), default="source")
    args = parser.parse_args()

    repository = Path(args.repository).resolve()
    verification = Verification()

    print("AI.WEB SLICE 39B-E ROADMAP CONTINUITY CORRECTION VERIFIER")
    print(f"repository={repository}")
    print(f"mode={args.mode}")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")

    verification.check(repository.is_dir(), "repository exists")
    verification.check(len(PAYLOAD_PATHS) == EXPECTED_PAYLOAD_COUNT, "payload count")
    verification.check(len(MODIFIED_PATHS) == EXPECTED_MODIFIED_COUNT, "modified count")
    verification.check(len(ADDED_PATHS) == EXPECTED_ADDED_COUNT, "added count")
    verification.check(len(PAYLOAD_PATHS) == len(set(PAYLOAD_PATHS)), "payload unique")

    protected_path = repository / "scripts" / "AIWEB_SLICE39B_39E_ROADMAP_CONTINUITY_CORRECTION_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    try:
        protected = parse_manifest(protected_path)
    except Exception as error:
        verification.check(False, f"protected manifest parse: {error}")
        protected = ()
    verification.check(len(protected) == EXPECTED_PROTECTED_COUNT, "protected predecessor count")

    for digest, relative in protected:
        path = repository / relative
        verification.check(path.is_file() and not path.is_symlink(), f"protected predecessor exists {relative}")
        if path.is_file() and not path.is_symlink():
            verification.check(sha256_file(path) == digest, f"protected predecessor hash {relative}")

    for relative in PAYLOAD_PATHS:
        path = repository / relative
        verification.check(path.is_file() and not path.is_symlink(), f"payload exists {relative}")
        if path.is_file() and not path.is_symlink():
            expected_mode = 0o755 if relative in {
                "scripts/aiweb_slice39b_39e_roadmap_continuity_correction_verify.py",
                "scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py",
            } else 0o644
            verification.check(stat.S_IMODE(path.stat().st_mode) == expected_mode, f"payload mode {relative}")

    verify_git_state(repository, args.mode, verification)
    static_source_checks(repository, verification)

    current_test = "scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py"
    inherited = () if args.mode == "source" else INHERITED_TESTS
    tests = (current_test, *inherited)

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env.pop("PYTHONPYCACHEPREFIX", None)

    test_failures = 0
    observed_behavior_checks: int | None = None
    observed_critical_runtime_files: int | None = None
    observed_slice38h_behavior_checks: int | None = None
    observed_slice38h_malformed_cases: int | None = None

    for index, relative in enumerate(tests, 1):
        print()
        print(f"=== VISIBLE TEST {index} OF {len(tests)} ===")
        print(f"path={relative}")
        if relative == SLICE38H_INHERITED_TEST:
            print("output_begins_below")
            return_code, output = stream_source_only_inherited_test(repository, relative, env=env, verification=verification)
        else:
            command = [sys.executable, "-B", str(repository / relative), str(repository)]
            print(f"command={' '.join(command)}")
            print("output_begins_below")
            return_code, output = stream_test(command, cwd=repository, env=env)

        if relative == current_test:
            observed_behavior_checks = parse_single_integer_marker(output, "check_count")
            observed_critical_runtime_files = parse_single_integer_marker(output, "critical_runtime_files_unchanged")
            verification.check(observed_behavior_checks == EXPECTED_BEHAVIOR_CHECKS, "correction behavior check count")
            verification.check(observed_critical_runtime_files == EXPECTED_CRITICAL_RUNTIME_FILES, "critical runtime file count")
            verification.check("AI.WEB SLICE 39B-E ROADMAP CONTINUITY CORRECTION TEST: PASS" in output, "correction pass marker")
            for marker in (
                "roadmap_sequence=39A>39B>39C>39D>39E>39F>39G>39H>40",
                "next_after_39e=39F",
                "slice40_entry_requires=39H",
                "constructor_installed=0",
                "manifest_integration_installed=0",
                "bootstrap_integration_installed=0",
                "slice39_closeout_created=0",
                "gate_engine_installed=0",
            ):
                verification.check(marker in output, f"correction marker {marker}")

        if relative == SLICE38H_INHERITED_TEST:
            observed_slice38h_behavior_checks = parse_single_integer_marker(output, "check_count")
            observed_slice38h_malformed_cases = parse_single_integer_marker(output, "malformed_closeout_cases")
            verification.check(observed_slice38h_behavior_checks == EXPECTED_SLICE38H_SOURCE_BEHAVIOR_CHECKS, "Slice 38H source behavior count")
            verification.check(observed_slice38h_malformed_cases == EXPECTED_SLICE38H_MALFORMED_CASES, "Slice 38H malformed count")
            verification.check("AI.WEB SLICE 38H BEHAVIOR TEST: PASS" in output, "Slice 38H source pass marker")
            verification.check("source_only_git_proof_deferred=1" in output, "Slice 38H Git proof deferred")

        print("output_ended_above")
        print(f"return_code={return_code}")
        verification.check(return_code == 0, f"test passed {relative}")
        if return_code != 0:
            test_failures += 1

    print()
    print("=== SLICE 39B-E CORRECTION VERIFIER SUMMARY ===")
    print(f"pass_count={verification.passes}")
    print(f"failure_count={len(verification.failures)}")
    for failure in verification.failures:
        print(f"FAIL: {failure}")

    if verification.failures or test_failures:
        print("SLICE 39B-E ROADMAP CONTINUITY CORRECTION VERIFIER: FAIL")
        return 1

    print("SLICE 39B-E ROADMAP CONTINUITY CORRECTION VERIFIER: PASS")
    print(f"protected_predecessor_files={EXPECTED_PROTECTED_COUNT}")
    print(f"corrected_existing_files={EXPECTED_MODIFIED_COUNT}")
    print(f"new_correction_files={EXPECTED_ADDED_COUNT}")
    print(f"exact_payload_files={EXPECTED_PAYLOAD_COUNT}")
    print(f"inherited_tests={len(inherited)}")
    print(f"visible_total_tests={len(tests)}")
    print(f"behavior_checks={observed_behavior_checks}")
    print(f"critical_runtime_files_unchanged={observed_critical_runtime_files}")
    print("roadmap_sequence=39A>39B>39C>39D>39E>39F>39G>39H>40")
    print("next_after_39e=39F")
    print("slice40_entry_requires=39H")
    print("candidate_identity_behavior_changed=0")
    print("candidate_content_behavior_changed=0")
    print("candidate_set_behavior_changed=0")
    print("constructor_installed=0")
    print("manifest_integration_installed=0")
    print("bootstrap_integration_installed=0")
    print("slice39_closeout_created=0")
    print("gate_engine_installed=0")
    print("selected_meaning_created=0")
    print("truth_evidence_permission=0")
    print("route_action_memory_rendering_delivery=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
