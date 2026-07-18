# AI.Web Slice 39E Candidate Set and Alternative Preservation Runtime Specification

## Purpose

Provide an immutable, deterministic, fail-closed representation of candidate
sets assembled from exact accepted Slice 39D semantic-content results. This
representation is input custody for Slice 39F; it is not itself a completed
CandidateMeaning constructor result.

## Input contract

The public constructor accepts one exact tuple of zero or more
`CandidateSemanticContentAssemblyResult` records and the exact canonical Slice
39E profile. Every nonempty member must validate under Slice 39D, have status
`ASSEMBLED`, contain its exact assembly, and share one source event and source
checksum with every other member.

## Zero, one, and many

An empty input creates a real `ZERO_CANDIDATES` set with no fabricated source
identity. One input creates `ONE_CANDIDATE` while leaving selection false. Two
or more input occurrences create `MULTIPLE_CANDIDATES` while leaving ambiguity
and selection false.

## Ordering and exact duplicates

Ordering uses only exact deterministic Slice 39D canonical digest and result
identity for reproducibility. It is never rank, score, preference, tie-break, or
evaluation. Exact duplicate records remain visible through deterministic member
and duplicate-group custody and are never silently erased.

## Alternatives, ancestry, and candidate-specific custody

Every pair of unique records receives one exact-difference alternative
reference with `ambiguity_determined=False`. Shared ancestry preserves common
source and exact intersections without merging lineages. Limitations, missing
roles, conflicts, effect boundaries, and capability references remain attached
to the candidate that carried them.

## Failure and side-effect boundary

Wrong types, malformed Slice 39D records, mixed source custody, profile
substitution, identity/count/mapping changes, silent collapse, ranking,
confidence, preference, selection, tie-breaking, ambiguity resolution, gate
creation, or downstream authority mutation fail closed.

The runtime performs no filesystem or network access, external-resource loading,
model calls, embeddings, similarity, route creation, action, memory access,
rendering, or delivery.

## Exact continuation

Slice 39E does not end Slice 39. The required continuation is:

1. Slice 39F — deterministic CandidateMeaning constructor and construction receipt;
2. Slice 39G — candidate-side MeaningStructureManifestV1 integration;
3. Slice 39H — disabled bootstrap integration and Slice 39 closeout;
4. Slice 40 — verbal-cognition gates, only after 39H acceptance.
