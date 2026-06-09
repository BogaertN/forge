#!/usr/bin/env python3
"""Patch 274 verifier — AI.Web Build Manifest Endpoint + Terminus overlay containment."""
from __future__ import annotations

import ast
from pathlib import Path

FORGE = Path('/home/nic/forge')
APP = Path('/home/nic/aiweb/apps/forge-operator-console')

checks: list[tuple[str, bool, str]] = []

def add(name: str, ok: bool, detail: str = '') -> None:
    checks.append((name, bool(ok), detail))

main = FORGE / 'main.py'
main_text = main.read_text(encoding='utf-8') if main.exists() else ''
try:
    ast.parse(main_text)
    add('main_ast_ok', True)
except Exception as exc:
    add('main_ast_ok', False, str(exc))

required_backend = [
    'def _p274_aiweb_build_manifest_v1',
    'def _p274_file_sha16',
    'def _p274_module_status',
    '"/api/aiweb-os/build-manifest"',
    'aiweb_os_build_manifest_patch274',
    'Patch 274 — AI.Web Build Manifest Endpoint',
    'hidden_by_default',
    'operator_console_modal_iframe_overlay',
    'direct_new_tab_open',
    'browser_shell_authority',
]
for marker in required_backend:
    add(f'backend_marker:{marker}', marker in main_text)

add('operator_contract_lists_build_manifest', 'read_only_build_manifest_patch274' in main_text)
add('route_handler_build_manifest', 'elif _p249_req_path == "/api/aiweb-os/build-manifest"' in main_text)
add('no_aiweb_shell_route', '/api/aiweb-os/shell' not in main_text)
add('no_aiweb_command_route', '/api/aiweb-os/command' not in main_text)
add('boundary_no_identity_write', '"identity_vault_write": False' in main_text)
add('boundary_no_rmc_write', '"rmc_live_memory_write": False' in main_text)
add('boundary_no_chroma_write', '"chroma_write": False' in main_text)
add('boundary_no_llm_call', '"llm_call": False' in main_text)
add('preserve_patch263S1_mode', 'aiweb_os_lifecycle_manifest_patch263S1' in main_text)
add('preserve_patch273_deep_dry_run', '/api/rmc/deep-dry-run' in main_text)

frontend_files = {
    'forgeClient': APP / 'src/api/forgeClient.ts',
    'types': APP / 'src/api/types.ts',
    'operator_layout': APP / 'src/shell/OperatorLayout.tsx',
    'lifecycle_menu': APP / 'src/shell/OperatorLifecycleMenu.tsx',
    'left_rail': APP / 'src/shell/LeftRail.tsx',
    'terminus_overlay': APP / 'src/shell/TerminusOverlay.tsx',
    'system_status': APP / 'src/tabs/SystemStatusTab.tsx',
    'theme': APP / 'src/styles/theme.css',
}
for name, path in frontend_files.items():
    add(f'frontend_file_exists:{name}', path.exists(), str(path))

texts = {name: path.read_text(encoding='utf-8') if path.exists() else '' for name, path in frontend_files.items()}
add('client_exports_build_manifest', 'getAiwebOsBuildManifest' in texts['forgeClient'])
add('types_define_build_manifest', 'AiwebOsBuildManifestResponse' in texts['types'])
add('lifecycle_menu_has_build_manifest_button', 'Build Manifest' in texts['lifecycle_menu'])
add('lifecycle_menu_calls_build_manifest', 'getAiwebOsBuildManifest' in texts['lifecycle_menu'])
add('system_status_reads_build_manifest', 'BuildManifestPanel' in texts['system_status'])
add('operator_layout_installs_terminus_overlay', 'TerminusOverlay' in texts['operator_layout'])
add('left_rail_no_window_open_for_terminus', 'window.open' not in texts['left_rail'])
add('left_rail_dispatches_terminus_event', 'aiweb-open-terminus' in texts['left_rail'])
add('terminus_overlay_iframe_present', '<iframe' in texts['terminus_overlay'] and 'src="/"' in texts['terminus_overlay'])
add('terminus_overlay_has_sandbox', 'sandbox=' in texts['terminus_overlay'])
add('css_terminus_overlay_present', 'terminus-overlay-backdrop' in texts['theme'])
add('css_build_manifest_present', 'operator-life-build-grid' in texts['theme'])
add('patch273_ui_preserved', 'Interactive Scenario Control' in (APP / 'src/tabs/RmcDeepDryRunTab.tsx').read_text(encoding='utf-8'))

failed = [c for c in checks if not c[1]]
print(f'PATCH 274 VERIFIER  Total:{len(checks)} Passed:{len(checks)-len(failed)} Failed:{len(failed)}')
for name, ok, detail in checks:
    mark = 'PASS' if ok else 'FAIL'
    suffix = f' — {detail}' if detail else ''
    print(f'  {"✓" if ok else "✗"} [{mark}] {name}{suffix}')
if failed:
    raise SystemExit(1)
print('RESULT: PATCH_274_VERIFY_OK')
