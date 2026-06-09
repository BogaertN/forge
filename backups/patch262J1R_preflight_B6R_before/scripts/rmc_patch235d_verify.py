#!/usr/bin/env python3
"""Static verifier for Patch 235D — Athena Governed Handshake Receipt Verification."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"
text = MAIN.read_text(encoding="utf-8")
errors = []
required = [
    "PATCH235D_ATHENA_HANDSHAKE_VERIFY_COMMANDS",
    "forge-athena-governed-handshake-verify",
    "forge-athena-governed-handshake-verify-report",
    "def cmd_forge_athena_governed_handshake_verify(session_id: str) -> None:",
    "def cmd_forge_athena_governed_handshake_verify_report(session_id: str) -> None:",
    "ATHENA_GOVERNED_HANDSHAKE_RECEIPT_VERIFIED",
    "BLOCKED_ATHENA_GOVERNED_HANDSHAKE_RECEIPT_VERIFY",
    "P235D_REQUIRED_235C_VERDICT",
    "P235D_REQUIRED_ECHO_VERDICT",
    "aiweb_patch235d_athena_governed_handshake_receipt_verify_v1",
    "source_patch235c_receipt_hash",
    "recomputed_receipt_hash",
    "no_rmc_memory_write",
    "no_secret_reads",
    "no_autonomous_execution",
]
for needle in required:
    if needle not in text:
        errors.append(f"missing main marker: {needle}")
idx_defs = text.find("# --- BEGIN PATCH 235D ATHENA GOVERNED HANDSHAKE RECEIPT VERIFY ---")
idx_main = text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main):
    errors.append("Patch 235D definitions appear after runtime main() call")
idx_action_route = text.find('user_input.lower() == "forge-athena-governed-handshake-verify"')
idx_report_route = text.find('user_input.lower() == "forge-athena-governed-handshake-verify-report"')
if not (0 <= idx_action_route < idx_report_route):
    errors.append("Patch 235D action route should be before report route")
block = text[idx_defs:idx_main] if idx_defs >= 0 and idx_main >= 0 else text
for bad in [
    '"identity_vault_database_written": True,',
    '"rmc_memory_written": True,',
    '"secret_reads_granted": True,',
    '"autonomous_tool_execution_granted": True,',
    '"secret_values_read": True,',
    '"autonomous_tool_execution_performed": True,',
]:
    if bad in block:
        errors.append(f"forbidden Patch 235D marker: {bad}")
try:
    data = json.loads(REG.read_text(encoding="utf-8"))
    tools = data.get("tools", {})
    for cmd in ["forge-athena-governed-handshake-verify", "forge-athena-governed-handshake-verify-report"]:
        if cmd not in tools:
            errors.append(f"tool registry missing {cmd}")
    if data.get("current_trust_level") != 5.0:
        errors.append(f"unexpected trust level: {data.get('current_trust_level')!r}")
except Exception as exc:
    errors.append(f"registry parse failed: {type(exc).__name__}: {exc}")
if errors:
    print("PATCH235D_VERIFY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("PATCH235D_VERIFY_PASS")
print("commands=forge-athena-governed-handshake-verify, forge-athena-governed-handshake-verify-report")
print("boundary=read-only Athena handshake receipt verification; no Identity Vault DB write; no RMC memory write; no secret reads; no autonomous execution")
