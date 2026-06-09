#!/usr/bin/env python3
"""
Patch 225B — Identity Vault Operational Profile Schema Migration Plan
Purpose: read-only planning pass after Patch 225A proved the live Identity Vault schema
is too thin for the full Self-Hosted Identity Vault operational profile blueprint.

Boundary: writes reports only under Forge memory. Does not modify Identity Vault code,
databases, service contracts, .env, node_modules, Forge registry, RMC memory, or agent identity state.
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
IDENTITY_ROOT = Path('/home/nic/identity-vault')
AIWEB_ROOT = Path('/home/nic/aiweb')
CANONICAL_DB = IDENTITY_ROOT / 'data' / 'identity_vault.db'
LEGACY_DB = IDENTITY_ROOT / 'vault.db'
ENV_PATH = IDENTITY_ROOT / '.env'
IDENTITY_DRAFT_CONTRACT = IDENTITY_ROOT / 'service_contracts' / 'identity_vault_readonly_service_contract.draft.json'
AIWEB_IDENTITY_CONTRACT = AIWEB_ROOT / 'service_contracts' / 'identity_vault.contract.json'
OUT_ROOT = FORGE_ROOT / 'memory' / 'identity_vault_patch225b_schema_migration_plan_v1'

USER_BLUEPRINT_FIELDS = [
    'user_id', 'canonical_name', 'spirit_name', 'project_affiliations', 'identity_tags',
    'version', 'last_updated', 'project_context', 'interaction_preferences', 'meta_rules',
    'session_state',
]

AGENT_BLUEPRINT_FIELDS = [
    'agent_id', 'canonical_name', 'version', 'last_updated', 'role', 'symbolic_signature',
    'description', 'capabilities', 'limitations', 'persona', 'voice_style',
    'quotes_or_character_inspiration', 'special_style_notes', 'permissions', 'authority',
    'enforcement_rules', 'forbidden_actions', 'session_state', 'last_action',
    'last_feedback', 'log_fields', 'timestamp',
]

# Conservative field aliases already present in live schema.
ALIASES = {
    'last_updated': {'updated_at'},
    'limitations': {'limits'},
    'enforcement_rules': {'enforcement'},
    'timestamp': {'updated_at', 'created_at'},
}

REQUIRED_CONTRACT_FIELDS = [
    'name', 'role', 'allowed_reads', 'allowed_writes', 'forbidden_writes',
    'api_or_cli_commands_exposed', 'audit_log_path', 'test_command', 'startup_command',
    'shutdown_command', 'health_check_command', 'owner_authority',
]


def _utc_ts() -> str:
    return _dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S_UTC')


def _sha256(path: Path, read_contents: bool = True) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    if not read_contents:
        st = path.stat()
        meta = f'{path}:{st.st_size}:{oct(st.st_mode & 0o777)}:{int(st.st_mtime)}'.encode('utf-8')
        return hashlib.sha256(meta).hexdigest()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: Path) -> Tuple[bool, Dict[str, Any] | None, str | None]:
    try:
        return True, json.loads(path.read_text(encoding='utf-8')), None
    except Exception as exc:  # noqa: BLE001
        return False, None, f'{type(exc).__name__}: {exc}'


def _connect_ro(path: Path) -> sqlite3.Connection:
    uri = f'file:{path}?mode=ro'
    return sqlite3.connect(uri, uri=True)


def _sqlite_summary(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        'path': str(path),
        'exists': path.exists(),
        'opened_readonly': False,
        'ok': False,
        'tables': [],
        'schemas': {},
        'row_counts': {},
        'error': None,
    }
    if not path.exists():
        out['error'] = 'missing database'
        return out
    try:
        con = _connect_ro(path)
        out['opened_readonly'] = True
        cur = con.cursor()
        rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        tables = [r[0] for r in rows]
        out['tables'] = tables
        for table in tables:
            info = cur.execute(f'PRAGMA table_info({table})').fetchall()
            out['schemas'][table] = [
                {'cid': r[0], 'name': r[1], 'type': r[2], 'notnull': bool(r[3]), 'default': r[4], 'pk': bool(r[5])}
                for r in info
            ]
            try:
                out['row_counts'][table] = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            except Exception as exc:  # noqa: BLE001
                out['row_counts'][table] = f'ERROR: {type(exc).__name__}: {exc}'
        con.close()
        out['ok'] = True
    except Exception as exc:  # noqa: BLE001
        out['error'] = f'{type(exc).__name__}: {exc}'
    return out


def _columns(schema: Dict[str, Any], table: str) -> List[str]:
    return [c['name'] for c in schema.get('schemas', {}).get(table, [])]


def _present_fields(required: List[str], live_cols: List[str]) -> Tuple[List[str], List[str], List[str]]:
    live = set(live_cols)
    present: List[str] = []
    alias_present: List[str] = []
    missing: List[str] = []
    for field in required:
        if field in live:
            present.append(field)
            continue
        alias_hits = sorted(ALIASES.get(field, set()) & live)
        if alias_hits:
            alias_present.append(f'{field} via {alias_hits[0]}')
            continue
        missing.append(field)
    return present, alias_present, missing


def _contract_summary(path: Path) -> Dict[str, Any]:
    ok, data, error = _load_json(path) if path.exists() else (False, None, 'missing')
    missing: List[str] = []
    if data:
        missing = [f for f in REQUIRED_CONTRACT_FIELDS if f not in data]
    return {
        'path': str(path),
        'exists': path.exists(),
        'json_ok': ok,
        'error': error,
        'name': data.get('name') if data else None,
        'missing_required_fields': missing,
        'ok': ok and not missing,
    }


def _proposed_strategy() -> Dict[str, Any]:
    return {
        'selected_strategy': 'hybrid_json_payload_plus_indexed_core_columns',
        'reasoning': [
            'The live schema already has useful indexed core columns such as agent_id/user_id, canonical_name, role, version, is_active, created_at, and updated_at.',
            'The manual blueprint contains many nested/list fields that fit poorly as separate scalar columns during bootstrap.',
            'A JSON payload column preserves the full operational identity exactly while keeping a few indexed columns available for fast lookup and safe previews.',
            'This avoids prematurely over-normalizing the schema before real agent usage patterns exist.',
        ],
        'agent_profiles_add_columns_plan': [
            {'name': 'operational_profile_json', 'type': 'TEXT', 'purpose': 'Full Agent Operational Identity JSON payload matching the manual blueprint.'},
            {'name': 'profile_schema_version', 'type': 'TEXT', 'purpose': 'Version of the operational identity payload schema.'},
            {'name': 'rmc_namespace', 'type': 'TEXT', 'purpose': 'Read-only pointer to the agent-scoped RMC namespace. Not memory content.'},
            {'name': 'activation_state', 'type': 'TEXT', 'purpose': 'inactive/draft/active lifecycle marker. Default must be inactive.'},
            {'name': 'profile_hash', 'type': 'TEXT', 'purpose': 'Hash of operational_profile_json for tamper-evidence.'},
            {'name': 'last_validated_at', 'type': 'TEXT', 'purpose': 'Timestamp of last schema/profile validation.'},
        ],
        'user_profiles_add_columns_plan': [
            {'name': 'operational_profile_json', 'type': 'TEXT', 'purpose': 'Full User Operational Identity JSON payload matching the manual blueprint.'},
            {'name': 'profile_schema_version', 'type': 'TEXT', 'purpose': 'Version of the operational identity payload schema.'},
            {'name': 'profile_hash', 'type': 'TEXT', 'purpose': 'Hash of operational_profile_json for tamper-evidence.'},
            {'name': 'last_validated_at', 'type': 'TEXT', 'purpose': 'Timestamp of last schema/profile validation.'},
        ],
        'default_safety_values': {
            'agent_profiles.activation_state': 'inactive',
            'agent_profiles.operational_profile_json': '{}',
            'user_profiles.operational_profile_json': '{}',
            'profile_schema_version': '1.0.0-blueprint',
        },
        'forbidden_in_migration': [
            'Do not create live agent profiles.',
            'Do not set activation_state to active.',
            'Do not write RMC memory.',
            'Do not read .env secret values.',
            'Do not delete legacy vault.db.',
            'Do not create EchoForge or ProtoForge2 live execution roots.',
        ],
    }


def _sql_plan() -> List[str]:
    return [
        '-- Patch 226 candidate SQL plan only; do not execute in Patch 225B.',
        'ALTER TABLE agent_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT \'{}\';',
        "ALTER TABLE agent_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint';",
        'ALTER TABLE agent_profiles ADD COLUMN rmc_namespace TEXT;',
        "ALTER TABLE agent_profiles ADD COLUMN activation_state TEXT NOT NULL DEFAULT 'inactive';",
        'ALTER TABLE agent_profiles ADD COLUMN profile_hash TEXT;',
        'ALTER TABLE agent_profiles ADD COLUMN last_validated_at TEXT;',
        'ALTER TABLE user_profiles ADD COLUMN operational_profile_json TEXT NOT NULL DEFAULT \'{}\';',
        "ALTER TABLE user_profiles ADD COLUMN profile_schema_version TEXT NOT NULL DEFAULT '1.0.0-blueprint';",
        'ALTER TABLE user_profiles ADD COLUMN profile_hash TEXT;',
        'ALTER TABLE user_profiles ADD COLUMN last_validated_at TEXT;',
        "CREATE INDEX IF NOT EXISTS idx_agent_profiles_agent_id ON agent_profiles(agent_id);",
        "CREATE INDEX IF NOT EXISTS idx_agent_profiles_activation_state ON agent_profiles(activation_state);",
        "CREATE INDEX IF NOT EXISTS idx_agent_profiles_rmc_namespace ON agent_profiles(rmc_namespace);",
        "CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);",
    ]


def _write_reports(report: Dict[str, Any], run_dir: Path, ts: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / f'{ts}_identity_vault_patch225b_schema_migration_plan.json'
    md_path = run_dir / f'{ts}_identity_vault_patch225b_schema_migration_plan.md'
    latest_json = OUT_ROOT / 'latest_identity_vault_patch225b_schema_migration_plan.json'
    latest_md = OUT_ROOT / 'latest_identity_vault_patch225b_schema_migration_plan.md'

    json_text = json.dumps(report, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding='utf-8')
    latest_json.write_text(json_text, encoding='utf-8')

    md = _render_md(report)
    md_path.write_text(md, encoding='utf-8')
    latest_md.write_text(md, encoding='utf-8')


def _render_md(r: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append('# Identity Vault Patch 225B Operational Profile Schema Migration Plan')
    lines.append('')
    lines.append(f"Timestamp: `{r['timestamp']}`")
    lines.append(f"Verdict: **{r['verdict']}**")
    lines.append('')
    lines.append('## Boundary')
    for b in r['boundary']:
        lines.append(f'- {b}')
    lines.append('')
    lines.append('## Current Schema Summary')
    db = r['canonical_database']
    lines.append(f"- canonical DB: `{db['path']}` opened_readonly=`{db['opened_readonly']}` ok=`{db['ok']}`")
    lines.append(f"- tables: `{', '.join(db.get('tables', []))}`")
    for table in ['agent_profiles', 'user_profiles']:
        lines.append(f"- `{table}` columns: `{', '.join(r['live_alignment'][table]['columns'])}`")
        lines.append(f"  - exact fields present: `{len(r['live_alignment'][table]['present_exact'])}/{len(r['live_alignment'][table]['required_fields'])}`")
        lines.append(f"  - alias fields present: `{len(r['live_alignment'][table]['present_by_alias'])}`")
        lines.append(f"  - missing fields: `{len(r['live_alignment'][table]['missing'])}`")
    lines.append('')
    lines.append('## Selected Migration Strategy')
    strategy = r['migration_strategy']
    lines.append(f"- selected: `{strategy['selected_strategy']}`")
    for reason in strategy['reasoning']:
        lines.append(f'- reason: {reason}')
    lines.append('')
    lines.append('## Planned Agent Profile Additions')
    for col in strategy['agent_profiles_add_columns_plan']:
        lines.append(f"- `{col['name']}` `{col['type']}` — {col['purpose']}")
    lines.append('')
    lines.append('## Planned User Profile Additions')
    for col in strategy['user_profiles_add_columns_plan']:
        lines.append(f"- `{col['name']}` `{col['type']}` — {col['purpose']}")
    lines.append('')
    lines.append('## SQL Plan Preview')
    lines.append('```sql')
    lines.extend(r['sql_plan_preview'])
    lines.append('```')
    lines.append('')
    lines.append('## Contract / Boundary Checks')
    for name, c in r['contracts'].items():
        lines.append(f"- `{name}` exists=`{c['exists']}` json_ok=`{c['json_ok']}` ok=`{c['ok']}` name=`{c['name']}`")
    lines.append('')
    lines.append('## Safety Checks')
    for k, v in r['safety_checks'].items():
        lines.append(f'- `{k}`: `{v}`')
    lines.append('')
    lines.append('## Findings')
    for finding in r['findings']:
        lines.append(f"- **{finding['level']}** `{finding['code']}` — {finding['message']}")
    lines.append('')
    lines.append('## Recommended Next Safe Step')
    lines.append('Create Patch 226 as a backed-up schema migration apply patch that adds JSON payload/profile metadata columns only. It must not create live agent profiles or activate identities. After Patch 226 passes, create inactive draft Gilligan/Athena/Neo profiles from the Identity Vault blueprint.')
    return '\n'.join(lines) + '\n'


def main() -> int:
    ts = _utc_ts()
    run_dir = OUT_ROOT / ts
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    before = {
        'env_stat': _sha256(ENV_PATH, read_contents=False),
        'canonical_db': _sha256(CANONICAL_DB),
        'legacy_db': _sha256(LEGACY_DB),
        'identity_draft_contract': _sha256(IDENTITY_DRAFT_CONTRACT),
        'aiweb_identity_contract': _sha256(AIWEB_IDENTITY_CONTRACT),
    }

    db_summary = _sqlite_summary(CANONICAL_DB)
    agent_cols = _columns(db_summary, 'agent_profiles')
    user_cols = _columns(db_summary, 'user_profiles')
    agent_present, agent_alias, agent_missing = _present_fields(AGENT_BLUEPRINT_FIELDS, agent_cols)
    user_present, user_alias, user_missing = _present_fields(USER_BLUEPRINT_FIELDS, user_cols)

    contracts = {
        'identity_vault_draft': _contract_summary(IDENTITY_DRAFT_CONTRACT),
        'aiweb_identity_vault': _contract_summary(AIWEB_IDENTITY_CONTRACT),
    }

    strategy = _proposed_strategy()
    sql = _sql_plan()

    after = {
        'env_stat': _sha256(ENV_PATH, read_contents=False),
        'canonical_db': _sha256(CANONICAL_DB),
        'legacy_db': _sha256(LEGACY_DB),
        'identity_draft_contract': _sha256(IDENTITY_DRAFT_CONTRACT),
        'aiweb_identity_contract': _sha256(AIWEB_IDENTITY_CONTRACT),
    }

    safety = {
        'env_secret_values_read': False,
        'env_stat_unchanged': before['env_stat'] == after['env_stat'],
        'canonical_db_sha_unchanged': before['canonical_db'] == after['canonical_db'],
        'legacy_db_sha_unchanged': before['legacy_db'] == after['legacy_db'],
        'identity_contract_draft_unchanged': before['identity_draft_contract'] == after['identity_draft_contract'],
        'aiweb_identity_contract_unchanged': before['aiweb_identity_contract'] == after['aiweb_identity_contract'],
        'database_write_performed': False,
        'agent_identity_activation_performed': False,
        'forge_tool_registry_modified': False,
        'schema_migration_executed': False,
    }

    representation_ready_after_plan = bool(strategy and sql)
    blockers = []
    if not db_summary.get('ok'):
        blockers.append('canonical DB did not open read-only')
    if not all(c['ok'] for c in contracts.values()):
        blockers.append('contract baseline invalid')
    if not all(safety.values()):
        blockers.append('safety snapshot changed or forbidden action detected')
    if not representation_ready_after_plan:
        blockers.append('migration strategy not produced')

    findings: List[Dict[str, str]] = []
    if agent_missing:
        findings.append({'level': 'INFO', 'code': 'IV_AGENT_PROFILE_JSON_PAYLOAD_REQUIRED', 'message': f'Live agent_profiles is missing {len(agent_missing)} blueprint fields; plan chooses a full operational_profile_json payload column plus indexed core columns.'})
    if user_missing:
        findings.append({'level': 'INFO', 'code': 'IV_USER_PROFILE_JSON_PAYLOAD_REQUIRED', 'message': f'Live user_profiles is missing {len(user_missing)} blueprint fields; plan chooses a full operational_profile_json payload column plus indexed core columns.'})
    findings.append({'level': 'INFO', 'code': 'IV_NO_SCHEMA_MIGRATION_EXECUTED', 'message': 'Patch 225B writes a migration plan only; no ALTER TABLE statements were executed.'})
    if blockers:
        for b in blockers:
            findings.append({'level': 'FAIL', 'code': 'IV_SCHEMA_PLAN_BLOCKER', 'message': b})

    verdict = 'PASS' if not blockers else 'FAIL'

    report: Dict[str, Any] = {
        'timestamp': ts,
        'verdict': verdict,
        'boundary': [
            'This patch is a read-only migration planning pass.',
            'It writes reports only under Forge memory.',
            'It does not modify Identity Vault code, databases, .env, node_modules, Forge registry, service contracts, RMC memory, or agent identity activation state.',
            'It does not read .env secret values.',
            'It does not execute ALTER TABLE or create live agent profiles.',
        ],
        'roots': {
            'forge_root': str(FORGE_ROOT),
            'identity_vault_root': str(IDENTITY_ROOT),
            'aiweb_root': str(AIWEB_ROOT),
            'canonical_db': str(CANONICAL_DB),
            'legacy_db_preserved': str(LEGACY_DB),
        },
        'blueprint_baseline': {
            'source': 'Self-Hosted Identity Vault manual, Operational Identity Profiles section',
            'required_user_profile_fields': USER_BLUEPRINT_FIELDS,
            'required_agent_profile_fields': AGENT_BLUEPRINT_FIELDS,
        },
        'canonical_database': db_summary,
        'live_alignment': {
            'agent_profiles': {
                'columns': agent_cols,
                'required_fields': AGENT_BLUEPRINT_FIELDS,
                'present_exact': agent_present,
                'present_by_alias': agent_alias,
                'missing': agent_missing,
            },
            'user_profiles': {
                'columns': user_cols,
                'required_fields': USER_BLUEPRINT_FIELDS,
                'present_exact': user_present,
                'present_by_alias': user_alias,
                'missing': user_missing,
            },
        },
        'migration_strategy': strategy,
        'sql_plan_preview': sql,
        'contracts': contracts,
        'safety_checks': safety,
        'findings': findings,
        'next_safe_step': 'Patch 226 should apply the schema migration after backup, adding JSON payload/profile metadata columns only. It must not create live agent profiles or activate identities.',
    }

    _write_reports(report, run_dir, ts)
    print('Identity Vault Patch 225B operational profile schema migration plan complete.')
    print(f'Run directory: {run_dir}')
    print(f'Report: {OUT_ROOT / "latest_identity_vault_patch225b_schema_migration_plan.md"}')
    print(f'JSON report: {OUT_ROOT / "latest_identity_vault_patch225b_schema_migration_plan.json"}')
    print(f'Verdict: {verdict}')
    return 0 if verdict == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
