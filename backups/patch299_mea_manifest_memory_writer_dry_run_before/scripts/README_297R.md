# Patch 297R — MEA Idempotent Response Action/State Semantic Separation Hotfix

## Purpose

Patch 297 completed the first controlled atomic MEA manifest advance. Its repeated identical-transaction response was safely non-mutating, but reused action-named flags (`commits_live_candidates`, `advances_live_manifest`, `seals_candidates`, `executes_seal`) to describe the already stored state. This could make a no-op retry look like a second executed transition.

Patch 297R repairs the response contract without changing the already committed manifest or exposing any new mutation route.

## Changes

- The existing `POST /api/mea/seal-transaction-commit` route remains the only controlled commit route.
- An idempotent duplicate invocation now reports all invocation action fields as `false`.
- Stored-state facts are separately reported as `stored_candidate_committed`, `stored_live_manifest_advanced`, and `stored_seal_executed`.
- `GET /api/mea/problem-manifest` now distinguishes the Patch 294 route owner from the patch that wrote the stored record and from this response-contract hotfix.
- Discovery-kernel status no longer reports stale pre-commit capability fields after the controlled commit route has been installed.
- `/api/mea/foundation-status` now identifies Patch 297R as the active response-contract layer while retaining the controlled commit route and blocked-memory boundary.

## Hard Boundaries Preserved

- No canonical `/api/mea/seal` route.
- No new approved commit is executed during installation or verification.
- No RMC memory, Chroma, or Identity Vault write.
- No memory promotion.
- No LLM, shell, network, rendering, UI, or launcher action.

## Operator Validation Rule

The live validation step for this hotfix may resubmit the already committed transaction payload only to exercise the idempotent no-write path. It must capture before/after hashes and prove no stored file changes.
