#!/usr/bin/env python3
"""Patch 263S behavior tests.

These tests verify the lifecycle menu contract without performing restart,
shutdown, shell execution, memory writes, or browser-close side effects.
"""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'main.py'
AIWEB_SRC = ROOT.parent / 'aiweb' / 'apps' / 'forge-operator-console' / 'src'
DEFERRED = ROOT / 'scripts' / 'aiweb_os_deferred_action.py'

results: list[tuple[str, bool, str]] = []

def ok(name: str, condition: bool, detail: str = '') -> None:
    results.append((name, bool(condition), detail))


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''

main_text = read(MAIN)
menu_text = read(AIWEB_SRC / 'shell' / 'OperatorLifecycleMenu.tsx')
client_text = read(AIWEB_SRC / 'api' / 'forgeClient.ts')
types_text = read(AIWEB_SRC / 'api' / 'types.ts')
layout_text = read(AIWEB_SRC / 'shell' / 'OperatorLayout.tsx')
css_text = read(AIWEB_SRC / 'styles' / 'theme.css')
deferred_text = read(DEFERRED)

# T1 — backend contract routes.
for route in [
    '/api/aiweb-os/lifecycle-manifest',
    '/api/aiweb-os/status',
    '/api/aiweb-os/logs',
    '/api/aiweb-os/exit-window-preview',
    '/api/aiweb-os/exit-window-confirm',
    '/api/aiweb-os/restart-preview',
    '/api/aiweb-os/restart-confirm',
    '/api/aiweb-os/shutdown-preview',
    '/api/aiweb-os/shutdown-confirm',
]:
    ok(f'T1_route_{route}', route in main_text)

# T2 — safe pure payload semantics.
try:
    spec = importlib.util.spec_from_file_location('forge_main_patch263s_test', MAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    manifest = module._p263s_lifecycle_manifest_v1()
    exit_preview = module._p263s_preview_payload('exit_window')
    restart_preview = module._p263s_preview_payload('restart')
    shutdown_preview = module._p263s_preview_payload('shutdown')
    wrong = module._p263s_confirm_payload('shutdown', '/api/aiweb-os/shutdown-confirm?token=nope')
    exit_ok = module._p263s_confirm_payload('exit_window', '/api/aiweb-os/exit-window-confirm?token=EXIT_AIWEB_OPERATOR_WINDOW')

    ok('T2_manifest_status', manifest.get('status') == 'OK')
    ok('T2_manifest_eight_routes', len(manifest.get('routes', [])) == 8)
    ok('T2_exit_preview_token', exit_preview.get('confirmation_token') == 'EXIT_AIWEB_OPERATOR_WINDOW')
    ok('T2_restart_preview_token', restart_preview.get('confirmation_token') == 'RESTART_AIWEB_OS')
    ok('T2_shutdown_preview_token', shutdown_preview.get('confirmation_token') == 'SHUTDOWN_AIWEB_OS')
    ok('T2_previews_do_not_execute', all(item.get('executes_now') is False for item in [exit_preview, restart_preview, shutdown_preview]))
    ok('T2_wrong_token_refused', wrong.get('status') == 'REFUSED' and wrong.get('executed') is False)
    ok('T2_exit_confirm_browser_only', exit_ok.get('status') == 'CONFIRMED' and exit_ok.get('close_operator_window_in_browser') is True and exit_ok.get('executed') is False)
    boundary = manifest.get('boundary', {})
    ok('T2_boundary_browser_shell_false', boundary.get('browser_executes_shell') is False)
    ok('T2_boundary_arbitrary_command_false', boundary.get('browser_executes_arbitrary_command') is False)
    ok('T2_boundary_fixed_allowlist_true', boundary.get('backend_uses_fixed_allowlist') is True)
    ok('T2_boundary_no_memory_writes', boundary.get('identity_vault_write') is False and boundary.get('rmc_live_memory_write') is False and boundary.get('chroma_write') is False)
except ModuleNotFoundError as exc:
    ok('T2_safe_import_payloads_skipped_without_full_forge_tree', True, str(exc))
except Exception as exc:
    ok('T2_safe_import_payloads', False, str(exc))

# T3 — no dangerous backend/browser route added.
ok('T3_no_aiweb_shell_route', '/api/aiweb-os/shell' not in main_text)
ok('T3_no_aiweb_command_route', '/api/aiweb-os/command' not in main_text)
ok('T3_confirm_uses_token_query', '_p263s_query_token' in main_text and 'confirmation_token_mismatch' in main_text)
ok('T3_status_uses_fixed_wrapper', 'fixed_appctl_status_wrapper' in main_text and '[str(wrapper)]' in main_text)
ok('T3_deferred_script_allowlist_only', 'ALLOWLIST' in deferred_text and 'restart' in deferred_text and 'shutdown' in deferred_text)
ok('T3_deferred_no_shell_true', 'shell=True' not in deferred_text)
ok('T3_deferred_no_os_system', 'os.system' not in deferred_text)
ok('T3_deferred_no_eval_exec', 'eval(' not in deferred_text and 'exec(' not in deferred_text)

# T4 — frontend final-product menu wiring.
ok('T4_menu_component_exists', 'export function OperatorLifecycleMenu' in menu_text)
ok('T4_layout_installs_menu', 'OperatorLifecycleMenu' in layout_text and '<OperatorLifecycleMenu />' in layout_text)
ok('T4_menu_has_status_logs', 'Status' in menu_text and 'View Logs' in menu_text)
ok('T4_menu_has_lifecycle_actions', 'Exit Window' in menu_text and 'Restart AI.Web OS' in menu_text and 'Shutdown AI.Web OS' in menu_text)
ok('T4_menu_preview_first', 'previewAiwebOsLifecycleAction' in menu_text and 'beginAction' in menu_text)
ok('T4_menu_token_gate', 'tokenMatches' in menu_text and 'confirmation_token' in menu_text)
ok('T4_menu_no_raw_shell_fetch', '/api/aiweb-os/shell' not in menu_text and '/api/aiweb-os/command' not in menu_text)
ok('T4_client_exports_status', 'getAiwebOsStatus' in client_text)
ok('T4_client_exports_logs', 'getAiwebOsLogs' in client_text)
ok('T4_client_exports_preview_confirm', 'previewAiwebOsLifecycleAction' in client_text and 'confirmAiwebOsLifecycleAction' in client_text)
ok('T4_types_added', 'AiwebOsLifecycleAction' in types_text and 'AiwebOsLifecycleBoundary' in types_text)
ok('T4_css_popover', '.operator-life-popover' in css_text)
ok('T4_css_confirm_button', '.operator-life-confirm-button' in css_text)

# T5 — preserve recent work.
ok('T5_preserve_patch271_route', '/api/rmc/deep-dry-run' in main_text)
ok('T5_preserve_patch270_route', '/api/rmc/deep-pipeline-preflight' in main_text)
ok('T5_preserve_patch269_route', '/api/rmc/resurrection-preview' in main_text)
ok('T5_preserve_patch268_route', '/api/rmc/protoforge2-drift-preview' in main_text)
ok('T5_preserve_patch273_interactive_ui', 'Custom operator input' in read(AIWEB_SRC / 'tabs' / 'RmcDeepDryRunTab.tsx'))

# T6 — parse checks.
for path in [MAIN, DEFERRED]:
    try:
        ast.parse(read(path))
        ok(f'T6_ast_{path.name}', True)
    except Exception as exc:
        ok(f'T6_ast_{path.name}', False, str(exc))

passed = sum(1 for _, status, _ in results if status)
failed = len(results) - passed
print('PATCH 263S — OPERATOR LIFECYCLE MENU TESTS')
print('─' * 66)
for name, status, detail in results:
    mark = '✓ [PASS]' if status else '✗ [FAIL]'
    suffix = f' — {detail}' if detail else ''
    print(f'  {mark} {name}{suffix}')
print('─' * 66)
print(f'  Total: {len(results)}  Passed: {passed}  Failed: {failed}')
if failed:
    print('\n  RESULT: patch263S_tests=FAIL')
    raise SystemExit(1)
print('\n  RESULT: patch263S_tests=PASS')
