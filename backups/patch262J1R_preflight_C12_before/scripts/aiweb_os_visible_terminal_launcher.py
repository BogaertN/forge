#!/usr/bin/env python3
"""
Patch 258C — AI.Web OS visible terminal launcher.
Purpose:
  Make the desktop launcher always open a visible terminal window first, then open
  the Operator Console browser URL. If Forge is not running, the terminal starts
  Forge through the existing local main.py flow, auto-selects scope 2, and runs
  forge-ui-start through the visible terminal session.
Boundary:
  This is a local desktop convenience launcher only.
  It does not patch Forge main.py.
  It does not add Forge commands.
  It does not bypass Forge authority.
  It does not grant the browser shell access.
"""
from __future__ import annotations

import argparse
import os
import pty
import select
import shutil
import subprocess
import sys
import termios
import threading
import time
import tty
import urllib.request
import webbrowser
from pathlib import Path

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
URL = "http://localhost:7477/operator-console"
STATUS_URLS = (
    "http://localhost:7477/api/forge/status",
    "http://localhost:7477/operator-console",
)


def forge_is_up(timeout: float = 1.2) -> bool:
    for url in STATUS_URLS:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                if 200 <= int(response.status) < 500:
                    return True
        except Exception:
            continue
    return False


def delayed_browser_open(delay: float = 2.0) -> None:
    def _open() -> None:
        time.sleep(delay)
        try:
            webbrowser.open(URL)
        except Exception:
            subprocess.Popen(["xdg-open", URL], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=_open, daemon=True).start()


def terminal_command() -> list[str]:
    script_path = Path(__file__).resolve()
    inside = f"python3 {script_path} --inside-terminal; echo; read -r -p 'Launcher session ended. Press Enter to close this window...' _"
    candidates = [
        ["gnome-terminal", "--title=AI.Web OS Desktop Launcher", "--", "bash", "-lc", inside],
        ["kgx", "--", "bash", "-lc", inside],
        ["x-terminal-emulator", "-e", f"bash -lc {inside!r}"],
        ["xfce4-terminal", "--title=AI.Web OS Desktop Launcher", "--command", f"bash -lc {inside!r}"],
        ["konsole", "--title", "AI.Web OS Desktop Launcher", "-e", "bash", "-lc", inside],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            return cmd
    raise SystemExit("No supported terminal program found. Install gnome-terminal or open Forge manually.")


def launch_outer() -> int:
    if not FORGE_ROOT.exists():
        raise SystemExit(f"Forge root not found: {FORGE_ROOT}")
    cmd = terminal_command()
    subprocess.Popen(cmd, cwd=str(FORGE_ROOT))
    delayed_browser_open(2.5)
    return 0


def print_header() -> None:
    print("=" * 72)
    print("AI.Web OS Desktop Launcher — Visible Forge Terminal")
    print("=" * 72)
    print(f"Forge root: {FORGE_ROOT}")
    print(f"Operator Console: {URL}")
    print("Authority boundary: launcher opens Forge; Forge still governs.")
    print("No browser shell. No direct model tools. No Identity Vault/RMC write.")
    print("=" * 72)
    print()


def run_existing_forge_status_shell() -> int:
    print_header()
    print("Forge already appears to be running on localhost:7477.")
    print("This visible terminal was opened so you are not blind to runtime state.")
    print()
    print("Useful checks from this window:")
    print("  cd ~/forge")
    print("  source .venv/bin/activate")
    print("  python main.py")
    print()
    print("Use the already-open Operator Console in the browser.")
    print("Leaving you at a normal shell in ~/forge.")
    print()
    os.chdir(FORGE_ROOT)
    subprocess.call(["bash", "-i"])
    return 0


def spawn_forge_with_visible_autostart() -> int:
    print_header()
    print("Forge is not responding yet. Starting Forge visibly now.")
    print("Auto-start will select scope 2: /home/nic/aiweb")
    print("Then it will run: forge-ui-start")
    print("After that, this terminal becomes the live Forge terminal.")
    print()
    delayed_browser_open(5.0)

    command = (
        "cd ~/forge && "
        "if [ -f .venv/bin/activate ]; then source .venv/bin/activate; fi; "
        "python main.py"
    )
    pid, fd = pty.fork()
    if pid == 0:
        os.execlp("bash", "bash", "-lc", command)

    old_attrs = None
    stdin_fd = sys.stdin.fileno()
    try:
        old_attrs = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)
    except Exception:
        old_attrs = None

    injected_scope = False
    injected_ui = False
    buffer = ""
    start_time = time.time()

    try:
        while True:
            readable, _, _ = select.select([fd, stdin_fd], [], [], 0.1)
            if fd in readable:
                try:
                    data = os.read(fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                os.write(sys.stdout.fileno(), data)
                text = data.decode(errors="ignore")
                buffer = (buffer + text)[-4000:]

                if (not injected_scope) and ("Choice [1-3]" in buffer or "Choice" in buffer):
                    time.sleep(0.2)
                    os.write(fd, b"2\n")
                    injected_scope = True
                    buffer = ""

                if injected_scope and (not injected_ui) and ("forge>" in buffer):
                    time.sleep(0.2)
                    os.write(fd, b"forge-ui-start\n")
                    injected_ui = True
                    buffer = ""

                if (not injected_scope) and time.time() - start_time > 8.0:
                    # Safe fallback: do not loop forever waiting for exact prompt text.
                    os.write(fd, b"2\n")
                    injected_scope = True

            if stdin_fd in readable:
                try:
                    user_data = os.read(stdin_fd, 1024)
                except OSError:
                    user_data = b""
                if user_data:
                    os.write(fd, user_data)
                else:
                    break
    finally:
        if old_attrs is not None:
            try:
                termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_attrs)
            except Exception:
                pass
    return 0


def launch_inside_terminal() -> int:
    if not FORGE_ROOT.exists():
        print(f"Forge root not found: {FORGE_ROOT}")
        return 1
    if forge_is_up():
        return run_existing_forge_status_shell()
    return spawn_forge_with_visible_autostart()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inside-terminal", action="store_true")
    args = parser.parse_args()
    if args.inside_terminal:
        return launch_inside_terminal()
    return launch_outer()


if __name__ == "__main__":
    raise SystemExit(main())
