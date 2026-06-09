# Patch 299 — MEA Manifest Memory Writer Dry-Run

## Purpose

Patch 299 installs a non-mutating MEA manifest memory-writer preview layer after the committed Patch 297 hypothesis transition and the successful Patch 298 live trace replay verification.

The MEA architecture places `manifest_memory_writer.py` after sealing and before renderer integration. This patch does not write memory. It builds the exact bounded memory-record object that a future approval-gated local writer may store after further compatibility work.

## Added module

```text
forge/rmc_engine_v1/mea/manifest_memory_writer.py
```

## Added routes

```text
GET  /api/mea/memory-writer/status
POST /api/mea/memory-writer-dry-run
```

Approval token for the POST dry-run route:

```text
APPROVE_MEA_MEMORY_WRITER_DRY_RUN
```

## Source requirements

The dry-run accepts only an explicitly targeted committed state and internally reruns Patch 298 replay verification. The current accepted source is:

```text
candidate_id:              cg_hypothesis_001
claim_status:              hypothesis
proof_debt:                0.85
committed_manifest_hash:   852feb2c1491683bca39d89ee3d86e43e4f8fe9aecad2c403c9be70018c95a83
transaction_intent_hash:   9ff10b208c0adc06dedff97a59415962f9786c20bc8d7bd18c877fd58a876691
```

## Memory record semantics

The returned memory record is a preview only. It explicitly records:

```text
memory_tier: hypothesis_test_required_record
verified_fact: false
renderer_output_permitted: false
memory_write_executed: false
```

The record binds the committed manifest, source manifest, state-content hashes, candidate hash, transaction hashes, receipt hash, rollback hash, and replay verification outcome.

## RMC Memory Writer integration boundary

The existing core RMC Memory Writer was audited before this patch. It consumes rendered and echo-validated output. Patch 299 does not fabricate an echo report and does not invoke that downstream writer. It defines the MEA manifest-record adapter boundary only; renderer and Echo Validator integration remain future work.

## Rejected draft handling

The architecture eventually requires rejected drafts to route to containment-aware memory. The currently committed Patch 297 transition contains no real rejected-draft lineage selected for storage. Patch 299 therefore returns an empty rejected-draft preview list rather than fabricating one.

## Hard boundaries

Patch 299 performs:

```text
No live memory write
No JSONL ledger write
No MEA runtime-state write
No Chroma write
No Identity Vault write
No candidate commit
No new manifest advance
No new seal execution
No memory promotion
No rendering
No LLM call
No shell execution
No network I/O
No canonical /api/mea/seal route
```
