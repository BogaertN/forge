#!/usr/bin/env python3
"""Patch 274 behavior tests — static production-safety checks for build manifest and Terminus containment."""
from __future__ import annotations

import ast
from pathlib import Path

FORGE = Path('/home/nic/forge')
APP = Path('/home/nic/aiweb/apps/forge-operator-console')

results: list[tuple[str, bool, str]] = []

def ok(name: str, value: bool, detail: str = '') -> None:
    results.append((name, bool(value), detail))

main_text = (FORGE / 'main.py').read_text(encoding='utf-8')
try:
    ast.parse(main_text)
    ok('T0_main_ast', True)
except Exception as exc:
    ok('T0_main_ast', False, str(exc))

# Endpoint and contract shape.
ok('T1_endpoint_declared', '/api/aiweb-os/build-manifest' in main_text)
ok('T1_mode_patch274', 'aiweb_os_build_manifest_patch274' in main_text)
ok('T1_current_patch_field', 'Patch 274 — AI.Web Build Manifest Endpoint' in main_text)
ok('T1_last_successful_patch_field', 'Patch 263S1 — Lifecycle Boundary Proof Fix' in main_text)
ok('T1_counts_surface_present', 'rmc_canonical_routes' in main_text and 'command_surface_expected' in main_text)
ok('T1_active_modules_present', 'active_modules' in main_text and 'protoforge2_drift_connector' in main_text)
ok('T1_known_gaps_present', 'known_gaps' in main_text and 'deep_pipeline_live_writes' in main_text)
ok('T1_dirty_state_no_shell', 'No git or shell status is executed by this endpoint' in main_text)
ok('T1_boundary_read_only', '"read_only": True' in main_text and '"writes_files": False' in main_text)
ok('T1_no_authority_escalation', '"ui_is_authority": False' in main_text and '"forge_governs": True' in main_text)
ok('T1_no_memory_writes', '"identity_vault_write": False' in main_text and '"rmc_live_memory_write": False' in main_text)
ok('T1_no_chroma_or_llm', '"chroma_write": False' in main_text and '"llm_call": False' in main_text)
ok('T1_no_arbitrary_shell', '"browser_executes_shell": False' in main_text and '"browser_executes_arbitrary_command": False' in main_text)
ok('T1_operator_contract_knows_route', 'read_only_build_manifest_patch274' in main_text)

# Preserve recent stack.
for route in [
    '/api/aiweb-os/lifecycle-manifest',
    '/api/rmc/deep-dry-run',
    '/api/rmc/deep-pipeline-preflight',
    '/api/rmc/resurrection-preview',
    '/api/rmc/protoforge2-drift-preview',
]:
    ok(f'T2_preserve_route:{route}', route in main_text)

# UI behavior.
left = (APP / 'src/shell/LeftRail.tsx').read_text(encoding='utf-8')
layout = (APP / 'src/shell/OperatorLayout.tsx').read_text(encoding='utf-8')
overlay = (APP / 'src/shell/TerminusOverlay.tsx').read_text(encoding='utf-8')
menu = (APP / 'src/shell/OperatorLifecycleMenu.tsx').read_text(encoding='utf-8')
client = (APP / 'src/api/forgeClient.ts').read_text(encoding='utf-8')
types = (APP / 'src/api/types.ts').read_text(encoding='utf-8')
status_tab = (APP / 'src/tabs/SystemStatusTab.tsx').read_text(encoding='utf-8')
css = (APP / 'src/styles/theme.css').read_text(encoding='utf-8')

ok('T3_terminus_not_new_tab', 'window.open' not in left)
ok('T3_terminus_event_driven', 'aiweb-open-terminus' in left and 'addEventListener' in layout)
ok('T3_terminus_hidden_by_state', 'terminusOpen' in layout and 'if (!open) return null' in overlay)
ok('T3_terminus_iframe_sandboxed', '<iframe' in overlay and 'sandbox=' in overlay)
ok('T3_terminus_css_overlay', 'terminus-overlay-backdrop' in css and 'z-index: 95' in css)
ok('T3_build_manifest_client', 'getAiwebOsBuildManifest' in client)
ok('T3_build_manifest_types', 'AiwebOsBuildManifestResponse' in types)
ok('T3_build_manifest_menu_button', 'Build Manifest' in menu)
ok('T3_build_manifest_system_status', 'BuildManifestPanel' in status_tab)
ok('T3_build_manifest_no_post', "fetch('/api/aiweb-os/build-manifest'" in client and 'method: \'POST\'' not in client[client.find('getAiwebOsBuildManifest'):client.find('getAiwebOsLifecycleManifest')])

failed = [r for r in results if not r[1]]
print('PATCH 274 — BUILD MANIFEST + TERMINUS CONTAINMENT TESTS')
print('─' * 66)
for name, passed, detail in results:
    print(f'  {"✓" if passed else "✗"} [{"PASS" if passed else "FAIL"}] {name}{(" — " + detail) if detail else ""}')
print('─' * 66)
print(f'  Total: {len(results)}  Passed: {len(results)-len(failed)}  Failed: {len(failed)}')
if failed:
    raise SystemExit(1)
print('\n  RESULT: patch274_tests=PASS')
