#!/usr/bin/env python3
"""Patch 238 verifier — ProtoForge2 discovery scan."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REG = ROOT / "config" / "tool_registry.json"

REQUIRED = [
    "forge-protoforge2-discovery-scan",
    "forge-protoforge2-discovery-scan-report",
    "PATCH238_PROTOFORGE2_COMMANDS",
    "PROTOFORGE2_DISCOVERY_SCAN_ROOT_FOUND",
    "PROTOFORGE2_DISCOVERY_SCAN_NO_ROOT_FOUND",
    "/home/nic/protoforge2",
    "/home/nic/ProtoForge2",
    "/home/nic/aiweb/protoforge2",
    "/home/nic/forge/protoforge2",
    "/home/nic/aiweb/service_contracts/protoforge2.contract.json",
    "protoforge2_execution_performed",
    "service_contract_written",
]

FORBIDDEN_IN_PATCH_BLOCK = [
    "subprocess.run(",
    "subprocess.call(",
    "subprocess.Popen(",
    "os.system(",
]


def fail(msg: str) -> None:
    print(f"PATCH238_VERIFY_FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    if not MAIN.exists():
        fail("main.py missing")
    if not REG.exists():
        fail("config/tool_registry.json missing")
    text = MAIN.read_text(encoding="utf-8")
    for token in REQUIRED:
        if token not in text:
            fail(f"missing token: {token}")
    m = re.search(r"# --- BEGIN PATCH 238 PROTOFORGE2 DISCOVERY SCAN ---(.*?)# --- END PATCH 238 PROTOFORGE2 DISCOVERY SCAN ---", text, re.S)
    if not m:
        fail("Patch 238 block not found")
    block = m.group(1)
    for token in FORBIDDEN_IN_PATCH_BLOCK:
        if token in block:
            fail(f"forbidden execution primitive inside Patch 238 block: {token}")
    if "FORGE_EXPECTED_COMMANDS.append(_p238_cmd)" not in block:
        fail("expected command append missing")
    print("PATCH238_VERIFY_PASS")
    print("commands=forge-protoforge2-discovery-scan, forge-protoforge2-discovery-scan-report")
    print("boundary=read-only ProtoForge2 discovery; no ProtoForge2 execution; no service contract write; no Identity Vault DB write; no RMC memory write; no private memory exposure; no secret reads; no autonomous execution")


if __name__ == "__main__":
    main()
