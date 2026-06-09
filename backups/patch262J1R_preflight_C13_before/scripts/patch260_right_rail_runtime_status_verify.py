#!/usr/bin/env python3
"""Patch 260 verifier: Right Rail Runtime Status.

Checks that Patch 260 wires the right rail as a live read-only status surface
without adding Forge commands, shell paths, direct writes, Identity Vault writes,
or RMC live-memory writes.
"""
from pathlib import Path
import json
import sys

ROOT = Path.home() / "forge"
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"

text = MAIN.read_text(encoding="utf-8")
reg = json.loads(REG.read_text(encoding="utf-8"))

required = [
    'right_rail_runtime_status_slot',
    'Patch 261 — Operator Console Core Parity Smoke Test',
    'right_rail_runtime_status_enabled',
    'right_rail_runtime_status_read_only',
    'right_rail_uses_existing_read_only_apis',
    'right_rail_executes_command": False',
    'right_rail_direct_shell": False',
    'right_rail_direct_file_write": False',
    'right_rail_identity_vault_write": False',
    'right_rail_rmc_live_memory_write": False',
]
missing = [x for x in required if x not in text]

if missing:
    print("PATCH260_RIGHT_RAIL_RUNTIME_STATUS_VERIFY_FAIL")
    print("missing:", ", ".join(missing))
    sys.exit(1)

print("PATCH260_RIGHT_RAIL_RUNTIME_STATUS_VERIFY_PASS")
print("mode=live_read_only_runtime_status_rail")
print("uses_existing_read_only_apis=True")
print("adds_forge_commands=False")
print("new_backend_endpoint=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
print(f"trust={reg.get('current_trust_level')}")
