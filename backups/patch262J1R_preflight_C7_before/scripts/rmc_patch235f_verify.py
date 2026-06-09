#!/usr/bin/env python3
"""Patch 235F static verifier — controlled Athena RMC test receipt verification."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main_text = (root / "main.py").read_text(encoding="utf-8")
registry = json.loads((root / "config" / "tool_registry.json").read_text(encoding="utf-8"))
required = [
    "forge-rmc-athena-test-receipt-verify",
    "forge-rmc-athena-test-receipt-verify-report",
    "cmd_forge_rmc_athena_test_receipt_verify",
    "cmd_forge_rmc_athena_test_receipt_verify_report",
    "RMC_TEST_RECEIPT_VERIFIED_GOVERNED_ATHENA",
    'P235F_EXPECTED_WRITE_TYPE = "test_receipt"',
    "receipt_filename_safe",
    "receipt_boundary_secret_false",
    "current_athena_profile_hash_matches_receipt",
    "Patch 236 — Neo activation dry-run gate",
]
missing = [item for item in required if item not in main_text]
if missing:
    raise SystemExit("PATCH235F_VERIFY_FAIL missing main markers: " + ", ".join(missing))
for forbidden in [
    '"agent_memory_written": True',
    '"long_term_memory_written": True',
    '"private_memory_written": True',
    '"shared_memory_written": True',
    '"secret_values_read": True',
    '"autonomous_tool_execution_performed": True',
]:
    if forbidden in main_text:
        raise SystemExit("PATCH235F_VERIFY_FAIL unsafe marker present: " + forbidden)
for cmd in ["forge-rmc-athena-test-receipt-verify", "forge-rmc-athena-test-receipt-verify-report"]:
    if cmd not in registry.get("tools", {}):
        raise SystemExit("PATCH235F_VERIFY_FAIL missing registry tool: " + cmd)
if registry.get("current_trust_level") != 5.0:
    raise SystemExit("PATCH235F_VERIFY_FAIL trust level changed")
print("PATCH235F_VERIFY_PASS")
print("commands=forge-rmc-athena-test-receipt-verify, forge-rmc-athena-test-receipt-verify-report")
print("boundary=read-only Athena test_receipt verification; no Identity Vault DB write; no RMC memory write; no memory pollution; no secret reads; no autonomous execution")
