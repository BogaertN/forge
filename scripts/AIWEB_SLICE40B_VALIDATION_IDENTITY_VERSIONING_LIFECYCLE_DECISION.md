# AI.Web Slice 40B Validation, Identity, Versioning, and Lifecycle Decision

## Decision 1 — Preserve Slice 40A unchanged

The four accepted Slice 40A parent modules remain byte-for-byte protected.
Slice 40B adds a governed-lifecycle companion below the parent package rather
than adding validation or identity side effects to the schema-only modules.

## Decision 2 — Canonical identity is content-bound

Every supported record has a fixed versioned field order. Canonical JSON uses
UTF-8, stable separators, explicit tuple ordering, enum values, and SHA-256.
Identifiers exclude only their own identifier field. Bundle digests exclude
only the bundle identifier and digest fields.

Timestamps, randomness, process identity, filesystem state, environment state,
and hash-table order are expressly prohibited as identity inputs.

## Decision 3 — Unknown versions fail closed

The first admitted gate and gate-profile version is `v1.0.0`. A syntactically
valid but unadmitted version is an `unknown_version` error. Malformed versions,
schema mismatches, and cross-record version mismatches are separate explicit
errors. No fallback, nearest-known substitution, or silent migration occurs.

## Decision 4 — Provenance is exact custody, not truth

Validation requires the exact candidate input reference, source SHA-256,
profile reference, governing document references, authority-version pairs,
schema-version pairs, and predecessor schema custody. Provenance validation
does not establish truth, evidence validity, resource admission, or permission.

## Decision 5 — Lifecycle creates immutable successors only

The normal validation chain is:

`schema_declared`
→ `profile_version_bound`
→ `candidate_reference_bound`
→ `provenance_validated`
→ `record_validated`
→ `record_sealed`

Fail-closed successor states preserve incomplete validation, unknown versions,
malformed records, and invalid provenance. A corrected input begins a new
immutable chain through an explicit `resume_validation` transition; no prior
record is rewritten.

## Decision 6 — Validation is not gate evaluation

No Slice 40B function evaluates expectancy, congruity, connectedness, or
recoverable purpose. No lifecycle transition creates a pass, failure,
ambiguity, clarification, unsupported, refusal-relevant, held, blocked,
positive-selection-review, or selected-meaning disposition.

The binding boundary is:

- valid gate record != valid candidate meaning;
- valid gate record != successful gate result;
- lifecycle progression != selected-meaning progression;
- selected meaning remains Slice 41 authority.
