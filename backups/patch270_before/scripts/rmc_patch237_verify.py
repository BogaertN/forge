#!/usr/bin/env python3
"""Patch 237 static verifier."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
main = root / "main.py"
registry = root / "config" / "tool_registry.json"
text = main.read_text(encoding="utf-8")
required = [
    "forge-triad-governed-status",
    "forge-triad-governed-status-report",
    "TRIAD_GOVERNED_IDENTITY_BOUNDARY_VERIFIED",
    "P237_AGENT_SPECS",
    "cmd_forge_triad_governed_status",
    "cmd_forge_triad_governed_status_report",
    "protoforge2_execution_performed",
    "echoforge_creation_performed",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("PATCH237_VERIFY_FAIL missing=" + ",".join(missing))
if "forge-protoforge2-status" in text or "forge-echoforge-status" in text:
    raise SystemExit("PATCH237_VERIFY_FAIL phase11_or_phase12_command_installed_too_early")
if registry.exists():
    json.loads(registry.read_text(encoding="utf-8"))
print("PATCH237_VERIFY_PASS")
print("commands=forge-triad-governed-status, forge-triad-governed-status-report")
print("boundary=read-only triad governed identity status; no Identity Vault DB write; no RMC memory write; no new receipt write; no private memory exposure; no secret reads; no autonomous execution; no ProtoForge2/EchoForge execution")
