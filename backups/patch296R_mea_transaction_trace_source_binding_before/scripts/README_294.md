# Patch 294 — MEA Controlled Problem Manifest Store

## Purpose

Patch 294 is the first intentionally persistent MEA patch. It exposes the Phase 5 problem-manifest API required by the MEA build order:

- `GET /api/mea/problem-manifest`
- `POST /api/mea/problem-manifest`

This patch persists **one initial validated problem manifest seed only**. It does not persist the Patch 293 candidate-driven advance preview, does not execute a seal, does not commit a candidate, and does not write memory.

## Storage Location

The runtime creates its state only after an approved POST request:

```text
/home/nic/forge/runtime_state/mea_problem_manifest_store_v1/
  current_problem_manifest.json
  .store.lock
  receipts/<transaction_id>_write_receipt.json
  rollback_plans/<transaction_id>_rollback_plan.json
```

This is Forge-owned MEA runtime state, not RMC memory, not Chroma, and not Identity Vault storage.

## Controlled Write Contract

The POST body must include:

```json
{
  "approval_token": "APPROVE_MEA_PROBLEM_MANIFEST_STORE",
  "operation": "seed",
  "use_fixture": true
}
```

A custom manifest may be supplied instead of `use_fixture`, but it must pass the existing Patch 281 seed-manifest gate.

Patch 294 enforces:

- approval token validation;
- seed-gate validation before persistence;
- initial seed only;
- no candidate-driven advance;
- atomic same-directory write using `fsync` and `os.replace`;
- exclusive file locking;
- SHA-256 content binding;
- an audit receipt and rollback plan;
- idempotent re-submission of the same manifest with no new write;
- rejection of any conflicting manifest rather than overwrite.

## Output-Permission Terminology Correction

The existing MEA schema uses:

```text
output_permissions: sealed
```

Patch 294 keeps this value for compatibility but writes an explicit interpretation alongside it:

```text
sealed = renderer gate closed until a later valid seal and echo-validation path
```

It does **not** mean:

- the candidate was sealed;
- a seal was executed;
- the manifest was advanced through a candidate;
- memory was promoted.

## Deliberate Boundary Change

Previous preview patches proved that `/api/mea/problem-manifest` did not yet exist. Patch 294 intentionally supersedes that negative boundary and adds the controlled GET/POST state-store route. Historical verifiers from Patch 293 and earlier that assert this route is absent are point-in-time proofs and are not the current integrated acceptance test after Patch 294.

## Still Forbidden

```text
/api/mea/seal unavailable
/api/mea/candidates unavailable
candidate commit false
candidate-driven manifest advance false
seal execution false
memory write false
memory promotion false
Chroma write false
Identity Vault write false
LLM call false
shell execution false
network I/O false
renderer output false
```

## Verification

Run:

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile main.py rmc_engine_v1/mea/*.py scripts/patch294_verify.py scripts/test_patch294_mea_problem_manifest_store.py

cd ~
python forge/scripts/patch294_verify.py
python forge/scripts/test_patch294_mea_problem_manifest_store.py
```

The behavior tests use temporary test directories and do not write live MEA state.

## Live Route Testing Caution

A successful approved POST test will create the first live MEA seed state file. Do not run the approved POST until you intend to initialize live MEA state. Test missing-token rejection and GET status first; then perform the approved seed deliberately.
