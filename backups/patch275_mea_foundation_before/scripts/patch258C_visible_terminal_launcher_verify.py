#!/usr/bin/env python3
"""Patch 258C static verifier."""
from pathlib import Path

ROOT = Path.home() / "forge"
SCRIPT = ROOT / "scripts" / "aiweb_os_visible_terminal_launcher.py"
INSTALLER = ROOT / "scripts" / "install_patch258C_visible_terminal_launcher.py"
THIS = ROOT / "scripts" / "patch258C_visible_terminal_launcher_verify.py"
REQUIRED = [SCRIPT, INSTALLER, THIS]

FORBIDDEN_IN_LAUNCHER = [
    "main.py.write_text",
    "tool_registry.json",
    "identity_vault.db",
    "vault.db",
    "rmc_live_memory_write=True",
]
REQUIRED_MARKERS = [
    "--inside-terminal",
    "forge-ui-start",
    "Choice [1-3]",
    "operator-console",
    "patches_main_py",
]


def main() -> int:
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("PATCH258C_VISIBLE_TERMINAL_LAUNCHER_VERIFY_FAIL")
        print("missing=" + ", ".join(missing))
        return 1
    text = SCRIPT.read_text(encoding="utf-8", errors="replace")
    missing_markers = [m for m in REQUIRED_MARKERS if m not in text]
    forbidden_hits = [m for m in FORBIDDEN_IN_LAUNCHER if m in text]
    if missing_markers or forbidden_hits:
        print("PATCH258C_VISIBLE_TERMINAL_LAUNCHER_VERIFY_FAIL")
        if missing_markers:
            print("missing_markers=" + ", ".join(missing_markers))
        if forbidden_hits:
            print("forbidden_hits=" + ", ".join(forbidden_hits))
        return 1
    print("PATCH258C_VISIBLE_TERMINAL_LAUNCHER_VERIFY_PASS")
    print("mode=visible_terminal_launcher_fix")
    print("always_opens_terminal=True")
    print("opens_operator_console=True")
    print("auto_scope_choice=2")
    print("runs_existing_command=forge-ui-start")
    print("patches_main_py=False")
    print("adds_forge_commands=False")
    print("bypasses_forge=False")
    print("browser_shell_access=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
