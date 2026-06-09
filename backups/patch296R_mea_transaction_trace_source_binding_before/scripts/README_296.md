# Patch 296 — MEA Persisted-State Seal / Advance Transaction Preflight

## Purpose

Patch 296 closes the binding seam exposed when Patch 294 introduced real persisted MEA state and Patch 295 introduced live candidates generated from that state. It adds one approval-token POST route that accepts an explicitly selected candidate and proves a deterministic future seal-and-advance transaction chain without performing any mutation.

## New Route

```text
POST /api/mea/seal-transaction-preflight
```

Approval token:

```text
APPROVE_MEA_SEAL_TRANSACTION_PREFLIGHT
```

Required request values:

```text
source_manifest_hash
source_state_content_hash
candidate_id
candidate_hash
```

Optional stronger bindings:

```text
candidate_set_hash
gate_report_hash
```

## Transaction Binding Chain

```text
verified persisted M_t state and state-content hash
  -> explicit submitted live candidate id/hash
  -> live candidate report and gate report hash
  -> transaction-scoped seal-packet preview hash
  -> transaction audit-chain preview hash
  -> proposed M_(t+1) hash
  -> future receipt preview hash
  -> future rollback preview hash
```

## Safety Rule

Ranking does not select. The current candidate score can report `cg_branch_001` above `cg_hypothesis_001`, but this route does not act on rank. The operator must submit a candidate id and matching candidate hash explicitly.

## Hard Boundary

Patch 296 is non-mutating. It does not create `/api/mea/seal`, execute a seal, commit a candidate, advance the persisted manifest, write files, write MEA state, write RMC memory, write Chroma, touch Identity Vault, call an LLM, execute shell, make network calls, or render user output.

## 144 Hz Anti-Confabulation Behavior

A preflight for `cg_hypothesis_001` remains `hypothesis`, preserves proof debt at `0.85`, adds the test-required unresolved gap to the proposed next-manifest preview, and never becomes a verified claim. A recall candidate cannot enter transaction preflight; a rejected/tamper candidate cannot enter transaction preflight.

## Verification

```bash
python forge/scripts/patch296_verify.py
python forge/scripts/test_patch296_mea_seal_transaction_preflight.py
```
