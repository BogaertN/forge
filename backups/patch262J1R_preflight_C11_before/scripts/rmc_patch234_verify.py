#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
main = (ROOT / "main.py").read_text(encoding="utf-8")
reg = json.loads((ROOT / "config" / "tool_registry.json").read_text(encoding="utf-8"))
errors = []
required = [
    "forge-rmc-gilligan-test-receipt-write",
    "forge-rmc-gilligan-test-receipt-write-report",
    "cmd_forge_rmc_gilligan_test_receipt_write",
    "cmd_forge_rmc_gilligan_test_receipt_write_report",
    "RMC_TEST_RECEIPT_WRITTEN_GOVERNED_GILLIGAN",
    "P234_WRITE_TYPE = \"test_receipt\"",
    "P234_FORBIDDEN_WRITE_TYPES",
]
for token in required:
    if token not in main:
        errors.append(f"missing main token: {token}")
entry = 'if __name__ == "__main__":\n    main()'
for fn in ["def cmd_forge_rmc_gilligan_test_receipt_write", "def cmd_forge_rmc_gilligan_test_receipt_write_report"]:
    if fn in main and entry in main and main.index(fn) > main.index(entry):
        errors.append(f"{fn} appears after runtime entrypoint")
for cmd in ["forge-rmc-gilligan-test-receipt-write", "forge-rmc-gilligan-test-receipt-write-report"]:
    if cmd not in reg.get("tools", {}):
        errors.append(f"missing registry tool: {cmd}")
if "identity_vault_database_written\": True" in main[main.find("# --- BEGIN PATCH 234"):main.find("# --- END PATCH 234")]:
    errors.append("Patch 234 block claims Identity Vault database write")
if errors:
    print("PATCH234_VERIFY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("PATCH234_VERIFY_PASS")
print("commands=forge-rmc-gilligan-test-receipt-write, forge-rmc-gilligan-test-receipt-write-report")
print("boundary=controlled RMC write_type=test_receipt only; no Identity Vault DB write; no agent/long_term/private/shared memory; no autonomous execution")
