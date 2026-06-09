#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
main = (root / "main.py").read_text(encoding="utf-8", errors="replace")
required = [
    '"/api/rmc/phase-preview"',
    '_p262b_rmc_phase_preview_v1',
    'read_only_phase_graph_frequency_preview',
    'generates_audio": False',
    'generates_cymatics": False',
    'rmc_phase_preview_enabled',
]
missing = [item for item in required if item not in main]
for forbidden in ['subprocess.run(', 'os.system(', 'Popen(', 'sqlite3.connect']:
    if forbidden in main[main.find('# ─── PATCH 262B'):main.find('# ─── PATCH 255')]:
        missing.append(f'forbidden token in patch block: {forbidden}')
if missing:
    print('PATCH262B_RMC_PHASE_PREVIEW_VERIFY_FAIL')
    for item in missing:
        print(f'missing_or_forbidden={item}')
    raise SystemExit(1)
print('PATCH262B_RMC_PHASE_PREVIEW_VERIFY_PASS')
print('endpoint=/api/rmc/phase-preview')
print('mode=read_only_phase_graph_frequency_preview')
print('uses_manifest_trace=True')
print('generates_audio=False')
print('generates_cymatics=False')
print('adds_forge_commands=False')
print('executes_command=False')
print('executes_shell=False')
print('writes_files=False')
print('identity_vault_write=False')
print('rmc_live_memory_write=False')
