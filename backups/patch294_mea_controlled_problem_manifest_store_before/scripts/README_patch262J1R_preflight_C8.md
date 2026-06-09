# Patch 262J1R-Preflight-C8 — Gated Memory Writer Commit

C8 is the first RMC memory mutation layer. It does not replace C7. C7 computes `W_t` dry-run write plans. C8 commits a plan only when all gates pass.

## New endpoints

- `/api/rmc/gated-memory-writer`
- `/api/rmc/memory-write-commit`
- `/api/rmc/commit-memory-write`

## Approval token

Actual write requires:

`approval=APPROVE_RMC_MEMORY_WRITE`

Without the token, C8 returns a structured refusal and writes nothing.

## Commit gates

C8 writes only if:

1. C6 Echo Validator passed.
2. C5 produced a render packet.
3. C4 produced a manifest packet.
4. C7 produced a valid `W_t` write plan.
5. Explicit approval token is supplied.
6. Target paths resolve inside `/home/nic/forge/memory/rmc_live_memory_v1`.
7. Duplicate check against the memory writer index passes.

## Files written on approved commit

- memory node JSON
- write receipt JSON
- memory writer index JSONL row

C8 does not write canonical reference files, Identity Vault, Chroma DB internals, source documents, shell, network, or UI code.

## Expected weak-input behavior

For inputs blocked upstream by C4/C5/C6, C8 should return:

- `status: REFUSED`
- `memory_write_committed: false`
- `actual_files_written: []`
- `memory_write_allowed: false`

This is a gate refusal, not an algorithm failure.
