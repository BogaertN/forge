# MEA-RMC-MEMORY-WRITER-BUILD-005

## Purpose

Build 005 installs the first controlled writer from a sealed, replay-verified MEA problem manifest into Forge-owned append-only local JSONL memory.

## Controlled write target

```text
/home/nic/forge/memory/mea_manifest_memory_v1/hypothesis_test_required_records.jsonl
```

## Required gate bindings

```text
sealed_manifest_hash
seal_receipt_hash
memory_writer_preview_hash
approval token
```

The writer does not trust caller-provided values alone. It reconstructs the Patch 299 memory preview from the Patch 297 committed state through the Patch 298 replay verification path and requires exact hash equality before creating storage.

## Locked record boundary

The first record is the already sealed `144hz_substrate_status` candidate:

```text
candidate_id: cg_hypothesis_001
claim_status: hypothesis
proof_debt: 0.85
memory_tier: hypothesis_test_required_record
```

The writer stores no rendered output and does not promote this hypothesis to a verified fact.

## Forbidden effects

Build 005 does not write or call:

```text
Identity Vault
Contribution Economy
CT minting
Influence Ledger
Investment Ledger
RMC rendered-output memory
Chroma
LLM services
Network operations
Shell execution
User-facing rendering
```

## Live activation surface

Live persistence is executed only by the reviewed CLI script:

```text
forge/scripts/mea_rmc_memory_writer_build005_apply.py
```

No HTTP mutation route and no UI write control are introduced in Build 005.
