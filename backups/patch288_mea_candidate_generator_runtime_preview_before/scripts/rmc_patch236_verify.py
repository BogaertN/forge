#!/usr/bin/env python3
"""Static verifier for Patch 236 — Neo Manual Activation Dry-Run Gate."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"

main_text = MAIN.read_text(encoding="utf-8")
registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
tools = registry.get("tools", {})

required_tokens = [
    "PATCH236_NEO_ACTIVATION_DRY_RUN_COMMANDS",
    '"forge-agent-activate-neo-dry-run"',
    '"forge-agent-activate-neo-dry-run-report"',
    "cmd_forge_agent_activate_neo_dry_run",
    "cmd_forge_agent_activate_neo_dry_run_report",
    "_p236_build_neo_activation_dry_run",
    "NEO_MANUAL_ACTIVATION_DRY_RUN_READY",
    "NEO_MANUAL_ACTIVATION_DRY_RUN_BLOCKED",
    "P236_REQUIRED_PATCH235F_VERDICT",
    "RMC_TEST_RECEIPT_VERIFIED_GOVERNED_ATHENA",
    "No RMC memory write, no Identity Vault DB write, no activation, no secret reads.",
]

missing = [tok for tok in required_tokens if tok not in main_text]
if missing:
    raise SystemExit(f"PATCH236_VERIFY_FAIL missing main.py tokens: {missing}")

for command in ["forge-agent-activate-neo-dry-run", "forge-agent-activate-neo-dry-run-report"]:
    if command not in main_text:
        raise SystemExit(f"PATCH236_VERIFY_FAIL command missing from main.py: {command}")

for tool_name in ["forge_agent_activate_neo_dry_run", "forge_agent_activate_neo_dry_run_report"]:
    if tool_name not in tools:
        raise SystemExit(f"PATCH236_VERIFY_FAIL tool_registry missing: {tool_name}")

section_start = main_text.find("# --- BEGIN PATCH 236 NEO MANUAL ACTIVATION DRY-RUN GATE ---")
section_end = main_text.find("# --- END PATCH 236 NEO MANUAL ACTIVATION DRY-RUN GATE ---")
if section_start < 0 or section_end < 0 or section_end <= section_start:
    raise SystemExit("PATCH236_VERIFY_FAIL Patch 236 section markers missing")
patch236_section = main_text[section_start:section_end]
for forbidden in [
    "forge-agent-activate-neo-manual",
    "NEO_ACTIVATED_ACTIVE_GOVERNED",
    "UPDATE identity_profiles SET activation_state",
    "identity_vault_database_written\": True",
    "rmc_memory_written\": True",
    "agent_identity_activation_performed\": True",
    "secret_reads_granted\": True",
    "autonomous_execution\": True",
]:
    if forbidden in patch236_section:
        raise SystemExit(f"PATCH236_VERIFY_FAIL forbidden Patch 236 activation/write token present: {forbidden}")

print("PATCH236_VERIFY_PASS")
print("commands=forge-agent-activate-neo-dry-run, forge-agent-activate-neo-dry-run-report")
print("boundary=Neo activation dry-run only; no Identity Vault DB write; no RMC memory write; no activation; no secret reads; no autonomous execution")
