# AI.Web Slice 39A Candidate Meaning Core Schema Runtime Specification

## Status

Schema-only increment. No runtime constructor is installed.

## Accepted parent

- Repository: `/home/nic/forge`
- Branch: `main`
- HEAD: `bb22f0fff6b64deaeeae8285dfabdbdd586d8473`
- Tree: `12131cc607c1dd293b3e741443d42ad69ba83063`
- Subject: `Slice 38H disabled bootstrap integration and Slice 38 closeout`

## Purpose

Slice 39A defines immutable constructor-shape contracts for deterministic
candidate-meaning construction. It creates a versioned companion record family
that can preserve the complete Slice 36 through Slice 38 ancestry required by
later Slice 39 increments.

## Admitted records

1. `CandidateMeaningIdentity`
2. `CandidateMeaningContent`
3. `CandidateMeaningProvenance`
4. `CandidateMeaningAlternativeReference`
5. `CandidateMeaningConstructionReceipt`
6. `CandidateMeaningState`
7. `CandidateMeaningConstructionStatus`

## Closed construction statuses

- `constructed`
- `construction_incomplete`
- `construction_unknown`
- `construction_unsupported`
- `construction_conflicted`
- `predecessor_invalid`

These are construction statuses. They are not gate outcomes.

## Existing MSM-v1 compatibility decision

The accepted Slice 35 `CandidateMeaningRecord` remains unchanged. Its compact
semantic fields do not carry the exact Slice 36 structural ancestry, Slice 37
concept and sense candidate identities, Slice 38 predicate-role-frame candidate
identities, or the registry snapshot chain required by Slice 39.

Slice 39A therefore introduces a versioned companion schema. It does not
supersede, mutate, subclass, or adapt the existing MSM-v1 record. Exact manifest
adaptation remains deferred to Slice 39G.

## Deferred work

- deterministic identity calculation;
- validation;
- lifecycle transitions;
- exact predecessor binding;
- content assembly;
- alternative-set management;
- candidate construction;
- MSM-v1 adaptation;
- disabled bootstrap integration;
- gate evaluation;
- selected meaning;
- truth and evidence status;
- permission, routes, invocation, action, memory, rendering, and delivery.
