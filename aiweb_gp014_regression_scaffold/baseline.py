"""Deterministic GP-014 baseline preservation record builder.

This module records GP-014 / LANG-EXPR-001 as a protected bounded baseline.
It does not import, execute, replace, or supersede GP-014.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASELINE_SCHEMA_VERSION = "aiweb.gp014.baseline_preservation.v1"
GP014_BASELINE_IDENTITY = "LANG-EXPR-001 / GP-014"
PROTECTED_SCOPE = "accepted bounded mathematical-output expression scope only"
PRESERVATION_STATUS = "preserved_not_superseded"

EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    "target",
    "dist",
    "build",
    ".next",
    "coverage",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "memory",
    "logs",
    "runtime",
    "backups",
    "backup",
    "vector_store",
    "chroma",
    ".chroma",
}

TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".sh",
    ".rs",
}

MARKERS = ("GP-014", "LANG-EXPR-001", "LANG_EXPR", "gp014", "gp-014")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_git(repo_path: Path, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_path), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _is_candidate_text_file(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
        return False
    return True


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_gp014_marker_files(repo_path: str | Path, *, max_files: int = 250) -> list[str]:
    """Return relative files containing GP-014/LANG-EXPR marker text.

    This is discovery only. Finding a file does not authorize modifying it.
    """

    root = Path(repo_path).resolve()
    found: list[str] = []
    if not root.exists():
        return found

    for path in sorted(root.rglob("*")):
        if len(found) >= max_files:
            break
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if not _is_candidate_text_file(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(marker in text for marker in MARKERS):
            found.append(rel.as_posix())
    return found


def build_gp014_file_manifest(repo_path: str | Path, marker_files: list[str]) -> list[dict[str, str]]:
    root = Path(repo_path).resolve()
    manifest: list[dict[str, str]] = []
    for rel in sorted(set(marker_files)):
        path = root / rel
        if path.is_file():
            manifest.append({"path": rel, "sha256": _sha256_file(path)})
    return manifest


def build_gp014_baseline_record(
    repo_path: str | Path,
    *,
    include_timestamp: bool = True,
    discovered_files: list[str] | None = None,
) -> dict[str, Any]:
    """Build a baseline preservation record for GP-014.

    The record asserts preservation, not replacement or supersession.
    """

    root = Path(repo_path).resolve()
    marker_files = discovered_files if discovered_files is not None else find_gp014_marker_files(root)
    record: dict[str, Any] = {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "record_type": "gp014_baseline_preservation_record",
        "baseline_identity": GP014_BASELINE_IDENTITY,
        "protected_scope": PROTECTED_SCOPE,
        "preservation_status": PRESERVATION_STATUS,
        "repo_path": str(root),
        "git_head": _run_git(root, ["rev-parse", "HEAD"]),
        "git_branch": _run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        "git_status_short": _run_git(root, ["status", "--short"]),
        "discovered_marker_files": sorted(marker_files),
        "baseline_file_manifest": build_gp014_file_manifest(root, marker_files),
        "explicit_non_claims": {
            "gp014_superseded": False,
            "gp014_replaced": False,
            "gp015_repaired": False,
            "gp015r1_installed": False,
            "general_language_authority_created": False,
            "production_readiness_claimed": False,
        },
        "blocked_authorities_preserved": [
            "general_language_interpretation",
            "concept_resolution",
            "predicate_role_resolution",
            "outward_expression_authority",
            "ui_authority",
            "memory_authority",
            "evidence_authority",
            "corpus_authority",
            "external_resource_authority",
            "delivery_authority",
            "action_routing_authority",
            "llm_model_vector_embedding_authority",
        ],
    }
    if include_timestamp:
        record["created_utc"] = _utc_now_iso()
    return record


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def write_baseline_record(path: str | Path, record: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(canonical_json(record), encoding="utf-8")
