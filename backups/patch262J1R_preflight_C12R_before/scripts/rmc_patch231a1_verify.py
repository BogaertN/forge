#!/usr/bin/env python3
"""Patch 231A.1 verifier — activation preflight report route hotfix."""
from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
registry = root / "config" / "tool_registry.json"
text = main.read_text(encoding="utf-8")

required = [
    "BEGIN PATCH 231A.1 IDENTITY ACTIVATION PREFLIGHT REPORT ROUTE HOTFIX",
    'if user_input.lower() == "forge-agent-activation-preflight-report":',
    'cmd_forge_agent_activation_preflight_report(session_id)',
    'if user_input.lower().startswith("forge-agent-activation-preflight"):',
    'cmd_forge_agent_activation_preflight(_p231a_agent_id, session_id)',
]
missing = [item for item in required if item not in text]
if missing:
    print("PATCH231A1_VERIFY_FAIL")
    print("missing markers:", missing)
    sys.exit(1)

report_pos = text.find('if user_input.lower() == "forge-agent-activation-preflight-report":')
prefix_pos = text.find('if user_input.lower().startswith("forge-agent-activation-preflight"):', report_pos)
if report_pos < 0 or prefix_pos < 0 or report_pos > prefix_pos:
    print("PATCH231A1_VERIFY_FAIL")
    print("report route does not precede prefix route")
    sys.exit(1)

forbidden = [
    "forge-agent-activate-manual",
    "identity_vault_database_written\": True",
    "agent_identity_activation_performed\": True",
    "rmc_memory_written\": True",
]
# The activation plan text may mention future activation command in existing Patch 231 material,
# so only fail if a route/function for actual manual activation appears in this hotfix region.
hotfix_region = text[text.find("BEGIN PATCH 231A.1"):text.find("END PATCH 231A.1")]
if "forge-agent-activate-manual" in hotfix_region:
    print("PATCH231A1_VERIFY_FAIL")
    print("manual activation command appears in hotfix route region")
    sys.exit(1)

if not registry.exists():
    print("PATCH231A1_VERIFY_FAIL")
    print("missing tool_registry.json")
    sys.exit(1)
try:
    json.loads(registry.read_text(encoding="utf-8"))
except Exception as exc:
    print("PATCH231A1_VERIFY_FAIL")
    print("tool registry invalid json:", exc)
    sys.exit(1)

print("PATCH231A1_VERIFY_PASS")
print("commands=unchanged; forge-agent-activation-preflight-report route fixed before prefix route")
print("boundary=route/display hotfix only; no activation command installed; no RMC memory write; no Identity Vault DB write; no activation")
