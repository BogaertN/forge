"""Verification helpers for AI.Web Slice 3 status/claim scaffold."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, Tuple

from .claims import ClaimEvidence, ClaimRecord, validate_claim
from .vocabulary import BLOCKED_AUTHORITY_CLAIMS, STATUS_DEFINITIONS, list_status_keys


REQUIRED_RELATIVE_FILES: Tuple[str, ...] = (
    "aiweb_status_claim_scaffold/__init__.py",
    "aiweb_status_claim_scaffold/vocabulary.py",
    "aiweb_status_claim_scaffold/claims.py",
    "aiweb_status_claim_scaffold/verify.py",
    "scripts/test_aiweb_slice03_status_claim_scaffold.py",
    "scripts/aiweb_slice03_status_claim_verify.py",
    "scripts/README_aiweb_slice03_status_claim_scaffold.md",
)

ALLOWED_GIT_STATUS_PREFIXES: Tuple[str, ...] = (
    "?? aiweb_status_claim_scaffold/",
    "?? scripts/README_aiweb_slice03_status_claim_scaffold.md",
    "?? scripts/aiweb_slice03_status_claim_verify.py",
    "?? scripts/test_aiweb_slice03_status_claim_scaffold.py",
    "A  aiweb_status_claim_scaffold/",
    "A  scripts/README_aiweb_slice03_status_claim_scaffold.md",
    "A  scripts/aiweb_slice03_status_claim_verify.py",
    "A  scripts/test_aiweb_slice03_status_claim_scaffold.py",
)

FORBIDDEN_IMPORT_ROOTS: Tuple[str, ...] = (
    "chromadb",
    "openai",
    "langchain",
    "llama_index",
    "faiss",
    "sentence_transformers",
    "transformers",
    "torch",
    "tensorflow",
    "ollama",
    "requests",
    "httpx",
    "urllib",
    "socket",
)


def required_files_present(repo: Path) -> Tuple[str, ...]:
    """Return missing required files."""

    return tuple(rel for rel in REQUIRED_RELATIVE_FILES if not (repo / rel).is_file())


def syntax_error_for_file(path: Path) -> str:
    """Return an empty string when syntax is valid, otherwise a stable error."""

    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return f"{path}: {exc}"
    return ""


def forbidden_imports_in_file(path: Path) -> Tuple[str, ...]:
    """Return forbidden active imports found by AST, not by comments or strings."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".", 1)[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    found.append(node.module)
    return tuple(sorted(set(found)))


def git_status_is_slice03_only(status_lines: Iterable[str]) -> Tuple[str, ...]:
    """Return git status lines outside the Slice 3 additive scope."""

    unexpected = []
    for line in status_lines:
        stripped = line.rstrip()
        if not stripped:
            continue
        if not any(stripped.startswith(prefix) for prefix in ALLOWED_GIT_STATUS_PREFIXES):
            unexpected.append(stripped)
    return tuple(unexpected)


def vocabulary_shape_ok() -> bool:
    """Check that required controlled status keys and blocked claims exist."""

    required_statuses = {
        "planned",
        "designed",
        "authorized_for_installation",
        "installed",
        "tested_passed",
        "tested_failed",
        "verified_within_scope",
        "accepted_within_scope",
        "accepted_with_warnings_within_scope",
        "held",
        "rejected",
        "rolled_back",
        "current_baseline",
        "release_candidate",
        "released",
        "production_ready",
    }
    return required_statuses.issubset(set(list_status_keys())) and bool(BLOCKED_AUTHORITY_CLAIMS)


def sample_claim_checks_ok() -> bool:
    """Run deterministic sample checks used by the verifier."""

    accepted = ClaimRecord(
        claimed_status="accepted_within_scope",
        claim_text="Slice 3 accepted within scope only.",
        scope="Slice 3 status claim scaffold",
        evidence=ClaimEvidence(
            {
                "fresh_source_packet": True,
                "source_inspection": True,
                "patch_design": True,
                "backup": True,
                "installation_record": True,
                "changed_file_manifest": True,
                "tests_recorded": True,
                "tests_passed": True,
                "verifier_recorded": True,
                "verifiers_passed": True,
                "result_packet": True,
                "decision_record": True,
                "public_claim_boundary": True,
            }
        ),
        public_claim=True,
    )
    if not validate_claim(accepted).ok:
        return False

    bad_production = ClaimRecord(
        claimed_status="verified_within_scope",
        claim_text="This is production-ready.",
        scope="Slice 3",
        evidence=ClaimEvidence({"verifier_recorded": True, "verifiers_passed": True}),
        production_claim=True,
    )
    if validate_claim(bad_production).ok:
        return False

    bad_gp014 = ClaimRecord(
        claimed_status="accepted_within_scope",
        claim_text="GP-014 is superseded.",
        scope="Slice 3",
        evidence=accepted.evidence,
        authority_claims={"gp014_supersession_claim": True},
    )
    if validate_claim(bad_gp014).ok:
        return False

    bad_public = ClaimRecord(
        claimed_status="verified_within_scope",
        claim_text="Verified within scope.",
        scope="Slice 3",
        evidence=ClaimEvidence({"verifier_recorded": True, "verifiers_passed": True}),
        public_claim=True,
    )
    if validate_claim(bad_public).ok:
        return False

    return True
