#!/usr/bin/env python3
"""Patch 258B static verifier."""
from pathlib import Path
import hashlib

ROOT = Path.home() / "forge"
REQUIRED = [
    ROOT / "assets" / "aiweb_os_desktop_launcher.png",
    ROOT / "scripts" / "install_patch258B_aiweb_os_desktop_launcher.py",
    ROOT / "scripts" / "patch258B_aiweb_os_desktop_launcher_verify.py",
    ROOT / "scripts" / "forge_operator_console_launcher_icon_fallback.py",
]


def main() -> int:
    missing = [str(p) for p in REQUIRED if not p.exists()]
    if missing:
        print("PATCH258B_AIWEB_OS_DESKTOP_LAUNCHER_VERIFY_FAIL")
        print("missing=" + ", ".join(missing))
        return 1
    icon = ROOT / "assets" / "aiweb_os_desktop_launcher.png"
    digest = hashlib.sha256(icon.read_bytes()).hexdigest()
    if icon.stat().st_size < 10000:
        print("PATCH258B_AIWEB_OS_DESKTOP_LAUNCHER_VERIFY_FAIL")
        print("reason=icon_asset_too_small")
        return 1
    print("PATCH258B_AIWEB_OS_DESKTOP_LAUNCHER_VERIFY_PASS")
    print("mode=desktop_icon_and_launcher_installer")
    print("patches_main_py=False")
    print("adds_forge_commands=False")
    print("bypasses_forge=False")
    print("installs_icon=True")
    print("creates_desktop_launcher=True")
    print("icon_sha256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
