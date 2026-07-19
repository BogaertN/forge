# Slice 40G — Gate Composition and Non-Selection Disposition Runtime

Slice 40G composes the four accepted verbal-cognition gate-family results for
one traceable candidate branch. The runtime is deterministic, immutable,
offline, non-LLM, candidate-specific, and non-selection only.

## Runtime package

`aiweb_language_core_bootstrap.verbal_cognition_gate_runtime.gate_composition`

The package exports immutable schema records, canonical serialization,
deterministic SHA-256 identities, strict fail-closed validation, and
`evaluate_gate_composition`.

## Seven dispositions

- material ambiguity preserved
- clarification relevant
- unsupported
- refusal relevant
- held
- blocked progression
- candidate supported for later selection review

Several dispositions may coexist where exact authority supports them. The
runtime never flattens all gate results to a generic pass/fail label.

## Permanent boundaries

- gate-supported candidate is not selected meaning;
- multiple candidates are not automatic ambiguity;
- missing structure is not automatic clarification;
- unsupported is not automatic refusal;
- refusal relevance is not outward refusal;
- understanding is not action;
- family-result composition creates no downstream authority.

## Verification

Run:

```bash
python3 -B scripts/test_aiweb_slice40g_gate_composition_non_selection_disposition_runtime.py /home/nic/forge
python3 -B scripts/aiweb_slice40g_gate_composition_non_selection_disposition_runtime_verify.py /home/nic/forge --mode applied
```

The verifier runs the Slice 40G behavior test and every inherited visible test
from Slice 40F backward through the accepted language-core chain.
