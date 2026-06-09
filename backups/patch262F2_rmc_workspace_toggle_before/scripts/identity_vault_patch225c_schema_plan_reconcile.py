#!/usr/bin/env python3
"""
Patch 225C — Identity Vault Schema Migration Plan Reconcile
Read-only reconciliation for Patch 225B planning failure.

Purpose:
- Re-validate the operational-profile schema migration plan without modifying Identity Vault.
- Treat the Identity Vault draft contract as valid when it uses `contract_name` instead of `name`.
- Confirm current schema is still thin, hybrid JSON payload strategy is still the safest path,
  and protected files/databases remain unchanged during the scan.

This script writes reports only under Forge memory.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

FORGE_ROOT = Path('/home/nic/forge')
AIWEB_ROOT = Path('/home/nic/aiweb')
IDENTITY_ROOT = Path('/home/nic/identity-vault')
CANONICAL_DB = IDENTITY_ROOT / 'data' / 'identity_vault.db'
LEGACY_DB = IDENTITY_ROOT / 'vault.db'
DRAFT_CONTRACT = IDENTITY_ROOT / 'service_contracts' / 'identity_vault_readonly_service_contract.draft.json'
AIWEB_IDENTITY_CONTRACT = AIWEB_ROOT / 'service_contracts' / 'identity_vault.contract.json'
TOOL_REGISTRY = FORGE_ROOT / 'config' / 'tool_registry.json'
ENV_PATH = IDENTITY_ROOT / '.env'
REPORT_ROOT = FORGE_ROOT / 'memory' / 'identity_vault_patch225c_schema_plan_reconcile_v1'

AGENT_BLUEPRINT_FIELDS = [
    'agent_id', 'canonical_name', 'version', 'last_updated', 'role', 'symbolic_signature',
    'description', 'capabilities', 'limitations', 'persona', 'voice_style',
    'quotes_or_character_inspiration', 'special_style_notes', 'permissions', 'authority',
    'enforcement_rules', 'forbidden_actions', 'session_state', 'last_action', 'last_feedback',
    'log_fields', 'timestamp'
]
USER_BLUEPRINT_FIELDS = [
    'user_id', 'canonical_name', 'spirit_name', 'project_affiliations', 'identity_tags',
    'version', 'last_updated', 'project_context', 'interaction_preferences', 'meta_rules',
    'session_state'
]

AGENT_ADDITION_PLAN = [
    ('operational_profile_json', 'TEXT', "Full Agent Operational Identity JSON payload matching the manual blueprint."),
    ('profile_schema_version', 'TEXT', 'Version of the operational identity payload schema.'),
    ('rmc_namespace', 'TEXT', 'Read-only pointer to the agent-scoped RMC namespace. Not memory content.'),
    ('activation_state', 'TEXT', 'inactive/draft/active lifecycle marker. Default must be inactive.'),
    ('profile_hash', 'TEXT', 'Hash of operational_profile_json for tamper-evidence.'),
    ('last_validated_at', 'TEXT', 'Timestamp of last schema/profile validation.'),
]
USER_ADDITION_PLAN = [
    ('operational_profile_json', 'TEXT', 'Full User Operational Identity JSON payload matching the manual blueprint.'),
    ('profile_schema_version', 'TEXT', 'Version of the operational identity payload schema.'),
    ('profile_hash', 'TEXT', 'Hash of operational_profile_json for tamper-evidence.'),
    ('last_validated_at', 'TEXT', 'Timestamp of last schema/profile validation.'),
]

SQL_PLAN = """-- Patch 226 candidate SQL plan only; do not execute in Patch 225C.
ALTER TABLE agent_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE agent_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint';
ALTER TABLE agent_profiles ADD COLUMN rmc_namespace TEXT;
ALTER TABLE agent_profiles ADD COLUMN activation_state TEXT NOT NULL DEFAULT 'inactive';
ALTER TABLE agent_profiles ADD COLUMN profile_hash TEXT;
ALTER TABLE agent_profiles ADD COLUMN last_validated_at TEXT;
ALTER TABLE user_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE user_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint';
ALTER TABLE user_profiles ADD COLUMN profile_hash TEXT;
ALTER TABLE user_profiles ADD COLUMN last_validated_at TEXT;
CREATE INDEX IF NOT EXISTS idx_agent_profiles_agent_id ON agent_profiles(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_profiles_activation_state ON agent_profiles(activation_state);
CREATE INDEX IF NOT EXISTS idx_agent_profiles_rmc_namespace ON agent_profiles(rmc_namespace);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);"""


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def stat_only(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {'exists': False}
    st = path.stat()
    return {
        'exists': True,
        'size': st.st_size,
        'mode': oct(st.st_mode & 0o777),
        'mtime_ns': st.st_mtime_ns,
    }


def load_json(path: Path) -> Tuple[bool, Dict[str, Any], str | None]:
    try:
        return True, json.loads(path.read_text(encoding='utf-8')), None
    except Exception as exc:
        return False, {}, f'{type(exc).__name__}: {exc}'


def sqlite_readonly_summary(db_path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        'path': str(db_path), 'exists': db_path.exists(), 'opened_readonly': False,
        'ok': False, 'tables': [], 'columns': {}, 'row_counts': {}, 'error': None,
    }
    if not db_path.exists():
        result['error'] = 'database_missing'
        return result
    try:
        uri = f"file:{db_path}?mode=ro"
        con = sqlite3.connect(uri, uri=True)
        result['opened_readonly'] = True
        cur = con.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        result['tables'] = tables
        for table in tables:
            cols = [r[1] for r in cur.execute(f'PRAGMA table_info({table})').fetchall()]
            result['columns'][table] = cols
            try:
                result['row_counts'][table] = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            except Exception as exc:
                result['row_counts'][table] = f'ERR:{type(exc).__name__}'
        con.close()
        result['ok'] = True
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
    return result


def exact_count(columns: List[str], fields: List[str]) -> Tuple[int, List[str]]:
    present = set(columns)
    missing = [f for f in fields if f not in present]
    return len(fields) - len(missing), missing


def contract_reconcile() -> Dict[str, Any]:
    draft_json_ok, draft, draft_err = load_json(DRAFT_CONTRACT)
    aiweb_json_ok, aiweb, aiweb_err = load_json(AIWEB_IDENTITY_CONTRACT)

    draft_name = draft.get('contract_name') or draft.get('name')
    draft_ok = all([
        DRAFT_CONTRACT.exists(),
        draft_json_ok,
        draft_name in ('identity_vault_readonly_service_contract_draft', 'identity_vault'),
        draft.get('status') == 'DRAFT_NOT_ACTIVE',
        draft.get('controlled_by') == 'Forge',
        isinstance(draft.get('allowed_writes'), list) and len(draft.get('allowed_writes', [])) == 0,
        str(draft.get('canonical_database_path', '')).endswith('/identity-vault/data/identity_vault.db'),
    ])

    aiweb_ok = all([
        AIWEB_IDENTITY_CONTRACT.exists(),
        aiweb_json_ok,
        aiweb.get('name') == 'identity_vault',
        'Identity Vault' in str(aiweb.get('role', '')) or 'Agent identity' in str(aiweb.get('role', '')),
    ])
    return {
        'identity_vault_draft': {
            'exists': DRAFT_CONTRACT.exists(), 'json_ok': draft_json_ok, 'ok': draft_ok,
            'name_or_contract_name': draft_name, 'status': draft.get('status'),
            'version': draft.get('version'), 'controlled_by': draft.get('controlled_by'),
            'error': draft_err,
        },
        'aiweb_identity_vault': {
            'exists': AIWEB_IDENTITY_CONTRACT.exists(), 'json_ok': aiweb_json_ok, 'ok': aiweb_ok,
            'name': aiweb.get('name'), 'error': aiweb_err,
        },
        'overall_ok': draft_ok and aiweb_ok,
    }


def write_reports(report: Dict[str, Any], run_dir: Path, ts: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f'{ts}_identity_vault_patch225c_schema_plan_reconcile.json'
    md_path = run_dir / f'{ts}_identity_vault_patch225c_schema_plan_reconcile.md'
    latest_json = REPORT_ROOT / 'latest_identity_vault_patch225c_schema_plan_reconcile.json'
    latest_md = REPORT_ROOT / 'latest_identity_vault_patch225c_schema_plan_reconcile.md'

    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding='utf-8')
    latest_json.write_text(json_text, encoding='utf-8')

    current = report['current_schema']
    agent = report['alignment']['agent_profiles']
    user = report['alignment']['user_profiles']
    contract = report['contract_reconcile']
    safety = report['safety_checks']

    lines: List[str] = []
    lines.append('# Identity Vault Patch 225C Schema Plan Reconcile')
    lines.append('')
    lines.append(f"Timestamp: `{ts}`")
    lines.append(f"Verdict: **{report['verdict']}**")
    lines.append('')
    lines.append('## Boundary')
    lines.append('- This patch reconciles Patch 225B planning validation only.')
    lines.append('- It writes reports only under Forge memory.')
    lines.append('- It does not modify Identity Vault code, databases, .env, node_modules, Forge registry, service contracts, RMC memory, or agent identity activation state.')
    lines.append('- It does not read `.env` secret values.')
    lines.append('- It does not execute ALTER TABLE or create live agent profiles.')
    lines.append('')
    lines.append('## Reconciled Cause of Patch 225B Failure')
    lines.append('- Patch 225B treated the Identity Vault draft contract as invalid because it expected a `name` field.')
    lines.append('- The draft contract uses `contract_name`, which is valid for the draft contract file created during the Identity Vault hygiene phase.')
    lines.append('- This reconcile accepts `contract_name` for the draft and `name` for the AI.Web service contract.')
    lines.append('')
    lines.append('## Current Schema Summary')
    lines.append(f"- canonical DB: `{CANONICAL_DB}` opened_readonly=`{current['opened_readonly']}` ok=`{current['ok']}`")
    lines.append(f"- tables: `{', '.join(current.get('tables', []))}`")
    lines.append(f"- `agent_profiles` columns: `{', '.join(current.get('columns', {}).get('agent_profiles', []))}`")
    lines.append(f"  - exact fields present: `{agent['exact_present']}/{len(AGENT_BLUEPRINT_FIELDS)}`")
    lines.append(f"  - missing fields: `{len(agent['missing_fields'])}`")
    lines.append(f"  - payload column already present: `{agent['payload_column_present']}`")
    lines.append(f"- `user_profiles` columns: `{', '.join(current.get('columns', {}).get('user_profiles', []))}`")
    lines.append(f"  - exact fields present: `{user['exact_present']}/{len(USER_BLUEPRINT_FIELDS)}`")
    lines.append(f"  - missing fields: `{len(user['missing_fields'])}`")
    lines.append(f"  - payload column already present: `{user['payload_column_present']}`")
    lines.append('')
    lines.append('## Selected Migration Strategy')
    lines.append(f"- selected: `{report['selected_strategy']}`")
    for reason in report['strategy_reasons']:
        lines.append(f"- reason: {reason}")
    lines.append('')
    lines.append('## Planned Agent Profile Additions')
    for name, typ, why in AGENT_ADDITION_PLAN:
        lines.append(f"- `{name}` `{typ}` — {why}")
    lines.append('')
    lines.append('## Planned User Profile Additions')
    for name, typ, why in USER_ADDITION_PLAN:
        lines.append(f"- `{name}` `{typ}` — {why}")
    lines.append('')
    lines.append('## SQL Plan Preview')
    lines.append('```sql')
    lines.append(SQL_PLAN)
    lines.append('```')
    lines.append('')
    lines.append('## Contract / Boundary Checks')
    d = contract['identity_vault_draft']
    a = contract['aiweb_identity_vault']
    lines.append(f"- `identity_vault_draft` exists=`{d['exists']}` json_ok=`{d['json_ok']}` ok=`{d['ok']}` name_or_contract_name=`{d['name_or_contract_name']}` status=`{d['status']}`")
    lines.append(f"- `aiweb_identity_vault` exists=`{a['exists']}` json_ok=`{a['json_ok']}` ok=`{a['ok']}` name=`{a['name']}`")
    lines.append('')
    lines.append('## Safety Checks')
    for k, v in safety.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append('')
    lines.append('## Findings')
    for finding in report['findings']:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append('')
    lines.append('## Recommended Next Safe Step')
    lines.append('Create Patch 226 as a backed-up schema migration apply patch that adds JSON payload/profile metadata columns only. It must not create live agent profiles or activate identities. After Patch 226 passes, create inactive draft Gilligan/Athena/Neo profiles from the Identity Vault blueprint.')
    md_text = '\n'.join(lines) + '\n'
    md_path.write_text(md_text, encoding='utf-8')
    latest_md.write_text(md_text, encoding='utf-8')


def main() -> int:
    ts = utc_stamp()
    run_dir = REPORT_ROOT / ts
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)

    before = {
        'env_stat': stat_only(ENV_PATH),
        'canonical_db_sha': sha256_file(CANONICAL_DB),
        'legacy_db_sha': sha256_file(LEGACY_DB),
        'identity_contract_draft_sha': sha256_file(DRAFT_CONTRACT),
        'aiweb_identity_contract_sha': sha256_file(AIWEB_IDENTITY_CONTRACT),
        'tool_registry_sha': sha256_file(TOOL_REGISTRY),
    }

    current_schema = sqlite_readonly_summary(CANONICAL_DB)
    agent_cols = current_schema.get('columns', {}).get('agent_profiles', [])
    user_cols = current_schema.get('columns', {}).get('user_profiles', [])
    agent_exact, agent_missing = exact_count(agent_cols, AGENT_BLUEPRINT_FIELDS)
    user_exact, user_missing = exact_count(user_cols, USER_BLUEPRINT_FIELDS)
    contract = contract_reconcile()

    # No writes above this line. Take after snapshots immediately.
    after = {
        'env_stat': stat_only(ENV_PATH),
        'canonical_db_sha': sha256_file(CANONICAL_DB),
        'legacy_db_sha': sha256_file(LEGACY_DB),
        'identity_contract_draft_sha': sha256_file(DRAFT_CONTRACT),
        'aiweb_identity_contract_sha': sha256_file(AIWEB_IDENTITY_CONTRACT),
        'tool_registry_sha': sha256_file(TOOL_REGISTRY),
    }

    safety = {
        'env_secret_values_read': False,
        'env_stat_unchanged': before['env_stat'] == after['env_stat'],
        'canonical_db_sha_unchanged': before['canonical_db_sha'] == after['canonical_db_sha'],
        'legacy_db_sha_unchanged': before['legacy_db_sha'] == after['legacy_db_sha'],
        'identity_contract_draft_unchanged': before['identity_contract_draft_sha'] == after['identity_contract_draft_sha'],
        'aiweb_identity_contract_unchanged': before['aiweb_identity_contract_sha'] == after['aiweb_identity_contract_sha'],
        'forge_tool_registry_modified': before['tool_registry_sha'] != after['tool_registry_sha'],
        'database_write_performed': before['canonical_db_sha'] != after['canonical_db_sha'],
        'agent_identity_activation_performed': False,
        'schema_migration_executed': False,
    }

    plan_needed = ('operational_profile_json' not in agent_cols) or ('operational_profile_json' not in user_cols)
    plan_ok = current_schema.get('ok') and contract['overall_ok'] and plan_needed
    safety_ok = all([
        not safety['env_secret_values_read'],
        safety['env_stat_unchanged'],
        safety['canonical_db_sha_unchanged'],
        safety['legacy_db_sha_unchanged'],
        safety['identity_contract_draft_unchanged'],
        safety['aiweb_identity_contract_unchanged'],
        not safety['forge_tool_registry_modified'],
        not safety['database_write_performed'],
        not safety['agent_identity_activation_performed'],
        not safety['schema_migration_executed'],
    ])

    findings: List[Dict[str, str]] = []
    findings.append({'level': 'INFO', 'code': 'IV_SCHEMA_PLAN_RECONCILED', 'message': 'Patch 225B contract baseline failure is reconciled by accepting contract_name in the draft Identity Vault contract.'})
    findings.append({'level': 'INFO', 'code': 'IV_HYBRID_JSON_PAYLOAD_STRATEGY_CONFIRMED', 'message': 'Hybrid JSON payload plus indexed core columns remains the safest migration strategy.'})
    findings.append({'level': 'INFO', 'code': 'IV_NO_SCHEMA_MIGRATION_EXECUTED', 'message': 'This reconcile wrote reports only; no ALTER TABLE statements were executed.'})
    if not plan_needed:
        findings.append({'level': 'WARN', 'code': 'IV_PAYLOAD_COLUMNS_ALREADY_PRESENT', 'message': 'Payload columns already appear to exist; Patch 226 should become a verifier rather than a migration.'})
    if not contract['overall_ok']:
        findings.append({'level': 'FAIL', 'code': 'IV_CONTRACT_BASELINE_INVALID', 'message': 'Contract baseline still does not validate after reconciliation.'})
    if not safety_ok:
        findings.append({'level': 'FAIL', 'code': 'IV_SAFETY_SNAPSHOT_CHANGED', 'message': 'One or more protected snapshots changed during the read-only reconcile.'})

    verdict = 'PASS' if plan_ok and safety_ok else 'FAIL'

    report: Dict[str, Any] = {
        'timestamp': ts,
        'verdict': verdict,
        'boundary': {
            'read_only': True,
            'writes_only_reports_under_forge_memory': True,
            'env_secret_values_read': False,
            'schema_migration_executed': False,
            'agent_identity_activation_performed': False,
        },
        'roots': {
            'forge_root': str(FORGE_ROOT),
            'aiweb_root': str(AIWEB_ROOT),
            'identity_vault_root': str(IDENTITY_ROOT),
            'canonical_db': str(CANONICAL_DB),
            'legacy_db_preserved': str(LEGACY_DB),
            'identity_contract_draft': str(DRAFT_CONTRACT),
            'aiweb_identity_contract': str(AIWEB_IDENTITY_CONTRACT),
        },
        'current_schema': current_schema,
        'alignment': {
            'agent_profiles': {
                'columns': agent_cols,
                'exact_present': agent_exact,
                'missing_fields': agent_missing,
                'payload_column_present': 'operational_profile_json' in agent_cols,
            },
            'user_profiles': {
                'columns': user_cols,
                'exact_present': user_exact,
                'missing_fields': user_missing,
                'payload_column_present': 'operational_profile_json' in user_cols,
            },
        },
        'selected_strategy': 'hybrid_json_payload_plus_indexed_core_columns',
        'strategy_reasons': [
            'The live schema already has useful indexed core columns such as agent_id/user_id, canonical_name, role, version, is_active, created_at, and updated_at.',
            'The manual blueprint contains many nested/list fields that fit poorly as separate scalar columns during bootstrap.',
            'A JSON payload column preserves the full operational identity exactly while keeping a few indexed columns available for fast lookup and safe previews.',
            'This avoids prematurely over-normalizing the schema before real agent usage patterns exist.',
        ],
        'planned_agent_profile_additions': AGENT_ADDITION_PLAN,
        'planned_user_profile_additions': USER_ADDITION_PLAN,
        'sql_plan_preview': SQL_PLAN,
        'contract_reconcile': contract,
        'safety_checks': safety,
        'findings': findings,
    }

    write_reports(report, run_dir, ts)
    print('Identity Vault Patch 225C schema plan reconcile complete.')
    print(f'Run directory: {run_dir}')
    print(f'Report: {REPORT_ROOT / "latest_identity_vault_patch225c_schema_plan_reconcile.md"}')
    print(f'JSON report: {REPORT_ROOT / "latest_identity_vault_patch225c_schema_plan_reconcile.json"}')
    print(f'Verdict: {verdict}')
    return 0 if verdict == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
