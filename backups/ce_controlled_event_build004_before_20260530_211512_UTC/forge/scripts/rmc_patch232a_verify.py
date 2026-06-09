#!/usr/bin/env python3
"""Patch 232A static verifier."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"
main_text = MAIN.read_text(encoding="utf-8")
required = [
    "PATCH 232A GILLIGAN MANUAL ACTIVATION DRY-RUN GATE ROUTES",
    "PATCH 232A GILLIGAN MANUAL ACTIVATION DRY-RUN GATE",
    "forge-agent-activate-gilligan-dry-run",
    "forge-agent-activate-gilligan-dry-run-report",
    "def cmd_forge_agent_activate_gilligan_dry_run(session_id: str) -> None:",
    "def cmd_forge_agent_activate_gilligan_dry_run_report(session_id: str) -> None:",
    "GILLIGAN_MANUAL_ACTIVATION_DRY_RUN_READY",
    "BLOCKED_GILLIGAN_MANUAL_ACTIVATION_DRY_RUN",
    "active_governed",
    "identity_vault_database_written",
    "agent_identity_activation_performed",
    "manual_activation_command_installed",
]
missing = [item for item in required if item not in main_text]
if missing:
    print("PATCH232A_VERIFY_FAIL missing markers:")
    for item in missing:
        print(" -", item)
    sys.exit(1)
# Must not install or define a live activation command.
for forbidden in (
    "def cmd_forge_agent_activate_manual",
    'user_input.lower() == "forge-agent-activate-manual"',
    'user_input.lower().startswith("forge-agent-activate-manual")',
    "identity_vault_database_written\": True",
    "agent_identity_activation_performed\": True",
):
    if forbidden in main_text:
        print("PATCH232A_VERIFY_FAIL live activation/write marker appears installed:", forbidden)
        sys.exit(1)
idx_defs = main_text.find("# --- BEGIN PATCH 232A GILLIGAN MANUAL ACTIVATION DRY-RUN GATE ---")
idx_main_entry = main_text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main_entry):
    print("PATCH232A_VERIFY_FAIL Patch 232A definitions appear after runtime main() call")
    print("idx_defs=", idx_defs, "idx_main_entry=", idx_main_entry)
    sys.exit(1)
# Route should appear before the 231A generic preflight prefix route is irrelevant but route must exist.
for route in (
    'user_input.lower() == "forge-agent-activate-gilligan-dry-run"',
    'user_input.lower() == "forge-agent-activate-gilligan-dry-run-report"',
):
    if route not in main_text:
        print("PATCH232A_VERIFY_FAIL route missing", route)
        sys.exit(1)
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
tools = registry.get("tools", {})
for key in ("forge_agent_activate_gilligan_dry_run", "forge_agent_activate_gilligan_dry_run_report"):
    if key not in tools:
        print(f"PATCH232A_VERIFY_FAIL missing tool registry key {key}")
        sys.exit(1)
if registry.get("current_trust_level") != 5.0:
    print("PATCH232A_VERIFY_FAIL trust level changed", registry.get("current_trust_level"))
    sys.exit(1)
print("PATCH232A_VERIFY_PASS")
print("commands=forge-agent-activate-gilligan-dry-run, forge-agent-activate-gilligan-dry-run-report")
print("boundary=Gilligan activation dry-run only; no activation command installed; no RMC memory write; no Identity Vault DB write; no activation")
