# Patch 268S1 — ProtoForge2 Drift Candidate Adapter Test-Hardening

This patch is a professional-production bug fix for Patch 268S.

## What it fixes

Patch 268S failed on Nic's live machine because the missing-candidate test used an explicit `pf2_root` while the connector still scanned the global live candidate registry. Since the real drift candidates exist on Nic's machine, the test expected `SKIPPED` but the connector correctly found live candidates.

Patch 268S1 makes scoped root probes deterministic: when `pf2_root` is supplied and no `_test_candidates` are injected, the connector scans only that root's legacy substrate filenames and does not fall back to global absolute candidates. Normal HTTP/default behavior is unchanged: the approved live candidate registry is used when no scoped root is supplied.

## Safety boundary

- No shell execution.
- No subprocess execution.
- No browser-selected import path.
- Controlled local import only.
- Default HTTP preview remains read-only.
- Full `DriftMonitor` is detected but not called by default.
- No Chroma writes.
- No Identity Vault access.
- No LLM calls.

## Files

- `forge/rmc_engine_v1/protoforge2_drift_connector.py`
- `forge/main.py`
- `forge/scripts/patch268S1_verify.py`
- `forge/scripts/test_patch268S1_pf2_drift_adapter.py`
- `forge/scripts/README_268S1.md`
- cumulative deep architecture modules from 265R-268S

## Verify

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile main.py rmc_engine_v1/protoforge2_drift_connector.py rmc_engine_v1/__init__.py scripts/patch268S1_verify.py scripts/test_patch268S1_pf2_drift_adapter.py
python scripts/patch268S1_verify.py
python scripts/test_patch268S1_pf2_drift_adapter.py
```

Expected:

```text
RESULT: PATCH_268S1_VERIFY_OK
RESULT: patch268S1_tests=PASS
```
