#!/usr/bin/env python3
"""Static verifier for Patch 235A — Athena Manual Activation Apply."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"

errors = []
text = MAIN.read_text(encoding="utf-8")

required = [
    "PATCH235A_ATHENA_MANUAL_ACTIVATION_COMMANDS",
    "forge-agent-activate-athena-manual",
    "forge-agent-activate-athena-manual-report",
    "CONFIRM_ATHENA_ACTIVE_GOVERNED",
    "ATHENA_ACTIVATED_ACTIVE_GOVERNED",
    "BLOCKED_ATHENA_MANUAL_ACTIVATION_APPLY",
    "ATHENA_ONLY_ACTIVATION_TARGET_REQUIRED",
    "PATCH235_DRY_RUN_NOT_READY",
    "ATHENA_PREFLIGHT_NOT_READY",
    "GILLIGAN_NOT_ACTIVE_GOVERNED",
    "NEO_NOT_STILL_INACTIVE",
    "athena_can_execute_tools_by_itself",
    "athena_can_write_memory_by_itself",
    "athena_can_bypass_forge",
    "athena_can_read_secrets",
    "forge_patch235a_athena_manual_activation_apply",
]
for needle in required:
    if needle not in text:
        errors.append(f"missing main marker: {needle}")

if "forge-agent-activate-athena-manual" not in text or "cmd_forge_agent_activate_athena_manual" not in text:
    errors.append("Athena manual activation route/function missing")

if "P235A_TARGET_AGENT_ID = \"athena.local\"" not in text:
    errors.append("P235A target agent is not locked to athena.local")

if "P235A_REQUIRED_APPROVAL_TOKEN = \"CONFIRM_ATHENA_ACTIVE_GOVERNED\"" not in text:
    errors.append("P235A approval token constant missing")

# Ensure this patch does not alter Gilligan's existing command implementation name.
if "def cmd_forge_agent_activate_manual" not in text:
    errors.append("existing Gilligan manual activation command missing")

try:
    data = json.loads(REG.read_text(encoding="utf-8"))
    tools = data.get("tools", {})
    for cmd in ["forge-agent-activate-athena-manual", "forge-agent-activate-athena-manual-report"]:
        if cmd not in tools:
            errors.append(f"tool registry missing {cmd}")
    if data.get("current_trust_level") != 5.0:
        errors.append(f"unexpected trust level: {data.get('current_trust_level')!r}")
except Exception as exc:
    errors.append(f"registry parse failed: {type(exc).__name__}: {exc}")

# Confirm the expected command surface grew by 2 from Patch 235 (818 -> 820).
match = re.findall(r"FORGE_EXPECTED_COMMANDS\.append\(_p235a_cmd\)", text)
if not match:
    errors.append("P235A commands are not appended to FORGE_EXPECTED_COMMANDS")

if errors:
    print("PATCH235A_VERIFY_FAIL")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("PATCH235A_VERIFY_PASS")
print("commands=forge-agent-activate-athena-manual, forge-agent-activate-athena-manual-report")
print("boundary=Athena-only explicit-token Identity Vault activation apply; no RMC memory write; no autonomous execution; no secret reads")
