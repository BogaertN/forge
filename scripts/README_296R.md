# Patch 296R — MEA Transaction Trace Source-Binding Hotfix

## Reason for the hotfix

The accepted Patch 296 live preflight correctly bound its outer transaction fields to the persisted manifest and state hashes, and it performed no mutation. However, audit of the uploaded accepted preflight JSON exposed a serious inner-trace defect: the proposed next manifest's appended `operator_history` record contained:

```text
input_manifest_hash: "None"
parameters.source_state_content_hash: null
```

The cause was an internal lookup against non-existent status keys (`source_manifest_hash` and `source_state_content_hash`) instead of the persisted store status keys (`manifest_hash` and `state_content_hash`). A real commit must never be built on an operator trace whose source binding is null.

## What Patch 296R changes

Patch 296R keeps the same route and stays fully non-mutating:

```text
POST /api/mea/seal-transaction-preflight
```

It changes only the persisted-state preflight trace binding and visible patch identity:

```text
proposed operator trace input_manifest_hash -> verified persisted manifest_hash
proposed operator trace parameters.source_state_content_hash -> verified persisted state_content_hash
```

It also enforces this as an acceptance gate. If the proposed operator trace does not bind to the current persisted source hashes, preflight returns:

```text
reason_code: proposed_trace_source_binding_failed
```

## Security and authority boundary

Patch 296R does not expose a new mutation surface. It still guarantees:

```text
No /api/mea/seal
No seal execution
No candidate commit
No live manifest advance
No MEA runtime-state write
No memory write or memory promotion
No Chroma or Identity Vault write
No LLM, shell, network, renderer, UI, or launcher action
```

## Why Patch 297 is paused

Patch 297 will be the first candidate-driven persistent manifest transition. It must not be built until the accepted Patch 296 preflight trace is source-bound all the way into its proposed next-manifest operator history. Patch 296R closes that seam first.

## Changed files

```text
forge/main.py
forge/rmc_engine_v1/mea/__init__.py
forge/rmc_engine_v1/mea/discovery_kernel.py
forge/rmc_engine_v1/mea/live_candidates.py
forge/rmc_engine_v1/mea/seal_transaction_preflight.py
forge/scripts/README_296R.md
forge/scripts/patch296R_verify.py
forge/scripts/test_patch296R_mea_transaction_trace_source_binding.py
forge/SHA256SUMS.txt
```

## Verification

Run from your Forge environment after installation:

```bash
python forge/scripts/patch296R_verify.py
python forge/scripts/test_patch296R_mea_transaction_trace_source_binding.py
```

Both scripts are read-only with respect to your live persisted MEA state. Test-only persistence, where used, is restricted to temporary directories.
