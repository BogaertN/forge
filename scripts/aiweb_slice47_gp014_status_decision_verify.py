#!/usr/bin/env python3
"""Independent verifier for Slice 47 and accepted applied-context Slice 46 inheritance."""
from __future__ import annotations
import argparse
import ast
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import shlex
import subprocess
import sys
import tempfile

EXPECTED_PARENT_HEAD = '0af2e034f061dfdbb86868090a6db2424131b999'
EXPECTED_PARENT_TREE = 'f7dd3b4ec061f28f8076d62b06e49f8cead32938'
EXPECTED_PARENT_SUBJECT = 'Slice 46 GP-014 equivalence and regression proof'
EXPECTED_PARENT_PARENT = '00df51e4b2fe14e437291c5228159820dd1cf139'
EXPECTED_COMMIT_SUBJECT = 'Slice 47 GP-014 status decision and Phase D closeout'
EXPECTED_PAYLOAD_COUNT = 16
EXPECTED_PREDECESSOR_COUNT = 59
PACKAGE_RELATIVE = Path("aiweb_language_core_bootstrap/gp014_status_decision")
EXACT_PACKAGE_FILES = (
    "__init__.py", "authority.py", "canonical.py", "closeout.py",
    "decision.py", "receipt.py", "schema.py", "validation.py",
)
EXACT_PATH_FILE = Path("scripts/AIWEB_SLICE47_EXACT_PAYLOAD_PATHS.txt")
PREDECESSOR_MANIFEST = Path("scripts/AIWEB_SLICE47_PROTECTED_PREDECESSOR_SHA256SUMS.txt")
BEHAVIOR_TEST = Path("scripts/test_aiweb_slice47_gp014_status_decision.py")
SLICE46_PATH_FILE = Path("scripts/AIWEB_SLICE46_EXACT_PAYLOAD_PATHS.txt")
SLICE46_VERIFIER = Path("scripts/aiweb_slice46_gp014_equivalence_regression_proof_verify.py")

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
    return subprocess.run(command, cwd=str(cwd), env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/usr/bin/git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
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


def select_python(repo: Path) -> str:
    candidate = repo / ".venv/bin/python3"
    return str(candidate) if candidate.is_file() else "/usr/bin/python3"


def print_visible(result: subprocess.CompletedProcess[str]) -> None:
    print(result.stdout, end="" if result.stdout.endswith("\n") or not result.stdout else "\n")


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
    ledger.check(not tracked, "no tracked unstaged paths")
    if mode == "applied":
        ledger.check(head == EXPECTED_PARENT_HEAD, "applied parent head")
        ledger.check(tree == EXPECTED_PARENT_TREE, "applied parent tree")
        ledger.check(subject == EXPECTED_PARENT_SUBJECT, "applied parent subject")
        ledger.check(untracked == tuple(sorted(expected_paths)), "exact applied untracked payload")
    else:
        parent = git(repo, "rev-parse", "HEAD^").stdout.strip()
        changed = tuple(sorted(line for line in git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines() if line))
        ledger.check(subject == EXPECTED_COMMIT_SUBJECT, "committed subject")
        ledger.check(parent == EXPECTED_PARENT_HEAD, "committed parent")
        ledger.check(changed == tuple(sorted(expected_paths)), "exact committed path set")
        ledger.check(not untracked, "committed repository has no untracked paths")


def copy_commit_path(source_repo: Path, commit: str, relative: str, destination_repo: Path) -> None:
    blob = subprocess.run(["/usr/bin/git", "-C", str(source_repo), "show", f"{commit}:{relative}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if blob.returncode != 0:
        raise RuntimeError("unable to read committed Slice 46 path: " + relative)
    destination = destination_repo / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(blob.stdout)
    mode = git(source_repo, "ls-tree", commit, "--", relative).stdout.split(None, 1)[0]
    os.chmod(destination, 0o755 if mode == "100755" else 0o644)


def run_inherited_slice46(repo: Path, env: dict[str, str]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="aiweb-slice47-inherited-") as temp_name:
        temp = Path(temp_name)
        clone = temp / "forge"
        clone_result = subprocess.run(["/usr/bin/git", "clone", "--quiet", "--no-hardlinks", str(repo), str(clone)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if clone_result.returncode != 0:
            return clone_result.returncode, clone_result.stdout
        checkout = git(clone, "checkout", "--quiet", "-B", "main", EXPECTED_PARENT_PARENT)
        if checkout.returncode != 0:
            return checkout.returncode, checkout.stderr
        slice46_paths_result = subprocess.run(["/usr/bin/git", "-C", str(repo), "show", f"{EXPECTED_PARENT_HEAD}:{SLICE46_PATH_FILE.as_posix()}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if slice46_paths_result.returncode != 0:
            return slice46_paths_result.returncode, slice46_paths_result.stderr
        slice46_paths = tuple(line for line in slice46_paths_result.stdout.splitlines() if line)
        if len(slice46_paths) != 16:
            return 1, "Slice 46 exact path count mismatch\n"
        try:
            for relative in slice46_paths:
                copy_commit_path(repo, EXPECTED_PARENT_HEAD, relative, clone)
        except Exception as error:
            return 1, f"{type(error).__name__}: {error}\n"
        inherited_env = env.copy()
        inherited_env["PYTHONPATH"] = str(clone)
        inherited_env["PYTHONPYCACHEPREFIX"] = str(temp / "python_cache")

        # The disposable Git clone intentionally has no tracked virtual
        # environment. Build an ignored interpreter bridge that invokes the
        # accepted live Forge virtual environment without resolving its
        # python3 symlink to /usr/bin/python3. Slice 46 then sees a bounded
        # clone-local .venv entry while all dependency imports, including
        # lark, come from the accepted live environment.
        source_python = Path(select_python(repo))
        if not source_python.is_file():
            return 1, f"accepted Python interpreter missing: {source_python}\n"

        bridge_python = clone / ".venv/bin/python3"
        bridge_python.parent.mkdir(parents=True, exist_ok=True)
        if bridge_python.exists() or bridge_python.is_symlink():
            bridge_python.unlink()
        bridge_python.write_text(
            "#!/bin/sh\n" + shlex.quote(str(source_python)) + ' "$@"\n',
            encoding="utf-8",
        )
        bridge_python.chmod(0o755)

        inherited_env["VIRTUAL_ENV"] = str(repo / ".venv")
        inherited_env["PATH"] = (
            str(bridge_python.parent)
            + os.pathsep
            + inherited_env.get("PATH", "")
        )

        result = run(
            [
                str(bridge_python),
                "-u",
                "-B",
                str(clone / SLICE46_VERIFIER),
                str(clone),
                "--mode",
                "applied",
            ],
            clone,
            inherited_env,
        )
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
    ledger.check(package.is_dir(), "status-decision package exists")
    ledger.check(tuple(sorted(path.name for path in package.glob("*.py"))) == EXACT_PACKAGE_FILES, "exact package source files")
    for name in EXACT_PACKAGE_FILES:
        path = package / name
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            ledger.check(False, "syntax " + name)
        else:
            ledger.check(True, "syntax " + name)

    source = "\n".join((package / name).read_text(encoding="utf-8") for name in EXACT_PACKAGE_FILES)
    for prohibited in (
        "import rmc_engine_v1", "from rmc_engine_v1", "importlib", "subprocess",
        "socket", "requests", "urllib", "open(", "write_text(", "write_bytes(",
        "@app.route", "@app.post", "FastAPI(", "Flask(",
    ):
        ledger.check(prohibited not in source, "package source prohibits " + prohibited)
    ledger.check("preserved_as_unchanged_bounded_lane" in source, "selected status present")
    ledger.check("wrapped_behind_general_interface" in source, "lawful wrapped alternative recorded")
    ledger.check("adapter_is_general_interface=False" in source, "adapter not promoted to general interface")
    ledger.check("gp014_superseded=False" in source, "supersession false")

    source_caches = []
    for cache in repo.rglob("__pycache__"):
        try:
            relative = cache.relative_to(repo)
        except ValueError:
            continue
        if relative.parts and relative.parts[0] in {".git", ".venv"}:
            continue
        if cache.is_dir():
            source_caches.append(relative.as_posix())
    ledger.check(not source_caches, "no source-tree Python caches")

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = str(repo)
    with tempfile.TemporaryDirectory(prefix="aiweb-slice47-verifier-") as cache_temp:
        env["PYTHONPYCACHEPREFIX"] = cache_temp
        py = select_python(repo)
        print("=== CURRENT SLICE 47 BEHAVIOR ===")
        current = run([py, "-u", "-B", str(repo / BEHAVIOR_TEST), str(repo)], repo, env)
        print_visible(current)
        ledger.check(current.returncode == 0, "current Slice 47 behavior return code")
        ledger.check("AI.WEB SLICE 47 BEHAVIOR TEST: PASS" in current.stdout, "current Slice 47 behavior marker")

        print("=== ACCEPTED APPLIED-CONTEXT SLICE 46 VERIFIER ===")
        inherited_rc, inherited_output = run_inherited_slice46(repo, env)
        print(inherited_output, end="" if inherited_output.endswith("\n") or not inherited_output else "\n")
        ledger.check(inherited_rc == 0, "inherited Slice 46 verifier return code")
        ledger.check("AI.WEB SLICE 46 VERIFIER: PASS" in inherited_output, "inherited Slice 46 verifier marker")

    print("=== SLICE 47 VERIFIER SUMMARY ===")
    print("checks=" + str(ledger.passes + len(ledger.failures)))
    print("passes=" + str(ledger.passes))
    print("failures=" + str(len(ledger.failures)))
    print("protected_predecessor_files=" + str(len(predecessor)))
    print("slice47_files=" + str(len(expected)))
    print("selected_status=preserved_as_unchanged_bounded_lane")
    print("gp014_source_unchanged=1")
    print("gp014_adapter_general_interface=0")
    print("gp014_refactored=0")
    print("gp014_replaced=0")
    print("gp014_superseded=0")
    print("phase_d_complete=1")
    print("route_api_ui_memory_resource_tool_action_delivery=0")
    print("production_release_authority=0")
    for failure in ledger.failures:
        print("FAIL - " + failure)
    print("AI.WEB SLICE 47 VERIFIER: " + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
