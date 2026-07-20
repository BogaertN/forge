# AI.Web Slice 41A Selected Meaning Runtime Core Schema Specification

## Status

Schema-only increment.  No eligibility evaluator, selector, selected-meaning
constructor, MSM-v1 adapter, or bootstrap integration is installed.

## Accepted parent

- Repository: `/home/nic/forge`
- Branch: `main`
- HEAD: `fcc6b57e62e95cbfe2dbc80b88a212432c681907`
- Tree: `55dc8ebf863c2df547ae31b38e3445b25f6cc22a`
- Subject:
  `Slice 40H MSM gate integration disabled bootstrap and Slice 40 closeout`

## Package

`aiweb_language_core_bootstrap.selected_meaning_runtime`

## Purpose

Create immutable typed companion records that can later preserve all
candidate-specific grounds required for lawful selected-meaning review without
performing that review.

## Admitted schema types

1. `SelectionCandidateCustodyRecord`
2. `GateCustodyReferenceRecord`
3. `SelectionAuthorityRequirementRecord`
4. `AlternativeCandidateCustodyRecord`
5. `UnresolvedStateCustodyRecord`
6. `InheritedLimitationCustodyRecord`
7. `SelectionEligibilityStatusRecord`
8. `SelectedMeaningDecisionStatusRecord`
9. `SelectionTraceBoundaryRecord`
10. `SelectionReceiptBoundaryRecord`
11. `SelectedMeaningRuntimeSchemaRecord`

Schema-only enums:

1. `SelectionEligibilityCustodyState`
2. `SelectedMeaningDecisionCustodyState`

## Exact custody obligations

The schema can preserve exact references to:

- accepted candidate meaning identity, state, lineage, content, provenance,
  construction receipt, candidate set, candidate-set member, lifecycle, and
  manifest candidate custody;
- the Slice 40H MSM gate-custody companion;
- all four gate-family custody and result records;
- the exact Slice 40G composition result and dispositions;
- selection-authority requirements and later authority dependencies;
- every preserved alternative and non-selected candidate;
- unresolved, unknown, unsupported, conflicted, clarification-dependent, held,
  blocked-progression, and refusal-relevant conditions;
- inherited source, candidate, gate, effect, domain, evidence, memory, privacy,
  delivery, execution, correction, and supersession limitations;
- trace and receipt boundaries.

## Hard boundary

Slice 41A does not:

- calculate deterministic identities;
- validate records;
- serialize or deserialize records;
- authorize lifecycle transitions;
- evaluate selection eligibility;
- choose, rank, prefer, or discard candidates;
- resolve ambiguity;
- emit clarification;
- issue refusal;
- construct `SelectedGovernedMeaningRecord`;
- modify or migrate MSM-v1;
- enable bootstrap integration;
- create governed outward meaning;
- determine truth or proof;
- validate evidence;
- grant permission;
- authorize execution;
- create routes;
- invoke tools;
- perform actions;
- access or write memory;
- render or deliver output;
- load external resources;
- use an LLM, embedding, vector store, RAG path, similarity score, confidence
  score, or hidden classifier.

## MSM-v1 decision

Decision value:

`deferred_to_slice41e_exact_additive_adapter`

The accepted MSM-v1 schema remains unchanged in Slice 41A.

## Deferred work

All Slice 41B through 41F work remains deferred and separately testable.
