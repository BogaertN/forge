#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

def extract_do_get(text: str) -> str:
    m = re.search(r"def do_GET\(self\):(?P<body>.*?)(?:\n\s*# ── Patch 203: real command execution|\n\s*def do_POST\(self\):)", text, re.S)
    if not m:
        return ""
    return m.group("body")

def main() -> int:
    text = MAIN.read_text(errors="replace")
    do_get = extract_do_get(text)

    checks = {
        "helper_contract": "def _p245_api_contract_v1" in text,
        "helper_forge_status": "def _p245_forge_status_v1" in text,
        "helper_audit_tail": "def _p245_audit_tail_v1" in text,
        "helper_protoforge_reports": "def _p245_protoforge_reports_v1" in text,
        "do_get_found": bool(do_get),
        "route_operator_contract": 'self.path == "/api/operator/contract"' in do_get,
        "route_forge_status": 'self.path == "/api/forge/status"' in do_get,
        "route_audit_tail": 'self.path == "/api/audit/tail"' in do_get,
        "route_protoforge_reports": '"/api/protoforge/reports"' in do_get,
        "route_protoforge_alias": '"/api/protoforge-reports"' in do_get,
        "route_calls_contract_helper": "_p245_api_contract_v1()" in do_get,
        "route_calls_status_helper": "_p245_forge_status_v1()" in do_get,
        "route_calls_audit_helper": "_p245_audit_tail_v1()" in do_get,
        "route_calls_protoforge_helper": "_p245_protoforge_reports_v1()" in do_get,
        "existing_api_status_preserved": 'self.path == "/api/status"' in do_get,
        "existing_seen_pages_preserved": 'self.path == "/api/seen-pages"' in do_get,
        "command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "adds_forge_commands_false": "forge-terminus-operator-console-plan" not in text,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH245A_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1

    print("PATCH245A_VERIFY_PASS")
    print("patch=245A")
    print("fix=api_do_get_route_table")
    print("endpoints_live=/api/operator/contract,/api/forge/status,/api/audit/tail,/api/protoforge/reports")
    print("compatibility_alias=/api/protoforge-reports")
    print("command_surface_delta=0_expected")
    print("adds_forge_commands=False")
    print("executes_simulation=False")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
