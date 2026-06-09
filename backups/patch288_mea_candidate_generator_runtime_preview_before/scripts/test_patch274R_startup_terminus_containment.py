#!/usr/bin/env python3
from __future__ import annotations
import ast
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
DESKTOPS = [
    ROOT / "Desktop" / "AI.Web OS Desktop Launcher.desktop",
    ROOT / "Desktop" / "aiweb-os-desktop-launcher.desktop",
    ROOT / ".local" / "share" / "applications" / "aiweb-os-desktop-launcher.desktop",
]

results: list[tuple[str, bool, str]] = []

def ok(name: str, condition: bool, detail: str = "") -> None:
    results.append((name, bool(condition), detail))

def text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

app = text(APPCTL) if APPCTL.exists() else ""
vis = text(VISIBLE) if VISIBLE.exists() else ""

try:
    ast.parse(app)
    ok("T1_appctl_ast", True)
except Exception as e:
    ok("T1_appctl_ast", False, repr(e))
try:
    ast.parse(vis)
    ok("T1_visible_wrapper_ast", True)
except Exception as e:
    ok("T1_visible_wrapper_ast", False, repr(e))

ok("T2_startup_policy_hidden", "terminus_hidden_by_default=True" in app)
ok("T2_startup_policy_no_standalone", "startup_opens_standalone_terminus=False" in app)
ok("T2_owned_terminus_closes_with_app", "owned_terminus_closes_with_app=True" in app)
ok("T2_operator_url_still_primary", 'OPERATOR_URL = "http://localhost:7477/operator-console"' in app)
ok("T2_no_terminus_app_start", "--app={TERMINUS_ROOT_URL}" not in app)
ok("T2_no_standalone_terminus_launcher", "open_standalone_terminus" not in app and "open_terminus_window" not in app)
ok("T2_stop_closes_owned_terminus", "close_owned_standalone_terminus_surface()" in app)
ok("T2_terminus_closure_conservative", "regular Chrome windows" in app and "left alone" in app)
ok("T2_no_arbitrary_browser_kill_scan", "for pid in _proc_pids():\n        if pid_alive(pid) and is_owned_standalone_terminus_process" not in app)

ok("T3_visible_wrapper_delegates", "subprocess.run([sys.executable, str(APPCTL), \"start\"]" in vis)
ok("T3_visible_wrapper_no_url", "localhost:7477" not in vis and "127.0.0.1:7477" not in vis)
ok("T3_visible_wrapper_no_browser", all(s not in vis for s in ["webbrowser", "xdg-open", "google-chrome", "chromium", "forge-ui-start"]))
ok("T3_visible_wrapper_no_shell", "shell=True" not in vis and "os.system" not in vis)
ok("T3_visible_wrapper_no_eval", "eval(" not in vis and "exec(" not in vis)

for idx, d in enumerate(DESKTOPS, 1):
    txt = text(d) if d.exists() else ""
    ok(f"T4_desktop_{idx}_exists", d.exists(), str(d))
    ok(f"T4_desktop_{idx}_clean_exec", "Exec=/home/nic/forge/scripts/aiweb_os_appctl.py start" in txt)
    ok(f"T4_desktop_{idx}_no_legacy_launcher", "aiweb_os_visible_terminal_launcher.py" not in txt)
    ok(f"T4_desktop_{idx}_terminal_false", "Terminal=false" in txt)
    ok(f"T4_desktop_{idx}_icon", "aiweb-os-desktop-launcher.png" in txt)

ok("T5_no_shell_true_appctl", "shell=True" not in app)
ok("T5_no_os_system_appctl", "os.system" not in app)
ok("T5_no_eval_exec_appctl", "eval(" not in app and "exec(" not in app)
ok("T5_existing_status_command_preserved", "def print_status" in app and "status" in app)
ok("T5_existing_restart_preserved", "def restart" in app and "stop(force_external=False)" in app and "start(force_build=force_build)" in app)

passed = sum(1 for _, cond, _ in results if cond)
failed = len(results) - passed
print("PATCH 274R — STARTUP TERMINUS CONTAINMENT TESTS")
print("─" * 66)
for name, cond, detail in results:
    print(f"  {'✓ [PASS]' if cond else '✗ [FAIL]'} {name}{(' — ' + detail) if detail else ''}")
print("─" * 66)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed:
    print("\n  RESULT: patch274R_tests=FAIL")
    raise SystemExit(1)
print("\n  RESULT: patch274R_tests=PASS")
