# AI.Web Slice 41E — MSM-v1 Selected Meaning Integration and Custody Runtime Specification

## Runtime entry point

`integrate_selected_meaning_into_manifest(input)` accepts one exact `MsmSelectedMeaningIntegrationInput` and returns one deterministic `MsmSelectedMeaningIntegrationResult`.

## Required input custody

The input must contain:

- an exact valid Slice 40H `MsmGateIntegrationResult`;
- its exact `MsmGateCustodyCompanionV1`;
- an exact valid Slice 41D `SelectedMeaningConstructionInput`;
- an exact valid Slice 41D `SelectedMeaningConstructionPackage`;
- the exact selected candidate once in the source MSM-v1 manifest;
- the exact Slice 41D selection receipt;
- the exact shared lineage and gate-composition ancestry;
- the approved fail-closed Slice 41E authority profile.

## Deterministic successor operation

The adapter:

1. validates the complete source manifest and canonical round trip;
2. creates an external-authority record whose external object is the exact Slice 41D selection receipt;
3. creates one integrated selected record with exact candidate and dormant-record semantic content;
4. appends the candidate-to-selected transition through accepted MSM-v1 lifecycle law;
5. computes a deterministic successor manifest identity from source custody and the three added records;
6. creates a versioned companion preserving before-and-after candidate, non-selection, authority, transition, gate, and selection ancestry;
7. creates a deterministic receipt containing source and successor canonical SHA-256 values;
8. validates the complete successor manifest and all cross-record identities.

## Exact additive delta

The source and successor may differ only in:

- manifest identity;
- one appended selected-governed-meaning record;
- one appended external-authority-reference record;
- one appended semantic-transition-trace record.

All other MSM-v1 sections must be byte-for-byte equivalent after canonical serialization. Candidate and non-selection collection order is retained exactly.

## Failure behavior

Wrong types, malformed nested records, missing custody, changed lineage, changed candidate content, semantic enrichment or deletion, candidate or non-selection deletion, altered Slice 40H custody, changed selection receipt, noncanonical IDs, populated downstream sections, or any prohibited authority flag fail closed with explicit validation issues. Validation must not raise an unhandled exception for deliberately malformed nested records.

## Side-effect boundary

The runtime is pure, in-memory, standard-library Python. It does not read or write files, access networks or external resources, stage or commit Git state, call a model, rank candidates, render, deliver, or activate bootstrap routes.
