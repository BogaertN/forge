# AI.Web Slice 39F Deterministic Candidate Meaning Constructor Runtime Specification

## Purpose

Create actual immutable in-memory `CandidateMeaningState` records and exact
construction receipts from accepted typed Slice 37 and Slice 38 proposal
outputs, while preserving the full Slice 36–39 ancestry chain and all permanent
candidate-only boundaries.

## Bounded execution path

1. Accept an exact tuple of `CandidateMeaningConstructorInput` records.
2. Reject any raw text or arbitrary non-typed input.
3. Invoke Slice 39C complete predecessor custody for every input.
4. Require exact source, ancestry, registry snapshot, and resource-version
   verification from Slice 39C.
5. Invoke Slice 39D candidate semantic-content assembly.
6. Pass the exact assembly results to Slice 39E candidate-set preservation.
7. Construct one CandidateMeaning identity per unique exact content/provenance
   pair.
8. Construct directional alternative references from Slice 39E exact material
   alternative custody without determining ambiguity.
9. Construct one deterministic receipt and one immutable CandidateMeaningState
   per unique candidate.
10. Return an immutable constructor result containing the Slice 39E set,
    constructed states, receipts, source identities, counts, and zero-authority
    proof flags.

## Construction-status law

Construction statuses are assigned by exact content custody only:

- conflicting role references → `CONSTRUCTION_CONFLICTED`;
- unsupported reason references → `CONSTRUCTION_UNSUPPORTED`;
- unknown reason references → `CONSTRUCTION_UNKNOWN`;
- missing role or unresolved referent references → `CONSTRUCTION_INCOMPLETE`;
- otherwise → `CONSTRUCTED`.

This ordering is deterministic and construction-only. It does not reject a
candidate, ask clarification, resolve ambiguity, determine gate passage, or
select meaning.

## Deterministic identity

Candidate identity uses the accepted Slice 39B identity law: exact governed
CandidateMeaningContent plus exact CandidateMeaningProvenance. Constructor-owned
profile, wrapper, and result identities use canonical UTF-8 JSON and SHA-256.
No time, randomness, process identity, environment state, filesystem state, or
hash-table iteration order participates in identity.

## Side-effect boundary

The constructor is explicitly invoked, offline, standard-library only,
read-only, deterministic, in-memory only, source preserving, and fail closed.
It performs no filesystem or network access and loads no external resources.
It does not use an LLM, model, embedding, vector, RAG, or semantic similarity.

## Deferred scope

MeaningStructureManifest integration belongs to Slice 39G. Bootstrap
integration, rollback proof, complete predecessor protection, repeated fixture
construction, and final Slice 39 acceptance belong to Slice 39H. Verbal
cognition gates, ambiguity disposition, clarification, rejection, blocked
progression, and selection belong to Slice 40.
