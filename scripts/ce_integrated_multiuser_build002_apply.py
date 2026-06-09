#!/usr/bin/env python3
"""Apply CE-INTEGRATED-MULTIUSER-CORE-BUILD-002 structural initialization only."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True)
    parser.add_argument("--identity-vault-root", required=True)
    parser.add_argument("--identity-schema-approval-token", required=True)
    parser.add_argument("--core-store-approval-token", required=True)
    args = parser.parse_args()
    forge_root = Path(args.forge_root).resolve(); identity_root = Path(args.identity_vault_root).resolve()
    sys.path.insert(0, str(forge_root))
    from contribution_economy_v1.identity_vault.multiuser_authority import (
        initialize_multiuser_authority_schema, resolve_authority_receipt,
    )
    from contribution_economy_v1.storage.core_store import initialize_empty_core_store
    from contribution_economy_v1.ledgers import verify_dual_ledger_store
    from contribution_economy_v1.integration.service import IntegratedContributionEconomyCore
    principal_id = "ivp_nic_bogaert_contribution_owner_v1"
    identity = initialize_multiuser_authority_schema(identity_root, approval_token=args.identity_schema_approval_token)
    existing_nic = resolve_authority_receipt(identity_root, principal_id)
    core = initialize_empty_core_store(
        forge_root / "memory" / "contribution_economy_v1" / "core",
        approval_token=args.core_store_approval_token,
    )
    ledgers = verify_dual_ledger_store(forge_root / "memory" / "contribution_economy_v1" / "ledgers")
    integrated = IntegratedContributionEconomyCore(forge_root, identity_root).status()
    receipt = {
        "schema_version": "ce_integrated_multiuser_build002_apply_receipt_v1",
        "build_id": "CE-INTEGRATED-MULTIUSER-CORE-BUILD-002",
        "operation": "initialize_integrated_multiuser_core_without_economic_activity",
        "identity_schema_initialization": identity,
        "existing_nic_bootstrap_resolved_without_duplicate": existing_nic,
        "integrated_core_store_initialization": core,
        "dual_ledgers_preserved": {
            "verified": ledgers["verified"],
            "influence_entry_count": ledgers["influence_entry_count"],
            "investment_entry_count": ledgers["investment_entry_count"],
        },
        "integrated_status_verified": bool(integrated["identity_authority_schema"]["verified"] and integrated["core_store"]["verified"]),
        "new_live_contributor_principals_written": 0,
        "new_live_consent_events_written": 0,
        "live_contribution_events_written": 0,
        "live_capsule_candidates_written": 0,
        "live_validation_records_written": 0,
        "capsules_finalized": 0,
        "ct_minted_milli_ct": 0,
        "influence_ledger_entries_written": 0,
        "investment_ledger_entries_written": 0,
        "writes_mea_state": False,
        "writes_rmc_output_memory": False,
        "writes_chroma": False,
        "public_routes_exposed": False,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
