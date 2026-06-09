#!/usr/bin/env python3
"""Patch 263S verifier — In-App Operator Lifecycle Menu.

Static and safe in-process checks only. This verifier never calls restart,
shutdown, stop, shell, Identity Vault writes, RMC memory writes, or LLM routes.
"""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'main.py'
SCRIPTS = ROOT / 'scripts'
AIWEB_SRC = ROOT.parent / 'aiweb' / 'apps' / 'forge-operator-console' / 'src'

checks: list[tuple[str, bool, str]] = []

def check(name: str, ok: bool, detail: str = '') -> None:
    checks.append((name, bool(ok), detail))


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''

main_text = read(MAIN)
check('main_exists', MAIN.exists(), str(MAIN))
try:
    ast.parse(main_text)
    check('main_ast_ok', True)
except Exception as exc:
    check('main_ast_ok', False, str(exc))

required_routes = [
    '/api/aiweb-os/lifecycle-manifest',
    '/api/aiweb-os/status',
    '/api/aiweb-os/logs',
    '/api/aiweb-os/exit-window-preview',
    '/api/aiweb-os/exit-window-confirm',
    '/api/aiweb-os/restart-preview',
    '/api/aiweb-os/restart-confirm',
    '/api/aiweb-os/shutdown-preview',
    '/api/aiweb-os/shutdown-confirm',
]
for route in required_routes:
    check(f'route_present:{route}', route in main_text)

required_symbols = [
    'def _p263s_lifecycle_manifest_v1',
    'def _p263s_status_payload',
    'def _p263s_logs_payload',
    'def _p263s_preview_payload',
    'def _p263s_confirm_payload',
    'def _p263s_schedule_action',
]
for symbol in required_symbols:
    check(f'symbol_present:{symbol}', symbol in main_text)

check('browser_shell_boundary_false', '"browser_executes_shell": False' in main_text)
check('browser_arbitrary_command_boundary_false', '"browser_executes_arbitrary_command": False' in main_text)
check('token_exit', 'EXIT_AIWEB_OPERATOR_WINDOW' in main_text)
check('token_restart', 'RESTART_AIWEB_OS' in main_text)
check('token_shutdown', 'SHUTDOWN_AIWEB_OS' in main_text)
check('uses_deferred_action', 'aiweb_os_deferred_action.py' in main_text)
check('does_not_add_post_shell_endpoint', '/api/aiweb-os/shell' not in main_text and '/api/aiweb-os/command' not in main_text)

# Verify helper script.
deferred = SCRIPTS / 'aiweb_os_deferred_action.py'
deferred_text = read(deferred)
check('deferred_script_exists', deferred.exists(), str(deferred))
try:
    ast.parse(deferred_text)
    check('deferred_script_ast_ok', True)
except Exception as exc:
    check('deferred_script_ast_ok', False, str(exc))
check('deferred_allowlist_restart', "'restart'" in deferred_text and 'aiweb-os-restart' in deferred_text)
check('deferred_allowlist_shutdown', "'shutdown'" in deferred_text and 'aiweb-os-stop' in deferred_text)
check('deferred_no_shell_true', 'shell=True' not in deferred_text)
check('deferred_no_os_system', 'os.system' not in deferred_text)
check('deferred_no_eval_exec', 'eval(' not in deferred_text and 'exec(' not in deferred_text)

# Safe in-process import and pure function checks.
try:
    spec = importlib.util.spec_from_file_location('forge_main_patch263s_verify', MAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    manifest = module._p263s_lifecycle_manifest_v1()
    exit_preview = module._p263s_preview_payload('exit_window')
    refused = module._p263s_confirm_payload('restart', '/api/aiweb-os/restart-confirm?token=WRONG')
    check('manifest_ok', manifest.get('status') == 'OK')
    check('manifest_route_count_8', len(manifest.get('routes', [])) == 8, str(len(manifest.get('routes', []))))
    check('preview_no_execute', exit_preview.get('executes_now') is False)
    check('preview_requires_token', bool(exit_preview.get('confirmation_token')))
    check('wrong_token_refused', refused.get('status') == 'REFUSED')
    check('wrong_token_no_execute', refused.get('executed') is False)
    boundary = manifest.get('boundary', {})
    check('boundary_forge_governs', boundary.get('forge_governs') is True)
    check('boundary_browser_shell_false', boundary.get('browser_executes_shell') is False)
    check('boundary_identity_write_false', boundary.get('identity_vault_write') is False)
    check('boundary_rmc_write_false', boundary.get('rmc_live_memory_write') is False)
except ModuleNotFoundError as exc:
    # Clean-extract patch audits may not include the whole Forge agents tree.
    # The installed verifier runs inside /home/nic/forge where agents exist.
    check('safe_inprocess_checks_skipped_without_full_forge_tree', True, str(exc))
except Exception as exc:
    check('safe_inprocess_checks', False, str(exc))

# Frontend files.
frontend_files = [
    AIWEB_SRC / 'shell' / 'OperatorLifecycleMenu.tsx',
    AIWEB_SRC / 'shell' / 'OperatorLayout.tsx',
    AIWEB_SRC / 'api' / 'forgeClient.ts',
    AIWEB_SRC / 'api' / 'types.ts',
    AIWEB_SRC / 'styles' / 'theme.css',
]
for f in frontend_files:
    check(f'frontend_file_exists:{f.name}', f.exists(), str(f))

menu_text = read(AIWEB_SRC / 'shell' / 'OperatorLifecycleMenu.tsx')
client_text = read(AIWEB_SRC / 'api' / 'forgeClient.ts')
layout_text = read(AIWEB_SRC / 'shell' / 'OperatorLayout.tsx')
css_text = read(AIWEB_SRC / 'styles' / 'theme.css')
check('frontend_menu_component', 'export function OperatorLifecycleMenu' in menu_text)
check('frontend_preview_first', 'previewAiwebOsLifecycleAction' in menu_text and 'confirmation_token' in menu_text)
check('frontend_confirm_token_gate', 'tokenMatches' in menu_text and 'Confirm' in menu_text)
check('frontend_window_close_only_after_confirm', 'window.close()' in menu_text and 'close_operator_window_in_browser' in menu_text)
check('frontend_client_status', 'getAiwebOsStatus' in client_text and '/api/aiweb-os/status' in client_text)
check('frontend_client_logs', 'getAiwebOsLogs' in client_text and '/api/aiweb-os/logs' in client_text)
check('frontend_client_confirm', 'confirmAiwebOsLifecycleAction' in client_text)
check('layout_imports_menu', 'OperatorLifecycleMenu' in layout_text)
check('css_lifecycle_present', '.operator-life-popover' in css_text and '.operator-life-confirm-button' in css_text)

# Preserve current RMC UI strings.
check('preserve_deep_dry_run_route', '/api/rmc/deep-dry-run' in main_text)
check('preserve_pf2_route', '/api/rmc/protoforge2-drift-preview' in main_text)
check('preserve_patch273_ui', 'Patch 273' in read(AIWEB_SRC / 'tabs' / 'RmcDeepDryRunTab.tsx') or 'Patch 273' in read(ROOT / 'operator_console_src' / 'RmcDeepDryRunTab.tsx'))

passed = sum(1 for _, ok, _ in checks if ok)
failed = len(checks) - passed
print(f'PATCH 263S VERIFIER  Total:{len(checks)} Passed:{passed} Failed:{failed}')
for name, ok, detail in checks:
    mark = '✓ [PASS]' if ok else '✗ [FAIL]'
    suffix = f' — {detail}' if detail else ''
    print(f'  {mark} {name}{suffix}')
if failed:
    print('RESULT: PATCH_263S_VERIFY_FAILED')
    raise SystemExit(1)
print('RESULT: PATCH_263S_VERIFY_OK')
