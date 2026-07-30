# Forge RMC exact language store v2

The Language Core now has a trusted, read-only RMC provider. It admits files
from exactly these repository-local directories:

```text
memory/rmc_language_core_v1/
├── stable/  # accepted_stable records
└── live/    # reserved; current governed approval is stable-only
```

The directories may be absent or empty. That produces `TRUSTED_EMPTY` and does
not weaken the compiler. The path retains its original `v1` directory name for
custody continuity, while admitted records use the hardened v2 schema.

## Record contract

Each `.json` file is one immutable, content-addressed record created by
`build_exact_language_memory_record`. Its filename is the hexadecimal digest
portion of its `record_id`, plus `.json`.

A record contains only:

- the exact Forge registry ID;
- an exact semantic contract binding polarity, speech act, purport, frame,
  grammar rule, predicate, and semantic signature;
- exact concept, sense, relation, role, and ancestry IDs;
- exact source and operator-approval receipt IDs;
- a content-addressed provenance-chain ID;
- lifecycle, immutability, and read-only assertions; and
- explicit false assertions for raw text, token streams, embeddings, and
  vectors.

IDs are checked against the current Forge-owned registry. An ancestry set must
contain both an `input_event:` ID and a `source_form:` ID. Role IDs must agree
with the role relations in the same record.

The trusted loader separately derives the only valid stable target and the only
valid promotion-receipt identity from the record plus its source and approval
receipts. The record is not admitted unless that persisted promotion receipt is
present and exact. This avoids a content-addressing cycle in the record while
still enforcing the distinct Promote decision.

The only installed writer is the governed local transaction in
`rmc_language_promotion.py`: Prepare performs no write, Approve writes the
source and approval receipts, and Promote writes one promotion receipt plus one
exact stable record. Ordinary Ask Forge requests have no writer path. No live
record approval contract is installed, so `live/` remains fail-closed.

## Fail-closed behavior

One malformed, unknown, non-canonical, misnamed, group- or world-writable,
symlinked, hardlinked, tampered, or unsupported file rejects the complete store.
A rejected provider projects an empty compiler snapshot and Ask Forge returns a
typed error; it does not use partially valid memory.

The provider does not perform raw-word overlap, tokenization, embeddings,
vectors, approximate matching, similarity scoring, or runtime writes. Exact
identity intersections are audit facts, not hidden authority. The existing
public Ask Forge endpoint still accepts only `{"source_text": "..."}` and
rejects caller-supplied memory snapshots.

## Verification

From `/home/nic/forge`, run:

```bash
python scripts/test_aiweb_rmc_exact_language_store.py .
```

The test covers stable admission and live refusal, all five exact identity
types, semantic-contract mismatches, all three receipts, deterministic
projection, missing/tampered/mismatched evidence, unsafe filesystem objects,
and public snapshot-injection rejection.
