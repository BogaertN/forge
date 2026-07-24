#!/usr/bin/env python3
"""Independent verifier for Slice 48 and accepted Slice 47 inheritance."""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

EXPECTED_PARENT_HEAD = "1f9070065aad5df11627cbb16732430ca47ded11"
EXPECTED_PARENT_TREE = "2d18842fb938c99ce5616fc713577b7e9f2ea1ae"
EXPECTED_PARENT_SUBJECT = "Slice 47 GP-014 status decision and Phase D closeout"
EXPECTED_COMMIT_SUBJECT = "Slice 48 local runtime service boundary"
EXPECTED_PAYLOAD_COUNT = 19
EXPECTED_PREDECESSOR_COUNT = 60
PACKAGE_RELATIVE = Path("aiweb_language_core_bootstrap/local_runtime_service")
EXACT_PACKAGE_FILES = (
    "__init__.py",
    "authority.py",
    "canonical.py",
    "capabilities.py",
    "control.py",
    "protocol.py",
    "schema.py",
    "service.py",
    "state.py",
    "validation.py",
)
EXACT_PATH_FILE = Path("scripts/AIWEB_SLICE48_EXACT_PAYLOAD_PATHS.txt")
PREDECESSOR_MANIFEST = Path("scripts/AIWEB_SLICE48_PROTECTED_PREDECESSOR_SHA256SUMS.txt")
BEHAVIOR_TEST = Path("scripts/test_aiweb_slice48_local_runtime_service_boundary.py")
SLICE47_VERIFIER = Path("scripts/aiweb_slice47_gp014_status_decision_verify.py")


class Ledger:
    def __init__(self) -> None:
        self.passes = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if condition:
            self.passes += 1
        else:
            self.failures.append(label)
            print("FAIL - " + label)


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=str(cwd), env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=1200)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/usr/bin/git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, relative = line.split("  ", 1)
        pure = PurePosixPath(relative)
        if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
            raise ValueError("unsafe manifest path")
        rows.append((digest, relative))
    return tuple(rows)


def exact_paths(repo: Path) -> tuple[str, ...]:
    return tuple(line for line in (repo / EXACT_PATH_FILE).read_text(encoding="utf-8").splitlines() if line)


def selected_python(repo: Path) -> str:
    candidate = repo / ".venv/bin/python3"
    return str(candidate) if candidate.is_file() else "/usr/bin/python3"


def verify_git_state(repo: Path, mode: str, expected_paths: tuple[str, ...], ledger: Ledger) -> None:
    branch = git(repo, "branch", "--show-current").stdout.strip()
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    subject = git(repo, "show", "-s", "--format=%s", "HEAD").stdout.strip()
    staged = tuple(line for line in git(repo, "diff", "--cached", "--name-only").stdout.splitlines() if line)
    tracked = tuple(line for line in git(repo, "diff", "--name-only").stdout.splitlines() if line)
    untracked = tuple(sorted(line for line in git(repo, "ls-files", "--others", "--exclude-standard").stdout.splitlines() if line))
    ledger.check(branch == "main", "branch main")
    ledger.check(not staged, "no staged paths")
    ledger.check(not tracked, "no tracked changes")
    if mode == "applied":
        ledger.check(head == EXPECTED_PARENT_HEAD, "applied parent head")
        ledger.check(tree == EXPECTED_PARENT_TREE, "applied parent tree")
        ledger.check(subject == EXPECTED_PARENT_SUBJECT, "applied parent subject")
        ledger.check(untracked == tuple(sorted(expected_paths)), "exact applied payload")
    else:
        parent = git(repo, "rev-parse", "HEAD^").stdout.strip()
        changed = tuple(sorted(line for line in git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines() if line))
        ledger.check(subject == EXPECTED_COMMIT_SUBJECT, "committed subject")
        ledger.check(parent == EXPECTED_PARENT_HEAD, "committed parent")
        ledger.check(changed == tuple(sorted(expected_paths)), "exact committed path set")
        ledger.check(not untracked, "no untracked paths after commit")


def run_inherited_slice47(repo: Path, env: dict[str, str]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="aiweb-slice48-inherited-") as temp_name:
        temp = Path(temp_name)
        clone = temp / "forge"
        clone_result = subprocess.run(["/usr/bin/git", "clone", "--quiet", "--no-hardlinks", str(repo), str(clone)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, umask=0o022)
        if clone_result.returncode != 0:
            return clone_result.returncode, clone_result.stdout
        checkout = git(clone, "checkout", "--quiet", "-B", "main", EXPECTED_PARENT_HEAD)
        if checkout.returncode != 0:
            return checkout.returncode, checkout.stderr
        source_venv = repo / ".venv"
        if source_venv.is_dir() and not (clone / ".venv").exists():
            # Slice 47 committed-mode verification requires the disposable
            # repository to expose no untracked paths. The accepted
            # interpreter bridge is excluded only in this disposable clone;
            # no live repository or tracked ignore rule is changed.
            info_exclude = clone / ".git" / "info" / "exclude"
            info_exclude.parent.mkdir(parents=True, exist_ok=True)
            with info_exclude.open("a", encoding="utf-8") as handle:
                handle.write(
                    "\n# Slice 48 disposable accepted interpreter bridge\n"
                    ".venv\n"
                )
            (clone / ".venv").symlink_to(
                source_venv,
                target_is_directory=True,
            )
        inherited_env = env.copy()
        inherited_env["PYTHONPATH"] = str(clone)
        inherited_env["PYTHONPYCACHEPREFIX"] = str(temp / "python-cache")
        py = selected_python(clone)
        result = run([py, "-u", "-B", str(clone / SLICE47_VERIFIER), str(clone), "--mode", "committed"], clone, inherited_env)
        return result.returncode, result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--mode", choices=("applied", "committed"), default="applied")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    ledger = Ledger()

    expected = exact_paths(repo)
    ledger.check(len(expected) == EXPECTED_PAYLOAD_COUNT, "payload count")
    ledger.check(len(set(expected)) == EXPECTED_PAYLOAD_COUNT, "payload paths unique")
    verify_git_state(repo, args.mode, expected, ledger)

    predecessor = parse_manifest(repo / PREDECESSOR_MANIFEST)
    ledger.check(len(predecessor) == EXPECTED_PREDECESSOR_COUNT, "predecessor count")
    ledger.check(len({relative for _, relative in predecessor}) == EXPECTED_PREDECESSOR_COUNT, "predecessor paths unique")
    for digest, relative in predecessor:
        target = repo / relative
        ledger.check(target.is_file(), "predecessor exists " + relative)
        if target.is_file():
            ledger.check(sha256_file(target) == digest, "predecessor hash " + relative)

    package = repo / PACKAGE_RELATIVE
    ledger.check(package.is_dir(), "local service package exists")
    ledger.check(tuple(sorted(path.name for path in package.glob("*.py"))) == EXACT_PACKAGE_FILES, "exact package files")
    source_parts = []
    for name in EXACT_PACKAGE_FILES:
        path = package / name
        try:
            text = path.read_text(encoding="utf-8")
            ast.parse(text)
        except (OSError, SyntaxError):
            ledger.check(False, "syntax " + name)
        else:
            ledger.check(True, "syntax " + name)
            source_parts.append(text)
    source = "\n".join(source_parts)
    ledger.check("socket.AF_INET" not in source and "socket.AF_INET6" not in source, "no Internet socket family")
    ledger.check("TCPServer" not in source and "HTTPServer" not in source, "no TCP or HTTP server")
    ledger.check("main.py" not in source, "no main.py launch")
    ledger.check("aiweb_os_appctl" not in source, "no legacy appctl launch")
    ledger.check("FastAPI" not in source and "Flask" not in source and "uvicorn" not in source, "no web framework")
    ledger.check("SIGKILL" not in source, "no SIGKILL")
    ledger.check("shell=True" not in source, "no shell execution")
    ledger.check("AF_UNIX" in source, "AF_UNIX explicitly used")
    ledger.check("language.inspection_api" in source and '"DEFERRED"' in source, "Slice 49 API deferred")
    ledger.check("gp014.bounded_lane" in source and '"PRESERVED"' in source, "GP-014 preserved")

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = str(repo)
    env["PYTHONPYCACHEPREFIX"] = tempfile.mkdtemp(prefix="slice48-cache-")
    py = selected_python(repo)

    print("=== CURRENT SLICE 48 BEHAVIOR ===")
    behavior = run([py, "-u", "-B", str(repo / BEHAVIOR_TEST), str(repo)], repo, env)
    print(behavior.stdout, end="" if behavior.stdout.endswith("\n") or not behavior.stdout else "\n")
    ledger.check(behavior.returncode == 0, "current Slice 48 behavior return code")
    ledger.check("AI.WEB SLICE 48 BEHAVIOR TEST: PASS" in behavior.stdout, "current Slice 48 behavior marker")

    print("=== ACCEPTED SLICE 47 VERIFIER ===")
    inherited_rc, inherited_output = run_inherited_slice47(repo, env)
    print(inherited_output, end="" if inherited_output.endswith("\n") or not inherited_output else "\n")
    ledger.check(inherited_rc == 0, "inherited Slice 47 verifier return code")
    ledger.check("AI.WEB SLICE 47 VERIFIER: PASS" in inherited_output, "inherited Slice 47 verifier marker")

    print("=== SLICE 48 VERIFIER SUMMARY ===")
    print("checks=" + str(ledger.passes + len(ledger.failures)))
    print("passes=" + str(ledger.passes))
    print("failures=" + str(len(ledger.failures)))
    print("protected_predecessor_files=" + str(len(predecessor)))
    print("slice48_files=" + str(len(expected)))
    print("local_runtime_service_boundary=1")
    print("transport_unix_domain_socket=1")
    print("tcp_udp_http_listener=0")
    print("legacy_main_appctl_activation=0")
    print("language_inspection_api=0")
    print("memory_resource_tool_action_delivery_authority=0")
    print("gp014_superseded=0")
    print("next_lawful_slice=49")
    print("AI.WEB SLICE 48 VERIFIER: " + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
