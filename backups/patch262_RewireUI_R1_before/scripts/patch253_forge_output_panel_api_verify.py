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

    checks = {
        "helper_present": "def _p253_operator_output_state_v1" in text,
        "route_present": 'self.path == "/api/operator/output-state"' in do_get,
        "route_calls_helper": "_p253_operator_output_state_v1()" in do_get,
        "contract_lists_endpoint": '"/api/operator/output-state"' in text,
        "uses_status": "_p245_forge_status_v1()" in text,
        "uses_audit": "_p245_audit_tail_v1(max_lines=30)" in text,
        "uses_inventory": "_p252_operator_core_inventory_v1()" in text,
        "command_execution_disabled": '"command_execution_enabled": False' in text,
        "llm_execution_disabled": '"llm_execution_enabled": False' in text,
        "no_command_added": "forge-output-panel" not in text,
        "command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "no_llm_call": '"calls_llm": False' in text,
        "no_file_write": '"writes_files": False' in text,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH253_FORGE_OUTPUT_PANEL_API_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1

    print("PATCH253_FORGE_OUTPUT_PANEL_API_VERIFY_PASS")
    print("patch=253")
    print("api=/api/operator/output-state")
    print("command_surface_delta=0_expected")
    print("executes_commands=False")
    print("calls_llm=False")
    print("writes_files=False")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    print("next=Patch 254 — Safe Command Runner Bridge")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
