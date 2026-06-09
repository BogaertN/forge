# Patch 268S2 — ProtoForge2 Drift Candidate Adapter Import Fix

## Purpose

Patch 268S2 fixes the live preview import failure seen after Patch 268S1.

The failure was:

```text
'NoneType' object has no attribute '__dict__'
```

The root cause is Python importlib behavior: `module_from_spec()` does not always insert the module into `sys.modules` before `exec_module()`. Modules that use `dataclasses` or decorator-time module resolution can fail because `sys.modules[cls.__module__]` is missing during execution.

## Fix

`_safe_import()` now registers the module in `sys.modules` before `exec_module()`, preserving/restoring any previous module entry on failure. This matches normal import semantics without adding shell/subprocess/write behavior.

## Safety Boundary

- No shell execution
- No subprocess execution
- No browser-selected import path
- Controlled local import only
- HTTP preview remains read-only
- DriftMonitor remains not called by default
- No Chroma writes
- No Identity Vault writes
- No LLM calls
- No RMC memory writes

## Expected Results

```bash
python scripts/patch268S2_verify.py
# RESULT: PATCH_268S2_VERIFY_OK

python scripts/test_patch268S2_pf2_drift_adapter.py
# RESULT: patch268S2_tests=PASS
```

After restart, `/api/rmc/protoforge2-drift-preview` should no longer return `IMPORT_FAILED` for the safe arbitrator candidate.
