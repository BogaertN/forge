# AI.Web Slice 42G MSM-v1 Outward-Meaning and Expression-Link Custody Runtime Specification

## Required exact inputs

- exact accepted Slice 41E MSM selected-meaning integration input and result;
- exact accepted Slice 42F surface-realization input and result;
- exact unvalidated expression candidate, realization trace, and realization receipt;
- strict Slice 42G authority profile;
- explicit selected-to-outward and outward-to-expression transition reasons.

## Deterministic additions

The immutable successor adds only:

- one `ExternalAuthorityReferenceRecord` whose external object reference is the exact expression-candidate identity;
- one `GovernedOutwardMeaningRecord` whose prior selected meaning is exact and whose claims, qualifications, prohibitions, dependencies, and preservation classes are deterministically derived from the candidate and accepted realization boundaries;
- one `ExpressionLinkRecord` linking the exact governed outward meaning to the exact candidate;
- two `SemanticTransitionTraceRecord` instances using admitted ancestry transitions.

## Required preservation

The successor retains byte-equivalent record tuples for:

- lineage root;
- candidate meanings;
- non-selection outcomes;
- selected governed meanings;
- governed-result references;
- validation links;
- delivery or containment links.

It also preserves alternatives, unresolved conditions, selected-meaning ancestry, realization ancestry, caveats, refusal boundaries, ambiguity, unsupported states, certainty, evidence status, scope, memory boundaries, resource status, delivery status, and privacy/identity boundaries.

## Validation

Validation is fail-closed and verifies:

- exact predecessor input/result chains;
- exact candidate identity and unvalidated status;
- existing dormant MSM-v1 sections;
- exact authority profile;
- exact additive artifacts and deterministic identities;
- exact retained sections;
- authorized lifecycle transitions;
- complete successor-manifest validity;
- exact companion and receipt custody;
- zero downstream authority.

## Deferred scope

Slice 42G does not modify the MSM-v1 schema, perform automatic migration, mutate the source manifest, delete alternatives, resolve unresolved states, create validation or delivery links, perform Echo validation, authorize delivery, enable bootstrap integration, close Slice 42, or supersede GP-014.
