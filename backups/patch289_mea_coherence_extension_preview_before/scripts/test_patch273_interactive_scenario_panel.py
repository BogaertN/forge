#!/usr/bin/env python3
from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = pathlib.Path('/home/nic/aiweb/apps/forge-operator-console')
if not APP.exists():
    APP = ROOT.parent / 'aiweb/apps/forge-operator-console'

def read(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception:
        return ''

main = read(ROOT / 'main.py')
engine = read(ROOT / 'rmc_engine_v1/deep_dry_run_orchestrator.py')
tab = read(APP / 'src/tabs/RmcDeepDryRunTab.tsx')
client = read(APP / 'src/lib/rmc-api-client.ts')

tests: list[tuple[str, bool, str]] = []

def check(name: str, ok: bool, detail: str = '') -> None:
    tests.append((name, bool(ok), detail))

# Backend contract.
check('T1_engine_273', 'ENGINE_VERSION = "rmc_deep_dry_run_orchestrator_v2_patch273"' in engine)
check('T1_scenario_catalog_export', 'def scenario_catalog()' in engine)
check('T1_resolve_interactive_request', 'def _resolve_interactive_request' in engine)
check('T1_interactive_request_returned', '"interactive_request": interactive_request' in engine)
check('T1_forbidden_effects_preserved', 'FORBIDDEN_EFFECTS' in engine and 'projection_allowed' in engine and 'memory_write_committed' in engine)
check('T1_no_subprocess', 'subprocess' not in engine)
check('T1_no_os_system', 'os.system' not in engine)
check('T1_no_open_write', "open(" not in engine or "'w'" not in engine)
check('T1_no_llm', 'openai' not in engine.lower() and 'anthropic' not in engine.lower())

# Main endpoint contract.
check('T2_main_query_parse', 'urlsplit(raw_path)' in main and 'parse_qs' in main)
check('T2_main_input_names', '"input", "text", "query"' in main)
check('T2_main_scenario_names', '"scenario", "scenario_id", "mode"' in main)
check('T2_main_calls_run_with_text', 'run_deep_dry_run(source_text=_input_text' in main)
check('T2_main_returns_catalog', '"scenario_catalog": _scenario_catalog()' in main)
check('T2_main_read_only', '"writes_files": False' in main and '"calls_llm": False' in main)

# Scenario list.
for scenario in [
    'clean_governed_path',
    'phase_skip_projection_attempt',
    'bypass_correction_attack',
    'memory_write_before_echo',
    'ghost_loop_pressure',
    'resurrection_candidate_probe',
    'custom',
]:
    check(f'T3_scenario_{scenario}', scenario in engine and scenario in tab)

# UI behavior.
check('T4_select_added', '<select' in tab and 'Deep dry-run scenario' in tab)
check('T4_textarea_added', '<textarea' in tab and 'Deep dry-run scenario input' in tab)
check('T4_run_button', 'Run selected scenario' in tab)
check('T4_reset_button', 'Reset scenario text' in tab)
check('T4_scenario_proof', 'Scenario Result Proof' in tab)
check('T4_interactive_request_displayed', 'interactive_request' in tab)
check('T4_get_deep_dry_run_params', 'getDeepDryRun(dryRunParams)' in tab)
check('T4_get_pf2_with_text', 'getProtoForge2DriftPreview({ text: input, scenario: selectedScenario })' in tab)
check('T4_no_raw_fetch', 'fetch(' not in tab)
check('T4_no_eval', 'eval(' not in tab)
check('T4_no_window_open', 'window.open' not in tab)
check('T4_no_local_storage', 'localStorage.set' not in tab)
check('T4_no_write_api_calls', all(x not in tab for x in ['getGatedMemoryWriter', 'getPromotionPromote', 'promoteCandidate', 'getMemoryWriter']))

# API client type supports params.
check('T5_client_scenario_param', 'scenario?: string;' in client)
check('T5_client_use_pf2_param', 'use_protoforge2_preview?: boolean | string;' in client)
check('T5_deep_dry_run_getter_preserved', "fetchRmcEndpoint('deep_dry_run', params)" in client)

# Syntax.
try:
    ast.parse(main)
    check('T6_main_ast', True)
except Exception as exc:
    check('T6_main_ast', False, str(exc))
try:
    ast.parse(engine)
    check('T6_engine_ast', True)
except Exception as exc:
    check('T6_engine_ast', False, str(exc))

print('PATCH 273 — INTERACTIVE SCENARIO PANEL TESTS')
print('─' * 66)
failed = 0
for name, ok, detail in tests:
    mark = 'PASS' if ok else 'FAIL'
    print(f"  {'✓' if ok else '✗'} [{mark}] {name}{(' — ' + detail) if detail else ''}")
    failed += 0 if ok else 1
print('─' * 66)
print(f'  Total: {len(tests)}  Passed: {len(tests)-failed}  Failed: {failed}')
print()
if failed:
    print('RESULT: patch273_tests=FAIL')
    sys.exit(1)
print('RESULT: patch273_tests=PASS')
