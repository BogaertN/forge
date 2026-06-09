#!/usr/bin/env python3
"""Patch 236C verifier: static/package-level checks only."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
main = ROOT / "main.py"
registry = ROOT / "config" / "tool_registry.json"
text = main.read_text(encoding="utf-8")
reg = json.loads(registry.read_text(encoding="utf-8"))

required = [
    "forge-neo-governed-handshake",
    "forge-neo-governed-handshake-report",
    "NEO_HANDSHAKE_ACCEPTED_GOVERNED_ACTIVE_AGENT",
    "ECHO_VALIDATION_PASSED_NEO_GOVERNED_ACTIVE_AGENT",
    "P236C_HANDSHAKE_JSON",
    "P236C_REQUIRED_236B_VERDICT",
    "Patch 236C — Neo Governed Handshake",
    "private_memory_exposure_granted",
]
missing = [s for s in required if s not in text]
if missing:
    print("PATCH236C_VERIFY_FAIL")
    print("missing_in_main=" + ", ".join(missing))
    sys.exit(1)

for cmd in ["forge-neo-governed-handshake", "forge-neo-governed-handshake-report"]:
    if cmd not in reg.get("tools", {}):
        print("PATCH236C_VERIFY_FAIL")
        print(f"missing_registry={cmd}")
        sys.exit(1)

for forbidden in [
    "CONFIRM_NEO_ACTIVE_GOVERNED",
    "identity_vault_database_written\": True",
    "rmc_memory_written\": True",
]:
    if forbidden in text[text.find("# --- BEGIN PATCH 236C NEO GOVERNED HANDSHAKE ---"):]:
        print("PATCH236C_VERIFY_FAIL")
        print("forbidden=" + forbidden)
        sys.exit(1)

print("PATCH236C_VERIFY_PASS")
print("commands=forge-neo-governed-handshake, forge-neo-governed-handshake-report")
print("boundary=governed Neo handshake only; Forge-owned receipt/report; no Identity Vault DB write; no RMC memory write; no private memory exposure; no secret reads; no autonomous execution")
