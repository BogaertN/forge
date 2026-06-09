# Patch 292 — MEA Controlled Seal Candidate Gate

Patch 292 adds the first controlled seal-candidate gate:

`POST /api/mea/seal-candidate-gate`

This is **not** `/api/mea/seal`. It does not execute a live seal, commit candidates, advance the live manifest, write memory, write Chroma, touch Identity Vault, call an LLM, execute shell, perform network I/O, render user output, or mutate the Operator Console.

The route requires:

- `approval_token = APPROVE_MEA_SEAL_CANDIDATE_GATE`
- `candidate_id`
- matching `candidate_hash`

Optional hard-match fields are supported:

- `seal_object_hash`
- `seal_packet_hash`
- `gate_report_hash`

The accepted response returns a sealed-candidate preview object only. It proves candidate hash matching, seal-packet hash/audit-chain matching, gate-engine pass, seal-allowed claim status, proof-debt compatibility, replay confirmation, no tamper, and no route mismatch.

Canonical accepted preview target:

- `cg_hypothesis_001`

Canonical bounded preview target:

- `cg_branch_001`

Canonical rejected targets:

- `cg_recall_001` — reference-only, not a seal target
- `cg_tamper_001` — rejected/containment, not user-visible

## Verification

Run:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile main.py rmc_engine_v1/mea/*.py scripts/patch292_verify.py scripts/test_patch292_mea_seal_candidate_gate.py
cd ~
python forge/scripts/patch292_verify.py
python forge/scripts/test_patch292_mea_seal_candidate_gate.py
```

Expected:

```text
RESULT: PATCH_292_VERIFY PASS
RESULT: PATCH_292_BEHAVIOR PASS
```
