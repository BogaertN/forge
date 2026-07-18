# AI.Web Slice 39B — Deterministic Validation, Identity, Versioning, and Lifecycle

**Decision Owner:** Nicholas Jacob Bogaert / AI.Web  
**Repository:** `/home/nic/forge`  
**Accepted parent HEAD:** `b01f9e190d2bc6dde39340bda9260aeaa02832d6`  
**Accepted parent tree:** `0c58df87d63cf06dba1f0c535db12b467d65910f`  
**Accepted parent subject:** `Slice 39A candidate meaning core schema`

## Purpose

Slice 39B makes the immutable Slice 39A candidate-meaning record family
fail-closed, reproducible, version-custodied, and lifecycle-governed.

The implementation is isolated in:

```text
aiweb_language_core_bootstrap/
  candidate_meaning_construction/
    governed_lifecycle/
```

The accepted Slice 39A parent files and exports remain unchanged.

## Deterministic identity law

The canonical `candidate_meaning_id` is derived only from:

1. the exact canonical `CandidateMeaningContent` body, excluding only its own
   circular `content_id`; and
2. the exact canonical `CandidateMeaningProvenance` body, excluding only its
   own circular `provenance_id`.

Candidate semantic identity does not read or include timestamps, random values,
process identifiers, filesystem state, environment variables, platform state,
or hash-table iteration order.

Each supporting record also receives a deterministic SHA-256 identity derived
from its exact canonical body with only its own circular identifier excluded.

## Canonical field-order law

Slice 39B declares one exact field order for each supported record type:

- CandidateMeaningIdentity
- CandidateMeaningContent
- CandidateMeaningProvenance
- CandidateMeaningAlternativeReference
- CandidateMeaningConstructionReceipt
- CandidateMeaningState
- CandidateMeaningVersionCustody
- CandidateMeaningLifecycleRecord
- CandidateMeaningLifecycleTransitionRecord
- CandidateMeaningGovernanceBundle

Strict field-pair canonicalization rejects:

- duplicate fields;
- unknown fields;
- missing fields;
- unsupported record types;
- malformed field-pair structures.

No dictionary insertion order or unordered set traversal becomes identity
authority.

## Schema and version custody

`CandidateMeaningVersionCustody` preserves exact custody of:

- Slice 39A schema version;
- identity, content, provenance, alternative-reference, construction-receipt,
  and state schema identities;
- candidate version;
- construction-profile identity and version;
- Slice 37 registry snapshot identity and version;
- Slice 38 registry snapshot identity and version;
- compatibility-registry snapshot identity and version;
- canonical field-order version;
- SHA-256 digest algorithm.

Versions must use canonical `vN`, `vN.N`, or `vN.N.N` form without leading
zeroes.

## Validation law

Validation is pure, deterministic, and fail-closed.

It rejects:

- malformed identifiers;
- malformed SHA-256 values;
- malformed versions;
- duplicate tuple members;
- empty required ancestry;
- mismatched content, provenance, receipt, state, custody, lifecycle, and bundle
  identities;
- mismatched registry snapshot custody;
- duplicated lifecycle records or transitions;
- non-deterministic identity inputs;
- any gate, selection, truth, evidence, permission, route, invocation, action,
  memory, rendering, or delivery authority.

Required minimum ancestry includes source spans, structural candidates,
structural ancestry, constrained trails, phase trails, operator graphs,
operator nodes, operator definitions, operator-key/version pairs, scope
occurrences, and predecessor receipts.

## Lifecycle law

The closed construction lifecycle stages are:

1. `schema_declared`
2. `provenance_bound`
3. `content_constructed`
4. `candidate_sealed`
5. `candidate_set_referenced`
6. `construction_incomplete`
7. `predecessor_invalid`

The closed transition matrix permits only the explicit transitions recorded in
`CANDIDATE_MEANING_LIFECYCLE_TRANSITION_RULES`.

Automatic lifecycle progression is prohibited.

Lifecycle progression is not gate progression. The lifecycle layer cannot
create selected meaning, ambiguity disposition, clarification-required state,
refusal, blocked progression, truth, evidence validity, permission, routes,
invocation, action, memory access, rendering, or delivery.

## Deferred scope

Slice 39B does not:

- complete predecessor binding owned by Slice 39C;
- assemble semantic payloads owned by Slice 39D;
- create candidate sets or alternative ranking owned by Slice 39E;
- construct candidates at runtime;
- adapt records into MSM-v1;
- evaluate verbal-cognition gates;
- select meaning;
- install routes, tools, actions, memory, rendering, or delivery.

## Zero-effect result

```text
runtime constructor installed = 0
candidate ranking installed = 0
gate engine installed = 0
selected meaning installed = 0
routes installed = 0
invocations installed = 0
actions installed = 0
memory installed = 0
rendering installed = 0
delivery installed = 0
```
