#!/usr/bin/env python3
"""Patch 229A verifier: static/runtime-surface checks only; no scaffold apply."""
from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"
CONNECTOR = ROOT / "agents" / "forge" / "aiweb_readonly_connectors.py"

required_main_markers = [
    "forge-rmc-namespace-scaffold-apply",
    "forge-rmc-namespace-scaffold-apply-report",
    "cmd_forge_rmc_namespace_scaffold_apply",
    "cmd_forge_rmc_namespace_scaffold_apply_report",
    "P229A_RMC_NAMESPACE_APPLY_REPORT_DIR",
    "APPLIED_NAMESPACE_SCAFFOLD_DIRECTORIES_ONLY",
    "REFUSED_UNSAFE_SCAFFOLD_PATHS",
    '"rmc_memory_written": False',
    '"identity_vault_database_written": False',
    '"agent_identity_activation_performed": False',
]

main_text = MAIN.read_text(encoding="utf-8")
missing = [marker for marker in required_main_markers if marker not in main_text]
if missing:
    print("PATCH229A_VERIFY_FAIL")
    print("missing_main_markers=" + ", ".join(missing))
    sys.exit(1)

with REGISTRY.open("r", encoding="utf-8") as fh:
    registry = json.load(fh)

tools = registry.get("tools", {})
for name in ["forge_rmc_namespace_scaffold_apply", "forge_rmc_namespace_scaffold_apply_report"]:
    if name not in tools:
        print("PATCH229A_VERIFY_FAIL")
        print(f"missing_registry_tool={name}")
        sys.exit(1)

if registry.get("current_trust_level") != 5.0:
    print("PATCH229A_VERIFY_FAIL")
    print("current_trust_level_not_5_0")
    sys.exit(1)

for target in [MAIN, CONNECTOR, Path(__file__)]:
    py_compile.compile(str(target), doraise=True)

print("PATCH229A_VERIFY_PASS")
print("commands=forge-rmc-namespace-scaffold-apply, forge-rmc-namespace-scaffold-apply-report")
print("boundary=directories only from Patch 229 preview; no RMC memory write; no Identity Vault DB write; no activation")
