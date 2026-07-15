# AI.Web Slice 35D — MeaningStructureManifest v1 Canonical Serialization Runtime Specification

**Date:** July 15, 2026  
**Decision Owner:** Nicholas Jacob Bogaert / AI.Web  
**Repository:** `/home/nic/forge`  
**Target package:** `aiweb_language_core_bootstrap.meaning_structure_manifest`  
**Required predecessor:** Slice 35C commit `df4b921a63001af6478d6e9fc00e14a8e26067af`  
**Specification identity:** `aiweb-msm-v1-canonical-serialization`  
**Specification version:** `aiweb-msm-v1-serialization-v1`

## 1. Decision

Slice 35D establishes the first deterministic runtime serialization contract for `MeaningStructureManifestV1`.

The accepted wire form is canonical UTF-8 JSON with:

- canonical format identity `aiweb-msm-v1-canonical-json`;
- canonical format version `1`;
- package identity `aiweb-forge-meaning-structure-manifest`;
- schema identity `aiweb-forge-meaning-structure-manifest-v1`;
- schema version `MSM-v1`;
- exact record fields;
- exact record-kind and lifecycle-state values;
- exact enum values;
- ordered arrays corresponding to immutable Python tuples;
- explicit `null` only where the in-memory schema permits `None`;
- no extra members;
- no omitted members;
- no duplicate object member names;
- no non-standard JSON constants;
- no byte-order mark;
- no surrounding whitespace or trailing data.

This is a transparent implementation decision. Document 2 requires versioned and inspectable semantic custody while leaving final serialized field names, identifiers, hashes, storage format and technical immutability representation open. Slice 35D supplies the bounded runtime representation needed by the accepted production roadmap.

## 2. Governing authority

This specification preserves these Document 2 rulings:

- MSM-v1 is a versioned semantic custody lineage.
- Candidate, selected, outward, expression-linked, validation-linked, delivery-linked, corrected and superseded responsibilities remain distinguishable.
- External authority remains referenced rather than absorbed.
- Issued semantic history must remain reconstructable.
- Existing RMC meaning objects are not automatically migrated or superseded.
- Migration or supersession requires a later authorized and verified decision.

It also preserves the accepted Slice 35A record contract, Slice 35B validation contract and Slice 35C lifecycle transition law without modifying their source files or export surfaces.

## 3. Canonical JSON law

Canonical bytes are produced by the Python standard-library JSON encoder with all of the following fixed settings:

- `ensure_ascii=True`;
- `allow_nan=False`;
- `sort_keys=True`;
- `separators=(",", ":")`;
- ASCII output bytes, which are also valid UTF-8;
- no final newline.

The canonical representation is unique for one accepted in-memory manifest. Repeated serialization of an equal manifest must produce identical bytes and an identical SHA-256 digest.

Array order is preserved. Slice 35D does not reorder records or semantic atoms because their order may carry trace or source significance. Canonicalization standardizes representation, not meaning.

## 4. Envelope law

Every payload has exactly these six top-level members:

- `canonical_format`;
- `canonical_format_version`;
- `manifest`;
- `package_id`;
- `schema_id`;
- `schema_version`.

The envelope repeats package and schema identities that also appear inside the manifest. This redundancy is intentional. It allows strict compatibility checks before the complete record graph is trusted.

## 5. Record representation law

Every record is encoded as a JSON object containing:

- all constructor fields;
- its fixed `record_kind`;
- its fixed or derived `lifecycle_state` where one exists;
- its fixed `schema_version`.

Enum members are encoded only by their accepted string values. Immutable tuples become ordered JSON arrays. Optional text becomes either a JSON string or `null`.

The decoder uses explicit record-by-record construction. It does not use dynamic class lookup, reflection-based object creation, `pickle`, executable expressions or arbitrary type tags.

## 6. Strict deserialization law

Strict deserialization accepts only exact `str` or `bytes` input. It then:

1. decodes UTF-8 strictly;
2. rejects a UTF-8 byte-order mark;
3. parses standard JSON only;
4. rejects duplicate object names;
5. requires the exact envelope fields;
6. verifies canonical format identity and format version;
7. verifies package identity, schema identity and schema version;
8. requires exact fields for every record;
9. rejects unknown enum values;
10. reconstructs immutable Slice 35A records explicitly;
11. runs complete Slice 35B manifest validation;
12. checks serialized transition history against the accepted Slice 35C transition matrix and authority bindings;
13. serializes the reconstructed manifest again; and
14. requires byte-for-byte equality with the received payload.

A payload that represents valid data but uses alternate whitespace, key order, Unicode spelling, escape form or trailing newline is rejected as non-canonical.

## 7. Round-trip equivalence law

For every accepted manifest `M`:

```text
deserialize_manifest(serialize_manifest(M)) == M
```

The following must also hold:

```text
serialize_manifest(deserialize_manifest(P)) == P
```

for every accepted canonical payload `P`.

Dataclass equality, immutable tuple order, enums, optional fields, fixed identities, transition traces and authority references must survive the round trip without widening, narrowing, repair or inferred substitution.

## 8. Version compatibility law

Slice 35D accepts only:

```text
canonical_format_version = "1"
schema_version = "MSM-v1"
```

Unknown format versions are rejected. Unknown schema versions are rejected. A different package identity or schema identity is rejected as incompatible.

No automatic migration is authorized.

The decoder does not:

- guess a predecessor version;
- rename old fields;
- fill missing fields;
- discard unknown fields;
- coerce unknown enums;
- automatically upgrade a payload;
- automatically downgrade a payload;
- translate an existing RMC MeaningManifest;
- supersede a live object;
- call a migration registry;
- invoke external code.

A future schema or format version requires its own explicit specification, code path, tests, verifier, compatibility decision and authorization.

## 9. Lifecycle-history conformance

Slice 35D does not create lifecycle transitions. Slice 35C remains the transition authority.

However, deserialization is a trust boundary. A canonical payload must not be allowed to smuggle in a transition history that could not have been created under the accepted Slice 35C law. Therefore the serializer and decoder verify:

- source and target records exist;
- source and target are different records;
- trace states match the referenced records;
- the direct state pair exists in the accepted transition matrix;
- the transition kind is admitted for that pair;
- required external authority is present;
- the successor carries the named authority or receipt;
- direct ancestry is proven by the successor fields;
- correction and supersession use same-kind immutable successors with authority;
- synthetic `corrected` or `superseded` target records are not accepted.

This is conformance checking only. It does not authorize a new transition.

## 10. Error law

All failures use `CanonicalSerializationError` with a closed `SerializationErrorCode`, a bounded path and a deterministic detail string.

The error surface distinguishes at least:

- payload type failure;
- invalid UTF-8;
- invalid JSON;
- duplicate key;
- non-canonical payload;
- missing or unknown fields;
- type mismatch;
- fixed identity mismatch;
- unknown enum;
- unsupported canonical format;
- unsupported canonical format version;
- incompatible package or schema identity;
- unsupported schema version;
- manifest validation failure;
- lifecycle-history failure.

The exception carries no authority to repair, migrate, persist or execute anything.

## 11. Hash law

`canonical_manifest_sha256()` returns the lowercase SHA-256 digest of the canonical bytes. It performs no filesystem write. The digest is an integrity and regression aid only. It is not evidence authority, acceptance, signature, identity proof, delivery authorization or lifecycle permission.

## 12. Non-authority boundary

Slice 35D does not add:

- persistence;
- file loading or saving;
- database access;
- networking;
- routes or APIs;
- UI work;
- bootstrap integration;
- memory writes;
- evidence writes;
- resource ingestion;
- tool invocation;
- execution;
- delivery;
- LLMs, Ollama, embeddings, vector stores or RAG;
- automatic migration;
- Slice 35E integration;
- Slice 36 structural analysis.

Serialization is not persistence. Deserialization is not trust. A digest is not proof. Version recognition is not migration authority.

## 13. Acceptance requirements

Slice 35D is acceptable only when:

- all Slice 35A behavior tests pass;
- all Slice 35B behavior tests and its verifier pass;
- all Slice 35C behavior tests and its verifier pass;
- Slice 35D import and star-import tests pass;
- canonical serialization is deterministic;
- strict deserialization rejects non-canonical and malformed payloads;
- full record-graph round-trip equivalence passes;
- golden SHA-256 regression checks pass;
- unknown and incompatible versions are rejected;
- lifecycle-history smuggling is rejected;
- no migration or upgrade API exists;
- the independent Slice 35D verifier passes;
- only the five approved Slice 35D paths are committed;
- the repository is clean after commit;
- no push occurs unless separately requested.

## 14. Decision Owner adoption

Nicholas Jacob Bogaert, acting as Decision Owner for AI.Web, directed that missing runtime specifications be created during the build rather than treated as a reason to stop. This specification adopts the bounded runtime decisions above for Slice 35D only, subject to successful local application, testing, independent verification and commit evidence.
