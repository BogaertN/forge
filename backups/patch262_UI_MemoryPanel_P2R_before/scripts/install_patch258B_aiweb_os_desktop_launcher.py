#!/usr/bin/env python3
"""
Patch 258B installer: AI.Web OS Desktop Launcher icon + desktop shortcut.
Installs the generated AI.Web OS icon into the user's local icon folder, updates/creates
an app-menu launcher, and places a desktop launcher on ~/Desktop.
"""
from pathlib import Path
import os
import shutil
import subprocess

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
ASSET = FORGE_ROOT / "assets" / "aiweb_os_desktop_launcher.png"
ICON_DIR = HOME / ".local" / "share" / "icons" / "aiweb"
ICON_DEST = ICON_DIR / "aiweb-os-desktop-launcher.png"
APP_DIR = HOME / ".local" / "share" / "applications"
APP_DESKTOP = APP_DIR / "aiweb-os-desktop-launcher.desktop"
OLD_APP_DESKTOP = APP_DIR / "aiweb-forge-operator-console.desktop"
DESKTOP_DIR = HOME / "Desktop"
DESKTOP_FILE = DESKTOP_DIR / "AI.Web OS Desktop Launcher.desktop"
EXISTING_LAUNCHER = FORGE_ROOT / "scripts" / "forge_operator_console_launcher.py"
FALLBACK_LAUNCHER = FORGE_ROOT / "scripts" / "forge_operator_console_launcher_icon_fallback.py"


def run_quiet(cmd):
    try:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def desktop_text(exec_target: Path) -> str:
    return f"""[Desktop Entry]
Version=1.0
Type=Application
Name=AI.Web OS Desktop Launcher
Comment=Launch AI.Web Forge Operator Console
Exec=python3 {exec_target}
Icon={ICON_DEST}
Terminal=false
Categories=Development;Utility;
StartupNotify=true
"""


def main() -> int:
    if not ASSET.exists():
        raise SystemExit(f"Missing icon asset: {ASSET}")

    ICON_DIR.mkdir(parents=True, exist_ok=True)
    APP_DIR.mkdir(parents=True, exist_ok=True)
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ASSET, ICON_DEST)
    os.chmod(ICON_DEST, 0o644)

    exec_target = EXISTING_LAUNCHER if EXISTING_LAUNCHER.exists() else FALLBACK_LAUNCHER
    if not exec_target.exists():
        raise SystemExit(f"Missing launcher script: {exec_target}")
    os.chmod(exec_target, 0o755)

    text = desktop_text(exec_target)
    APP_DESKTOP.write_text(text, encoding="utf-8")
    os.chmod(APP_DESKTOP, 0o755)

    shutil.copy2(APP_DESKTOP, DESKTOP_FILE)
    os.chmod(DESKTOP_FILE, 0o755)

    # Also update the older Patch 258A app-menu file if it exists, but preserve its Exec line.
    if OLD_APP_DESKTOP.exists():
        old_text = OLD_APP_DESKTOP.read_text(encoding="utf-8", errors="replace")
        lines = []
        saw_icon = False
        for line in old_text.splitlines():
            if line.startswith("Icon="):
                lines.append(f"Icon={ICON_DEST}")
                saw_icon = True
            else:
                lines.append(line)
        if not saw_icon:
            lines.append(f"Icon={ICON_DEST}")
        OLD_APP_DESKTOP.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(OLD_APP_DESKTOP, 0o755)

    run_quiet(["update-desktop-database", str(APP_DIR)])
    run_quiet(["gtk-update-icon-cache", str(ICON_DIR)])
    run_quiet(["gio", "set", str(DESKTOP_FILE), "metadata::trusted", "true"])
    run_quiet(["gio", "set", str(APP_DESKTOP), "metadata::trusted", "true"])

    print("PATCH258B_AIWEB_OS_DESKTOP_LAUNCHER_INSTALL_PASS")
    print(f"icon={ICON_DEST}")
    print(f"app_menu_launcher={APP_DESKTOP}")
    print(f"desktop_launcher={DESKTOP_FILE}")
    print(f"exec={exec_target}")
    print("If Ubuntu asks, right-click the desktop icon and choose 'Allow Launching'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
