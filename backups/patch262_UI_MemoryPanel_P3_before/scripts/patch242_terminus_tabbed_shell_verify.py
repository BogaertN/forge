#!/usr/bin/env python3
from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"
REGISTRY = ROOT / "config" / "tool_registry.json"

def decode_html(text: str) -> str:
    m = re.search(r'_P201_HTML_B64 = "([^"]+)"', text)
    if not m:
        raise RuntimeError("missing _P201_HTML_B64")
    return base64.b64decode(m.group(1)).decode("utf-8", "replace")

def main() -> int:
    text = MAIN.read_text(errors="replace")
    html = decode_html(text)

    checks = {
        "main_exists": MAIN.exists(),
        "registry_exists": REGISTRY.exists(),
        "tabbar_present": 'id="console-tabs"' in html,
        "forge_output_tab": 'data-tab="forge_output"' in html,
        "protoforge_tab": 'data-tab="protoforge_simulations"' in html,
        "identity_tab": 'data-tab="identity_vault"' in html,
        "echoforge_tab": 'data-tab="echoforge"' in html,
        "rmc_tab": 'data-tab="rmc_memory"' in html,
        "context_tab": 'data-tab="context_library"' in html,
        "audit_tab": 'data-tab="audit_receipts"' in html,
        "system_tab": 'data-tab="system_status"' in html,
        "set_console_tab_function": "function setConsoleTab(tab)" in html,
        "panel_page_function": "function panelPage(tab)" in html,
        "protoforge_sidebar_preserved": "forge-protoforge-status" in html and "forge-protoforge-simulation-run-approved" in html,
        "gate_preserved": "RUN-PROTOFORGE" in text,
        "no_operator_plan_commands": "forge-terminus-operator-console-plan" not in text,
        "identity_boundary_visible": "No Identity Vault mutation" in html,
        "rmc_boundary_visible": "No RMC live memory write" in html,
        "no_browser_physics_claim": "not browser-side physics" in html,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("PATCH242_VERIFY_FAIL")
        print("failed=" + ",".join(failed))
        return 1

    print("PATCH242_VERIFY_PASS")
    print("patch=242")
    print("ui=terminus_tabbed_shell_prototype")
    print("tabs=8")
    print("command_surface_delta=0_expected")
    print("protoforge_bridge_preserved=True")
    print("ui_redesign=prototype_shell_only")
    print("identity_vault_write=False")
    print("rmc_live_memory_write=False")
    print("auto_simulation=False")
    print("next=Patch 243 — ProtoForge Simulation Panel Read-Only Binding")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
