# AI.Web Slice 43D — Meaning-Preservation Comparison Runtime Specification

## Status

External additive implementation package for application to the exact accepted
Slice 43C parent:

- repository: `/home/nic/forge`
- branch: `main`
- parent HEAD: `6f2cbafc18ef9eff259bca038d189f1bbe7fc4c6`
- parent tree: `c378cb1cd0be715160a9f919ea01815799ee4f56`
- parent subject: `Slice 43C authorized meaning and proposed-expression admission`

This document does not accept the implementation, authorize staging or commit,
or grant delivery or production authority.

## Purpose

Consume only the exact accepted Slice 43C source-admission result and its exact
accepted Slice 42 ancestry. Deterministically compare the admitted authorized
meaning custody against the admitted proposed-expression custody and create one
finding for each required dimension.

## Exact comparison dimensions

1. semantic content;
2. communicative purpose;
3. claim status;
4. scope;
5. certainty;
6. evidence status;
7. caveats and limitations;
8. refusal state;
9. unresolved conditions;
10. action status;
11. memory status;
12. delivery status;
13. required next-step or hold status.

## Finding outcomes

Each dimension remains independent and receives exactly one deterministic
finding outcome:

- `preserved`;
- `changed`;
- `missing`;
- `unsupported`;
- `conflicted`;
- `indeterminate`.

These are dimension-level findings. They are not an overall Echo disposition.

## Input law

The public comparison entry point requires:

- an exact Slice 43D comparison request;
- the exact accepted Slice 43C `SourceAdmissionResult`;
- the exact accepted Slice 42H closeout result bound by that admission;
- no arbitrary raw text;
- an explicit comparison request;
- supported exact schema and profile versions.

The validator independently verifies the complete Slice 43C result, exact
accepted identities, exact Slice 42 ancestry, and cross-record references before
comparison.

## Comparison law

For each dimension, the runtime creates immutable source and proposed-expression
snapshots. Each snapshot records:

- exact field paths;
- normalized values derived from typed predecessor records;
- exact evidence references;
- exact trace references;
- supported, conflict, and indeterminate custody.

Outcome precedence is:

1. conflicted;
2. unsupported;
3. indeterminate;
4. missing;
5. exact tuple equality means preserved;
6. otherwise changed.

Neither snapshot is rewritten. No nearest-known, similarity, model, or hidden
repair path exists.

## Output law

The successful runtime output is an immutable comparison package containing
exactly 13 ordered findings and a deterministic result identity. It records that
comparison and finding creation occurred. It does not include an overall
`PASSED`, `REJECTED`, or `CONTAINED` decision.

## Deferred and prohibited authority

Slice 43D does not:

- classify drift or decide materiality;
- decide an Echo disposition;
- issue rejection or containment;
- correct, repair, or rewrite expression text;
- modify MSM-v1 or create a validation link;
- authorize or perform delivery;
- create routes or APIs;
- access a network, filesystem, external resource, or runtime memory;
- invoke tools or perform actions;
- use an LLM, EchoForge, embeddings, vectors, RAG, similarity, a neural parser,
  or a hidden classifier;
- determine truth, evidence sufficiency, permission, or execution authority;
- supersede GP-014.

## Required proof

Acceptance requires Nic to run on `/home/nic/forge`:

1. the Slice 43D behavior test;
2. the Slice 43D independent verifier;
3. the inherited Slice 43C verifier invoked visibly by the Slice 43D verifier;
4. protected-predecessor verification;
5. exact Git and payload containment checks;
6. the applied-result collector.

Nothing may be staged or committed until the returned applied evidence is
independently accepted.
