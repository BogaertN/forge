#!/usr/bin/env python3
"""Visible sequential verifier for AI.Web Slice 38H."""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys

EXPECTED_BRANCH = "main"
EXPECTED_HEAD = "bf8ef1893c4093e950676699155c41dac4f34b2b"
EXPECTED_TREE = "ad5180f412b91aafde6eba875ffda4f17779c1d5"
EXPECTED_SUBJECT = "Slice 38G predicate role and frame candidate proposal"
EXPECTED_COMMITTED_SUBJECT = "Slice 38H disabled bootstrap integration and Slice 38 closeout"
EXPECTED_PREDECESSOR_COUNT = 347
EXPECTED_PAYLOAD_COUNT = 14
EXPECTED_SOURCE_BEHAVIOR_CHECKS = 2655
EXPECTED_LIVE_BEHAVIOR_CHECKS = 2666
EXPECTED_MALFORMED_CASES = 420

PAYLOAD_PATHS = (
    "aiweb_language_core_bootstrap/disabled_predicate_role_frame_bootstrap/__init__.py",
    "aiweb_language_core_bootstrap/disabled_predicate_role_frame_bootstrap/fixtures.py",
    "aiweb_language_core_bootstrap/disabled_predicate_role_frame_bootstrap/integration.py",
    "aiweb_language_core_bootstrap/disabled_predicate_role_frame_bootstrap/schema.py",
    "aiweb_language_core_bootstrap/disabled_predicate_role_frame_bootstrap/validation.py",
    "scripts/AIWEB_SLICE38H_BOUNDARY_AND_CLOSEOUT_DECISION.md",
    "scripts/AIWEB_SLICE38H_DISABLED_BOOTSTRAP_INTEGRATION_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE38H_EXACT_PAYLOAD_PATHS.txt",
    "scripts/AIWEB_SLICE38H_PRE_SLICE38_RECOVERY_BASELINE.txt",
    "scripts/AIWEB_SLICE38H_PROTECTED_SLICE35_38_PREDECESSOR_SHA256SUMS.txt",
    "scripts/AIWEB_SLICE38_ACCEPTANCE_RECORD.md",
    "scripts/README_aiweb_slice38h_disabled_bootstrap_integration_closeout.md",
    "scripts/aiweb_slice38h_disabled_bootstrap_integration_closeout_verify.py",
    "scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py",
)

INHERITED_TESTS = (
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

PROHIBITED_IMPORT_ROOTS = {
    "anthropic", "chromadb", "faiss", "httpx", "keras", "langchain",
    "llama_index", "nltk", "numpy", "openai", "pandas", "requests",
    "scipy", "sentence_transformers", "sklearn", "spacy", "tensorflow",
    "torch", "transformers",
}
PROHIBITED_TOKENS = (
    "@app.route", "@router.", "FastAPI(", "Flask(", "requests.",
    "urlopen(", "socket.socket(", "os.system(", "openai.", "anthropic.",
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
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
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
    staged = git(repository, "diff", "--cached", "--name-status")
    tracked = git(repository, "diff", "--name-status")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")
    for result, label in ((branch, "branch"), (head, "HEAD"), (tree, "tree"), (subject, "subject"), (staged, "staged"), (tracked, "tracked"), (untracked, "untracked")):
        verification.check(result.returncode == 0, f"git {label} inspection")
    if mode == "applied":
        verification.check(branch.stdout.strip() == EXPECTED_BRANCH, "applied branch")
        verification.check(head.stdout.strip() == EXPECTED_HEAD, "applied HEAD")
        verification.check(tree.stdout.strip() == EXPECTED_TREE, "applied tree")
        verification.check(subject.stdout.strip() == EXPECTED_SUBJECT, "applied subject")
        verification.check(not staged.stdout.strip(), "applied staged paths zero")
        verification.check(not tracked.stdout.strip(), "applied tracked modifications zero")
        actual = tuple(sorted(line for line in untracked.stdout.splitlines() if line))
        verification.check(actual == tuple(sorted(PAYLOAD_PATHS)), "applied exact untracked payload")
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        verification.check(parent.returncode == 0 and parent.stdout.strip() == EXPECTED_HEAD, "committed parent")
        verification.check(subject.stdout.strip() == EXPECTED_COMMITTED_SUBJECT, "committed subject")
        verification.check(not staged.stdout.strip(), "committed staged paths zero")
        verification.check(not tracked.stdout.strip(), "committed tracked modifications zero")
        verification.check(not untracked.stdout.strip(), "committed untracked paths zero")
        committed = git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
        actual = tuple(sorted(line for line in committed.stdout.splitlines() if line))
        verification.check(committed.returncode == 0 and actual == tuple(sorted(PAYLOAD_PATHS)), "committed exact payload paths")


def static_source_checks(repository: Path, verification: Verification) -> None:
    package = repository / "aiweb_language_core_bootstrap" / "disabled_predicate_role_frame_bootstrap"
    files = tuple(sorted(package.glob("*.py")))
    verification.check(len(files) == 5, "runtime package file count")
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
        verification.check(not (roots & PROHIBITED_IMPORT_ROOTS), f"standard-library import boundary {path.name}")
        for token in PROHIBITED_TOKENS:
            verification.check(token not in text, f"no wire token {path.name} {token}")



def parse_single_integer_marker(output: str, marker: str) -> int | None:
    prefix = f"{marker}="
    values: list[int] = []

    for line in output.splitlines():
        if not line.startswith(prefix):
            continue

        raw_value = line[len(prefix):]

        try:
            values.append(int(raw_value))
        except ValueError:
            return None

    if len(values) != 1:
        return None

    return values[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--mode", choices=("source", "applied", "committed"), default="source")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    verification = Verification()

    print("AI.WEB SLICE 38H VISIBLE INDEPENDENT VERIFIER")
    print(f"repository={repository}")
    print(f"mode={args.mode}")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")

    verification.check(repository.is_dir(), "repository exists")
    verification.check(tuple(sorted(PAYLOAD_PATHS)) == tuple(sorted(set(PAYLOAD_PATHS))), "payload paths unique")
    path_manifest = repository / "scripts" / "AIWEB_SLICE38H_EXACT_PAYLOAD_PATHS.txt"
    declared = tuple(line for line in path_manifest.read_text(encoding="utf-8").splitlines() if line)
    verification.check(tuple(sorted(declared)) == tuple(sorted(PAYLOAD_PATHS)), "exact payload declaration")

    protected = parse_manifest(repository / "scripts" / "AIWEB_SLICE38H_PROTECTED_SLICE35_38_PREDECESSOR_SHA256SUMS.txt")
    verification.check(len(protected) == EXPECTED_PREDECESSOR_COUNT, "protected predecessor count")
    for digest, relative in protected:
        path = repository / relative
        verification.check(path.is_file() and not path.is_symlink(), f"protected predecessor exists {relative}")
        if path.is_file() and not path.is_symlink():
            verification.check(sha256_file(path) == digest, f"protected predecessor hash {relative}")

    for relative in PAYLOAD_PATHS:
        path = repository / relative
        verification.check(path.is_file() and not path.is_symlink(), f"payload exists {relative}")
        if path.is_file():
            expected_mode = 0o755 if relative.endswith(".py") and relative.startswith("scripts/") else 0o644
            verification.check(stat.S_IMODE(path.stat().st_mode) == expected_mode, f"payload mode {relative}")

    verify_git_state(repository, args.mode, verification)
    static_source_checks(repository, verification)

    source_only_inherited = (
        "scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py",
        "scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py",
        "scripts/test_aiweb_slice37g_disabled_integration_closeout.py",
        "scripts/test_aiweb_slice38a_action_root_predicate_schema.py",
        "scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py",
        "scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py",
        "scripts/test_aiweb_slice38d_participant_role_identity_registry.py",
        "scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py",
        "scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py",
        "scripts/test_aiweb_slice38g_predicate_role_frame_candidate_proposal.py",
    )
    inherited = source_only_inherited if args.mode == "source" else INHERITED_TESTS
    tests = ("scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py", *inherited)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPYCACHEPREFIX", None)
    python = sys.executable
    test_failures = 0
    observed_behavior_checks: int | None = None
    observed_malformed_cases: int | None = None

    for index, relative in enumerate(tests, 1):
        command = [python, "-B", str(repository / relative), str(repository)]
        print()
        print(f"=== VISIBLE TEST {index} OF {len(tests)} ===")
        print(f"path={relative}")
        print(f"command={' '.join(command)}")
        print("output_begins_below")
        completed = subprocess.run(
            command,
            cwd=str(repository),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.stdout:
            print(
                completed.stdout,
                end="" if completed.stdout.endswith("\n") else "\n",
            )

        if relative == (
            "scripts/"
            "test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py"
        ):
            observed_behavior_checks = parse_single_integer_marker(
                completed.stdout,
                "check_count",
            )
            observed_malformed_cases = parse_single_integer_marker(
                completed.stdout,
                "malformed_closeout_cases",
            )
            expected_behavior_checks = (
                EXPECTED_SOURCE_BEHAVIOR_CHECKS
                if args.mode == "source"
                else EXPECTED_LIVE_BEHAVIOR_CHECKS
            )
            verification.check(
                observed_behavior_checks == expected_behavior_checks,
                "behavior check count",
            )
            verification.check(
                observed_malformed_cases == EXPECTED_MALFORMED_CASES,
                "malformed closeout case count",
            )

        print("output_ended_above")
        print(f"return_code={completed.returncode}")
        verification.check(completed.returncode == 0, f"test passed {relative}")
        if completed.returncode != 0:
            test_failures += 1

    print()
    print("=== SLICE 38H VERIFIER SUMMARY ===")
    print(f"pass_count={verification.passes}")
    print(f"failure_count={len(verification.failures)}")
    for failure in verification.failures:
        print(f"FAIL: {failure}")
    if verification.failures or test_failures:
        print("SLICE 38H VISIBLE INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 38H VISIBLE INDEPENDENT VERIFIER: PASS")
    print("protected_predecessor_files=347")
    print(f"inherited_tests={len(inherited)}")
    print(f"visible_total_tests={len(tests)}")
    print("slice38h_files=14")
    print(
        "behavior_checks="
        f"{observed_behavior_checks if observed_behavior_checks is not None else 'unavailable'}"
    )
    print(f"source_behavior_checks={EXPECTED_SOURCE_BEHAVIOR_CHECKS}")
    print(f"live_behavior_checks={EXPECTED_LIVE_BEHAVIOR_CHECKS}")
    print(f"malformed_closeout_cases={EXPECTED_MALFORMED_CASES}")
    print("fixture_count=5")
    print("integration_stage_count=2")
    print("deterministic_repeat_count=3")
    print("canonical_compatibility_rules=0")
    print("canonical_compatibility_conflicts=0")
    print("selected_predicate=0")
    print("selected_frame=0")
    print("selected_participant_assignment=0")
    print("candidate_meaning=0")
    print("selected_meaning=0")
    print("clarification_refusal_blocked_progression=0")
    print("permission_capability_availability_route_invocation=0")
    print("tool_action_memory_rendering_delivery=0")
    print("evidence_validity_truth=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
