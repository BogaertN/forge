#!/usr/bin/env python3
"""
Patch 258B fallback launcher for AI.Web OS Desktop Launcher.
Purpose:
  Start Forge in a normal terminal and open the Operator Console URL.
Boundary:
  This does not patch Forge, does not add Forge commands, and does not bypass Forge.
  It only opens the same local runtime path the user already runs manually.
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import time
import webbrowser
import urllib.request

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
URL = "http://localhost:7477/operator-console"


def forge_is_up() -> bool:
    try:
        with urllib.request.urlopen("http://localhost:7477/api/forge/status", timeout=1.5) as r:
            return 200 <= int(r.status) < 500
    except Exception:
        try:
            with urllib.request.urlopen("http://localhost:7477/operator-console", timeout=1.5) as r:
                return 200 <= int(r.status) < 500
        except Exception:
            return False


def open_forge_terminal() -> None:
    if not FORGE_ROOT.exists():
        raise SystemExit(f"Forge root not found: {FORGE_ROOT}")

    shell_script = (
        "cd ~/forge && "
        "if [ -f .venv/bin/activate ]; then source .venv/bin/activate; fi; "
        "echo 'AI.Web Forge starting...'; "
        "echo 'When prompted, choose scope 2: /home/nic/aiweb'; "
        "echo 'Then run: forge-ui-start'; "
        "python main.py; "
        "echo; read -p 'Forge stopped. Press Enter to close this window...'"
    )

    terminal_candidates = [
        ["gnome-terminal", "--", "bash", "-lc", shell_script],
        ["kgx", "--", "bash", "-lc", shell_script],
        ["x-terminal-emulator", "-e", f"bash -lc {shell_script!r}"],
        ["xfce4-terminal", "--command", f"bash -lc {shell_script!r}"],
        ["konsole", "-e", "bash", "-lc", shell_script],
    ]

    for cmd in terminal_candidates:
        if shutil.which(cmd[0]):
            subprocess.Popen(cmd)
            return

    raise SystemExit("No supported terminal launcher found. Open Terminal and run: cd ~/forge && source .venv/bin/activate && python main.py")


def main() -> int:
    if not forge_is_up():
        open_forge_terminal()
        time.sleep(2)
    webbrowser.open(URL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
