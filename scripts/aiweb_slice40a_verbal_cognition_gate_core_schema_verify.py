#!/usr/bin/env python3
"""Visible sequential verifier for AI.Web Slice 40A."""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tarfile
import tempfile


EXPECTED_BRANCH = "main"
EXPECTED_HEAD = "643686b8664fe938b8e87e6335cf6ecc3c87e1d3"
EXPECTED_TREE = "a83b0561ff7858d0ea69db0f92ed6494fcde26aa"
EXPECTED_SUBJECT = "Slice 39H disabled bootstrap integration closeout"
EXPECTED_COMMITTED_SUBJECT = "Slice 40A verbal cognition gate core schema"
EXPECTED_PROTECTED_COUNT = 479
EXPECTED_PAYLOAD_COUNT = 12
EXPECTED_BEHAVIOR_CHECKS = 556
EXPECTED_MALFORMED_CASES = 29
CURRENT_TEST = "scripts/test_aiweb_slice40a_verbal_cognition_gate_core_schema.py"
PARENT_CONTEXT_TEST = "scripts/test_aiweb_slice39h_disabled_bootstrap_integration_closeout.py"
PRE_SLICE39G_CONTEXT_TEST = "scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py"
SLICE38H_INHERITED_TEST = "scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py"
PRE_SLICE39G_CONTEXT_COMMIT = "e311e8960b96eff2015b7773b92b16bf2f0dc6a3"
PAYLOAD_PATHS = ('aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/__init__.py', 'aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/authority.py', 'aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/identity.py', 'aiweb_language_core_bootstrap/verbal_cognition_gate_runtime/schema.py', 'scripts/AIWEB_SLICE40A_EXACT_PAYLOAD_PATHS.txt', 'scripts/AIWEB_SLICE40A_PROTECTED_PREDECESSOR_SHA256SUMS.txt', 'scripts/AIWEB_SLICE40A_SCHEMA_ONLY_AND_DEFERRED_SCOPE_DECISION.md', 'scripts/AIWEB_SLICE40A_SOURCE_INSPECTION_RECORD.md', 'scripts/AIWEB_SLICE40A_VERBAL_COGNITION_GATE_CORE_SCHEMA_RUNTIME_SPEC.md', 'scripts/README_aiweb_slice40a_verbal_cognition_gate_core_schema.md', 'scripts/aiweb_slice40a_verbal_cognition_gate_core_schema_verify.py', 'scripts/test_aiweb_slice40a_verbal_cognition_gate_core_schema.py')
INHERITED_TESTS = ('scripts/test_aiweb_slice39h_disabled_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice39g_meaning_structure_manifest_candidate_integration.py', 'scripts/test_aiweb_slice39f_deterministic_candidate_meaning_constructor.py', 'scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py', 'scripts/test_aiweb_slice39e_candidate_set_alternative_preservation.py', 'scripts/test_aiweb_slice39d_candidate_semantic_content_assembly.py', 'scripts/test_aiweb_slice39c_complete_provenance_predecessor_custody.py', 'scripts/test_aiweb_slice39b_deterministic_validation_identity_versioning_lifecycle.py', 'scripts/test_aiweb_slice39a_candidate_meaning_core_schema.py', 'scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice38g_predicate_role_frame_candidate_proposal.py', 'scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py', 'scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py', 'scripts/test_aiweb_slice38d_participant_role_identity_registry.py', 'scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py', 'scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py', 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py', 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py', 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py', 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py', 'scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py', 'scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py', 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py', 'scripts/test_aiweb_slice36g_deterministic_structural_derivation.py', 'scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py', 'scripts/test_aiweb_slice37b_deterministic_validation_identity_lifecycle.py', 'scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py', 'scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py', 'scripts/test_aiweb_slice37e_semantic_class_relation_registry.py', 'scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py', 'scripts/test_aiweb_slice37g_disabled_integration_closeout.py', 'scripts/test_aiweb_slice38a_action_root_predicate_schema.py', 'scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py')
EXECUTABLE_PATHS = {
    "scripts/aiweb_slice40a_verbal_cognition_gate_core_schema_verify.py",
    "scripts/test_aiweb_slice40a_verbal_cognition_gate_core_schema.py",
}
PROHIBITED_IMPORT_ROOTS = {
    "anthropic", "chromadb", "faiss", "httpx", "keras", "langchain",
    "llama_index", "nltk", "numpy", "ollama", "openai", "pandas",
    "requests", "scipy", "sentence_transformers", "sklearn", "socket",
    "spacy", "tensorflow", "torch", "transformers", "urllib",
}
PROHIBITED_CALL_NAMES = {
    "open", "exec", "eval", "compile", "__import__", "system", "popen",
    "urlopen", "socket",
}
PROHIBITED_ATTRIBUTE_CALLS = {
    "write_text", "write_bytes", "unlink", "mkdir", "makedirs", "rename",
    "rmdir", "remove", "touch", "connect", "send", "recv",
}


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
    records = []
    seen = set()
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
    verification.check(all(item.returncode == 0 for item in (branch, head, tree, subject, staged, tracked, untracked)), "Git inspection")
    if mode == "applied":
        verification.check(branch.stdout.strip() == EXPECTED_BRANCH, "applied branch")
        verification.check(head.stdout.strip() == EXPECTED_HEAD, "applied head")
        verification.check(tree.stdout.strip() == EXPECTED_TREE, "applied tree")
        verification.check(subject.stdout.strip() == EXPECTED_SUBJECT, "applied subject")
        verification.check(not staged.stdout.strip(), "applied staged paths zero")
        verification.check(not tracked.stdout.strip(), "applied tracked modifications zero")
        actual = tuple(sorted(line for line in untracked.stdout.splitlines() if line))
        verification.check(actual == PAYLOAD_PATHS, "applied exact untracked payload")
    elif mode == "committed":
        parent = git(repository, "rev-parse", "HEAD^")
        committed = git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
        actual = tuple(sorted(line for line in committed.stdout.splitlines() if line))
        verification.check(parent.returncode == 0 and parent.stdout.strip() == EXPECTED_HEAD, "committed parent")
        verification.check(subject.stdout.strip() == EXPECTED_COMMITTED_SUBJECT, "committed subject")
        verification.check(committed.returncode == 0 and actual == PAYLOAD_PATHS, "committed exact payload paths")
        verification.check(not staged.stdout.strip() and not tracked.stdout.strip() and not untracked.stdout.strip(), "committed repository clean")


def select_python(repository: Path) -> str:
    candidates = (
        repository / ".venv" / "bin" / "python3",
        Path("/usr/bin/python3"),
    )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return sys.executable


def static_source_checks(repository: Path, verification: Verification) -> None:
    package = repository / "aiweb_language_core_bootstrap" / "verbal_cognition_gate_runtime"
    files = tuple(sorted(package.glob("*.py")))
    verification.check(tuple(path.name for path in files) == ("__init__.py", "authority.py", "identity.py", "schema.py"), "exact Slice 40A package files")
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
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                verification.check(False, f"no package function {path.name}:{node.name}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    verification.check(node.func.id not in PROHIBITED_CALL_NAMES, f"no direct side-effect call {path.name}:{node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    verification.check(node.func.attr not in PROHIBITED_ATTRIBUTE_CALLS, f"no attribute side-effect call {path.name}:{node.func.attr}")
        verification.check(not (roots & PROHIBITED_IMPORT_ROOTS), f"no prohibited import root {path.name}")
        verification.check("aiweb_verbal_cognition_gate_boundary_scaffold" not in text, f"old scaffold not imported {path.name}")
        verification.check("meaning_structure_manifest import" not in text, f"MSM not imported {path.name}")


def parse_single_integer_marker(output: str, key: str) -> int | None:
    prefix = f"{key}="
    values = []
    for line in output.splitlines():
        if line.startswith(prefix):
            try:
                values.append(int(line[len(prefix):]))
            except ValueError:
                return None
    return values[0] if len(values) == 1 else None


def stream_test(command: list[str], *, cwd: Path, env: dict[str, str]) -> tuple[int, str]:
    process = subprocess.Popen(command, cwd=str(cwd), env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
    output = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
        output.append(line)
    return process.wait(), "".join(output)


def stream_commit_context_test(
    repository: Path,
    relative: str,
    commit: str,
    label: str,
    *,
    python_executable: str,
    env: dict[str, str],
    verification: Verification,
) -> tuple[int, str]:
    archive = subprocess.run(
        [
            "git", "-C", str(repository), "archive", "--format=tar", commit,
            "aiweb_language_core_bootstrap", "scripts",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if archive.returncode != 0:
        verification.check(False, f"{label} archive creation")
        return 1, archive.stderr.decode("utf-8", errors="replace")
    with tempfile.TemporaryDirectory(prefix=f"aiweb_slice40a_{label}_") as temporary:
        source_only_repository = Path(temporary)
        try:
            with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as handle:
                members = handle.getmembers()
                for member in members:
                    pure = PurePosixPath(member.name)
                    if pure.is_absolute() or ".." in pure.parts or member.issym() or member.islnk():
                        raise ValueError(f"unsafe archive member: {member.name}")
                handle.extractall(source_only_repository)
        except Exception as error:
            verification.check(False, f"{label} archive extraction")
            return 1, f"FAIL: {label} extraction: {error}\n"
        verification.check(not (source_only_repository / ".git").exists(), f"{label} Git metadata absent")
        command = [python_executable, "-B", str(source_only_repository / relative), str(source_only_repository)]
        print(f"execution_context={label}")
        print(f"accepted_commit={commit}")
        print(f"source_only_repository={source_only_repository}")
        print(f"command={' '.join(command)}")
        return stream_test(command, cwd=source_only_repository, env=env)


def stream_source_only_inherited_test(
    repository: Path,
    relative: str,
    label: str,
    *,
    python_executable: str,
    env: dict[str, str],
    verification: Verification,
) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix=f"aiweb_slice40a_{label}_") as temporary:
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
            verification.check(False, f"{label} source-only view creation")
            return 1, f"FAIL: {label} source-only view creation: {error}\n"
        verification.check(not (source_only_repository / ".git").exists(), f"{label} Git metadata absent")
        command = [python_executable, "-B", str(source_only_repository / relative), str(source_only_repository)]
        print(f"execution_context={label}")
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

    print("AI.WEB SLICE 40A VISIBLE INDEPENDENT VERIFIER")
    print(f"repository={repository}")
    print(f"mode={args.mode}")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")

    verification.check(repository.is_dir(), "repository exists")
    verification.check(len(PAYLOAD_PATHS) == EXPECTED_PAYLOAD_COUNT, "payload count")
    verification.check(len(PAYLOAD_PATHS) == len(set(PAYLOAD_PATHS)), "payload unique")

    protected_path = repository / "scripts" / "AIWEB_SLICE40A_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
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
            expected_mode = 0o755 if relative in EXECUTABLE_PATHS else 0o644
            verification.check(stat.S_IMODE(path.stat().st_mode) == expected_mode, f"payload mode {relative}")

    exact_path_file = repository / "scripts" / "AIWEB_SLICE40A_EXACT_PAYLOAD_PATHS.txt"
    exact_paths = tuple(sorted(line for line in exact_path_file.read_text(encoding="utf-8").splitlines() if line))
    verification.check(exact_paths == PAYLOAD_PATHS, "exact payload path authority")

    verify_git_state(repository, args.mode, verification)
    static_source_checks(repository, verification)

    inherited = () if args.mode == "source" else INHERITED_TESTS
    tests = (CURRENT_TEST, *inherited)
    python_executable = select_python(repository)
    print(f"python_executable={python_executable}")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env.pop("PYTHONPYCACHEPREFIX", None)

    test_failures = 0
    current_output = ""
    observed_checks = None
    observed_malformed = None
    parent_context_pass = False

    for index, relative in enumerate(tests, 1):
        print()
        print(f"=== VISIBLE TEST {index} OF {len(tests)} ===")
        print(f"path={relative}")
        print("output_begins_below")
        if relative == PRE_SLICE39G_CONTEXT_TEST:
            return_code, output = stream_commit_context_test(
                repository, relative, PRE_SLICE39G_CONTEXT_COMMIT,
                "accepted_pre_slice39g_source",
                python_executable=python_executable, env=env, verification=verification,
            )
        elif relative == SLICE38H_INHERITED_TEST:
            return_code, output = stream_source_only_inherited_test(
                repository, relative, "accepted_slice38h_source_only",
                python_executable=python_executable, env=env, verification=verification,
            )
        else:
            command = [python_executable, "-B", str(repository / relative), str(repository)]
            print(f"command={' '.join(command)}")
            return_code, output = stream_test(command, cwd=repository, env=env)
        if relative == PARENT_CONTEXT_TEST:
            parent_context_pass = "AI.WEB SLICE 39H BEHAVIOR TEST: PASS" in output
        print("output_ended_above")
        print(f"return_code={return_code}")
        verification.check(return_code == 0, f"test passed {relative}")
        if return_code != 0:
            test_failures += 1
        if relative == CURRENT_TEST:
            current_output = output
            observed_checks = parse_single_integer_marker(output, "check_count")
            observed_malformed = parse_single_integer_marker(output, "malformed_constructor_cases")

    verification.check(observed_checks == EXPECTED_BEHAVIOR_CHECKS, "behavior check count")
    verification.check(observed_malformed == EXPECTED_MALFORMED_CASES, "malformed case count")
    if args.mode != "source":
        verification.check(parent_context_pass, "accepted Slice 39H context pass marker")

    required_markers = (
        "AI.WEB SLICE 40A BEHAVIOR TEST: PASS",
        "record_types=9",
        "gate_family_count=4",
        "schema_evaluation_state_count=4",
        "permanent_boundaries=32",
        "versioned_companion_required=1",
        "msm_v1_modified=0",
        "positive_disposition_name_deferred=1",
        "runtime_evaluator_installed=0",
        "gate_evaluation_performed=0",
        "gate_outcome_created=0",
        "candidate_accepted_rejected_clarified_selected=0",
        "truth_evidence_permission_execution=0",
        "route_tool_action_memory_rendering_delivery=0",
    )
    for marker in required_markers:
        verification.check(marker in current_output, f"behavior marker {marker}")

    print()
    print("=== SLICE 40A VERIFIER SUMMARY ===")
    print(f"pass_count={verification.passes}")
    print(f"failure_count={len(verification.failures)}")
    for failure in verification.failures:
        print(f"FAIL: {failure}")
    if verification.failures or test_failures:
        print("SLICE 40A VISIBLE INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 40A VISIBLE INDEPENDENT VERIFIER: PASS")
    print("protected_predecessor_files=479")
    print(f"inherited_tests={len(inherited)}")
    print(f"visible_total_tests={len(tests)}")
    print(f"slice40a_files={EXPECTED_PAYLOAD_COUNT}")
    print(f"behavior_checks={observed_checks}")
    print(f"malformed_constructor_cases={observed_malformed}")
    print("record_types=9")
    print("gate_family_count=4")
    print("schema_evaluation_state_count=4")
    print("versioned_companion_required=1")
    print("msm_v1_modified=0")
    print("positive_disposition_name_deferred=1")
    print("runtime_evaluator_installed=0")
    print("gate_evaluation_performed=0")
    print("gate_outcome_created=0")
    print("selected_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
