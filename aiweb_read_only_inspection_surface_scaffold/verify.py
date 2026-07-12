"""Verifier for Slice 21 read-only inspection surface boundary scaffold."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Iterable

from .boundary import check_boundary_integrity
from .core import (
    EXPECTED_COMMIT_SUBJECT,
    REQUIRED_BASE_HEAD_FOR_APPLICATION,
    REQUIRED_BASE_PARENT_FOR_APPLICATION,
    REQUIRED_BASE_SUBJECT_FOR_APPLICATION,
    SLICE_ID,
    SLICE_TITLE,
)
from .receipt import build_receipt

EXPECTED_PAYLOAD_FILES: tuple[str, ...] = (
    "aiweb_read_only_inspection_surface_scaffold/__init__.py",
    "aiweb_read_only_inspection_surface_scaffold/authority.py",
    "aiweb_read_only_inspection_surface_scaffold/boundary.py",
    "aiweb_read_only_inspection_surface_scaffold/core.py",
    "aiweb_read_only_inspection_surface_scaffold/receipt.py",
    "aiweb_read_only_inspection_surface_scaffold/verify.py",
    "scripts/README_aiweb_slice21_read_only_inspection_surface_scaffold.md",
    "scripts/aiweb_slice21_read_only_inspection_surface_verify.py",
    "scripts/test_aiweb_slice21_read_only_inspection_surface_scaffold.py",
)

PROHIBITED_SOURCE_FRAGMENTS: tuple[str, ...] = (
    "shell" + "=True",
    "os." + "system(",
    "socket" + ".",
    "requests" + ".",
    "httpx" + ".",
    "urllib" + ".request",
    "smtplib" + ".",
    "send" + "_email(",
    "send" + "_draft(",
    "forward" + "_emails(",
    "create" + "_event(",
    "update" + "_event(",
    "delete" + "_event(",
    "gmail" + ".",
    "gcal" + ".",
    ".write" + "_text(",
    ".write" + "_bytes(",
)

FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "open" + "ai",
    "anthropic",
    "chromadb",
    "langchain",
    "faiss",
    "sklearn",
    "sentence" + "_transformers",
    "transformers",
    "torch",
    "tensorflow",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "smtplib",
    "gmail",
    "gcal",
)

VERIFY_ONLY_IMPORT_ROOTS: tuple[str, ...] = ("subprocess",)


@dataclass(frozen=True, slots=True)
class VerificationResult:
    passed: bool
    context_label: str
    failures: tuple[str, ...]
    checked_files: tuple[str, ...]

    def render(self) -> str:
        lines = [
            "AIWEB SLICE 21 VERIFIER",
            "slice=" + SLICE_ID,
            "title=" + SLICE_TITLE,
            "context_label=" + self.context_label,
            "checked_file_count=" + str(len(self.checked_files)),
        ]
        if self.failures:
            lines.append("failures:")
            lines.extend(" - " + item for item in self.failures)
        lines.append("VERDICT: " + ("PASS" if self.passed else "FAIL"))
        return "\n".join(lines)


def _run_git(repo: Path, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode, result.stdout.rstrip("\n"), result.stderr.rstrip("\n")


def _detect_context(repo: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    code_head, head, err_head = _run_git(repo, "rev-parse", "HEAD")
    code_parent, parent, err_parent = _run_git(repo, "rev-parse", "HEAD^")
    code_subject, subject, err_subject = _run_git(repo, "log", "-1", "--pretty=%s")
    code_status, porcelain, err_status = _run_git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    code_cached, cached_names, err_cached = _run_git(repo, "diff", "--cached", "--name-only")

    if code_head != 0:
        failures.append("could not read HEAD: " + err_head)
    if code_parent != 0:
        failures.append("could not read HEAD parent: " + err_parent)
    if code_subject != 0:
        failures.append("could not read HEAD subject: " + err_subject)
    if code_status != 0:
        failures.append("could not read status: " + err_status)
    if code_cached != 0:
        failures.append("could not read cached diff: " + err_cached)
    if failures:
        return "invalid_git_context", failures

    cached_set = {line.strip() for line in cached_names.splitlines() if line.strip()}
    payload_set = set(EXPECTED_PAYLOAD_FILES)

    if head == REQUIRED_BASE_HEAD_FOR_APPLICATION and subject == REQUIRED_BASE_SUBJECT_FOR_APPLICATION:
        if parent != REQUIRED_BASE_PARENT_FOR_APPLICATION:
            failures.append("base parent mismatch for Slice 20 HEAD")
            return "invalid_base_parent", failures

        lines = porcelain.splitlines()
        untracked = {line[3:] for line in lines if line.startswith("?? ")}
        staged_adds = {line[3:] for line in lines if line.startswith("A  ")}
        other = [line for line in lines if not (line.startswith("?? ") or line.startswith("A  "))]

        if untracked == payload_set and not staged_adds and not cached_set and not other:
            return "slice21_precommit_untracked_patch_context", failures
        if staged_adds == payload_set and cached_set == payload_set and not untracked and not other:
            return "slice21_precommit_staged_patch_context", failures

        failures.append("base HEAD detected but working tree is not exact Slice 21 patch context")
        return "invalid_base_patch_context", failures

    if subject == EXPECTED_COMMIT_SUBJECT:
        if parent != REQUIRED_BASE_HEAD_FOR_APPLICATION:
            code_ancestor, _, _ = _run_git(repo, "merge-base", "--is-ancestor", REQUIRED_BASE_HEAD_FOR_APPLICATION, "HEAD")
            if code_ancestor != 0:
                failures.append("Slice 20 base is not an ancestor of current HEAD")
                return "invalid_committed_context", failures
        if porcelain.strip():
            failures.append("committed Slice 21 context must be clean")
            return "invalid_committed_context", failures
        return "slice21_clean_committed_context", failures

    code_ancestor, _, _ = _run_git(repo, "merge-base", "--is-ancestor", REQUIRED_BASE_HEAD_FOR_APPLICATION, "HEAD")
    if code_ancestor == 0 and not porcelain.strip():
        return "slice21_or_later_clean_committed_context", failures

    failures.append("repository is neither exact Slice 21 patch context nor clean committed descendant context")
    return "unknown_context", failures


def _check_files_exist(repo: Path, paths: Iterable[str]) -> list[str]:
    failures: list[str] = []
    for rel in paths:
        if not (repo / rel).is_file():
            failures.append("missing expected payload file: " + rel)
    return failures


def _python_payload_files(paths: Iterable[str]) -> tuple[str, ...]:
    return tuple(rel for rel in paths if rel.endswith(".py"))


def _import_roots(tree: ast.AST) -> tuple[str, ...]:
    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.level == 0:
                roots.append(node.module.split(".", 1)[0])
    return tuple(roots)


def _check_sources_parse_and_imports(repo: Path, paths: Iterable[str]) -> list[str]:
    failures: list[str] = []
    for rel in _python_payload_files(paths):
        path = repo / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(rel + " does not parse: " + str(exc))
            continue

        roots = _import_roots(tree)
        for root in roots:
            if root in FORBIDDEN_IMPORT_ROOTS:
                failures.append(rel + " imports forbidden root: " + root)
            if root in VERIFY_ONLY_IMPORT_ROOTS and not rel.endswith("/verify.py"):
                failures.append(rel + " imports verifier-only root outside verifier: " + root)
    return failures


def _check_no_prohibited_fragments(repo: Path, paths: Iterable[str]) -> list[str]:
    failures: list[str] = []
    for rel in _python_payload_files(paths):
        path = repo / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for fragment in PROHIBITED_SOURCE_FRAGMENTS:
            if fragment in text:
                failures.append(rel + " contains prohibited source fragment: " + fragment)
    return failures


def verify_slice21_boundary(repo: str | Path = ".", *, require_git_context: bool = True) -> VerificationResult:
    repo_path = Path(repo).resolve()
    failures: list[str] = []

    boundary_result = check_boundary_integrity()
    if not boundary_result.passed:
        failures.extend(boundary_result.failures)

    receipt = build_receipt()
    if receipt.verdict != "PASS":
        failures.append("receipt verdict was not PASS")
    if receipt.runtime_effect != "no_runtime_authority_no_state_change_no_memory_write_no_tool_route_no_delivery":
        failures.append("receipt runtime effect changed")
    if receipt.production_effect != "no_live_api_no_route_registration_no_ui_no_config_change_no_deployment":
        failures.append("receipt production effect changed")

    if require_git_context:
        context_label, context_failures = _detect_context(repo_path)
        failures.extend(context_failures)
    else:
        context_label = "git_context_not_required_for_source_behavior_test"

    failures.extend(_check_files_exist(repo_path, EXPECTED_PAYLOAD_FILES))
    failures.extend(_check_sources_parse_and_imports(repo_path, EXPECTED_PAYLOAD_FILES))
    failures.extend(_check_no_prohibited_fragments(repo_path, EXPECTED_PAYLOAD_FILES))

    return VerificationResult(
        passed=not failures,
        context_label=context_label,
        failures=tuple(failures),
        checked_files=EXPECTED_PAYLOAD_FILES,
    )
