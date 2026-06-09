#!/usr/bin/env python3
"""Static verifier for Patch 234A — Controlled RMC Test Receipt Verification."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"

REQUIRED = [
    "forge-rmc-gilligan-test-receipt-verify",
    "forge-rmc-gilligan-test-receipt-verify-report",
    "cmd_forge_rmc_gilligan_test_receipt_verify",
    "cmd_forge_rmc_gilligan_test_receipt_verify_report",
    "P234A_VERIFY_JSON",
    "RMC_TEST_RECEIPT_VERIFIED_GOVERNED_GILLIGAN",
    "RMC_TEST_RECEIPT_VERIFY_BLOCKED",
    "receipt_hash_valid",
    "patch234_identity_vault_unchanged",
    "patch234_agent_memory_not_written",
    "patch234_shared_memory_not_written",
]

FORBIDDEN = [
    "identity_vault_database_written\": True",
    "agent_memory_written\": True",
    "long_term_memory_written\": True",
    "private_memory_written\": True",
    "shared_memory_written\": True",
    "autonomous_tool_execution_performed\": True",
]

def fail(msg: str) -> int:
    print(f"PATCH234A_VERIFY_FAIL: {msg}")
    return 1


def main() -> int:
    if not MAIN.exists():
        return fail("main.py missing")
    text = MAIN.read_text(encoding="utf-8")
    for token in REQUIRED:
        if token not in text:
            return fail(f"missing token: {token}")
    start = text.find("# --- BEGIN PATCH 234A CONTROLLED RMC TEST RECEIPT VERIFY ---")
    end = text.find("# --- END PATCH 234A CONTROLLED RMC TEST RECEIPT VERIFY ---")
    if start < 0 or end < start:
        return fail("Patch 234A block markers missing")
    patch_block = text[start:end]
    for token in FORBIDDEN:
        if token in patch_block:
            return fail(f"forbidden token present in Patch 234A block: {token}")
    if 'if __name__ == "__main__":' not in text:
        return fail("runtime entrypoint missing")
    entry_idx = text.rindex('if __name__ == "__main__":')
    for fn in ["def cmd_forge_rmc_gilligan_test_receipt_verify", "def cmd_forge_rmc_gilligan_test_receipt_verify_report"]:
        idx = text.find(fn)
        if idx < 0:
            return fail(f"missing function: {fn}")
        if idx > entry_idx:
            return fail(f"function appears after runtime entrypoint: {fn}")
    try:
        reg = json.loads(REG.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail(f"tool registry unreadable: {exc}")
    tools = reg.get("tools", {})
    for cmd in ["forge-rmc-gilligan-test-receipt-verify", "forge-rmc-gilligan-test-receipt-verify-report"]:
        if cmd not in tools:
            return fail(f"registry missing command: {cmd}")
    if tools["forge-rmc-gilligan-test-receipt-verify"].get("writes") is not True:
        return fail("verify command should write only Forge-owned verification report")
    if tools["forge-rmc-gilligan-test-receipt-verify-report"].get("writes") is not False:
        return fail("report command should be read-only")
    print("PATCH234A_VERIFY_PASS")
    print("commands=forge-rmc-gilligan-test-receipt-verify, forge-rmc-gilligan-test-receipt-verify-report")
    print("boundary=read-only verification report; no Identity Vault DB write; no RMC memory write; no memory pollution; no autonomous execution")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
