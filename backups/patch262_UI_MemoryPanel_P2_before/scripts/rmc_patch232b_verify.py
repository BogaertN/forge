#!/usr/bin/env python3
"""Patch 232B static verifier."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"
main_text = MAIN.read_text(encoding="utf-8")
required = [
    "PATCH 232B GILLIGAN MANUAL ACTIVATION APPLY ROUTES",
    "PATCH 232B GILLIGAN MANUAL ACTIVATION APPLY",
    "forge-agent-activate-manual",
    "forge-agent-activate-manual-report",
    "def cmd_forge_agent_activate_manual(session_id: str, agent_id: str = \"\", approval_token: str = \"\") -> None:",
    "def cmd_forge_agent_activate_manual_report(session_id: str) -> None:",
    "CONFIRM_GILLIGAN_ACTIVE_GOVERNED",
    "GILLIGAN_ACTIVATED_ACTIVE_GOVERNED",
    "BLOCKED_GILLIGAN_MANUAL_ACTIVATION_APPLY",
    "identity_vault_database_written\": True",
    "agent_identity_activation_performed\": ok",
    "gilligan_can_execute_tools_by_itself",
    "gilligan_can_write_memory_by_itself",
    "gilligan_can_bypass_forge",
]
missing = [item for item in required if item not in main_text]
if missing:
    print("PATCH232B_VERIFY_FAIL missing markers:")
    for item in missing:
        print(" -", item)
    sys.exit(1)
# Definitions must be above runtime main() entry.
idx_defs = main_text.find("# --- BEGIN PATCH 232B GILLIGAN MANUAL ACTIVATION APPLY ---")
idx_main_entry = main_text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main_entry):
    print("PATCH232B_VERIFY_FAIL Patch 232B definitions appear after runtime main() call")
    print("idx_defs=", idx_defs, "idx_main_entry=", idx_main_entry)
    sys.exit(1)
# Report exact route must precede prefix route.
idx_report_route = main_text.find('user_input.lower() == "forge-agent-activate-manual-report"')
idx_prefix_route = main_text.find('user_input.lower().startswith("forge-agent-activate-manual")')
if not (0 <= idx_report_route < idx_prefix_route):
    print("PATCH232B_VERIFY_FAIL report route must precede prefix route")
    print("idx_report_route=", idx_report_route, "idx_prefix_route=", idx_prefix_route)
    sys.exit(1)
for forbidden in (
    "P232B_TARGET_AGENT_ID = \"athena.local\"",
    "P232B_TARGET_AGENT_ID = \"neo.local\"",
    '"rmc_memory_written": True',
    '"autonomous_tool_execution_granted": True',
    '"forge_bypass_granted": True',
    '"patch_autonomy_granted": True',
):
    if forbidden in main_text:
        print("PATCH232B_VERIFY_FAIL forbidden marker appears:", forbidden)
        sys.exit(1)
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
tools = registry.get("tools", {})
for key in ("forge_agent_activate_manual", "forge_agent_activate_manual_report"):
    if key not in tools:
        print(f"PATCH232B_VERIFY_FAIL missing tool registry key {key}")
        sys.exit(1)
if registry.get("current_trust_level") != 5.0:
    print("PATCH232B_VERIFY_FAIL trust level changed", registry.get("current_trust_level"))
    sys.exit(1)
print("PATCH232B_VERIFY_PASS")
print("commands=forge-agent-activate-manual, forge-agent-activate-manual-report")
print("boundary=Gilligan-only explicit-token Identity Vault activation apply; no RMC memory write; no autonomous execution")
