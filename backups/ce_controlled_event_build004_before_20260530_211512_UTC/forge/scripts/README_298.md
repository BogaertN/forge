# Patch 298 — MEA Live Trace Replay Verification

## Purpose

Patch 297 performed the first controlled atomic MEA manifest advance and Patch 297R clarified the response contract for idempotent duplicate requests. Patch 298 implements the next original MEA requirement: verify that the committed transition can be reconstructed from its stored trace and evidence chain without performing any new transition.

## New Route

```text
POST /api/mea/replay
```

Required approval token:

```text
APPROVE_MEA_LIVE_TRACE_REPLAY
```

The request must explicitly identify the already committed transaction by its transaction ID, transaction-intent hash, candidate ID/hash, committed manifest hash, and committed state-content hash.

## Replay Chain Verified

Patch 298 reads the integrity-verified committed state, its immutable advance receipt, and its immutable rollback record. It restores the prior source state from the rollback record, verifies that source state and its original linked seed artifacts, rebuilds the selected candidate through the existing operator/candidate/scoring/gate pipeline, recompiles the transaction objects from that restored source, and compares every stored binding with the recomputed binding:

```text
restored M_t
  -> rebuilt candidate hash
  -> replayed gate path
  -> replayed transaction seal-packet hash
  -> replayed transaction audit-chain hash
  -> replayed transaction-intent hash
  -> replayed receipt-preview hash
  -> replayed rollback-preview hash
  -> replayed committed manifest hash M_(t+1)
  -> stored advance receipt and rollback record
```

## Output Hash Binding Clarification

The committed manifest operator trace retains the Patch 296R deferred output-hash marker to avoid self-referential mutation. Patch 298 verifies the deliberate binding mode: the committed manifest hash is bound externally by the committed state record and immutable receipt rather than by altering its own embedded historical trace after hashing.

## Hard Boundaries

Patch 298 is verification-only:

- It does not write MEA runtime state.
- It does not commit a candidate.
- It does not advance the live manifest.
- It does not execute a new seal.
- It does not write or promote memory.
- It does not write Chroma or Identity Vault state.
- It does not call an LLM, execute shell commands, perform network I/O, or render output.
- It does not expose the canonical `/api/mea/seal` route.

## Validation Rule

Installation and verification may call `/api/mea/replay` against the already committed state only after capturing before/after state hashes. A successful replay must return `REPLAY_VERIFIED_NO_MUTATION` and prove the state-store file hashes are unchanged.
