#!/usr/bin/env python3
"""Visible sequential verifier for AI.Web Slice 41D.

The verifier proves the additive selection-eligibility evaluator, protects every
accepted predecessor file, and visibly runs the current behavior test plus all
inherited accepted language-core tests in applied or committed mode. It never
modifies, stages, commits, pushes, hides test workers, or suppresses output.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

EXPECTED_BRANCH = "main"
EXPECTED_HEAD = 'd26423ccd5ed7c71b2f29f19ffd40c1010d87b98'
EXPECTED_TREE = 'd900c3e1e50bc9d94a0340ae0d0f60128985d273'
EXPECTED_SUBJECT = 'Slice 41C deterministic selection eligibility evaluation runtime'
EXPECTED_COMMITTED_SUBJECT = 'Slice 41D selected meaning construction alternative preservation'
EXPECTED_PROTECTED_COUNT = 629
EXPECTED_PAYLOAD_COUNT = 15
CURRENT_TEST = 'scripts/test_aiweb_slice41d_selected_meaning_construction_alternative_preservation.py'
PARENT_CONTEXT_TEST = 'scripts/test_aiweb_slice41c_selection_eligibility_evaluation_runtime.py'
PRE_SLICE39G_CONTEXT_TEST = 'scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py'
SLICE38H_INHERITED_TEST = 'scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py'
PRE_SLICE39G_CONTEXT_COMMIT = 'e311e8960b96eff2015b7773b92b16bf2f0dc6a3'
INHERITED_TESTS = ('scripts/test_aiweb_slice41c_selection_eligibility_evaluation_runtime.py', 'scripts/test_aiweb_slice41b_deterministic_validation_identity_versioning_lifecycle.py', 'scripts/test_aiweb_slice41a_selected_meaning_runtime_core_schema.py', 'scripts/test_aiweb_slice40h_msm_gate_integration_disabled_bootstrap_closeout.py', 'scripts/test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py', 'scripts/test_aiweb_slice40f_recoverable_purpose_runtime.py', 'scripts/test_aiweb_slice40e_connectedness_gate_runtime.py', 'scripts/test_aiweb_slice40d_congruity_gate_runtime.py', 'scripts/test_aiweb_slice40c_expectancy_gate_runtime.py', 'scripts/test_aiweb_slice40b_deterministic_validation_identity_versioning_lifecycle.py', 'scripts/test_aiweb_slice40a_verbal_cognition_gate_core_schema.py', 'scripts/test_aiweb_slice39h_disabled_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice39g_meaning_structure_manifest_candidate_integration.py', 'scripts/test_aiweb_slice39f_deterministic_candidate_meaning_constructor.py', 'scripts/test_aiweb_slice39b_39e_roadmap_continuity_correction.py', 'scripts/test_aiweb_slice39e_candidate_set_alternative_preservation.py', 'scripts/test_aiweb_slice39d_candidate_semantic_content_assembly.py', 'scripts/test_aiweb_slice39c_complete_provenance_predecessor_custody.py', 'scripts/test_aiweb_slice39b_deterministic_validation_identity_versioning_lifecycle.py', 'scripts/test_aiweb_slice39a_candidate_meaning_core_schema.py', 'scripts/test_aiweb_slice38h_disabled_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice38g_predicate_role_frame_candidate_proposal.py', 'scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py', 'scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py', 'scripts/test_aiweb_slice38d_participant_role_identity_registry.py', 'scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py', 'scripts/test_aiweb_slice24_full_regression_acceptance_bundle_scaffold.py', 'scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py', 'scripts/test_aiweb_slice31_disabled_bootstrap_adapter.py', 'scripts/test_aiweb_slice32_accepted_boundary_component_loading.py', 'scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py', 'scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py', 'scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py', 'scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py', 'scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py', 'scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py', 'scripts/test_aiweb_slice35e_meaning_structure_manifest_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice36a_input_event_source_custody.py', 'scripts/test_aiweb_slice36b0_rsoc_fbsc_language_operator_contract.py', 'scripts/test_aiweb_slice36b_deterministic_source_field_projection.py', 'scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py', 'scripts/test_aiweb_slice36d_resonant_operator_candidate_binding.py', 'scripts/test_aiweb_slice36e_candidate_resonant_phase_trail.py', 'scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py', 'scripts/test_aiweb_slice36g_deterministic_structural_derivation.py', 'scripts/test_aiweb_slice36h_bounded_bootstrap_integration_closeout.py', 'scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py', 'scripts/test_aiweb_slice37b_deterministic_validation_identity_lifecycle.py', 'scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py', 'scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py', 'scripts/test_aiweb_slice37e_semantic_class_relation_registry.py', 'scripts/test_aiweb_slice37f_structural_concept_candidate_proposal.py', 'scripts/test_aiweb_slice37g_disabled_integration_closeout.py', 'scripts/test_aiweb_slice38a_action_root_predicate_schema.py', 'scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py')


class VerificationLedger:
    def __init__(self) -> None:
        self.pass_count = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if condition is True:
            self.pass_count += 1
        else:
            self.failures.append(label)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_hash_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        try:
            expected_hash, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"invalid manifest line {line_number}") from error
        pure = PurePosixPath(relative)
        if (
            len(expected_hash) != 64
            or any(character not in "0123456789abcdef" for character in expected_hash)
            or pure.is_absolute()
            or ".." in pure.parts
            or relative in seen
        ):
            raise ValueError(f"unsafe manifest line {line_number}")
        seen.add(relative)
        entries.append((expected_hash, relative))
    return tuple(entries)


def select_python(repository: Path) -> str:
    candidate = repository / ".venv" / "bin" / "python3"
    return str(candidate) if candidate.is_file() else "/usr/bin/python3"


def run_visible(command: list[str], cwd: Path, env: dict[str, str]) -> tuple[int, str]:
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    output: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        output.append(line)
    return process.wait(), "".join(output)


def run_commit_context(
    repository: Path,
    relative: str,
    commit: str,
    python_executable: str,
    env: dict[str, str],
    ledger: VerificationLedger,
) -> tuple[int, str]:
    archive = subprocess.run(
        ["git", "-C", str(repository), "archive", "--format=tar", commit,
         "aiweb_language_core_bootstrap", "scripts"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if archive.returncode != 0:
        ledger.check(False, "pre-Slice-39G source archive")
        return 1, archive.stderr.decode(errors="replace")
    with tempfile.TemporaryDirectory(prefix="aiweb_slice41d_pre39g_") as temporary:
        root = Path(temporary)
        try:
            with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as handle:
                members = handle.getmembers()
                for member in members:
                    pure = PurePosixPath(member.name)
                    if pure.is_absolute() or ".." in pure.parts or member.issym() or member.islnk():
                        raise ValueError(member.name)
                handle.extractall(root, members=members)
        except Exception as error:
            ledger.check(False, "pre-Slice-39G source extraction")
            return 1, str(error)
        print("execution_context=accepted_pre_slice39g_source")
        print("accepted_commit=" + commit)
        print("source_only_repository=" + str(root))
        return run_visible(
            [python_executable, "-B", str(root / relative), str(root)], root, env
        )


def run_source_only(
    repository: Path,
    relative: str,
    python_executable: str,
    env: dict[str, str],
    ledger: VerificationLedger,
) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="aiweb_slice41d_slice38h_") as temporary:
        root = Path(temporary)
        try:
            os.symlink(
                repository / "aiweb_language_core_bootstrap",
                root / "aiweb_language_core_bootstrap",
                target_is_directory=True,
            )
            os.symlink(repository / "scripts", root / "scripts", target_is_directory=True)
        except OSError as error:
            ledger.check(False, "Slice 38H source-only view")
            return 1, str(error)
        print("execution_context=accepted_slice38h_source_only")
        print("source_only_repository=" + str(root))
        return run_visible(
            [python_executable, "-B", str(root / relative), str(root)], root, env
        )


def verify_source_contract(repository: Path, ledger: VerificationLedger) -> None:
    parent = repository / "aiweb_language_core_bootstrap" / "selected_meaning_runtime"
    parent_files = (
        tuple(sorted(path.name for path in parent.iterdir() if path.is_file()))
        if parent.is_dir() else ()
    )
    ledger.check(
        parent_files == ("__init__.py", "authority.py", "identity.py", "schema.py"),
        "accepted Slice 41A parent files unchanged",
    )
    governed = parent / "governed_lifecycle"
    governed_files = (
        tuple(sorted(path.name for path in governed.iterdir() if path.is_file()))
        if governed.is_dir() else ()
    )
    ledger.check(
        governed_files == (
            "__init__.py", "canonical.py", "identity.py", "lifecycle.py",
            "rules.py", "schema.py", "validation.py",
        ),
        "accepted Slice 41B package unchanged",
    )
    eligibility = parent / "eligibility_evaluation"
    eligibility_files = (
        tuple(sorted(path.name for path in eligibility.iterdir() if path.is_file()))
        if eligibility.is_dir() else ()
    )
    ledger.check(
        eligibility_files == (
            "__init__.py", "authority.py", "canonical.py", "evaluator.py",
            "identity.py", "schema.py", "validation.py",
        ),
        "accepted Slice 41C package unchanged",
    )
    package = parent / "selected_meaning_construction"
    expected_package_files = (
        "__init__.py", "authority.py", "canonical.py", "constructor.py",
        "identity.py", "schema.py", "validation.py",
    )
    actual = (
        tuple(sorted(path.name for path in package.iterdir() if path.is_file()))
        if package.is_dir() else ()
    )
    ledger.check(actual == expected_package_files, "exact Slice 41D package file set")

    prohibited_import_roots = {
        "anthropic", "chromadb", "faiss", "httpx", "keras", "langchain",
        "llama_index", "nltk", "numpy", "ollama", "openai", "pandas",
        "random", "requests", "scipy", "sentence_transformers", "sklearn",
        "socket", "spacy", "subprocess", "tensorflow", "time", "torch",
        "transformers", "urllib", "uuid",
    }
    prohibited_calls = {
        "open", "exec", "eval", "compile", "__import__", "system", "popen",
        "urlopen", "socket",
    }
    prohibited_attributes = {
        "write_text", "write_bytes", "unlink", "mkdir", "makedirs", "rename",
        "rmdir", "remove", "touch", "connect", "send", "recv",
    }
    prohibited_functions = {
        "rank_candidate", "choose_safest_candidate", "choose_first_candidate",
        "choose_only_candidate", "score_candidate", "classify_with_model",
        "integrate_selected_meaning_into_manifest", "render", "deliver",
    }
    prohibited_call_tokens = (
        "semantic_similarity(", "nearest_known(", "confidence_score(",
        "probability_score(", "model.predict(",
        "manifest.selected_governed_meanings.append(",
    )
    for name in expected_package_files:
        path = package / name
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            ledger.check(False, "AST parse " + name)
            continue
        ledger.check(True, "AST parse " + name)
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ledger.check(
                    node.name not in prohibited_functions,
                    f"no prohibited function {name}:{node.name}",
                )
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    ledger.check(
                        node.func.id not in prohibited_calls,
                        f"no prohibited call {name}:{node.func.id}",
                    )
                elif isinstance(node.func, ast.Attribute):
                    ledger.check(
                        node.func.attr not in prohibited_attributes,
                        f"no prohibited attribute call {name}:{node.func.attr}",
                    )
        ledger.check(
            imported_roots.isdisjoint(prohibited_import_roots),
            "no prohibited imports in " + name,
        )
        for token in prohibited_call_tokens:
            ledger.check(
                token not in source,
                f"no prohibited implementation token {name}:{token}",
            )
    constructor_source = (package / "constructor.py").read_text(encoding="utf-8")
    ledger.check(
        "SelectedGovernedMeaningRecord(" in constructor_source,
        "dormant selected governed meaning record constructed",
    )
    ledger.check(
        "construct_selected_meaning_package" in constructor_source,
        "selected meaning constructor API installed",
    )
    ledger.check(
        "MeaningStructureManifestV1(" not in constructor_source,
        "no MSM-v1 manifest construction or mutation",
    )

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--mode", choices=("source", "applied", "committed"), default="source")
    arguments = parser.parse_args()
    repository = Path(arguments.repository).resolve()
    ledger = VerificationLedger()

    exact_paths_file = repository / "scripts/AIWEB_SLICE41D_EXACT_PAYLOAD_PATHS.txt"
    protected_file = repository / "scripts/AIWEB_SLICE41D_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    try:
        payload_paths = tuple(sorted(
            line for line in exact_paths_file.read_text(encoding="utf-8").splitlines() if line
        ))
        protected = parse_hash_manifest(protected_file)
    except Exception as error:
        print("manifest_error=" + str(error))
        return 1

    ledger.check(len(protected) == EXPECTED_PROTECTED_COUNT, "protected predecessor count")
    protected_names = {name for _, name in protected}
    ledger.check(protected_names.isdisjoint(payload_paths), "protected and payload paths disjoint")
    for expected_hash, relative in protected:
        path = repository / relative
        ledger.check(path.is_file() and not path.is_symlink(), "protected predecessor exists " + relative)
        ledger.check(path.is_file() and sha256_file(path) == expected_hash, "protected predecessor hash " + relative)

    ledger.check(len(payload_paths) == EXPECTED_PAYLOAD_COUNT, "exact payload path count")
    ledger.check(tuple(sorted(payload_paths)) == payload_paths, "exact payload paths sorted")
    ledger.check(len(payload_paths) == len(set(payload_paths)), "exact payload paths unique")
    for relative in payload_paths:
        path = repository / relative
        expected_mode = 0o755 if relative.startswith("scripts/test_") or relative.startswith("scripts/aiweb_") else 0o644
        ledger.check(path.is_file() and not path.is_symlink(), "payload exists " + relative)
        ledger.check(
            path.is_file() and stat.S_IMODE(path.stat().st_mode) == expected_mode,
            "payload mode " + relative,
        )

    verify_source_contract(repository, ledger)

    if arguments.mode != "source":
        branch = git(repository, "branch", "--show-current")
        head = git(repository, "rev-parse", "HEAD")
        tree = git(repository, "rev-parse", "HEAD^{tree}")
        subject = git(repository, "show", "-s", "--format=%s", "HEAD")
        staged = git(repository, "diff", "--cached", "--name-only")
        tracked = git(repository, "diff", "--name-only")
        untracked = git(repository, "ls-files", "--others", "--exclude-standard")
        ledger.check(
            branch.returncode == 0 and branch.stdout.strip() == EXPECTED_BRANCH,
            "branch",
        )
        if arguments.mode == "applied":
            ledger.check(head.stdout.strip() == EXPECTED_HEAD, "applied base HEAD")
            ledger.check(tree.stdout.strip() == EXPECTED_TREE, "applied base tree")
            ledger.check(subject.stdout.strip() == EXPECTED_SUBJECT, "applied base subject")
            ledger.check(not staged.stdout.strip(), "applied staged paths zero")
            ledger.check(not tracked.stdout.strip(), "applied tracked modifications zero")
            ledger.check(
                tuple(sorted(untracked.stdout.splitlines())) == payload_paths,
                "applied exact untracked paths",
            )
        else:
            parent = git(repository, "rev-parse", "HEAD^")
            committed = git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD")
            ledger.check(parent.stdout.strip() == EXPECTED_HEAD, "committed parent")
            ledger.check(subject.stdout.strip() == EXPECTED_COMMITTED_SUBJECT, "committed subject")
            ledger.check(
                tuple(sorted(committed.stdout.splitlines())) == payload_paths,
                "committed exact paths",
            )
            ledger.check(
                not staged.stdout.strip() and not tracked.stdout.strip() and not untracked.stdout.strip(),
                "committed tree clean",
            )

    tests = (CURRENT_TEST,) if arguments.mode == "source" else (CURRENT_TEST, *INHERITED_TESTS)
    python_executable = select_python(repository)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = str(repository)
    env.pop("PYTHONPYCACHEPREFIX", None)
    current_output = ""
    failed_tests = 0
    for index, relative in enumerate(tests, 1):
        print(f"\n=== VISIBLE TEST {index} OF {len(tests)} ===")
        print("path=" + relative)
        print("output_begins_below")
        if relative == PRE_SLICE39G_CONTEXT_TEST:
            return_code, output = run_commit_context(
                repository, relative, PRE_SLICE39G_CONTEXT_COMMIT,
                python_executable, env, ledger,
            )
        elif relative == SLICE38H_INHERITED_TEST:
            return_code, output = run_source_only(
                repository, relative, python_executable, env, ledger,
            )
        else:
            return_code, output = run_visible(
                [python_executable, "-B", str(repository / relative), str(repository)],
                repository,
                env,
            )
        print("output_ended_above")
        print("return_code=" + str(return_code))
        ledger.check(return_code == 0, "test " + relative)
        failed_tests += int(return_code != 0)
        if relative == CURRENT_TEST:
            current_output = output
        if relative == PARENT_CONTEXT_TEST:
            ledger.check(
                "AI.WEB SLICE 41C BEHAVIOR TEST: PASS" in output,
                "Slice 41C context marker",
            )

    markers = (
        "AI.WEB SLICE 41D BEHAVIOR TEST: PASS",
        "selected_meaning_packages=1",
        "successful_slice41c_eligibility_required=1",
        "exact_selected_candidate_identity_and_lineage=1",
        "exact_semantic_content_copy=1",
        "authority_sensitive_distinctions_preserved=1",
        "inherited_limitations_and_blocked_consequences=1",
        "every_non_selected_candidate_preserved=1",
        "unresolved_alternatives_preserved_separately=1",
        "ambiguity_and_clarification_ancestry_preserved=1",
        "deterministic_selection_trace_and_receipt=1",
        "selected_candidate_only_candidate_claim=0",
        "semantic_enrichment=0",
        "semantic_deletion=0",
        "alternatives_deleted=0",
        "candidate_ranked=0",
        "msm_v1_modified=0",
        "governed_outward_meaning_created=0",
        "truth_evidence_permission_execution=0",
        "route_tool_action_memory_rendering_delivery=0",
        "language_model_hidden_classifier_similarity=0",
    )
    for marker in markers:
        ledger.check(marker in current_output, "current behavior marker " + marker)

    print("\n=== SLICE 41D VERIFIER SUMMARY ===")
    print("pass_count=" + str(ledger.pass_count))
    print("failure_count=" + str(len(ledger.failures)))
    for failure in ledger.failures:
        print("FAIL: " + failure)
    if ledger.failures or failed_tests:
        print("SLICE 41D VISIBLE INDEPENDENT VERIFIER: FAIL")
        return 1
    print("SLICE 41D VISIBLE INDEPENDENT VERIFIER: PASS")
    print("protected_predecessor_files=629")
    print("inherited_tests=" + str(len(tests) - 1))
    print("visible_total_tests=" + str(len(tests)))
    print("slice41d_files=15")
    print("selected_meaning_construction_runtime=1")
    print("successful_slice41c_eligibility_required=1")
    print("selected_meaning_created=1")
    print("selection_performed=1")
    print("candidate_ranked=0")
    print("every_non_selected_candidate_preserved=1")
    print("unresolved_alternatives_preserved_separately=1")
    print("semantic_enrichment=0")
    print("semantic_deletion=0")
    print("alternatives_deleted=0")
    print("msm_v1_modified=0")
    print("governed_outward_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
