# Patch 268S3 — ProtoForge2 Drift Candidate Adapter Signature Fix

Patch 268S3 is a surgical follow-up to 268S2.

## Problem fixed

268S2 fixed importlib module registration, but the live preview endpoint still failed against the real `DriftArbitrator.evaluate()` because the callable signature is:

```python
DriftArbitrator.evaluate(text, current_phase, phase_history=None, expected_shape=None, memory_baseline=None)
```

The older adapter called `evaluate(payload)`, which caused:

```text
DriftArbitrator.evaluate() missing 1 required positional argument: 'current_phase'
```

## Fix

Patch 268S3 adds signature-aware safe invocation:

- maps `text` to a stable probe string
- maps `current_phase` to the current phase from the probe phase path
- maps `phase_history` to a numeric phase history
- maps `expected_shape` to a harmless schema hint
- maps `memory_baseline` to a fixed safe baseline string
- keeps fallback support for older `evaluate(payload)` style callables
- supports `DriftBridge.evaluate(text, phase_history)`
- normalizes dataclass/to_dict outputs

## Boundary

Still read-only. Still no shell. Still no subprocess. Still no Chroma write. Still no Identity Vault. Still no LLM. Still does not instantiate `DriftMonitor` by default.

## Verify

```bash
python scripts/patch268S3_verify.py
python scripts/test_patch268S3_pf2_drift_adapter.py
```

Expected:

```text
RESULT: PATCH_268S3_VERIFY_OK
RESULT: patch268S3_tests=PASS
```
