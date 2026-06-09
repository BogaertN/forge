#!/usr/bin/env python3
"""Install Patch 258C visible terminal desktop launcher fix."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
SCRIPT = FORGE_ROOT / "scripts" / "aiweb_os_visible_terminal_launcher.py"
ICON_DEST = HOME / ".local" / "share" / "icons" / "aiweb" / "aiweb-os-desktop-launcher.png"
ICON_SOURCE = FORGE_ROOT / "assets" / "aiweb_os_desktop_launcher.png"
APP_DIR = HOME / ".local" / "share" / "applications"
APP_DESKTOP = APP_DIR / "aiweb-os-desktop-launcher.desktop"
DESKTOP_DIR = HOME / "Desktop"
DESKTOP_FILE = DESKTOP_DIR / "AI.Web OS Desktop Launcher.desktop"
OLD_APP_DESKTOP = APP_DIR / "aiweb-forge-operator-console.desktop"


def run_quiet(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def desktop_text() -> str:
    icon_line = str(ICON_DEST if ICON_DEST.exists() else ICON_SOURCE)
    return f"""[Desktop Entry]
Version=1.0
Type=Application
Name=AI.Web OS Desktop Launcher
Comment=Launch AI.Web Forge Operator Console with visible terminal
Exec=python3 {SCRIPT}
Icon={icon_line}
Terminal=false
Categories=Development;Utility;
StartupNotify=true
"""


def main() -> int:
    if not SCRIPT.exists():
        raise SystemExit(f"Missing visible launcher script: {SCRIPT}")
    os.chmod(SCRIPT, 0o755)

    APP_DIR.mkdir(parents=True, exist_ok=True)
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

    # Preserve Patch 258B icon if present. If only the Forge asset exists, install it locally.
    if ICON_SOURCE.exists() and not ICON_DEST.exists():
        ICON_DEST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ICON_SOURCE, ICON_DEST)
        os.chmod(ICON_DEST, 0o644)

    text = desktop_text()
    APP_DESKTOP.write_text(text, encoding="utf-8")
    os.chmod(APP_DESKTOP, 0o755)
    shutil.copy2(APP_DESKTOP, DESKTOP_FILE)
    os.chmod(DESKTOP_FILE, 0o755)

    # Also point the older 258A launcher to the visible terminal flow if it exists.
    if OLD_APP_DESKTOP.exists():
        old_text = OLD_APP_DESKTOP.read_text(encoding="utf-8", errors="replace")
        lines = []
        saw_exec = False
        saw_icon = False
        for line in old_text.splitlines():
            if line.startswith("Exec="):
                lines.append(f"Exec=python3 {SCRIPT}")
                saw_exec = True
            elif line.startswith("Icon="):
                lines.append(f"Icon={ICON_DEST if ICON_DEST.exists() else ICON_SOURCE}")
                saw_icon = True
            else:
                lines.append(line)
        if not saw_exec:
            lines.append(f"Exec=python3 {SCRIPT}")
        if not saw_icon:
            lines.append(f"Icon={ICON_DEST if ICON_DEST.exists() else ICON_SOURCE}")
        OLD_APP_DESKTOP.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(OLD_APP_DESKTOP, 0o755)

    run_quiet(["update-desktop-database", str(APP_DIR)])
    run_quiet(["gio", "set", str(DESKTOP_FILE), "metadata::trusted", "true"])
    run_quiet(["gio", "set", str(APP_DESKTOP), "metadata::trusted", "true"])

    print("PATCH258C_VISIBLE_TERMINAL_LAUNCHER_INSTALL_PASS")
    print(f"desktop_launcher={DESKTOP_FILE}")
    print(f"app_menu_launcher={APP_DESKTOP}")
    print(f"exec=python3 {SCRIPT}")
    print("behavior=always_opens_visible_terminal_then_browser")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
