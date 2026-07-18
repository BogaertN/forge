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

The canonical `candidate_meaning_id` is derived only from the exact canonical
`CandidateMeaningContent` body, excluding only its own circular `content_id`,
and the exact canonical `CandidateMeaningProvenance` body, excluding only its
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

Strict field-pair canonicalization rejects duplicate, unknown, missing, or
unsupported fields and malformed field-pair structures. No dictionary insertion
order or unordered set traversal becomes identity authority.

## Schema and version custody

`CandidateMeaningVersionCustody` preserves exact custody of the Slice 39A schema,
all record schema identities, candidate version, construction profile, Slice 37
and Slice 38 registry snapshots, compatibility-registry snapshot, canonical
field-order version, and SHA-256 digest algorithm.

## Validation and lifecycle law

Validation is pure, deterministic, and fail-closed. The closed construction
lifecycle stages are:

1. `schema_declared`
2. `provenance_bound`
3. `content_constructed`
4. `candidate_sealed`
5. `candidate_set_referenced`
6. `construction_incomplete`
7. `predecessor_invalid`

Automatic lifecycle progression is prohibited. Lifecycle progression is not
gate progression.

## Exact deferred scope

Slice 39B does not:

- complete predecessor binding owned by Slice 39C;
- assemble semantic payloads owned by Slice 39D;
- preserve candidate sets and alternatives owned by Slice 39E;
- construct actual CandidateMeaning states or construction receipts at runtime, owned by Slice 39F;
- integrate constructed candidates into MeaningStructureManifestV1, owned by Slice 39G;
- connect the constructor to the disabled bootstrap or close Slice 39, owned by Slice 39H;
- evaluate verbal-cognition gates, owned by Slice 40;
- select meaning;
- install routes, tools, actions, memory, rendering, or delivery.

Slice 40 is not the successor of Slice 39E. Slice 40 remains blocked until Slice
39F, Slice 39G, and the Slice 39H closeout are accepted.

## Zero-effect result

```text
runtime constructor installed = 0
MSM candidate integration installed = 0
Slice 39 bootstrap integration installed = 0
Slice 39 closeout created = 0
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
