# Patch 266R — SPC / Archive / Dream / Ghost Storage Preview Suite

Rebased. Preserves all current routes. Adds four containment storage preview endpoints.

## New endpoints
  /api/rmc/spc-cold-storage/preview
  /api/rmc/drift-archive/preview
  /api/rmc/dream-state/preview
  /api/rmc/ghost-loop/preview

## New modules
  forge/rmc_engine_v1/spc_cold_storage.py
  forge/rmc_engine_v1/drift_archive.py
  forge/rmc_engine_v1/dream_state_quarantine.py
  forge/rmc_engine_v1/ghost_loop_containment.py

HTTP preview endpoints are read-only. commit_*() functions exist for future gated use
but NO production HTTP route calls them — they require explicit approval tokens.
84/84 tests pass. 30/30 verifier checks pass.

## Install
```bash
cd /home/nic && tar -xzf ~/patch266R_rmc_storage_preview_suite.tar.gz
python3 -m py_compile forge/main.py && echo OK
python3 forge/scripts/patch266R_verify.py
```
Requires: Patch 265R installed first.
