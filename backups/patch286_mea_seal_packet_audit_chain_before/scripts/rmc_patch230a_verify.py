#!/usr/bin/env python3
"""Patch 230A static verifier — bootstrap handshake receipt verification."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
registry = root / "config" / "tool_registry.json"
main_text = main.read_text(encoding="utf-8")
reg = json.loads(registry.read_text(encoding="utf-8"))
required = [
    "forge-bootstrap-handshake-verify",
    "forge-bootstrap-handshake-verify-report",
    "cmd_forge_bootstrap_handshake_verify",
    "cmd_forge_bootstrap_handshake_verify_report",
    "aiweb_patch230a_bootstrap_handshake_receipt_verify_v1",
    "VERIFIED_HANDSHAKE_DRY_RUN_RECEIPT_INACTIVE_GATE",
    "HANDSHAKE_DRY_RUN_PROFILE_FOUND_BUT_INACTIVE",
    "identity_vault_database_written",
    "rmc_memory_written",
    "agent_identity_activation_performed",
    "new_rmc_directories_created",
]
missing = [item for item in required if item not in main_text]
for key in ["forge_bootstrap_handshake_verify", "forge_bootstrap_handshake_verify_report"]:
    if key not in (reg.get("tools") or {}):
        missing.append(f"registry:{key}")
if missing:
    print("PATCH230A_VERIFY_FAIL")
    for item in missing:
        print(f"missing={item}")
    raise SystemExit(1)
print("PATCH230A_VERIFY_PASS")
print("commands=forge-bootstrap-handshake-verify, forge-bootstrap-handshake-verify-report")
print("boundary=verification-only report; no RMC memory write; no Identity Vault DB write; no activation")
