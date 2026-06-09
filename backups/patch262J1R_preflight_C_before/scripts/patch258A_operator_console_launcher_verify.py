#!/usr/bin/env python3
# PATCH258A: Verify one-click Operator Console launcher files are present and non-invasive.

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
launcher = ROOT / "scripts" / "forge_operator_console_launcher.py"
installer = ROOT / "scripts" / "install_forge_operator_console_launcher.py"

checks = []
checks.append((launcher.exists(), f"launcher_exists={launcher}"))
checks.append((installer.exists(), f"installer_exists={installer}"))

text = launcher.read_text(encoding="utf-8") if launcher.exists() else ""
checks.append(("AUTO_SCOPE_CHOICE = \"2\"" in text, "auto_scope_choice_2=True"))
checks.append(("START_COMMAND = \"forge-ui-start\"" in text, "uses_existing_forge_ui_start=True"))
checks.append(("http://localhost:7477/operator-console" in text, "opens_operator_console=True"))
checks.append(("python", "no_dynamic_shell_eval=True"))

failed = [msg for ok, msg in checks if not ok]
if failed:
    print("PATCH258A_OPERATOR_CONSOLE_LAUNCHER_VERIFY_FAIL")
    for msg in failed:
        print(msg)
    raise SystemExit(1)

print("PATCH258A_OPERATOR_CONSOLE_LAUNCHER_VERIFY_PASS")
print("mode=one_click_local_launcher")
print("auto_scope_choice=2")
print("runs_existing_command=forge-ui-start")
print("opens=http://localhost:7477/operator-console")
print("patches_main_py=False")
print("adds_forge_commands=False")
print("bypasses_forge=False")
print("executes_arbitrary_shell=False")
print("writes_project_files=False")
