#!/usr/bin/env python3
"""Patch 235E.1 static verifier — Athena RMC receipt resolver hotfix."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main_text = (root / "main.py").read_text(encoding="utf-8")
registry = json.loads((root / "config" / "tool_registry.json").read_text(encoding="utf-8"))
required = [
    "forge-rmc-athena-test-receipt-write",
    "forge-rmc-athena-test-receipt-write-report",
    "cmd_forge_rmc_athena_test_receipt_write",
    "cmd_forge_rmc_athena_test_receipt_write_report",
    "RMC_TEST_RECEIPT_WRITTEN_GOVERNED_ATHENA",
    "P235E_WRITE_TYPE = \"test_receipt\"",
    "scaffold = _p230_latest_scaffold_root()",
    "profile = identity.get(\"resolved_profile\") or {}",
]
missing = [item for item in required if item not in main_text]
if missing:
    raise SystemExit("PATCH235E1_VERIFY_FAIL missing main markers: " + ", ".join(missing))
if "scaffold = _p229_resolve_rmc_root()" in main_text:
    raise SystemExit("PATCH235E1_VERIFY_FAIL stale undefined _p229_resolve_rmc_root call still present")
for cmd in ["forge-rmc-athena-test-receipt-write", "forge-rmc-athena-test-receipt-write-report"]:
    if cmd not in registry.get("tools", {}):
        raise SystemExit("PATCH235E1_VERIFY_FAIL missing registry tool: " + cmd)
if registry.get("current_trust_level") != 5.0:
    raise SystemExit("PATCH235E1_VERIFY_FAIL trust level changed")
print("PATCH235E1_VERIFY_PASS")
print("commands=forge-rmc-athena-test-receipt-write, forge-rmc-athena-test-receipt-write-report")
print("hotfix=replace stale undefined _p229_resolve_rmc_root dependency with _p230_latest_scaffold_root and read resolved_profile")
print("boundary=no new commands; controlled Athena RMC write_type=test_receipt only; no Identity Vault DB write; no agent/long_term/private/shared memory; no secret reads; no autonomous execution")
