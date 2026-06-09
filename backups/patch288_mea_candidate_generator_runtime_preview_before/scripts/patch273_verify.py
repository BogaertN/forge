#!/usr/bin/env python3
from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = pathlib.Path('/home/nic/aiweb/apps/forge-operator-console')
if not APP.exists():
    # Clean-extract fallback.
    APP = ROOT.parent / 'aiweb/apps/forge-operator-console'

checks: list[tuple[str, bool, str]] = []

def add(name: str, ok: bool, detail: str = '') -> None:
    checks.append((name, bool(ok), detail))

def read(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception:
        return ''

main_py = ROOT / 'main.py'
engine_py = ROOT / 'rmc_engine_v1/deep_dry_run_orchestrator.py'
tab_tsx = APP / 'src/tabs/RmcDeepDryRunTab.tsx'
client_ts = APP / 'src/lib/rmc-api-client.ts'
theme_css = APP / 'src/styles/theme.css'
staging_tab = ROOT / 'operator_console_src/RmcDeepDryRunTab.tsx'

for label, path in [
    ('main_py', main_py),
    ('engine_py', engine_py),
    ('tab_tsx', tab_tsx),
    ('client_ts', client_ts),
    ('theme_css', theme_css),
    ('staging_tab', staging_tab),
]:
    add(f'file_exists_{label}', path.exists(), str(path))

main = read(main_py)
engine = read(engine_py)
tab = read(tab_tsx)
client = read(client_ts)
theme = read(theme_css)
staging = read(staging_tab)

try:
    ast.parse(main)
    add('main_py_ast_compiles', True)
except Exception as exc:
    add('main_py_ast_compiles', False, str(exc))
try:
    ast.parse(engine)
    add('engine_ast_compiles', True)
except Exception as exc:
    add('engine_ast_compiles', False, str(exc))

add('engine_273_version', 'rmc_deep_dry_run_orchestrator_v2_patch273' in engine)
add('engine_scenario_library', 'SCENARIO_LIBRARY' in engine and 'phase_skip_projection_attempt' in engine)
add('engine_interactive_request', 'interactive_request' in engine)
add('engine_no_writes_boundary', 'FORBIDDEN_EFFECTS' in engine and 'memory_write_committed' in engine)
add('main_parses_query', 'urllib.parse' in main and 'parse_qs' in main)
add('main_passes_input', 'run_deep_dry_run(source_text=_input_text' in main)
add('main_returns_scenario_catalog', 'scenario_catalog' in main)
add('main_patch_273_label', 'Patch 273 — Deep Dry-Run Interactive Scenario Panel' in main)

for scenario in [
    'clean_governed_path',
    'phase_skip_projection_attempt',
    'bypass_correction_attack',
    'memory_write_before_echo',
    'ghost_loop_pressure',
    'resurrection_candidate_probe',
    'custom',
]:
    add(f'scenario_{scenario}', scenario in tab and scenario in engine)

add('ui_select_control', '<select' in tab and 'onScenarioChange' in tab)
add('ui_textarea_control', '<textarea' in tab and 'setInput' in tab)
add('ui_calls_deep_dry_run_with_params', 'getDeepDryRun(dryRunParams)' in tab)
add('ui_scenario_proof_section', 'Scenario Result Proof' in tab)
add('ui_no_raw_fetch', 'fetch(' not in tab)
add('ui_no_eval', 'eval(' not in tab)
add('ui_no_window_open', 'window.open' not in tab)
for forbidden in ['getGatedMemoryWriter(', 'getPromotionPromote(', 'promoteCandidate(', 'getOutputRenderer(']:
    add(f'ui_no_{forbidden}', forbidden not in tab)

add('client_scenario_type', 'scenario?: string;' in client and 'use_protoforge2_preview?' in client)
add('theme_scenario_input', '.rmc-scenario-input' in theme)
add('staging_updated', 'Patch 273' in staging and 'Interactive Scenario Control' in staging)

print('PATCH 273 VERIFY')
print('─' * 60)
failed = 0
for name, ok, detail in checks:
    mark = 'PASS' if ok else 'FAIL'
    print(f"  {'✓' if ok else '✗'} [{mark}] {name}{(' — ' + detail) if detail else ''}")
    failed += 0 if ok else 1
print('─' * 60)
print(f'  Total: {len(checks)}  Passed: {len(checks)-failed}  Failed: {failed}')
print()
if failed:
    print('RESULT: PATCH_273_VERIFY_FAIL')
    sys.exit(1)
print('RESULT: PATCH_273_VERIFY_OK')
