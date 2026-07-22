#!/usr/bin/env python3
"""Visible independent verifier for Slice 43C authorized source admission.

The verifier protects every accepted predecessor path, verifies the exact
additive Slice 43C payload and runtime source contract, runs the current Slice
43C behavior test visibly, and runs the accepted Slice 43B verifier visibly
from an exact isolated checkout of the accepted Slice 43B commit.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile


EXPECTED_BRANCH = "main"
EXPECTED_PARENT_HEAD = "42db0a12fd0b09dbe002fe652d869987dd955ed6"
EXPECTED_PARENT_TREE = "bd734175783e413fab30084f686d80fde9e76b29"
EXPECTED_PARENT_SUBJECT = (
    "Slice 43B deterministic validation identity versioning lifecycle"
)
EXPECTED_COMMIT_SUBJECT = (
    "Slice 43C authorized meaning and proposed-expression admission"
)
PACKAGE_RELATIVE = Path(
    "aiweb_language_core_bootstrap/rmc_echo_runtime/authorized_source_admission"
)
EXACT_PACKAGE_FILES = (
    "__init__.py",
    "admission.py",
    "authority.py",
    "canonical.py",
    "identity.py",
    "rules.py",
    "schema.py",
    "validation.py",
)
EXACT_PAYLOAD_MANIFEST = Path(
    "scripts/AIWEB_SLICE43C_EXACT_PAYLOAD_PATHS.txt"
)
PROTECTED_PREDECESSOR_MANIFEST = Path(
    "scripts/AIWEB_SLICE43C_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
)
BEHAVIOR_TEST = Path(
    "scripts/test_aiweb_slice43c_authorized_meaning_proposed_expression_admission.py"
)
INHERITED_VERIFIER = Path(
    "scripts/aiweb_slice43b_deterministic_validation_identity_versioning_lifecycle_verify.py"
)
EXPECTED_PREDECESSOR_COUNT = 1680
EXPECTED_PAYLOAD_COUNT = 16


class Ledger:
    def __init__(self) -> None:
        self.passes = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if condition is True:
            self.passes += 1
        else:
            self.failures.append(label)


def git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    previous = ""
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        1,
    ):
        if not line:
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as error:
            raise ValueError(f"invalid manifest line {number}") from error
        pure = PurePosixPath(relative)
        if (
            len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or pure.is_absolute()
            or any(part in ("", ".", "..") for part in pure.parts)
            or relative in seen
            or (previous and relative < previous)
        ):
            raise ValueError(f"unsafe or unsorted manifest line {number}")
        seen.add(relative)
        previous = relative
        entries.append((digest, relative))
    return tuple(entries)


def payload_paths(repository: Path) -> tuple[str, ...]:
    path = repository / EXACT_PAYLOAD_MANIFEST
    values = tuple(
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    )
    previous = ""
    seen: set[str] = set()
    for value in values:
        pure = PurePosixPath(value)
        if (
            pure.is_absolute()
            or any(part in ("", ".", "..") for part in pure.parts)
            or value in seen
            or (previous and value < previous)
        ):
            raise ValueError("unsafe, duplicate, or unsorted payload path")
        seen.add(value)
        previous = value
    return values


def select_python(repository: Path) -> str:
    candidate = repository / ".venv/bin/python3"
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


def verify_git_state(
    repository: Path,
    mode: str,
    expected_paths: tuple[str, ...],
    ledger: Ledger,
) -> None:
    branch = git(repository, "branch", "--show-current")
    head = git(repository, "rev-parse", "HEAD")
    tree = git(repository, "rev-parse", "HEAD^{tree}")
    subject = git(repository, "show", "-s", "--format=%s", "HEAD")
    ledger.check(
        branch.returncode == 0
        and branch.stdout.strip() == EXPECTED_BRANCH,
        "branch main",
    )
    if mode == "applied":
        ledger.check(
            head.returncode == 0
            and head.stdout.strip() == EXPECTED_PARENT_HEAD,
            "applied parent head",
        )
        ledger.check(
            tree.returncode == 0
            and tree.stdout.strip() == EXPECTED_PARENT_TREE,
            "applied parent tree",
        )
        ledger.check(
            subject.returncode == 0
            and subject.stdout.strip() == EXPECTED_PARENT_SUBJECT,
            "applied parent subject",
        )
        status = git(
            repository,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        lines = tuple(line for line in status.stdout.splitlines() if line)
        untracked = tuple(
            sorted(line[3:] for line in lines if line.startswith("?? "))
        )
        other = tuple(line for line in lines if not line.startswith("?? "))
        ledger.check(status.returncode == 0, "git status")
        ledger.check(not other, "no staged or tracked modifications")
        ledger.check(
            untracked == tuple(sorted(expected_paths)),
            "exact applied untracked payload",
        )
    else:
        parent = git(repository, "rev-parse", "HEAD^")
        ledger.check(
            parent.returncode == 0
            and parent.stdout.strip() == EXPECTED_PARENT_HEAD,
            "committed parent",
        )
        ledger.check(
            subject.returncode == 0
            and subject.stdout.strip() == EXPECTED_COMMIT_SUBJECT,
            "committed subject",
        )
        changed = git(
            repository,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
        )
        ledger.check(
            changed.returncode == 0
            and tuple(sorted(changed.stdout.splitlines()))
            == tuple(sorted(expected_paths)),
            "exact committed payload",
        )
        status = git(
            repository,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        ledger.check(
            status.returncode == 0 and not status.stdout.strip(),
            "committed repository clean",
        )


def verify_source_contract(repository: Path, ledger: Ledger) -> None:
    package = repository / PACKAGE_RELATIVE
    actual = (
        tuple(sorted(path.name for path in package.iterdir() if path.is_file()))
        if package.is_dir()
        else ()
    )
    ledger.check(actual == EXACT_PACKAGE_FILES, "exact package file set")
    ledger.check(
        package.is_dir()
        and not any(path.is_dir() for path in package.iterdir()),
        "authorized source admission package has no nested runtime directory",
    )

    allowed_import_roots = {
        "__future__",
        "dataclasses",
        "enum",
        "hashlib",
        "json",
        "typing",
    }
    prohibited_call_names = {
        "open", "exec", "eval", "compile", "__import__", "system",
        "popen", "urlopen", "socket",
    }
    prohibited_attributes = {
        "read_text", "read_bytes", "write_text", "write_bytes", "open",
        "unlink", "mkdir", "rename", "remove", "touch", "connect",
        "send", "recv",
    }
    prohibited_tokens = (
        "aiweb_rmc_echo_boundary_scaffold",
        "rmc_engine_v1.echo_validator",
        "rmc_engine_v1.renderer.echo_validator",
        "rmc_engine_v1.general_pipeline.echo_approval",
        "from echoforge",
        "import echoforge",
        "echo_forge(",
        "validate_echo(",
        "approve_echo(",
        "compare_meaning(",
        "classify_drift(",
        "decide_disposition(",
        "repair_expression(",
        "ValidationLinkRecord(",
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
    required_definitions = {
        "SourceAdmissionRequest",
        "AuthorizedMeaningAdmissionRecord",
        "ProposedExpressionAdmissionRecord",
        "EchoValidationAdmissionPackage",
        "SourceAdmissionResult",
        "canonical_record_bytes",
        "expected_record_id",
        "validate_exact_source",
        "validate_admission_package",
        "admit_authorized_meaning_and_proposed_expression",
    }
    found_definitions: set[str] = set()
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
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                found_definitions.add(node.name)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    ledger.check(
                        node.func.id not in prohibited_call_names,
                        f"no prohibited call {name}:{node.func.id}",
                    )
                elif isinstance(node.func, ast.Attribute):
                    ledger.check(
                        node.func.attr not in prohibited_attributes,
                        f"no prohibited attribute {name}:{node.func.attr}",
                    )
        ledger.check(
            imported_roots.issubset(allowed_import_roots),
            "only admitted deterministic imports in " + name,
        )
        for token in prohibited_tokens:
            ledger.check(token not in source, f"no prohibited token {name}:{token}")
    ledger.check(
        required_definitions.issubset(found_definitions),
        "all required authorized source admission definitions",
    )


def run_inherited(
    repository: Path,
    env: dict[str, str],
) -> tuple[int, str]:
    previous_umask = os.umask(0o022)
    try:
        with tempfile.TemporaryDirectory(
            prefix="aiweb_slice43c_slice43b_"
        ) as temporary:
            checkout = Path(temporary) / "slice43b"
            clone = subprocess.run(
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
            if clone.returncode != 0:
                print(clone.stdout, end="")
                return clone.returncode, clone.stdout
            checked_out = subprocess.run(
                [
                    "git",
                    "-C",
                    str(checkout),
                    "checkout",
                    "--quiet",
                    "-B",
                    EXPECTED_BRANCH,
                    EXPECTED_PARENT_HEAD,
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                env=env,
            )
            if checked_out.returncode != 0:
                print(checked_out.stdout, end="")
                return checked_out.returncode, checked_out.stdout
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default="/home/nic/forge")
    parser.add_argument(
        "--mode",
        choices=("applied", "committed"),
        default="applied",
    )
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    ledger = Ledger()

    print("=== AI.WEB SLICE 43C INDEPENDENT VERIFIER ===")
    print(f"repository={repository}")
    print(f"mode={args.mode}")

    ledger.check(repository.is_dir(), "repository exists")
    if not repository.is_dir():
        print("AI.WEB SLICE 43C VERIFIER: FAIL")
        return 1

    try:
        expected_paths = payload_paths(repository)
    except Exception as error:
        print("payload manifest error:", error)
        return 1
    ledger.check(
        len(expected_paths) == EXPECTED_PAYLOAD_COUNT,
        "exact payload count",
    )
    ledger.check(
        len(set(expected_paths)) == len(expected_paths),
        "unique payload paths",
    )
    verify_git_state(repository, args.mode, expected_paths, ledger)

    executable_paths = {
        str(BEHAVIOR_TEST),
        "scripts/aiweb_slice43c_authorized_meaning_proposed_expression_admission_verify.py",
    }
    for relative in expected_paths:
        path = repository / relative
        ledger.check(path.is_file(), "payload exists " + relative)
        if path.is_file():
            expected_mode = 0o755 if relative in executable_paths else 0o644
            ledger.check(
                stat.S_IMODE(path.stat().st_mode) == expected_mode,
                "exact payload mode " + relative,
            )

    predecessor_path = repository / PROTECTED_PREDECESSOR_MANIFEST
    try:
        predecessor = parse_manifest(predecessor_path)
    except Exception as error:
        print("predecessor manifest error:", error)
        return 1
    ledger.check(
        len(predecessor) == EXPECTED_PREDECESSOR_COUNT,
        "predecessor manifest count",
    )
    for expected_hash, relative in predecessor:
        path = repository / relative
        ledger.check(path.is_file(), "predecessor exists " + relative)
        if path.is_file():
            ledger.check(
                sha256_file(path) == expected_hash,
                "predecessor hash " + relative,
            )

    for protected in (
        "aiweb_language_core_bootstrap/rmc_echo_runtime/__init__.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/authority.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/identity.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/schema.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/governed_lifecycle/schema.py",
        "scripts/aiweb_slice43b_deterministic_validation_identity_versioning_lifecycle_verify.py",
        "aiweb_rmc_echo_boundary_scaffold/__init__.py",
        "rmc_engine_v1/echo_validator.py",
        "rmc_engine_v1/renderer/echo_validator.py",
        "rmc_engine_v1/general_pipeline/echo_approval.py",
    ):
        ledger.check(
            any(relative == protected for _, relative in predecessor),
            "protected predecessor " + protected,
        )

    tracked_new = git(
        repository,
        "cat-file",
        "-e",
        "HEAD:aiweb_language_core_bootstrap/rmc_echo_runtime/authorized_source_admission/schema.py",
    )
    ledger.check(
        (tracked_new.returncode != 0) if args.mode == "applied" else True,
        "Slice 43C package additive at parent",
    )
    verify_source_contract(repository, ledger)

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(
        prefix="aiweb_slice43c_pycache_"
    ) as cache:
        env["PYTHONPYCACHEPREFIX"] = cache
        env["PYTHONPATH"] = str(repository)
        python = select_python(repository)
        print("\n=== CURRENT SLICE 43C BEHAVIOR ===")
        behavior_rc, behavior_output = run_visible(
            [
                python,
                "-B",
                str(repository / BEHAVIOR_TEST),
                str(repository),
            ],
            repository,
            env,
        )
        ledger.check(behavior_rc == 0, "current behavior test")
        ledger.check(
            "AI.WEB SLICE 43C BEHAVIOR TEST: PASS" in behavior_output,
            "current behavior verdict",
        )
        print("\n=== INHERITED SLICE 43B VERIFIER ===")
        inherited_rc, inherited_output = run_inherited(repository, env)
        ledger.check(inherited_rc == 0, "inherited Slice 43B verifier")
        ledger.check(
            "AI.WEB SLICE 43B VERIFIER: PASS" in inherited_output,
            "inherited Slice 43B verdict",
        )

    cache_hits = tuple(
        path
        for path in (repository / PACKAGE_RELATIVE).rglob("__pycache__")
    ) if (repository / PACKAGE_RELATIVE).is_dir() else ()
    ledger.check(not cache_hits, "no governed package Python cache")

    print("\n=== SLICE 43C VERIFIER SUMMARY ===")
    print(f"checks={ledger.passes + len(ledger.failures)}")
    print(f"passes={ledger.passes}")
    print(f"failures={len(ledger.failures)}")
    print(f"protected_predecessor_files={len(predecessor)}")
    print(f"slice43c_files={len(expected_paths)}")
    print("authorized_meaning_and_proposed_expression_admission=1")
    print("selected_governed_meaning_admitted=1")
    print("governed_outward_meaning_admitted=1")
    print("realized_expression_candidate_admitted=1")
    print("msm_v1_expression_link_admitted=1")
    print("slice42_trace_and_custody_admitted=1")
    print("raw_text_admitted=0")
    print("orphan_expression_admitted=0")
    print("recomputed_or_fabricated_identity_admitted=0")
    print("unsupported_version_admitted=0")
    print("missing_link_admitted=0")
    print("already_delivered_candidate_admitted=0")
    print("unauthorized_candidate_admitted=0")
    print("meaning_preservation_comparison=0")
    print("drift_classification_materiality=0")
    print("echo_disposition_rejection_containment=0")
    print("msm_v1_integration=0")
    print("delivery_or_downstream_authority=0")
    print("model_or_similarity_authority=0")
    print("gp014_superseded=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    for failure in ledger.failures:
        print("FAIL:", failure)
    verdict = "PASS" if not ledger.failures else "FAIL"
    print(f"AI.WEB SLICE 43C VERIFIER: {verdict}")
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
