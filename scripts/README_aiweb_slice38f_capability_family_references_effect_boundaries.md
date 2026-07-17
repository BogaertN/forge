# Slice 38F — Capability-Family References and Effect Boundaries

This slice adds a closed, immutable, non-operational capability-family reference registry and explicit effect-boundary identities on top of the accepted Slice 38E predicate frames.

Run the behavior test:

```text
python3 -B scripts/test_aiweb_slice38f_capability_family_references_effect_boundaries.py /home/nic/forge
```

Run the visible verifier after guarded application:

```text
python3 -B scripts/aiweb_slice38f_capability_family_references_effect_boundaries_verify.py /home/nic/forge --mode applied
```

The verifier runs tests sequentially and prints every child test directly. It does not use hidden workers or suppress child output.

This slice creates references only. It does not install capability availability, routes, invocation, arguments, permission, tools, execution, memory access, delivery, external-resource admission, implementation, semantic similarity, or LLM authority.
