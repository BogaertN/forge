# AI.Web Slice 41C — Selection Eligibility Evaluation Runtime Specification

## Scope

Slice 41C adds a deterministic, candidate-specific evaluator that decides only whether a preserved candidate may proceed to the later selected-meaning construction increment.

The evaluator accepts only exact validated records from the accepted language-core line:

1. one real MSM-v1 `CandidateMeaningRecord`;
2. its exact Slice 39G candidate-manifest companion;
3. one sealed, validated, unevaluated Slice 41B governance bundle;
4. the exact Slice 40H MSM gate-custody companion;
5. all four preserved gate-family custody records and results;
6. the exact Slice 40G composition result and explicit candidate-specific dispositions;
7. the approved strict selection-eligibility authority profile;
8. explicit unresolved, alternative-candidate, limitation, trace, provenance and version custody.

## Deterministic outcomes

The evaluator emits exactly one of:

- `eligible_for_selected_meaning_construction`;
- `held_pending_authority`;
- `materially_unresolved`;
- `clarification_dependent`;
- `unsupported`;
- `conflicted`;
- `indeterminate`;
- `not_eligible`.

Adverse states take precedence over positive support. Eligibility requires explicit candidate-specific positive support, exact approved authority, complete predecessor custody, and the absence of any material adverse condition.

## Permanent boundaries

- eligibility is not selection;
- eligibility is not selected meaning;
- eligibility is not MSM-v1 mutation;
- a valid record is not a valid candidate meaning;
- a valid record is not a successful gate result;
- a valid record is not selection eligibility;
- a selection lifecycle is not selected meaning;
- one candidate, the first candidate, the safest candidate, or the only remaining candidate is never automatic eligibility;
- understood meaning is never permission;
- refusal relevance, blocked progression, unresolved custody and alternatives remain visible;
- no confidence scoring, probability ranking, semantic similarity, nearest-known substitution, language model or hidden classifier participates;
- truth, evidence, proof, permission, execution, routes, tools, actions, memory, rendering and delivery remain outside this increment.

## Deferred work

Slice 41D owns selected-meaning construction and alternative preservation. Slice 41E owns later MSM selected-meaning integration. Slice 41C performs neither.
