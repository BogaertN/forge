#!/usr/bin/env python3
# PATCH258A: AI.Web Forge Operator Console Launcher
# Purpose: Start Forge in a real terminal, auto-select the AI.Web scope, start the existing Forge UI server,
#          and open the production Operator Console in the browser.
# Boundary: This does not patch Forge commands, does not bypass Forge authority, and does not write project files.

from __future__ import annotations

import os
import pty
import select
import socket
import subprocess
import sys
import termios
import time
import tty
import webbrowser
from pathlib import Path

FORGE_ROOT = Path.home() / "forge"
VENV_PYTHON = FORGE_ROOT / ".venv" / "bin" / "python"
FORGE_MAIN = FORGE_ROOT / "main.py"
OPERATOR_URL = "http://localhost:7477/operator-console"
HOST = "127.0.0.1"
PORT = 7477
AUTO_SCOPE_CHOICE = "2"  # /home/nic/aiweb in Nic's approved-path layout
START_COMMAND = "forge-ui-start"


def _port_open(host: str = HOST, port: int = PORT, timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _open_operator_console() -> None:
    try:
        webbrowser.open(OPERATOR_URL, new=2)
    except Exception:
        try:
            subprocess.Popen(["xdg-open", OPERATOR_URL], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            print(f"\n[launcher] Browser open failed. Open manually: {OPERATOR_URL}\n")


def _print_header() -> None:
    print("\nAI.Web Forge Operator Console Launcher")
    print("──────────────────────────────────────")
    print(f"Forge root : {FORGE_ROOT}")
    print(f"Console    : {OPERATOR_URL}")
    print("Scope      : auto-select option 2 when Forge asks")
    print("Action     : run existing Forge command: forge-ui-start")
    print("Boundary   : no shell bridge, no file write bridge, no authority bypass")
    print("──────────────────────────────────────\n")


def main() -> int:
    _print_header()

    if not FORGE_ROOT.exists():
        print(f"[launcher] Missing Forge root: {FORGE_ROOT}")
        return 1
    if not FORGE_MAIN.exists():
        print(f"[launcher] Missing Forge main.py: {FORGE_MAIN}")
        return 1

    python_bin = str(VENV_PYTHON if VENV_PYTHON.exists() else sys.executable)

    already_open = _port_open()
    if already_open:
        print(f"[launcher] Port {PORT} is already responding. Browser will open after Forge attaches.")

    master_fd, slave_fd = pty.openpty()

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    proc = subprocess.Popen(
        [python_bin, "main.py"],
        cwd=str(FORGE_ROOT),
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        env=env,
        close_fds=True,
    )
    os.close(slave_fd)

    old_tty = None
    stdin_fd = None
    if sys.stdin.isatty():
        stdin_fd = sys.stdin.fileno()
        old_tty = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)

    buffer = ""
    sent_scope = False
    sent_start = False
    browser_opened = False
    last_port_check = 0.0
    start_sent_at = 0.0

    try:
        while proc.poll() is None:
            read_fds = [master_fd]
            if stdin_fd is not None:
                read_fds.append(stdin_fd)

            ready, _, _ = select.select(read_fds, [], [], 0.1)

            if master_fd in ready:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                text = data.decode(errors="replace")
                sys.stdout.write(text)
                sys.stdout.flush()
                buffer = (buffer + text)[-8000:]

                if (not sent_scope) and "Choice [1-" in buffer:
                    os.write(master_fd, (AUTO_SCOPE_CHOICE + "\n").encode())
                    sent_scope = True
                    buffer = ""

                if sent_scope and (not sent_start) and "forge>" in buffer:
                    os.write(master_fd, (START_COMMAND + "\n").encode())
                    sent_start = True
                    start_sent_at = time.time()
                    buffer = ""

                if (not browser_opened) and ("Terminus running at:" in buffer or "terminus running" in buffer.lower()):
                    _open_operator_console()
                    browser_opened = True

            if stdin_fd is not None and stdin_fd in ready:
                try:
                    user_data = os.read(stdin_fd, 4096)
                except OSError:
                    user_data = b""
                if user_data:
                    os.write(master_fd, user_data)

            now = time.time()
            if (not browser_opened) and (already_open or sent_start) and now - last_port_check > 0.5:
                last_port_check = now
                if _port_open():
                    # Give Vite-served production route a moment to be ready after the socket opens.
                    if already_open or now - start_sent_at >= 1.0:
                        _open_operator_console()
                        browser_opened = True

    finally:
        if old_tty is not None and stdin_fd is not None:
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_tty)
        try:
            os.close(master_fd)
        except OSError:
            pass

    return proc.returncode or 0


if __name__ == "__main__":
    raise SystemExit(main())
