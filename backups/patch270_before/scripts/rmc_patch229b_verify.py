#!/usr/bin/env python3
"""Patch 229B static verifier.

Checks the shipped files contain the verification-only command surface and
expected boundary strings. It does not read or write live RMC memory.
"""
from pathlib import Path
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"

required_strings = [
    "forge-rmc-namespace-scaffold-verify",
    "forge-rmc-namespace-scaffold-verify-report",
    "cmd_forge_rmc_namespace_scaffold_verify",
    "cmd_forge_rmc_namespace_scaffold_verify_report",
    "rmc_patch229b_namespace_scaffold_verify_v1",
    "VERIFIED_NAMESPACE_SCAFFOLD_DIRECTORIES_ONLY",
    "No RMC memory write",
    "no Identity Vault DB write",
    "no activation",
]

try:
    py_compile.compile(str(MAIN), doraise=True)
except Exception as exc:
    print(f"PATCH229B_VERIFY_FAIL py_compile main.py: {exc}")
    sys.exit(1)

try:
    json.loads(REGISTRY.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"PATCH229B_VERIFY_FAIL tool_registry invalid JSON: {exc}")
    sys.exit(1)

text = MAIN.read_text(encoding="utf-8")
missing = [item for item in required_strings if item not in text]
if missing:
    print("PATCH229B_VERIFY_FAIL missing markers:")
    for item in missing:
        print(f"- {item}")
    sys.exit(1)

print("PATCH229B_VERIFY_PASS")
print("commands=forge-rmc-namespace-scaffold-verify, forge-rmc-namespace-scaffold-verify-report")
print("boundary=verification only; no new RMC directory creation; no RMC memory write; no Identity Vault DB write; no activation")
