#!/usr/bin/env python3
"""Patch 232 static verifier."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"
main_text = MAIN.read_text(encoding="utf-8")
required = [
    "PATCH 232 MANUAL ACTIVATION COMMAND DESIGN/PREFLIGHT ROUTES",
    "PATCH 232 MANUAL ACTIVATION COMMAND DESIGN/PREFLIGHT PLAN",
    "forge-agent-activation-command-plan",
    "forge-agent-activation-command-plan-report",
    "def cmd_forge_agent_activation_command_plan(session_id: str) -> None:",
    "def cmd_forge_agent_activation_command_plan_report(session_id: str) -> None:",
    "MANUAL_ACTIVATION_COMMAND_PLAN_WRITTEN",
    "BLOCKED_MANUAL_ACTIVATION_COMMAND_PLAN",
    "forge-agent-activate-manual <agent_id>",
    "manual_activation_command_installed",
    "agent_identity_activation_performed",
    "identity_vault_database_written",
]
missing = [item for item in required if item not in main_text]
if missing:
    print("PATCH232_VERIFY_FAIL missing markers:")
    for item in missing:
        print(" -", item)
    sys.exit(1)
# Critical safety check: future command may appear as a string in the design plan,
# but the callable activation implementation and runtime route must not exist.
for forbidden in (
    "def cmd_forge_agent_activate_manual",
    'user_input.lower() == "forge-agent-activate-manual"',
    'user_input.lower().startswith("forge-agent-activate-manual")',
):
    if forbidden in main_text:
        print("PATCH232_VERIFY_FAIL activation command appears installed:", forbidden)
        sys.exit(1)
idx_defs = main_text.find("# --- BEGIN PATCH 232 MANUAL ACTIVATION COMMAND DESIGN/PREFLIGHT PLAN ---")
idx_main_entry = main_text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main_entry):
    print("PATCH232_VERIFY_FAIL Patch 232 definitions appear after runtime main() call")
    print("idx_defs=", idx_defs, "idx_main_entry=", idx_main_entry)
    sys.exit(1)
idx_route = main_text.find('user_input.lower() == "forge-agent-activation-command-plan"')
idx_route_report = main_text.find('user_input.lower() == "forge-agent-activation-command-plan-report"')
if idx_route < 0 or idx_route_report < 0:
    print("PATCH232_VERIFY_FAIL routes missing")
    sys.exit(1)
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
tools = registry.get("tools", {})
for key in ("forge_agent_activation_command_plan", "forge_agent_activation_command_plan_report"):
    if key not in tools:
        print(f"PATCH232_VERIFY_FAIL missing tool registry key {key}")
        sys.exit(1)
if registry.get("current_trust_level") != 5.0:
    print("PATCH232_VERIFY_FAIL trust level changed", registry.get("current_trust_level"))
    sys.exit(1)
print("PATCH232_VERIFY_PASS")
print("commands=forge-agent-activation-command-plan, forge-agent-activation-command-plan-report")
print("boundary=manual activation command design/preflight plan only; activation command not installed; no RMC memory write; no Identity Vault DB write; no activation")
