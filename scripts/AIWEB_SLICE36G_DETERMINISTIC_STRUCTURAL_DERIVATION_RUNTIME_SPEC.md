# AI.Web Slice 36G — Deterministic Structural Derivation Runtime Specification

## 1. Status and scope

This specification governs the bounded Slice 36G runtime that combines accepted Slice 36A through Slice 36F records into immutable structural-analysis candidates and explicit lawful non-progress results.

Slice 36G does not construct CandidateMeaning, select intended meaning, resolve concepts or senses, define predicate identity, assign participant roles, determine truth, determine evidence validity, ask clarification questions, semantically reject input, infer permission, select capability, route tools, execute actions, read or write memory, render outward answers, or authorize delivery.

## 2. Required inputs

The derivation entrypoint requires the exact accepted predecessor result records:

1. `InputEventCaptureResult` from Slice 36A.
2. `SourceFieldProjectionResult` from Slice 36B.
3. `ResonantOperatorCandidateBindingResult` from Slice 36D.
4. `CandidateResonantPhaseTrailResult` from Slice 36E.
5. `ScopeAttachmentReferenceConstraintResult` from Slice 36F.

The five records must share exact source-event, source-field, binding-set, phase-trail-set and constraint-set ancestry. Mismatched ancestry fails closed.

## 3. Immutable output model

The runtime returns `DeterministicStructuralDerivationResult`. A successful bounded result contains `StructuralAnalysisCandidateSet`, which preserves zero, one or multiple `StructuralAnalysisCandidate` records.

Each candidate preserves:

- candidate structural identity;
- source-event and custody ancestry;
- source-field and projection ancestry;
- operator-binding and unbound-signal ancestry;
- phase-trail and application ancestry;
- scope, attachment and reference ancestry;
- an explicit candidate-only operator graph;
- bounded source coverage and unconsumed ranges;
- exact reconstruction proof against source custody;
- exact rule-application traces and rule versions;
- completeness, malformed, unsupported, ambiguity, drift and suspension state;
- every applicable non-progress reason.

All records are frozen dataclasses with stable content-derived identities. Predecessor records are embedded or referenced without mutation.

## 4. Closed derivation rules

The default registry contains exactly ten deterministic rule contracts:

1. preserve source custody ancestry;
2. preserve source-field ancestry and reconstruction proof;
3. preserve operator-binding ancestry;
4. preserve phase-trail ancestry;
5. preserve scope and attachment candidates;
6. preserve reference candidates;
7. construct one candidate per constrained predecessor trail;
8. compute bounded source coverage and unconsumed spans;
9. preserve explicit structural non-progress;
10. prohibit later semantic and operational authority.

Only the candidate-construction rule creates structural candidates. None creates selected meaning, asks a clarification question or performs semantic rejection.

## 5. Structural candidate plurality

One constrained predecessor trail produces at most one structural candidate. Multiple predecessor trails remain multiple structural candidates. Conflict, attachment and reference alternatives remain visible. No candidate is selected by source order, naturalness, convenience, confidence, capability availability or code order.

`selected_structural_candidate_id` must remain `None` in Slice 36G.

## 6. Operator graph

The candidate operator graph may contain only edges supported by exact predecessor evidence:

- possible parent-child edges explicitly preserved by Slice 36D;
- application-sequence edges explicitly preserved by Slice 36E;
- competition edges explicitly preserved by candidate conflict records.

The runtime must not invent arbitrary neighboring composition, implicit scope, semantic relation or predicate structure.

## 7. Source coverage and reconstruction

Every structural candidate carries source coverage proof containing:

- exact covered code-point and UTF-8 ranges;
- exact unconsumed code-point and UTF-8 ranges;
- exact source fragments for both;
- unresolved operator spans;
- reconstruction output and SHA-256 proof;
- custody-source hash comparison.

Unconsumed source is evidence, not an error to hide. The runtime never inserts, normalizes, silently drops or rewrites source text.

## 8. Lawful non-progress

The closed non-progress vocabulary is:

- `UNRESOLVED_REFERENCE`
- `UNRESOLVED_OPERATOR_BINDING`
- `UNSUPPORTED_SOURCE_STRUCTURE`
- `UNSUPPORTED_OPERATOR_SEQUENCE`
- `MALFORMED_SOURCE_STRUCTURE`
- `MULTIPLE_STRUCTURAL_CANDIDATES`
- `CONFLICTING_PHASE_TRAILS`
- `INCOMPLETE_INPUT`
- `INCOMPLETE_OPERATOR_TRAIL`
- `PROHIBITED_CONTEXT_DEPENDENCY`
- `DRIFT_CONTAINED`
- `RECURSION_SUSPENDED`
- `NO_SUPPORTED_DERIVATION`

Non-progress is a valid structural result. The runtime must never guess merely to avoid returning one of these outcomes.

## 9. Result cardinality

Lawful top-level statuses are:

- `ZERO_STRUCTURAL_CANDIDATES`
- `ONE_STRUCTURAL_CANDIDATE`
- `MULTIPLE_STRUCTURAL_CANDIDATES`
- `STRUCTURAL_DERIVATION_LIMIT_EXCEEDED`
- `STRUCTURAL_DERIVATION_FAILED`

Zero candidates with `NO_SUPPORTED_DERIVATION` is an accepted result, not a parser crash.

## 10. Resource limits

The runtime enforces explicit caller-visible limits and hard absolute ceilings for candidate count, trace count, graph nodes, graph edges and source ranges. Limit excess returns a typed non-authoritative failure result. It never truncates silently.

## 11. Side-effect and dependency boundary

The runtime is deterministic, standard-library only and offline. It performs no filesystem, repository-history, environment, subprocess, network, memory, web, embedding, similarity or language-model access. It does not import or call frozen legacy RMC.

## 12. Later authority boundary

Structural candidate is not CandidateMeaning. Slice 39 owns candidate-meaning construction. Slice 40 owns gate evaluation, ambiguity disposition, clarification-required status, rejection, unsupported-language disposition, blocked progression and refusal-relevant interpretation.
