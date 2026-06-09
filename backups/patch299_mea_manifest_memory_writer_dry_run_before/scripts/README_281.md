# Patch 281 — MEA Controlled Seed Manifest Gate

Purpose: add the first controlled MEA seed-manifest gate after Patch 280 read-only visibility.

This patch does **not** commit a live MEA problem manifest. It validates seed-manifest requests behind an explicit approval token and returns a deterministic gate report only.

## Added

- `forge/rmc_engine_v1/mea/seed_manifest_gate.py`
- `GET /api/mea/seed-manifest-gate/status`
- `POST /api/mea/seed-manifest-gate`
- `POST /api/mea/problem-manifest-gate` as a compatibility alias

## Required POST token

`APPROVE_MEA_SEED_MANIFEST_GATE`

Example approved fixture body:

```json
{
  "approval_token": "APPROVE_MEA_SEED_MANIFEST_GATE",
  "use_fixture": true,
  "source": "canonical_144hz_test_fixture"
}
```

## Boundary

- Creates controlled POST gate routes: yes
- Writes files: no
- Writes memory: no
- Writes Chroma: no
- Writes Identity Vault: no
- Calls LLM: no
- Executes shell: no
- Performs network I/O: no
- Seeds live manifests: no
- Seals candidates: no
- Promotes to memory: no
- Mutates launcher behavior: no
- Mutates Operator Console UI: no

## Hard gates

The seed gate rejects:

- missing or invalid approval token
- missing or malformed manifest
- manifests with no explicit unknowns
- manifests entering as `verified_claim`
- manifests whose `output_permissions` are not `sealed`
- manifests above the Patch 281 drift threshold

The canonical 144 Hz fixture is accepted only as a non-mutating preview. It remains high proof debt and cannot be promoted to verified claim.
