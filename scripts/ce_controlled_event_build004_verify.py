#!/usr/bin/env python3
"""Installed-state verifier for the bounded CE-EVT-000001 write."""
from __future__ import annotations
import argparse, json, sqlite3, sys
from pathlib import Path

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--forge-root', required=True); parser.add_argument('--identity-vault-root', required=True); args=parser.parse_args()
    forge=Path(args.forge_root).resolve(); identity=Path(args.identity_vault_root).resolve(); sys.path.insert(0, str(forge))
    from contribution_economy_v1.controlled_writes import EVENT_ID, CAPSULE_ID, PRINCIPAL_ID, read_locked_event_state
    from contribution_economy_v1.contracts.ct_reward_policy import calculate_reward_preview
    state=read_locked_event_state(forge, identity)
    core=sqlite3.connect(f"file:{forge / 'memory/contribution_economy_v1/core/contribution_economy_core.db'}?mode=ro&immutable=1", uri=True)
    iv=sqlite3.connect(f"file:{identity / 'data/identity_vault.db'}?mode=ro&immutable=1", uri=True)
    ledger=sqlite3.connect(f"file:{forge / 'memory/contribution_economy_v1/ledgers/contribution_ledgers.db'}?mode=ro&immutable=1", uri=True)
    passed=failed=0
    def check(name, ok, detail=''):
        nonlocal passed, failed
        if ok: passed+=1; print(f"  [PASS] {name}" + (f" - {detail}" if detail else ''))
        else: failed+=1; print(f"  [FAIL] {name}" + (f" - {detail}" if detail else ''))
    try:
        event=state.get('event') or {}; capsule=state.get('candidate') or {}; receipt=state.get('write_receipt') or {}
        check('locked_event_persisted', state.get('persisted') is True)
        check('event_identity_locked', event.get('event_id') == EVENT_ID and event.get('principal_id') == PRINCIPAL_ID)
        check('event_pending_validation', event.get('event_status') == 'persisted_pending_validation_not_finalized_not_minted' and event.get('classification_status') == 'asserted_candidate_requires_evidence_validation')
        check('private_attribution_only', event.get('identity_disclosure_class') == 'private_identity_vault_only' and event.get('public_attribution_authorized') is False)
        check('action_proof_present', isinstance(event.get('contributor_action_proof_hash'), str) and len(event['contributor_action_proof_hash']) == 64)
        check('capsule_identity_locked', capsule.get('capsule_id') == CAPSULE_ID and capsule.get('contribution_event_id') == EVENT_ID)
        check('capsule_non_finalized', capsule.get('finalized') is False and capsule.get('capsule_status') == 'identity_bound_candidate_persisted_pending_validation_not_finalized')
        check('capsule_pending_validation', capsule.get('validation_status') == 'pending_classification_evidence_validation')
        check('capsule_ct_zero', capsule.get('ct_minted_milli') == 0 and capsule.get('ct_minting_status') == 'blocked_not_validated_not_finalized_not_minted')
        preview=calculate_reward_preview('BLD','standard','direct').as_dict()
        check('reward_is_reference_only', capsule.get('ct_reward_calculation_preview_reference_only',{}).get('calculated_milli_ct') == 10000 and preview['calculated_milli_ct'] == 10000 and preview['mint_authorized'] is False)
        check('receipt_blocks_economic_effects', receipt.get('blocked_effects',{}).get('ct_mint') is True and receipt.get('blocked_effects',{}).get('influence_ledger') is True and receipt.get('blocked_effects',{}).get('investment_ledger') is True)
        consent_count=iv.execute("SELECT COUNT(*) FROM contributor_internal_persistence_consent_events_v1 WHERE principal_id=? AND event_scope_id=? AND internal_contribution_event_persistence_authorized=1 AND internal_capsule_candidate_persistence_authorized=1 AND public_display_authorized=0 AND economic_processing_authorized=0 AND ct_minting_authorized=0 AND investment_processing_authorized=0", (PRINCIPAL_ID, EVENT_ID)).fetchone()[0]
        check('one_internal_persistence_consent', consent_count == 1, str(consent_count))
        audit_count=iv.execute("SELECT COUNT(*) FROM contributor_authority_audit_events WHERE principal_id=? AND event_type='internal_event_capsule_persistence_scope_grant'", (PRINCIPAL_ID,)).fetchone()[0]
        check('one_identity_audit_extension', audit_count == 1, str(audit_count))
        core_counts={t:core.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('contribution_events','memory_capsule_candidates','capsule_validation_records','capsule_finalization_receipts','ct_mint_events','nullification_correction_events')}
        check('one_event_and_one_candidate_only', core_counts['contribution_events']==1 and core_counts['memory_capsule_candidates']==1, json.dumps(core_counts, sort_keys=True))
        check('no_validation_finalization_mint_or_correction', all(core_counts[t]==0 for t in ('capsule_validation_records','capsule_finalization_receipts','ct_mint_events','nullification_correction_events')), json.dumps(core_counts, sort_keys=True))
        ledger_counts={t:ledger.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('influence_live_entries','influence_user_entries','influence_archive_entries','investment_live_entries','investment_user_entries','investment_archive_entries')}
        check('all_ledgers_still_empty', all(v==0 for v in ledger_counts.values()), json.dumps(ledger_counts, sort_keys=True))
    finally:
        core.close(); iv.close(); ledger.close()
    if failed:
        print(f"RESULT: CE-CONTROLLED-CONTRIBUTION-EVENT-BUILD-004_VERIFY FAIL  Total:{passed+failed} Passed:{passed} Failed:{failed}")
        return 1
    print(f"RESULT: CE-CONTROLLED-CONTRIBUTION-EVENT-BUILD-004_VERIFY PASS  Total:{passed} Passed:{passed} Failed:0")
    return 0
if __name__ == '__main__': raise SystemExit(main())
