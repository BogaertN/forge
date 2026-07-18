# AI.Web Slice 39E Candidate Set and Alternative Preservation Runtime Specification

## Purpose

Provide an immutable, deterministic, fail-closed representation of candidate sets assembled from exact accepted Slice 39D candidate semantic-content results.

## Input contract

The public constructor accepts one exact tuple of zero or more `CandidateSemanticContentAssemblyResult` records and the exact canonical Slice 39E profile. Every nonempty member must validate under Slice 39D, have status `ASSEMBLED`, contain its exact assembly, and share one source event and source checksum with every other member.

## Zero, one, and many

An empty input creates a real `ZERO_CANDIDATES` set with no fabricated source identity. One input creates a `ONE_CANDIDATE` set while leaving selection false. Two or more input occurrences create `MULTIPLE_CANDIDATES` while leaving ambiguity and selection false.

## Ordering

Candidate records are ordered only by their exact deterministic Slice 39D canonical digest and result identity. This ordering exists for reproducibility and identity generation. It is never a rank, score, preference, tie-break, or evaluation.

## Exact duplicates

An exact duplicate is an input occurrence with the same valid Slice 39D result identity as another occurrence. Unique candidate records are stored once by exact identity, while every input occurrence receives a deterministic member record and occurrence index. Duplicate groups state the primary occurrence, every duplicate member, total occurrence count, and `silently_collapsed=False`.

## Material alternative references

Each pair of unique candidate records receives one alternative reference. The reference lists exact fields whose governed payload or provenance differs. `materially_distinct_by_exact_content=True` means exact deterministic candidate identity differs; `ambiguity_determined=False` remains mandatory.

## Shared ancestry

One shared-ancestry record preserves the common source event and checksum, all distinct lineage identities, and exact intersections of source spans, structural ancestry, operator definitions, concept and sense candidates, action/predicate candidates, role-layout candidates, and predecessor receipts. `lineages_merged=False` is permanent.

## Candidate-specific custody

Every member separately retains limitations, missing-role references, conflicting-role references, effect-boundary references, and capability-reference candidates from its own Slice 39D content. Set construction may not move, union, erase, or substitute those records across candidates.

## Failure behavior

Wrong types, malformed Slice 39D records, non-assembled results, mixed source events, mixed source checksums, profile substitutions, identity mismatches, count mismatches, mapping changes, silent duplicate collapse, ranking, confidence, preference, selection, tie-breaking, ambiguity resolution, ambiguous-state creation, or downstream authority mutations fail closed into a typed rejected result or fail independent validation.

## Side-effect boundary

The runtime performs no filesystem reads or writes, network access, external-resource loading, language-model calls, embeddings, semantic similarity, route creation, action, memory access, rendering, or delivery.
