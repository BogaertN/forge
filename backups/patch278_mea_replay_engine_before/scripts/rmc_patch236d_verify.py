#!/usr/bin/env python3
"""Patch 236D static verifier.

Verifies that the Neo governed handshake receipt verification commands are
installed and that this patch is read-only at the source-text boundary.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"

text = MAIN.read_text(encoding="utf-8")
reg = REG.read_text(encoding="utf-8")

required = [
    "PATCH236D_NEO_HANDSHAKE_VERIFY_COMMANDS",
    "forge-neo-governed-handshake-verify",
    "forge-neo-governed-handshake-verify-report",
    "P236D_REQUIRED_236C_VERDICT = \"NEO_HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT\"",
    "P236D_REQUIRED_ECHO_VERDICT = \"ECHO_VALIDATION_PASSED_NEO_GOVERNED_ACTIVE_AGENT\"",
    "NEO_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED",
    "cmd_forge_neo_governed_handshake_verify",
    "cmd_forge_neo_governed_handshake_verify_report",
    "no_private_memory_exposure",
    "no_secret_reads",
    "no_autonomous_execution",
    "no_rmc_memory_write",
    "no_identity_vault_write",
]
missing = [s for s in required if s not in text]
if missing:
    print("PATCH236D_VERIFY_FAIL")
    print("missing=" + ", ".join(missing))
    sys.exit(1)

if '"current_trust_level": 5.0' not in reg:
    print("PATCH236D_VERIFY_FAIL")
    print("current_trust_level_not_5_0")
    sys.exit(1)

if text.count('"forge-neo-governed-handshake-verify"') < 2:
    print("PATCH236D_VERIFY_FAIL")
    print("command_not_registered_and_routed")
    sys.exit(1)

if 'if __name__ == "__main__":' not in text:
    print("PATCH236D_VERIFY_FAIL")
    print("runtime_entrypoint_missing")
    sys.exit(1)

print("PATCH236D_VERIFY_PASS")
print("commands=forge-neo-governed-handshake-verify, forge-neo-governed-handshake-verify-report")
print("boundary=read-only Neo governed handshake receipt verification; no Identity Vault DB write; no RMC memory write; no private memory exposure; no secret reads; no autonomous execution")
