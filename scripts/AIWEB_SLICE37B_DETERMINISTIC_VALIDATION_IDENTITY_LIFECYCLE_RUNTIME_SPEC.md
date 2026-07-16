# AI.Web Slice 37B — Deterministic Validation, Identity and Lifecycle Law

**Decision Owner:** Nicholas Jacob Bogaert / AI.Web
**Repository:** `/home/nic/forge`
**Accepted parent:** Slice 37A at `432d38eb8829dbf18c05d95e909a69df80229c18`
**Implementation state:** Validation and lifecycle-law increment only

## Purpose

Slice 37B adds deterministic validation, exact version-record identity, material
lineage identity, provenance enforcement, namespace and scope validation,
explicit lifecycle transition records, a closed transition matrix, quarantine,
rejection, correction, deprecation and supersession ancestry, and
collection-level duplicate/conflict detection.

It does not populate the controlled registry. It does not perform concept
lookup, map a source occurrence, select a sense, create a semantic relation
instance, consume a Slice 36 structural result, construct CandidateMeaning, or
create runtime, route, tool, memory, action, rendering or delivery authority.

## Record law

Every governed record remains an immutable Slice 37A record. Slice 37B adds:

- `ConceptLifecycleAuthorityRecord`;
- `ConceptLifecycleTransitionRecord`;
- `ConceptLifecycleTransitionRule`;
- `ConceptLifecycleTransitionDecision`;
- `ConceptGovernanceBatch`;
- deterministic validation reports and issues.

A version-record ID hashes the complete canonical version body. A material
lineage ID hashes only the record-kind-specific fields that remain stable across
versions. Recomputed identity must match exactly.

## Version law

Resource versions use only `vN`, `vN.N`, or `vN.N.N`, without leading zeroes.
A transition target version must compare strictly greater than its source.
Version and lifecycle state are scope-specific. Neither implies installation,
runtime availability, or production status.

## Transition law

A lifecycle transition must preserve:

- exact source and target record identities;
- the same material lineage and exact resource kind;
- prior and new lifecycle states;
- strictly advancing version;
- source authority and provenance;
- decision-owner and human-approval references;
- reason and exact scope;
- affected record references;
- prohibited uses;
- unresolved dependencies and missing authority;
- required conflict, unknown-state and dependency reviews;
- prior immutable record ancestry;
- explicit non-LLM provenance.

Automatic transitions are prohibited. Unknown may return to candidate review but
may not jump directly to admitted. Candidate admission requires complete source,
conflict, unknown-state, dependency and human review. Active states remain
blocked while dependencies or authority are missing.

## Quarantine law

Quarantine requires exact cause references and exact release requirements. It
is not pending approval and creates no partial authority. Release requires the
exact incoming quarantine ancestry, complete review, human approval and explicit
resolution of every recorded cause.

## Rejection law

Rejection preserves reason, scope, ancestry and materially equivalent blocked
reentry keys. It is negative authority, not deletion. Reopening rejected
material requires a new candidate version and an exact reference to the prior
rejection transition.

## Correction, deprecation and supersession

Correction creates a new version in the same material lineage and preserves the
prior record. Deprecation blocks new use while preserving bounded legacy
ancestry. Supersession identifies a distinct successor resource, preserves the
replaced record and limits the successor to the explicit supersession scope.
No transition silently expands authority.

## Collection integrity

A governance batch rejects:

- duplicate version-record IDs;
- duplicate or conflicting lineage/version records;
- missing provenance;
- missing or wrong-kind references;
- orphan versions;
- multiple incoming transitions;
- multiple outgoing transitions;
- active records without admission history;
- unresolved quarantine release;
- invalid successor references;
- duplicate transition or authority identities;
- any installed registry, lookup, mapping, relation, structural or runtime effect.

Validation is pure, deterministic and fail-closed. It does not apply a
transition or write state.
