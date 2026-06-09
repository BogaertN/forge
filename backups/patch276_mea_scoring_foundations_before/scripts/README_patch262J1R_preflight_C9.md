# Patch 262J1R-Preflight-C9 — RMC Pipeline Summary + Compact Trace Surface

C9 adds the compact end-to-end RMC application surface. It does not replace the individual engines. It calls the live stage adapters, compresses their stage status, identifies the first blocking gate, and clearly separates algorithm failures from lawful gate refusals and read-only refusals.

## New module

- `forge/rmc_engine_v1/rmc_pipeline.py`

## New endpoints

- `/api/rmc/pipeline-summary`
- `/api/rmc/full-pipeline`
- `/api/rmc/compact-trace`

## Default authority boundary

By default C9 is read-only. It calls through C7 dry-run, not C8 commit. It does not write memory unless both conditions are explicitly present in the request:

- `commit=true`
- `approval=APPROVE_RMC_MEMORY_WRITE`

Without those two flags, C9 marks the gated writer stage as `NOT_ATTEMPTED`.

## What C9 returns

- stage order
- stage summaries
- first blocker
- pipeline verdict
- algorithm failure count
- gate refusal count
- actual file write count
- compact response suitable for UI panels
- artifact hygiene note folding in the C8 checksum-manifest lesson

## C8 packaging hygiene folded into C9

C8 behavior was correct, but its `SHA256SUMS.txt` listed `__pycache__` / `.pyc` files that were not in the archive. C9 corrects that packaging discipline. The C9 checksum manifest must not list pycache or bytecode files.

## Still not included

- UI panel wiring
- Identity Vault permission ladder
- dataset review UI
- promotion patch builder
