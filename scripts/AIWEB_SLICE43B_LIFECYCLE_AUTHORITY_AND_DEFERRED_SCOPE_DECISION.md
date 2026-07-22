# AI.Web Slice 43B Lifecycle Authority and Deferred-Scope Decision

## Decision

Slice 43B may validate immutable Slice 43A record structure, calculate
deterministic SHA-256 identities, bind exact supported versions and predecessor
references, produce immutable validation-custody successors, evaluate explicit
lifecycle transitions, and reject malformed, duplicate, colliding,
unknown-version, or cross-record-inconsistent records.

## Structural validity is not Echo authority

The following implications are permanently rejected:

`structurally valid record → source admitted`

`structurally valid record → meaning preserved`

`structurally valid record → Echo disposition decided`

`record_sealed → delivery authorized`

Validation answers only whether supplied immutable records satisfy the admitted
Slice 43A and Slice 43B structural contracts.

## Lifecycle naming decision

Slice 43B uses the validation-only lifecycle:

- `schema_declared`
- `version_bound`
- `predecessors_bound`
- `cross_record_validated`
- `record_validated`
- `record_sealed`
- `validation_incomplete`
- `unknown_version_blocked`
- `malformed_record_blocked`
- `predecessor_invalid_blocked`
- `duplicate_record_blocked`
- `identity_collision_blocked`

These are validation-custody stages. They are not 43C admission outcomes, 43D
comparison results, 43E drift classifications, or 43F Echo dispositions.

## Dormant source ruling

- Slice 19 RMC Echo scaffold: protected historical boundary evidence only.
- Legacy `rmc_engine_v1` Echo validators and approval path: protected
  historical source only.
- Import, call, wrap, activate, copy, or treat those files as current runtime
  authority: prohibited.
- The accepted Slice 43A package remains byte-for-byte protected.
- The accepted Slice 42 records are referenced only as opaque predecessor
  custody strings. Their live admission belongs to Slice 43C.

## Deferred scope

Slice 43B does not implement admission, meaning comparison, drift
classification, materiality, disposition, rejection, containment, expression
repair, MSM-v1 integration, bootstrap integration, delivery, external-resource
use, model use, routes, tools, actions, memory writes, or GP-014 supersession.

## Implementation form

The implementation is one additive seven-module `governed_lifecycle` companion
package plus visible proof files. No accepted predecessor file is modified.
