# Patch 262J1R-Preflight-C15 — Chroma Integration Boundary

This patch adds a production-safe, read-only Chroma retrieval boundary for the RMC Memory Recaller.

## Scope

- Adds `rmc_engine_v1/chroma_connector.py`.
- Updates `memory_recaller.py` to support `retrieval_backend=filesystem|chroma|hybrid|auto`.
- Keeps `filesystem` as the default backend.
- Adds `/api/rmc/chroma-status`.
- Allows `/api/rmc/memory-recaller` and `/api/rmc/trace-spine` to receive `retrieval_backend`, `chroma_collection`, and `chroma_limit` query parameters.

## Security / governance

- No writes to Chroma.
- No creation of Chroma DB paths.
- No shell execution.
- No LLM calls.
- No Identity Vault writes.
- No RMC memory writes.
- No canonical reference mutation.

The only approved Chroma path is:

`forge/memory/context_library_v1/chroma_db`

The connector skips cleanly if that path or the `chromadb` package is unavailable.

## Verify

```bash
python scripts/patch262J1R_preflight_C15_verify.py
python scripts/test_rmc_chroma_connector_C15.py
python scripts/test_rmc_memory_recaller_behavior.py
python scripts/test_rmc_pipeline_summary_C9.py
```

Expected:

```text
RESULT: PATCH_262J1R_PREFLIGHT_C15_VERIFY_OK
RESULT: chroma_connector_C15_behavior_tests_pass=True
RESULT: memory_recaller_B6_behavior_tests_pass=True
RESULT: pipeline_summary_C9_behavior_tests_pass=True
```
