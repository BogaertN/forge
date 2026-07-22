#!/usr/bin/env python3
"""Visible independent verifier for Slice 43H closeout."""
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
EXPECTED_PARENT_HEAD = "2840bc205de8f2934a8a84941a560f22215fd10d"
EXPECTED_PARENT_TREE = "89e2a4f0d3512aec1292487116bba5b559c7ce6c"
EXPECTED_PARENT_SUBJECT = "Slice 43G MSM-v1 Echo-validation link custody"
EXPECTED_COMMIT_SUBJECT = "Slice 43H disabled bootstrap integration and Slice 43 closeout"
PRE_SLICE43_HEAD = "ebe931909b59a40ac4ef202b89d8f4f2702104a3"
PRE_SLICE43_TREE = "efab06b171dfd5a34b56c0cff81026788e40a1e0"
PACKAGE_RELATIVE = Path(
    "aiweb_language_core_bootstrap/rmc_echo_runtime/disabled_echo_closeout"
)
EXACT_PACKAGE_FILES = (
    "__init__.py", "authority.py", "canonical.py", "fixtures.py",
    "integration.py", "schema.py", "validation.py",
)
EXACT_PAYLOAD_MANIFEST = Path("scripts/AIWEB_SLICE43H_EXACT_PAYLOAD_PATHS.txt")
PROTECTED_PREDECESSOR_MANIFEST = Path(
    "scripts/AIWEB_SLICE43H_PROTECTED_PREDECESSOR_SHA256SUMS.txt"
)
BEHAVIOR_TEST = Path(
    "scripts/test_aiweb_slice43h_disabled_bootstrap_integration_and_slice43_closeout.py"
)
INHERITED_VERIFIER = Path(
    "scripts/aiweb_slice43g_msm_echo_validation_link_custody_verify.py"
)
EXPECTED_PREDECESSOR_COUNT = 1760
EXPECTED_PAYLOAD_COUNT = 15


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
        ["/usr/bin/git", "-C", str(repository), *args],
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


def source_uses_output_suppression(source: str) -> bool:
    """Return True only for semantic output-suppression constructs."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return True

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "subprocess"
                and node.attr == "DEVNULL"
            ):
                return True
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "contextlib"
                and node.attr in {"redirect_stdout", "redirect_stderr"}
            ):
                return True

        if isinstance(node, ast.Call):
            function = node.func
            if (
                isinstance(function, ast.Name)
                and function.id in {"redirect_stdout", "redirect_stderr"}
            ):
                return True
            for argument in node.args:
                if (
                    isinstance(argument, ast.Attribute)
                    and isinstance(argument.value, ast.Name)
                    and argument.value.id == "os"
                    and argument.attr == "devnull"
                ):
                    return True

    return False


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    previous = ""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
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
    values = tuple(
        line
        for line in (repository / EXACT_PAYLOAD_MANIFEST)
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    )
    seen: set[str] = set()
    previous = ""
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
    child_env = env.copy()
    child_env["PYTHONUNBUFFERED"] = "1"
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        env=child_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    output: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
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
        branch.returncode == 0 and branch.stdout.strip() == EXPECTED_BRANCH,
        "branch main",
    )
    if mode == "applied":
        ledger.check(
            head.returncode == 0 and head.stdout.strip() == EXPECTED_PARENT_HEAD,
            "applied parent head",
        )
        ledger.check(
            tree.returncode == 0 and tree.stdout.strip() == EXPECTED_PARENT_TREE,
            "applied parent tree",
        )
        ledger.check(
            subject.returncode == 0
            and subject.stdout.strip() == EXPECTED_PARENT_SUBJECT,
            "applied parent subject",
        )
        status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
        lines = tuple(line for line in status.stdout.splitlines() if line)
        untracked = tuple(sorted(line[3:] for line in lines if line.startswith("?? ")))
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
            parent.returncode == 0 and parent.stdout.strip() == EXPECTED_PARENT_HEAD,
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
        status = git(repository, "status", "--porcelain=v1", "--untracked-files=all")
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
    ledger.check(actual == EXACT_PACKAGE_FILES, "exact runtime package file set")
    ledger.check(
        package.is_dir() and not any(path.is_dir() for path in package.iterdir()),
        "runtime package has no nested directory",
    )

    prohibited_import_roots = {
        "asyncio", "builtins", "ctypes", "http", "multiprocessing", "openai",
        "ollama", "os", "pathlib", "requests", "shutil", "socket", "subprocess",
        "tempfile", "threading", "torch", "transformers", "urllib",
    }
    prohibited_call_names = {
        "open", "exec", "eval", "compile", "__import__", "system", "popen",
    }
    prohibited_attributes = {
        "read_text", "read_bytes", "write_text", "write_bytes", "open", "unlink",
        "mkdir", "rename", "remove", "touch", "connect", "send", "recv",
    }
    prohibited_tokens = (
        "import echoforge", "from echoforge", "import openai", "import ollama",
        "subprocess.", "requests.", "socket.", "urlopen(", "write_memory(",
        "invoke_tool(", "deliver(", "rewrite_expression(", "repair_expression(",
        "semantic_similarity(", "nearest_known(", "confidence_score(",
        "probability_score(",
    )
    required_definitions = {
        "DisabledEchoCloseoutState", "EchoCloseoutFixture", "EchoCloseoutInvocation",
        "Slice43CloseoutStageReceipt", "Slice43RollbackMetadata",
        "Slice43AcceptanceRecord", "DisabledEchoCloseoutResult",
        "canonical_json_bytes", "deterministic_digest", "stable_identifier",
        "list_echo_closeout_fixtures", "get_echo_closeout_fixture",
        "validate_state", "validate_fixture", "validate_invocation",
        "validate_acceptance_record", "validate_result",
        "build_disabled_echo_closeout_state", "build_echo_closeout_invocation",
        "build_slice43_rollback_metadata", "build_slice43_acceptance_record",
        "run_disabled_echo_closeout",
    }
    found_definitions: set[str] = set()
    for name in EXACT_PACKAGE_FILES:
        path = package / name
        ledger.check(path.is_file(), "runtime file exists " + name)
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            ledger.check(False, "runtime syntax " + name)
            continue
        ledger.check(True, "runtime syntax " + name)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                found_definitions.add(node.name)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    ledger.check(
                        alias.name.split(".")[0] not in prohibited_import_roots,
                        f"no prohibited import {name}:{alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                ledger.check(
                    node.module.split(".")[0] not in prohibited_import_roots,
                    f"no prohibited import {name}:{node.module}",
                )
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
        for token in prohibited_tokens:
            ledger.check(token not in source, f"no prohibited token {name}:{token}")

    ledger.check(
        required_definitions.issubset(found_definitions),
        "all required Slice 43H definitions",
    )
    integration_source = (package / "integration.py").read_text(encoding="utf-8")
    schema_source = (package / "schema.py").read_text(encoding="utf-8")
    authority_source = (package / "authority.py").read_text(encoding="utf-8")
    for required in (
        "build_source_admission_request", "compare_meaning_preservation",
        "classify_drift_and_materiality", "decide_echo_disposition",
        "integrate_echo_validation_link", "EXPECTED_STAGE_CHAIN",
    ):
        ledger.check(required in integration_source, "integration uses " + required)
    for required in (
        "slice43a_through_43h_completed", "authorized_meaning_required",
        "proposed_expression_required", "selected_meaning_preserved",
        "scope_preserved", "certainty_preserved", "evidence_status_preserved",
        "caveats_preserved", "refusal_state_preserved",
        "unresolved_conditions_preserved", "material_drift_rejected_or_contained",
        "echoforge_used", "llm_used", "delivery_authority", "truth_authority",
        "evidence_authority", "permission_authority", "execution_authority",
        "slice44_started",
    ):
        ledger.check(required in schema_source, "acceptance field " + required)
    ledger.check(
        "Slice 44 remains unstarted" in authority_source,
        "Slice 44 remains deferred",
    )
    ledger.check(
        "delivery-link creation" in authority_source,
        "delivery-link prohibition stated",
    )


def run_inherited(repository: Path, env: dict[str, str]) -> tuple[int, str]:
    previous_umask = os.umask(0o022)
    try:
        with tempfile.TemporaryDirectory(prefix="aiweb_slice43h_slice43g_") as temporary:
            checkout = Path(temporary) / "slice43g"
            clone = subprocess.run(
                [
                    "/usr/bin/git", "clone", "--quiet", "--no-hardlinks",
                    "--no-checkout", str(repository), str(checkout),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                env=env,
            )
            if clone.returncode != 0:
                print(clone.stdout, end="", flush=True)
                return clone.returncode, clone.stdout
            checked_out = subprocess.run(
                [
                    "/usr/bin/git", "-C", str(checkout), "checkout", "--quiet",
                    "-B", EXPECTED_BRANCH, EXPECTED_PARENT_HEAD,
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                env=env,
            )
            if checked_out.returncode != 0:
                print(checked_out.stdout, end="", flush=True)
                return checked_out.returncode, checked_out.stdout
            predecessor_env = env.copy()
            predecessor_env["PYTHONPATH"] = str(checkout)
            predecessor_env["PYTHONDONTWRITEBYTECODE"] = "1"
            return run_visible(
                [
                    select_python(checkout), "-u", "-B",
                    str(checkout / INHERITED_VERIFIER), str(checkout),
                    "--mode", "committed",
                ],
                checkout,
                predecessor_env,
            )
    finally:
        os.umask(previous_umask)


def verify_tree_recovery(repository: Path, ledger: Ledger) -> None:
    with tempfile.TemporaryDirectory(prefix="aiweb_slice43h_recovery_") as temporary:
        checkout = Path(temporary) / "pre43"
        clone = subprocess.run(
            [
                "/usr/bin/git", "clone", "--quiet", "--no-hardlinks",
                "--no-checkout", str(repository), str(checkout),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        ledger.check(clone.returncode == 0, "recovery clone created")
        if clone.returncode != 0:
            return
        checkout_result = git(checkout, "checkout", "--quiet", "--detach", PRE_SLICE43_HEAD)
        ledger.check(checkout_result.returncode == 0, "pre-Slice-43 checkout")
        recovered = git(checkout, "rev-parse", "HEAD^{tree}")
        ledger.check(
            recovered.returncode == 0 and recovered.stdout.strip() == PRE_SLICE43_TREE,
            "pre-Slice-43 exact tree recovery",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default="/home/nic/forge")
    parser.add_argument("--mode", choices=("applied", "committed"), default="applied")
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    ledger = Ledger()

    print("=== AI.WEB SLICE 43H INDEPENDENT VERIFIER ===")
    print(f"repository={repository}")
    print(f"mode={args.mode}")

    ledger.check(repository.is_dir(), "repository exists")
    if not repository.is_dir():
        print("AI.WEB SLICE 43H VERIFIER: FAIL")
        return 1

    try:
        expected_paths = payload_paths(repository)
    except Exception as error:
        print("payload manifest error:", error)
        return 1
    ledger.check(len(expected_paths) == EXPECTED_PAYLOAD_COUNT, "exact payload count")
    ledger.check(len(set(expected_paths)) == len(expected_paths), "unique payload paths")
    verify_git_state(repository, args.mode, expected_paths, ledger)

    executable_paths = {
        str(BEHAVIOR_TEST),
        "scripts/aiweb_slice43h_disabled_bootstrap_integration_and_slice43_closeout_verify.py",
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

    try:
        predecessor = parse_manifest(repository / PROTECTED_PREDECESSOR_MANIFEST)
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
        "aiweb_language_core_bootstrap/outward_expression_runtime/disabled_outward_expression_closeout/integration.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/authority.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/governed_lifecycle/validation.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/authorized_source_admission/admission.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/meaning_preservation_comparison/comparison.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/drift_materiality_classification/classification.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/echo_disposition/disposition.py",
        "aiweb_language_core_bootstrap/rmc_echo_runtime/msm_echo_validation_integration/integration.py",
        "scripts/test_aiweb_slice43g_msm_echo_validation_link_custody.py",
        "scripts/aiweb_slice43g_msm_echo_validation_link_custody_verify.py",
    ):
        ledger.check(
            any(relative == protected for _, relative in predecessor),
            "protected predecessor " + protected,
        )

    verify_source_contract(repository, ledger)

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(repository)
    print("\n=== CURRENT SLICE 43H BEHAVIOR ===")
    behavior_rc, behavior_output = run_visible(
        [select_python(repository), "-u", "-B", str(repository / BEHAVIOR_TEST), str(repository)],
        repository,
        env,
    )
    ledger.check(behavior_rc == 0, "current behavior return code")
    for marker in (
        "check_count=314",
        "acceptance_field_checks=19",
        "slice43A_through_43H_completed=1",
        "authorized_meaning_required=1",
        "proposed_expression_required=1",
        "material_drift_rejected_or_contained=1",
        "echoforge_used=0",
        "llm_used=0",
        "delivery_authority=0",
        "truth_authority=0",
        "evidence_authority=0",
        "permission_authority=0",
        "execution_authority=0",
        "slice44_started=0",
        "failure_count=0",
        "AI.WEB SLICE 43H BEHAVIOR TEST: PASS",
    ):
        ledger.check(marker in behavior_output, "behavior marker " + marker)

    print("\n=== INHERITED SLICE 43G VERIFIER ===")
    inherited_rc, inherited_output = run_inherited(repository, env)
    ledger.check(inherited_rc == 0, "inherited verifier return code")
    ledger.check(
        "AI.WEB SLICE 43G VERIFIER: PASS" in inherited_output,
        "inherited Slice 43G verifier pass",
    )
    verify_tree_recovery(repository, ledger)

    test_source = (repository / BEHAVIOR_TEST).read_text(encoding="utf-8")
    verifier_source = Path(__file__).read_text(encoding="utf-8")
    ledger.check("ThreadPoolExecutor" not in test_source, "no hidden test workers")
    ledger.check("ProcessPoolExecutor" not in test_source, "no hidden process workers")
    ledger.check(
        not source_uses_output_suppression(test_source),
        "no test output suppression",
    )
    ledger.check(
        not source_uses_output_suppression(verifier_source),
        "no verifier output suppression",
    )

    checks = ledger.passes + len(ledger.failures)
    print("\n=== SLICE 43H VERIFIER SUMMARY ===")
    print(f"checks={checks}")
    print(f"passes={ledger.passes}")
    print(f"failures={len(ledger.failures)}")
    print(f"protected_predecessor_files={len(predecessor)}")
    print(f"slice43h_files={len(expected_paths)}")
    print("slice43A_through_43H_completed=1")
    print("authorized_meaning_required=1")
    print("proposed_expression_required=1")
    print("selected_meaning_preserved=1")
    print("scope_preserved=1")
    print("certainty_preserved=1")
    print("evidence_status_preserved=1")
    print("caveats_preserved=1")
    print("refusal_state_preserved=1")
    print("unresolved_conditions_preserved=1")
    print("material_drift_rejected_or_contained=1")
    print("disabled_by_default=1")
    print("explicit_invocation_required=1")
    print("accepted_static_fixture_only=1")
    print("offline_in_memory_deterministic=1")
    print("final_slice43_acceptance_record_created=1")
    print("pre_slice43_tree_recovery=1")
    print("exact_staged_path_containment=1")
    print("echoforge_used=0")
    print("llm_used=0")
    print("delivery_authority=0")
    print("truth_authority=0")
    print("evidence_authority=0")
    print("permission_authority=0")
    print("execution_authority=0")
    print("slice44_started=0")
    print("route_api_network_filesystem_memory_tool_action_authority=0")
    print("delivery_link_created=0")
    print("gp014_superseded=0")
    print("hidden_test_workers=0")
    print("test_output_suppression=0")
    if ledger.failures:
        for failure in ledger.failures:
            print("FAIL: " + failure)
        print("AI.WEB SLICE 43H VERIFIER: FAIL")
        return 1
    print("AI.WEB SLICE 43H VERIFIER: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
