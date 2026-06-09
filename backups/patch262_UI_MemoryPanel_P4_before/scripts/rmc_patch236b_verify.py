#!/usr/bin/env python3
"""Patch 236B verifier: static/package-level checks only."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
main = ROOT / "main.py"
registry = ROOT / "config" / "tool_registry.json"
text = main.read_text(encoding="utf-8")
reg = json.loads(registry.read_text(encoding="utf-8"))

required = [
    "forge-agent-verify-neo-activation",
    "forge-agent-verify-neo-activation-report",
    "NEO_ACTIVATION_VERIFIED_ACTIVE_GOVERNED",
    "P236B_VERIFY_JSON",
    "P236B_REQUIRED_236A_VERDICT",
    "Patch 236B — Neo Activation Verification",
]
missing = [s for s in required if s not in text]
if missing:
    print("PATCH236B_VERIFY_FAIL")
    print("missing_in_main=" + ", ".join(missing))
    sys.exit(1)

for cmd in ["forge-agent-verify-neo-activation", "forge-agent-verify-neo-activation-report"]:
    if cmd not in reg.get("tools", {}):
        print("PATCH236B_VERIFY_FAIL")
        print(f"missing_registry={cmd}")
        sys.exit(1)

for forbidden in [
    "CONFIRM_NEO_ACTIVE_GOVERNED\" in PATCH236B",
]:
    if forbidden in text:
        print("PATCH236B_VERIFY_FAIL")
        print("forbidden=" + forbidden)
        sys.exit(1)

print("PATCH236B_VERIFY_PASS")
print("commands=forge-agent-verify-neo-activation, forge-agent-verify-neo-activation-report")
print("boundary=read-only Neo activation verification; no Identity Vault DB write; no RMC memory write; no activation; no private memory exposure; no secret reads; no autonomous execution")
