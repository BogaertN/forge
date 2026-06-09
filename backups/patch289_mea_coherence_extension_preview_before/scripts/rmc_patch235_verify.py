#!/usr/bin/env python3
"""Static verifier for Patch 235 — Athena Manual Activation Dry-Run Gate."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
main = ROOT / "main.py"
registry = ROOT / "config" / "tool_registry.json"

main_text = main.read_text(encoding="utf-8")
reg = json.loads(registry.read_text(encoding="utf-8"))
errors = []

required_commands = [
    "forge-agent-activate-athena-dry-run",
    "forge-agent-activate-athena-dry-run-report",
]
for cmd in required_commands:
    if cmd not in main_text:
        errors.append(f"missing command text in main.py: {cmd}")
    if cmd not in reg.get("tools", {}):
        errors.append(f"missing tool registry entry: {cmd}")

for marker in [
    "PATCH235_ATHENA_ACTIVATION_DRY_RUN_COMMANDS",
    "ATHENA_MANUAL_ACTIVATION_DRY_RUN_READY",
    "aiweb_patch235_athena_manual_activation_dry_run_v1",
    "forge_owned_dry_run_report",
    '"identity_vault_database_written": False',
    '"agent_identity_activation_performed": False',
    "Patch 235 — Athena Manual Activation Dry-Run Gate",
    "forbidden_tool_execution",
    "allowed_boundary_checks",
]:
    if marker not in main_text:
        errors.append(f"missing marker in main.py: {marker}")

for forbidden in [
    "sqlite3.connect(str(P235",  # Patch 235 must not open DB for writing.
    "ATHENA_ACTIVATED_ACTIVE_GOVERNED",
    "forge-agent-activate-athena-manual",
]:
    if forbidden in main_text:
        errors.append(f"forbidden Patch 235 activation/write marker found: {forbidden}")

if "current_trust_level" not in reg or float(reg.get("current_trust_level")) != 5.0:
    errors.append("current_trust_level must remain 5.0")

if errors:
    print("PATCH235_VERIFY_FAIL")
    for err in errors:
        print(f"- {err}")
    sys.exit(1)

print("PATCH235_VERIFY_PASS")
print("commands=forge-agent-activate-athena-dry-run, forge-agent-activate-athena-dry-run-report")
print("boundary=Athena activation dry-run only; no Identity Vault DB write; no RMC memory write; no activation; no autonomous execution")
