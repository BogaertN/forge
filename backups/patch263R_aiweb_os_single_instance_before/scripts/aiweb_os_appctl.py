#!/usr/bin/env python3
"""
Patch 263 — AI.Web OS Desktop App Orchestrator.

Purpose:
  Launch AI.Web Forge like a product instead of a development stack:
    - build the React operator console into static dist when needed
    - start Forge/Terminus in a managed background PTY if not already running
    - open a clean Chrome app-mode operator window at /operator-console
    - provide status/stop/restart commands with owned-process boundaries

Boundary:
  This script is a local desktop process supervisor only. It does not grant the
  browser shell authority, does not write RMC memory, does not touch Identity Vault,
  does not call LLMs, and does not execute arbitrary user commands.
"""
from __future__ import annotations

import argparse
import json
import os
import pty
import select
import shutil
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional

HOME = Path.home()
FORGE_ROOT = HOME / "forge"
FORGE_MAIN = FORGE_ROOT / "main.py"
FORGE_VENV_PYTHON = FORGE_ROOT / ".venv" / "bin" / "python"
UI_ROOT = HOME / "aiweb" / "apps" / "forge-operator-console"
UI_DIST_INDEX = UI_ROOT / "dist" / "index.html"
RUN_ROOT = HOME / ".local" / "state" / "aiweb-os"
LOG_ROOT = FORGE_ROOT / "logs" / "aiweb_os"
CHROME_PROFILE = HOME / ".config" / "aiweb-os" / "operator-console-chrome-profile"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 7477
OPERATOR_URL = "http://localhost:7477/operator-console"
APP_CLASS = "AIWebOSOperatorConsole"
SCOPE_CHOICE = "2"  # /home/nic/aiweb in current Forge approved path layout
FORGE_UI_COMMAND = "forge-ui-start"

SUPERVISOR_PID = RUN_ROOT / "forge_supervisor.pid"
FORGE_CHILD_PID = RUN_ROOT / "forge_main.pid"
WINDOW_PID = RUN_ROOT / "operator_window.pid"
STATE_FILE = RUN_ROOT / "state.json"
SUPERVISOR_LOG = LOG_ROOT / "forge_supervisor.log"
BUILD_LOG = LOG_ROOT / "react_build.log"
LAUNCHER_LOG = LOG_ROOT / "launcher.log"

NODE_HINTS = [
    HOME / ".nvm" / "versions" / "node" / "v18.20.8" / "bin",
    HOME / ".nvm" / "versions" / "node" / "current" / "bin",
]


@dataclass
class ServiceStatus:
    backend_port_open: bool
    backend_owned: bool
    backend_supervisor_pid: Optional[int]
    forge_child_pid: Optional[int]
    operator_window_owned: bool
    operator_window_pid: Optional[int]
    ui_root_exists: bool
    ui_dist_exists: bool
    chrome_available: bool
    npm_available: bool
    operator_url: str
    mode: str = "aiweb_os_desktop_orchestrator_patch263"


def ensure_dirs() -> None:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)


def log_line(path: Path, message: str) -> None:
    ensure_dirs()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {message}\n")


def _pid_from_file(path: Path) -> Optional[int]:
    try:
        value = path.read_text(encoding="utf-8").strip()
        if not value:
            return None
        return int(value)
    except Exception:
        return None


def _write_pid(path: Path, pid: int) -> None:
    ensure_dirs()
    path.write_text(str(pid), encoding="utf-8")


def _remove_file(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def pid_alive(pid: Optional[int]) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def cmdline_for_pid(pid: int) -> str:
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\x00", b" ").decode(errors="replace")
    except Exception:
        return ""


def terminate_pid(pid: int, label: str, timeout: float = 5.0) -> bool:
    if not pid_alive(pid):
        return True
    log_line(LAUNCHER_LOG, f"terminate request label={label} pid={pid}")
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return True
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not pid_alive(pid):
            return True
        time.sleep(0.15)
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        return True
    return not pid_alive(pid)


def port_open(host: str = BACKEND_HOST, port: int = BACKEND_PORT, timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_for_port(seconds: float = 25.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if port_open():
            return True
        time.sleep(0.25)
    return False


def command_path(name: str) -> Optional[str]:
    enriched = build_env()["PATH"]
    return shutil.which(name, path=enriched)


def build_env() -> dict[str, str]:
    env = os.environ.copy()
    path_parts = []
    for hint in NODE_HINTS:
        if hint.exists():
            path_parts.append(str(hint))
    path_parts.append(env.get("PATH", ""))
    env["PATH"] = os.pathsep.join([p for p in path_parts if p])
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("BROWSER", "none")
    return env


def source_newer_than_dist() -> bool:
    if not UI_DIST_INDEX.exists():
        return True
    dist_mtime = UI_DIST_INDEX.stat().st_mtime
    candidates: list[Path] = []
    for rel in ("package.json", "vite.config.ts", "vite.config.js", "tsconfig.json", "index.html"):
        p = UI_ROOT / rel
        if p.exists():
            candidates.append(p)
    src = UI_ROOT / "src"
    if src.exists():
        candidates.extend(p for p in src.rglob("*") if p.is_file() and p.suffix in {".ts", ".tsx", ".js", ".jsx", ".css", ".html"})
    newest = max((p.stat().st_mtime for p in candidates), default=0.0)
    return newest > dist_mtime


def build_react_if_needed(force: bool = False) -> bool:
    ensure_dirs()
    if not UI_ROOT.exists():
        raise RuntimeError(f"UI root missing: {UI_ROOT}")
    if not force and not source_newer_than_dist():
        log_line(BUILD_LOG, "React dist already fresh; skipping build")
        return True
    npm = command_path("npm")
    if not npm:
        raise RuntimeError("npm not found. Node/NPM path is unavailable in launcher environment.")
    log_line(BUILD_LOG, "Starting npm run build for operator console")
    with BUILD_LOG.open("a", encoding="utf-8") as log:
        log.write("\n===== npm run build =====\n")
        proc = subprocess.run([npm, "run", "build"], cwd=str(UI_ROOT), env=build_env(), stdout=log, stderr=subprocess.STDOUT, text=True, timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"npm run build failed; see {BUILD_LOG}")
    if not UI_DIST_INDEX.exists():
        raise RuntimeError(f"Build completed but dist index is missing: {UI_DIST_INDEX}")
    log_line(BUILD_LOG, "React build OK")
    return True


def cleanup_dead_pidfiles() -> None:
    for path in (SUPERVISOR_PID, FORGE_CHILD_PID, WINDOW_PID):
        pid = _pid_from_file(path)
        if pid and not pid_alive(pid):
            _remove_file(path)


def backend_owned() -> bool:
    sup = _pid_from_file(SUPERVISOR_PID)
    child = _pid_from_file(FORGE_CHILD_PID)
    if sup and pid_alive(sup):
        return True
    if child and pid_alive(child):
        return True
    return False


def start_backend_if_needed() -> None:
    ensure_dirs()
    cleanup_dead_pidfiles()
    if port_open():
        log_line(LAUNCHER_LOG, "Backend already open; reusing existing port 7477")
        return
    python_bin = str(FORGE_VENV_PYTHON if FORGE_VENV_PYTHON.exists() else sys.executable)
    script = Path(__file__).resolve()
    log_line(LAUNCHER_LOG, "Starting Forge supervisor")
    with (LOG_ROOT / "appctl_start.log").open("a", encoding="utf-8") as out:
        proc = subprocess.Popen([python_bin, str(script), "supervise"], cwd=str(FORGE_ROOT), env=build_env(), stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    _write_pid(SUPERVISOR_PID, proc.pid)
    if not wait_for_port(35.0):
        raise RuntimeError(f"Forge backend did not open port {BACKEND_PORT}; see {SUPERVISOR_LOG}")


def supervise() -> int:
    ensure_dirs()
    if not FORGE_MAIN.exists():
        log_line(SUPERVISOR_LOG, f"missing main.py: {FORGE_MAIN}")
        return 1
    python_bin = str(FORGE_VENV_PYTHON if FORGE_VENV_PYTHON.exists() else sys.executable)
    _write_pid(SUPERVISOR_PID, os.getpid())
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(str(FORGE_ROOT))
        os.execvpe(python_bin, [python_bin, "main.py"], build_env())
    _write_pid(FORGE_CHILD_PID, pid)
    injected_scope = False
    injected_start = False
    buffer = ""
    last_log_flush = 0.0
    try:
        with SUPERVISOR_LOG.open("a", encoding="utf-8") as log:
            log.write("\n===== Forge supervisor session start =====\n")
            while True:
                try:
                    ready, _, _ = select.select([fd], [], [], 0.2)
                except OSError:
                    break
                if fd in ready:
                    try:
                        data = os.read(fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    text = data.decode(errors="replace")
                    log.write(text)
                    now = time.time()
                    if now - last_log_flush > 0.5:
                        log.flush()
                        last_log_flush = now
                    buffer = (buffer + text)[-8000:]
                    if (not injected_scope) and ("Choice [1-" in buffer or "Choice [1-3]" in buffer):
                        time.sleep(0.15)
                        os.write(fd, (SCOPE_CHOICE + "\n").encode())
                        injected_scope = True
                        buffer = ""
                    if injected_scope and (not injected_start) and "forge>" in buffer:
                        time.sleep(0.15)
                        os.write(fd, (FORGE_UI_COMMAND + "\n").encode())
                        injected_start = True
                        buffer = ""
                # If the child died, leave loop.
                finished, _status = os.waitpid(pid, os.WNOHANG)
                if finished == pid:
                    break
    finally:
        try:
            os.close(fd)
        except OSError:
            pass
        _remove_file(SUPERVISOR_PID)
        _remove_file(FORGE_CHILD_PID)
    return 0


def chrome_candidates() -> list[str]:
    return ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def chrome_bin() -> Optional[str]:
    for name in chrome_candidates():
        found = command_path(name)
        if found:
            return found
    return None


def open_operator_window() -> int:
    ensure_dirs()
    chrome = chrome_bin()
    if not chrome:
        opener = command_path("xdg-open")
        if not opener:
            raise RuntimeError("No Chrome/Chromium or xdg-open available for operator window")
        proc = subprocess.Popen([opener, OPERATOR_URL], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        _write_pid(WINDOW_PID, proc.pid)
        return proc.pid
    args = [
        chrome,
        f"--app={OPERATOR_URL}",
        f"--user-data-dir={CHROME_PROFILE}",
        f"--class={APP_CLASS}",
        "--no-first-run",
        "--disable-default-apps",
        "--disable-translate",
        "--window-size=1500,920",
        "--window-position=80,60",
    ]
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    _write_pid(WINDOW_PID, proc.pid)
    log_line(LAUNCHER_LOG, f"operator window launched pid={proc.pid} url={OPERATOR_URL}")
    return proc.pid


def status() -> ServiceStatus:
    cleanup_dead_pidfiles()
    sup = _pid_from_file(SUPERVISOR_PID)
    child = _pid_from_file(FORGE_CHILD_PID)
    win = _pid_from_file(WINDOW_PID)
    return ServiceStatus(
        backend_port_open=port_open(),
        backend_owned=backend_owned(),
        backend_supervisor_pid=sup if pid_alive(sup) else None,
        forge_child_pid=child if pid_alive(child) else None,
        operator_window_owned=pid_alive(win),
        operator_window_pid=win if pid_alive(win) else None,
        ui_root_exists=UI_ROOT.exists(),
        ui_dist_exists=UI_DIST_INDEX.exists(),
        chrome_available=chrome_bin() is not None,
        npm_available=command_path("npm") is not None,
        operator_url=OPERATOR_URL,
    )


def start(force_build: bool = False, no_window: bool = False) -> int:
    ensure_dirs()
    build_react_if_needed(force=force_build)
    start_backend_if_needed()
    if not no_window:
        open_operator_window()
    print(json.dumps(asdict(status()), indent=2, sort_keys=True))
    return 0


def stop(force_external: bool = False) -> int:
    ensure_dirs()
    cleanup_dead_pidfiles()
    # Close the managed app window first.
    win = _pid_from_file(WINDOW_PID)
    if win and pid_alive(win):
        terminate_pid(win, "operator_window")
    _remove_file(WINDOW_PID)

    sup = _pid_from_file(SUPERVISOR_PID)
    child = _pid_from_file(FORGE_CHILD_PID)
    if sup and pid_alive(sup):
        terminate_pid(sup, "forge_supervisor")
    if child and pid_alive(child):
        terminate_pid(child, "forge_child")
    _remove_file(SUPERVISOR_PID)
    _remove_file(FORGE_CHILD_PID)

    if port_open() and not force_external:
        print("Backend port 7477 is still open but is not owned by this orchestrator. Leaving it running.")
    elif port_open() and force_external:
        raise RuntimeError("External Forge backend stop is intentionally not implemented. Stop it from its owning terminal.")
    print(json.dumps(asdict(status()), indent=2, sort_keys=True))
    return 0


def print_status(as_json: bool = False) -> int:
    s = status()
    if as_json:
        print(json.dumps(asdict(s), indent=2, sort_keys=True))
        return 0
    print("AI.Web OS Desktop Orchestrator Status")
    print("──────────────────────────────────────")
    for k, v in asdict(s).items():
        print(f"{k}: {v}")
    print(f"logs: {LOG_ROOT}")
    return 0


def restart(force_build: bool = False) -> int:
    stop(force_external=False)
    return start(force_build=force_build)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="AI.Web OS desktop app orchestrator")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_start = sub.add_parser("start")
    p_start.add_argument("--force-build", action="store_true")
    p_start.add_argument("--no-window", action="store_true")
    p_stop = sub.add_parser("stop")
    p_stop.add_argument("--force-external", action="store_true")
    p_status = sub.add_parser("status")
    p_status.add_argument("--json", action="store_true")
    p_restart = sub.add_parser("restart")
    p_restart.add_argument("--force-build", action="store_true")
    sub.add_parser("supervise")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "start":
            return start(force_build=args.force_build, no_window=args.no_window)
        if args.cmd == "stop":
            return stop(force_external=args.force_external)
        if args.cmd == "status":
            return print_status(as_json=args.json)
        if args.cmd == "restart":
            return restart(force_build=args.force_build)
        if args.cmd == "supervise":
            return supervise()
    except Exception as exc:
        log_line(LAUNCHER_LOG, f"ERROR {type(exc).__name__}: {exc}")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
