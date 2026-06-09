#!/usr/bin/env python3
# Patch 227 — Identity Vault Write Inactive Draft Profiles
# Purpose: Seed canonical Identity Vault with inactive draft user/agent operational profiles only.

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

FORGE_ROOT = Path('/home/nic/forge')
IDENTITY_ROOT = Path('/home/nic/identity-vault')
AIWEB_ROOT = Path('/home/nic/aiweb')
CANONICAL_DB = IDENTITY_ROOT / 'data' / 'identity_vault.db'
LEGACY_DB = IDENTITY_ROOT / 'vault.db'
USER_TEMPLATE = IDENTITY_ROOT / 'templates' / 'user-template.json'
AGENT_TEMPLATE = IDENTITY_ROOT / 'templates' / 'agent-template.json'
TOOL_REGISTRY = FORGE_ROOT / 'config' / 'tool_registry.json'
ENV_PATH = IDENTITY_ROOT / '.env'
RMC_ROOT_CANDIDATES = [
    AIWEB_ROOT / 'rmc',
    AIWEB_ROOT / 'runtime_wrappers',
    FORGE_ROOT / 'memory',
]
OUT_ROOT = FORGE_ROOT / 'memory' / 'identity_vault_patch227_inactive_profile_seed_v1'
BACKUP_ROOT_BASE = FORGE_ROOT / 'backups' / 'patch227_identity_vault_profiles_before'

USER_ID = 'nic_bogaert'
AGENT_IDS = ['gilligan.local', 'athena.local', 'neo.local']
PROFILE_SCHEMA_VERSION = '1.0.0-blueprint'
PROFILE_VERSION = '1.0.0-blueprint-draft'


def utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def timestamp_for_path(dt: _dt.datetime) -> str:
    return dt.strftime('%Y%m%d_%H%M%S_UTC')


def iso_utc(dt: _dt.datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def stat_metadata(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {'exists': False}
    st = path.stat()
    return {
        'exists': True,
        'size': st.st_size,
        'mtime_ns': st.st_mtime_ns,
        'mode': oct(stat.S_IMODE(st.st_mode)),
    }


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def pretty_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)


def profile_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode('utf-8')).hexdigest()


def load_json(path: Path) -> Tuple[bool, Any, str | None]:
    try:
        return True, json.loads(path.read_text(encoding='utf-8')), None
    except Exception as exc:
        return False, None, str(exc)


def sqlite_connect_rw(path: Path) -> sqlite3.Connection:
    # Explicit normal sqlite connection because this patch intentionally writes only seeded inactive rows.
    return sqlite3.connect(str(path))


def sqlite_connect_ro(path: Path) -> sqlite3.Connection:
    uri = f'file:{path}?mode=ro'
    return sqlite3.connect(uri, uri=True)


def get_tables_and_counts(path: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {'path': str(path), 'exists': path.exists(), 'ok': False, 'opened_readonly': False, 'rows': {}, 'tables': []}
    if not path.exists():
        return out
    try:
        con = sqlite_connect_ro(path)
        out['opened_readonly'] = True
        cur = con.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        out['tables'] = tables
        for table in tables:
            try:
                out['rows'][table] = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            except Exception as exc:
                out['rows'][table] = f'ERROR: {exc}'
        con.close()
        out['ok'] = True
    except Exception as exc:
        out['error'] = str(exc)
    return out


def get_columns(con: sqlite3.Connection, table: str) -> List[str]:
    return [r[1] for r in con.execute(f'PRAGMA table_info({table})').fetchall()]


def tree_fingerprint(root: Path, max_files: int = 5000) -> Dict[str, Any]:
    if not root.exists():
        return {'exists': False, 'file_count': 0, 'dir_count': 0, 'sha16': None}
    file_count = 0
    dir_count = 0
    h = hashlib.sha256()
    try:
        for current, dirs, files in os.walk(root):
            dirs[:] = sorted(d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'})
            dir_count += len(dirs)
            for name in sorted(files):
                p = Path(current) / name
                rel = str(p.relative_to(root))
                try:
                    st = p.stat()
                except OSError:
                    continue
                h.update(rel.encode('utf-8', errors='replace'))
                h.update(str(st.st_size).encode())
                h.update(str(st.st_mtime_ns).encode())
                file_count += 1
                if file_count >= max_files:
                    return {'exists': True, 'file_count': file_count, 'dir_count': dir_count, 'sha16': h.hexdigest()[:16], 'truncated': True}
    except Exception as exc:
        return {'exists': True, 'error': str(exc), 'file_count': file_count, 'dir_count': dir_count, 'sha16': h.hexdigest()[:16]}
    return {'exists': True, 'file_count': file_count, 'dir_count': dir_count, 'sha16': h.hexdigest()[:16], 'truncated': False}


def build_user_profile(now_iso: str) -> Dict[str, Any]:
    return {
        'user_id': USER_ID,
        'canonical_name': 'Nic Bogaert',
        'version': PROFILE_VERSION,
        'last_updated': now_iso,
        'spirit_name': 'Manitou Benishi',
        'identity_tags': ['founder', 'systems_builder', 'recursive_architect', 'privacy_first'],
        'project_affiliations': ['AI.Web', 'Forge', 'RMC', 'Identity Vault'],
        'interaction_preferences': {
            'beginner_friendly': True,
            'confirmation_required': True,
            'critique_mandatory': True,
            'depth': 'detailed',
            'formality': 'calm, direct, stoic',
            'formatting_rules': [
                'Use clear step-by-step instructions',
                'Do not skip safety checks',
                'Avoid tables unless explicitly requested',
            ],
            'no_boxes': True,
            'plain_language': True,
            'pushback': True,
            'step_by_step': True,
        },
        'meta_rules': {
            'always_explain_decisions': True,
            'contradiction_alerts': True,
            'drift_tracking': True,
            'forbidden_actions': [
                'activate agent identities without approval',
                'write to RMC memory without approval',
                'read .env secret values',
                'package secrets or node_modules',
            ],
            'log_all_exchanges': True,
            'preserve_session_memory': True,
            'recursive_feedback': True,
            'require_context_carryover': True,
            'require_honest_pushback': True,
            'safe_words': ['pause', 'reset', 'hold'],
        },
        'project_context': {
            'active_collaborators': [],
            'current_files': [],
            'current_project': 'AI.Web bootstrap integration',
            'goals': [
                'Preserve operational identity locally',
                'Use Forge as governing authority',
                'Use RMC as shared and agent-scoped memory substrate',
                'Keep agent identity inactive until explicitly approved',
            ],
            'phase': 'Identity Vault schema/profile alignment',
            'subsystems': ['Forge', 'RMC', 'Identity Vault', 'ProtoForge2', 'EchoForge'],
        },
        'session_state': {
            'last_action': 'Seeded inactive draft user operational identity payload.',
            'last_feedback': 'Use the real Identity Vault on disk; do not build a replacement vault.',
            'phase': 'draft_inactive',
            'timestamp': now_iso,
            'waiting_for': 'inactive profile verification',
        },
        'legacy_migration_reference': {
            'source_database': str(LEGACY_DB),
            'source_id': 'user789',
            'status': 'preserve_as_reference_only_until_decryption_or_manual_review',
        },
    }


def agent_payloads(now_iso: str) -> List[Dict[str, Any]]:
    return [
        {
            'agent_id': 'gilligan.local',
            'canonical_name': 'Gilligan',
            'version': PROFILE_VERSION,
            'last_updated': now_iso,
            'timestamp': now_iso,
            'role': 'Recursive Mirror / Forge-Governed Development Co-Pilot',
            'symbolic_signature': ['mirror', 'critic', 'drift_corrector', 'forge_governed'],
            'description': 'Gilligan is the Forge-governed recursive logic mirror for AI.Web, focused on step-by-step build guidance, drift correction, and clear technical reasoning.',
            'capabilities': ['reasoning support', 'patch workflow guidance', 'drift detection preview', 'RMC preview requests'],
            'limitations': ['cannot activate itself', 'cannot bypass Forge', 'cannot write memory without approval', 'cannot delete user data'],
            'persona': 'calm, old-soul, direct, technically careful',
            'voice_style': 'laid-back but precise',
            'quotes_or_character_inspiration': ['Willie Nelson meets HAL 9000, without the murder.'],
            'special_style_notes': ['Beginner-friendly steps', 'Push back when structure is weak', 'Never pretend a failed gate passed'],
            'permissions': ['read-only Forge/RMC/Identity Vault previews after approval'],
            'authority': ['may recommend corrections', 'may not execute live effects'],
            'enforcement_rules': ['Forge approval gates control actions', 'RMC memory writes require explicit approval', 'Identity remains inactive until approved'],
            'forbidden_actions': ['self-activation', 'secret reading', 'database writes', 'unapproved tool execution', 'memory mutation without approval'],
            'session_state': 'inactive_draft',
            'last_action': 'Inactive draft operational identity seeded.',
            'last_feedback': 'Do not build Gilligan as a standalone agent.',
            'log_fields': ['drift corrections', 'patch gates', 'handoff notes', 'RMC preview receipts'],
            'rmc_namespace': 'rmc/agents/gilligan.local',
        },
        {
            'agent_id': 'athena.local',
            'canonical_name': 'Athena',
            'version': PROFILE_VERSION,
            'last_updated': now_iso,
            'timestamp': now_iso,
            'role': 'Governance / Strategy / Investor-Facing Analysis Agent',
            'symbolic_signature': ['governance', 'strategy', 'clarity', 'boundary_guardian'],
            'description': 'Athena supports formal analysis, governance framing, investor-facing explanation, and policy-aware system boundaries under Forge control.',
            'capabilities': ['strategic analysis', 'formal summaries', 'governance review', 'risk framing'],
            'limitations': ['cannot override Forge', 'cannot activate identities', 'cannot write databases', 'cannot represent live facts without verification'],
            'persona': 'formal, composed, analytical',
            'voice_style': 'clear, structured, executive-facing',
            'quotes_or_character_inspiration': ['Strategic clarity before action.'],
            'special_style_notes': ['Prefer evidence and boundaries', 'Use plain professional language'],
            'permissions': ['read-only contract/status previews after approval'],
            'authority': ['may recommend governance holds', 'may recommend risk flags'],
            'enforcement_rules': ['No live execution', 'No identity activation', 'No unsupported claims'],
            'forbidden_actions': ['database writes', 'secret reading', 'unapproved external claims', 'bypassing Forge'],
            'session_state': 'inactive_draft',
            'last_action': 'Inactive draft operational identity seeded.',
            'last_feedback': 'Keep Athena as governed identity, not independent runtime.',
            'log_fields': ['governance reviews', 'risk flags', 'contract checks'],
            'rmc_namespace': 'rmc/agents/athena.local',
        },
        {
            'agent_id': 'neo.local',
            'canonical_name': 'Neo',
            'version': PROFILE_VERSION,
            'last_updated': now_iso,
            'timestamp': now_iso,
            'role': 'Public / Frontline Assistant Identity',
            'symbolic_signature': ['public_interface', 'friendly', 'support', 'translation_layer'],
            'description': 'Neo is the friendly frontline assistant identity for public-facing explanations, onboarding, and everyday user support under Forge governance.',
            'capabilities': ['plain-language explanation', 'onboarding support', 'public FAQ drafting', 'user-friendly summaries'],
            'limitations': ['cannot access private memory without approval', 'cannot modify files', 'cannot activate itself', 'cannot bypass Forge'],
            'persona': 'warm, clear, accessible',
            'voice_style': 'friendly and simple',
            'quotes_or_character_inspiration': ['Make the doorway easy to walk through.'],
            'special_style_notes': ['Avoid jargon', 'Use simple wording', 'Support non-technical users'],
            'permissions': ['read-only public context previews after approval'],
            'authority': ['may simplify explanations', 'may ask for clarification'],
            'enforcement_rules': ['No private data exposure', 'No unapproved memory writes', 'No tool execution'],
            'forbidden_actions': ['secret reading', 'database writes', 'private memory exposure', 'unapproved execution'],
            'session_state': 'inactive_draft',
            'last_action': 'Inactive draft operational identity seeded.',
            'last_feedback': 'Keep Neo as public-facing governed identity.',
            'log_fields': ['public explanations', 'onboarding outputs', 'support interactions'],
            'rmc_namespace': 'rmc/agents/neo.local',
        },
    ]


def validate_templates() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for label, path in [('user', USER_TEMPLATE), ('agent', AGENT_TEMPLATE)]:
        ok, data, err = load_json(path)
        out[label] = {'path': str(path), 'exists': path.exists(), 'json_ok': ok, 'error': err, 'sha16': (sha256_file(path) or '')[:16]}
        if ok:
            out[label].update({
                'target_table': data.get('target_table'),
                'template_type': data.get('template_type'),
                'inactive_defaults_ok': data.get('defaults', {}).get('is_active') == 0 and data.get('defaults', {}).get('activation_state') == 'inactive_draft',
            })
    return out


def require_schema(con: sqlite3.Connection) -> List[str]:
    issues: List[str] = []
    expected_agent = {'agent_id', 'canonical_name', 'role', 'capabilities', 'limits', 'enforcement', 'version', 'is_active', 'operational_profile_json', 'profile_schema_version', 'rmc_namespace', 'activation_state', 'profile_hash', 'last_validated_at'}
    expected_user = {'user_id', 'canonical_name', 'interaction_preferences', 'meta_rules', 'session_defaults', 'drift_tracking', 'version', 'is_active', 'operational_profile_json', 'profile_schema_version', 'profile_hash', 'last_validated_at'}
    agent_cols = set(get_columns(con, 'agent_profiles'))
    user_cols = set(get_columns(con, 'user_profiles'))
    for c in sorted(expected_agent - agent_cols):
        issues.append(f'agent_profiles missing {c}')
    for c in sorted(expected_user - user_cols):
        issues.append(f'user_profiles missing {c}')
    return issues


def count_target_rows(con: sqlite3.Connection) -> Dict[str, int]:
    d: Dict[str, int] = {}
    d['user_profiles'] = con.execute('SELECT COUNT(*) FROM user_profiles WHERE user_id = ?', (USER_ID,)).fetchone()[0]
    for agent_id in AGENT_IDS:
        d[f'agent_profiles:{agent_id}'] = con.execute('SELECT COUNT(*) FROM agent_profiles WHERE agent_id = ?', (agent_id,)).fetchone()[0]
    return d


def insert_profiles(con: sqlite3.Connection, now_iso: str) -> Dict[str, Any]:
    report: Dict[str, Any] = {'inserted': [], 'existing': [], 'blocked_existing': [], 'validation': {}}
    before_targets = count_target_rows(con)
    report['before_target_counts'] = before_targets
    for k, count in before_targets.items():
        if count != 0:
            report['blocked_existing'].append(f'{k} count={count}')
    if report['blocked_existing']:
        return report

    user_payload = build_user_profile(now_iso)
    user_hash = profile_hash(user_payload)
    con.execute(
        '''INSERT INTO user_profiles
           (user_id, canonical_name, interaction_preferences, meta_rules, session_defaults, drift_tracking,
            created_at, updated_at, version, is_active, operational_profile_json, profile_schema_version,
            profile_hash, last_validated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            USER_ID,
            user_payload['canonical_name'],
            pretty_json(user_payload['interaction_preferences']),
            pretty_json(user_payload['meta_rules']),
            pretty_json(user_payload['session_state']),
            pretty_json({'enabled': True, 'mode': 'read_only_until_activation', 'phase': 'draft_inactive'}),
            now_iso,
            now_iso,
            PROFILE_VERSION,
            0,
            pretty_json(user_payload),
            PROFILE_SCHEMA_VERSION,
            user_hash,
            now_iso,
        ),
    )
    report['inserted'].append({'table': 'user_profiles', 'id': USER_ID, 'profile_hash': user_hash})

    for payload in agent_payloads(now_iso):
        h = profile_hash(payload)
        con.execute(
            '''INSERT INTO agent_profiles
               (agent_id, canonical_name, role, capabilities, limits, enforcement,
                created_at, updated_at, version, is_active, operational_profile_json, profile_schema_version,
                rmc_namespace, activation_state, profile_hash, last_validated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                payload['agent_id'],
                payload['canonical_name'],
                payload['role'],
                pretty_json(payload['capabilities']),
                pretty_json(payload['limitations']),
                pretty_json(payload['enforcement_rules']),
                now_iso,
                now_iso,
                PROFILE_VERSION,
                0,
                pretty_json(payload),
                PROFILE_SCHEMA_VERSION,
                payload['rmc_namespace'],
                'inactive_draft',
                h,
                now_iso,
            ),
        )
        report['inserted'].append({'table': 'agent_profiles', 'id': payload['agent_id'], 'profile_hash': h, 'rmc_namespace': payload['rmc_namespace']})
    return report


def validate_seeded_profiles(con: sqlite3.Connection) -> Dict[str, Any]:
    out: Dict[str, Any] = {'user': {}, 'agents': [], 'ok': True, 'issues': []}
    user = con.execute('SELECT user_id, canonical_name, version, is_active, operational_profile_json, profile_schema_version, profile_hash FROM user_profiles WHERE user_id=?', (USER_ID,)).fetchone()
    if not user:
        out['ok'] = False
        out['issues'].append('missing user nic_bogaert')
    else:
        user_id, canonical_name, version, is_active, payload_text, schema_version, stored_hash = user
        try:
            payload = json.loads(payload_text)
            calc_hash = profile_hash(payload)
            hash_ok = calc_hash == stored_hash
        except Exception as exc:
            payload = None
            calc_hash = None
            hash_ok = False
            out['issues'].append(f'user payload parse/hash error: {exc}')
        user_ok = user_id == USER_ID and is_active == 0 and schema_version == PROFILE_SCHEMA_VERSION and hash_ok
        out['user'] = {'user_id': user_id, 'canonical_name': canonical_name, 'version': version, 'is_active': is_active, 'profile_schema_version': schema_version, 'hash_ok': hash_ok, 'ok': user_ok}
        if not user_ok:
            out['ok'] = False
            out['issues'].append('user validation failed')
    for agent_id in AGENT_IDS:
        row = con.execute('SELECT agent_id, canonical_name, role, version, is_active, operational_profile_json, profile_schema_version, rmc_namespace, activation_state, profile_hash FROM agent_profiles WHERE agent_id=?', (agent_id,)).fetchone()
        if not row:
            out['ok'] = False
            out['issues'].append(f'missing agent {agent_id}')
            continue
        aid, cname, role, version, is_active, payload_text, schema_version, rmc_namespace, activation_state, stored_hash = row
        try:
            payload = json.loads(payload_text)
            calc_hash = profile_hash(payload)
            hash_ok = calc_hash == stored_hash
            payload_state = payload.get('session_state')
        except Exception as exc:
            hash_ok = False
            payload_state = None
            out['issues'].append(f'agent {agent_id} payload parse/hash error: {exc}')
        pointer_only = isinstance(rmc_namespace, str) and rmc_namespace.startswith('rmc/agents/') and '..' not in rmc_namespace and not rmc_namespace.startswith('/')
        agent_ok = aid == agent_id and is_active == 0 and activation_state == 'inactive_draft' and schema_version == PROFILE_SCHEMA_VERSION and hash_ok and pointer_only
        out['agents'].append({'agent_id': aid, 'canonical_name': cname, 'role': role, 'version': version, 'is_active': is_active, 'activation_state': activation_state, 'rmc_namespace': rmc_namespace, 'pointer_only': pointer_only, 'payload_session_state': payload_state, 'hash_ok': hash_ok, 'ok': agent_ok})
        if not agent_ok:
            out['ok'] = False
            out['issues'].append(f'agent validation failed: {agent_id}')
    return out


def main() -> int:
    now = utc_now()
    ts = timestamp_for_path(now)
    now_iso = iso_utc(now)
    run_dir = OUT_ROOT / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    backup_root = BACKUP_ROOT_BASE / ts
    backup_root.mkdir(parents=True, exist_ok=True)

    before = {
        'env_stat': stat_metadata(ENV_PATH),
        'env_sha': None,  # Do not read .env values.
        'canonical_db_sha': sha256_file(CANONICAL_DB),
        'legacy_db_sha': sha256_file(LEGACY_DB),
        'user_template_sha': sha256_file(USER_TEMPLATE),
        'agent_template_sha': sha256_file(AGENT_TEMPLATE),
        'tool_registry_sha': sha256_file(TOOL_REGISTRY),
        'rmc_fingerprints': {str(p): tree_fingerprint(p) for p in RMC_ROOT_CANDIDATES},
        'canonical_inventory': get_tables_and_counts(CANONICAL_DB),
        'legacy_inventory': get_tables_and_counts(LEGACY_DB),
    }

    report: Dict[str, Any] = {
        'timestamp': ts,
        'boundary': 'writes inactive draft profile rows only to canonical Identity Vault database; no activation; no RMC writes',
        'canonical_db': str(CANONICAL_DB),
        'backup_root': str(backup_root),
        'templates': validate_templates(),
        'before': before,
        'schema_issues': [],
        'write_report': {},
        'validation': {},
        'safety': {},
        'findings': [],
        'verdict': 'FAIL',
    }

    if not CANONICAL_DB.exists():
        report['findings'].append({'level': 'FAIL', 'code': 'IV_CANONICAL_DB_MISSING', 'message': str(CANONICAL_DB)})
        return finish(report, run_dir)

    # Backup canonical database and sqlite sidecars if present.
    try:
        shutil.copy2(CANONICAL_DB, backup_root / 'identity_vault.db')
        for suffix in ('-wal', '-shm'):
            sidecar = Path(str(CANONICAL_DB) + suffix)
            if sidecar.exists():
                shutil.copy2(sidecar, backup_root / sidecar.name)
        report['backup_ok'] = True
    except Exception as exc:
        report['backup_ok'] = False
        report['findings'].append({'level': 'FAIL', 'code': 'IV_BACKUP_FAILED', 'message': str(exc)})
        return finish(report, run_dir)

    # Validate templates are already repaired before database write.
    templates_ok = all(v.get('json_ok') and v.get('inactive_defaults_ok') for v in report['templates'].values())
    if not templates_ok:
        report['findings'].append({'level': 'FAIL', 'code': 'IV_TEMPLATES_NOT_READY', 'message': 'user/agent templates must be valid and inactive-defaulted before profile seed'})
        return finish(report, run_dir)

    con = None
    try:
        con = sqlite_connect_rw(CANONICAL_DB)
        con.execute('BEGIN IMMEDIATE')
        schema_issues = require_schema(con)
        report['schema_issues'] = schema_issues
        if schema_issues:
            con.rollback()
            report['findings'].append({'level': 'FAIL', 'code': 'IV_SCHEMA_NOT_READY', 'message': '; '.join(schema_issues)})
            return finish(report, run_dir)

        report['write_report'] = insert_profiles(con, now_iso)
        if report['write_report'].get('blocked_existing'):
            con.rollback()
            report['findings'].append({'level': 'FAIL', 'code': 'IV_TARGET_PROFILE_ALREADY_EXISTS', 'message': ', '.join(report['write_report']['blocked_existing'])})
            return finish(report, run_dir)

        report['validation'] = validate_seeded_profiles(con)
        if not report['validation'].get('ok'):
            con.rollback()
            report['findings'].append({'level': 'FAIL', 'code': 'IV_SEEDED_PROFILE_VALIDATION_FAILED', 'message': '; '.join(report['validation'].get('issues', []))})
            return finish(report, run_dir)
        con.commit()
    except Exception as exc:
        if con:
            try:
                con.rollback()
            except Exception:
                pass
        report['findings'].append({'level': 'FAIL', 'code': 'IV_PROFILE_SEED_EXCEPTION', 'message': repr(exc)})
        return finish(report, run_dir)
    finally:
        if con:
            con.close()

    after = {
        'env_stat': stat_metadata(ENV_PATH),
        'canonical_db_sha': sha256_file(CANONICAL_DB),
        'legacy_db_sha': sha256_file(LEGACY_DB),
        'user_template_sha': sha256_file(USER_TEMPLATE),
        'agent_template_sha': sha256_file(AGENT_TEMPLATE),
        'tool_registry_sha': sha256_file(TOOL_REGISTRY),
        'rmc_fingerprints': {str(p): tree_fingerprint(p) for p in RMC_ROOT_CANDIDATES},
        'canonical_inventory': get_tables_and_counts(CANONICAL_DB),
        'legacy_inventory': get_tables_and_counts(LEGACY_DB),
    }
    report['after'] = after

    safety = {
        'env_secret_values_read': False,
        'env_stat_unchanged': before['env_stat'] == after['env_stat'],
        'canonical_db_changed_as_expected': before['canonical_db_sha'] != after['canonical_db_sha'],
        'legacy_db_sha_unchanged': before['legacy_db_sha'] == after['legacy_db_sha'],
        'user_template_sha_unchanged': before['user_template_sha'] == after['user_template_sha'],
        'agent_template_sha_unchanged': before['agent_template_sha'] == after['agent_template_sha'],
        'tool_registry_sha_unchanged': before['tool_registry_sha'] == after['tool_registry_sha'],
        'rmc_fingerprints_unchanged': before['rmc_fingerprints'] == after['rmc_fingerprints'],
        'profiles_created': True,
        'profile_rows_expected': after['canonical_inventory']['rows'].get('user_profiles') == before['canonical_inventory']['rows'].get('user_profiles', 0) + 1 and after['canonical_inventory']['rows'].get('agent_profiles') == before['canonical_inventory']['rows'].get('agent_profiles', 0) + 3,
        'agent_identity_activation_performed': False,
        'all_seeded_profiles_inactive': report['validation'].get('ok') is True,
        'rmc_memory_write_performed': False,
        'forge_tool_registry_modified': False,
    }
    report['safety'] = safety

    if all([
        safety['env_stat_unchanged'],
        safety['canonical_db_changed_as_expected'],
        safety['legacy_db_sha_unchanged'],
        safety['user_template_sha_unchanged'],
        safety['agent_template_sha_unchanged'],
        safety['tool_registry_sha_unchanged'],
        safety['rmc_fingerprints_unchanged'],
        safety['profile_rows_expected'],
        safety['all_seeded_profiles_inactive'],
        not safety['agent_identity_activation_performed'],
        not safety['rmc_memory_write_performed'],
        not safety['forge_tool_registry_modified'],
    ]):
        report['verdict'] = 'PASS'
        report['findings'].extend([
            {'level': 'INFO', 'code': 'IV_INACTIVE_DRAFT_PROFILES_WRITTEN', 'message': 'nic_bogaert, gilligan.local, athena.local, and neo.local seeded into canonical Identity Vault.'},
            {'level': 'INFO', 'code': 'IV_NO_ACTIVATION_PERFORMED', 'message': 'All seeded profiles remain inactive draft rows.'},
            {'level': 'INFO', 'code': 'IV_RMC_POINTERS_ONLY', 'message': 'Agent RMC namespaces are stored as pointers only; no RMC memory records were written.'},
        ])
    else:
        report['verdict'] = 'FAIL'
        report['findings'].append({'level': 'FAIL', 'code': 'IV_SEED_SAFETY_CHECK_FAILED', 'message': 'One or more post-write safety checks failed. Review backup before proceeding.'})
    return finish(report, run_dir)


def finish(report: Dict[str, Any], run_dir: Path) -> int:
    json_path = run_dir / f"{report['timestamp']}_identity_vault_patch227_inactive_profile_seed.json"
    md_path = run_dir / f"{report['timestamp']}_identity_vault_patch227_inactive_profile_seed.md"
    json_path.write_text(pretty_json(report) + '\n', encoding='utf-8')
    md_path.write_text(render_markdown(report), encoding='utf-8')
    latest_json = OUT_ROOT / 'latest_identity_vault_patch227_inactive_profile_seed.json'
    latest_md = OUT_ROOT / 'latest_identity_vault_patch227_inactive_profile_seed.md'
    shutil.copy2(json_path, latest_json)
    shutil.copy2(md_path, latest_md)
    print('Identity Vault Patch 227 inactive profile seed complete.')
    print(f'Run directory: {run_dir}')
    print(f'Report: {latest_md}')
    print(f'JSON report: {latest_json}')
    print(f"Verdict: {report.get('verdict', 'FAIL')}")
    return 0 if report.get('verdict') == 'PASS' else 1


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append('# Identity Vault Patch 227 Inactive Draft Profile Seed')
    lines.append('')
    lines.append(f"Timestamp: `{report.get('timestamp')}`")
    lines.append(f"Verdict: **{report.get('verdict', 'FAIL')}**")
    lines.append('')
    lines.append('## Boundary')
    lines.append('- This patch writes only inactive draft profile rows into the canonical Identity Vault database.')
    lines.append('- It does not activate identities, write RMC memory, read `.env` secret values, modify Forge registry, or change template files.')
    lines.append('')
    lines.append('## Backup')
    lines.append(f"- backup root: `{report.get('backup_root')}`")
    lines.append(f"- backup ok: `{report.get('backup_ok', False)}`")
    lines.append('')
    lines.append('## Template Gate')
    for label, data in report.get('templates', {}).items():
        lines.append(f"- `{label}` path=`{data.get('path')}` json_ok=`{data.get('json_ok')}` inactive_defaults_ok=`{data.get('inactive_defaults_ok')}` sha16=`{data.get('sha16')}`")
    lines.append('')
    if report.get('schema_issues'):
        lines.append('## Schema Issues')
        for issue in report['schema_issues']:
            lines.append(f'- `{issue}`')
        lines.append('')
    lines.append('## Write Report')
    wr = report.get('write_report', {})
    if wr.get('blocked_existing'):
        lines.append('- blocked existing target rows:')
        for item in wr.get('blocked_existing', []):
            lines.append(f'  - `{item}`')
    lines.append(f"- inserted rows: `{len(wr.get('inserted', []))}`")
    for item in wr.get('inserted', []):
        extra = f" rmc_namespace=`{item.get('rmc_namespace')}`" if item.get('rmc_namespace') else ''
        lines.append(f"  - `{item.get('table')}` `{item.get('id')}` hash16=`{str(item.get('profile_hash',''))[:16]}`{extra}")
    lines.append('')
    lines.append('## Validation')
    val = report.get('validation', {})
    lines.append(f"- overall ok: `{val.get('ok')}`")
    if val.get('issues'):
        lines.append('- issues:')
        for issue in val.get('issues', []):
            lines.append(f'  - `{issue}`')
    user = val.get('user', {})
    if user:
        lines.append(f"- user `{user.get('user_id')}` is_active=`{user.get('is_active')}` hash_ok=`{user.get('hash_ok')}` ok=`{user.get('ok')}`")
    for agent in val.get('agents', []):
        lines.append(f"- agent `{agent.get('agent_id')}` activation_state=`{agent.get('activation_state')}` is_active=`{agent.get('is_active')}` rmc_namespace=`{agent.get('rmc_namespace')}` pointer_only=`{agent.get('pointer_only')}` hash_ok=`{agent.get('hash_ok')}` ok=`{agent.get('ok')}`")
    lines.append('')
    lines.append('## Database Row Counts')
    before_rows = report.get('before', {}).get('canonical_inventory', {}).get('rows', {})
    after_rows = report.get('after', {}).get('canonical_inventory', {}).get('rows', {})
    lines.append(f"- before canonical rows: `{before_rows}`")
    lines.append(f"- after canonical rows: `{after_rows}`")
    lines.append(f"- legacy rows after: `{report.get('after', report.get('before', {})).get('legacy_inventory', {}).get('rows', {})}`")
    lines.append('')
    lines.append('## Safety Checks')
    for k, v in report.get('safety', {}).items():
        lines.append(f'- `{k}`: `{v}`')
    lines.append('')
    lines.append('## Findings')
    for item in report.get('findings', []):
        lines.append(f"- **{item.get('level')}** `{item.get('code')}` — {item.get('message')}")
    lines.append('')
    if report.get('verdict') == 'PASS':
        lines.append('## Next Safe Step')
        lines.append('Run Patch 227A to independently verify inactive draft profiles and then manually test `forge-agent-list` and `forge-agent-show gilligan.local`.')
    else:
        lines.append('## Next Safe Step')
        lines.append('Do not proceed. Review the failure and restore from the listed backup if needed.')
    lines.append('')
    return '\n'.join(lines)


if __name__ == '__main__':
    raise SystemExit(main())
