# AI.Web Forge Slice 35A - MeaningStructureManifest Core Schema Contract

## Scope

This increment adds only the immutable in-memory core schema contract for
MeaningStructureManifest v1 under:

`aiweb_language_core_bootstrap.meaning_structure_manifest`

It does not modify the root bootstrap package exports and does not connect the
schema to Forge runtime behavior.

## Authority mapping

Document 2 binds seven semantic record responsibilities: lineage root,
candidate meaning, selected governed meaning, governed outward meaning,
expression link, external authority reference, and semantic transition trace.
It also binds distinguishable non-selection, governed-result, validation,
delivery, containment, correction, and supersession lifecycle responsibilities.

Document 2 explicitly does **not** prescribe final serialized field names, enum
names, identifiers, hashing rules, persistence, APIs, or storage format. Slice
35A therefore uses a transparent Python mapping:

- frozen, slotted dataclasses for immutable record structures;
- opaque text identifiers, pending Slice 35B validation law;
- tuples for immutable collections;
- closed string enums only for distinctions Document 2 makes binding;
- free-text semantic atoms where Documents 3-6 retain vocabulary authority;
- no custom constructor validation beyond Python dataclass shape enforcement.

## Included records

- `LineageRootRecord`
- `CandidateMeaningRecord`
- `NonSelectionOutcomeRecord`
- `SelectedGovernedMeaningRecord`
- `GovernedResultReferenceRecord`
- `GovernedOutwardMeaningRecord`
- `ExpressionLinkRecord`
- `ValidationLinkRecord`
- `DeliveryContainmentLinkRecord`
- `ExternalAuthorityReferenceRecord`
- `SemanticTransitionTraceRecord`
- `MeaningStructureManifestV1`

## Excluded

This increment contains no deterministic validation rules, identifier
validation, cross-field invariants, lifecycle transition law, serialization,
deserialization, migration, hashing helpers, bootstrap integration, memory
writes, evidence writes, routes, APIs, UI, delivery, tools, actions, LLMs,
Ollama, vectors, embeddings, RAG, network access, external resources, corpus
ingestion, `main.py` change, Slice 35B work, or Slice 36 work.

## Tests

Run from `/home/nic/forge` with Python bytecode writes disabled:

```text
/usr/bin/python3 -B scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py
/usr/bin/python3 -B scripts/aiweb_slice35a_meaning_structure_manifest_core_schema_verify.py
```

The tests explicitly exercise both normal package import and star import. They
also check `__all__`, public export identity, immutability, unsupported keyword
rejection, equality, hashing, absence of import side effects, and prohibited
implementation surfaces.
