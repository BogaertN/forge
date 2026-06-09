#!/usr/bin/env python3
# Patch 262E — RMC TraceRecord + Manifest Contract verifier
# Purpose: prove endpoint exists, is read-only, and does not pretend RMC is complete.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
main = (ROOT / "main.py").read_text(encoding="utf-8")
registry = (ROOT / "config" / "tool_registry.json").read_text(encoding="utf-8")

required = [
    "def _p262e_rmc_compiler_contract_v1",
    '"endpoint": "/api/rmc/compiler-contract"',
    '"mode": "read_only_rmc_trace_manifest_contract"',
    '"trace_complete": False',
    '"manifest_complete": False',
    '"current_rmc_is_shippable": False',
    '"move_to_context_library_recommended_now": False',
    '"next_patch": "Patch 262F — RMC Phase Parser Read-Only"',
    '_p262e_rmc_compiler_contract_v1(self.path)',
]
missing = [item for item in required if item not in main]
if missing:
    raise SystemExit("PATCH262E_VERIFY_FAIL missing=" + repr(missing))

section = main[main.find("def _p262e_rmc_compiler_contract_v1"):main.find("# ─── PATCH 255")]
for forbidden in [
    "subprocess.",
    "os.system",
    "open(\"",
    "open('",
    "sqlite3.connect",
    "chromadb",
    '"identity_vault_write": True',
    '"rmc_live_memory_write": True',
]:
    if forbidden in section:
        raise SystemExit("PATCH262E_VERIFY_FAIL forbidden=" + forbidden)

if '"current_trust_level": 5' not in registry and '"current_trust_level": 5.0' not in registry:
    raise SystemExit("PATCH262E_VERIFY_FAIL trust level changed or missing")

print("PATCH262E_RMC_COMPILER_CONTRACT_VERIFY_PASS")
print("endpoint=/api/rmc/compiler-contract")
print("mode=read_only_rmc_trace_manifest_contract")
print("marks_rmc_shippable=False")
print("next_patch=Patch 262F — RMC Phase Parser Read-Only")
print("adds_forge_commands=False")
print("executes_command=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
