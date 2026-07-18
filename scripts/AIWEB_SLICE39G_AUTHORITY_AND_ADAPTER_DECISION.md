# AI.Web Slice 39G Authority and Source-Grounded Adapter Decision

## Decision

The accepted Slice 35 `CandidateMeaningRecord` remains the canonical MSM-v1
candidate projection. It is not modified, superseded, or automatically
migrated.

Slice 39G introduces a versioned companion custody record and an exact adapter
into the existing `MeaningStructureManifestV1`.

Decision value:

`versioned_companion_required`

## Source-grounded reason

The exact committed Slice 35 record safely carries:

- lineage membership;
- source-expression reference;
- candidate communicative-act reference;
- candidate concept references;
- candidate semantic-relation references;
- candidate meaning modifiers;
- candidate ambiguity-reason custody;
- unresolved-referent custody;
- authority-sensitive implication custody;
- semantic preservation classes.

It does not contain exact fields for:

- source checksum and source-span custody;
- structural-rule, operator, phase-trail, scope, attachment, and reference
  ancestry;
- Slice 37 and Slice 38 registry snapshots and exact resource versions;
- Slice 39F constructor-record and construction-receipt custody;
- candidate limitation-reference families;
- candidate alternative-relationship families.

Placing those exact typed records into existing broad fields would misclassify
them and would make MSM-v1 appear to contain distinctions it does not define.
Changing the accepted Slice 35 dataclass would alter the accepted schema and its
canonical serialization. Automatic migration is not authorized.

Therefore Slice 39G preserves the existing MSM-v1 record as a bounded,
candidate-facing projection and places all exact Slice 36-39F custody in a
versioned immutable companion family referenced by MSM-v1 external-reference
and semantic-transition-trace records.

## Candidate-only manifest content

Slice 39G may populate only:

- the inward lineage root;
- MSM-v1 candidate meaning records;
- construction ancestry traces;
- external references to exact construction-trace custody;
- external references to exact provenance custody;
- external references to exact limitation custody;
- external references to exact candidate-alternative custody.

## Sections that must remain empty

- non-selection outcomes;
- selected governed meanings;
- governed result references;
- governed outward meanings;
- expression links;
- validation links;
- delivery or containment links.

## Permanent boundary

Manifest integration is custody, not gate evaluation. A construction status is
not a non-selection outcome. A limitation is not a clarification decision. A
candidate alternative relationship is not an ambiguity disposition. A
constructed candidate is not selected meaning.
