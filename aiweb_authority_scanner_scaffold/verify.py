"""Verifier for Slice 6 scanner scaffold."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .catalog import assembled_unsafe_catalog, scanner_scope_record, safe_demo_text, unsafe_demo_text
from .scanner import scan_paths, scan_text


REQUIRED_FILES = [
    "aiweb_authority_scanner_scaffold/__init__.py",
    "aiweb_authority_scanner_scaffold/catalog.py",
    "aiweb_authority_scanner_scaffold/scanner.py",
    "aiweb_authority_scanner_scaffold/verify.py",
    "scripts/test_aiweb_slice06_authority_scanner_scaffold.py",
    "scripts/aiweb_slice06_authority_scanner_verify.py",
    "scripts/README_aiweb_slice06_authority_scanner_scaffold.md",
]

ALLOWED_GIT_STATUS_PREFIXES = (
    "?? aiweb_authority_scanner_scaffold/",
    "A  aiweb_authority_scanner_scaffold/",
    "?? scripts/README_aiweb_slice06_authority_scanner_scaffold.md",
    "A  scripts/README_aiweb_slice06_authority_scanner_scaffold.md",
    "?? scripts/aiweb_slice06_authority_scanner_verify.py",
    "A  scripts/aiweb_slice06_authority_scanner_verify.py",
    "?? scripts/test_aiweb_slice06_authority_scanner_scaffold.py",
    "A  scripts/test_aiweb_slice06_authority_scanner_scaffold.py",
)

_BAD_IMPORT_PARTS = [
    ("open", "ai"),
    ("anth", "ropic"),
    ("oll", "ama"),
    ("chrom", "adb"),
    ("lang", "chain"),
    ("ll", "ama"),
    ("fa", "iss"),
    ("torch",),
    ("tensorflow",),
    ("transform", "ers"),
    ("sentence", "_", "transform", "ers"),
    ("sk", "learn"),
]


def _join(parts: Sequence[str]) -> str:
    return "".join(parts)


def _bad_import_names() -> List[str]:
    return [_join(parts) for parts in _BAD_IMPORT_PARTS]


def _run_git(repo: Path, args: Sequence[str]) -> Tuple[int, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode, proc.stdout


def _python_files(repo: Path) -> List[Path]:
    return [repo / item for item in REQUIRED_FILES if item.endswith(".py")]


def _check_python_syntax(path: Path) -> Tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return False, f"{path}: {exc}"
    return True, str(path)


def _check_bad_imports(path: Path) -> Tuple[bool, str]:
    bad = set(_bad_import_names())
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return False, f"{path}: {exc}"
    found: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".")[0].lower()
                if root_name in bad:
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_name = node.module.split(".")[0].lower()
                if root_name in bad:
                    found.append(node.module)
    if found:
        return False, f"{path}: {', '.join(sorted(set(found)))}"
    return True, str(path)


def _check_source_has_no_raw_unsafe(path: Path) -> Tuple[bool, str]:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    hits = []
    for item in assembled_unsafe_catalog():
        if item.phrase.lower() in text:
            hits.append(item.phrase)
    if hits:
        return False, f"{path}: {', '.join(sorted(set(hits)))}"
    return True, str(path)


def verify_slice06(repo: Path) -> Tuple[List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []
    repo = repo.resolve()

    if repo.exists():
        passes.append(f"target repo directory exists: {repo}")
    else:
        failures.append(f"target repo directory missing: {repo}")
        return passes, failures

    if (repo / ".git").is_dir():
        passes.append("target repo is a git repository")
    else:
        failures.append("target repo is not a git repository")

    for rel in REQUIRED_FILES:
        path = repo / rel
        if path.is_file():
            passes.append(f"required file exists: {rel}")
        else:
            failures.append(f"required file missing: {rel}")

    for path in _python_files(repo):
        if not path.exists():
            continue
        ok, detail = _check_python_syntax(path)
        (passes if ok else failures).append(
            f"python syntax valid: {detail}" if ok else f"python syntax invalid: {detail}"
        )
        ok, detail = _check_bad_imports(path)
        (passes if ok else failures).append(
            f"no blocked active imports: {detail}" if ok else f"blocked active import found: {detail}"
        )

    for rel in REQUIRED_FILES:
        path = repo / rel
        if path.is_file():
            ok, detail = _check_source_has_no_raw_unsafe(path)
            (passes if ok else failures).append(
                f"no raw unsafe phrases in source: {detail}" if ok else f"raw unsafe phrase in source: {detail}"
            )

    code, status = _run_git(repo, ["status", "--short"])
    if code == 0:
        bad_lines = []
        for line in status.splitlines():
            if not line.strip():
                continue
            if not any(line.startswith(prefix) for prefix in ALLOWED_GIT_STATUS_PREFIXES):
                bad_lines.append(line)
        if bad_lines:
            failures.append("git status contains out-of-scope paths: " + " | ".join(bad_lines))
        else:
            passes.append("git status is clean or limited to Slice 6 scaffold paths")
    else:
        failures.append("git status command failed")

    scope = scanner_scope_record()
    if scope.get("scanner_only") is True and scope.get("runtime_effect") == "none":
        passes.append("scanner scope record is scanner-only and non-runtime")
    else:
        failures.append("scanner scope record is not scanner-only")

    safe_report = scan_text(safe_demo_text(), path_label="safe_demo")
    if safe_report.passed:
        passes.append("safe demo text produces no findings")
    else:
        failures.append("safe demo text unexpectedly produced findings")

    unsafe_report = scan_text(unsafe_demo_text(), path_label="unsafe_demo")
    categories = {item.category for item in unsafe_report.findings}
    needed = {
        "public_claim_overreach",
        "baseline_failure_path_overclaim",
        "model_or_opaque_authority",
        "retrieval_or_similarity_authority",
        "stored_material_or_action_overreach",
    }
    if needed.issubset(categories):
        passes.append("runtime-assembled unsafe demo text is detected across required categories")
    else:
        failures.append("unsafe demo text did not cover required categories")

    required_paths = [repo / item for item in REQUIRED_FILES]
    package_report = scan_paths(required_paths)
    if package_report.finding_count == 0:
        passes.append("scanner does not flag committed Slice 6 source files")
    else:
        failures.append(f"scanner flagged committed source files: {package_report.finding_count}")

    if len(assembled_unsafe_catalog()) >= 20:
        passes.append("unsafe catalog has broad scanner coverage")
    else:
        failures.append("unsafe catalog coverage is too small")

    return passes, failures


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    repo = Path(args[0]) if args else Path.cwd()
    print("=" * 60)
    print("AIWEB SLICE 6 UNIFIED AUTHORITY SCANNER SCAFFOLD VERIFIER")
    print("=" * 60)
    print(f"Target repo: {repo}")
    passes, failures = verify_slice06(repo)
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL - Slice 6 scanner scaffold verifier failed")
        return 1
    print("VERDICT: PASS - Slice 6 scanner scaffold verifier passed within Slice 6 scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
