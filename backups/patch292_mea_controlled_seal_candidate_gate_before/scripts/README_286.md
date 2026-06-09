# Patch 286 — MEA Seal Packet Audit Chain / Hash Stability Ledger Preview

Patch 286 adds a non-mutating audit-chain preview for Patch 285 seal-packet previews.
It proves the lineage across:

- parent manifest hash
- candidate hash
- hard-gate report hash
- seal-readiness report hash
- seal-packet hash

This patch does not create `/api/mea/seal`. It does not execute a seal, commit live candidates, advance live manifests, write files, write memory, write Chroma, touch Identity Vault, call an LLM, execute shell commands, perform network I/O, promote memory, render user output, mutate the Operator Console UI, or mutate launcher/appctl behavior.

## New module

`rmc_engine_v1/mea/seal_packet_audit_chain.py`

## New routes

- `GET /api/mea/seal-audit-chain/status`
- `GET /api/mea/seal-audit-chain-preview`
- `POST /api/mea/seal-audit-chain-gate`

## Approval token

`APPROVE_MEA_SEAL_AUDIT_CHAIN_PREVIEW`

## Expected canonical result

The 144 Hz fixture produces two audit links:

- `c_hypothesis_001` — best audit candidate, claim status remains `hypothesis`
- `c_branch_derive_001` — bounded/speculative branch

Recall and tamper/replay-failure paths remain blocked from audit packet sealing.

## Verification

Run from the Forge root or from home:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile main.py rmc_engine_v1/mea/*.py scripts/patch286_verify.py scripts/test_patch286_mea_seal_audit_chain.py

cd ~
python forge/scripts/patch286_verify.py
python forge/scripts/test_patch286_mea_seal_audit_chain.py
```

Expected:

```text
RESULT: PATCH_286_VERIFY PASS
RESULT: PATCH_286_BEHAVIOR PASS
```
