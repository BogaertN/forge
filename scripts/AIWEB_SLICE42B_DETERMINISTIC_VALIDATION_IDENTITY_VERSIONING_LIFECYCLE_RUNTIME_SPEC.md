# AI.Web Slice 42B Deterministic Validation, Identity, Versioning, and Lifecycle Runtime Specification

## Status

Additive validation-and-custody increment beneath
`aiweb_language_core_bootstrap.outward_expression_runtime.governed_lifecycle`.
No accepted Slice 42A file is modified.

## Accepted parent

- Repository: `/home/nic/forge`
- Branch: `main`
- HEAD: `bf38d5dbefd27d6cc69f38f5053071316d1ded63`
- Tree: `ce3232f0adef1de5b7488ff1ec10a919cd9b54af`
- Subject: `Slice 42A outward expression runtime core schema and authority contract`

## Purpose

Slice 42B supplies deterministic structural governance for the immutable Slice
42A outward-expression schema:

1. canonical UTF-8 JSON serialization with exact dataclass field order;
2. deterministic SHA-256 record and bundle identities;
3. exact schema, specification, validation-profile, and parent-version custody;
4. exact predecessor-reference custody;
5. immutable validation and lifecycle successor records;
6. a closed explicit lifecycle transition law;
7. malformed-record, duplicate-record, identity-collision, unknown-version, and
   inconsistent-reference rejection;
8. fail-closed cross-record preservation checks.

## Canonical identity law

Canonical records use:

- admitted dataclass field order;
- enum values rather than implementation representations;
- tuples represented as ordered arrays;
- string-key mappings sorted lexicographically;
- UTF-8 JSON;
- no insignificant separator whitespace;
- no timestamps, randomness, process identity, environment state, filesystem
  state, or hash-table iteration order;
- SHA-256 only.

The identity field itself is excluded from its record digest. Bundle ID and
bundle digest are excluded from the bundle digest. All remaining fields are
included.

## Exact record custody

Slice 42B governs all ten Slice 42A schema record types plus:

- `OutwardExpressionVersionCustody`;
- `OutwardExpressionLifecycleRecord`;
- `OutwardExpressionLifecycleTransitionRecord`;
- `OutwardExpressionGovernanceBundle`.

## Cross-record consistency

Validation requires exact internal references through the complete chain:

selected-meaning source custody → authority requirement → preservation custody
→ eligibility-status custody → governed-outward-meaning boundary → expression
plan boundary → realized-expression boundary → trace boundary → receipt
boundary.

It also fails closed when inherited limitations, unresolved conditions,
ambiguity ancestry, refusal boundaries, caveats, qualifications, preservation
classes, selected-meaning traces, or predecessor receipts are omitted from the
later custody records that must preserve them.

## Lifecycle law

Admitted success stages are:

`schema_declared → version_bound → predecessors_bound →
cross_record_validated → record_validated → record_sealed`.

Every transition is explicit. Automatic progression is prohibited. Incomplete,
unknown-version, malformed, invalid-predecessor, duplicate-record, and
identity-collision outcomes are separate blocked states. Resumption begins a
new immutable successor chain and preserves the blocked predecessor identity.

## Authority-zero law

A structurally valid, canonically serialized, identity-valid, lifecycle-sealed
record is not an expression authorization. Slice 42B does not:

- admit selected-meaning-chain authority;
- admit outward-expression authority;
- evaluate expression eligibility;
- project preservation obligations;
- construct governed outward meaning;
- construct an expression plan;
- create an expression candidate or human-readable text;
- modify or integrate MSM-v1;
- perform Echo validation;
- enable bootstrap integration;
- deliver output;
- determine truth, validate evidence, grant permission, or authorize execution;
- create routes or APIs, invoke tools, execute actions, access memory, touch the
  filesystem or network, load external resources, or use a model, embedding,
  vector, RAG, similarity engine, neural parser, or hidden classifier;
- supersede GP-014.

## Deferred work

Authority admission and expression-eligibility evaluation remain Slice 42C.
All Slice 42D through 42H work, Slice 43 Echo validation, and later delivery or
action authority remain separately authorized and tested.
