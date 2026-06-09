# Patch 293 — MEA Live Manifest Advance Preview

## Purpose

Patch 293 introduces the first deterministic preview of the MEA state transition `M_t -> M_(t+1)` after Patch 292 proved a controlled sealed-candidate **response-only** gate.

This patch does **not** persist a manifest and does **not** execute a seal. It compiles a proposed next-manifest preview for the canonical `144hz_substrate_status` test case using the Patch 292 accepted preview candidate `cg_hypothesis_001`.

## New runtime module

- `rmc_engine_v1/mea/manifest_advance_preview.py`

## New route

- `GET /api/mea/manifest-advance-preview`

## Transition proof fields

The response proves:

- old manifest hash;
- selected candidate hash;
- selected sealed-candidate preview hash;
- deterministic proposed new manifest hash;
- operator-history update;
- claim-status history update;
- unknown-vector update;
- proof-debt update;
- phase-path update;
- no persistence and no live advance.

## Canonical 144 Hz behavior

The selected preview remains a `hypothesis`, not a `verified_claim`.

- proof debt remains `0.85` because no new evidence has been added;
- two original unknowns remain unresolved;
- one test-required derived-status unknown is added;
- the phase path records current `Phi5` context but performs no phase promotion;
- output permissions remain sealed because there is no live state advance or rendered output.

## Hard boundary

Patch 293 is GET-only and non-mutating:

- no `/api/mea/seal` route;
- no live candidate commit;
- no live manifest advance;
- no problem-manifest persistence;
- no file writes;
- no memory writes;
- no Chroma writes;
- no Identity Vault writes;
- no LLM calls;
- no shell execution;
- no network I/O;
- no UI mutation;
- no user-facing rendering.

The proposed transition trace explicitly defers output-hash binding until a future controlled persistence patch. That prevents the preview from claiming that an uncommitted manifest has already been written or sealed.
