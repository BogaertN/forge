# Patch 262-UI-MemoryPanel-P3

Professional-production UI hardening for RMC Memory Panel Phase 2.

## Purpose

P2R exposed the remaining read-only memory surface routes. P3 hardens the only visible write-capable UI action in the panel: promotion from `review_queue` to `stable_memory`.

## What changed

- Adds `rmc-ui-guards.ts` and `rmc-ui-guards.js`.
- Requires a current promotion preview before the Promote button can arm.
- Requires exact approval token: `APPROVE_RMC_PROMOTION`.
- Requires exact confirmation fingerprint: `PROMOTE <candidate_id>`.
- Refuses to arm when preview candidate does not match selected candidate.
- Refuses to arm when preview reports duplicate promotion, missing fields, unsafe paths, or non-promotable state.
- Keeps backend as authority. The UI guard is friction, not authorization.

## Safety

This patch is UI source only. It does not add backend writes, shell execution, DB access, Chroma writes, LLM calls, or Identity Vault access.
