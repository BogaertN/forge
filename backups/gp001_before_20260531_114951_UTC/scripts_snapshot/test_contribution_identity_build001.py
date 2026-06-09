#!/usr/bin/env python3
"""Behavior tests for Build 001. All mutation testing occurs in temporary copies only."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

sys.dont_write_bytecode = True
passed = 0
failed = 0


def check(name: str, condition: bool, detail: Any | None = None) -> None:
    global passed, failed
    if condition:
        passed += 1
        suffix = f" - {detail}" if detail is not None else ""
        print(f"  [PASS] {name}{suffix}")
    else:
        failed += 1
        suffix = f" - observed={detail!r}" if detail is not None else ""
        print(f"  [FAIL] {name}{suffix}")


def raises(name: str, function: Callable[[], object]) -> None:
    try:
        function()
    except Exception:
        check(name, True)
    else:
        check(name, False, "exception not raised")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", type=Path, required=True)
    parser.add_argument("--identity-vault-root", type=Path, required=True)
    args = parser.parse_args()
    forge_root = args.forge_root.resolve()
    identity_root = args.identity_vault_root.resolve()
    sys.path.insert(0, str(forge_root))
    from contribution_economy_v1.capsules import build_mea_capsule_compatibility_preview
    from contribution_economy_v1.identity_vault import APPLY_APPROVAL_TOKEN, apply_nic_contributor_authority, verify_nic_contributor_authority
    from contribution_economy_v1.ledgers import (
        LEDGER_INITIALIZE_APPROVAL_TOKEN,
        append_authorized_influence_entry,
        append_authorized_investment_entry,
        initialize_dual_ledger_store,
        verify_dual_ledger_store,
    )

    print("CE-IV-LEDGER-CAPSULE-BUILD-001 BEHAVIOR TESTS - TEMPORARY MUTATION ONLY")
    with tempfile.TemporaryDirectory(prefix="ce_build001_test_") as temporary:
        test_root = Path(temporary)
        test_identity = test_root / "identity-vault"
        shutil.copytree(identity_root, test_identity)
        database = test_identity / "data" / "identity_vault.db"
        # Return the temporary database to its pre-build schema so the apply path itself is tested.
        conn = sqlite3.connect(database)
        try:
            for trigger in (
                "block_update_contributor_principals", "block_delete_contributor_principals",
                "block_update_contributor_consent_events", "block_delete_contributor_consent_events",
                "block_update_contributor_authority_audit_events", "block_delete_contributor_authority_audit_events",
            ):
                conn.execute(f"DROP TRIGGER IF EXISTS {trigger}")
            conn.execute("DROP TABLE IF EXISTS contributor_authority_audit_events")
            conn.execute("DROP TABLE IF EXISTS contributor_consent_events")
            conn.execute("DROP TABLE IF EXISTS contributor_principals")
            conn.commit()
        finally:
            conn.close()
        contract_path = test_identity / "service_contracts" / "contribution_economy_contributor_authority_contract.v1.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["canonical_database_path"] = str(database.resolve())
        contract["schema_extension_path"] = str((test_identity / "schema_extensions" / "contribution_economy_identity_authority_v1.sql").resolve())
        contract["authority_manifest_path"] = str((test_identity / "contributor_authority" / "nic_bogaert_contributor_authority_manifest.v1.json").resolve())
        contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raises("identity_wrong_approval_token_blocked", lambda: apply_nic_contributor_authority(test_identity, approval_token="WRONG"))
        first = apply_nic_contributor_authority(test_identity, approval_token=APPLY_APPROVAL_TOKEN)
        check("identity_principal_inserted", first["outcomes"]["principal"] == "inserted")
        check("identity_consent_inserted", first["outcomes"]["consent"] == "inserted")
        check("identity_audit_inserted", first["outcomes"]["audit"] == "inserted")
        verified = verify_nic_contributor_authority(test_identity)
        check("identity_verification_passed", verified["verified"] is True)
        check("identity_nic_profile_remains_inactive", verified["existing_user_profile_is_active"] is False)
        check("identity_internal_reference_allowed", verified["consent_scope"]["internal_attribution_reference_authorized"] is True)
        check("identity_capsule_candidate_reference_allowed", verified["consent_scope"]["capsule_candidate_reference_authorized"] is True)
        check("identity_public_display_blocked", verified["consent_scope"]["public_display_authorized"] is False)
        check("identity_economic_processing_blocked", verified["consent_scope"]["economic_processing_authorized"] is False)
        check("identity_ct_minting_blocked", verified["consent_scope"]["ct_minting_authorized"] is False)
        second = apply_nic_contributor_authority(test_identity, approval_token=APPLY_APPROVAL_TOKEN)
        check("identity_second_apply_idempotent", all(value == "existing_verified_idempotent_no_write" for value in second["outcomes"].values()))
        conn = sqlite3.connect(database)
        try:
            raises(
                "identity_append_only_update_trigger_blocks_mutation",
                lambda: conn.execute("UPDATE contributor_principals SET authority_status='revoked_by_append_only_event' WHERE principal_id='ivp_nic_bogaert_contribution_owner_v1'").fetchall(),
            )
        finally:
            conn.rollback()
            conn.close()

        ledger_root = test_root / "forge" / "memory" / "contribution_economy_v1" / "ledgers"
        raises("ledger_wrong_initialization_token_blocked", lambda: initialize_dual_ledger_store(ledger_root, approval_token="WRONG"))
        initialized = initialize_dual_ledger_store(ledger_root, approval_token=LEDGER_INITIALIZE_APPROVAL_TOKEN)
        check("ledger_real_empty_store_initialized", initialized["verification"]["verified"] is True)
        check("ledger_empty_influence_after_initialize", initialized["verification"]["influence_entry_count"] == 0)
        check("ledger_empty_investment_after_initialize", initialized["verification"]["investment_entry_count"] == 0)
        second_init = initialize_dual_ledger_store(ledger_root, approval_token=LEDGER_INITIALIZE_APPROVAL_TOKEN)
        check("ledger_second_initialize_idempotent", second_init["metadata_outcome"] == "existing_empty_store_metadata_verified_idempotent_no_write")
        influence_authorization = {
            "schema_version": "finalized_validated_capsule_ct_mint_authorization_receipt_v1",
            "authorization_type": "finalized_validated_capsule_ct_mint_authorization_receipt",
            "authorized": True,
            "capsule_id": "capsule_temp_validated_001",
        }
        influence_entry = {
            "entry_id": "infl_temp_001",
            "principal_id": "ivp_nic_bogaert_contribution_owner_v1",
            "capsule_id": "capsule_temp_validated_001",
            "capsule_top_level_hash": sha("capsule"),
            "mint_event_id": "mint_temp_001",
            "mint_event_hash": sha("mint"),
            "ct_minted_milli_ct": 1000,
            "contribution_type": "CRT",
            "influence_type": "direct",
            "difficulty": "light",
            "contributor_action_proof_hash": sha("action"),
            "validator_id": "test.validator",
            "timestamp_utc": "2026-05-30T18:01:00Z",
            "capsule_finalized": True,
            "breath_validation_status": "validated",
            "ct_minting_status": "minted",
        }
        raises("ledger_influence_missing_mint_authorization_blocked", lambda: append_authorized_influence_entry(ledger_root, influence_entry, {"schema_version": "bad"}))
        influence_receipt = append_authorized_influence_entry(ledger_root, influence_entry, influence_authorization)
        check("ledger_influence_future_authorized_append_atomic", len(influence_receipt["surfaces_written"]) == 3)
        after_influence = verify_dual_ledger_store(ledger_root)
        check("ledger_influence_three_surface_equal", after_influence["influence_entry_count"] == 1 and after_influence["surfaces_atomic_and_equal"] is True)
        check("ledger_investment_still_empty_after_influence", after_influence["investment_entry_count"] == 0)
        investment_authorization = {
            "schema_version": "legal_reviewed_investment_ledger_write_receipt_v1",
            "authorization_type": "legal_reviewed_investment_ledger_write_receipt",
            "authorized": True,
            "legal_review_completed": True,
        }
        investment_entry = {
            "entry_id": "invest_temp_001",
            "principal_id": "ivp_nic_bogaert_contribution_owner_v1",
            "investment_event_id": "investment_temp_001",
            "amount_minor_units": 10000,
            "currency_code": "USD",
            "verification_receipt_hash": sha("investment"),
            "timestamp_utc": "2026-05-30T18:02:00Z",
            "creates_ct": True,
        }
        raises("ledger_investment_cannot_create_ct", lambda: append_authorized_investment_entry(ledger_root, investment_entry, investment_authorization))
        investment_entry["creates_ct"] = False
        investment_receipt = append_authorized_investment_entry(ledger_root, investment_entry, investment_authorization)
        check("ledger_investment_future_authorized_append_atomic", len(investment_receipt["surfaces_written"]) == 3)
        after_investment = verify_dual_ledger_store(ledger_root)
        check("ledger_investment_three_surface_equal", after_investment["investment_entry_count"] == 1 and after_investment["surfaces_atomic_and_equal"] is True)
        check("ledger_money_still_never_creates_ct", after_investment["money_creates_ct"] is False)

        evidence = {
            "candidate_id": "cg_hypothesis_001",
            "candidate_hash": "a27ce2e352839119f79f0742d63cdcd964c49321e3206ce24b89f333c8b90901",
            "claim_status": "hypothesis",
            "proof_debt": "0.85",
            "source_manifest_hash": "787485dbbde35501f182b28470e7fccdfdb600ea06eedce92aea82d5502d039e",
            "source_state_content_hash": "e6ac06360a18fd67512f3f6b3004ddd751630ec83651a654a82811551cf08198",
            "committed_manifest_hash": "852feb2c1491683bca39d89ee3d86e43e4f8fe9aecad2c403c9be70018c95a83",
            "committed_state_content_hash": "a10f4d719dd1d7041f0b16f2c474c5a7bcbee972ed9411b7eaa48e3219c9dc0d",
            "transaction_id": "advance_9ff10b208c0adc06dedff97a",
            "transaction_intent_hash": "9ff10b208c0adc06dedff97a59415962f9786c20bc8d7bd18c877fd58a876691",
            "transaction_seal_packet_hash": "498c9de340cb6df63d1f01b338a0097b45fe946be0b939b8641523e545746bbf",
            "transaction_audit_chain_hash": "15fafc454b13033acb5e9b86b7e7fc183f39819180dada56146f1fa88c86bd96",
            "advance_receipt_hash": "1066fac6e124cb1300a50f39aaaf42c987f310184902dee303615d897e843e52",
            "rollback_record_hash": "762553891bdd58f1f4404a6beedef052051ade2e98010c43497fa5c5739e4eb5",
            "memory_record_id": "mea_mem_preview_4cc7f39eb2c2110c282ab1ef",
            "memory_record_hash": "4cc7f39eb2c2110c282ab1ef43183826c7ea6d27b7f68b78164d708cfaa92115",
            "memory_tier": "hypothesis_test_required_record",
            "replay_verified": True,
            "all_replay_checks_passed": True,
            "source_state_integrity_verified": True,
        }
        capsule_one = build_mea_capsule_compatibility_preview(evidence)
        capsule_two = build_mea_capsule_compatibility_preview(evidence)
        check("capsule_preview_deterministic", capsule_one == capsule_two)
        check("capsule_preview_not_finalized", capsule_one["finalized"] is False)
        check("capsule_preview_preserves_hypothesis", capsule_one["claim_status"] == "hypothesis")
        check("capsule_preview_does_not_fake_contributor_proof", capsule_one["proof_hash"] is None)
        check("capsule_preview_has_source_artifact_proof", len(capsule_one["source_artifact_proof_hash"]) == 64)
        check("capsule_preview_has_top_level_hash", len(capsule_one["top_level_hash"]) == 64)
        check("capsule_preview_does_not_persist", capsule_one["persistence_authorized"] is False and capsule_one["writes_memory_capsule"] is False)
        check("capsule_preview_does_not_mint_or_write_ledger", capsule_one["mints_ct"] is False and capsule_one["writes_ledgers"] is False)
        bad_evidence = dict(evidence)
        bad_evidence["replay_verified"] = False
        raises("capsule_preview_requires_replay_verified_mea", lambda: build_mea_capsule_compatibility_preview(bad_evidence))

    if failed:
        print(f"RESULT: CE-IV-LEDGER-CAPSULE-BUILD-001_BEHAVIOR FAIL  Total:{passed + failed} Passed:{passed} Failed:{failed}")
        return 1
    print(f"RESULT: CE-IV-LEDGER-CAPSULE-BUILD-001_BEHAVIOR PASS  Total:{passed} Passed:{passed} Failed:0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
