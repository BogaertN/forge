#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks: list[tuple[bool, str, str]] = []

def add(ok: bool, name: str, detail: str = '') -> None:
    checks.append((ok, name, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{' :: ' + detail if detail else ''}")

def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding='utf-8') if path.exists() else ''

required = [
    'operator_console_src/RmcMemoryTab.tsx',
    'operator_console_src/rmc-memory-sections.tsx',
    'operator_console_src/rmc-panel-primitives.tsx',
    'operator_console_src/rmc-api-client.ts',
    'operator_console_src/rmc-ui-guards.ts',
    'operator_console_src/rmc-panel-health.ts',
    'operator_console_src/README_patch262_UIMemoryPanelP6.md',
    'scripts/test_rmc_memory_panel_p6_section_split.py',
    'scripts/patch262_UIMemoryPanelP6_verify.py',
    'SHA256SUMS.txt',
]
for rel in required:
    add((ROOT / rel).exists(), f'file_exists_{rel}', rel)

panel = read('operator_console_src/RmcMemoryTab.tsx')
sections = read('operator_console_src/rmc-memory-sections.tsx')
sha = read('SHA256SUMS.txt')

add('Patch 262-UI-MemoryPanel-P6' in panel, 'panel_version_p6')
add('rmc-memory-sections' in panel, 'panel_imports_section_module')
add('RmcPanelShell' in panel, 'panel_uses_shell')
add('RmcTopMetricsSection' in panel, 'panel_uses_top_metrics_section')
add('RmcEndpointHealthSection' in panel, 'panel_uses_endpoint_health_section')
add('RmcRouteManifestSection' in panel, 'panel_uses_route_manifest_section')
add('RmcContextLibrarySection' in panel, 'panel_uses_context_library_section')
add('RmcActiveLoopSection' in panel, 'panel_uses_active_loop_section')
add('RmcPromotionSection' in panel, 'panel_uses_promotion_section')
add('RmcRendererSection' in panel, 'panel_uses_renderer_section')
add('RmcBoundarySection' in panel, 'panel_uses_boundary_section')
add('fetch(' not in panel and 'axios' not in panel, 'panel_no_raw_fetch')
add('exec(' not in panel and 'spawn(' not in panel and 'child_process' not in panel, 'panel_no_shell_exec')
add('PROMOTION_TOKEN_FROM_GUARDS' in panel and 'evaluateGuardPromotionArmState' in panel, 'p3r_guard_preserved')
add('makeEndpointHealth' in panel and 'summarizeEndpointHealth' in panel, 'p4_health_preserved')
add("llmEnabled ? 'on' : 'off'" in panel and 'useState(false)' in panel, 'llm_toggle_default_off_preserved')
add('fetchRouteManifest(true)' in panel, 'route_manifest_source_preserved')

for export in [
    'RmcPanelShell', 'RmcTopMetricsSection', 'RmcEndpointHealthSection', 'RmcRouteManifestSection',
    'RmcContextLibrarySection', 'RmcActiveLoopSection', 'RmcPromotionSection', 'RmcRendererSection',
    'RmcBoundarySection', 'RmcPanelData'
]:
    add(f'export function {export}' in sections or f'export type {export}' in sections, f'section_export_{export}')

add('getPromotionPromote' not in sections, 'sections_no_direct_promotion_write_call')
add('fetch(' not in sections and 'axios' not in sections, 'sections_no_network')
add('exec(' not in sections and 'spawn(' not in sections and 'child_process' not in sections, 'sections_no_shell_exec')
add('evaluatePromotionArmState' not in sections, 'sections_do_not_recompute_guard')
add('PromotionArmState' in sections, 'sections_receive_guard_state')
add('__pycache__' not in sha and '.pyc' not in sha and '.venv' not in sha and 'node_modules' not in sha, 'sha_excludes_bad_artifacts')

# sha check
if (ROOT / 'SHA256SUMS.txt').exists():
    result = subprocess.run(['sha256sum','-c','SHA256SUMS.txt'], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    add(result.returncode == 0, 'sha_manifest_hashes_ok', result.stdout.strip().splitlines()[-1] if result.stdout.strip() else '')
else:
    add(False, 'sha_manifest_hashes_ok', 'missing SHA256SUMS.txt')

# behavior test
result = subprocess.run(['python', 'scripts/test_rmc_memory_panel_p6_section_split.py'], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
add(result.returncode == 0 and 'RESULT: rmc_memory_panel_p6_section_split_tests_pass=True' in result.stdout, 'behavior_test_passes', result.stdout.strip().splitlines()[-1] if result.stdout.strip() else '')

failed = [name for ok, name, _ in checks if not ok]
print('─' * 72)
print(f'Total: {len(checks)}')
print(f'Passed: {len(checks)-len(failed)}')
print(f'Failed: {len(failed)}')
if failed:
    print('RESULT: PATCH_262_UI_MEMORY_PANEL_P6_VERIFY_OK_FALSE')
    raise SystemExit(1)
print('RESULT: PATCH_262_UI_MEMORY_PANEL_P6_VERIFY_OK')
