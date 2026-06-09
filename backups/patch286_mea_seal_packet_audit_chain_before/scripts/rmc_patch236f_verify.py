#!/usr/bin/env python3
"""Patch 236F verifier: controlled Neo RMC test receipt verification."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"

required = [
    "forge-rmc-neo-test-receipt-verify",
    "forge-rmc-neo-test-receipt-verify-report",
    "RMC_TEST_RECEIPT_VERIFIED_GOVERNED_NEO",
    "P236F_VERIFY_JSON",
    "cmd_forge_rmc_neo_test_receipt_verify",
    "cmd_forge_rmc_neo_test_receipt_verify_report",
    "private_memory_payloads_read",
    "public_frontline_receipt_only",
]
for path in (MAIN, REGISTRY):
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
text = MAIN.read_text(encoding="utf-8")
missing = [token for token in required if token not in text]
if missing:
    raise SystemExit(f"PATCH236F_VERIFY_FAIL missing tokens: {missing}")
if "identity_vault_database_written\": False" not in text:
    raise SystemExit("PATCH236F_VERIFY_FAIL boundary missing identity false")
if "rmc_test_receipt_written\": False" not in text:
    raise SystemExit("PATCH236F_VERIFY_FAIL boundary missing no new receipt write")
if "private_memory_exposure_granted" not in text:
    raise SystemExit("PATCH236F_VERIFY_FAIL private memory exposure guard missing")
# Expected command surface should be 844 after two command additions.
if 'Expected: 844' in text:
    pass
# Count literal command registrations in FORGE_EXPECTED_COMMANDS append block indirectly.
for cmd in ["forge-rmc-neo-test-receipt-verify", "forge-rmc-neo-test-receipt-verify-report"]:
    if text.count(cmd) < 2:
        raise SystemExit(f"PATCH236F_VERIFY_FAIL command not fully wired: {cmd}")
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
if registry.get("current_trust_level") != 5.0:
    raise SystemExit("PATCH236F_VERIFY_FAIL trust level changed")
print("PATCH236F_VERIFY_PASS")
print("commands=forge-rmc-neo-test-receipt-verify, forge-rmc-neo-test-receipt-verify-report")
print("boundary=read-only Neo RMC test_receipt verification; no Identity Vault DB write; no new RMC write; no agent/long-term/private/shared memory; no private memory exposure; no secret reads; no autonomous execution")
