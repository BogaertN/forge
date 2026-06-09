# Patch 273 — Deep Dry-Run Interactive Scenario Panel

Patch 273 upgrades the Patch 272 Deep Dry-Run UI from a passive proof panel into an interactive read-only scenario surface.

It adds scenario selection and operator-provided input for `/api/rmc/deep-dry-run` while preserving the no-write boundary.

## Scope

Changed files:

- `forge/main.py`
- `forge/rmc_engine_v1/deep_dry_run_orchestrator.py`
- `aiweb/apps/forge-operator-console/src/tabs/RmcDeepDryRunTab.tsx`
- `aiweb/apps/forge-operator-console/src/lib/rmc-api-client.ts`
- `aiweb/apps/forge-operator-console/src/styles/theme.css`
- staging copies in `forge/operator_console_src/`

## What it does

The UI can now run these read-only scenarios:

- clean governed path
- Φ5→Φ8 projection attempt
- bypass correction attack
- memory write before echo
- ghost loop pressure
- resurrection candidate probe
- custom operator input

The backend now parses query parameters for:

- `input`
- `text`
- `query`
- `scenario`
- `scenario_id`
- `use_protoforge2_preview`

It sends these into `run_deep_dry_run()` as read-only source text and metadata.

## Hard boundary

Patch 273 does not add any write endpoint. It does not execute shell commands, write RMC memory, promote memory, emit manifests, approve output, call the LLM, mutate Identity Vault, or write Chroma.

The browser remains a control surface only.
