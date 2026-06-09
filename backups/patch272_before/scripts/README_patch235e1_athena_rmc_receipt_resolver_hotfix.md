# Patch 235E.1 — Athena RMC Test Receipt Resolver Hotfix

This is a narrow hotfix for Patch 235E. Patch 235E compiled and installed, but the live command crashed because it called the stale undefined helper `_p229_resolve_rmc_root()`.

Patch 235E.1 keeps the same command surface and changes no boundaries. It replaces the stale resolver call with the existing `_p230_latest_scaffold_root()` resolver and reads Athena through the normalized `resolved_profile` field returned by the read-only Identity Vault adapter.

Commands remain:

- `forge-rmc-athena-test-receipt-write`
- `forge-rmc-athena-test-receipt-write-report`

Expected command surface remains `828/828`.

Expected verdict after rerun: `RMC_TEST_RECEIPT_WRITTEN_GOVERNED_ATHENA`.

Boundary: no new commands, no Identity Vault DB write, no agent/long-term/private/shared memory write, no secret reads, no autonomous execution. The only permitted RMC write remains `write_type=test_receipt` for `athena.local`.
