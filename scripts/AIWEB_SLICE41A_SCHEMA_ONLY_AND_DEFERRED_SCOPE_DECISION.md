# AI.Web Slice 41A Schema-Only and Deferred-Scope Decision

## Decision 1 — New additive runtime companion

Slice 41A creates
`aiweb_language_core_bootstrap.selected_meaning_runtime` as a new additive,
immutable, standard-library-only schema package.

The accepted MeaningStructureManifest v1 schema is not modified.  The dormant
`SelectedGovernedMeaningRecord` remains unpopulated.  The accepted Slice 16
selected-meaning boundary scaffold remains predecessor evidence only.

## Decision 2 — Custody state is not selection state

The Slice 41A eligibility and decision vocabularies contain only non-outcome
custody states:

Eligibility custody:

- `not_evaluated`
- `ready_for_later_evaluation`
- `evaluation_deferred`
- `evaluation_unavailable`

Decision custody:

- `not_decided`
- `ready_for_later_decision`
- `decision_deferred`
- `decision_unavailable`

No value means eligible, ineligible, accepted, rejected, selected, clarified,
ambiguous, unsupported, refused, held, blocked, or final.

## Decision 3 — Positive eligibility naming remains deferred

The exact positive eligibility outcome name belongs to Slice 41C after the
accepted eligibility evaluator exists.  Slice 41A does not invent an
`eligible`, `accepted`, `approved`, `selected`, or probability-based result.

The exact selected-meaning decision and construction record belongs to Slice
41D.  Slice 41A does not create it early.

## Decision 4 — Exact predecessor references remain opaque

Slice 41A records carry exact identifiers for accepted Slice 39 candidate
custody, Slice 40 gate results, Slice 40G composition, and Slice 40H MSM gate
custody.  The new package does not import or execute those predecessor
runtimes.  It cannot re-evaluate gates or modify their results.

## Decision 5 — Later increments remain separate

- Slice 41B: validation, identity, canonical serialization, versioning, and
  lifecycle.
- Slice 41C: deterministic selection-eligibility evaluation.
- Slice 41D: selected-meaning construction and alternative preservation.
- Slice 41E: exact additive MSM-v1 selected-meaning integration.
- Slice 41F: disabled bootstrap integration and Slice 41 closeout.

## Permanent boundary

Schema existence is not eligibility.  Eligibility is not selection.  Selection
is not truth, evidence, proof, permission, execution, outward meaning,
rendering, or delivery.
