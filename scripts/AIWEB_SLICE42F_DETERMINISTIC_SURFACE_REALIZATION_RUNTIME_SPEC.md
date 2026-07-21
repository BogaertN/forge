# AI.Web Slice 42F — Deterministic Surface Realization Runtime Specification

## Accepted base

- Repository: `/home/nic/forge`
- Branch: `main`
- Parent HEAD: `48f4b6d698350461eea3aec95b7b2cc8ec08b204`
- Parent tree: `734b9d55e5341b8d60de982ad9b3f6ca7d425c98`
- Parent subject: `Slice 42E controlled expression plan construction`

## Purpose

Slice 42F realizes one exact accepted Slice 42E expression plan into one
human-readable deterministic expression candidate.

The runtime requires:

1. the exact Slice 42E plan input;
2. the exact validated Slice 42E plan result;
3. the exact controlled expression plan;
4. a separate explicit realization-authority record;
5. exact admitted deterministic realization-rule references;
6. an exact controlled-resource bundle;
7. exact predecessor receipts, trace, provenance and version custody.

## Realization law

The runtime:

- selects only the template admitted for the governed plan disposition;
- requires an exact controlled claim-text resource before realizing an
  authorized affirmative claim;
- produces nonaffirmative language for blocked, refusal-preserving and
  unresolved-preserving plans;
- exposes certainty and evidence status without upgrading them;
- exposes limitations, qualifications, caveats, refusal boundaries,
  unresolved conditions, ambiguity and unsupported states when present;
- exposes memory, external-resource, delivery, privacy and identity custody;
- binds the exact text, segments, rules, resources, plan and ancestry into a
  deterministic trace and receipt.

## Fail-closed authorized-claim rule

An authorized plan is not sufficient by itself to invent human wording.
An exact admitted claim-text resource bound to the selected-meaning custody
reference is required. If it is absent, realization must hold rather than
guess.

## Output boundary

The output is an `UnvalidatedExpressionCandidate`.

It is:

- human-readable;
- deterministic;
- trace-bound;
- receipt-bound;
- unvalidated;
- not Echo-approved;
- not delivery-authorized;
- not delivered.

Slice 42F does not create a governed outward-meaning MSM record, modify
MSM-v1, activate bootstrap integration, access memory, load external
resources, create routes, call tools, perform actions or supersede GP-014.
