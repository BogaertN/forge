#!/usr/bin/env python3
from __future__ import annotations
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path


def repo_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "forge").exists():
        return cwd
    if cwd.name == "forge":
        return cwd.parent
    return Path.home()

ROOT = repo_root()
FORGE = ROOT / "forge"
APPCTL = FORGE / "scripts" / "aiweb_os_appctl.py"
VISIBLE = FORGE / "scripts" / "aiweb_os_visible_terminal_launcher.py"
DESKTOP_A = ROOT / "Desktop" / "AI.Web OS Desktop Launcher.desktop"
DESKTOP_B = ROOT / "Desktop" / "aiweb-os-desktop-launcher.desktop"
LOCAL_APP = ROOT / ".local" / "share" / "applications" / "aiweb-os-desktop-launcher.desktop"

checks: list[tuple[bool, str]] = []

def add(name: str, ok: bool, detail: str = "") -> None:
    checks.append((bool(ok), f"{name}{' — ' + detail if detail else ''}"))

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

add("appctl_exists", APPCTL.exists(), str(APPCTL))
add("visible_wrapper_exists", VISIBLE.exists(), str(VISIBLE))
app = read(APPCTL) if APPCTL.exists() else ""
vis = read(VISIBLE) if VISIBLE.exists() else ""

try:
    ast.parse(app)
    add("appctl_ast_ok", True)
except Exception as e:
    add("appctl_ast_ok", False, repr(e))
try:
    ast.parse(vis)
    add("visible_wrapper_ast_ok", True)
except Exception as e:
    add("visible_wrapper_ast_ok", False, repr(e))

add("mode_patch274R", "patch274R_terminus_contained" in app)
add("terminus_pid_declared", "TERMINUS_WINDOW_PID" in app)
add("terminus_hidden_by_default_field", "terminus_hidden_by_default" in app)
add("startup_opens_standalone_false_field", "startup_opens_standalone_terminus" in app and "False" in app)
add("owned_terminus_closes_with_app_field", "owned_terminus_closes_with_app" in app)
add("close_owned_terminus_function", "def close_owned_standalone_terminus_surface" in app)
add("owned_terminus_only_pidfile", "owned_standalone_terminus_pid" in app and "TERMINUS_WINDOW_PID" in app)
add("no_process_scan_kill_for_terminus", "for pid in _proc_pids():\n        if pid_alive(pid) and is_owned_standalone_terminus_process" not in app)
add("stop_calls_terminus_close", "close_owned_standalone_terminus_surface()" in app)
add("open_operator_url_only", "--app={OPERATOR_URL}" in app and "--app={TERMINUS_ROOT_URL}" not in app)
add("start_no_terminus_window_call", "open_standalone_terminus" not in app and "open_terminus_window" not in app)
add("appctl_no_shell_true", "shell=True" not in app)
add("appctl_no_os_system", "os.system" not in app)
add("appctl_no_eval_exec", "eval(" not in app and "exec(" not in app)

add("visible_delegates_to_appctl", "aiweb_os_appctl.py" in vis and '"start"' in vis)
add("visible_no_forge_ui_start", "forge-ui-start" not in vis)
add("visible_no_browser_open", "webbrowser" not in vis and "xdg-open" not in vis and "google-chrome" not in vis and "chromium" not in vis)
add("visible_no_localhost_url", "localhost:7477" not in vis and "127.0.0.1:7477" not in vis)
add("visible_no_shell_true", "shell=True" not in vis)
add("visible_no_os_system", "os.system" not in vis)
add("visible_no_eval_exec", "eval(" not in vis and "exec(" not in vis)

for label, path in [("desktop_named", DESKTOP_A), ("desktop_lower", DESKTOP_B), ("local_app", LOCAL_APP)]:
    add(f"{label}_exists", path.exists(), str(path))
    txt = read(path) if path.exists() else ""
    add(f"{label}_exec_appctl", "Exec=/home/nic/forge/scripts/aiweb_os_appctl.py start" in txt)
    add(f"{label}_terminal_false", "Terminal=false" in txt)
    add(f"{label}_icon_preserved", "aiweb-os-desktop-launcher.png" in txt)
    add(f"{label}_no_visible_launcher_exec", "aiweb_os_visible_terminal_launcher.py" not in txt)

# Optional import-level status proof without launching anything.
try:
    ns: dict[str, object] = {}
    exec(compile(app, str(APPCTL), "exec"), ns)
    ServiceStatus = ns.get("ServiceStatus")
    annotations = getattr(ServiceStatus, "__annotations__", {}) if ServiceStatus else {}
    add("service_status_has_terminus_fields", all(k in annotations for k in ["terminus_hidden_by_default", "startup_opens_standalone_terminus", "owned_terminus_closes_with_app"]))
except Exception as e:
    add("service_status_import_safe", False, repr(e))

passed = sum(1 for ok, _ in checks if ok)
failed = len(checks) - passed
print(f"PATCH 274R VERIFIER  Total:{len(checks)} Passed:{passed} Failed:{failed}")
for ok, msg in checks:
    print(f"  {'✓ [PASS]' if ok else '✗ [FAIL]'} {msg}")
if failed:
    print("RESULT: PATCH_274R_VERIFY_FAILED")
    raise SystemExit(1)
print("RESULT: PATCH_274R_VERIFY_OK")
