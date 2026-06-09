# CE-IV-LEDGER-CAPSULE-BUILD-001

## Identity Vault Contributor Authority, Dual Ledger Foundation, and MEA Capsule Compatibility Preview

This production build begins the real Contribution Economy implementation before any output-memory or renderer work. It deliberately extends only the accepted local Identity Vault and the new `forge/contribution_economy_v1/` sibling package.

## Controlled live writes executed by this build

The build is inert until the operator runs `contribution_identity_build001_apply.py` with both explicit approval tokens. When authorized, it performs only these live writes:

1. It extends the canonical Identity Vault database at `/home/nic/identity-vault/data/identity_vault.db` with append-only contribution-authority tables and triggers.
2. It inserts a contributor-principal binding for the already-existing inactive `nic_bogaert` user profile only if that approved record is absent.
3. It inserts one limited internal consent event and one identity-authority audit event only if absent.
4. It initializes a real but empty dual-ledger SQLite store at `forge/memory/contribution_economy_v1/ledgers/`, including separate Influence and Investment Ledger surfaces protected by append-only triggers.

It does not update or activate the existing Nic profile, and it does not modify Gilligan, Athena, or Neo identity records.

## Nic consent scope installed by this build

Authorized now:

- private local identity storage inside Identity Vault;
- internal opaque contributor-principal references;
- future Memory Capsule candidate references.

Blocked now:

- public identity display;
- identity portability;
- economic processing;
- CT minting;
- investment processing.

## Ledger architecture

The canonical Memory Economy requires that work-earned CT and financial support remain separate. It also describes live, user, and immutable archive ledger surfaces. This build creates six append-only SQLite tables in one transaction-safe database:

- `influence_live_entries`, `influence_user_entries`, `influence_archive_entries`;
- `investment_live_entries`, `investment_user_entries`, `investment_archive_entries`.

Using one local SQLite transaction domain makes future triple-surface writes atomic: the ledger cannot successfully write a live entry while failing to write the user or archive copy. Installation creates no entries, records no money, and mints no CT.

## Memory Capsule compatibility preview

The build adds a pure, deterministic MEA adapter that maps the already committed and replay-verified MEA hypothesis into an in-memory capsule-compatible preview only. The preview contains source evidence hashes and a preview top-level hash, while explicitly preserving:

- `finalized: false`;
- `claim_status: hypothesis`;
- `proof_hash: null`, because MEA artifact evidence is not contributor-action proof;
- `ct_minting_status: blocked`;
- no ledger authorization;
- no capsule persistence.

## Prohibited actions

This build does not write MEA state, RMC output memory, Chroma, any Memory Capsule store, CT, an Influence Ledger entry, an Investment Ledger entry, public output, or public identity disclosure. It adds no API route and does not modify `forge/main.py`.
