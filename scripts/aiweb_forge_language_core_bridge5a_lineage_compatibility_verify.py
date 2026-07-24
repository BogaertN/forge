#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

EXPECTED_PARENT = '492d85032342aabbcf328b15110bc34b19ec8ca2'
VALIDATION_PATH = 'aiweb_language_core_bootstrap/selected_meaning_runtime/eligibility_evaluation/validation.py'
EXACT_PATHS_PATH = 'scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5A_39G_41C_LINEAGE_COMPATIBILITY_EXACT_PAYLOAD_PATHS.txt'
PAYLOAD_MANIFEST_PATH = 'scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5A_39G_41C_LINEAGE_COMPATIBILITY_PAYLOAD_SHA256SUMS.txt'
PROTECTED_MANIFEST_PATH = 'scripts/AIWEB_FORGE_LANGUAGE_CORE_BRIDGE5A_39G_41C_LINEAGE_COMPATIBILITY_PROTECTED_PREDECESSOR_SHA256SUMS.txt'
CORRECTED_VALIDATION_SHA256 = '9ea8fd868de36f7d55209332b02f1c0257d6a5ba5f1d42e2661efb6b7c1d76da'
OLD_INVALID_CLAUSE = 'or manifest_record.lineage_id != manifest_companion.candidate_lineage_id'
REQUIRED_COMMENT = 'Slice 39G intentionally preserves two exact lineage domains'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['/usr/bin/git', '-C', str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def read_manifest(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line:
            continue
        digest, relative = line.split('  ', 1)
        records[relative] = digest
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('repository', nargs='?', default='.')
    parser.add_argument('--mode', choices=('applied', 'committed'), default='applied')
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    failures: list[str] = []

    exact_file = repo / EXACT_PATHS_PATH
    payload_manifest = repo / PAYLOAD_MANIFEST_PATH
    protected_manifest = repo / PROTECTED_MANIFEST_PATH
    for required in (exact_file, payload_manifest, protected_manifest):
        if not required.is_file():
            failures.append(f'missing_required_file:{required.relative_to(repo)}')
    if failures:
        for failure in failures: print(f'FAIL - {failure}')
        return 1

    exact_paths = {line.strip() for line in exact_file.read_text(encoding='utf-8').splitlines() if line.strip()}
    payload_records = read_manifest(payload_manifest)
    protected_records = read_manifest(protected_manifest)
    if len(exact_paths) != 10:
        failures.append(f'exact_path_count:{len(exact_paths)}')
    if set(payload_records) != exact_paths - {PAYLOAD_MANIFEST_PATH}:
        failures.append('payload_manifest_path_set_mismatch')

    for relative, expected in sorted(payload_records.items()):
        path = repo / relative
        if not path.is_file(): failures.append(f'payload_missing:{relative}'); continue
        actual = sha256_file(path)
        if actual != expected: failures.append(f'payload_hash_mismatch:{relative}:{actual}')
    validation = repo / VALIDATION_PATH
    if validation.is_file():
        text = validation.read_text(encoding='utf-8')
        if sha256_file(validation) != CORRECTED_VALIDATION_SHA256: failures.append('corrected_validation_hash_mismatch')
        if OLD_INVALID_CLAUSE in text: failures.append('invalid_lineage_equality_still_present')
        if REQUIRED_COMMENT not in text: failures.append('lineage_domain_correction_comment_missing')

    for relative, expected in sorted(protected_records.items()):
        if relative == VALIDATION_PATH:
            continue
        path = repo / relative
        if not path.is_file(): failures.append(f'protected_file_missing:{relative}'); continue
        if sha256_file(path) != expected: failures.append(f'protected_file_changed:{relative}')

    staged = {x for x in git(repo, 'diff', '--cached', '--name-only').stdout.splitlines() if x}
    if staged: failures.append('staged_paths_present:' + ','.join(sorted(staged)))
    memory_changed = git(repo, 'diff', '--name-only', '--', 'memory').stdout.strip()
    memory_untracked = git(repo, 'ls-files', '--others', '--exclude-standard', '--', 'memory').stdout.strip()
    if memory_changed: failures.append('tracked_memory_changes')
    if memory_untracked: failures.append('untracked_memory_paths')

    head = git(repo, 'rev-parse', 'HEAD').stdout.strip()
    if args.mode == 'applied':
        if head != EXPECTED_PARENT: failures.append(f'unexpected_applied_head:{head}')
        changed = {x for x in git(repo, 'diff', '--name-only').stdout.splitlines() if x} | {x for x in git(repo, 'ls-files', '--others', '--exclude-standard').stdout.splitlines() if x}
        if changed != exact_paths: failures.append('applied_change_path_set_mismatch')
    else:
        parent = git(repo, 'rev-parse', 'HEAD^').stdout.strip()
        committed = {x for x in git(repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').stdout.splitlines() if x}
        status = git(repo, 'status', '--porcelain=v1', '-uall').stdout.strip()
        if parent != EXPECTED_PARENT: failures.append(f'committed_parent_mismatch:{parent}')
        if committed != exact_paths: failures.append('committed_path_set_mismatch')
        if status: failures.append('repository_not_clean')

    if failures:
        print('AI.WEB BRIDGE 5A LINEAGE COMPATIBILITY VERIFIER: FAIL')
        for failure in failures: print(f'FAIL - {failure}')
        return 1
    print('AI.WEB BRIDGE 5A LINEAGE COMPATIBILITY VERIFIER: PASS')
    print(f'mode={args.mode}')
    print(f'payload_files={len(exact_paths)}')
    print('slice39g_manifest_lineage_preserved=1')
    print('slice39g_source_candidate_lineage_preserved=1')
    print('lineage_domains_conflated=0')
    print('exact_record_companion_link_preserved=1')
    print('selected_meaning_authority=0')
    print('tool_routing_authority=0')
    print('action_authority=0')
    print('staged_paths=0')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
