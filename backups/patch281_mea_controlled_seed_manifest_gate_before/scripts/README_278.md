# Patch 278 — MEA Replay Engine

This patch adds the first hardened read-only replay layer for the MEA / Forge Discovery Kernel.

## New modules

- `rmc_engine_v1/mea/operator_registry.py`
- `rmc_engine_v1/mea/replay_engine.py`

## Replay law

`Replay(H(M_t), O_k, theta_k) = H(c_i)`

A candidate cannot be replay-confirmed unless the starting manifest hash, operator ID, operator parameters, and expected candidate hash reproduce the same output hash.

## Boundary

Patch 278 is read-only.

It does **not**:

- create POST routes
- seed live problem manifests
- seal candidates
- write files
- write memory
- write Chroma
- write Identity Vault
- call an LLM
- execute shell commands
- mutate the Operator Console UI
- mutate launcher/appctl behavior

## Verification

Run from home:

```bash
cd ~
python forge/scripts/patch278_verify.py
python forge/scripts/test_patch278_mea_replay_engine.py
```

Expected:

```text
RESULT: PATCH_278_VERIFY PASS
RESULT: PATCH_278_BEHAVIOR PASS
```
