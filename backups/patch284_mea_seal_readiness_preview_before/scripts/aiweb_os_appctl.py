#!/usr/bin/env python3
"""
Patch 274R — AI.Web OS Desktop App Orchestrator, startup Terminus containment.

Purpose:
  Launch AI.Web Forge like a product instead of a development stack:
    - build the React operator console into static dist when needed
    - start Forge/Terminus in a managed background PTY if not already running
    - open one clean Chrome app-mode operator window at /operator-console
    - keep the high-security Terminus shell hidden until opened inside Operator Console
    - never auto-open standalone Terminus/HTML Chrome windows during startup
    - close owned auxiliary Terminus surfaces during stop/restart/shutdown
    - provide status/stop/restart commands with owned-process boundaries
    - refuse duplicate app windows on repeated/double desktop clicks

Boundary:
  This script is a local desktop process supervisor only. It does not grant the
  browser shell authority, does not write RMC memory, does not touch Identity Vault,
  does not call LLMs, does not query Chroma, and does not execute arbitrary user commands.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
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
from typing import Iterator, Optional

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
TERMINUS_ROOT_URL = "http://localhost:7477/"
APP_CLASS = "AIWebOSOperatorConsole"
TERMINUS_APP_CLASS = "AIWebOSTerminusShell"
SCOPE_CHOICE = "2"  # /home/nic/aiweb in current Forge approved path layout
FORGE_UI_COMMAND = "forge-ui-start"

SUPERVISOR_PID = RUN_ROOT / "forge_supervisor.pid"
FORGE_CHILD_PID = RUN_ROOT / "forge_main.pid"
WINDOW_PID = RUN_ROOT / "operator_window.pid"
TERMINUS_WINDOW_PID = RUN_ROOT / "terminus_window.pid"
STATE_FILE = RUN_ROOT / "state.json"
LOCK_FILE = RUN_ROOT / "appctl.lock"
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
    operator_window_pid_source: Optional[str]
    owned_standalone_terminus_window_pid: Optional[int]
    terminus_hidden_by_default: bool
    startup_opens_standalone_terminus: bool
    owned_terminus_closes_with_app: bool
    ui_root_exists: bool
    ui_dist_exists: bool
    chrome_available: bool
    npm_available: bool
    operator_url: str
    single_instance_lock_path: str
    single_instance_lock_state: str
    logs: str
    mode: str = "aiweb_os_desktop_orchestrator_patch274R_terminus_contained"


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


def command_path(name: str) -> Optional[str]:
    return shutil.which(name, path=build_env()["PATH"])


@contextlib.contextmanager
def single_instance_lock(timeout: float = 15.0) -> Iterator[None]:
    """Serialize start/stop/restart so double-clicks cannot race into duplicate windows."""
    ensure_dirs()
    deadline = time.time() + timeout
    with LOCK_FILE.open("a+", encoding="utf-8") as fh:
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fh.seek(0)
                fh.truncate()
                fh.write(str(os.getpid()))
                fh.flush()
                try:
                    yield
                finally:
                    fh.seek(0)
                    fh.truncate()
                    fh.flush()
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                return
            except BlockingIOError:
                if time.time() >= deadline:
                    raise RuntimeError(f"AI.Web OS launcher is busy; lock not released within {timeout:.1f}s: {LOCK_FILE}")
                time.sleep(0.15)


def lock_state() -> str:
    ensure_dirs()
    if not LOCK_FILE.exists():
        return "unlocked"
    try:
        with LOCK_FILE.open("a+", encoding="utf-8") as fh:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                return "unlocked"
            except BlockingIOError:
                return "locked"
    except Exception:
        return "unknown"


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
    for path in (SUPERVISOR_PID, FORGE_CHILD_PID, WINDOW_PID, TERMINUS_WINDOW_PID):
        pid = _pid_from_file(path)
        if pid and not pid_alive(pid):
            log_line(LAUNCHER_LOG, f"removing stale pidfile path={path} pid={pid}")
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


def _proc_pids() -> list[int]:
    pids: list[int] = []
    proc = Path("/proc")
    try:
        for child in proc.iterdir():
            if child.name.isdigit():
                pids.append(int(child.name))
    except Exception:
        return []
    return pids


def is_operator_window_process(pid: int) -> bool:
    cmd = cmdline_for_pid(pid)
    if not cmd:
        return False
    profile_match = str(CHROME_PROFILE) in cmd
    class_match = APP_CLASS in cmd
    url_match = OPERATOR_URL in cmd or "/operator-console" in cmd
    browserish = any(name in cmd for name in chrome_candidates()) or "chrome" in cmd.lower() or "chromium" in cmd.lower() or "xdg-open" in cmd
    return browserish and (profile_match or (class_match and url_match) or (profile_match and url_match))


def is_owned_standalone_terminus_process(pid: int) -> bool:
    """Return True only for a Terminus shell process that this orchestrator owns.

    Patch 274R is intentionally conservative: it does not scan and kill the user's
    regular Chrome windows or normal browser tabs. It only closes a standalone
    Terminus process if a future controlled launcher records it in TERMINUS_WINDOW_PID
    and its command line proves it is a local AI.Web Terminus surface, not the
    Operator Console.
    """
    cmd = cmdline_for_pid(pid)
    if not cmd:
        return False
    local_aiweb = "localhost:7477" in cmd or "127.0.0.1:7477" in cmd
    not_operator_console = "/operator-console" not in cmd
    class_match = TERMINUS_APP_CLASS in cmd
    app_mode_root = "--app=http://localhost:7477" in cmd or "--app=http://127.0.0.1:7477" in cmd
    browserish = any(name in cmd for name in chrome_candidates()) or "chrome" in cmd.lower() or "chromium" in cmd.lower() or "xdg-open" in cmd
    return browserish and local_aiweb and not_operator_console and (class_match or app_mode_root)


def owned_standalone_terminus_pid() -> Optional[int]:
    pid = _pid_from_file(TERMINUS_WINDOW_PID)
    if pid and pid_alive(pid) and is_owned_standalone_terminus_process(pid):
        return pid
    if pid and not pid_alive(pid):
        _remove_file(TERMINUS_WINDOW_PID)
    return None


def close_owned_standalone_terminus_surface() -> None:
    """Close controlled Terminus shells during stop/restart/shutdown.

    This is not a browser-tab killer. Existing regular Chrome windows containing a
    manually opened localhost tab are left alone because closing those would risk
    destroying unrelated user browser work. The final-product startup path no longer
    opens such tabs in the first place.
    """
    pid = owned_standalone_terminus_pid()
    if pid and pid_alive(pid):
        terminate_pid(pid, "owned_standalone_terminus_window")
    _remove_file(TERMINUS_WINDOW_PID)


def find_operator_window_pid() -> tuple[Optional[int], Optional[str]]:
    pidfile_pid = _pid_from_file(WINDOW_PID)
    if pidfile_pid and pid_alive(pidfile_pid) and is_operator_window_process(pidfile_pid):
        return pidfile_pid, "pidfile"
    if pidfile_pid and not pid_alive(pidfile_pid):
        _remove_file(WINDOW_PID)
    for pid in _proc_pids():
        if pid_alive(pid) and is_operator_window_process(pid):
            _write_pid(WINDOW_PID, pid)
            return pid, "process_scan"
    return None, None


def operator_window_already_open() -> bool:
    pid, _source = find_operator_window_pid()
    return bool(pid and pid_alive(pid))


def focus_operator_window() -> bool:
    wmctrl = command_path("wmctrl")
    if wmctrl:
        try:
            result = subprocess.run([wmctrl, "-xa", APP_CLASS], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            if result.returncode == 0:
                log_line(LAUNCHER_LOG, f"focused operator window via wmctrl class={APP_CLASS}")
                return True
        except Exception as exc:
            log_line(LAUNCHER_LOG, f"wmctrl focus failed: {type(exc).__name__}: {exc}")
    xdotool = command_path("xdotool")
    if xdotool:
        try:
            search = subprocess.run([xdotool, "search", "--class", APP_CLASS], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=2)
            window_ids = [line.strip() for line in search.stdout.splitlines() if line.strip()]
            if window_ids:
                subprocess.run([xdotool, "windowactivate", window_ids[-1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                log_line(LAUNCHER_LOG, f"focused operator window via xdotool id={window_ids[-1]}")
                return True
        except Exception as exc:
            log_line(LAUNCHER_LOG, f"xdotool focus failed: {type(exc).__name__}: {exc}")
    log_line(LAUNCHER_LOG, "operator window already open; no focus helper available")
    return False


def open_operator_window() -> int:
    ensure_dirs()
    existing, source = find_operator_window_pid()
    if existing and pid_alive(existing):
        focus_operator_window()
        log_line(LAUNCHER_LOG, f"operator window already open; reusing pid={existing} source={source}")
        return existing
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
    win, win_source = find_operator_window_pid()
    return ServiceStatus(
        backend_port_open=port_open(),
        backend_owned=backend_owned(),
        backend_supervisor_pid=sup if pid_alive(sup) else None,
        forge_child_pid=child if pid_alive(child) else None,
        operator_window_owned=bool(win and pid_alive(win)),
        operator_window_pid=win if pid_alive(win) else None,
        operator_window_pid_source=win_source,
        owned_standalone_terminus_window_pid=owned_standalone_terminus_pid(),
        terminus_hidden_by_default=True,
        startup_opens_standalone_terminus=False,
        owned_terminus_closes_with_app=True,
        ui_root_exists=UI_ROOT.exists(),
        ui_dist_exists=UI_DIST_INDEX.exists(),
        chrome_available=chrome_bin() is not None,
        npm_available=command_path("npm") is not None,
        operator_url=OPERATOR_URL,
        single_instance_lock_path=str(LOCK_FILE),
        single_instance_lock_state=lock_state(),
        logs=str(LOG_ROOT),
    )


def start(force_build: bool = False, no_window: bool = False) -> int:
    with single_instance_lock():
        ensure_dirs()
        build_react_if_needed(force=force_build)
        start_backend_if_needed()
        if not no_window:
            if operator_window_already_open():
                focus_operator_window()
                log_line(LAUNCHER_LOG, "start requested while operator window already open; reused existing window")
            else:
                open_operator_window()
    print(json.dumps(asdict(status()), indent=2, sort_keys=True))
    return 0


def stop(force_external: bool = False) -> int:
    with single_instance_lock():
        ensure_dirs()
        cleanup_dead_pidfiles()
        win, _source = find_operator_window_pid()
        if win and pid_alive(win):
            terminate_pid(win, "operator_window")
        _remove_file(WINDOW_PID)

        close_owned_standalone_terminus_surface()

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
