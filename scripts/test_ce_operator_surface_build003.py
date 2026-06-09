#!/usr/bin/env python3
"""CE-OPERATOR-SURFACE-BUILD-003 behavior verification.

Reads the live installed state only.  It does not persist a contribution event,
capsule, validation record, CT mint, ledger row, Identity Vault row, MEA state,
RMC memory, Chroma data, or React source.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

TESTS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    TESTS.append((name, bool(condition), detail))
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True)
    parser.add_argument("--identity-vault-root", required=True)
    parser.add_argument("--ui-root", required=True)
    args = parser.parse_args()

    forge = Path(args.forge_root).resolve()
    identity = Path(args.identity_vault_root).resolve()
    ui = Path(args.ui_root).resolve()

    sys.path.insert(0, str(forge))
    from contribution_economy_v1.operator_surface.read_only_status import (
        BUILD_ID,
        build_mea_capsule_preview_status,
        build_operator_status,
    )

    check("build_id", BUILD_ID == "CE-OPERATOR-SURFACE-BUILD-003")
    status = build_operator_status(forge_root=forge, identity_vault_root=identity)
    preview = build_mea_capsule_preview_status(forge_root=forge)

    check("operator_status_ok", status.get("status") == "OK")
    check("operator_status_read_only", status.get("read_only") is True)
    check("operator_visibility_read_only_routes_enabled", status.get("operator_visibility", {}).get("read_only_routes_enabled") is True)
    check("operator_visibility_mutation_routes_blocked", status.get("operator_visibility", {}).get("contribution_mutation_routes_enabled") is False and status.get("operator_visibility", {}).get("build002_core_mutation_routes_remain_disabled") is True)
    check("read_consistency_is_checkpointed_immutable", status.get("read_consistency", {}).get("model") == "checkpointed_primary_database_immutable_read" and status.get("read_consistency", {}).get("creates_sqlite_sidecars") is False and status.get("read_consistency", {}).get("requires_writer_checkpoint_before_visibility") is True)
    check("multiuser_schema_verified", status.get("identity_authority_schema", {}).get("verified") is True)
    check("registered_principal_present", status.get("identity_authority", {}).get("registered_principal_count", 0) >= 1)
    check("private_identity_not_exported", status.get("identity_authority", {}).get("raw_private_identity_exported") is False)
    check("all_principals_private_only", status.get("identity_authority", {}).get("all_principals_private_only") is True)
    check("no_public_grants_visible", status.get("identity_authority", {}).get("public_display_authorization_event_count") == 0)
    check("no_economic_grants_visible", status.get("identity_authority", {}).get("economic_authorization_event_count") == 0)
    check("core_event_persistence_disabled", status.get("integrated_core", {}).get("live_event_persistence_enabled") is False)
    check("core_finalization_disabled", status.get("integrated_core", {}).get("capsule_finalization_enabled") is False)
    check("core_mint_disabled", status.get("integrated_core", {}).get("ct_minting_enabled") is False)
    check("core_ledger_write_disabled", status.get("integrated_core", {}).get("ledger_write_enabled") is False)
    check("gate_finalization_blocked", status.get("economic_gates", {}).get("capsule_finalization_enabled") is False)
    check("gate_mint_blocked", status.get("economic_gates", {}).get("ct_minting_enabled") is False)
    check("gate_influence_write_blocked", status.get("economic_gates", {}).get("influence_ledger_writes_enabled") is False)
    check("gate_investment_write_blocked", status.get("economic_gates", {}).get("investment_ledger_writes_enabled") is False)
    check("money_never_creates_ct", status.get("ledgers", {}).get("money_creates_ct") is False)
    check("boundary_no_file_write", status.get("boundary", {}).get("writes_files") is False)
    check("boundary_no_identity_write", status.get("boundary", {}).get("writes_identity_vault") is False)
    check("boundary_no_event_write", status.get("boundary", {}).get("writes_contribution_events") is False)
    check("boundary_no_capsule_write", status.get("boundary", {}).get("writes_memory_capsules") is False)
    check("boundary_no_ct", status.get("boundary", {}).get("mints_ct") is False)
    check("boundary_no_ledger_writes", status.get("boundary", {}).get("writes_influence_ledger") is False and status.get("boundary", {}).get("writes_investment_ledger") is False)
    check("boundary_no_rmc_mea_chroma_write", all(status.get("boundary", {}).get(key) is False for key in ("writes_mea_state", "writes_rmc_output_memory", "writes_chroma")))
    check("boundary_no_shell_llm_network", all(status.get("boundary", {}).get(key) is False for key in ("executes_shell", "calls_llm", "performs_network_io")))

    body = preview.get("preview", {})
    check("mea_preview_ok", preview.get("status") == "OK")
    check("mea_preview_read_only", preview.get("read_only") is True)
    check("mea_remains_hypothesis", body.get("claim_status") == "hypothesis")
    check("mea_capsule_unfinalized", body.get("finalized") is False)
    check("mea_contributor_proof_absent", body.get("proof_hash") is None)
    check("mea_contributors_empty", body.get("contributors_count") == 0)
    check("mea_ct_blocked", body.get("ct_minting_status") == "blocked")
    check("mea_no_persistence_or_ledgers", body.get("persistence_authorized") is False and body.get("influence_ledger_write_authorized") is False and body.get("investment_ledger_write_authorized") is False)

    main_text = (forge / "main.py").read_text(encoding="utf-8")
    check("main_get_status_route_present", '"/api/contribution-economy/status"' in main_text)
    check("main_get_preview_route_present", '"/api/contribution-economy/mea-capsule-preview"' in main_text)
    check("main_api_contract_updated", '"version": "1.2.0-CEOperatorSurface-Build003"' in main_text)
    check("main_no_ce_post_route", '_p281_req_path == "/api/contribution-economy/' not in main_text)

    runtime_text = (forge / "contribution_economy_v1" / "operator_surface" / "read_only_status.py").read_text(encoding="utf-8")
    ast.parse(runtime_text)
    forbidden_runtime = ["subprocess", "requests", "httpx", "urllib", "socket", "chromadb", "ollama", "INSERT INTO", "UPDATE ", "DELETE FROM", "CREATE TABLE", "CREATE TRIGGER"]
    hits = [term for term in forbidden_runtime if term in runtime_text]
    check("operator_surface_no_mutating_or_external_pathway", not hits, str(hits))
    check("operator_surface_uses_immutable_sqlite_reads", "mode=ro&immutable=1" in runtime_text and "from ..identity_vault.multiuser_authority import verify_multiuser_authority_schema" not in runtime_text)

    required_ui = [
        ui / "src" / "tabs" / "ContributionEconomyTab.tsx",
        ui / "src" / "App.tsx",
        ui / "src" / "api" / "types.ts",
        ui / "src" / "api" / "forgeClient.ts",
        ui / "src" / "shell" / "TopTabs.tsx",
        ui / "src" / "shell" / "RightAuditRail.tsx",
        ui / "src" / "styles" / "theme.css",
    ]
    check("required_ui_files_present", all(path.is_file() for path in required_ui))
    combined_ui = "\n".join(path.read_text(encoding="utf-8") for path in required_ui if path.is_file())
    check("ui_contribution_tab_wired", "'contribution_economy'" in combined_ui and "ContributionEconomyTab" in combined_ui)
    check("ui_calls_read_only_endpoints", "/api/contribution-economy/status" in combined_ui and "/api/contribution-economy/mea-capsule-preview" in combined_ui)
    ui_forbidden = ["mintCT(", "finalizeCapsule(", "/api/contribution-economy/mint", "/api/contribution-economy/finalize", "method: 'POST'"]
    ui_hits = [term for term in ui_forbidden if term in (ui / "src" / "tabs" / "ContributionEconomyTab.tsx").read_text(encoding="utf-8")]
    check("ui_has_no_contribution_write_control", not ui_hits, str(ui_hits))

    passed = sum(1 for _, ok, _ in TESTS if ok)
    total = len(TESTS)
    result = "PASS" if passed == total else "FAIL"
    print()
    print(f"RESULT: CE-OPERATOR-SURFACE-BUILD-003_BEHAVIOR {result}  Total:{total} Passed:{passed} Failed:{total-passed}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
