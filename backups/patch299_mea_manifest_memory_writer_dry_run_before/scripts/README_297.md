# Patch 297 — MEA Controlled Atomic Seal / Manifest Advance Commit

## Purpose

Patch 297 is the first candidate-driven persistent transition in the MEA runtime. It commits exactly one explicitly selected **hypothesis** candidate through a narrowly controlled route:

```text
POST /api/mea/seal-transaction-commit
```

It intentionally does **not** expose the canonical `/api/mea/seal` route. The canonical route remains blocked until the controlled commit engine has been proven live with receipt, rollback, readback, and idempotency evidence.

## Required approval and transaction bindings

The route requires approval token:

```text
APPROVE_MEA_SEAL_TRANSACTION_COMMIT
```

The request must submit the exact repaired Patch 296R transaction chain:

```text
source_manifest_hash
source_state_content_hash
candidate_id
candidate_hash
candidate_set_hash
gate_report_hash
transaction_seal_packet_hash
transaction_audit_chain_hash
proposed_new_manifest_hash
transaction_intent_hash
receipt_preview_hash
rollback_preview_hash
```

Patch 297 reruns Patch 296R preflight under the MEA store lock and rejects any stale or mismatched chain.

## Epistemic boundary

For this first persistent transition, Patch 297 commits only:

```text
candidate_id: cg_hypothesis_001
claim_status: hypothesis
proof_debt: 0.85
```

It refuses to commit the higher-ranked speculative branch. Rank can inform review; rank cannot choose or authorize persistence.

## Atomic persistence design

Within the existing MEA store lock, Patch 297:

1. Revalidates the current persisted `M_t` and every submitted Patch 296R hash.
2. Builds a committed advanced-state record bound to the repaired preflight chain.
3. Writes an immutable rollback record containing the complete previous state record.
4. Writes an immutable commit receipt.
5. Atomically replaces only `current_problem_manifest.json` as the final visibility point of `M_(t+1)`.
6. Immediately re-reads and verifies the advanced state plus linked artifacts.

A duplicate submission of the identical transaction is idempotent and writes nothing. A conflicting replay is rejected.

## State transition facts

After the approved live commit succeeds, the MEA persisted state may truthfully report:

```text
selected_candidate_committed: true
seal_executed: true
live_manifest_advanced: true
claim_status: hypothesis
proof_debt: 0.85
```

The manifest field `output_permissions: "sealed"` still means the renderer gate remains closed. It does not grant output rendering or memory promotion.

## Hard boundaries retained

Patch 297 does not permit:

```text
/api/mea/seal canonical route
RMC memory write or promotion
Chroma write
Identity Vault write
LLM call
shell execution
network I/O
rendered user output
UI or launcher mutation
```

## Added module

```text
rmc_engine_v1/mea/seal_transaction_commit.py
```

## Added test and verifier

```text
scripts/patch297_verify.py
scripts/test_patch297_mea_seal_transaction_commit.py
```
