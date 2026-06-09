# Patch 272 — RMC Deep Dry-Run UI Panel

Adds a read-only Operator Console tab for the Patch 271 deep dry-run orchestrator.

## Adds

- `src/tabs/RmcDeepDryRunTab.tsx`
- `rmc_deep_dry_run` Operator tab registration
- client routes for:
  - `/api/rmc/deep-dry-run`
  - `/api/rmc/deep-pipeline-preflight`
  - `/api/rmc/protoforge2-drift-preview`
  - `/api/rmc/resurrection-preview`
  - adjacent containment/χ(t)/storage preview routes in fallback map

## Boundary

This is UI-only. It does not create new backend authority.
It calls read-only GET endpoints only.
It does not call write, promotion, gated memory writer, LLM, shell, Chroma write, or Identity Vault endpoints.

## Install

Extract from `/home/nic`:

```bash
cd ~
tar -xzf ~/patch272_deep_dry_run_ui_panel.tar.gz
```

Then verify:

```bash
cd ~/forge
source .venv/bin/activate
python scripts/patch272_verify.py
python scripts/test_patch272_deep_dry_run_ui_panel.py
```

Rebuild/restart the Operator Console layer after verification.
