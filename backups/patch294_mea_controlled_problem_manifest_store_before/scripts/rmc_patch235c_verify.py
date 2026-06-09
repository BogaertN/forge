#!/usr/bin/env python3
"""Static verifier for Patch 235C — Athena Governed Handshake."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"
text = MAIN.read_text(encoding="utf-8")
errors = []
required = [
    "PATCH235C_ATHENA_GOVERNED_HANDSHAKE_COMMANDS",
    "forge-athena-governed-handshake",
    "forge-athena-governed-handshake-report",
    "def cmd_forge_athena_governed_handshake(session_id: str) -> None:",
    "def cmd_forge_athena_governed_handshake_report(session_id: str) -> None:",
    "ATHENA_HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT",
    "BLOCKED_ATHENA_GOVERNED_HANDSHAKE",
    "ECHO_VALIDATION_PASSED_ATHENA_GOVERNED_ACTIVE_AGENT",
    "P235C_REQUIRED_235B_VERDICT",
    "governed_athena_strategy_handshake",
    "athena_can_read_secrets",
    "athena_can_execute_tools_by_itself",
    "secret_reads_granted",
    "aiweb_patch235c_athena_governed_handshake_v1",
]
for needle in required:
    if needle not in text:
        errors.append(f"missing main marker: {needle}")
idx_defs = text.find("# --- BEGIN PATCH 235C ATHENA GOVERNED HANDSHAKE ---")
idx_main = text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main):
    errors.append("Patch 235C definitions appear after runtime main() call")
idx_action_route = text.find('user_input.lower() == "forge-athena-governed-handshake"')
idx_report_route = text.find('user_input.lower() == "forge-athena-governed-handshake-report"')
if not (0 <= idx_action_route < idx_report_route):
    errors.append("Patch 235C action route should be before report route")
block = text[idx_defs:idx_main] if idx_defs >= 0 and idx_main >= 0 else text
for bad in [
    '"identity_vault_database_written": True,',
    '"rmc_memory_written": True,',
    '"autonomous_tool_execution_granted": True,',
    '"secret_reads_granted": True,',
    '"athena_can_execute_tools_by_itself": True,',
    '"athena_can_read_secrets": True,',
    '"athena_can_mutate_identity_vault": True,',
    '"athena_can_bypass_forge": True,',
    '"athena_can_create_patches_without_approval": True,',
]:
    if bad in block:
        errors.append(f"forbidden Patch 235C marker: {bad}")
try:
    data = json.loads(REG.read_text(encoding="utf-8"))
    tools = data.get("tools", {})
    for cmd in ["forge-athena-governed-handshake", "forge-athena-governed-handshake-report"]:
        if cmd not in tools:
            errors.append(f"tool registry missing {cmd}")
    if data.get("current_trust_level") != 5.0:
        errors.append(f"unexpected trust level: {data.get('current_trust_level')!r}")
except Exception as exc:
    errors.append(f"registry parse failed: {type(exc).__name__}: {exc}")
if errors:
    print("PATCH235C_VERIFY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("PATCH235C_VERIFY_PASS")
print("commands=forge-athena-governed-handshake, forge-athena-governed-handshake-report")
print("boundary=governed Athena handshake receipt only; no Identity Vault DB write; no RMC memory write; no secret reads; no autonomous execution")
