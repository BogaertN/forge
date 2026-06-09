#!/usr/bin/env python3
# Patch 226C.3 — Dashboard Roadmap Source Reconcile
# Purpose: Patch the actual Forge roadmap source block so AI.Web bootstrap status advances to S19AT/S19AU.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

FORGE_ROOT = Path('/home/nic/forge')
MAIN = FORGE_ROOT / 'main.py'
REPORT_ROOT = FORGE_ROOT / 'memory' / 'dashboard_roadmap_patch226c3_source_reconcile_v1'
BACKUP_ROOT = FORGE_ROOT / 'backups' / 'patch226c3_dashboard_roadmap_source_reconcile_before'
TOOL_REGISTRY = FORGE_ROOT / 'config' / 'tool_registry.json'
IDENTITY_ROOT = Path('/home/nic/identity-vault')
CANONICAL_DB = IDENTITY_ROOT / 'data' / 'identity_vault.db'
LEGACY_DB = IDENTITY_ROOT / 'vault.db'
ENV_FILE = IDENTITY_ROOT / '.env'

TARGET_CURRENT = 'S19AT — Identity Vault Profile Seed Preview / Template Repair Gate'
TARGET_NEXT = 'Patch 226D — Identity Vault Template Repair Preview / No-Write JSON Repair Review'
MARKER_BEGIN = '# AIWEB_BOOTSTRAP_CANONICAL_ROADMAP_ROWS_BEGIN — Patch 226C.3'
MARKER_END = '# AIWEB_BOOTSTRAP_CANONICAL_ROADMAP_ROWS_END — Patch 226C.3'


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.UTC).strftime('%Y%m%d_%H%M%S_UTC')


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def stat_meta(path: Path) -> dict:
    if not path.exists():
        return {'exists': False}
    st = path.stat()
    return {'exists': True, 'size': st.st_size, 'mtime_ns': st.st_mtime_ns}


def replace_all(text: str, old: str, new: str, changes: list[str]) -> str:
    count = text.count(old)
    if count:
        text = text.replace(old, new)
        changes.append(f'replace_all:{old[:80]} count={count}')
    return text


def canonical_rows_code() -> str:
    # The row payload intentionally lives inside main.py so Forge's existing roadmap/status builders can read it.
    rows = [
        ('S19AC', 'DONE', 'Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only', 'Patch 183 — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only', 'Completed earlier runtime candidate sandbox staging step; superseded by AI.Web bootstrap integration work.'),
        ('S19AD', 'DONE', 'Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt', 'Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt', 'Completed earlier sandbox copy integrity gate; superseded by AI.Web bootstrap integration work.'),
        ('S19AE', 'DONE', 'RMC Integration Freeze / No-Move Snapshot', 'Patch 207 — RMC Integration Freeze', 'Freeze RMC integration state before moving, deleting, or wiring modules.'),
        ('S19AF', 'DONE', 'RMC Missing Module Install / Phase Parser, Drift Arbitrator, Echo Gate', 'Patch 209 — RMC Missing Modules Install and Orchestrator Repair', 'Install missing phase, drift, and echo modules and verify RMC orchestration.'),
        ('S19AG', 'DONE', 'Forge RMC Read-Only Wrapper', 'Patch 211 — Forge RMC Read-Only Wrapper', 'Expose RMC preview logic to Forge through a read-only wrapper.'),
        ('S19AH', 'DONE', 'Forge RMC Runtime Preview Check', 'Patch 213 — Forge Runtime Preview Check', 'Verify read-only RMC preview functions from Forge boundary.'),
        ('S19AI', 'DONE', 'Identity Vault Boundary Scan / Hygiene', 'Patch 217 — Identity Vault Boundary Scan', 'Scan Identity Vault boundary, unsafe files, and database state before wiring.'),
        ('S19AJ', 'DONE', 'Identity Vault Readiness Reconcile', 'Patch 217A — Identity Vault Readiness Reconcile', 'Reconcile Identity Vault readiness predicates and confirm draft contract boundary.'),
        ('S19AK', 'DONE', 'Identity Vault Read-Only Adapter', 'Patch 218 — Identity Vault Read-Only Adapter', 'Add read-only Forge adapter to the real Identity Vault on disk.'),
        ('S19AL', 'DONE', 'Identity Vault Drift Auto-Confirm Safety', 'Patch 220 — Drift Auto-Confirm Safety', 'Disable unsafe drift auto-confirm behavior and require manual gate.'),
        ('S19AM', 'DONE', 'Identity Vault DB Canonical Reconcile', 'Patch 221A — DB Canonical Reconcile', 'Normalize runtime references to the canonical Identity Vault database path.'),
        ('S19AN', 'DONE', 'AI.Web Service Contracts Apply', 'Patch 222 — AI.Web Service Contracts Apply', 'Create Forge/RMC/Identity Vault/ProtoForge2/EchoForge service contracts.'),
        ('S19AO', 'DONE', 'AI.Web Service Contracts Verify', 'Patch 223 — AI.Web Service Contracts Verify', 'Verify all five service contracts before connector wiring.'),
        ('S19AP', 'DONE', 'Forge AI.Web Read-Only Connector Commands', 'Patch 224 — AI.Web Read-Only Connector Commands', 'Add first read-only Forge connector commands for RMC and Identity Vault.'),
        ('S19AQ', 'DONE', 'Identity Vault Operational Schema Alignment', 'Patch 225A-225C — Identity Vault Schema Alignment', 'Compare blueprint profile structure to live schema and confirm hybrid JSON payload strategy.'),
        ('S19AR', 'DONE', 'Identity Vault Schema Migration Apply', 'Patch 226 — Identity Vault Schema Migration Apply', 'Add operational profile JSON and profile metadata columns to canonical database.'),
        ('S19AS', 'DONE', 'Legacy Profile Migration Preview / Preserve Legacy user789', 'Patch 226B — Legacy Profile Migration Preview', 'Preserve encrypted or encoded legacy user789 profile as reference only.'),
        ('S19AT', 'ACTIVE', 'Identity Vault Profile Seed Preview / Template Repair Gate', 'Patch 226C — Identity Vault Profile Seed Preview', 'Preview Nic, Gilligan, Athena, and Neo draft operational profiles; hold at template repair gate.'),
        ('S19AU', 'NEXT', 'Identity Vault Template Repair Preview', TARGET_NEXT, 'Preview repair of malformed Identity Vault JSON templates before writing profiles.'),
        ('S19AV', 'FUTURE', 'Apply Repaired Identity Vault Templates', 'Patch 226E — Apply Repaired Identity Vault Templates', 'Back up and apply valid Identity Vault user/agent templates.'),
        ('S19AW', 'FUTURE', 'Verify Repaired Identity Vault Templates', 'Patch 226F — Verify Repaired Identity Vault Templates', 'Verify repaired templates match operational identity blueprint.'),
        ('S19AX', 'FUTURE', 'Write Inactive Draft Identity Vault Profiles', 'Patch 227 — Write Inactive Draft Identity Vault Profiles', 'Write Nic, Gilligan, Athena, and Neo as inactive draft rows only.'),
        ('S19AY', 'FUTURE', 'Verify Inactive Draft Identity Vault Profiles', 'Patch 227A — Verify Inactive Draft Profiles', 'Verify draft rows, hashes, activation state, and RMC pointers.'),
        ('S19AZ', 'FUTURE', 'Upgrade Full Profile Read-Only Adapter', 'Patch 228 — Full Profile Read-Only Adapter Upgrade', 'Teach Forge connector to read full operational profile payload summaries.'),
        ('S19BA', 'FUTURE', 'RMC Namespace Scaffold Preview', 'Patch 229 — RMC Namespace Scaffold Preview', 'Preview shared and agent-scoped RMC namespace folders.'),
        ('S19BB', 'FUTURE', 'RMC Namespace Scaffold Apply / Empty Namespaces Only', 'Patch 229A — RMC Namespace Scaffold Apply', 'Create empty/staged RMC namespaces only, no memory content.'),
        ('S19BC', 'FUTURE', 'Bootstrap Handshake Dry-Run v2 / Inactive Profile Respected', 'Patch 230 — Bootstrap Handshake Dry-Run v2', 'Dry-run Forge → Identity Vault → RMC handshake while respecting inactive profile state.'),
        ('S19BD', 'FUTURE', 'Agent Activation Preflight Command', 'Patch 231A — Agent Activation Preflight', 'Add read-only agent activation preflight command.'),
        ('S19BE', 'FUTURE', 'Activate Gilligan as Governed Profile', 'Patch 232 — Activate Gilligan Governed Profile', 'Activate Gilligan only as a Forge-governed identity, not autonomous execution.'),
        ('S19BF', 'FUTURE', 'Gilligan Governed Handshake', 'Patch 233 — Gilligan Governed Handshake', 'Run first active governed Gilligan handshake.'),
        ('S19BG', 'FUTURE', 'RMC Test Receipt Write', 'Patch 234 — RMC Test Receipt Write', 'Write first controlled test receipt to Gilligan RMC namespace.'),
        ('S19BH', 'FUTURE', 'Athena Activation and Governed Handshake', 'Patch 235 — Athena Activation and Handshake', 'Activate Athena separately for governance/strategy identity.'),
        ('S19BI', 'FUTURE', 'Neo Activation and Governed Handshake', 'Patch 236 — Neo Activation and Handshake', 'Activate Neo separately for public/frontline identity.'),
        ('S19BJ', 'FUTURE', 'ProtoForge2 Discovery Scan', 'Patch 237 — ProtoForge2 Discovery Scan', 'Find real ProtoForge2 runtime root and commands.'),
        ('S19BK', 'FUTURE', 'ProtoForge2 Read-Only Connector', 'Patch 238 — ProtoForge2 Read-Only Connector', 'Add Forge read-only ProtoForge2 status connector.'),
        ('S19BL', 'FUTURE', 'ProtoForge2 Controlled Simulation Handshake', 'Patch 239 — ProtoForge2 Controlled Simulation Handshake', 'Let Forge send controlled simulation request to ProtoForge2.'),
        ('S19BM', 'FUTURE', 'EchoForge Discovery Scan', 'Patch 240 — EchoForge Discovery Scan', 'Find real EchoForge root and command surface.'),
        ('S19BN', 'FUTURE', 'EchoForge Read-Only Connector', 'Patch 241 — EchoForge Read-Only Connector', 'Add Forge read-only EchoForge status/capability connector.'),
        ('S19BO', 'FUTURE', 'EchoForge Build-Intention Preview', 'Patch 242 — EchoForge Build-Intention Preview', 'Preview EchoForge build intention through Forge without file changes.'),
        ('S19BP', 'FUTURE', 'Full EchoForge to Forge to ProtoForge2 to RMC Approval Loop', 'Patch 243+ — Full Approval Loop', 'Complete EchoForge → Forge → ProtoForge2 → RMC → Identity Vault approval loop.'),
    ]
    payload = json.dumps([
        {'id': rid, 'status': status, 'title': title, 'patch': patch, 'summary': summary}
        for rid, status, title, patch, summary in rows
    ], ensure_ascii=False, indent=8)
    return f'''\n    {MARKER_BEGIN}\n    _aiweb_bootstrap_canonical_rows = {payload}\n    _aiweb_bootstrap_ids = {{_r.get("id") for _r in _aiweb_bootstrap_canonical_rows}}\n    _existing_by_id = {{_r.get("id"): _r for _r in rows if isinstance(_r, dict)}}\n    _rebuilt_rows = []\n    _inserted_aiweb_bootstrap = False\n    for _r in rows:\n        _rid = _r.get("id") if isinstance(_r, dict) else None\n        if _rid in _aiweb_bootstrap_ids:\n            if not _inserted_aiweb_bootstrap:\n                _rebuilt_rows.extend(_aiweb_bootstrap_canonical_rows)\n                _inserted_aiweb_bootstrap = True\n            continue\n        _rebuilt_rows.append(_r)\n    if not _inserted_aiweb_bootstrap:\n        _rebuilt_rows.extend(_aiweb_bootstrap_canonical_rows)\n    rows = _rebuilt_rows\n    {MARKER_END}\n'''


def patch_text(original: str) -> tuple[str, list[str]]:
    text = original
    changes: list[str] = []

    # Correct the labels damaged by 226C.1/226C.2 so the display reflects the reconciled patch.
    text = replace_all(text, 'Dashboard Roadmap Panel Status — Patch 226C.1', 'Dashboard Roadmap Panel Status — Patch 226C.3', changes)
    text = replace_all(text, 'Dashboard Roadmap Panel List — Patch 226C.1', 'Dashboard Roadmap Panel List — Patch 226C.3', changes)
    text = replace_all(text, 'Dashboard Roadmap Panel Build — Patch 147', 'Dashboard Roadmap Panel Build — Patch 226C.3', changes)
    text = replace_all(text, 'Forge Roadmap Status — Build Sequence / Patch 146', 'Forge Roadmap Status — Build Sequence / Patch 226C.3', changes)

    # Move hard-coded selection logic from S19AC/S19AD to S19AT/S19AU.
    text = replace_all(text, 'elif rid == "S19AC":', 'elif rid == "S19AT":', changes)
    text = replace_all(text, 'elif rid == "S19AD":', 'elif rid == "S19AU":', changes)

    # Correct known payload state literals that drive status panels.
    text = replace_all(text,
        'payload["current_phase"] = "S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only"',
        f'payload["current_phase"] = "{TARGET_CURRENT}"',
        changes)
    text = replace_all(text,
        'payload["active_patch"] = "Patch 183 — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only"',
        'payload["active_patch"] = "Patch 226C — Identity Vault Profile Seed Preview / Template Repair Gate"',
        changes)
    text = replace_all(text,
        'payload["next_patch"] = "Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt"',
        f'payload["next_patch"] = "{TARGET_NEXT}"',
        changes)
    text = replace_all(text,
        'payload["recommended_next_patch"] = "Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt"',
        f'payload["recommended_next_patch"] = "{TARGET_NEXT}"',
        changes)
    text = replace_all(text,
        '"next_patch": "Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt"',
        f'"next_patch": "{TARGET_NEXT}"',
        changes)
    text = replace_all(text,
        '"recommended_next_patch": "Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt"',
        f'"recommended_next_patch": "{TARGET_NEXT}"',
        changes)

    # Fix exact stale row literals found by grep.
    stale_s19ac_next = 'rows.append({"id":"S19AC","status":"NEXT","title":"Identity Vault Profile Seed Preview / Template Repair Gate","patch":"Patch 183 — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only","summary":"Create a Forge-owned sandbox stage and copy candidate files only after exact SHA precheck."})'
    fixed_s19ac_done = 'rows.append({"id":"S19AC","status":"DONE","title":"Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only","patch":"Patch 183 — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only","summary":"Completed earlier runtime candidate sandbox staging step; superseded by AI.Web bootstrap integration work."})'
    text = replace_all(text, stale_s19ac_next, fixed_s19ac_done, changes)

    stale_s19ac_active = 'rows.append({"id":"S19AC","status":"ACTIVE","title":"Identity Vault Profile Seed Preview / Template Repair Gate","patch":"Patch 183 — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only","summary":"Create a Forge-owned sandbox stage and copy selected candidate files only after exact SHA precheck."})'
    text = replace_all(text, stale_s19ac_active, fixed_s19ac_done, changes)

    stale_s19ad_next = 'rows.append({"id":"S19AD","status":"NEXT","title":"Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt","patch":"Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt","summary":"Review the Forge-owned sandbox copy/readback receipt before sandbox execution or tests are allowed."})'
    fixed_s19ad_done = 'rows.append({"id":"S19AD","status":"DONE","title":"Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt","patch":"Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt","summary":"Completed earlier sandbox copy integrity gate; superseded by AI.Web bootstrap integration work."})'
    text = replace_all(text, stale_s19ad_next, fixed_s19ad_done, changes)

    # Inject canonical source rows after the S19AD row append in the runtime/dashboard source block.
    if MARKER_BEGIN not in text:
        anchor = fixed_s19ad_done
        idx = text.find(anchor)
        if idx != -1:
            insert_at = idx + len(anchor)
            text = text[:insert_at] + canonical_rows_code() + text[insert_at:]
            changes.append('insert:canonical_aiweb_bootstrap_rows_after_s19ad')
        else:
            changes.append('WARN:canonical_insert_anchor_not_found')
    else:
        changes.append('canonical_rows_marker_already_present')

    return text, changes


def verify_static(text: str) -> dict:
    checks = {
        'target_current_present': TARGET_CURRENT in text,
        'target_next_present': TARGET_NEXT in text,
        'marker_present': MARKER_BEGIN in text and MARKER_END in text,
        's19aq_present': '"id": "S19AQ"' in text or "'S19AQ'" in text,
        's19ax_present': '"id": "S19AX"' in text or "'S19AX'" in text,
        's19bp_present': '"id": "S19BP"' in text or "'S19BP'" in text,
        's19at_active_present': '"id": "S19AT"' in text and '"status": "ACTIVE"' in text,
        's19au_next_present': '"id": "S19AU"' in text and '"status": "NEXT"' in text,
        's19ac_done_present': '"id": "S19AC"' in text and '"status": "DONE"' in text,
        's19ad_done_present': '"id": "S19AD"' in text and '"status": "DONE"' in text,
        'old_current_assignment_absent': 'payload["current_phase"] = "S19AC — Runtime Candidate Sandbox Stage Create/Verify / Forge-Owned Copy Only"' not in text,
        'old_next_assignment_absent': 'payload["next_patch"] = "Patch 184 — Runtime Candidate Sandbox Copy Integrity Review / No-Write Readback Receipt"' not in text,
    }
    checks['ok'] = all(checks.values())
    return checks


def write_report(run_dir: Path, data: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    latest_md = REPORT_ROOT / 'latest_dashboard_roadmap_patch226c3_source_reconcile.md'
    latest_json = REPORT_ROOT / 'latest_dashboard_roadmap_patch226c3_source_reconcile.json'
    ts = data['timestamp']
    lines = []
    lines.append('# Forge Dashboard Roadmap Patch 226C.3 Source Reconcile')
    lines.append('')
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{data['verdict']}**")
    lines.append('')
    lines.append('## Boundary')
    lines.append('- Modifies only `/home/nic/forge/main.py` after backup.')
    lines.append('- Restores `main.py` automatically if compile/static verification fails.')
    lines.append('- Writes reports only under Forge memory.')
    lines.append('- Does not write Identity Vault databases, RMC memory, `.env`, agent memory, AI.Web wrappers, or Forge tool registry.')
    lines.append('')
    lines.append('## Target State')
    lines.append(f"- Current: `{TARGET_CURRENT}`")
    lines.append(f"- Next patch: `{TARGET_NEXT}`")
    lines.append('- S19AC through S19AS: `DONE`')
    lines.append('- S19AT: `ACTIVE`')
    lines.append('- S19AU: `NEXT`')
    lines.append('- S19AV through S19BP: `FUTURE`')
    lines.append('')
    lines.append('## Files')
    lines.append(f"- main.py exists: `{MAIN.exists()}`")
    lines.append(f"- backup: `{data.get('backup')}`")
    lines.append(f"- changed: `{data.get('changed')}`")
    lines.append(f"- restored on failure: `{data.get('restored_on_failure')}`")
    lines.append('')
    lines.append('## Changes')
    for c in data.get('changes', []):
        lines.append(f'- `{c}`')
    lines.append('')
    lines.append('## Compile Check')
    cc = data.get('compile', {})
    lines.append(f"- attempted: `{cc.get('attempted')}`")
    lines.append(f"- ok: `{cc.get('ok')}`")
    lines.append(f"- returncode: `{cc.get('returncode')}`")
    if cc.get('stderr_tail'):
        lines.append('```text')
        lines.append(cc.get('stderr_tail'))
        lines.append('```')
    lines.append('')
    lines.append('## Static Verification')
    for k, v in data.get('static', {}).items():
        lines.append(f'- `{k}`: `{v}`')
    lines.append('')
    lines.append('## Safety Checks')
    for k, v in data.get('safety', {}).items():
        lines.append(f'- `{k}`: `{v}`')
    lines.append('')
    lines.append('## Findings')
    for f in data.get('findings', []):
        lines.append(f"- **{f['level']}** `{f['code']}` — {f['message']}")
    lines.append('')
    lines.append('## Next Safe Step')
    if data['verdict'] == 'PASS':
        lines.append('Start Forge and run `forge-dashboard-roadmap-status`, `forge-dashboard-roadmap-list`, and `forge-roadmap-status`. If they show S19AT active and Patch 226D next, proceed to Patch 226D Identity Vault Template Repair Preview.')
    else:
        lines.append('Do not start Forge from a failed partial patch. This script should already have restored `main.py`; verify with `python -m py_compile main.py`, then inspect the report before continuing.')
    md = '\n'.join(lines) + '\n'
    (run_dir / f'{ts}_dashboard_roadmap_patch226c3_source_reconcile.md').write_text(md, encoding='utf-8')
    (run_dir / f'{ts}_dashboard_roadmap_patch226c3_source_reconcile.json').write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    latest_md.write_text(md, encoding='utf-8')
    latest_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def main() -> int:
    ts = utc_stamp()
    run_dir = REPORT_ROOT / ts
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    backup_dir = BACKUP_ROOT / ts
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / 'main.py'

    before = {
        'tool_registry_sha': sha256(TOOL_REGISTRY),
        'canonical_db_sha': sha256(CANONICAL_DB),
        'legacy_db_sha': sha256(LEGACY_DB),
        'env_meta': stat_meta(ENV_FILE),
        'main_sha': sha256(MAIN),
    }

    data = {
        'timestamp': ts,
        'verdict': 'FAIL',
        'backup': str(backup_path),
        'changed': False,
        'restored_on_failure': False,
        'changes': [],
        'compile': {'attempted': False, 'ok': False, 'returncode': None},
        'static': {},
        'safety': {},
        'findings': [],
    }

    if not MAIN.exists():
        data['findings'].append({'level': 'FAIL', 'code': 'MAIN_PY_MISSING', 'message': str(MAIN)})
        write_report(run_dir, data)
        print('Forge Dashboard Roadmap Patch 226C.3 source reconcile complete.')
        print(f'Run directory: {run_dir}')
        print(f'Report: {REPORT_ROOT / "latest_dashboard_roadmap_patch226c3_source_reconcile.md"}')
        print('Verdict: FAIL')
        return 1

    shutil.copy2(MAIN, backup_path)
    original = MAIN.read_text(encoding='utf-8')
    patched, changes = patch_text(original)
    data['changes'] = changes
    data['changed'] = patched != original

    if not data['changed']:
        data['findings'].append({'level': 'WARN', 'code': 'NO_TEXT_CHANGES', 'message': 'No main.py text changes were produced; source may already be patched or patterns moved.'})

    MAIN.write_text(patched, encoding='utf-8')

    compile_result = subprocess.run(['python', '-m', 'py_compile', str(MAIN)], cwd=str(FORGE_ROOT), text=True, capture_output=True)
    data['compile'] = {
        'attempted': True,
        'ok': compile_result.returncode == 0,
        'returncode': compile_result.returncode,
        'stderr_tail': compile_result.stderr[-2000:] if compile_result.stderr else '',
    }

    after_text = MAIN.read_text(encoding='utf-8') if MAIN.exists() else ''
    data['static'] = verify_static(after_text)

    after = {
        'tool_registry_sha': sha256(TOOL_REGISTRY),
        'canonical_db_sha': sha256(CANONICAL_DB),
        'legacy_db_sha': sha256(LEGACY_DB),
        'env_meta': stat_meta(ENV_FILE),
        'main_sha': sha256(MAIN),
    }
    data['safety'] = {
        'tool_registry_sha_unchanged': before['tool_registry_sha'] == after['tool_registry_sha'],
        'canonical_db_sha_unchanged': before['canonical_db_sha'] == after['canonical_db_sha'],
        'legacy_db_sha_unchanged': before['legacy_db_sha'] == after['legacy_db_sha'],
        'env_stat_unchanged': before['env_meta'] == after['env_meta'],
        'identity_vault_db_write_performed': before['canonical_db_sha'] != after['canonical_db_sha'] or before['legacy_db_sha'] != after['legacy_db_sha'],
        'forge_tool_registry_modified': before['tool_registry_sha'] != after['tool_registry_sha'],
        'main_py_modified': before['main_sha'] != after['main_sha'],
    }

    ok = data['compile']['ok'] and data['static'].get('ok') and all([
        data['safety']['tool_registry_sha_unchanged'],
        data['safety']['canonical_db_sha_unchanged'],
        data['safety']['legacy_db_sha_unchanged'],
        data['safety']['env_stat_unchanged'],
    ])

    if ok:
        data['verdict'] = 'PASS'
        data['findings'].append({'level': 'INFO', 'code': 'ROADMAP_SOURCE_RECONCILED', 'message': 'main.py static roadmap source now contains S19AT active and Patch 226D next state.'})
        data['findings'].append({'level': 'INFO', 'code': 'CANONICAL_ROWS_PRESENT', 'message': 'Canonical AI.Web bootstrap rows S19AC-S19BP are present in the roadmap source.'})
    else:
        # Restore automatically. This prevents another failed roadmap patch from leaving main.py half-mutated.
        shutil.copy2(backup_path, MAIN)
        data['restored_on_failure'] = True
        data['findings'].append({'level': 'FAIL', 'code': 'VERIFICATION_FAILED_MAIN_RESTORED', 'message': 'Compile/static/safety verification failed. main.py was restored from backup automatically.'})
        # Recalculate main_py_modified after restore.
        restored_after = sha256(MAIN)
        data['safety']['main_py_modified_after_restore'] = before['main_sha'] != restored_after

    write_report(run_dir, data)
    print('Forge Dashboard Roadmap Patch 226C.3 source reconcile complete.')
    print(f'Run directory: {run_dir}')
    print(f'Report: {REPORT_ROOT / "latest_dashboard_roadmap_patch226c3_source_reconcile.md"}')
    print(f'Verdict: {data["verdict"]}')
    return 0 if data['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
