"""Slice 2 verifier for GP-014 baseline preservation scaffold."""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path
from typing import Any

from .baseline import build_gp014_baseline_record, find_gp014_marker_files
from .regression import build_regression_receipt, validate_regression_receipt

REQUIRED_FILES = [
    "aiweb_gp014_regression_scaffold/__init__.py",
    "aiweb_gp014_regression_scaffold/baseline.py",
    "aiweb_gp014_regression_scaffold/regression.py",
    "aiweb_gp014_regression_scaffold/verify.py",
    "scripts/test_aiweb_slice02_gp014_regression_scaffold.py",
    "scripts/aiweb_slice02_gp014_regression_verify.py",
    "scripts/README_aiweb_slice02_gp014_regression_scaffold.md",
]

FORBIDDEN_IMPORT_ROOTS = {
    "openai",
    "ollama",
    "chromadb",
    "langchain",
    "faiss",
    "llama_index",
    "requests",
    "httpx",
    "urllib3",
    "sentence_transformers",
    "transformers",
    "torch",
}

ALLOWED_STATUS_PREFIXES = (
    "?? aiweb_gp014_regression_scaffold/",
    "?? scripts/test_aiweb_slice02_gp014_regression_scaffold.py",
    "?? scripts/aiweb_slice02_gp014_regression_verify.py",
    "?? scripts/README_aiweb_slice02_gp014_regression_scaffold.md",
    "A  aiweb_gp014_regression_scaffold/",
    "A  scripts/test_aiweb_slice02_gp014_regression_scaffold.py",
    "A  scripts/aiweb_slice02_gp014_regression_verify.py",
    "A  scripts/README_aiweb_slice02_gp014_regression_scaffold.md",
)


def _run_git(repo_path: Path, args: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_path), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def _python_files(repo_path: Path) -> list[Path]:
    return [repo_path / rel for rel in REQUIRED_FILES if rel.endswith(".py")]


def _parse_import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots


def _status_paths_allowed(repo_path: Path) -> tuple[bool, list[str]]:
    code, stdout, _stderr = _run_git(repo_path, ["status", "--short"])
    if code != 0:
        return False, ["git status failed"]
    bad: list[str] = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        if not any(line.startswith(prefix) for prefix in ALLOWED_STATUS_PREFIXES):
            bad.append(line)
    return not bad, bad


def verify_slice02_gp014_regression_scaffold(repo_path: str | Path) -> dict[str, Any]:
    repo = Path(repo_path).resolve()
    passes: list[str] = []
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        if condition:
            passes.append(label)
        else:
            failures.append(label)

    check(str(repo) == "/home/nic/forge", "target repo is exactly /home/nic/forge")
    check(repo.exists(), "target repo directory exists")
    check((repo / ".git").is_dir(), "target repo is a git repository")

    for rel in REQUIRED_FILES:
        check((repo / rel).is_file(), f"required file exists: {rel}")

    for path in _python_files(repo):
        if not path.is_file():
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
            passes.append(f"python syntax valid: {path.relative_to(repo).as_posix()}")
        except SyntaxError as exc:
            failures.append(f"python syntax invalid: {path.relative_to(repo).as_posix()}: {exc}")
        try:
            roots = _parse_import_roots(path)
            forbidden = sorted(roots & FORBIDDEN_IMPORT_ROOTS)
            check(not forbidden, f"no forbidden active model/network imports: {path.relative_to(repo).as_posix()}")
            if forbidden:
                failures.append(f"forbidden imports in {path.relative_to(repo).as_posix()}: {forbidden}")
        except SyntaxError:
            pass

    allowed, bad_status = _status_paths_allowed(repo)
    check(allowed, "git status contains only Slice 2 scaffold paths")
    for item in bad_status:
        failures.append(f"out-of-scope git status entry: {item}")

    marker_files = find_gp014_marker_files(repo)
    check(bool(marker_files), "GP-014 / LANG-EXPR marker files discoverable")

    baseline = build_gp014_baseline_record(repo, include_timestamp=False, discovered_files=marker_files)
    check(baseline.get("baseline_identity") == "LANG-EXPR-001 / GP-014", "baseline identity preserved")
    check(baseline.get("preservation_status") == "preserved_not_superseded", "baseline status is preserved_not_superseded")
    check(baseline.get("explicit_non_claims", {}).get("gp014_superseded") is False, "baseline record does not claim GP-014 supersession")
    check(baseline.get("explicit_non_claims", {}).get("gp014_replaced") is False, "baseline record does not claim GP-014 replacement")

    sample_changed = [
        "aiweb_gp014_regression_scaffold/__init__.py",
        "aiweb_gp014_regression_scaffold/baseline.py",
        "aiweb_gp014_regression_scaffold/regression.py",
        "aiweb_gp014_regression_scaffold/verify.py",
        "scripts/test_aiweb_slice02_gp014_regression_scaffold.py",
        "scripts/aiweb_slice02_gp014_regression_verify.py",
        "scripts/README_aiweb_slice02_gp014_regression_scaffold.md",
    ]
    receipt = build_regression_receipt(repo, baseline, changed_files=sample_changed, include_timestamp=False)
    result = validate_regression_receipt(receipt)
    check(result.get("passed") is True, "sample Slice 2 regression receipt validates")

    bad_receipt = build_regression_receipt(repo, baseline, changed_files=["some/GP-014_runtime.py"], include_timestamp=False)
    bad_result = validate_regression_receipt(bad_receipt)
    check(bad_result.get("passed") is False, "bad GP-014-touching receipt fails validation")

    return {
        "passed": not failures,
        "passes": passes,
        "failures": failures,
    }
