#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

EXPECTED_BASE_HEAD = "cf2d5dc94113a857d0ffd53dd4710534df1aa55e"
EXPECTED_BASE_PARENT = "3b640f380b8633ce93143d178dcbee143503f03d"
EXPECTED_BASE_SUBJECT = "Slice 17 output expression boundary scaffold"

EXPECTED_SLICE18_HEAD = "7046051567b5d82c98811f64b2413e746da70a97"
EXPECTED_SLICE18_PARENT = EXPECTED_BASE_HEAD
EXPECTED_SLICE18_SUBJECT = "Slice 18 GP-014 preservation wrapper decision scaffold"

ALLOWED_NEW_PATHS = (
    "aiweb_gp014_preservation_decision_scaffold/__init__.py",
    "aiweb_gp014_preservation_decision_scaffold/core.py",
    "aiweb_gp014_preservation_decision_scaffold/gp014_reference.py",
    "aiweb_gp014_preservation_decision_scaffold/wrapper_decision.py",
    "aiweb_gp014_preservation_decision_scaffold/preservation_receipt.py",
    "aiweb_gp014_preservation_decision_scaffold/verify.py",
    "scripts/README_aiweb_slice18_gp014_preservation_decision_scaffold.md",
    "scripts/aiweb_slice18_gp014_preservation_decision_verify.py",
    "scripts/test_aiweb_slice18_gp014_preservation_decision_scaffold.py",
)

PROTECTED_HASHES = {
    "rmc_engine_v1/general_pipeline/gp014_operator_guided_language_realizer.py": "431e6c2133a06204131f81276c11b05528ed8e6553a0d5590555ffd23ef38473",
    "rmc_engine_v1/general_pipeline/symbolic_math_operator_language_realizer.py": "f1f2486504bb987d705efee70d775c1549d3597f5153d30e87cbf11f38bedf1a",
    "rmc_engine_v1/reference/symbolic_math_expression_lexicon_v1_gp014.json": "e99c7691d0ba951343bdf80a82d65d19e464b660bedd942b9a9db2b16283c93e",
    "scripts/test_operator_guided_language_realizer_build_langexpr001_gp014.py": "d047b3ca07c13e4e29ab55f9aa8fb357ee87a1a7d649ea2b23f68f30b75af3be",
    "scripts/operator_guided_language_realizer_build_langexpr001_gp014_verify.py": "c84800156011727cd49f743b722502c60f555c109859ff79aa399cb32ae4d797",
    "rmc_engine_v1/general_pipeline/gp015_ask_forge_trace_surface.py": "9449cdac60047d6d9dd4522e0d4128b72dd86485db225c21203dfd234ba53453",
    "aiweb_output_expression_boundary_scaffold/__init__.py": "35f61a64a3eeb1cac5ed5a2640540025f4d46b0486cc338ecc1ffdd30e932183",
}

FORBIDDEN_IMPORT_PREFIXES = (
    "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer",
    "rmc_engine_v1.general_pipeline.symbolic_math_operator_language_realizer",
    "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface",
    "rmc_engine_v1.renderer",
    "rmc_engine_v1.llm_renderer",
    "rmc_engine_v1.chroma_connector",
    "aiweb_output_expression_boundary_scaffold",
    "openai",
    "anthropic",
    "chromadb",
    "langchain",
    "faiss",
    "sklearn",
    "sentence_transformers",
    "transformers",
    "torch",
    "tensorflow",
    "requests",
    "httpx",
    "urllib",
    "socket",
    "sqlite3",
    "ollama",
    "llama_cpp",
)


@dataclass(frozen=True)
class RepositoryContext:
    head: str
    parent: str
    subject: str
    status_lines: Tuple[str, ...]
    slice18_is_ancestor: bool
    slice18_parent: str
    slice18_subject: str
    slice18_name_status_lines: Tuple[str, ...]


def _run_git(repo: Path, *args: str) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        return 127, "GIT_NOT_FOUND"
    return proc.returncode, proc.stdout.rstrip("\n")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _status_path(line: str) -> str:
    cleaned = line[3:] if len(line) > 3 else line
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ", 1)[1]
    return cleaned.strip()


def _status_lines(repo: Path) -> List[str]:
    code, output = _run_git(repo, "status", "--short")
    if code != 0:
        return [output or "GIT_STATUS_FAILED"]
    lines: List[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        path = _status_path(line)
        if "__pycache__/" in path or path.endswith((".pyc", ".pyo")):
            continue
        lines.append(line)
    return lines


def _imports(path: Path) -> List[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def _is_forbidden_import(name: str) -> bool:
    root = name.split(".")[0]
    if root in {prefix.split(".")[0] for prefix in FORBIDDEN_IMPORT_PREFIXES if "." not in prefix}:
        return True
    return any(name == prefix or name.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES)


def _check(label: str, condition: bool, passes: List[str], failures: List[str]) -> None:
    (passes if condition else failures).append(label)


def _slice18_commit_paths_from_name_status(lines: Sequence[str]) -> Tuple[set[str], List[str]]:
    added_paths: set[str] = set()
    bad_lines: List[str] = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            bad_lines.append(line)
            continue
        status, path = parts
        if status == "A":
            added_paths.add(path)
        else:
            bad_lines.append(line)
    return added_paths, bad_lines


def _status_paths_are_allowed(status_lines: Iterable[str]) -> Tuple[bool, List[str]]:
    bad: List[str] = []
    allowed_dir = "aiweb_gp014_preservation_decision_scaffold"
    allowed_set = set(ALLOWED_NEW_PATHS)
    for line in status_lines:
        rel_path = _status_path(line)
        if rel_path in allowed_set or rel_path.rstrip("/") == allowed_dir:
            continue
        bad.append(line)
    return not bad, bad


def classify_repository_context(context: RepositoryContext) -> Tuple[str, List[str], List[str]]:
    passes: List[str] = []
    failures: List[str] = []

    staged_or_untracked_allowed, bad_status = _status_paths_are_allowed(context.status_lines)

    if context.head == EXPECTED_BASE_HEAD:
        label = "slice18_precommit_patch_context"
        _check("context is pre-commit Slice 18 patch context", True, passes, failures)
        _check("pre-commit parent remains accepted Slice 17 parent", context.parent == EXPECTED_BASE_PARENT, passes, failures)
        _check("pre-commit subject remains Slice 17 base subject", context.subject == EXPECTED_BASE_SUBJECT, passes, failures)
        _check("pre-commit status limited to Slice 18 additive paths", staged_or_untracked_allowed, passes, failures)
        for line in bad_status:
            failures.append("unexpected pre-commit status line: " + line)
        return label, passes, failures

    if context.slice18_is_ancestor:
        label = "slice18_postcommit_or_descendant_clean_context"
        _check("context is post-commit or later descendant of Slice 18", True, passes, failures)
        _check("Slice 18 commit parent is accepted Slice 17 HEAD", context.slice18_parent == EXPECTED_SLICE18_PARENT, passes, failures)
        _check("Slice 18 commit subject is accepted", context.slice18_subject == EXPECTED_SLICE18_SUBJECT, passes, failures)
        _check("post-commit descendant working tree is clean", len(context.status_lines) == 0, passes, failures)

        added_paths, bad_name_status = _slice18_commit_paths_from_name_status(context.slice18_name_status_lines)
        expected_paths = set(ALLOWED_NEW_PATHS)
        _check("Slice 18 commit changed exactly expected additive paths", added_paths == expected_paths and not bad_name_status, passes, failures)
        for path in sorted(expected_paths - added_paths):
            failures.append("Slice 18 commit missing expected path: " + path)
        for path in sorted(added_paths - expected_paths):
            failures.append("Slice 18 commit has unexpected path: " + path)
        for line in bad_name_status:
            failures.append("Slice 18 commit non-additive or malformed change: " + line)
        return label, passes, failures

    label = "unaccepted_repository_context"
    failures.append("Repository is neither accepted Slice 18 pre-commit context nor clean Slice 18 post-commit/descendant context.")
    failures.append("head=" + context.head)
    failures.append("parent=" + context.parent)
    failures.append("subject=" + context.subject)
    return label, passes, failures


def _git_repository_context(repo: Path) -> RepositoryContext:
    _, head = _run_git(repo, "rev-parse", "HEAD")
    _, parent = _run_git(repo, "rev-parse", "HEAD^")
    _, subject = _run_git(repo, "log", "-1", "--pretty=%s")

    merge_code, _ = _run_git(repo, "merge-base", "--is-ancestor", EXPECTED_SLICE18_HEAD, "HEAD")
    slice18_is_ancestor = merge_code == 0

    _, slice18_parent = _run_git(repo, "rev-parse", EXPECTED_SLICE18_HEAD + "^")
    _, slice18_subject = _run_git(repo, "log", "-1", "--pretty=%s", EXPECTED_SLICE18_HEAD)
    _, slice18_name_status = _run_git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r", EXPECTED_SLICE18_HEAD)

    return RepositoryContext(
        head=head,
        parent=parent,
        subject=subject,
        status_lines=tuple(_status_lines(repo)),
        slice18_is_ancestor=slice18_is_ancestor,
        slice18_parent=slice18_parent,
        slice18_subject=slice18_subject,
        slice18_name_status_lines=tuple(line for line in slice18_name_status.splitlines() if line.strip()),
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: aiweb_slice18_gp014_preservation_decision_verify.py /home/nic/forge")
        return 2
    repo = Path(sys.argv[1]).resolve()
    passes: List[str] = []
    failures: List[str] = []

    _check("repository path exists", repo.is_dir(), passes, failures)
    _check("repository has .git directory", (repo / ".git").exists(), passes, failures)

    if repo.is_dir() and (repo / ".git").exists():
        context = _git_repository_context(repo)
        context_label, context_passes, context_failures = classify_repository_context(context)
        passes.append("repository context label: " + context_label)
        passes.extend(context_passes)
        failures.extend(context_failures)
    else:
        context = None

    for rel_path in ALLOWED_NEW_PATHS:
        _check(f"required Slice 18 path exists: {rel_path}", (repo / rel_path).is_file(), passes, failures)

    status_lines = _status_lines(repo) if repo.is_dir() else []
    for line in status_lines:
        rel_path = _status_path(line)
        allowed, _ = _status_paths_are_allowed([line])
        _check(f"status path allowed for current context: {rel_path}", allowed, passes, failures)

    for rel_path, expected_hash in PROTECTED_HASHES.items():
        target = repo / rel_path
        _check(f"protected path exists: {rel_path}", target.is_file(), passes, failures)
        if target.is_file():
            _check(f"protected path hash unchanged: {rel_path}", _sha256_file(target) == expected_hash, passes, failures)
        _check(f"protected path not dirty in git status: {rel_path}", all(_status_path(line) != rel_path for line in status_lines), passes, failures)

    for rel_path in ALLOWED_NEW_PATHS:
        if not rel_path.endswith(".py"):
            continue
        target = repo / rel_path
        if not target.is_file():
            continue
        try:
            compile(target.read_text(encoding="utf-8"), str(target), "exec")
            _check(f"Python syntax valid: {rel_path}", True, passes, failures)
        except SyntaxError:
            _check(f"Python syntax valid: {rel_path}", False, passes, failures)
            continue
        names = _imports(target)
        _check(f"no forbidden imports: {rel_path}", not any(_is_forbidden_import(name) for name in names), passes, failures)

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    try:
        from aiweb_gp014_preservation_decision_scaffold.verify import run_verification

        behavior_passes, behavior_failures = run_verification(repo)
        _check("behavior verifier import and run succeeded", not behavior_failures, passes, failures)
        for item in behavior_passes:
            passes.append("behavior: " + item)
        for item in behavior_failures:
            failures.append("behavior: " + item)
    except Exception as exc:
        failures.append(f"behavior verifier raised: {exc}")

    print("=" * 72)
    print("AIWEB SLICE 18 GP-014 PRESERVATION DECISION VERIFY")
    print("=" * 72)
    print(f"Target repo: {repo}")
    print("PASSES:")
    for item in passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in failures:
        print(f"  FAIL - {item}")
    if failures:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
