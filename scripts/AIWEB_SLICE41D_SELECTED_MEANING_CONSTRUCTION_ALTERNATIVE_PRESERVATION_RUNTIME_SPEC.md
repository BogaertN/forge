# AI.Web Slice 41D Selected Meaning Construction and Alternative Preservation Runtime Specification

## Purpose

Construct a deterministic selected-meaning package from one exact successful Slice 41C eligibility result while preserving all candidate history and without modifying MSM-v1.

## Runtime input

`SelectedMeaningConstructionInput` contains:

1. the exact validated Slice 41C evaluation input;
2. the exact validated successful Slice 41C result;
3. the one approved Slice 41D authority profile;
4. explicit selection-reason, ambiguity-ancestry, clarification-ancestry, trace, provenance, and version references;
5. fixed-false declarations for every prohibited shortcut and downstream authority.

## Runtime output

`SelectedMeaningConstructionPackage` contains:

- the exact source `CandidateMeaningRecord`;
- the exact `CandidateMeaningManifestCompanionV1`;
- a deterministic `SelectedMeaningDecisionRecord`;
- a dormant `SelectedGovernedMeaningRecord`;
- a deterministic `SelectedMeaningContentProof`;
- one `PreservedAlternativeCandidateRecord` for every exact non-selected candidate reference;
- separate unresolved, ambiguity, clarification, limitation, blocked-consequence, refusal-relevant, and authority-sensitive custody;
- deterministic selection trace and receipt records;
- fixed authority-boundary flags.

## Exact semantic-copy law

The following selected fields must equal the selected candidate fields exactly:

- `communicative_act`;
- `concept_refs`;
- `relation_refs`;
- `meaning_modifiers`;
- `preservation_classes`;
- `lineage_id`;
- `selected_candidate_ref`;
- `authority_sensitive_distinctions` from candidate authority-sensitive implications.

The content proof calculates canonical SHA-256 digests over the meaning-bearing fields and records all added or removed elements. A valid package requires equal digests, all exact flags true, all added/removed sets empty, and enrichment/deletion flags false.

## Alternative law

The complete ordered non-selected candidate set is derived from the exact union of:

- Slice 41C preserved alternative refs;
- Slice 41A alternative-custody preserved refs;
- Slice 41A non-selected candidate refs;
- Slice 41A unresolved candidate refs.

The selected candidate identities are excluded. Every remaining exact reference must have one immutable preservation record. Each record must remain unselected, undeleted, unranked, unscored, and preserved by exact reference.

## Determinism

All Slice 41D identities use canonical UTF-8 JSON and SHA-256. Timestamps, randomness, process identity, filesystem state, environment state, hash-table order, network data, models, embeddings, vectors, RAG, and semantic similarity do not participate.

## No MSM mutation

The dormant `SelectedGovernedMeaningRecord` is constructed in memory only. The supplied manifest is neither accepted as a mutable input nor returned as a modified manifest. Slice 41E is required for immutable successor integration.
