#!/usr/bin/env python3
"""Patch 229 local verifier.
Checks that command markers exist and Patch 229 report commands are registered.
Does not create RMC folders, does not write Identity Vault DB, and does not activate agents.
"""
from __future__ import annotations
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
registry = root / "config" / "tool_registry.json"
text = main.read_text(encoding="utf-8")
reg = json.loads(registry.read_text(encoding="utf-8"))
needles = [
    "forge-rmc-namespace-scaffold-preview",
    "forge-rmc-namespace-scaffold-report",
    "RMC_NAMESPACE_SCAFFOLD_PREVIEW_WRITTEN",
    "rmc_patch229_namespace_scaffold_preview_v1",
]
missing = [n for n in needles if n not in text]
missing_tools = [
    key for key in [
        "forge_rmc_namespace_scaffold_preview",
        "forge_rmc_namespace_scaffold_report",
    ] if key not in reg.get("tools", {})
]
if missing or missing_tools:
    print("PATCH229_VERIFY_FAIL")
    if missing:
        print("missing_main_markers=", missing)
    if missing_tools:
        print("missing_registry_tools=", missing_tools)
    raise SystemExit(1)
print("PATCH229_VERIFY_PASS")
print("commands=forge-rmc-namespace-scaffold-preview, forge-rmc-namespace-scaffold-report")
print("boundary=no RMC memory write, no Identity Vault DB write, no activation")
