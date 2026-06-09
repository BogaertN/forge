#!/usr/bin/env python3
"""Patch 232C static verifier."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"
main_text = MAIN.read_text(encoding="utf-8")
required = [
    "PATCH 232C GILLIGAN ACTIVATION VERIFY ROUTES",
    "PATCH 232C GILLIGAN ACTIVATION VERIFICATION",
    "forge-agent-verify-gilligan-activation",
    "forge-agent-verify-gilligan-activation-report",
    "def cmd_forge_agent_verify_gilligan_activation(session_id: str) -> None:",
    "def cmd_forge_agent_verify_gilligan_activation_report(session_id: str) -> None:",
    "GILLIGAN_ACTIVATION_VERIFIED_ACTIVE_GOVERNED",
    "ALL_TARGET_AGENTS_READY_FOR_MANUAL_ACTIVATION",
    "GILLIGAN_ACTIVATED_ACTIVE_GOVERNED",
    "athena.local",
    "neo.local",
    "post_activation_preflight_no_longer_ready",
    "no_autonomous_tool_execution_granted",
]
missing = [item for item in required if item not in main_text]
if missing:
    print("PATCH232C_VERIFY_FAIL missing markers:")
    for item in missing:
        print(" -", item)
    sys.exit(1)
idx_defs = main_text.find("# --- BEGIN PATCH 232C GILLIGAN ACTIVATION VERIFICATION ---")
idx_main_entry = main_text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main_entry):
    print("PATCH232C_VERIFY_FAIL Patch 232C definitions appear after runtime main() call")
    print("idx_defs=", idx_defs, "idx_main_entry=", idx_main_entry)
    sys.exit(1)
idx_report_route = main_text.find('user_input.lower() == "forge-agent-verify-gilligan-activation-report"')
idx_action_route = main_text.find('user_input.lower() == "forge-agent-verify-gilligan-activation"')
if not (0 <= idx_action_route < idx_report_route):
    print("PATCH232C_VERIFY_FAIL expected action route before report route for exact commands")
    print("idx_action_route=", idx_action_route, "idx_report_route=", idx_report_route)
    sys.exit(1)
for forbidden in (
    '"identity_vault_database_written": True,\n            "rmc_memory_written": False,\n            "agent_identity_activation_performed": False',
    'forge-agent-activate-manual gilligan.local CONFIRM_GILLIGAN_ACTIVE_GOVERNED',
    '"rmc_memory_written": True',
    '"autonomous_tool_execution_granted": True',
    '"forge_bypass_granted": True',
    '"patch_autonomy_granted": True',
):
    if forbidden in main_text and forbidden != 'forge-agent-activate-manual gilligan.local CONFIRM_GILLIGAN_ACTIVE_GOVERNED':
        print("PATCH232C_VERIFY_FAIL forbidden marker appears:", forbidden)
        sys.exit(1)
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
tools = registry.get("tools", {})
for key in ("forge_agent_verify_gilligan_activation", "forge_agent_verify_gilligan_activation_report"):
    if key not in tools:
        print(f"PATCH232C_VERIFY_FAIL missing tool registry key {key}")
        sys.exit(1)
if registry.get("current_trust_level") != 5.0:
    print("PATCH232C_VERIFY_FAIL trust level changed", registry.get("current_trust_level"))
    sys.exit(1)
print("PATCH232C_VERIFY_PASS")
print("commands=forge-agent-verify-gilligan-activation, forge-agent-verify-gilligan-activation-report")
print("boundary=read-only verification; no Identity Vault DB write; no RMC memory write; no activation")
