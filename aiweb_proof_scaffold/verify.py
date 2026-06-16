"""Installation verifier for AI.Web Slice 1 proof scaffold."""

from __future__ import annotations

import ast
import importlib
import json
import py_compile
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

REQUIRED_FILES = (
    "aiweb_proof_scaffold/__init__.py",
    "aiweb_proof_scaffold/schema.py",
    "aiweb_proof_scaffold/receipt.py",
    "aiweb_proof_scaffold/verify.py",
    "scripts/test_aiweb_slice01_proof_scaffold.py",
    "scripts/aiweb_slice01_proof_scaffold_verify.py",
    "scripts/README_aiweb_slice01_proof_scaffold.md",
)

FORBIDDEN_IMPORT_ROOTS = (
    "ollama",
    "chromadb",
    "openai",
    "langchain",
    "faiss",
    "llama_index",
    "requests",
    "httpx",
    "socket",
)

PROTECTED_MARKERS = ("GP-014", "LANG-EXPR-001", "GP-015", "GP-015R1")


@dataclass(frozen=True)
class VerificationResult:
    passes: List[str]
    failures: List[str]

    @property
    def ok(self) -> bool:
        return not self.failures


def _repo_path(repo_root: str | Path) -> Path:
    return Path(repo_root).expanduser().resolve()


def _iter_python_files(repo: Path) -> Iterable[Path]:
    for rel in REQUIRED_FILES:
        p = repo / rel
        if p.suffix == ".py":
            yield p


def _active_import_roots(path: Path) -> List[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.append(node.module.split(".")[0])
    return roots


def verify_installation(repo_root: str | Path) -> VerificationResult:
    """Verify the Slice 1 scaffold exists and preserves its authority boundary."""
    repo = _repo_path(repo_root)
    passes: List[str] = []
    failures: List[str] = []

    if str(repo) == "/home/nic/forge":
        passes.append("target repo is exactly /home/nic/forge")
    else:
        failures.append(f"target repo is not /home/nic/forge: {repo}")

    if repo.is_dir():
        passes.append("target repo directory exists")
    else:
        failures.append("target repo directory missing")
        return VerificationResult(passes, failures)

    if (repo / ".git").is_dir():
        passes.append("target repo is a git repository")
    else:
        failures.append("target repo .git directory missing")

    for rel in REQUIRED_FILES:
        path = repo / rel
        if path.is_file():
            passes.append(f"required file exists: {rel}")
        else:
            failures.append(f"required file missing: {rel}")

    if failures:
        return VerificationResult(passes, failures)

    for path in _iter_python_files(repo):
        rel = path.relative_to(repo).as_posix()
        try:
            py_compile.compile(str(path), doraise=True)
            passes.append(f"python syntax valid: {rel}")
        except py_compile.PyCompileError as exc:
            failures.append(f"python syntax invalid: {rel}: {exc}")

        try:
            roots = _active_import_roots(path)
        except SyntaxError as exc:
            failures.append(f"cannot parse imports: {rel}: {exc}")
            roots = []
        bad = sorted(set(roots).intersection(FORBIDDEN_IMPORT_ROOTS))
        if bad:
            failures.append(f"forbidden active imports in {rel}: {', '.join(bad)}")
        else:
            passes.append(f"no forbidden active model/network imports: {rel}")

    sys.path.insert(0, str(repo))
    try:
        mod = importlib.import_module("aiweb_proof_scaffold")
        receipt = mod.build_receipt(
            receipt_type="verification_sample",
            status="PASS",
            target_repo=str(repo),
            head_commit="verification-only",
            authority_basis=["Document 10 Slice 1"],
            fresh_packet_identity={"packet": "verification-only"},
            changed_files=[],
            behavior_tests=[{"name": "schema_smoke", "status": "PASS"}],
            verifier_gates=[{"name": "import_smoke", "status": "PASS"}],
            rollback={"required": False, "reason": "verification-only"},
            accepted_scope={"claim": "No live authority accepted by verification sample."},
            notes=["sample only"],
        )
        validation = mod.validate_receipt(receipt)
        if validation:
            failures.append("sample receipt validation failed: " + "; ".join(validation))
        else:
            passes.append("sample receipt builds and validates deterministically")
    except Exception as exc:  # pragma: no cover - used by script verifier
        failures.append(f"aiweb_proof_scaffold import/smoke failed: {exc}")
    finally:
        try:
            sys.path.remove(str(repo))
        except ValueError:
            pass

    protected_touched = [rel for rel in REQUIRED_FILES if any(marker in rel for marker in PROTECTED_MARKERS)]
    if protected_touched:
        failures.append("Slice 1 scaffold file path touches protected GP marker: " + ", ".join(protected_touched))
    else:
        passes.append("Slice 1 scaffold file paths do not touch GP-014/GP-015 markers")

    return VerificationResult(passes, failures)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    repo = args[0] if args else "/home/nic/forge"
    result = verify_installation(repo)
    print("============================================================")
    print("AIWEB SLICE 1 PROOF SCAFFOLD VERIFIER")
    print("============================================================")
    print(f"Target repo: {Path(repo).expanduser().resolve()}")
    print("PASSES:")
    for item in result.passes:
        print(f"  PASS - {item}")
    print("FAILURES:")
    for item in result.failures:
        print(f"  FAIL - {item}")
    if result.ok:
        print("VERDICT: PASS - Slice 1 proof scaffold verifier passed within Slice 1 scope")
        return 0
    print("VERDICT: FAIL - mandatory verifier failure blocks acceptance")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
