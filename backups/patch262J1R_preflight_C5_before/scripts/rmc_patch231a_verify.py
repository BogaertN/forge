#!/usr/bin/env python3
"""Patch 231A static verifier."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
main = (ROOT / "main.py").read_text(encoding="utf-8")
registry = json.loads((ROOT / "config" / "tool_registry.json").read_text(encoding="utf-8"))
required = [
    "forge-agent-activation-preflight",
    "forge-agent-activation-preflight-report",
    "READY_FOR_MANUAL_ACTIVATION",
    "BLOCKED_ACTIVATION_PREFLIGHT_",
    "AGENT_PERMISSIONS_MISSING",
    "AGENT_FORBIDDEN_ACTIONS_MISSING",
    "PROFILE_HASH_INVALID_OR_MISSING",
    "SERVICE_CONTRACTS_MISSING_OR_INVALID",
    "P231A_ACTIVATION_PREFLIGHT_REPORT_DIR",
    "agent_identity_activation_performed\": False",
    "identity_vault_database_written\": False",
    "rmc_memory_written\": False",
]
missing = [item for item in required if item not in main]
if missing:
    raise SystemExit("PATCH231A_VERIFY_FAIL missing markers: " + ", ".join(missing))
for tool in ("forge_agent_activation_preflight", "forge_agent_activation_preflight_report"):
    if tool not in registry.get("tools", {}):
        raise SystemExit(f"PATCH231A_VERIFY_FAIL missing registry tool: {tool}")
if registry.get("current_trust_level") != 5.0:
    raise SystemExit("PATCH231A_VERIFY_FAIL trust level changed")
if "forge-agent-activate-manual" in main and "manual_activation_command_future_patch" not in main:
    raise SystemExit("PATCH231A_VERIFY_FAIL activation command appears installed unexpectedly")
print("PATCH231A_VERIFY_PASS")
print("commands=forge-agent-activation-preflight, forge-agent-activation-preflight-report")
print("boundary=read-only preflight; no activation command installed; no RMC memory write; no Identity Vault DB write; no activation")
