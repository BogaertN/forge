"""Slice 24 source guards.

The runner may use subprocess to execute required local verifier/test commands.
Network/model clients, route/config mutation, memory/delivery/action authority, and
shell-based execution are forbidden in the Slice 24 patch payload.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ast

from .authority import SLICE24_PATCH_FILES, FORBIDDEN_NETWORK_OR_MODEL_FRAGMENTS, ALLOWED_SUBPROCESS_FILES, PROHIBITED_ACCEPTANCE_CLAIMS

@dataclass(frozen=True)
class SourceGuardResult:
    guard_id: str
    passed: bool
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "guard_id": self.guard_id,
            "passed": self.passed,
            "failures": list(self.failures),
        }


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8", errors="replace")


def guard_patch_file_set(root: Path) -> SourceGuardResult:
    failures: list[str] = []
    for rel in SLICE24_PATCH_FILES:
        if not (root / rel).is_file():
            failures.append(f"missing_patch_file:{rel}")
    return SourceGuardResult("slice24_exact_patch_file_set", not failures, tuple(failures))


def guard_no_forbidden_fragments(root: Path) -> SourceGuardResult:
    failures: list[str] = []
    for rel in SLICE24_PATCH_FILES:
        path = root / rel
        if not path.is_file():
            failures.append(f"missing_for_fragment_scan:{rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for fragment in FORBIDDEN_NETWORK_OR_MODEL_FRAGMENTS:
            if fragment in text:
                failures.append(f"forbidden_fragment:{rel}:{fragment}")
    return SourceGuardResult("slice24_no_network_model_or_shell_fragments", not failures, tuple(failures))


def guard_subprocess_allowlist(root: Path) -> SourceGuardResult:
    failures: list[str] = []
    for rel in SLICE24_PATCH_FILES:
        path = root / rel
        if not path.is_file() or not rel.endswith(".py"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as exc:
            failures.append(f"syntax_error:{rel}:{exc}")
            continue
        imports_subprocess = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports_subprocess = imports_subprocess or any(alias.name == "subprocess" for alias in node.names)
            if isinstance(node, ast.ImportFrom):
                imports_subprocess = imports_subprocess or node.module == "subprocess"
        if imports_subprocess and rel not in ALLOWED_SUBPROCESS_FILES:
            failures.append(f"subprocess_import_not_allowlisted:{rel}")
    return SourceGuardResult("slice24_subprocess_import_allowlist", not failures, tuple(failures))


def guard_no_prohibited_broad_claims(root: Path) -> SourceGuardResult:
    failures: list[str] = []
    for rel in SLICE24_PATCH_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for claim in PROHIBITED_ACCEPTANCE_CLAIMS:
            if claim in text and "PROHIBITED_ACCEPTANCE_CLAIMS" not in text:
                failures.append(f"prohibited_broad_claim:{rel}:{claim}")
    return SourceGuardResult("slice24_no_broad_acceptance_claims", not failures, tuple(failures))


def run_source_guards(root: Path) -> list[SourceGuardResult]:
    return [
        guard_patch_file_set(root),
        guard_no_forbidden_fragments(root),
        guard_subprocess_allowlist(root),
        guard_no_prohibited_broad_claims(root),
    ]
