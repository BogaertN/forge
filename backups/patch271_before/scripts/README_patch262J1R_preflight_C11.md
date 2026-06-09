# Patch 262J1R-Preflight-C11 — Active Loop State / L_t

This patch implements the read-only `active_loop_state.py` engine module and exposes `/api/rmc/active-loop-state` plus `/api/rmc/loop-state` through `main.py`.

## What it adds

- `forge/rmc_engine_v1/active_loop_state.py`
- `forge/scripts/test_rmc_active_loop_state_C11.py`
- `forge/scripts/patch262J1R_preflight_C11_verify.py`
- `forge/scripts/README_patch262J1R_preflight_C11.md`
- Updates `forge/rmc_engine_v1/__init__.py`
- Updates `forge/main.py` with thin read-only endpoint adapters

## What L_t contains

The active loop state object reconstructs:

- `current_loop_id`
- `current_phase`
- `phase_path`
- `open_issues`
- `completed_stages`
- `unresolved_branches`
- `next_expected_step`
- `last_valid_manifest`
- `last_valid_render`
- `last_valid_echo`
- `memory_write_status`
- `user_session_continuity`
- `memory_surface`

## Safety boundaries

C11 is read-only. It performs no writes, no shell execution, no LLM call, no Chroma query, no Identity Vault access, and no memory mutation. The endpoint strips commit and approval parameters before calling the C9 pipeline summary so it cannot accidentally trigger C8 gated memory writing.

## Verify

Run:

```bash
python scripts/patch262J1R_preflight_C11_verify.py
python scripts/test_rmc_active_loop_state_C11.py
```

Expected:

```text
RESULT: PATCH_262J1R_PREFLIGHT_C11_VERIFY_OK
RESULT: active_loop_state_C11_behavior_tests_pass=True
```
