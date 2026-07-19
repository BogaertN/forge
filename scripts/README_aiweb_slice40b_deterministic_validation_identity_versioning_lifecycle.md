# AI.Web Slice 40B — Deterministic Gate Governance

This increment makes the accepted Slice 40A verbal-cognition gate records
production-grade and fail-closed without installing a gate evaluator.

## Installed source

The new `governed_lifecycle` companion provides:

- strict type, identifier, tuple, enum, version, and SHA-256 validation;
- canonical field-order custody and canonical JSON bytes;
- deterministic SHA-256 record identifiers;
- exact schema and gate-profile version custody;
- exact cross-record and provenance validation;
- immutable lifecycle and transition records;
- closed lifecycle transition law;
- explicit unknown-version and malformed-record rejection;
- bundle validation and fail-closed assertion helpers.

## Permanent exclusions

This slice does not evaluate any gate family. It does not create gate results,
candidate dispositions, selected meaning, truth, evidence validity,
permission, execution, routes, tools, actions, memory, rendering, delivery,
external-resource loading, model authority, embeddings, vectors, RAG, or
semantic similarity.

## Verification

The behavior test exercises all four gate families, every supported canonical
record type, normal lifecycle transitions, malformed field sets, unknown and
malformed versions, exact provenance mismatches, nondeterministic identity
inputs, forbidden authority flags, illegal lifecycle skips, duplicate records,
and immutability.

The independent verifier protects 491 accepted predecessor files and runs the
current test plus the complete inherited language-core test chain visibly.
