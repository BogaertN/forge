#!/usr/bin/env python3
"""Read-only installed-state verifier for CE-IV-LEDGER-CAPSULE-BUILD-001."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
EXPECTED_MEA_STATE_TREE_SHA256 = "5c56daeb4af84f0ac1d8605677cfd21b84a2ab0e3aeb00220d8fd7b6ee0c10f3"
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}):
        digest.update(f"{path.relative_to(root).as_posix()}\0{sha256_file(path)}\n".encode("utf-8"))
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forge-root", type=Path, required=True)
    parser.add_argument("--identity-vault-root", type=Path, required=True)
    args = parser.parse_args()
    forge_root = args.forge_root.resolve()
    identity_root = args.identity_vault_root.resolve()
    sys.path.insert(0, str(forge_root))
    from contribution_economy_v1.capsules import build_current_committed_mea_capsule_preview
    from contribution_economy_v1.identity_vault import verify_nic_contributor_authority
    from contribution_economy_v1.ledgers import verify_dual_ledger_store

    print("CE-IV-LEDGER-CAPSULE-BUILD-001 INSTALLED-STATE VERIFIER")
    print(f"Forge root: {forge_root}")
    print(f"Identity Vault root: {identity_root}")
    try:
        identity = verify_nic_contributor_authority(identity_root)
        check("identity_authority_verified", identity["verified"] is True)
        check("nic_existing_profile_binding_preserved", identity["existing_user_profile_hash"] == "59412c799a127fbf78ea4abdba241b2cbadf5cad36e7adf7c13924f1507d32f0")
        check("nic_existing_profile_remains_inactive", identity["existing_user_profile_is_active"] is False)
        check("nic_principal_record_exactly_one", identity["principal_record_count"] == 1, identity["principal_record_count"])
        check("nic_initial_consent_event_exactly_one", identity["consent_event_count"] == 1, identity["consent_event_count"])
        check("identity_public_disclosure_blocked", identity["public_disclosure_authorized"] is False)
        check("identity_economic_processing_blocked", identity["economic_processing_authorized"] is False)
        check("identity_ct_minting_blocked", identity["ct_minting_authorized"] is False)
        check("identity_investment_processing_blocked", identity["investment_processing_authorized"] is False)
        check("identity_raw_private_export_blocked", identity["raw_private_identity_exported"] is False)
        check("identity_agent_profiles_not_modified_by_build", identity["agent_profiles_modified"] is False)
    except Exception as exc:
        check("identity_authority_verification_exception", False, str(exc))
    try:
        ledger = verify_dual_ledger_store(forge_root / "memory" / "contribution_economy_v1" / "ledgers")
        check("dual_ledger_storage_verified", ledger["verified"] is True)
        check("influence_ledger_initialized_empty", ledger["influence_entry_count"] == 0, ledger["influence_entry_count"])
        check("investment_ledger_initialized_empty", ledger["investment_entry_count"] == 0, ledger["investment_entry_count"])
        check("ledger_three_surface_atomic_equality", ledger["surfaces_atomic_and_equal"] is True)
        check("ledger_append_only_protection", ledger["append_only_protection_verified"] is True)
        check("money_does_not_create_ct", ledger["money_creates_ct"] is False)
        check("no_ct_minting_during_ledger_initialization", ledger["ct_minting_performed_during_initialization"] is False)
        check("no_investment_activity_during_ledger_initialization", ledger["investment_activity_recorded_during_initialization"] is False)
    except Exception as exc:
        check("dual_ledger_storage_verification_exception", False, str(exc))
    try:
        adapter = build_current_committed_mea_capsule_preview(forge_root=forge_root)
        capsule = adapter["capsule_compatibility_preview"]
        check("capsule_preview_only", adapter["preview_only"] is True)
        check("capsule_not_persisted", capsule["persistence_authorized"] is False and capsule["writes_memory_capsule"] is False)
        check("capsule_not_finalized", capsule["finalized"] is False and capsule["finalized_timestamp"] is None)
        check("capsule_preserves_hypothesis_status", capsule["claim_status"] == "hypothesis", capsule["claim_status"])
        check("capsule_contributor_proof_not_faked", capsule["proof_hash"] is None)
        check("capsule_source_artifact_proof_present", len(capsule["source_artifact_proof_hash"]) == 64)
        check("capsule_preview_top_level_hash_present", len(capsule["top_level_hash"]) == 64)
        check("capsule_has_no_contributors_inferred", capsule["contributors"] == [])
        check("capsule_breath_validation_not_executed", capsule["breath_validation"]["status"] == "not_executed")
        check("capsule_ct_mint_blocked", capsule["ct_minting_status"] == "blocked" and capsule["mints_ct"] is False)
        check("capsule_ledger_writes_blocked", capsule["influence_ledger_write_authorized"] is False and capsule["investment_ledger_write_authorized"] is False)
        check("capsule_preview_no_identity_write", capsule["writes_identity_vault"] is False)
    except Exception as exc:
        check("capsule_compatibility_preview_exception", False, str(exc))
    mea_digest = tree_digest(forge_root / "runtime_state" / "mea_problem_manifest_store_v1")
    check("protected_mea_state_unchanged", mea_digest == EXPECTED_MEA_STATE_TREE_SHA256, mea_digest)
    if failed:
        print(f"RESULT: CE-IV-LEDGER-CAPSULE-BUILD-001_VERIFY FAIL  Total:{passed + failed} Passed:{passed} Failed:{failed}")
        return 1
    print(f"RESULT: CE-IV-LEDGER-CAPSULE-BUILD-001_VERIFY PASS  Total:{passed} Passed:{passed} Failed:0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
