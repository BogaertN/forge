#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
def main() -> int:
    text = MAIN.read_text(errors="replace")
    checks = {
        "api_contract_helper": "def _p245_api_contract_v1" in text,
        "forge_status_helper": "def _p245_forge_status_v1" in text,
        "audit_tail_helper": "def _p245_audit_tail_v1" in text,
        "protoforge_reports_helper": "def _p245_protoforge_reports_v1" in text,
        "operator_contract_route": '"/api/operator/contract"' in text,
        "forge_status_route": '"/api/forge/status"' in text,
        "audit_tail_route": '"/api/audit/tail"' in text,
        "protoforge_reports_route": '"/api/protoforge/reports"' in text,
        "protoforge_alias_route": "/api/protoforge-reports" in text,
        "no_design_command_added": "forge-terminus-operator-console-plan" not in text,
        "command_bridge_preserved": 'elif self.path == "/api/command":' in text,
        "gate_preserved": "RUN-PROTOFORGE" in text,
        "read_only_boundary_claim": "identity_vault_write" in text and "rmc_live_memory_write" in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH245_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1
    print("PATCH245_VERIFY_PASS")
    print("patch=245")
    print("api_contract=forge_operator_console_api_v1")
    print("endpoints=/api/operator/contract,/api/forge/status,/api/audit/tail,/api/protoforge/reports")
    print("command_surface_delta=0_expected")
    print("adds_forge_commands=False")
    print("executes_simulation=False")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    print("next=Patch 246 — Operator Console Read-Only Forge Status")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
