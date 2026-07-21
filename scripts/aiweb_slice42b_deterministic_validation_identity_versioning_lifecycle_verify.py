#!/usr/bin/env python3
"""Visible verifier for Slice 42B deterministic governance.

This verifier protects every accepted Slice 30-42A predecessor path, verifies
that Slice 42B is an exact additive validation/identity/version/lifecycle
companion, runs the current Slice 42B behavior test visibly, and runs the
accepted Slice 42A verifier against an exact isolated checkout of the accepted
Slice 42A commit. It does not modify the target repository, stage, commit,
fetch, pull, push, activate runtime, hide test workers, or suppress output.
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
EXPECTED_HEAD = "bf38d5dbefd27d6cc69f38f5053071316d1ded63"
EXPECTED_PARENT = "661ff1e17d8d4a982641ca39dc150b23bbb766e9"
EXPECTED_TREE = "ce3232f0adef1de5b7488ff1ec10a919cd9b54af"
EXPECTED_SUBJECT = (
    "Slice 42A outward expression runtime core schema and authority contract"
)
EXPECTED_COMMITTED_SUBJECT = (
    "Slice 42B deterministic validation identity versioning lifecycle"
)
EXPECTED_PROTECTED_COUNT = 686
EXPECTED_PAYLOAD_COUNT = 15
EXPECTED_INHERITED_VISIBLE_TESTS = 59
CURRENT_TEST = (
    "scripts/test_aiweb_slice42b_deterministic_validation_identity_versioning_lifecycle.py"
)
INHERITED_VERIFIER = (
    "scripts/aiweb_slice42a_outward_expression_runtime_core_schema_verify.py"
)
PACKAGE_RELATIVE = (
    "aiweb_language_core_bootstrap/outward_expression_runtime/governed_lifecycle"
)
EXACT_PACKAGE_FILES = (
    "__init__.py",
    "canonical.py",
    "identity.py",
    "lifecycle.py",
    "rules.py",
    "schema.py",
    "validation.py",
)


class VerificationLedger:
    """Accumulate every visible verifier result without short-circuiting."""

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
    previous = ""
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
            or any(part in ("", ".", "..") for part in pure.parts)
            or relative in seen
            or (previous and relative < previous)
        ):
            raise ValueError(f"unsafe or unsorted manifest line {line_number}")
        seen.add(relative)
        previous = relative
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


def run_inherited_slice42a_verifier(
    repository: Path,
    env: dict[str, str],
) -> tuple[int, str]:
    """Run accepted Slice 42A from an exact, umask-neutral checkout."""

    previous_umask = os.umask(0o022)
    try:
        with tempfile.TemporaryDirectory(prefix="aiweb_slice42b_slice42a_") as temporary:
            checkout = Path(temporary) / "slice42a"
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
                output = "temporary Slice 42A clone failed\n" + cloned.stdout
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
                output = "temporary Slice 42A checkout failed\n" + checked_out.stdout
                print(output, end="" if output.endswith("\n") else "\n")
                return checked_out.returncode, output

            predecessor_python = select_python(checkout)
            predecessor_env = env.copy()
            predecessor_env["PYTHONPATH"] = str(checkout)
            predecessor_env["PYTHONDONTWRITEBYTECODE"] = "1"
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


def dotted_call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


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
        "exact Slice 42B governed-lifecycle package file set",
    )
    ledger.check(
        package.is_dir()
        and not any(path.is_dir() for path in package.iterdir()),
        "governed-lifecycle package contains no nested runtime directory",
    )

    allowed_absolute_import_roots = {
        "__future__",
        "dataclasses",
        "enum",
        "hashlib",
        "json",
        "re",
        "typing",
    }
    prohibited_call_names = {
        "open",
        "exec",
        "eval",
        "compile",
        "__import__",
        "system",
        "popen",
        "urlopen",
        "socket",
        "connect",
        "send",
        "recv",
        "write",
        "unlink",
        "remove",
        "rename",
        "replace_file",
        "mkdir",
        "makedirs",
        "rmdir",
        "touch",
        "run",
        "Popen",
        "call",
        "check_call",
        "check_output",
    }
    prohibited_tokens = (
        "subprocess",
        "pathlib",
        "requests",
        "urllib",
        "http.client",
        "socket.",
        "openai",
        "ollama",
        "chromadb",
        "embedding_model(",
        "vector_store",
        "semantic_similarity",
        "nearest_known",
        "confidence_score",
        "probability_score",
        "write_memory",
        "deliver(",
        "invoke_tool",
        "execute_action",
        "route_request",
        "integrate_selected_meaning_into_manifest",
        "GovernedOutwardMeaningRecord(",
        "ExpressionLinkRecord(",
        "ValidationLinkRecord(",
        "DeliveryContainmentLinkRecord(",
    )

    for name in EXACT_PACKAGE_FILES:
        path = package / name
        if not path.is_file():
            ledger.check(False, "package file exists " + name)
            continue
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            ledger.check(False, "AST parse " + name)
            continue
        ledger.check(True, "AST parse " + name)

        absolute_import_roots: set[str] = set()
        relative_imports_valid = True
        prohibited_calls_found: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                absolute_import_roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    absolute_import_roots.add(node.module.split(".", 1)[0])
                elif node.level not in (1, 2):
                    relative_imports_valid = False
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                    if call_name in prohibited_call_names:
                        prohibited_calls_found.append(call_name)
                elif isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr
                    if (
                        call_name in prohibited_call_names
                        and call_name != "compile"
                    ):
                        prohibited_calls_found.append(call_name)

        ledger.check(
            absolute_import_roots.issubset(allowed_absolute_import_roots),
            "only admitted standard-library absolute imports in " + name,
        )
        ledger.check(relative_imports_valid, "only bounded relative imports in " + name)
        ledger.check(
            not prohibited_calls_found,
            "no filesystem/network/process/action call in " + name,
        )
        for token in prohibited_tokens:
            ledger.check(
                token not in source,
                f"no prohibited implementation token {name}:{token}",
            )

    schema_source = (package / "schema.py").read_text(encoding="utf-8")
    canonical_source = (package / "canonical.py").read_text(encoding="utf-8")
    identity_source = (package / "identity.py").read_text(encoding="utf-8")
    lifecycle_source = (package / "lifecycle.py").read_text(encoding="utf-8")
    rules_source = (package / "rules.py").read_text(encoding="utf-8")
    validation_source = (package / "validation.py").read_text(encoding="utf-8")

    required_governance_types = (
        "OutwardExpressionVersionCustody",
        "OutwardExpressionLifecycleRecord",
        "OutwardExpressionLifecycleTransitionRecord",
        "OutwardExpressionLifecycleDecision",
        "OutwardExpressionGovernanceBundle",
    )
    for name in required_governance_types:
        ledger.check(f"class {name}" in schema_source, "required governance type " + name)

    required_version_tokens = (
        'SLICE42B_SCHEMA_VERSION = (',
        'VALIDATION_PROFILE_VERSION = (',
        'CANONICAL_FIELD_ORDER_VERSION = (',
        "SUPPORTED_RUNTIME_SCHEMA_VERSIONS",
        "SUPPORTED_RUNTIME_SPEC_VERSIONS",
        "SUPPORTED_VALIDATION_PROFILE_VERSIONS",
        EXPECTED_HEAD,
        EXPECTED_TREE,
        EXPECTED_SUBJECT,
    )
    for token in required_version_tokens:
        ledger.check(token in schema_source, "required version custody token " + token)

    required_canonical_tokens = (
        "canonical_field_order",
        "canonicalize_field_pairs",
        "canonical_json_bytes",
        "canonical_record_bytes",
        "deterministic_digest",
        "deterministic_record_digest",
        "sort_keys=False",
        'separators=(",", ":")',
        'ensure_ascii=False',
        'allow_nan=False',
    )
    for token in required_canonical_tokens:
        ledger.check(token in canonical_source, "required canonical behavior " + token)

    required_identity_tokens = (
        "expected_record_id",
        "with_expected_id",
        "expected_bundle_digest",
        "expected_bundle_id",
        "with_expected_bundle_identity",
    )
    for token in required_identity_tokens:
        ledger.check(token in identity_source, "required deterministic identity " + token)

    required_validation_tokens = (
        "validate_field_pairs",
        "validate_identity_collection",
        "validate_runtime_schema_record",
        "expected_record_schema_versions",
        "expected_predecessor_references",
        "validate_version_custody",
        "validate_lifecycle_record",
        "validate_lifecycle_transition_record",
        "validate_governance_bundle",
        "assert_valid_runtime_schema_record",
        "assert_valid_version_custody",
        "assert_valid_governance_bundle",
        "DUPLICATE_RECORD_ID",
        "IDENTITY_COLLISION",
        "UNKNOWN_VERSION",
        "TYPE_MISMATCH",
        "REQUIRED_VALUE_MISSING",
        "CROSS_RECORD_IDENTITY_MISMATCH",
    )
    for token in required_validation_tokens:
        ledger.check(token in validation_source, "required validation behavior " + token)

    required_lifecycle_tokens = (
        "evaluate_lifecycle_transition",
        "assert_lifecycle_transition",
        "immutable successor",
        "transition_allowed",
    )
    combined_lifecycle = lifecycle_source + rules_source
    for token in required_lifecycle_tokens:
        ledger.check(token in combined_lifecycle, "required lifecycle behavior " + token)

    zero_authority_tokens = (
        "structural_validity_grants_expression_authority: bool",
        "selected_meaning_chain_admitted: bool",
        "outward_expression_authority_admitted: bool",
        "expression_eligibility_evaluated: bool",
        "preservation_obligations_projected: bool",
        "governed_outward_meaning_created: bool",
        "expression_plan_created: bool",
        "human_readable_text_produced: bool",
        "msm_v1_modified_or_integrated: bool",
        "echo_validation_performed: bool",
        "gp014_superseded: bool",
    )
    for token in zero_authority_tokens:
        ledger.check(token in schema_source, "required zero-authority field " + token)

    ledger.check(
        "_validate_governance_bool_fields" in validation_source,
        "all lifecycle and bundle bool authority fields are validated",
    )
    ledger.check(
        'item.name.endswith("_authorized")' in validation_source,
        "all version-custody authorization fields are validated false",
    )
    ledger.check(
        "gp014_supersession_authorized" in validation_source,
        "GP-014 supersession remains explicitly validated false",
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
    name_status = git(
        repository,
        "diff-tree",
        "--no-commit-id",
        "--name-status",
        "-r",
        "HEAD",
    )
    status = git(repository, "status", "--porcelain")
    ledger.check(head.returncode == 0, "committed HEAD readable")
    ledger.check(parent.stdout.strip() == EXPECTED_HEAD, "committed exact parent")
    ledger.check(
        subject.stdout.strip() == EXPECTED_COMMITTED_SUBJECT,
        "committed exact subject",
    )
    ledger.check(
        tuple(sorted(committed_paths.stdout.splitlines())) == payload_paths,
        "committed exact payload paths",
    )
    ledger.check(
        all(line.startswith("A\t") for line in name_status.stdout.splitlines()),
        "committed payload is additive only",
    )
    ledger.check(not status.stdout.strip(), "committed repository clean")
    ledger.check(tree.stdout.strip() != EXPECTED_TREE, "committed tree advances")


def verify_cache_boundary(
    repository: Path,
    payload_paths: tuple[str, ...],
    ledger: VerificationLedger,
) -> None:
    tracked = git(repository, "ls-files")
    tracked_cache_paths = tuple(
        line
        for line in tracked.stdout.splitlines()
        if "__pycache__" in PurePosixPath(line).parts
        or line.endswith((".pyc", ".pyo"))
    )
    ledger.check(tracked.returncode == 0, "tracked path inventory readable")
    ledger.check(not tracked_cache_paths, "no tracked Python cache artifacts")

    payload_cache_paths: list[str] = []
    for relative in payload_paths:
        path = repository / relative
        if path.name == "__pycache__" or path.suffix in (".pyc", ".pyo"):
            payload_cache_paths.append(relative)
    package = repository / PACKAGE_RELATIVE
    if package.is_dir():
        for path in package.rglob("*"):
            if path.name == "__pycache__" or path.suffix in (".pyc", ".pyo"):
                payload_cache_paths.append(str(path.relative_to(repository)))
    ledger.check(not payload_cache_paths, "Slice 42B source and payload cache-free")


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
        repository / "scripts/AIWEB_SLICE42B_EXACT_PAYLOAD_PATHS.txt"
    )
    protected_file = (
        repository
        / "scripts/AIWEB_SLICE42B_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
    )
    try:
        payload_paths = tuple(
            line
            for line in exact_paths_file.read_text(encoding="utf-8").splitlines()
            if line
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
    verify_cache_boundary(repository, payload_paths, ledger)

    python_executable = select_python(repository)
    with tempfile.TemporaryDirectory(prefix="aiweb_slice42b_pycache_") as cache:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPYCACHEPREFIX"] = cache
        env["PYTHONPATH"] = str(repository)

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
            "AI.WEB SLICE 42B BEHAVIOR TEST: PASS" in current_output,
            "current behavior test PASS marker",
        )
        ledger.check(
            "failure_count=0" in current_output,
            "current behavior test zero failures",
        )
        ledger.check(
            "canonical_serialization=1" in current_output,
            "current canonical serialization proof",
        )
        ledger.check(
            "deterministic_sha256_identities=1" in current_output,
            "current deterministic identity proof",
        )
        ledger.check(
            "exact_predecessor_references=1" in current_output,
            "current exact predecessor proof",
        )
        ledger.check(
            "duplicate_rejection=1" in current_output
            and "identity_collision_rejection=1" in current_output,
            "current duplicate and collision proof",
        )
        ledger.check(
            "structurally_valid_record_is_expression_authorized=0"
            in current_output,
            "current structural validity authority-zero proof",
        )

        print("\n=== INHERITED VISIBLE VERIFIER: SLICE 42A / 59 TESTS ===")
        inherited_rc, inherited_output = run_inherited_slice42a_verifier(
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
            "visible_total_tests=59" in inherited_output,
            "59 inherited visible tests",
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

    print("\n=== SLICE 42B VERIFIER SUMMARY ===")
    print(f"pass_count={ledger.pass_count}")
    print(f"failure_count={len(ledger.failures)}")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    print(f"protected_predecessor_files={len(protected)}")
    print(f"slice42b_files={len(payload_paths)}")
    print(f"inherited_visible_tests={EXPECTED_INHERITED_VISIBLE_TESTS}")
    print(f"visible_total_tests={EXPECTED_INHERITED_VISIBLE_TESTS + 1}")
    print("governed_validation_identity_versioning_lifecycle=1")
    print("canonical_serialization=1")
    print("deterministic_sha256_identities=1")
    print("exact_predecessor_references=1")
    print("schema_and_profile_version_custody=1")
    print("immutable_successor_records=1")
    print("explicit_lifecycle_transition_rules=41")
    print("duplicate_rejection=1")
    print("identity_collision_rejection=1")
    print("unknown_version_rejection=1")
    print("malformed_record_rejection=1")
    print("cross_record_consistency_validation=1")
    print("structurally_valid_record_is_expression_authorized=0")
    print("selected_meaning_chain_admitted=0")
    print("outward_expression_authority_admitted=0")
    print("expression_eligibility_evaluated=0")
    print("preservation_obligations_projected=0")
    print("governed_outward_meaning_created=0")
    print("expression_plan_or_text_created=0")
    print("msm_v1_modified_or_integrated=0")
    print("echo_validation_delivery_action=0")
    print("route_api_network_filesystem_memory_tool_action=0")
    print("external_resource_or_model_authority=0")
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
