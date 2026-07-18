# AI.Web Slice 39D — Candidate Semantic Content Assembly Runtime Specification

## Accepted predecessor

- Repository: `/home/nic/forge`
- Branch: `main`
- Parent HEAD: `cc69a1fb092a9ed8d2d398a9ec6ae19643337a45`
- Parent tree: `261e29410bc3bad50d6c0aecf3da2f9b5d9886be`
- Parent subject: `Slice 39C complete provenance predecessor custody`

## Purpose

Slice 39D deterministically assembles one candidate-only semantic-content record
from exact Slice 39C custody and accepted Slice 36–38 candidate records. It
defines what a possible meaning may contain. It does not create the final
in-memory CandidateMeaning state and does not determine which meaning is correct
or permitted.

## Lawful candidate content

The assembly may preserve possible communicative purpose and force,
requested-act descriptions, concept and sense candidates, semantic-relation
references, action-root and predicate candidates, frame and role-layout
candidates, referent candidates, source and comparison-target references,
conditions, negation, qualification, temporal and status distinctions, scope,
attachments, limitations, missing and conflicting information,
authority-sensitive implications, effect boundaries, and capability references.

## Binding boundaries

- Every content reference must be supported by exact Slice 39C lineage and admitted predecessor records.
- Semantic relations are candidate relation-type references only.
- Role layouts remain possible role layouts, not participant assignments.
- Referents remain candidates, not resolved referents.
- Missing information is recorded without emitting clarification.
- Requested acts remain descriptions without permission, routing, invocation, or execution.
- Candidate alternatives remain zero, one, or many without ranking or selection.
- The runtime is deterministic, offline, and non-LLM.

## Exact deferred authority

- Slice 39E preserves candidate sets and alternatives.
- Slice 39F constructs actual CandidateMeaning states and deterministic construction receipts.
- Slice 39G integrates those constructed candidates into candidate-side MSM-v1 custody.
- Slice 39H connects the completed constructor to the disabled bootstrap and closes Slice 39.
- Slice 40 evaluates verbal-cognition gates only after 39H acceptance.

Slice 39D does not implement ranking, collapse, runtime CandidateMeaning state
construction, MSM integration, bootstrap integration, Slice 39 closeout, gate
evaluation, clarification, refusal, selected meaning, truth, evidence,
permission, capability availability, routes, tools, actions, memory, rendering,
or delivery.
