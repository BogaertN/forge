#!/usr/bin/env python3
"""Visible verifier for Slice 42A outward-expression core schema.

This verifier protects every accepted Slice 30-41 predecessor path, verifies the
additive schema-only package, runs the current behavior test visibly, and then
runs the accepted Slice 41F verifier against an exact temporary checkout of the
accepted Slice 41F commit so all 58 inherited visible language-core tests remain
exercised. It does not modify the target repository, stage, commit, fetch, pull,
push, hide workers, or suppress test output.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath


EXPECTED_BRANCH = "main"
EXPECTED_HEAD = "661ff1e17d8d4a982641ca39dc150b23bbb766e9"
EXPECTED_TREE = "e56c9af88be9b845de534c62c9b82fa6af960f3f"
EXPECTED_SUBJECT = "Slice 41F disabled bootstrap integration and Slice 41 closeout"
EXPECTED_COMMITTED_SUBJECT = (
    "Slice 42A outward expression runtime core schema and authority contract"
)
EXPECTED_PROTECTED_COUNT = 674
EXPECTED_PAYLOAD_COUNT = 12
EXPECTED_INHERITED_VISIBLE_TESTS = 58
CURRENT_TEST = (
    "scripts/test_aiweb_slice42a_outward_expression_runtime_core_schema.py"
)
INHERITED_VERIFIER = (
    "scripts/aiweb_slice41f_disabled_bootstrap_integration_and_slice41_closeout_verify.py"
)
PACKAGE_RELATIVE = "aiweb_language_core_bootstrap/outward_expression_runtime"
EXACT_PACKAGE_FILES = (
    "__init__.py",
    "authority.py",
    "identity.py",
    "schema.py",
)


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
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
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


def run_visible(
    command: list[str],
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
    )
    output: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        output.append(line)
    return process.wait(), "".join(output)


def run_inherited_slice41f_verifier(
    repository: Path,
    env: dict[str, str],
) -> tuple[int, str]:
    """Run Slice 41F from an exact checkout with deterministic POSIX modes.

    Git records only the executable bit. A checkout otherwise applies the caller's
    umask, so a normal collaborative umask such as 0002 produces 0664/0775 paths
    even though the committed index modes are 100644/100755. Slice 41F's accepted
    verifier intentionally checks exact 0644/0755 working-tree modes. Temporarily
    using umask 0022 for this isolated checkout makes that proof independent of the
    operator shell without changing any file in the live repository.
    """
    previous_umask = os.umask(0o022)
    try:
        with tempfile.TemporaryDirectory(prefix="aiweb_slice42a_slice41f_") as temporary:
            checkout = Path(temporary) / "slice41f"
            cloned = subprocess.run(
                [
                    "git",
                    "clone",
                    "--quiet",
                    "--shared",
                    "--no-checkout",
                    str(repository),
                    str(checkout),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                env=env,
            )
            if cloned.returncode != 0:
                output = "temporary Slice 41F clone failed\n" + cloned.stdout
                print(output, end="" if output.endswith("\n") else "\n")
                return cloned.returncode, output

            checked_out = subprocess.run(
                [
                    "git",
                    "-C",
                    str(checkout),
                    "checkout",
                    "--quiet",
                    "-B",
                    EXPECTED_BRANCH,
                    EXPECTED_HEAD,
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                env=env,
            )
            if checked_out.returncode != 0:
                output = "temporary Slice 41F checkout failed\n" + checked_out.stdout
                print(output, end="" if output.endswith("\n") else "\n")
                return checked_out.returncode, output

            predecessor_python = select_python(checkout)
            predecessor_env = env.copy()
            predecessor_env["PYTHONPATH"] = str(checkout)
            return run_visible(
                [
                    predecessor_python,
                    "-B",
                    str(checkout / INHERITED_VERIFIER),
                    str(checkout),
                    "--mode",
                    "committed",
                ],
                checkout,
                predecessor_env,
            )
    finally:
        os.umask(previous_umask)


def verify_source_contract(
    repository: Path,
    ledger: VerificationLedger,
) -> None:
    package = repository / PACKAGE_RELATIVE
    actual_package_files = (
        tuple(sorted(path.name for path in package.iterdir() if path.is_file()))
        if package.is_dir()
        else ()
    )
    ledger.check(
        actual_package_files == EXACT_PACKAGE_FILES,
        "exact Slice 42A package file set",
    )

    allowed_import_roots = {
        "__future__",
        "dataclasses",
        "enum",
        "typing",
    }
    prohibited_calls = {
        "open",
        "exec",
        "eval",
        "compile",
        "__import__",
        "system",
        "popen",
        "urlopen",
        "socket",
    }
    prohibited_attributes = {
        "read_text",
        "read_bytes",
        "write_text",
        "write_bytes",
        "open",
        "unlink",
        "mkdir",
        "makedirs",
        "rename",
        "rmdir",
        "remove",
        "touch",
        "connect",
        "send",
        "recv",
    }
    prohibited_tokens = (
        "GovernedOutwardMeaningRecord(",
        "ExpressionLinkRecord(",
        "ValidationLinkRecord(",
        "DeliveryContainmentLinkRecord(",
        "integrate_selected_meaning_into_manifest(",
        "append_lifecycle_successor(",
        "render(",
        "deliver(",
        "invoke_tool(",
        "write_memory(",
        "requests.",
        "subprocess.",
        "socket.",
        "openai.",
        "ollama.",
        "semantic_similarity(",
        "nearest_known(",
        "confidence_score(",
        "probability_score(",
    )

    for name in EXACT_PACKAGE_FILES:
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
                imported_roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.level == 0
            ):
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ledger.check(False, f"schema package contains function {name}:{node.name}")
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
            imported_roots.issubset(allowed_import_roots),
            "only standard schema imports in " + name,
        )
        for token in prohibited_tokens:
            ledger.check(
                token not in source,
                f"no prohibited implementation token {name}:{token}",
            )

    authority_source = (package / "authority.py").read_text(encoding="utf-8")
    schema_source = (package / "schema.py").read_text(encoding="utf-8")
    identity_source = (package / "identity.py").read_text(encoding="utf-8")

    required_schema_types = (
        "SelectedMeaningExpressionSourceCustodyRecord",
        "OutwardExpressionAuthorityRequirementRecord",
        "ExpressionPreservationObligationCustodyRecord",
        "ExpressionEligibilityStatusRecord",
        "GovernedOutwardMeaningBoundaryRecord",
        "ExpressionPlanBoundaryRecord",
        "RealizedExpressionBoundaryRecord",
        "ExpressionTraceBoundaryRecord",
        "ExpressionReceiptBoundaryRecord",
        "OutwardExpressionRuntimeSchemaRecord",
    )
    for name in required_schema_types:
        ledger.check(
            f"class {name}" in schema_source,
            "required schema type " + name,
        )

    required_obligation_fields = (
        "active_scope_refs",
        "certainty_level_refs",
        "evidence_status_refs",
        "inherited_limitation_refs",
        "required_caveat_refs",
        "refusal_relevant_boundary_refs",
        "unresolved_condition_refs",
        "memory_authority_refs",
        "external_resource_status_refs",
        "delivery_authority_refs",
    )
    for name in required_obligation_fields:
        ledger.check(name in schema_source, "required obligation field " + name)

    required_boundary_tokens = (
        "selected_meaning_may_not_be_rewritten",
        "candidate_alternatives_may_not_be_deleted",
        "unresolved_state_may_not_be_silently_resolved",
        "uncertainty_may_not_be_upgraded",
        "evidence_status_may_not_be_upgraded",
        "required_caveats_may_not_be_omitted",
        "refusal_may_not_be_softened_into_permission",
        "realized_expression_is_not_echo_validation",
        "echo_validation_belongs_to_slice43",
        "gp014_is_not_superseded",
    )
    for token in required_boundary_tokens:
        ledger.check(token in authority_source, "required boundary " + token)

    ledger.check(
        EXPECTED_HEAD in identity_source
        and EXPECTED_TREE in identity_source
        and EXPECTED_SUBJECT in identity_source,
        "accepted parent identity exact",
    )
    ledger.check(
        "deferred_to_slice42g_exact_additive_adapter" in authority_source,
        "MSM additive adapter deferred to Slice 42G",
    )
    ledger.check(
        "SURFACE_REALIZATION_ALLOWED: Final[bool] = False" in authority_source,
        "surface realization disabled",
    )
    ledger.check(
        "ECHO_VALIDATION_ALLOWED: Final[bool] = False" in authority_source,
        "Echo validation disabled",
    )
    ledger.check(
        "DELIVERY_AUTHORITY_ALLOWED: Final[bool] = False" in authority_source,
        "delivery authority disabled",
    )
    ledger.check(
        "human_readable_text_produced: bool = field(default=False, init=False)"
        in schema_source,
        "human-readable text remains absent",
    )
    ledger.check(
        "msm_v1_schema_modified: bool = field(default=False, init=False)"
        in schema_source,
        "MSM-v1 mutation remains false",
    )
    ledger.check(
        "echo_validation_performed: bool = field(default=False, init=False)"
        in schema_source,
        "Echo validation remains false",
    )
    ledger.check(
        "gp014_superseded: bool = field(default=False, init=False)"
        in schema_source,
        "GP-014 supersession remains false",
    )


def verify_git_context(
    repository: Path,
    mode: str,
    payload_paths: tuple[str, ...],
    ledger: VerificationLedger,
) -> None:
    if mode == "source":
        return

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
    if mode == "applied":
        ledger.check(head.stdout.strip() == EXPECTED_HEAD, "applied base HEAD")
        ledger.check(tree.stdout.strip() == EXPECTED_TREE, "applied base tree")
        ledger.check(subject.stdout.strip() == EXPECTED_SUBJECT, "applied base subject")
        ledger.check(not staged.stdout.strip(), "applied staged paths zero")
        ledger.check(not tracked.stdout.strip(), "applied tracked modifications zero")
        ledger.check(
            tuple(sorted(untracked.stdout.splitlines())) == payload_paths,
            "applied exact untracked paths",
        )
        return

    parent = git(repository, "rev-parse", "HEAD^")
    committed_paths = git(
        repository,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "HEAD",
    )
    status = git(repository, "status", "--porcelain")
    ledger.check(parent.stdout.strip() == EXPECTED_HEAD, "committed exact parent")
    ledger.check(
        subject.stdout.strip() == EXPECTED_COMMITTED_SUBJECT,
        "committed exact subject",
    )
    ledger.check(
        tuple(sorted(committed_paths.stdout.splitlines())) == payload_paths,
        "committed exact payload paths",
    )
    ledger.check(not status.stdout.strip(), "committed repository clean")
    ledger.check(tree.stdout.strip() != EXPECTED_TREE, "committed tree advances")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument(
        "--mode",
        choices=("source", "applied", "committed"),
        default="source",
    )
    arguments = parser.parse_args()
    repository = Path(arguments.repository).resolve()
    ledger = VerificationLedger()

    exact_paths_file = (
        repository / "scripts/AIWEB_SLICE42A_EXACT_PAYLOAD_PATHS.txt"
    )
    protected_file = (
        repository
        / "scripts/AIWEB_SLICE42A_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    )
    try:
        payload_paths = tuple(
            sorted(
                line
                for line in exact_paths_file.read_text(
                    encoding="utf-8"
                ).splitlines()
                if line
            )
        )
        protected = parse_hash_manifest(protected_file)
    except Exception as error:
        print("manifest_error=" + str(error))
        return 1

    ledger.check(
        len(protected) == EXPECTED_PROTECTED_COUNT,
        "protected predecessor count",
    )
    protected_names = {name for _, name in protected}
    ledger.check(
        protected_names.isdisjoint(payload_paths),
        "protected and payload paths disjoint",
    )
    for expected_hash, relative in protected:
        path = repository / relative
        ledger.check(
            path.is_file() and not path.is_symlink(),
            "protected predecessor exists " + relative,
        )
        ledger.check(
            path.is_file() and sha256_file(path) == expected_hash,
            "protected predecessor hash " + relative,
        )

    ledger.check(
        len(payload_paths) == EXPECTED_PAYLOAD_COUNT,
        "exact payload path count",
    )
    ledger.check(
        tuple(sorted(payload_paths)) == payload_paths,
        "exact payload paths sorted",
    )
    ledger.check(
        len(payload_paths) == len(set(payload_paths)),
        "exact payload paths unique",
    )
    for relative in payload_paths:
        path = repository / relative
        expected_mode = (
            0o755
            if relative.startswith("scripts/test_")
            or relative.startswith("scripts/aiweb_")
            else 0o644
        )
        ledger.check(
            path.is_file() and not path.is_symlink(),
            "payload exists " + relative,
        )
        ledger.check(
            path.is_file()
            and stat.S_IMODE(path.stat().st_mode) == expected_mode,
            "payload mode " + relative,
        )

    verify_source_contract(repository, ledger)
    verify_git_context(repository, arguments.mode, payload_paths, ledger)

    python_executable = select_python(repository)
    with tempfile.TemporaryDirectory(prefix="aiweb_slice42a_pycache_") as cache:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPYCACHEPREFIX"] = cache

        print("\n=== VISIBLE CURRENT TEST 1 OF 1 ===")
        current_rc, current_output = run_visible(
            [
                python_executable,
                "-B",
                str(repository / CURRENT_TEST),
                str(repository),
            ],
            repository,
            env,
        )
        print("current_test_return_code=" + str(current_rc))
        ledger.check(current_rc == 0, "current behavior test return code")
        ledger.check(
            "AI.WEB SLICE 42A BEHAVIOR TEST: PASS" in current_output,
            "current behavior test PASS marker",
        )
        ledger.check(
            "failure_count=0" in current_output,
            "current behavior test zero failures",
        )

        print("\n=== INHERITED VISIBLE VERIFIER: SLICE 41F / 58 TESTS ===")
        inherited_rc, inherited_output = run_inherited_slice41f_verifier(
            repository,
            env,
        )
        print("inherited_verifier_return_code=" + str(inherited_rc))
        ledger.check(inherited_rc == 0, "inherited verifier return code")
        ledger.check(
            "RESULT=PASS" in inherited_output,
            "inherited verifier PASS marker",
        )
        ledger.check(
            "visible_total_tests=58" in inherited_output,
            "58 inherited visible tests",
        )
        ledger.check(
            "failure_count=0" in inherited_output,
            "inherited verifier zero failures",
        )
        ledger.check(
            "hidden_test_workers=0" in inherited_output,
            "inherited hidden workers zero",
        )
        ledger.check(
            "test_output_suppression=0" in inherited_output,
            "inherited output suppression zero",
        )

    print("\n=== SLICE 42A VERIFIER SUMMARY ===")
    print(f"pass_count={ledger.pass_count}")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    print(f"protected_predecessor_files={len(protected)}")
    print(f"slice42a_files={len(payload_paths)}")
    print(f"inherited_visible_tests={EXPECTED_INHERITED_VISIBLE_TESTS}")
    print(f"visible_total_tests={EXPECTED_INHERITED_VISIBLE_TESTS + 1}")
    print("outward_expression_runtime_core_schema=1")
    print("exact_slice41_selected_meaning_custody_required=1")
    print("selected_meaning_outward_meaning_plan_realization_separated=1")
    print("scope_certainty_evidence_caveat_refusal_unresolved_custody=1")
    print("memory_resource_delivery_authority_custody=1")
    print("schema_only=1")
    print("expression_authority_admitted=0")
    print("expression_eligibility_evaluated=0")
    print("preservation_obligations_projected=0")
    print("governed_outward_meaning_created=0")
    print("expression_plan_created=0")
    print("human_readable_text_produced=0")
    print("msm_v1_modified_or_integrated=0")
    print("echo_validation_performed=0")
    print("delivery_truth_evidence_permission_execution_authority=0")
    print("route_api_network_filesystem_memory_tool_action=0")
    print("language_model_embedding_vector_rag_similarity_neural_classifier=0")
    print("gp014_superseded=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    if ledger.failures:
        print("RESULT=FAIL")
        return 1
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
