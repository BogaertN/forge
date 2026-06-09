#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks: list[tuple[bool, str]] = []

def add(ok: bool, name: str) -> None:
    checks.append((ok, name))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")

def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding='utf-8') if path.exists() else ''

panel = read('operator_console_src/RmcMemoryTab.tsx')
sections = read('operator_console_src/rmc-memory-sections.tsx')
primitives = read('operator_console_src/rmc-panel-primitives.tsx')
guards = read('operator_console_src/rmc-ui-guards.ts')
health = read('operator_console_src/rmc-panel-health.ts')
client = read('operator_console_src/rmc-api-client.ts')

add(bool(panel), 'panel_exists')
add(bool(sections), 'sections_exists')
add(bool(primitives), 'primitives_still_exists')
add(bool(guards), 'guard_still_exists')
add(bool(health), 'health_still_exists')
add(bool(client), 'client_still_exists')

for name in [
    'RmcPanelShell', 'RmcTopMetricsSection', 'RmcEndpointHealthSection', 'RmcRouteManifestSection',
    'RmcContextLibrarySection', 'RmcActiveLoopSection', 'RmcPromotionSection', 'RmcRendererSection', 'RmcBoundarySection'
]:
    add(name in panel, f'panel_uses_{name}')
    add(name in sections, f'sections_define_{name}')

add(panel.count('<Section title=') == 0, 'panel_no_inline_section_markup')
add(panel.count('<Metric label=') == 0, 'panel_no_inline_metric_markup')
add('ReviewQueueList' not in panel, 'panel_no_inline_review_queue_list')
add('JsonDetails' not in panel, 'panel_no_inline_json_details')
add('RouteAvailability' not in panel, 'panel_no_inline_route_availability')
add('DirectoryList' not in panel, 'panel_no_inline_directory_list')
add('type PanelData' not in panel and 'const emptyPanelData: PanelData' not in panel, 'panel_old_local_paneldata_removed')
add('RmcPanelData' in panel, 'panel_uses_shared_paneldata')

add('getPromotionPromote' in panel, 'controller_keeps_promote_call')
add('getPromotionPromote' not in sections, 'sections_do_not_call_promote')
add('fetch(' not in sections and 'fetch(' not in panel, 'no_raw_fetch')
add('child_process' not in sections + panel, 'no_child_process_reference')
add('PROMOTION_TOKEN_FROM_GUARDS' in panel, 'promotion_token_from_guard_preserved')
add('evaluateGuardPromotionArmState' in panel, 'guard_eval_preserved')
add('makeEndpointHealth' in panel and 'summarizeEndpointHealth' in panel, 'partial_load_preserved')
add('llmEnabled ? \'on\' : \'off\'' in panel, 'llm_toggle_preserved')
add('fetchRouteManifest(true)' in panel, 'route_manifest_preserved')
add('required confirmation' in sections.lower(), 'promotion_confirmation_copy_preserved')
add('The LLM toggle only drafts text through the sentence plan' in sections, 'llm_non_authority_copy_preserved')
add('P4 isolates endpoint failures' in sections, 'endpoint_health_copy_preserved')
add('This panel is a control surface only' in sections, 'control_surface_copy_preserved')
add('rmc-panel-primitives' in sections, 'sections_use_primitives')
add('rmc-ui-guards' not in sections or 'PromotionArmState' in sections, 'sections_reference_guard_type_only')

failed = [name for ok, name in checks if not ok]
print(f'Total: {len(checks)}')
print(f'Passed: {len(checks)-len(failed)}')
print(f'Failed: {len(failed)}')
if failed:
    print('RESULT: rmc_memory_panel_p6_section_split_tests_pass=False')
    raise SystemExit(1)
print('RESULT: rmc_memory_panel_p6_section_split_tests_pass=True')
