# AI.Web Slice 43C Authorized Meaning and Proposed-Expression Admission Runtime Specification

## Purpose

Create a deterministic, fail-closed admission layer between the accepted Slice
42 outward-expression closeout and the later Slice 43D preservation comparison.
The layer consumes only typed accepted predecessor records. It never consumes
raw text as authority.

## Runtime package

`aiweb_language_core_bootstrap.rmc_echo_runtime.authorized_source_admission`

## Exact input

`SourceAdmissionRequest` contains:

- the exact accepted `DisabledOutwardExpressionCloseoutResult`;
- the closed Slice 43C schema and profile versions;
- the exact admission operation name;
- an explicit admission flag;
- `raw_text=None`;
- a deterministic request identity.

## Exact accepted ancestry

The validator binds the exact accepted identities for:

1. Slice 41E selected governed meaning and selection custody;
2. Slice 42C expression-eligibility result;
3. Slice 42D preservation-obligation package;
4. Slice 42E controlled expression plan;
5. Slice 42F realization input, result, candidate, trace, and receipt;
6. Slice 42G integration input, result, receipt, source manifest, successor
   manifest, governed outward meaning, external-authority reference, expression
   link, and both semantic-transition traces;
7. Slice 42H fixture, result, acceptance record, stage receipts, and closeout
   custody.

The validator calls the accepted predecessor validators only after all direct
identity, version, link, delivery, authority, and lineage gates pass. Malformed
or hostile input therefore fails before expensive ancestry traversal.

## Output records

- `AuthorizedMeaningAdmissionRecord`
- `ProposedExpressionAdmissionRecord`
- `EchoValidationAdmissionPackage`
- `SourceAdmissionResult`

The package embeds immutable Slice 43A reference and input-boundary records and
adds Slice 43C admission custody without changing the Slice 43A schema.

## Determinism

All Slice 43C records use canonical UTF-8 JSON, closed field order, explicit enum
values, deterministic SHA-256 digests, and stable prefixed identifiers. Time,
randomness, process identity, environment state, filesystem order, hash-map
order, models, and similarity are excluded from identity.

## Rejection outcomes

Closed status values distinguish raw text, unsupported version, identity
invalidity, missing link, orphan expression, already-delivered candidate,
unauthorized candidate, inconsistent ancestry, unaccepted source, and general
invalid request. Held outcomes never contain an admission package and never
create downstream authority.

## Lifecycle and duplicates

The accepted Slice 43B governed-lifecycle layer validates the created immutable
reference records, package, and result. Exact duplicates and identity collisions
remain rejection conditions; admission does not mutate or replace predecessor
records.

## Non-authority

Successful admission means only that exact accepted source custody is available
for Slice 43D. It is not meaning-preservation proof, Echo approval, disposition,
MSM integration, delivery permission, truth, evidence, action, tool, memory, or
execution authority.
