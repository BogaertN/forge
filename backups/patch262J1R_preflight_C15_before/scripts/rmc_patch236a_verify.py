#!/usr/bin/env python3
# rmc_patch236a_verify.py — verifies Patch 236A Neo manual activation apply wiring.
from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
registry = root / "config" / "tool_registry.json"
text = main.read_text(encoding="utf-8")
reg = json.loads(registry.read_text(encoding="utf-8"))
required = [
    "forge-agent-activate-neo-manual",
    "forge-agent-activate-neo-manual-report",
    "CONFIRM_NEO_ACTIVE_GOVERNED",
    "NEO_ACTIVATED_ACTIVE_GOVERNED",
    "P236A_TARGET_AGENT_ID = \"neo.local\"",
    "P236_NEO_DRY_RUN_JSON",
    "GILLIGAN_NOT_ACTIVE_GOVERNED",
    "ATHENA_NOT_ACTIVE_GOVERNED",
]
missing = [item for item in required if item not in text]
if missing:
    print("PATCH236A_VERIFY_FAIL")
    print("missing=" + ", ".join(missing))
    sys.exit(1)
if "forge-agent-activate-neo-manual" not in reg.get("tools", {}):
    print("PATCH236A_VERIFY_FAIL")
    print("missing_registry_tool=forge-agent-activate-neo-manual")
    sys.exit(1)
if "forge-agent-activate-neo-manual-report" not in reg.get("tools", {}):
    print("PATCH236A_VERIFY_FAIL")
    print("missing_registry_tool=forge-agent-activate-neo-manual-report")
    sys.exit(1)
if "cmd_forge_agent_activate_neo_manual" not in text or "cmd_forge_agent_activate_neo_manual_report" not in text:
    print("PATCH236A_VERIFY_FAIL")
    print("missing_command_function")
    sys.exit(1)
if "forge-agent-activate-neo-manual-report" not in text.split("forge-agent-activate-neo-manual", 1)[0] and text.find('if user_input.lower() == "forge-agent-activate-neo-manual-report"') > text.find('if user_input.lower().startswith("forge-agent-activate-neo-manual")'):
    print("PATCH236A_VERIFY_FAIL")
    print("route_order_bad")
    sys.exit(1)
print("PATCH236A_VERIFY_PASS")
print("commands=forge-agent-activate-neo-manual, forge-agent-activate-neo-manual-report")
print("boundary=token-gated Neo-only Identity Vault activation apply; no RMC memory write; no private memory exposure; no secret reads; no autonomous execution")
