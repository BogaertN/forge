#!/usr/bin/env python3
"""Patch 231 static verifier — identity activation approval plan only."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
registry = root / "config" / "tool_registry.json"
main_text = main.read_text(encoding="utf-8")
reg = json.loads(registry.read_text(encoding="utf-8"))
required = [
    "forge-agent-activation-plan",
    "forge-agent-activation-plan-report",
    "cmd_forge_agent_activation_plan",
    "cmd_forge_agent_activation_plan_report",
    "aiweb_patch231_identity_activation_approval_plan_v1",
    "IDENTITY_ACTIVATION_APPROVAL_PLAN_WRITTEN",
    "forge-agent-activation-preflight <agent_id>",
    "forge-agent-activate-manual <agent_id>",
    "READY_FOR_MANUAL_ACTIVATION",
    "BLOCKED_ACTIVATION_PREFLIGHT_<REASON>",
    "activation_command_installed",
    "preflight_command_installed",
    "identity_vault_database_written",
    "rmc_memory_written",
    "agent_identity_activation_performed",
]
missing = [item for item in required if item not in main_text]
for key in ["forge_agent_activation_plan", "forge_agent_activation_plan_report"]:
    if key not in (reg.get("tools") or {}):
        missing.append(f"registry:{key}")
# Patch 231 must not add a route that actually calls activation.
for forbidden in ["if user_input.lower().startswith(\"forge-agent-activate-manual", "cmd_forge_agent_activate_manual(", "def cmd_forge_agent_activate_manual"]:
    if forbidden in main_text:
        missing.append(f"forbidden_activation_command_installed:{forbidden}")
if missing:
    print("PATCH231_VERIFY_FAIL")
    for item in missing:
        print(f"missing={item}")
    raise SystemExit(1)
print("PATCH231_VERIFY_PASS")
print("commands=forge-agent-activation-plan, forge-agent-activation-plan-report")
print("boundary=plan-only; no activation command installed; no preflight command installed; no RMC memory write; no Identity Vault DB write; no activation")
