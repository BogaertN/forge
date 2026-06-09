#!/usr/bin/env python3
"""CE-OPERATOR-SURFACE-BUILD-003 installed-state verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}):
        digest.update(f"{path.relative_to(root).as_posix()}\0{hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode("utf-8"))
    return digest.hexdigest()


def count_rows(database: Path, tables: tuple[str, ...]) -> dict[str, int]:
    connection = sqlite3.connect(f"file:{database.resolve()}?mode=ro&immutable=1", uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        return {table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]) for table in tables}
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True)
    parser.add_argument("--identity-vault-root", required=True)
    parser.add_argument("--ui-root", required=True)
    args = parser.parse_args()
    forge = Path(args.forge_root).resolve()
    identity = Path(args.identity_vault_root).resolve()
    ui = Path(args.ui_root).resolve()

    expected_files = [
        forge / "contribution_economy_v1" / "operator_surface" / "__init__.py",
        forge / "contribution_economy_v1" / "operator_surface" / "read_only_status.py",
        forge / "scripts" / "test_ce_operator_surface_build003.py",
        forge / "scripts" / "ce_operator_surface_build003_verify.py",
        forge / "scripts" / "README_ce_operator_surface_build003.md",
        ui / "src" / "tabs" / "ContributionEconomyTab.tsx",
    ]
    check("build003_required_files_installed", all(path.is_file() for path in expected_files))

    sys.path.insert(0, str(forge))
    from contribution_economy_v1.operator_surface.read_only_status import build_operator_status, build_mea_capsule_preview_status
    status = build_operator_status(forge_root=forge, identity_vault_root=identity)
    preview = build_mea_capsule_preview_status(forge_root=forge)
    check("status_endpoint_payload_healthy", status.get("status") == "OK")
    check("status_boundary_read_only", status.get("boundary", {}).get("read_only") is True)
    check("operator_visibility_read_only_only", status.get("operator_visibility", {}).get("read_only_routes_enabled") is True and status.get("operator_visibility", {}).get("contribution_mutation_routes_enabled") is False and status.get("operator_visibility", {}).get("build002_core_mutation_routes_remain_disabled") is True)
    check("read_consistency_no_sqlite_sidecars", status.get("read_consistency", {}).get("model") == "checkpointed_primary_database_immutable_read" and status.get("read_consistency", {}).get("creates_sqlite_sidecars") is False)
    check("status_boundary_zero_mutation", all(status.get("boundary", {}).get(key) is False for key in (
        "writes_files", "writes_identity_vault", "writes_contribution_events", "writes_memory_capsules",
        "finalizes_capsules", "mints_ct", "writes_influence_ledger", "writes_investment_ledger",
        "writes_mea_state", "writes_rmc_output_memory", "writes_chroma", "calls_llm", "executes_shell",
        "performs_network_io",
    )))
    check("preview_maintains_hypothesis_boundary", preview.get("preview", {}).get("claim_status") == "hypothesis" and preview.get("preview", {}).get("proof_hash") is None and preview.get("preview", {}).get("finalized") is False)

    core_counts = count_rows(
        forge / "memory" / "contribution_economy_v1" / "core" / "contribution_economy_core.db",
        ("contribution_events", "memory_capsule_candidates", "capsule_validation_records", "capsule_finalization_receipts", "ct_mint_events", "nullification_correction_events"),
    )
    check("core_governed_tables_still_empty", sum(core_counts.values()) == 0, json.dumps(core_counts, sort_keys=True))

    ledger_counts = count_rows(
        forge / "memory" / "contribution_economy_v1" / "ledgers" / "contribution_ledgers.db",
        ("influence_live_entries", "influence_user_entries", "influence_archive_entries", "investment_live_entries", "investment_user_entries", "investment_archive_entries"),
    )
    check("dual_ledgers_still_empty", sum(ledger_counts.values()) == 0, json.dumps(ledger_counts, sort_keys=True))

    dist_index = ui / "dist" / "index.html"
    check("react_dist_built", dist_index.is_file())
    dist_text = ""
    if dist_index.is_file():
        dist_text = dist_index.read_text(encoding="utf-8", errors="replace")
        assets = list((ui / "dist" / "assets").glob("*.js")) if (ui / "dist" / "assets").exists() else []
        dist_bundle_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in assets)
        check("react_dist_contains_contribution_surface", "Contribution Economy" in dist_bundle_text)
    else:
        check("react_dist_contains_contribution_surface", False, "dist/index.html missing")

    total = len(CHECKS)
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    result = "PASS" if total == passed else "FAIL"
    print()
    print(f"RESULT: CE-OPERATOR-SURFACE-BUILD-003_VERIFY {result}  Total:{total} Passed:{passed} Failed:{total-passed}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
