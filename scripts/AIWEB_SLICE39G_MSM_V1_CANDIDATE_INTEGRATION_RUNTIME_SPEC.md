# AI.Web Slice 39G MeaningStructureManifest Candidate Integration Runtime Specification

## Purpose

Place exact Slice 39F constructed candidate meanings into the accepted Slice 35
`MeaningStructureManifestV1` custody chain without changing MSM-v1 and without
creating any gate, selection, truth, evidence, permission, action, rendering,
or delivery authority.

## Accepted input

The adapter accepts only one exact validated
`CandidateMeaningConstructorResult`.

Raw text, arbitrary objects, rejected constructor results, incompatible
profiles, altered identities, mixed sources, and unknown preservation mappings
fail closed.

## Exact adapter path

1. Validate the exact Slice 39F result.
2. Require one exact source event and checksum for constructed candidates.
3. Create one inward MSM-v1 lineage root for the source.
4. Create one deterministic MSM-v1 `CandidateMeaningRecord` projection for each
   unique constructed candidate state.
5. Preserve full Slice 36-39F custody in versioned companion records.
6. Add candidate construction ancestry traces to MSM-v1.
7. Add non-authorizing external references to construction, provenance,
   limitation, and alternative companion custody.
8. Validate the complete immutable MSM-v1 manifest.
9. Return the manifest and all exact companion records in one deterministic
   in-memory integration result.

## Projection law

The MSM-v1 candidate projection carries only fields that are semantically safe
for the accepted Slice 35 schema:

- exact source-expression reference;
- candidate communicative-act reference;
- candidate concept references;
- candidate semantic-relation references;
- candidate modifiers;
- unresolved referents;
- authority-sensitive implications;
- mapped semantic preservation classes.

Sense, predicate, frame, role-layout, capability, effect, exact provenance,
receipt, limitation, and alternative custody remain in typed companion records.
They are not silently packed into unrelated MSM-v1 fields.

## Zero-candidate law

An explicit zero-input Slice 39F result has no source lineage. Slice 39G
preserves that result without inventing a manifest.

A typed Slice 39F zero-candidate result with one exact source event and checksum
creates an inward MSM-v1 lineage root with an empty candidate collection. It
does not create a non-selection outcome.

## Determinism

All Slice 39G identities use canonical UTF-8 JSON and SHA-256. No timestamp,
randomness, process identity, environment state, filesystem state, network
state, or hash-table iteration order participates in identity.

## Side-effect boundary

Slice 39G is explicitly invoked, offline, standard-library only, read-only,
in-memory only, deterministic, source preserving, and fail closed. It performs
no filesystem or network access and loads no external resources.

## Deferred scope

Disabled bootstrap integration, rollback proof, full repeated-fixture
closeout, predecessor-tree recovery, and the final Slice 39 acceptance record
belong to Slice 39H.

Verbal cognition gates, ambiguity disposition, clarification, rejection,
blocked progression, and selected meaning belong to Slice 40.
