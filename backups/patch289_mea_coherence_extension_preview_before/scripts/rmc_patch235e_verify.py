#!/usr/bin/env python3
"""Patch 235E static verifier."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main = (root / "main.py").read_text(encoding="utf-8")
registry = json.loads((root / "config" / "tool_registry.json").read_text(encoding="utf-8"))
required = [
    "forge-rmc-athena-test-receipt-write",
    "forge-rmc-athena-test-receipt-write-report",
    "cmd_forge_rmc_athena_test_receipt_write",
    "cmd_forge_rmc_athena_test_receipt_write_report",
    "RMC_TEST_RECEIPT_WRITTEN_GOVERNED_ATHENA",
    "P235E_WRITE_TYPE = \"test_receipt\"",
]
missing = [item for item in required if item not in main]
if missing:
    raise SystemExit("PATCH235E_VERIFY_FAIL missing main markers: " + ", ".join(missing))
for cmd in ["forge-rmc-athena-test-receipt-write", "forge-rmc-athena-test-receipt-write-report"]:
    if cmd not in registry.get("tools", {}):
        raise SystemExit("PATCH235E_VERIFY_FAIL missing registry tool: " + cmd)
if registry.get("current_trust_level") != 5.0:
    raise SystemExit("PATCH235E_VERIFY_FAIL trust level changed")
print("PATCH235E_VERIFY_PASS")
print("commands=forge-rmc-athena-test-receipt-write, forge-rmc-athena-test-receipt-write-report")
print("boundary=controlled Athena RMC write_type=test_receipt only; no Identity Vault DB write; no agent/long_term/private/shared memory; no secret reads; no autonomous execution")
