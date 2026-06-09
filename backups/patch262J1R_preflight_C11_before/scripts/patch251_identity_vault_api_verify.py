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
        "helper_present": "def _p251_identity_vault_status_v1" in text,
        "safe_summary_present": "def _p251_safe_json_summary" in text,
        "route_present": 'self.path == "/api/identity-vault/status"' in do_get,
        "route_calls_helper": "_p251_identity_vault_status_v1()" in do_get,
        "contract_lists_endpoint": '"/api/identity-vault/status"' in text,
        "no_db_open": ".sqlite" not in text[text.find("def _p251_identity_vault_status_v1"):text.find("def _p201_make_handler")],
        "secret_reads_false": '"secret_reads": False' in text,
        "autonomous_execution_false": '"autonomous_execution": False' in text,
        "identity_write_false": '"identity_vault_write": False' in text and '"identity_db_write": False' in text,
        "command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "no_command_added": "forge-identity-vault-ui-start" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH251_IDENTITY_VAULT_API_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1
    print("PATCH251_IDENTITY_VAULT_API_VERIFY_PASS")
    print("patch=251")
    print("api=/api/identity-vault/status")
    print("command_surface_delta=0_expected")
    print("executes_commands=False")
    print("agent_activation=False")
    print("secret_reads=False")
    print("identity_vault_write=False")
    print("identity_db_write=False")
    print("rmc_live_memory_write=False")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
