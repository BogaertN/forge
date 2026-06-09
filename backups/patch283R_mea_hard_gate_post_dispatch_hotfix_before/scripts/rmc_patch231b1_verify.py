#!/usr/bin/env python3
"""Patch 231B.1 static verifier."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"

main_text = MAIN.read_text(encoding="utf-8")
required = [
    "PATCH 231B MULTI-AGENT ACTIVATION PREFLIGHT ROUTES",
    "PATCH 231B MULTI-AGENT ACTIVATION PREFLIGHT VERIFY COMMANDS",
    "forge-agent-activation-preflight-all",
    "forge-agent-activation-preflight-all-report",
    "def cmd_forge_agent_activation_preflight_all(session_id: str) -> None:",
    "def cmd_forge_agent_activation_preflight_all_report(session_id: str) -> None:",
    "ALL_TARGET_AGENTS_READY_FOR_MANUAL_ACTIVATION",
    "BLOCKED_ACTIVATION_PREFLIGHT_ALL_TARGETS",
    'activation_command_installed": False',
    'identity_vault_database_written": False',
    'agent_identity_activation_performed": False',
]
missing = [item for item in required if item not in main_text]
if missing:
    print("PATCH231B1_VERIFY_FAIL missing markers:")
    for item in missing:
        print(" -", item)
    sys.exit(1)
if "def cmd_forge_agent_activate_manual" in main_text or "forge-agent-activate-manual\")" in main_text:
    print("PATCH231B1_VERIFY_FAIL activation command appears installed")
    sys.exit(1)
# Critical regression check: supporting definitions must appear before runtime main() call.
idx_defs = main_text.find("# --- BEGIN PATCH 231B MULTI-AGENT ACTIVATION PREFLIGHT VERIFY COMMANDS ---")
idx_main_entry = main_text.find('if __name__ == "__main__":\n    main()')
if not (0 <= idx_defs < idx_main_entry):
    print("PATCH231B1_VERIFY_FAIL 231B definitions still appear after runtime main() call")
    print("idx_defs=", idx_defs, "idx_main_entry=", idx_main_entry)
    sys.exit(1)
# Route ordering: all/report routes must appear before generic preflight prefix.
idx_all = main_text.find('user_input.lower() == "forge-agent-activation-preflight-all"')
idx_all_report = main_text.find('user_input.lower() == "forge-agent-activation-preflight-all-report"')
idx_report = main_text.find('user_input.lower() == "forge-agent-activation-preflight-report"')
idx_prefix = main_text.find('user_input.lower().startswith("forge-agent-activation-preflight")')
if not (0 <= idx_all < idx_prefix and 0 <= idx_all_report < idx_prefix and 0 <= idx_report < idx_prefix):
    print("PATCH231B1_VERIFY_FAIL route order unsafe")
    print(idx_all, idx_all_report, idx_report, idx_prefix)
    sys.exit(1)
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
tools = registry.get("tools", {})
for key in ("forge_agent_activation_preflight_all", "forge_agent_activation_preflight_all_report"):
    if key not in tools:
        print(f"PATCH231B1_VERIFY_FAIL missing tool registry key {key}")
        sys.exit(1)
print("PATCH231B1_VERIFY_PASS")
print("commands=unchanged from Patch 231B; definition order fixed before runtime main() call")
print("boundary=route/definition-order hotfix only; no activation command installed; no RMC memory write; no Identity Vault DB write; no activation")
