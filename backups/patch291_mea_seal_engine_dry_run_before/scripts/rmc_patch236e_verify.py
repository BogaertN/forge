#!/usr/bin/env python3
"""Patch 236E static verifier.

Verifies that the controlled Neo RMC test_receipt write commands are installed
and that the patch is constrained to receipt-only behavior.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"

text = MAIN.read_text(encoding="utf-8")
reg = REG.read_text(encoding="utf-8")

required = [
    "PATCH236E_RMC_NEO_TEST_RECEIPT_COMMANDS",
    "forge-rmc-neo-test-receipt-write",
    "forge-rmc-neo-test-receipt-write-report",
    "P236E_TARGET_AGENT = \"neo.local\"",
    "P236E_EXPECTED_236D_VERDICT = \"NEO_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED\"",
    "P236E_EXPECTED_236C_VERDICT = \"NEO_HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT\"",
    "P236E_EXPECTED_ECHO_VERDICT = \"ECHO_VALIDATION_PASSED_NEO_GOVERNED_ACTIVE_AGENT\"",
    "P236E_WRITE_TYPE = \"test_receipt\"",
    "P236E_FORBIDDEN_WRITE_TYPES",
    "RMC_TEST_RECEIPT_WRITTEN_GOVERNED_NEO",
    "cmd_forge_rmc_neo_test_receipt_write",
    "cmd_forge_rmc_neo_test_receipt_write_report",
    '"role_boundary": "public_frontline_receipt_only"',
    '"private_memory_payloads_read": False',
    '"agent_memory_written": False',
    '"long_term_memory_written": False',
    '"private_memory_written": False',
    '"shared_memory_written": False',
    '"full_chat_content_written": False',
    '"secret_values_read": False',
    '"autonomous_tool_execution_performed": False',
    '"protoforge2_execution_performed": False',
    '"echoforge_creation_performed": False',
    "_p230_latest_scaffold_root",
]
missing = [s for s in required if s not in text]
if missing:
    print("PATCH236E_VERIFY_FAIL")
    print("missing=" + ", ".join(missing))
    sys.exit(1)

if '"current_trust_level": 5.0' not in reg:
    print("PATCH236E_VERIFY_FAIL")
    print("current_trust_level_not_5_0")
    sys.exit(1)

if text.count('"forge-rmc-neo-test-receipt-write"') < 2:
    print("PATCH236E_VERIFY_FAIL")
    print("command_not_registered_and_routed")
    sys.exit(1)

if "_p229_resolve_rmc_root" in text:
    print("PATCH236E_VERIFY_FAIL")
    print("stale_p229_resolver_present")
    sys.exit(1)

if 'if __name__ == "__main__":' not in text:
    print("PATCH236E_VERIFY_FAIL")
    print("runtime_entrypoint_missing")
    sys.exit(1)

print("PATCH236E_VERIFY_PASS")
print("commands=forge-rmc-neo-test-receipt-write, forge-rmc-neo-test-receipt-write-report")
print("boundary=controlled Neo RMC test_receipt write only; no Identity Vault DB write; no agent/long-term/private/shared memory; no private memory exposure; no secret reads; no autonomous execution")
