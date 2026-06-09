#!/usr/bin/env python3
"""Apply the single controlled CE-EVT-000001 / candidate persistence transaction."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--forge-root', required=True)
    parser.add_argument('--identity-vault-root', required=True)
    parser.add_argument('--evidence-dir', required=True)
    parser.add_argument('--consent-effective-at-utc', required=True)
    parser.add_argument('--persistence-consent-approval-token', required=True)
    parser.add_argument('--controlled-write-approval-token', required=True)
    args = parser.parse_args()
    forge = Path(args.forge_root).resolve()
    sys.path.insert(0, str(forge))
    from contribution_economy_v1.controlled_writes import apply_locked_event_write
    receipt = apply_locked_event_write(
        forge_root=forge,
        identity_root=Path(args.identity_vault_root).resolve(),
        evidence_dir=Path(args.evidence_dir).resolve(),
        consent_effective_at_utc=args.consent_effective_at_utc,
        persistence_consent_approval_token=args.persistence_consent_approval_token,
        controlled_write_approval_token=args.controlled_write_approval_token,
    )
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
