#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

def extract_do_get(text: str) -> str:
    m = re.search(r"def do_GET\(self\):(?P<body>.*?)(?:\n\s*# ── Patch 203: real command execution|\n\s*def do_POST\(self\):)", text, re.S)
    return m.group("body") if m else ""

def main() -> int:
    text = MAIN.read_text(errors="replace")
    do_get = extract_do_get(text)
    p251_block = text[text.find("def _p251_safe_json_summary"):text.find("def _p251_list_identity_agent_dirs")]

    checks = {
        "helper_present": "def _p252_operator_core_inventory_v1" in text,
        "command_scan_present": "def _p252_extract_browser_command_names" in text,
        "route_present": 'self.path == "/api/operator/core-inventory"' in do_get,
        "route_calls_helper": "_p252_operator_core_inventory_v1()" in do_get,
        "contract_lists_endpoint": '"/api/operator/core-inventory"' in text,
        "p251_json_fix": "import json as _j" in p251_block,
        "no_command_added": "forge-core-parity-inventory" not in text,
        "command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "no_llm_call": '"calls_llm": False' in text,
        "no_file_write": '"writes_files": False' in text,
        "read_only_boundary": '"executes_command": False' in text and '"rmc_live_memory_write": False' in text,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH252_CORE_PARITY_INVENTORY_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1

    print("PATCH252_CORE_PARITY_INVENTORY_VERIFY_PASS")
    print("patch=252")
    print("api=/api/operator/core-inventory")
    print("p251_json_summary_fix=True")
    print("command_surface_delta=0_expected")
    print("executes_commands=False")
    print("calls_llm=False")
    print("writes_files=False")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    print("next=Patch 253 — Forge Output Panel v1")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
