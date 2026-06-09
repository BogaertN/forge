#!/usr/bin/env python3
"""Behavior tests for Build 002. Mutations occur only in temporary databases."""
from __future__ import annotations
import argparse, hashlib, json, shutil, sqlite3, sys, tempfile
from pathlib import Path


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--forge-root", required=True); parser.add_argument("--identity-vault-root", required=True); args=parser.parse_args()
    forge_root=Path(args.forge_root).resolve(); identity_root=Path(args.identity_vault_root).resolve(); sys.path.insert(0,str(forge_root))
    from contribution_economy_v1.identity_vault.multiuser_authority import (
        INITIALIZE_APPROVAL_TOKEN, REGISTER_APPROVAL_TOKEN, CONSENT_APPROVAL_TOKEN,
        initialize_multiuser_authority_schema, preview_existing_user_registration, register_existing_user_principal,
        resolve_authority_receipt, append_limited_internal_consent_event, append_principal_status_event, STATUS_APPROVAL_TOKEN,
    )
    from contribution_economy_v1.events import compile_contribution_event
    from contribution_economy_v1.capsules.candidate_engine import build_identity_bound_capsule_candidate
    from contribution_economy_v1.validation import validate_capsule_candidate
    from contribution_economy_v1.gates import evaluate_finalization, evaluate_mint, evaluate_influence_write, evaluate_investment_write
    from contribution_economy_v1.storage import CORE_STORE_INITIALIZE_APPROVAL_TOKEN, initialize_empty_core_store, verify_core_store
    from contribution_economy_v1.ledgers import append_authorized_influence_entry, append_authorized_investment_entry
    passed=failed=0
    def check(label, ok, detail=""):
        nonlocal passed,failed
        if ok: passed+=1; print(f"  [PASS] {label}" + (f" - {detail}" if detail else ""))
        else: failed+=1; print(f"  [FAIL] {label}" + (f" - {detail}" if detail else ""))
    def raises(label, fn):
        try: fn(); check(label, False, "expected rejection missing")
        except Exception: check(label, True)
    def sha(text): return hashlib.sha256(text.encode()).hexdigest()
    print("CE-INTEGRATED-MULTIUSER-CORE-BUILD-002 BEHAVIOR TESTS - TEMPORARY MUTATION ONLY")
    with tempfile.TemporaryDirectory(prefix="ce_build002_test_") as td:
        tmp=Path(td); tiv=tmp/"identity-vault"; (tiv/"data").mkdir(parents=True); (tiv/"schema_extensions").mkdir(); (tiv/"service_contracts").mkdir()
        shutil.copy2(identity_root/"data"/"identity_vault.db", tiv/"data"/"identity_vault.db")
        shutil.copy2(identity_root/"schema_extensions"/"contribution_economy_multiuser_authority_v2.sql", tiv/"schema_extensions"/"contribution_economy_multiuser_authority_v2.sql")
        shutil.copy2(identity_root/"service_contracts"/"contribution_economy_integrated_multiuser_core_build002.v1.json", tiv/"service_contracts"/"contribution_economy_integrated_multiuser_core_build002.v1.json")
        raises("wrong_identity_schema_token_blocked", lambda: initialize_multiuser_authority_schema(tiv, approval_token="WRONG"))
        schema=initialize_multiuser_authority_schema(tiv, approval_token=INITIALIZE_APPROVAL_TOKEN)
        check("multiuser_schema_real_initialization", schema["verification"]["verified"] is True)
        conn=sqlite3.connect(tiv/"data"/"identity_vault.db")
        conn.execute("INSERT INTO user_profiles (user_id,canonical_name,is_active,operational_profile_json,profile_schema_version,profile_hash) VALUES (?,?,?,?,?,?)", ("temporary_contributor", "TEMP TEST ONLY", 0, "{}", "test", sha("temporary-profile")))
        conn.commit(); conn.close()
        request={"user_id":"temporary_contributor","principal_type":"human_contributor","effective_at_utc":"2026-05-30T19:10:00Z","consent_scope":{"local_identity_storage_authorized":True,"internal_attribution_reference_authorized":True,"capsule_candidate_reference_authorized":True}}
        preview=preview_existing_user_registration(tiv,request)
        check("generic_registration_preview_for_non_founder", preview["principal_id"] != "ivp_nic_bogaert_contribution_owner_v1" and preview["registration_persisted"] is False)
        raises("economic_consent_grant_blocked", lambda: preview_existing_user_registration(tiv,{**request,"consent_scope":{**request["consent_scope"],"ct_minting_authorized":True}}))
        raises("registration_wrong_token_blocked", lambda: register_existing_user_principal(tiv, request, approval_token="WRONG"))
        enrolled=register_existing_user_principal(tiv, request, approval_token=REGISTER_APPROVAL_TOKEN)
        receipt=enrolled["authority_receipt"]
        check("temporary_principal_registered", receipt["authority_active"] is True)
        check("temporary_private_boundary_enforced", receipt["raw_private_identity_exported"] is False and receipt["consent_scope"]["public_display_authorized"] is False)
        conn=sqlite3.connect(tiv/"data"/"identity_vault.db")
        audit_count=conn.execute("SELECT COUNT(*) FROM contributor_authority_audit_events WHERE principal_id=?", (receipt["principal_id"],)).fetchone()[0]
        conn.close()
        check("registration_appends_authority_audit_event", audit_count == 1, audit_count)
        second=register_existing_user_principal(tiv, request, approval_token=REGISTER_APPROVAL_TOKEN)
        check("duplicate_principal_registration_idempotent", second["outcome"] == "existing_principal_resolved_idempotent_no_write")
        action={"action_id":"temp_action_001","action_type":"runtime_module_build","contribution_type":"BLD","difficulty_class":"standard","influence_type":"direct","timestamp_utc":"2026-05-30T19:11:00Z","action_payload_hash":sha("action-payload")}
        event=compile_contribution_event(receipt, action)
        check("identity_bound_event_compiles", event["event_status"] == "compiled_identity_bound_not_persisted" and event["persistence_authorized"] is False)
        capsule=build_identity_bound_capsule_candidate(event)
        check("capsule_candidate_identity_bound_not_finalized", capsule["finalized"] is False and capsule["proof_hash"] == event["contributor_action_proof_hash"])
        unproven=validate_capsule_candidate(capsule, receipt)
        check("unproven_classification_is_blocked", unproven["validation_status"] == "blocked_classification_evidence_not_verified" and unproven["reward_calculation_preview_not_minted"] is None)
        validation=validate_capsule_candidate(capsule, receipt, classification_evidence_verified=True)
        check("candidate_validation_executes_without_mint", validation["validation_status"] == "integrity_and_classification_validated_not_finalized_not_minted" and validation["mint_authorized"] is False)
        duplicate=validate_capsule_candidate(capsule, receipt, existing_event_hashes=[event["event_hash"]], classification_evidence_verified=True)
        check("duplicate_event_validation_blocked", duplicate["validation_status"] == "blocked_duplicate_contribution_event")
        check("finalization_gate_denies", evaluate_finalization(validation)["allowed"] is False)
        check("mint_gate_denies", evaluate_mint(None)["allowed"] is False)
        check("influence_gate_denies", evaluate_influence_write(None)["allowed"] is False)
        check("investment_gate_denies", evaluate_investment_write(None)["allowed"] is False)
        core_root=tmp/"core"
        initialize_empty_core_store(core_root, approval_token=CORE_STORE_INITIALIZE_APPROVAL_TOKEN)
        core=verify_core_store(core_root)
        check("core_store_real_empty_schema", core["verified"] is True and core["all_data_tables_empty"] is True)
        raises("direct_influence_writer_blocked_even_with_receipt", lambda: append_authorized_influence_entry(tmp/"ledger", {}, {"authorized":True}))
        raises("direct_investment_writer_blocked_even_with_receipt", lambda: append_authorized_investment_entry(tmp/"ledger", {}, {"authorized":True}))
        revoked=append_limited_internal_consent_event(tiv, receipt["principal_id"], {"event_type":"scope_revocation","effective_at_utc":"2026-05-30T19:12:00Z"}, approval_token=CONSENT_APPROVAL_TOKEN)["authority_receipt"]
        check("consent_revocation_resolves_inactive", revoked["consent_active"] is False)
        raises("revoked_consent_cannot_compile_event", lambda: compile_contribution_event(revoked, action))
        suspended=append_principal_status_event(tiv, receipt["principal_id"], event_type="authority_suspension", reason_code="temporary_test_suspension", effective_at_utc="2026-05-30T19:13:00Z", approval_token=STATUS_APPROVAL_TOKEN)["authority_receipt"]
        check("principal_suspension_resolves_inactive", suspended["authority_active"] is False)
        conn=sqlite3.connect(tiv/"data"/"identity_vault.db")
        final_audit_count=conn.execute("SELECT COUNT(*) FROM contributor_authority_audit_events WHERE principal_id=?", (receipt["principal_id"],)).fetchone()[0]
        conn.close()
        check("every_identity_change_appends_audit_event", final_audit_count == 3, final_audit_count)
    if failed:
        print(f"RESULT: CE-INTEGRATED-MULTIUSER-CORE-BUILD-002_BEHAVIOR FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}"); return 1
    print(f"RESULT: CE-INTEGRATED-MULTIUSER-CORE-BUILD-002_BEHAVIOR PASS  Total:{passed} Passed:{passed} Failed:0"); return 0
if __name__ == "__main__": raise SystemExit(main())
