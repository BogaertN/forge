#!/usr/bin/env python3
"""Visible independent verifier for AI.Web Slice 39G."""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import os
from pathlib import Path
import selectors
import stat
import subprocess
import sys
import tarfile
import tempfile
import time

EXPECTED_HEAD = "e311e8960b96eff2015b7773b92b16bf2f0dc6a3"
EXPECTED_TREE = "b3fded6b50f123b6b28d48f8d449f15febc0f057"
EXPECTED_SUBJECT = "Slice 39F deterministic candidate meaning constructor"
EXPECTED_COMMITTED_SUBJECT = "Slice 39G MSM-v1 candidate integration"
EXPECTED_PROTECTED_COUNT = 452
EXPECTED_BEHAVIOR_CHECKS = 596
EXPECTED_MALFORMED_CASES = 9
EXPECTED_REJECTIONS = 9

PACKAGE_PATHS = (
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration/__init__.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration/adapter.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration/authority.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration/canonical.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration/identity.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration/schema.py",
    "aiweb_language_core_bootstrap/candidate_meaning_construction/manifest_candidate_integration/validation.py",
)
SCRIPT_PATHS = (
    "scripts/AIWEB_SLICE39G_AUTHORITY_AND_ADAPTER_DECISION.md",
    "scripts/AIWEB_SLICE39G_MSM_V1_CANDIDATE_INTEGRATION_RUNTIME_SPEC.md",
    "scripts/AIWEB_SLICE39G_PROTECTED_PREDECESSOR_SHA256SUMS.txt",
    "scripts/README_aiweb_slice39g_meaning_structure_manifest_candidate_integration.md",
    "scripts/aiweb_slice39g_meaning_structure_manifest_candidate_integration_verify.py",
    "scripts/test_aiweb_slice39g_meaning_structure_manifest_candidate_integration.py",
)
PAYLOAD_PATHS = tuple(sorted(PACKAGE_PATHS + SCRIPT_PATHS))
EXECUTABLE_PATHS = {
    "scripts/aiweb_slice39g_meaning_structure_manifest_candidate_integration_verify.py",
    "scripts/test_aiweb_slice39g_meaning_structure_manifest_candidate_integration.py",
}
CURRENT_TEST = "scripts/test_aiweb_slice39g_meaning_structure_manifest_candidate_integration.py"
PRE_SLICE39G_CONTEXT_TEST = (
    "scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py"
)
SLICE38H_INHERITED_TEST = (
    "scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py"
)
INHERITED_TESTS = (
    "scripts/test_aiweb_slice39f_deterministic_candidate_meaning_constructor.py",
    "scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py",
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
PROHIBITED_IMPORT_ROOTS = {
    "requests", "numpy", "torch", "tensorflow", "transformers",
    "sentence_transformers", "sklearn", "chromadb", "langchain", "openai",
    "ollama", "faiss",
}
PROHIBITED_DIRECT_NAMES = {
    "open", "urlopen", "socket", "Popen", "run", "system", "remove", "unlink",
    "write_text", "write_bytes", "mkdir", "makedirs", "rename",
}
PROHIBITED_SOURCE_TOKENS = (
    "capture_input_event",
    "project_source_field",
    "propose_structural_concept_candidates",
    "propose_predicate_role_frame_candidates",
    "exact_source_text",
    ".source_text",
    "NonSelectionOutcomeRecord(",
    "SelectedGovernedMeaningRecord(",
    "GovernedResultReferenceRecord(",
    "GovernedOutwardMeaningRecord(",
    "ExpressionLinkRecord(",
    "ValidationLinkRecord(",
    "DeliveryContainmentLinkRecord(",
)


class Verification:
    def __init__(self) -> None:
        self.passes = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str) -> None:
        if condition is True:
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
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        result.append((digest, relative))
    return tuple(result)


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def verify_git_state(
    repository: Path,
    mode: str,
    verification: Verification,
) -> None:
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    subject = git(repository, "show", "-s", "--format=%s", "HEAD")
    staged = git(repository, "diff", "--cached", "--name-only")
    tracked = git(repository, "diff", "--name-only")
    untracked = git(repository, "ls-files", "--others", "--exclude-standard")
    verification.check(
        all(
            item.returncode == 0
            for item in (head, tree, subject, staged, tracked, untracked)
        ),
        "Git inspection",
    )
    if mode == "applied":
        verification.check(head.stdout.strip() == EXPECTED_HEAD, "applied head")
        verification.check(tree.stdout.strip() == EXPECTED_TREE, "applied tree")
        verification.check(
            subject.stdout.strip() == EXPECTED_SUBJECT,
            "applied subject",
        )
        verification.check(not staged.stdout.strip(), "applied staged paths zero")
        verification.check(
            not tracked.stdout.strip(),
            "applied tracked modifications zero",
        )
        actual = tuple(
            sorted(line for line in untracked.stdout.splitlines() if line)
        )
        verification.check(
            actual == PAYLOAD_PATHS,
            "applied exact untracked payload",
        )
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        verification.check(
            parent.returncode == 0
            and parent.stdout.strip() == EXPECTED_HEAD,
            "committed parent",
        )
        verification.check(
            subject.stdout.strip() == EXPECTED_COMMITTED_SUBJECT,
            "committed subject",
        )
        verification.check(not staged.stdout.strip(), "committed staged paths zero")
        verification.check(
            not tracked.stdout.strip(),
            "committed tracked modifications zero",
        )
        verification.check(
            not untracked.stdout.strip(),
            "committed untracked paths zero",
        )
        committed = git(
            repository,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
        )
        actual = tuple(
            sorted(line for line in committed.stdout.splitlines() if line)
        )
        verification.check(
            committed.returncode == 0 and actual == PAYLOAD_PATHS,
            "committed exact payload paths",
        )


def static_source_checks(
    repository: Path,
    verification: Verification,
) -> None:
    package = (
        repository
        / "aiweb_language_core_bootstrap"
        / "candidate_meaning_construction"
        / "manifest_candidate_integration"
    )
    files = tuple(sorted(package.glob("*.py")))
    verification.check(
        tuple(path.name for path in files)
        == (
            "__init__.py",
            "adapter.py",
            "authority.py",
            "canonical.py",
            "identity.py",
            "schema.py",
            "validation.py",
        ),
        "exact Slice 39G package files",
    )
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
        except Exception as error:
            verification.check(False, f"AST parse {path.name}: {error}")
            continue
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.level == 0
            ):
                roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    verification.check(
                        node.func.id not in PROHIBITED_DIRECT_NAMES,
                        f"no direct side-effect call {path.name}:{node.func.id}",
                    )
                elif isinstance(node.func, ast.Attribute):
                    verification.check(
                        node.func.attr not in PROHIBITED_DIRECT_NAMES,
                        f"no attribute side-effect call {path.name}:{node.func.attr}",
                    )
        verification.check(
            not (roots & PROHIBITED_IMPORT_ROOTS),
            f"no prohibited import root {path.name}",
        )
        for token in PROHIBITED_SOURCE_TOKENS:
            verification.check(
                token not in text,
                f"no prohibited source token {path.name}:{token}",
            )


def parse_single_integer_marker(output: str, marker: str) -> int | None:
    prefix = f"{marker}="
    values = []
    for line in output.splitlines():
        if line.startswith(prefix):
            try:
                values.append(int(line[len(prefix):]))
            except ValueError:
                return None
    return values[0] if len(values) == 1 else None


def stream_test(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
) -> tuple[int, str]:
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


def stream_source_only_inherited_test(
    repository: Path,
    relative: str,
    *,
    env: dict[str, str],
    verification: Verification,
) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(
        prefix="aiweb_slice39g_inherited_"
    ) as temporary:
        source_only_repository = Path(temporary)
        try:
            os.symlink(
                repository / "aiweb_language_core_bootstrap",
                source_only_repository / "aiweb_language_core_bootstrap",
                target_is_directory=True,
            )
            os.symlink(
                repository / "scripts",
                source_only_repository / "scripts",
                target_is_directory=True,
            )
        except OSError as error:
            verification.check(False, "source-only inherited view creation")
            return 1, f"FAIL: source-only view creation: {error}\n"
        verification.check(
            not (source_only_repository / ".git").exists(),
            "source-only inherited Git metadata absent",
        )
        command = [
            sys.executable,
            "-B",
            str(source_only_repository / relative),
            str(source_only_repository),
        ]
        print("execution_context=source_only_inherited")
        print(f"source_only_repository={source_only_repository}")
        print(f"command={' '.join(command)}")
        return stream_test(
            command,
            cwd=source_only_repository,
            env=env,
        )


def stream_pre_slice39g_context_test(
    repository: Path,
    relative: str,
    *,
    env: dict[str, str],
    verification: Verification,
) -> tuple[int, str]:
    archive = subprocess.run(
        ["git", "-C", str(repository), "archive", "--format=tar", EXPECTED_HEAD],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if archive.returncode != 0:
        verification.check(False, "pre-Slice39G archive creation")
        return 1, archive.stderr.decode("utf-8", errors="replace")
    with tempfile.TemporaryDirectory(
        prefix="aiweb_slice39g_pre_context_"
    ) as temporary:
        source_only_repository = Path(temporary)
        try:
            with tarfile.open(
                fileobj=io.BytesIO(archive.stdout),
                mode="r:",
            ) as handle:
                handle.extractall(source_only_repository)
        except Exception as error:
            verification.check(False, "pre-Slice39G archive extraction")
            return 1, f"FAIL: pre-Slice39G extraction: {error}\n"
        verification.check(
            not (source_only_repository / ".git").exists(),
            "pre-Slice39G context Git metadata absent",
        )
        command = [
            sys.executable,
            "-B",
            str(source_only_repository / relative),
            str(source_only_repository),
        ]
        print("execution_context=accepted_pre_slice39g_source")
        print(f"accepted_commit={EXPECTED_HEAD}")
        print(f"source_only_repository={source_only_repository}")
        print(f"command={' '.join(command)}")
        return stream_test(
            command,
            cwd=source_only_repository,
            env=env,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument(
        "--mode",
        choices=("source", "applied", "committed"),
        default="source",
    )
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    verification = Verification()

    print("AI.WEB SLICE 39G VISIBLE INDEPENDENT VERIFIER")
    print(f"repository={repository}")
    print(f"mode={args.mode}")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")

    verification.check(repository.is_dir(), "repository exists")
    verification.check(len(PAYLOAD_PATHS) == 13, "payload count 13")
    verification.check(
        len(PAYLOAD_PATHS) == len(set(PAYLOAD_PATHS)),
        "payload unique",
    )

    protected_path = (
        repository
        / "scripts"
        / "AIWEB_SLICE39G_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    )
    try:
        protected = parse_manifest(protected_path)
    except Exception as error:
        verification.check(False, f"protected manifest parse: {error}")
        protected = ()
    verification.check(
        len(protected) == EXPECTED_PROTECTED_COUNT,
        "protected predecessor count",
    )
    for digest, relative in protected:
        path = repository / relative
        verification.check(
            path.is_file() and not path.is_symlink(),
            f"protected predecessor exists {relative}",
        )
        if path.is_file() and not path.is_symlink():
            verification.check(
                sha256_file(path) == digest,
                f"protected predecessor hash {relative}",
            )

    for relative in PAYLOAD_PATHS:
        path = repository / relative
        verification.check(
            path.is_file() and not path.is_symlink(),
            f"payload exists {relative}",
        )
        if path.is_file() and not path.is_symlink():
            expected_mode = (
                0o755 if relative in EXECUTABLE_PATHS else 0o644
            )
            verification.check(
                stat.S_IMODE(path.stat().st_mode) == expected_mode,
                f"payload mode {relative}",
            )

    if args.mode != "source":
        verify_git_state(repository, args.mode, verification)
    static_source_checks(repository, verification)

    inherited = () if args.mode == "source" else INHERITED_TESTS
    tests = (CURRENT_TEST, *inherited)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env.pop("PYTHONPYCACHEPREFIX", None)

    test_failures = 0
    observed_checks = None
    observed_malformed = None
    observed_rejections = None
    for index, relative in enumerate(tests, 1):
        print()
        print(f"=== VISIBLE TEST {index} OF {len(tests)} ===")
        print(f"path={relative}")
        print("output_begins_below")
        if relative == PRE_SLICE39G_CONTEXT_TEST:
            return_code, output = stream_pre_slice39g_context_test(
                repository,
                relative,
                env=env,
                verification=verification,
            )
        elif relative == SLICE38H_INHERITED_TEST:
            return_code, output = stream_source_only_inherited_test(
                repository,
                relative,
                env=env,
                verification=verification,
            )
        else:
            command = [
                sys.executable,
                "-B",
                str(repository / relative),
                str(repository),
            ]
            print(f"command={' '.join(command)}")
            return_code, output = stream_test(
                command,
                cwd=repository,
                env=env,
            )
        print("output_ended_above")
        print(f"return_code={return_code}")
        verification.check(return_code == 0, f"test passed {relative}")
        if return_code != 0:
            test_failures += 1
        if relative == CURRENT_TEST:
            observed_checks = parse_single_integer_marker(
                output,
                "check_count",
            )
            observed_malformed = parse_single_integer_marker(
                output,
                "malformed_validation_cases",
            )
            observed_rejections = parse_single_integer_marker(
                output,
                "explicit_rejection_cases",
            )
            verification.check(
                observed_checks == EXPECTED_BEHAVIOR_CHECKS,
                "behavior check count",
            )
            verification.check(
                observed_malformed == EXPECTED_MALFORMED_CASES,
                "malformed case count",
            )
            verification.check(
                observed_rejections == EXPECTED_REJECTIONS,
                "rejection count",
            )
            verification.check(
                "AI.WEB SLICE 39G BEHAVIOR TEST: PASS" in output,
                "Slice 39G pass marker",
            )
            for marker in (
                "adapter_decision=versioned_companion_required",
                "accepted_slice35_schema_modified=0",
                "automatic_migration=0",
                "typed_zero_candidate_manifest=1",
                "one_candidate_manifest_records=1",
                "multiple_candidate_manifest_records=2",
                "candidate_alternative_relationships=2",
                "non_selection_gate_outcomes=0",
                "selected_governed_meanings=0",
                "expression_validation_delivery_links=0",
                "gate_outcome_selected_meaning=0",
                "bootstrap_closeout=0",
            ):
                verification.check(
                    marker in output,
                    f"Slice 39G marker {marker}",
                )

    print()
    print("=== SLICE 39G VERIFIER SUMMARY ===")
    print(f"pass_count={verification.passes}")
    print(f"failure_count={len(verification.failures)}")
    for failure in verification.failures:
        print(f"FAIL: {failure}")
    if verification.failures or test_failures:
        print("SLICE 39G VISIBLE INDEPENDENT VERIFIER: FAIL")
        return 1

    print("SLICE 39G VISIBLE INDEPENDENT VERIFIER: PASS")
    print(f"protected_predecessor_files={EXPECTED_PROTECTED_COUNT}")
    print(f"inherited_tests={len(inherited)}")
    print(f"visible_total_tests={len(tests)}")
    print("slice39g_files=13")
    print(f"behavior_checks={observed_checks}")
    print(f"malformed_validation_cases={observed_malformed}")
    print(f"explicit_rejection_cases={observed_rejections}")
    print("adapter_decision=versioned_companion_required")
    print("accepted_slice35_schema_modified=0")
    print("automatic_migration=0")
    print("zero_one_many_candidate_manifest_integration=1")
    print("candidate_construction_trace_custody=1")
    print("candidate_provenance_custody=1")
    print("candidate_limitation_custody=1")
    print("candidate_alternative_relationship_custody=1")
    print("non_selection_gate_outcomes=0")
    print("selected_governed_meanings=0")
    print("governed_result_outward_meanings=0")
    print("expression_validation_delivery_links=0")
    print("gate_outcome_selected_meaning=0")
    print("truth_evidence_permission=0")
    print("bootstrap_closeout=0")
    print("route_action_memory_rendering_delivery=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
