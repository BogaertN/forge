# Patch 271 — RMC Deep Pipeline Dry-Run Orchestrator

## Purpose

Patch 271 adds the first read-only orchestration layer that exercises the installed RMC deep stack together without activating live mutation.

It proves cross-module flow across:

1. input event
2. memory recall / trace spine
3. phase parser
4. structural drift engine
5. ProtoForge2 safe drift adapter
6. candidate generator
7. evolutionary drift explorer
8. coherence scorer
9. containment router
10. χ(t) correction gate preview
11. storage target preview
12. resurrection eligibility preview
13. manifest eligibility check
14. output renderer eligibility check
15. echo validation eligibility check
16. memory write eligibility check

## New module

`forge/rmc_engine_v1/deep_dry_run_orchestrator.py`

## New endpoint

`/api/rmc/deep-dry-run`

Alias:

`/api/rmc/deep-dry-run-orchestrator`

## Hard boundary

This patch is read-only. It does not:

- write files
- write RMC memory
- write Identity Vault
- write Chroma
- call an LLM
- execute shell commands
- emit a manifest
- render output
- validate echo as approved output
- commit memory
- promote stable memory
- re-enter active runtime

## Important implementation note

This is not live pipeline activation. It is an orchestration proof. The dry-run may call installed read-only modules and may fail closed if a stage is unavailable. It must never convert a sealed route into manifest, render, echo, or memory write access.

## Expected verification

```bash
cd ~/forge
source .venv/bin/activate

python -m py_compile \
  main.py \
  rmc_engine_v1/deep_dry_run_orchestrator.py \
  rmc_engine_v1/protoforge2_drift_connector.py \
  rmc_engine_v1/__init__.py \
  scripts/patch271_verify.py \
  scripts/test_patch271_deep_dry_run_orchestrator.py

python scripts/patch271_verify.py
python scripts/test_patch271_deep_dry_run_orchestrator.py
```

Expected:

```text
RESULT: PATCH_271_VERIFY_OK
RESULT: patch271_tests=PASS
```

## Live check

After restart:

```bash
curl -s 'http://localhost:7477/api/rmc/deep-dry-run' | python -m json.tool | head -420
```

Look for:

```text
"status": "OK"
"mode": "read_only_rmc_deep_pipeline_dry_run_orchestrator"
"DRY_RUN_COMPLETE"
"forbidden_effect_violations": []
"projection_allowed": false
"memory_write_committed": false
```
