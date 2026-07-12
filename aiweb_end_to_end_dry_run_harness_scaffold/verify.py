"""Verifier for Slice 23 end-to-end dry-run harness scaffold."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Iterable

from .authority import (
    DOWNSTREAM_FALSE_ONLY_FIELDS,
    EXPECTED_COMMIT_SUBJECT,
    REQUIRED_BASE_HEAD_FOR_APPLICATION,
    REQUIRED_BASE_PARENT_FOR_APPLICATION,
    REQUIRED_BASE_SUBJECT_FOR_APPLICATION,
    REQUIRED_DRY_RUN_LAWS,
    REQUIRED_DRY_RUN_STEP_ORDER,
    SLICE_ID,
    SLICE_TITLE,
    build_authority_separation_record,
    validate_authority_separation_record,
)
from .core import build_demo_harness_record, validate_dry_run_harness_record
from .fixture import BLOCKED_ACTION_FIXTURE_KEY, SAFE_DISPLAY_FIXTURE_KEY, build_default_fixtures
from .receipt import build_receipt, validate_receipt

EXPECTED_PAYLOAD_FILES: tuple[str, ...] = (
    "aiweb_end_to_end_dry_run_harness_scaffold/__init__.py",
    "aiweb_end_to_end_dry_run_harness_scaffold/authority.py",
    "aiweb_end_to_end_dry_run_harness_scaffold/fixture.py",
    "aiweb_end_to_end_dry_run_harness_scaffold/core.py",
    "aiweb_end_to_end_dry_run_harness_scaffold/receipt.py",
    "aiweb_end_to_end_dry_run_harness_scaffold/verify.py",
    "scripts/README_aiweb_slice23_end_to_end_dry_run_harness_scaffold.md",
    "scripts/aiweb_slice23_end_to_end_dry_run_harness_verify.py",
    "scripts/test_aiweb_slice23_end_to_end_dry_run_harness_scaffold.py",
)

FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "open" + "ai",
    "anthropic",
    "ollama",
    "langchain",
    "llama" + "_index",
    "requests",
    "httpx",
    "url" + "lib",
    "socket",
    "smtplib",
    "gmail",
    "gcal",
)

VERIFY_ONLY_IMPORT_ROOTS: tuple[str, ...] = ("sub" + "process",)

PROHIBITED_SOURCE_FRAGMENTS: tuple[str, ...] = (
    "shell" + "=True",
    "os." + "system(",
    "requests" + ".",
    "httpx" + ".",
    "url" + "lib.request",
    "socket" + ".",
    "smtplib" + ".",
    "send" + "_email(",
    "send" + "_draft(",
    "forward" + "_emails(",
    "create" + "_event(",
    "update" + "_event(",
    "delete" + "_event(",
    "memory" + "_writer.write",
    "manifest" + "_" + "memory" + "_" + "writer",
    "controlled" + "_" + "manifest" + "_" + "memory" + "_" + "writer",
    "tool" + ".invoke",
    "tool" + ".dispatch",
    "execute" + "_" + "action(",
    "git " + "push",
    "git " + "pull",
    "git " + "fetch",
    "bundle " + "create",
    "P" + "OST",
    "P" + "UT",
    "P" + "ATCH",
    "D" + "ELETE",
)


@dataclass(frozen=True, slots=True)
class VerificationResult:
    passed: bool
    context_label: str
    failures: tuple[str, ...]
    checked_files: tuple[str, ...]

    def render(self) -> str:
        lines = [
            "AIWEB SLICE 23 DRY-RUN HARNESS VERIFIER",
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


def _payload_set() -> set[str]:
    return set(EXPECTED_PAYLOAD_FILES)


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
    payload_set = _payload_set()

    if head == REQUIRED_BASE_HEAD_FOR_APPLICATION and subject == REQUIRED_BASE_SUBJECT_FOR_APPLICATION:
        if parent != REQUIRED_BASE_PARENT_FOR_APPLICATION:
            failures.append("base parent mismatch for Slice 21 HEAD")
            return "invalid_base_parent", failures

        lines = porcelain.splitlines()
        untracked = {line[3:] for line in lines if line.startswith("?? ")}
        staged_adds = {line[3:] for line in lines if line.startswith("A  ")}
        other = [line for line in lines if not (line.startswith("?? ") or line.startswith("A  "))]

        if untracked == payload_set and not staged_adds and not cached_set and not other:
            return "slice23_untracked_patch_context", failures
        if staged_adds == payload_set and cached_set == payload_set and not untracked and not other:
            return "slice23_precommit_staged_patch_context", failures

        failures.append("base HEAD detected but working tree is not exact Slice 23 patch context")
        return "invalid_base_patch_context", failures

    if subject == EXPECTED_COMMIT_SUBJECT:
        if parent != REQUIRED_BASE_HEAD_FOR_APPLICATION:
            failures.append("Slice 23 commit parent mismatch")
            return "invalid_committed_context", failures
        if porcelain.strip():
            failures.append("committed Slice 23 context must be clean")
            return "invalid_committed_context", failures
        return "slice23_clean_committed_context", failures

    code_log, subjects, err_log = _run_git(repo, "log", "--format=%s")
    if code_log == 0 and EXPECTED_COMMIT_SUBJECT in subjects.splitlines() and not porcelain.strip():
        return "slice23_or_later_clean_committed_context", failures
    if code_log != 0:
        failures.append("could not inspect commit subjects: " + err_log)

    failures.append("repository is neither exact Slice 23 patch context nor clean committed Slice 23 descendant context")
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


def _check_source_behavior() -> list[str]:
    failures: list[str] = []

    authority = build_authority_separation_record()
    authority_report = validate_authority_separation_record(authority)
    if not authority_report.passed:
        failures.extend("authority." + issue.field + ":" + issue.reason for issue in authority_report.issues)
    if authority.dry_run_laws != REQUIRED_DRY_RUN_LAWS:
        failures.append("authority laws changed")
    if authority.dry_run_step_order != REQUIRED_DRY_RUN_STEP_ORDER:
        failures.append("authority step order changed")
    for field_name in DOWNSTREAM_FALSE_ONLY_FIELDS:
        if bool(getattr(authority, field_name)):
            failures.append("authority flag became true: " + field_name)

    fixtures = build_default_fixtures()
    if tuple(f.fixture_key for f in fixtures) != (SAFE_DISPLAY_FIXTURE_KEY, BLOCKED_ACTION_FIXTURE_KEY):
        failures.append("fixture identity or order changed")

    harness = build_demo_harness_record()
    harness_report = validate_dry_run_harness_record(harness)
    if not harness_report.passed:
        failures.extend("harness." + issue.field + ":" + issue.reason for issue in harness_report.issues)

    for path in harness.paths:
        if path.step_order != REQUIRED_DRY_RUN_STEP_ORDER:
            failures.append("path step order changed for " + path.fixture_key)
        if tuple(step.step_key for step in path.steps) != REQUIRED_DRY_RUN_STEP_ORDER:
            failures.append("step record sequence changed for " + path.fixture_key)
        if path.fixture_key == BLOCKED_ACTION_FIXTURE_KEY:
            if not path.blocked_before_memory_delivery_or_action:
                failures.append("blocked fixture did not remain blocked before effects")
            if not path.no_memory_write or not path.no_delivery or not path.no_action:
                failures.append("blocked fixture effect boundary changed")

    receipt_a = build_receipt(harness)
    receipt_b = build_receipt(build_demo_harness_record())
    failures.extend(validate_receipt(receipt_a))
    if receipt_a.receipt_id != receipt_b.receipt_id:
        failures.append("receipt id is not stable across rebuild")
    if receipt_a.harness_digest != receipt_b.harness_digest:
        failures.append("receipt harness digest is not stable across rebuild")

    return failures


def verify_slice23_boundary(repo: str | Path = ".", *, require_git_context: bool = True) -> VerificationResult:
    repo_path = Path(repo).resolve()
    failures: list[str] = []

    if require_git_context:
        context_label, context_failures = _detect_context(repo_path)
        failures.extend(context_failures)
    else:
        context_label = "git_context_not_required_for_source_behavior_test"

    failures.extend(_check_files_exist(repo_path, EXPECTED_PAYLOAD_FILES))
    failures.extend(_check_sources_parse_and_imports(repo_path, EXPECTED_PAYLOAD_FILES))
    failures.extend(_check_no_prohibited_fragments(repo_path, EXPECTED_PAYLOAD_FILES))
    failures.extend(_check_source_behavior())

    return VerificationResult(
        passed=not failures,
        context_label=context_label,
        failures=tuple(failures),
        checked_files=EXPECTED_PAYLOAD_FILES,
    )
