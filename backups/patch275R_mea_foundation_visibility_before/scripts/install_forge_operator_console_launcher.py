#!/usr/bin/env python3
# PATCH258A: Desktop launcher installer for AI.Web Forge Operator Console
# Purpose: Create a local desktop/app-menu launcher that runs forge_operator_console_launcher.py.

from __future__ import annotations

import os
from pathlib import Path

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
LAUNCHER = FORGE_ROOT / "scripts" / "forge_operator_console_launcher.py"
APP_DIR = HOME / ".local" / "share" / "applications"
APP_FILE = APP_DIR / "aiweb-forge-operator-console.desktop"
DESKTOP_DIR = HOME / "Desktop"
DESKTOP_FILE = DESKTOP_DIR / "AI.Web Forge Operator Console.desktop"

DESKTOP_CONTENT = f"""[Desktop Entry]
Type=Application
Name=AI.Web Forge Operator Console
Comment=Launch Forge, start the local Operator Console, and open http://localhost:7477/operator-console
Exec={LAUNCHER}
Icon=utilities-terminal
Terminal=true
Categories=Development;Utility;
StartupNotify=true
"""


def main() -> int:
    if not LAUNCHER.exists():
        print(f"INSTALL_REFUSED: missing launcher script: {LAUNCHER}")
        return 1

    LAUNCHER.chmod(0o755)
    APP_DIR.mkdir(parents=True, exist_ok=True)
    APP_FILE.write_text(DESKTOP_CONTENT, encoding="utf-8")
    APP_FILE.chmod(0o755)

    wrote_desktop = False
    if DESKTOP_DIR.exists() and DESKTOP_DIR.is_dir():
        DESKTOP_FILE.write_text(DESKTOP_CONTENT, encoding="utf-8")
        DESKTOP_FILE.chmod(0o755)
        wrote_desktop = True

    print("PATCH258A_OPERATOR_CONSOLE_DESKTOP_INSTALL_PASS")
    print(f"app_menu_launcher={APP_FILE}")
    if wrote_desktop:
        print(f"desktop_launcher={DESKTOP_FILE}")
    else:
        print("desktop_launcher=SKIPPED_NO_DESKTOP_FOLDER")
    print("mode=local_launcher_only")
    print("authority=starts_existing_forge_runtime_and_existing_forge_ui_start_command")
    print("adds_forge_commands=False")
    print("patches_main_py=False")
    print("bypasses_forge=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
