"""Deterministic regression receipt helpers for GP-014 preservation.

These helpers validate preservation boundaries only.
They do not execute GP-014 and do not create language authority.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .baseline import GP014_BASELINE_IDENTITY, PRESERVATION_STATUS

REGRESSION_SCHEMA_VERSION = "aiweb.gp014.regression_receipt.v1"

ALLOWED_SLICE02_PREFIXES = (
    "aiweb_gp014_regression_scaffold/",
    "scripts/test_aiweb_slice02_gp014_regression_scaffold.py",
    "scripts/aiweb_slice02_gp014_regression_verify.py",
    "scripts/README_aiweb_slice02_gp014_regression_scaffold.md",
)

PROTECTED_MARKERS = ("GP-014", "LANG-EXPR-001", "LANG_EXPR", "gp014", "gp-014")
FAILURE_MARKERS = ("GP-015", "GP-015R1", "gp015", "gp-015")


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


def _git_changed_paths(repo_path: Path) -> list[str]:
    output = _run_git(repo_path, ["status", "--short"])
    paths: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        paths.append(line[3:].strip())
    return sorted(paths)


def _is_allowed_slice02_path(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in ALLOWED_SLICE02_PREFIXES)


def _touches_protected_baseline(path: str, baseline_files: list[str]) -> bool:
    if _is_allowed_slice02_path(path):
        return False
    if path in baseline_files:
        return True
    lowered = path.lower()
    return any(marker.lower() in lowered for marker in PROTECTED_MARKERS)


def _touches_failure_path(path: str) -> bool:
    if _is_allowed_slice02_path(path):
        return False
    lowered = path.lower()
    return any(marker.lower() in lowered for marker in FAILURE_MARKERS)


def build_regression_receipt(
    repo_path: str | Path,
    baseline_record: dict[str, Any],
    *,
    changed_files: list[str] | None = None,
    verifier_exit_code: int | None = None,
    behavior_test_exit_code: int | None = None,
    include_timestamp: bool = True,
) -> dict[str, Any]:
    """Build a scoped regression receipt for the current Slice 2 state."""

    root = Path(repo_path).resolve()
    baseline_files = list(baseline_record.get("discovered_marker_files", []))
    changed = sorted(changed_files if changed_files is not None else _git_changed_paths(root))
    gp014_touched = sorted(path for path in changed if _touches_protected_baseline(path, baseline_files))
    gp015_touched = sorted(path for path in changed if _touches_failure_path(path))
    out_of_scope = sorted(path for path in changed if not _is_allowed_slice02_path(path))

    receipt: dict[str, Any] = {
        "schema_version": REGRESSION_SCHEMA_VERSION,
        "record_type": "gp014_regression_preservation_receipt",
        "slice_id": "SLICE-02",
        "baseline_identity": baseline_record.get("baseline_identity", GP014_BASELINE_IDENTITY),
        "baseline_preservation_status": baseline_record.get("preservation_status", PRESERVATION_STATUS),
        "repo_path": str(root),
        "git_head": _run_git(root, ["rev-parse", "HEAD"]),
        "git_branch": _run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        "changed_files": changed,
        "allowed_slice02_paths_only": not out_of_scope,
        "out_of_scope_changed_files": out_of_scope,
        "gp014_baseline_paths_touched": gp014_touched,
        "gp015_failure_paths_touched": gp015_touched,
        "verifier_exit_code": verifier_exit_code,
        "behavior_test_exit_code": behavior_test_exit_code,
        "claims": {
            "gp014_superseded": False,
            "gp014_replaced": False,
            "gp015_repaired": False,
            "gp015r1_installed": False,
            "general_language_authority_created": False,
            "production_readiness_claimed": False,
        },
    }
    if include_timestamp:
        receipt["created_utc"] = _utc_now_iso()
    return receipt


def validate_regression_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Validate that a regression receipt preserves Slice 2 boundaries."""

    passes: list[str] = []
    failures: list[str] = []

    def require(condition: bool, label: str) -> None:
        if condition:
            passes.append(label)
        else:
            failures.append(label)

    require(receipt.get("schema_version") == REGRESSION_SCHEMA_VERSION, "schema_version matches")
    require(receipt.get("slice_id") == "SLICE-02", "slice_id matches")
    require(receipt.get("baseline_identity") == GP014_BASELINE_IDENTITY, "baseline identity preserved")
    require(receipt.get("baseline_preservation_status") == PRESERVATION_STATUS, "baseline preservation status preserved")
    require(receipt.get("allowed_slice02_paths_only") is True, "only Slice 2 paths changed")
    require(not receipt.get("out_of_scope_changed_files"), "no out-of-scope files changed")
    require(not receipt.get("gp014_baseline_paths_touched"), "no GP-014 baseline files touched")
    require(not receipt.get("gp015_failure_paths_touched"), "no GP-015 failure-path files touched")

    claims = receipt.get("claims", {})
    for key in (
        "gp014_superseded",
        "gp014_replaced",
        "gp015_repaired",
        "gp015r1_installed",
        "general_language_authority_created",
        "production_readiness_claimed",
    ):
        require(claims.get(key) is False, f"claim blocked: {key}")

    return {
        "passed": not failures,
        "passes": passes,
        "failures": failures,
    }


def canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def write_regression_receipt(path: str | Path, receipt: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(canonical_json(receipt), encoding="utf-8")
