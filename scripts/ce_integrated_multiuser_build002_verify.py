#!/usr/bin/env python3
"""Read-only installed-state verification for CE-INTEGRATED-MULTIUSER-CORE-BUILD-002."""
from __future__ import annotations
import argparse, sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", required=True)
    parser.add_argument("--identity-vault-root", required=True)
    args = parser.parse_args()
    forge_root = Path(args.forge_root).resolve(); identity_root = Path(args.identity_vault_root).resolve()
    sys.path.insert(0, str(forge_root))
    from contribution_economy_v1.identity_vault.multiuser_authority import resolve_authority_receipt, verify_multiuser_authority_schema
    from contribution_economy_v1.storage.core_store import verify_core_store
    from contribution_economy_v1.ledgers import verify_dual_ledger_store, append_authorized_influence_entry, append_authorized_investment_entry
    from contribution_economy_v1.integration.service import IntegratedContributionEconomyCore
    from contribution_economy_v1.gates import gate_manifest
    passed = failed = 0
    def check(label: str, ok: bool, detail: object = "") -> None:
        nonlocal passed, failed
        if ok:
            passed += 1; print(f"  [PASS] {label}" + (f" - {detail}" if detail != "" else ""))
        else:
            failed += 1; print(f"  [FAIL] {label}" + (f" - {detail}" if detail != "" else ""))
    def raises(label: str, fn) -> None:
        try:
            fn(); check(label, False, "expected rejection did not occur")
        except Exception:
            check(label, True)
    print("CE-INTEGRATED-MULTIUSER-CORE-BUILD-002 INSTALLED-STATE VERIFIER")
    identity = verify_multiuser_authority_schema(identity_root)
    check("multiuser_identity_schema_verified", identity["verified"] is True)
    check("identity_schema_initialization_did_not_create_v2_status_rows", identity["v2_row_counts"].get("contributor_principal_status_events_v2") == 0, identity["v2_row_counts"])
    check("identity_schema_initialization_did_not_create_v2_consent_rows", identity["v2_row_counts"].get("contributor_consent_events_v2") == 0, identity["v2_row_counts"])
    receipt = resolve_authority_receipt(identity_root, "ivp_nic_bogaert_contribution_owner_v1")
    check("build001_nic_principal_preserved_and_resolvable", receipt["authority_active"] is True)
    check("build001_nic_consent_fallback_preserved", receipt["consent_source"] == "build001_consent_event_fallback")
    check("nic_public_disclosure_still_blocked", receipt["consent_scope"]["public_display_authorized"] is False)
    check("nic_ct_minting_still_blocked", receipt["consent_scope"]["ct_minting_authorized"] is False)
    core = verify_core_store(forge_root / "memory" / "contribution_economy_v1" / "core")
    check("integrated_core_store_verified", core["verified"] is True)
    check("integrated_core_all_event_tables_empty", core["all_data_tables_empty"] is True, core["data_table_row_counts"])
    check("integrated_core_mutation_gates_disabled", core["all_live_mutation_gates_disabled"] is True)
    ledger = verify_dual_ledger_store(forge_root / "memory" / "contribution_economy_v1" / "ledgers")
    check("dual_ledger_storage_still_verified", ledger["verified"] is True)
    check("influence_ledger_still_empty", ledger["influence_entry_count"] == 0, ledger["influence_entry_count"])
    check("investment_ledger_still_empty", ledger["investment_entry_count"] == 0, ledger["investment_entry_count"])
    raises("direct_influence_ledger_bypass_now_blocked", lambda: append_authorized_influence_entry(Path("/tmp/none"), {}, {}))
    raises("direct_investment_ledger_bypass_now_blocked", lambda: append_authorized_investment_entry(Path("/tmp/none"), {}, {}))
    gates = gate_manifest()
    check("finalization_disabled", gates["capsule_finalization_enabled"] is False)
    check("minting_disabled", gates["ct_minting_enabled"] is False)
    check("ledger_writes_disabled", gates["influence_ledger_writes_enabled"] is False and gates["investment_ledger_writes_enabled"] is False)
    service = IntegratedContributionEconomyCore(forge_root, identity_root)
    mea = service.mea_compatibility_preview()["capsule_compatibility_preview"]
    check("mea_compatibility_preview_still_not_persisted", mea["persistence_authorized"] is False)
    check("mea_source_artifact_not_contributor_proof", mea["proof_hash"] is None)
    check("mea_hypothesis_remains_hypothesis", mea["claim_status"] == "hypothesis")
    check("no_routes_exposed", gates["live_policy"]["expose_api_routes"] is False)
    check("no_mea_write", gates["live_policy"]["write_mea_state"] is False)
    check("no_rmc_output_memory_write", gates["live_policy"]["write_rmc_output_memory"] is False)
    check("no_chroma_write", gates["live_policy"]["write_chroma"] is False)
    if failed:
        print(f"RESULT: CE-INTEGRATED-MULTIUSER-CORE-BUILD-002_VERIFY FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}")
        return 1
    print(f"RESULT: CE-INTEGRATED-MULTIUSER-CORE-BUILD-002_VERIFY PASS  Total:{passed} Passed:{passed} Failed:0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
