# Patch 265R — RMC Containment Router Core

Rebased against live ~/forge/main.py (96,607 lines, C16/RewireUI-R1/Memory Panel P2–P6).
All 46 existing routes preserved. One new route added.

## New endpoint
  /api/rmc/containment-router

## New module
  forge/rmc_engine_v1/containment_router.py

Six routes with hard sealing laws. 59/59 tests pass. 34/34 verifier checks pass.

## Install
```bash
cd /home/nic && tar -xzf ~/patch265R_rmc_containment_router_core.tar.gz
python3 -m py_compile forge/rmc_engine_v1/containment_router.py && echo OK
python3 -m py_compile forge/main.py && echo OK
python3 forge/scripts/patch265R_verify.py
# RESULT: PATCH_265R_VERIFY_OK — restart Forge
```
