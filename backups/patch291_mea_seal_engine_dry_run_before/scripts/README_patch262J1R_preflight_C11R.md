# Patch 262J1R-Preflight-C11R — Active Loop Test Repair + First-Class feedback_t

This patch repairs the C11 verifier failure and hardens Algorithm 6 memory writeback.

## Fixes

1. Repairs `scripts/test_rmc_active_loop_state_C11.py` by adding the Forge root to `sys.path` before importing `rmc_engine_v1`.
2. Keeps Active Loop State read-only and preserves the `/api/rmc/active-loop-state` and `/api/rmc/loop-state` endpoints installed by C11.
3. Adds a first-class `feedback_t` object to `memory_writer.py`:
   - Dry-run `W_t` now includes `feedback_object_preview`.
   - `feedback_t` has its own ID, type, signal, source links, status, and retrieval tags.
   - User feedback is not fabricated when absent; the object records `user_feedback_present: false`.
4. Gated commit now writes the feedback object as its own JSON file under `feedback_objects/` when, and only when, the normal approval token and write gates pass.
5. C7 and C8 behavior tests now prove the dry-run feedback object and committed feedback object.

## Boundary

- Active Loop State remains read-only.
- Memory writer dry-run remains read-only.
- Gated memory writer still writes only with `APPROVE_RMC_MEMORY_WRITE`.
- No LLM calls.
- No Chroma calls.
- No shell execution.
- No Identity Vault writes.
- No canonical reference mutation.

## Expected verifier result

```text
RESULT: PATCH_262J1R_PREFLIGHT_C11R_VERIFY_OK
```
