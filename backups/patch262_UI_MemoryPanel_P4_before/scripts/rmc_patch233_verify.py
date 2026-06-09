#!/usr/bin/env python3
"""Patch 233 static verifier."""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"
main_text = MAIN.read_text(encoding="utf-8")
required = [
    "PATCH 233 GILLIGAN GOVERNED HANDSHAKE ROUTES",
    "PATCH 233 GILLIGAN GOVERNED HANDSHAKE",
    "forge-gilligan-governed-handshake",
    "forge-gilligan-governed-handshake-report",
    "def cmd_forge_gilligan_governed_handshake(session_id: str) -> None:",
    "def cmd_forge_gilligan_governed_handshake_report(session_id: str) -> None:",
    "HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT",
    "ECHO_VALIDATION_PASSED_GOVERNED_ACTIVE_AGENT",
    "GILLIGAN_ACTIVATION_VERIFIED_ACTIVE_GOVERNED",
    "active_governed",
]
required = required + ['"rmc_memory_written": False', '"identity_vault_database_written": False', '"agent_identity_activation_performed": False', '"autonomous_tool_execution_performed": False']
missing = [item for item in required if item not in main_text]
if missing:
    print("PATCH233_VERIFY_FAIL missing markers:")
    for item in missing:
        print(" -", item)
    sys.exit(1)
idx_defs = main_text.find("# --- BEGIN PATCH 233 GILLIGAN GOVERNED HANDSHAKE ---")
idx_main_entry = main_text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main_entry):
    print("PATCH233_VERIFY_FAIL Patch 233 definitions appear after runtime main() call")
    print("idx_defs=", idx_defs, "idx_main_entry=", idx_main_entry)
    sys.exit(1)
idx_report_route = main_text.find('user_input.lower() == "forge-gilligan-governed-handshake-report"')
idx_action_route = main_text.find('user_input.lower() == "forge-gilligan-governed-handshake"')
if not (0 <= idx_action_route < idx_report_route):
    print("PATCH233_VERIFY_FAIL action/report route ordering unexpected")
    print("idx_action_route=", idx_action_route, "idx_report_route=", idx_report_route)
    sys.exit(1)
patch_block = main_text[idx_defs:idx_main_entry]
for forbidden in (
    '"identity_vault_database_written": True',
    '"rmc_memory_written": True',
    '"autonomous_tool_execution_performed": True',
    '"protoforge2_execution_performed": True',
    '"echoforge_creation_performed": True',
    'gilligan_can_execute_tools_by_itself": True',
    'gilligan_can_write_memory_by_itself": True',
    'gilligan_can_bypass_forge": True',
):
    if forbidden in patch_block:
        print("PATCH233_VERIFY_FAIL forbidden marker appears in Patch 233 block:", forbidden)
        sys.exit(1)
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
if registry.get("current_trust_level") != 5.0:
    print("PATCH233_VERIFY_FAIL trust level changed", registry.get("current_trust_level"))
    sys.exit(1)
tools = registry.get("tools", {})
for key in ("forge_gilligan_governed_handshake", "forge_gilligan_governed_handshake_report"):
    if key not in tools:
        print("PATCH233_VERIFY_FAIL missing tool registry key", key)
        sys.exit(1)
print("PATCH233_VERIFY_PASS")
print("commands=forge-gilligan-governed-handshake, forge-gilligan-governed-handshake-report")
print("boundary=governed handshake receipt only; no Identity Vault DB write; no RMC memory write; no autonomous execution")
