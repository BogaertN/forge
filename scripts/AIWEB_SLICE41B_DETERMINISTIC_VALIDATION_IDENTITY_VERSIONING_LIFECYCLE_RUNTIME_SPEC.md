# Slice 41B Deterministic Validation, Identity, Versioning, and Lifecycle Runtime Specification

## Purpose

Add deterministic validation custody around the immutable Slice 41A selected
meaning runtime schema without evaluating selection eligibility or creating
selected meaning.

## Implemented capabilities

- Exact canonical field order for every supported record type.
- UTF-8 canonical JSON serialization with deterministic tuple, enum, nested
  dataclass, and string-key mapping normalization.
- SHA-256 record identities that exclude only the record's own identity field.
- Exact Slice 41A schema and specification version custody.
- Exact accepted-parent and predecessor-reference custody.
- Duplicate deterministic identity rejection.
- Identity collision rejection when one identity is reused for different
  canonical content or record types.
- Unknown-version and malformed-record rejection.
- Cross-record consistency validation across candidate, gate, authority,
  alternatives, unresolved states, limitations, eligibility custody, decision
  custody, trace boundary, receipt boundary, and aggregate runtime record.
- Immutable lifecycle records and explicit transition law.
- Deterministic governance bundle identity and digest.

## Lifecycle states

1. `schema_declared`
2. `version_bound`
3. `predecessors_bound`
4. `cross_record_validated`
5. `record_validated`
6. `record_sealed`
7. `validation_incomplete`
8. `unknown_version_blocked`
9. `malformed_record_blocked`
10. `predecessor_invalid_blocked`
11. `identity_collision_blocked`

Every progression is represented by a new frozen record. No automatic
progression is permitted.

## Hard boundary

- valid record != valid candidate meaning
- valid record != successful gate result
- valid record != selection eligibility
- selection lifecycle != selected meaning
- validation != truth, evidence, proof, permission, execution, route, tool,
  action, memory, rendering, or delivery authority
