#!/usr/bin/env python3
"""Patch 255 verifier — Operator LLM / Natural-Language Request Bridge v1.

Checks source wiring only. Does not call Ollama, does not start Forge, does not
execute shell through Forge, and does not write Identity Vault/RMC memory.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

text = MAIN.read_text(encoding="utf-8", errors="replace")
errors = []

required = [
    "PATCH 255 — OPERATOR LLM / NATURAL-LANGUAGE REQUEST BRIDGE V1",
    "def _p255_operator_llm_request_v1",
    "def _p255_llm_boundary",
    '"/api/operator/llm-request"',
    '"mode": "forge_governed_plan_only"',
    "_p199_call_planner(request)",
    '"returns_proposal_only": True',
    '"executes_shell": False',
    '"writes_files": False',
    '"identity_vault_write": False',
    '"rmc_live_memory_write": False',
]

for needle in required:
    if needle not in text:
        errors.append(f"missing required marker: {needle}")

patch_block = text.split("# ─── PATCH 255 — OPERATOR LLM / NATURAL-LANGUAGE REQUEST BRIDGE V1", 1)[-1]
patch_block = patch_block.split("def _p201_make_handler", 1)[0]
for forbidden in ["subprocess", "os.system", "Popen(", "write_text(", "open("]:
    if forbidden in patch_block:
        errors.append(f"forbidden direct side-effect marker in Patch 255 block: {forbidden}")

route_order = text.find('elif self.path == "/api/operator/llm-request":')
command_route = text.find('elif self.path == "/api/command":')
if route_order == -1 or command_route == -1 or route_order > command_route:
    errors.append("/api/operator/llm-request route missing or placed after /api/command")

if "FORGE_EXPECTED_COMMANDS.append" in patch_block:
    errors.append("Patch 255 must not add Forge CLI commands")

if errors:
    print("PATCH255_LLM_REQUEST_BRIDGE_VERIFY_FAIL")
    for err in errors:
        print(f"- {err}")
    sys.exit(1)

print("PATCH255_LLM_REQUEST_BRIDGE_VERIFY_PASS")
print("endpoint=/api/operator/llm-request")
print("mode=forge_governed_plan_only")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
print("returns_proposal_only=True")
