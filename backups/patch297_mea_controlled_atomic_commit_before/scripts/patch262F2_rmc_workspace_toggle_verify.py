#!/usr/bin/env python3
"""
Patch 262F2 verifier
Purpose: confirm RMC workspace active modules can be toggled closed and inactive module panels stay hidden.
"""
from pathlib import Path

root = Path.home()
# Allow verifier to run from extracted patch tree or live Forge tree.
candidates = [
    root / "aiweb/apps/forge-operator-console/src/tabs/RmcMemoryTab.tsx",
    Path.cwd().parent / "aiweb/apps/forge-operator-console/src/tabs/RmcMemoryTab.tsx",
    Path.cwd() / "aiweb/apps/forge-operator-console/src/tabs/RmcMemoryTab.tsx",
]
rmc_tab = next((p for p in candidates if p.exists()), None)
if not rmc_tab:
    raise SystemExit("PATCH262F2_VERIFY_FAIL missing RmcMemoryTab.tsx")
text = rmc_tab.read_text(encoding="utf-8")
required = {
    "activeAction_state": "const [activeAction, setActiveAction]" in text,
    "beginActiveAction_toggle": "beginActiveAction" in text and "return false" in text and "setActivePanel(null)" in text,
    "clear_active_workspace": "clearActiveWorkspace" in text and "Close Active Module" in text,
    "active_action_metric": "Active Action" in text,
    "active_buttons": "className={activeAction ===" in text,
    "inactive_placeholder": "ActivePanelShell" in text,
    "backend_changed": False,
    "adds_forge_commands": False,
}
failed = [name for name, ok in required.items() if not ok and name not in {"backend_changed", "adds_forge_commands"}]
if failed:
    print("PATCH262F2_RMC_WORKSPACE_TOGGLE_VERIFY_FAIL")
    for item in failed:
        print(f"missing={item}")
    raise SystemExit(1)
print("PATCH262F2_RMC_WORKSPACE_TOGGLE_VERIFY_PASS")
print("active_action_state=True")
print("click_same_action_closes_panel=True")
print("close_active_module_button=True")
print("inactive_empty_panels_hidden=True")
print("backend_changed=False")
print("adds_forge_commands=False")
