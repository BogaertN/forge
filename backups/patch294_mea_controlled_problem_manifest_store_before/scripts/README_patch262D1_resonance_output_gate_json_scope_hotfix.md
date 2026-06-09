# Patch 262D1 — RMC Resonance Output Gate JSON Scope Hotfix

## Purpose

Patch 262D introduced `GET /api/rmc/resonance-output-gate`, but the receipt preview ID helper called `_j.dumps(...)`. `_j` only exists inside the HTTP handler scope, so the helper raised:

`NameError: name '_j' is not defined`

Patch 262D1 fixes that by importing JSON locally inside `_p262d_rmc_receipt_preview_id` as `_p262d_json` and using `_p262d_json.dumps(...)`.

## Boundary

- Does not add Forge commands.
- Does not add a new backend endpoint.
- Does not execute shell.
- Does not write files during endpoint execution.
- Does not write Identity Vault.
- Does not write RMC live memory.
- Keeps the resonance output gate preview read-only.
