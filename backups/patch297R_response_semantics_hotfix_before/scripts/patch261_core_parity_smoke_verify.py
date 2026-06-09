#!/usr/bin/env python3
"""Patch 261 verifier: Operator Console Core Parity Smoke Test."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
registry = root / "config" / "tool_registry.json"
text = main.read_text(encoding="utf-8", errors="replace")

required = [
    "PATCH 261 — OPERATOR CONSOLE CORE PARITY SMOKE TEST V1",
    "def _p261_operator_core_parity_smoke_v1()",
    '"endpoint": "/api/operator/core-parity-smoke"',
    '"mode": "read_only_core_parity_smoke_test"',
    'elif self.path == "/api/operator/core-parity-smoke":',
    "_p261_operator_core_parity_smoke_v1",
    '"next_patch": "Patch 262 — RMC Memory Panel v1"',
    '"executes_command": False',
    '"executes_shell": False',
    '"writes_files": False',
    '"identity_vault_write": False',
    '"rmc_live_memory_write": False',
    '"adds_forge_commands": False',
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("PATCH261_VERIFY_FAIL missing markers: " + ", ".join(missing))

# Verify no command-surface additions: endpoint is API only, not a Forge CLI command.
expected_block = ""
match = re.search(r"FORGE_EXPECTED_COMMANDS\s*=\s*\[(?P<body>.*?)\n\]", text, re.S)
if match:
    expected_block = match.group("body")
if "core-parity-smoke" in expected_block:
    raise SystemExit("PATCH261_VERIFY_FAIL endpoint leaked into FORGE_EXPECTED_COMMANDS")

reg = json.loads(registry.read_text(encoding="utf-8"))
trust = reg.get("current_trust_level")
if str(trust) not in {"5", "5.0"}:
    raise SystemExit(f"PATCH261_VERIFY_FAIL current_trust_level={trust!r}")

print("PATCH261_CORE_PARITY_SMOKE_VERIFY_PASS")
print("endpoint=/api/operator/core-parity-smoke")
print("mode=read_only_core_parity_smoke_test")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
print("next_patch=Patch 262 — RMC Memory Panel v1")
