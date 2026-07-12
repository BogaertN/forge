"""Read-only repository context checks for Slice 24."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import subprocess

from .authority import (
    REQUIRED_FORGE_BRANCH,
    REQUIRED_FORGE_HEAD_BEFORE_SLICE24,
    REQUIRED_FORGE_HEAD_SUBJECT_BEFORE_SLICE24,
    REQUIRED_AIWEB_HEAD_SLICE22,
    REQUIRED_AIWEB_SUBJECT_SLICE22,
    REQUIRED_EXTERNAL_CONTEXT_CHECKS,
)

@dataclass(frozen=True)
class CommandCapture:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    def as_dict(self) -> dict[str, object]:
        return {
            "args": list(self.args),
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }

@dataclass(frozen=True)
class ForgeContext:
    repo: str
    branch: str
    head: str
    subject: str
    status_porcelain: str
    cached_diff: str
    unstaged_diff: str
    python_cache_hits: tuple[str, ...]
    clean_for_acceptance: bool
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "repo": self.repo,
            "branch": self.branch,
            "head": self.head,
            "subject": self.subject,
            "status_porcelain": self.status_porcelain,
            "cached_diff": self.cached_diff,
            "unstaged_diff": self.unstaged_diff,
            "python_cache_hits": list(self.python_cache_hits),
            "clean_for_acceptance": self.clean_for_acceptance,
            "failures": list(self.failures),
        }

@dataclass(frozen=True)
class ExternalContext:
    repo: str
    head: str
    subject: str
    focused_status: str
    focused_cached: str
    focused_unstaged: str
    passed: bool
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "repo": self.repo,
            "head": self.head,
            "subject": self.subject,
            "focused_status": self.focused_status,
            "focused_cached": self.focused_cached,
            "focused_unstaged": self.focused_unstaged,
            "passed": self.passed,
            "failures": list(self.failures),
        }


def _git(repo: Path, *args: str) -> CommandCapture:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )
    return CommandCapture(tuple(["git", "-C", str(repo), *args]), result.returncode, result.stdout, result.stderr)


def scan_python_cache(root: Path) -> tuple[str, ...]:
    hits: list[str] = []
    if not root.exists():
        return tuple(hits)
    for walk_root, dirs, files in os.walk(root):
        walk_path = Path(walk_root)
        if ".git" in walk_path.parts:
            continue
        if any(part in {"node_modules", "dist", "build", ".next", ".turbo", ".cache"} for part in walk_path.parts):
            continue
        for dirname in dirs:
            if dirname == "__pycache__":
                hits.append(str(walk_path / dirname))
        for filename in files:
            if filename.endswith((".pyc", ".pyo")):
                hits.append(str(walk_path / filename))
    return tuple(sorted(hits))


def inspect_forge_context(root: Path, *, require_exact_head: bool = False) -> ForgeContext:
    failures: list[str] = []
    if not root.is_dir():
        failures.append(f"Forge root missing: {root}")
        return ForgeContext(str(root), "", "", "", "", "", "", tuple(), False, tuple(failures))

    top = _git(root, "rev-parse", "--show-toplevel")
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    head = _git(root, "rev-parse", "HEAD")
    subject = _git(root, "log", "-1", "--pretty=%s")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    cached = _git(root, "diff", "--cached", "--name-only")
    unstaged = _git(root, "diff", "--name-only")
    cache_hits = scan_python_cache(root)

    if top.returncode != 0 or top.stdout.strip() != str(root):
        failures.append("forge_top_level_mismatch")
    if branch.returncode != 0 or branch.stdout.strip() != REQUIRED_FORGE_BRANCH:
        failures.append("forge_branch_not_main")
    if require_exact_head and (head.returncode != 0 or head.stdout.strip() != REQUIRED_FORGE_HEAD_BEFORE_SLICE24):
        failures.append("forge_head_not_required_pre_slice24_head")
    if require_exact_head and (subject.returncode != 0 or subject.stdout.strip() != REQUIRED_FORGE_HEAD_SUBJECT_BEFORE_SLICE24):
        failures.append("forge_subject_not_required_pre_slice24_subject")
    if status.stdout.strip():
        failures.append("forge_status_not_clean")
    if cached.stdout.strip():
        failures.append("forge_cached_diff_not_empty")
    if unstaged.stdout.strip():
        failures.append("forge_unstaged_diff_not_empty")
    if cache_hits:
        failures.append("python_cache_artifacts_present")

    return ForgeContext(
        repo=str(root),
        branch=branch.stdout.strip(),
        head=head.stdout.strip(),
        subject=subject.stdout.strip(),
        status_porcelain=status.stdout,
        cached_diff=cached.stdout,
        unstaged_diff=unstaged.stdout,
        python_cache_hits=cache_hits,
        clean_for_acceptance=not failures,
        failures=tuple(failures),
    )


def inspect_slice22_external_context(aiweb_root: Path | None = None) -> ExternalContext:
    check = REQUIRED_EXTERNAL_CONTEXT_CHECKS[0]
    root = Path(aiweb_root or check["repo"])
    failures: list[str] = []

    if not root.is_dir():
        failures.append(f"aiweb_repo_missing:{root}")
        return ExternalContext(str(root), "", "", "", "", "", False, tuple(failures))

    head = _git(root, "rev-parse", "HEAD")
    subject = _git(root, "log", "-1", "--pretty=%s")
    focused_status = _git(root, "status", "--porcelain=v1", "--untracked-files=all", "--", *check["exact_paths"])
    focused_cached = _git(root, "diff", "--cached", "--name-only", "--", *check["exact_paths"])
    focused_unstaged = _git(root, "diff", "--name-only", "--", *check["exact_paths"])

    if head.returncode != 0 or head.stdout.strip() != REQUIRED_AIWEB_HEAD_SLICE22:
        failures.append("aiweb_head_not_required_slice22_head")
    if subject.returncode != 0 or subject.stdout.strip() != REQUIRED_AIWEB_SUBJECT_SLICE22:
        failures.append("aiweb_subject_not_slice22_subject")
    if focused_status.stdout.strip():
        failures.append("aiweb_slice22_exact_paths_not_clean")
    if focused_cached.stdout.strip():
        failures.append("aiweb_slice22_exact_paths_cached_diff")
    if focused_unstaged.stdout.strip():
        failures.append("aiweb_slice22_exact_paths_unstaged_diff")

    return ExternalContext(
        repo=str(root),
        head=head.stdout.strip(),
        subject=subject.stdout.strip(),
        focused_status=focused_status.stdout,
        focused_cached=focused_cached.stdout,
        focused_unstaged=focused_unstaged.stdout,
        passed=not failures,
        failures=tuple(failures),
    )
