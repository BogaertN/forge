#!/usr/bin/env python3
"""Behavior tests for Build 004. Every mutation occurs inside temporary database copies."""
from __future__ import annotations
import argparse, hashlib, shutil, sqlite3, sys, tempfile
from pathlib import Path

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--forge-root', required=True); parser.add_argument('--identity-vault-root', required=True); parser.add_argument('--evidence-dir', required=True); args=parser.parse_args()
    forge=Path(args.forge_root).resolve(); identity=Path(args.identity_vault_root).resolve(); evidence=Path(args.evidence_dir).resolve(); sys.path.insert(0, str(forge))
    from contribution_economy_v1.controlled_writes import (
        EVENT_ID, CAPSULE_ID, PRINCIPAL_ID, PERSISTENCE_CONSENT_APPROVAL_TOKEN, CONTROLLED_WRITE_APPROVAL_TOKEN,
        apply_locked_event_write, read_locked_event_state,
    )
    passed=failed=0
    def check(label, ok, detail=''):
        nonlocal passed,failed
        if ok: passed+=1; print(f"  [PASS] {label}" + (f" - {detail}" if detail else ''))
        else: failed+=1; print(f"  [FAIL] {label}" + (f" - {detail}" if detail else ''))
    def raises(label, fn):
        try: fn(); check(label, False, 'expected rejection missing')
        except Exception: check(label, True)
    print('CE-CONTROLLED-CONTRIBUTION-EVENT-BUILD-004 BEHAVIOR TESTS - TEMPORARY MUTATION ONLY')
    main_text=(forge/'main.py').read_text(encoding='utf-8')
    operator_text=(forge/'contribution_economy_v1/operator_surface/read_only_status.py').read_text(encoding='utf-8')
    controlled_text=(forge/'contribution_economy_v1/controlled_writes/build004_ce_evt_000001.py').read_text(encoding='utf-8').lower()
    check('main_read_only_event_endpoint_present', '/api/contribution-economy/controlled-event/latest' in main_text)
    check('main_read_only_candidate_endpoint_present', '/api/contribution-economy/capsule-candidate/latest' in main_text)
    check('operator_surface_build004_readback_present', 'build_controlled_event_latest_status' in operator_text and 'build_controlled_capsule_candidate_latest_status' in operator_text)
    forbidden_runtime = [term for term in ('requests', 'httpx', 'urllib', 'socket', 'subprocess', 'chromadb', 'ollama') if term in controlled_text]
    check('controlled_writer_no_network_shell_llm_chroma_pathway', not forbidden_runtime, str(forbidden_runtime))
    with tempfile.TemporaryDirectory(prefix='ce_build004_test_') as temp_name:
        root=Path(temp_name); tf=root/'forge'; ti=root/'identity-vault'
        (tf/'memory/contribution_economy_v1/core').mkdir(parents=True); (tf/'memory/contribution_economy_v1/ledgers').mkdir(parents=True)
        (tf/'contribution_economy_v1').mkdir(parents=True); (ti/'data').mkdir(parents=True); (ti/'schema_extensions').mkdir(); (ti/'service_contracts').mkdir()
        shutil.copytree(forge/'contribution_economy_v1', tf/'contribution_economy_v1', dirs_exist_ok=True)
        shutil.copy2(forge/'memory/contribution_economy_v1/core/contribution_economy_core.db', tf/'memory/contribution_economy_v1/core/contribution_economy_core.db')
        shutil.copy2(forge/'memory/contribution_economy_v1/ledgers/contribution_ledgers.db', tf/'memory/contribution_economy_v1/ledgers/contribution_ledgers.db')
        shutil.copy2(identity/'data/identity_vault.db', ti/'data/identity_vault.db')
        shutil.copy2(identity/'schema_extensions/contribution_economy_internal_persistence_consent_build004.sql', ti/'schema_extensions/contribution_economy_internal_persistence_consent_build004.sql')
        shutil.copy2(identity/'service_contracts/contribution_economy_controlled_persistence_build004.v1.json', ti/'service_contracts/contribution_economy_controlled_persistence_build004.v1.json')
        sys.path.insert(0, str(tf))
        # Imported functions reference installed package code but operate only on copied databases.
        raises('wrong_consent_token_blocked', lambda: apply_locked_event_write(forge_root=tf, identity_root=ti, evidence_dir=evidence, consent_effective_at_utc='2026-05-30T21:00:00Z', persistence_consent_approval_token='WRONG', controlled_write_approval_token=CONTROLLED_WRITE_APPROVAL_TOKEN))
        raises('wrong_write_token_blocked', lambda: apply_locked_event_write(forge_root=tf, identity_root=ti, evidence_dir=evidence, consent_effective_at_utc='2026-05-30T21:00:00Z', persistence_consent_approval_token=PERSISTENCE_CONSENT_APPROVAL_TOKEN, controlled_write_approval_token='WRONG'))
        receipt=apply_locked_event_write(forge_root=tf, identity_root=ti, evidence_dir=evidence, consent_effective_at_utc='2026-05-30T21:00:00Z', persistence_consent_approval_token=PERSISTENCE_CONSENT_APPROVAL_TOKEN, controlled_write_approval_token=CONTROLLED_WRITE_APPROVAL_TOKEN)
        check('controlled_write_commits', receipt['outcome']=='ce_evt_000001_and_candidate_committed')
        state=read_locked_event_state(tf, ti); event=state['event']; candidate=state['candidate']
        check('state_readback_persisted', state['persisted'] is True)
        check('event_id_exact', event['event_id']==EVENT_ID and event['principal_id']==PRINCIPAL_ID)
        check('event_pending_validation_only', event['event_status']=='persisted_pending_validation_not_finalized_not_minted')
        check('action_proof_present', len(event['contributor_action_proof_hash'])==64)
        check('candidate_id_exact', candidate['capsule_id']==CAPSULE_ID)
        check('candidate_not_finalized', candidate['finalized'] is False)
        check('candidate_pending_validation', candidate['validation_status']=='pending_classification_evidence_validation')
        check('candidate_reward_reference_not_mint', candidate['ct_reward_calculation_preview_reference_only']['calculated_milli_ct']==10000 and candidate['ct_minted_milli']==0)
        second=apply_locked_event_write(forge_root=tf, identity_root=ti, evidence_dir=evidence, consent_effective_at_utc='2026-05-30T21:01:00Z', persistence_consent_approval_token=PERSISTENCE_CONSENT_APPROVAL_TOKEN, controlled_write_approval_token=CONTROLLED_WRITE_APPROVAL_TOKEN)
        check('repeat_apply_idempotent_no_write', second['outcome']=='existing_locked_event_verified_idempotent_no_write')
        iv=sqlite3.connect(ti/'data/identity_vault.db'); core=sqlite3.connect(tf/'memory/contribution_economy_v1/core/contribution_economy_core.db'); ledger=sqlite3.connect(tf/'memory/contribution_economy_v1/ledgers/contribution_ledgers.db')
        try:
            check('one_persistence_consent_only', iv.execute('SELECT COUNT(*) FROM contributor_internal_persistence_consent_events_v1').fetchone()[0]==1)
            check('one_new_audit_event_only', iv.execute("SELECT COUNT(*) FROM contributor_authority_audit_events WHERE event_type='internal_event_capsule_persistence_scope_grant'").fetchone()[0]==1)
            counts={t:core.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('contribution_events','memory_capsule_candidates','capsule_validation_records','capsule_finalization_receipts','ct_mint_events','nullification_correction_events')}
            check('event_and_candidate_only', counts['contribution_events']==1 and counts['memory_capsule_candidates']==1, str(counts))
            check('no_validation_finalization_mint_correction', sum(counts[t] for t in ('capsule_validation_records','capsule_finalization_receipts','ct_mint_events','nullification_correction_events'))==0, str(counts))
            ledger_total=sum(ledger.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('influence_live_entries','influence_user_entries','influence_archive_entries','investment_live_entries','investment_user_entries','investment_archive_entries'))
            check('ledgers_untouched', ledger_total==0, str(ledger_total))
            raises('event_update_trigger_blocks_mutation', lambda: core.execute("UPDATE contribution_events SET status='tampered' WHERE event_id=?", (EVENT_ID,)).fetchall())
            raises('candidate_delete_trigger_blocks_mutation', lambda: core.execute('DELETE FROM memory_capsule_candidates WHERE capsule_id=?', (CAPSULE_ID,)).fetchall())
            raises('consent_delete_trigger_blocks_mutation', lambda: iv.execute('DELETE FROM contributor_internal_persistence_consent_events_v1').fetchall())
        finally:
            iv.close(); core.close(); ledger.close()
    if failed:
        print(f'RESULT: CE-CONTROLLED-CONTRIBUTION-EVENT-BUILD-004_BEHAVIOR FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}'); return 1
    print(f'RESULT: CE-CONTROLLED-CONTRIBUTION-EVENT-BUILD-004_BEHAVIOR PASS  Total:{passed} Passed:{passed} Failed:0'); return 0
if __name__=='__main__': raise SystemExit(main())
