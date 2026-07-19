# AI.Web Slice 40A Schema-Only and Deferred-Scope Decision

## Decision 1 — Versioned companion required

The accepted Slice 35 `MeaningStructureManifestV1` remains unchanged.
`NonSelectionOutcomeRecord` is a later semantic-custody projection and cannot
carry the complete family-specific gate identity, profile, candidate input,
requirement, reason-ground, trace, provenance, limitation, and version custody
required by Slice 40.

Slice 40A therefore creates a versioned immutable companion family. No MSM-v1
migration, subclassing, field reuse, automatic adaptation, or outcome
population is authorized.

## Decision 2 — Schema state is not a gate result

`GateEvaluationState` contains only non-outcome custody states. Slice 40A does
not represent a candidate as passed, failed, accepted, rejected, clarified,
ambiguous, unsupported, refusal-relevant, held, blocked, or selected.

## Decision 3 — Positive disposition name remains deferred

The later positive composition boundary means only that a candidate may be
supported for later selected-meaning review. The exact runtime disposition
name is intentionally not invented in 40A. It remains deferred to the
source-grounded Slice 40G composition decision.

## Permanent boundary

Gate schema is not gate evaluation. Gate review is not selected meaning.
Selected meaning belongs to Slice 41. No interpretation result creates truth,
evidence validity, permission, execution, memory, rendering, or delivery.
