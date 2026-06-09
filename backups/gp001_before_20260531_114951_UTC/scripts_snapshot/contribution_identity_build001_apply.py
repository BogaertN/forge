#!/usr/bin/env python3
"""Apply CE-IV-LEDGER-CAPSULE-BUILD-001 controlled live foundations.

Controlled writes executed only after explicit approval tokens:
- append-only Nic contributor authority and limited consent records in canonical Identity Vault;
- empty, permanently separated Influence/Investment Ledger storage foundation.

The MEA-to-capsule compatibility object is calculated only in memory and printed in the receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}):
        digest.update(f"{path.relative_to(root).as_posix()}\0{sha256_file(path)}\n".encode("utf-8"))
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply AI.Web Identity Vault + Dual Ledger Foundation Build 001")
    parser.add_argument("--forge-root", type=Path, required=True)
    parser.add_argument("--identity-vault-root", type=Path, required=True)
    parser.add_argument("--identity-approval-token", required=True)
    parser.add_argument("--ledger-approval-token", required=True)
    args = parser.parse_args()
    forge_root = args.forge_root.resolve()
    identity_root = args.identity_vault_root.resolve()
    sys.path.insert(0, str(forge_root))
    from contribution_economy_v1.capsules import build_current_committed_mea_capsule_preview
    from contribution_economy_v1.identity_vault import apply_nic_contributor_authority
    from contribution_economy_v1.ledgers import initialize_dual_ledger_store

    identity_db = identity_root / "data" / "identity_vault.db"
    mea_root = forge_root / "runtime_state" / "mea_problem_manifest_store_v1"
    ledger_root = forge_root / "memory" / "contribution_economy_v1" / "ledgers"
    before_identity_hash = sha256_file(identity_db)
    before_mea_digest = tree_digest(mea_root)
    identity_receipt = apply_nic_contributor_authority(identity_root, approval_token=args.identity_approval_token)
    ledger_receipt = initialize_dual_ledger_store(ledger_root, approval_token=args.ledger_approval_token)
    capsule_preview = build_current_committed_mea_capsule_preview(forge_root=forge_root)
    after_identity_hash = sha256_file(identity_db)
    after_mea_digest = tree_digest(mea_root)
    if before_mea_digest != after_mea_digest:
        raise RuntimeError("PROTECTED BOUNDARY VIOLATION: MEA state changed during Contribution Economy foundation installation")
    receipt = {
        "schema_version": "ce_identity_ledger_capsule_build001_apply_receipt_v1",
        "build_id": "CE-IV-LEDGER-CAPSULE-BUILD-001",
        "operation": "controlled_identity_authority_and_empty_dual_ledger_foundation_apply",
        "intended_identity_vault_database_write_occurred": before_identity_hash != after_identity_hash,
        "identity_vault_database_sha256_before": before_identity_hash,
        "identity_vault_database_sha256_after": after_identity_hash,
        "identity_authority_receipt": identity_receipt,
        "ledger_initialization_receipt": ledger_receipt,
        "capsule_compatibility_preview": capsule_preview,
        "mea_state_tree_sha256_before": before_mea_digest,
        "mea_state_tree_sha256_after": after_mea_digest,
        "mea_state_changed": False,
        "hard_boundaries": {
            "writes_rmc_output_memory": False,
            "writes_mea_state": False,
            "writes_chroma": False,
            "persists_memory_capsule": False,
            "mints_ct": False,
            "writes_influence_ledger_entry": False,
            "writes_investment_ledger_entry": False,
            "authorizes_public_disclosure": False,
            "authorizes_public_output": False,
        },
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
