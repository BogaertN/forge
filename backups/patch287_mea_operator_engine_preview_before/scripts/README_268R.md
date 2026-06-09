# Patch 268R — ProtoForge2 Drift Connector Preflight

Performs local runtime discovery on the machine at:
  /home/nic/aiweb/runtime_wrappers/protoforge_sandbox_substrate_v0/

Looks for: memory-drift.py (or memory_drift.py / drift.py)
Uses importlib.util.spec_from_file_location to handle hyphen filenames.

## Boundary (corrected wording)
No shell. No subprocess. No writes. Controlled local import of trusted
ProtoForge2 drift module only. Read-only preflight.
(Note: exec_module() is used internally by importlib — this is disclosed.)

## Three adapter modes: LIVE / SKIPPED / FALLBACK

## New endpoints
  /api/rmc/protoforge2-drift-status
  /api/rmc/protoforge2-drift-preview

## New module + docs
  forge/rmc_engine_v1/protoforge2_drift_connector.py
  forge/docs/RMC_DEEP_ARCHITECTURE_ROADMAP_v1.md

61/61 tests pass. 23/23 verifier checks pass.

## Install
```bash
cd /home/nic && tar -xzf ~/patch268R_protoforge2_drift_connector_preflight.tar.gz
python3 -m py_compile forge/main.py && echo OK
python3 forge/scripts/patch268R_verify.py
# Then: curl http://localhost:7477/api/rmc/protoforge2-drift-status | python3 -m json.tool
```
Requires: Patches 265R, 266R, 267R installed first.
