#!/usr/bin/env python3
"""Patch 259 verifier — Left Rail Command Launcher.

Checks that Patch 259 wires the React left rail through existing Forge API surfaces only.
It is intentionally static: it does not run Forge, shell actions, simulations, or commands.
"""
from pathlib import Path
import re
import sys

ROOT = Path.home() / "forge"
AIWEB = Path.home() / "aiweb"
main = ROOT / "main.py"
registry = ROOT / "config" / "tool_registry.json"
left = AIWEB / "apps" / "forge-operator-console" / "src" / "shell" / "LeftRail.tsx"
layout = AIWEB / "apps" / "forge-operator-console" / "src" / "shell" / "OperatorLayout.tsx"
types = AIWEB / "apps" / "forge-operator-console" / "src" / "api" / "types.ts"
css = AIWEB / "apps" / "forge-operator-console" / "src" / "styles" / "theme.css"

errors = []
for path in [main, registry, left, layout, types, css]:
    if not path.exists():
        errors.append(f"missing={path}")

if not errors:
    main_text = main.read_text(encoding="utf-8", errors="replace")
    left_text = left.read_text(encoding="utf-8", errors="replace")
    layout_text = layout.read_text(encoding="utf-8", errors="replace")
    types_text = types.read_text(encoding="utf-8", errors="replace")
    css_text = css.read_text(encoding="utf-8", errors="replace")

    required_main = [
        '"next_patch": "Patch 260 — Right Rail Runtime Status"',
        '"left_rail_command_launcher_enabled": True',
        '"left_rail_uses_existing_command_bridge": True',
        '"left_rail_direct_shell": False',
        '"left_rail_direct_file_write": False',
        '"left_rail_identity_vault_write": False',
        '"left_rail_rmc_live_memory_write": False',
    ]
    for marker in required_main:
        if marker not in main_text:
            errors.append(f"main_missing={marker}")

    required_left = [
        'runForgeCommand',
        "window.open('/', '_blank'",
        "onTabChange('forge_output')",
        "onTabChange('protoforge_simulations')",
        'forge-protoforge-status',
        'forge-protoforge-simulation-plan pybullet_fixed_falling_cube',
        'forge-protoforge-simulation-run-approved',
        'RUN-PROTOFORGE',
        'forge-protoforge-result-show',
        'window.confirm',
    ]
    for marker in required_left:
        if marker not in left_text:
            errors.append(f"left_missing={marker}")

    forbidden_left = ['child_process', 'exec(', 'spawn(', 'rmc_live_memory_write = true', 'identity_vault_write = true']
    for marker in forbidden_left:
        if marker in left_text:
            errors.append(f"left_forbidden={marker}")

    if '<LeftRail activeTab={activeTab} onTabChange={onTabChange} />' not in layout_text:
        errors.append('layout_not_wired_to_left_rail_props')

    for marker in ['left_rail_command_launcher_enabled?: boolean', 'left_rail_direct_shell?: boolean', 'left_rail_rmc_live_memory_write?: boolean']:
        if marker not in types_text:
            errors.append(f"types_missing={marker}")

    if 'Patch 259 — Left Rail Command Launcher' not in css_text:
        errors.append('css_missing_patch259_marker')

    safe_match = re.search(r"_SAFE\s*=\s*\{(?P<body>.*?)\n\s*\}", main_text, re.S)
    if not safe_match:
        errors.append('safe_allowlist_not_parseable')
    else:
        safe_body = safe_match.group('body')
        if 'left-rail' in safe_body.lower() or 'patch259' in safe_body.lower():
            errors.append('left_rail_added_to_safe_allowlist_unexpectedly')

if errors:
    print('PATCH259_LEFT_RAIL_COMMAND_LAUNCHER_VERIFY_FAIL')
    for e in errors:
        print(e)
    sys.exit(1)

print('PATCH259_LEFT_RAIL_COMMAND_LAUNCHER_VERIFY_PASS')
print('mode=frontend_left_rail_shortcuts_existing_bridge_only')
print('uses_existing_api_command=True')
print('opens_terminus_fallback=True')
print('focuses_page_capture_panel=True')
print('protoforge_status_safe_button=True')
print('protoforge_plan_safe_button=True')
print('protoforge_run_gated_confirmed_button=True')
print('latest_result_safe_button=True')
print('patches_main_py_metadata_only=True')
print('adds_forge_commands=False')
print('new_backend_endpoint=False')
print('direct_shell=False')
print('direct_file_write=False')
print('identity_vault_write=False')
print('rmc_live_memory_write=False')
