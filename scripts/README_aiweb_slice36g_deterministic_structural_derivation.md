# Slice 36G — Deterministic Structural Derivation

## Purpose

This package converts the accepted Slice 36A–36F record chain into immutable structural-analysis candidates and explicit lawful non-progress results. It remains below RMC meaning construction.

## Public entrypoint

```python
from aiweb_language_core_bootstrap.deterministic_structural_derivation import (
    derive_deterministic_structural_analysis,
)

result = derive_deterministic_structural_analysis(
    custody_result,
    projection_result,
    binding_result,
    phase_trail_result,
    constraint_result,
)
```

The caller must supply exact accepted predecessor results. The function performs no hidden retrieval.

## Reading the result

- `result.status` gives zero, one, multiple, limit-exceeded or failed cardinality.
- `result.structural_set` contains the candidate set when construction succeeds.
- `structural_set.candidates` preserves every structural candidate.
- `structural_set.aggregate_non_progress_reasons` preserves all lawful blocked conditions.
- `structural_set.non_progress_result` makes non-progress explicit and valid.
- `selected_structural_candidate_id` remains `None`.

Each candidate contains its exact predecessor phase trail, scope occurrences, attachment alternatives, reference alternatives, operator graph, source-coverage proof, unconsumed spans and rule traces.

## Zero-result example

Source with no supported operator derivation produces `ZERO_STRUCTURAL_CANDIDATES` and `NO_SUPPORTED_DERIVATION`. It does not trigger guessing or automatic clarification.

## Safety boundary

This package creates no CandidateMeaning, selected meaning, concept, sense, predicate, participant role, truth, evidence validity, clarification question, semantic rejection, permission, capability, route, tool call, action, memory operation, outward answer or delivery authorization.

## Verification

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPYCACHEPREFIX=/tmp/aiweb_slice36g_test_cache \
/usr/bin/python3 -B \
scripts/test_aiweb_slice36g_deterministic_structural_derivation.py
```

The independent verifier also runs every inherited accepted regression command before commit acceptance.
