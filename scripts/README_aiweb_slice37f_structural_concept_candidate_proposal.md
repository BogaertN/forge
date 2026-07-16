# AI.Web Slice 37F — Structural-to-Concept Candidate Proposal

Slice 37F is the first bounded bridge from the accepted Slice 36 structural result to the controlled Slice 37 registry.

## Exact input contract

The public proposal operation receives three matching immutable predecessors:

1. the Slice 36A `InputEventCaptureResult`, which owns the exact received source text and root source span;
2. the Slice 36B `SourceFieldProjectionResult`, which owns exact code-point, byte, observation and source-span coordinates;
3. the Slice 36G `DeterministicStructuralDerivationResult`, which owns structural candidates, operator graphs, phase trails, scope, attachment, reference and lawful non-progress ancestry.

Slice 36G alone does not contain the complete exact source text. Accepting the three linked records is therefore necessary to verify the lineage without reconstructing, guessing or consulting an outside source.

## Deterministic path

The operation performs only this sequence:

`36G structural result -> verified 36A/36B source ancestry -> explicit Slice 37F profile -> exact case-sensitive ASCII-boundary occurrence matching -> exact Slice 37D lookup -> zero/one/multiple concept and sense candidate proposals -> explicit unknown or unsupported result`

Every registry lookup uses the exact lexical form, language tag, namespace ID, namespace scope and domain scope admitted by the explicit profile. There is no normalization, case folding, spelling correction, stemming, synonym expansion, nearest match, frequency ranking, semantic similarity, model inference or dictionary fallback.

## Preserved records

Candidate proposals preserve:

- structural-result and structural-set identity;
- source-event, source-hash, input-event and root-span ancestry;
- exact code-point, UTF-8 byte and source-span coordinates;
- every structural-candidate identity;
- operator graph, binding, definition and version ancestry;
- phase trail, scope, attachment and reference ancestry;
- exact lexical-reference identity, version, lifecycle and provenance;
- exact lookup request and result identity;
- mapping identity and version;
- concept identity, key, version, lifecycle and provenance;
- sense identity, key, version, lifecycle and provenance;
- exact registry snapshot identity and all three registry digests;
- unresolved concept, sense, operator, attachment and reference alternatives;
- structural non-progress reasons;
- explicit unknown and unsupported states.

## Hard boundary

Slice 37F creates no `CandidateMeaning`, selected meaning, selected sense, predicate identity, participant roles, truth, evidence-validity decision, clarification, permission, capability route, tool invocation, action, memory access, rendering or delivery.

Semantic classes and relation types remain available only through the immutable registry snapshot. Slice 37F creates zero semantic relation instances and asserts zero relation facts.

## Public surface

```python
from aiweb_language_core_bootstrap.structural_concept_candidate_proposal import (
    build_default_structural_concept_proposal_profile,
    propose_structural_concept_candidates,
)
```

The package is additive and does not modify any accepted Slice 36 or Slice 37A–37E source.
