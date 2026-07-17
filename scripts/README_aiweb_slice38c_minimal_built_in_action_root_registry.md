# Slice 38C — Minimal Built-In Action-Root Registry

This slice adds a sealed, standard-library-only, read-only registry containing five action roots and five matching predicate identities.

## Files

The runtime package is:

`aiweb_language_core_bootstrap/predicate_role_frame_registry/built_in_action_root_registry/`

The visible behavior test is:

`scripts/test_aiweb_slice38c_minimal_built_in_action_root_registry.py`

The visible independent verifier is:

`scripts/aiweb_slice38c_minimal_built_in_action_root_registry_verify.py`

## Visible test rule

The verifier prints every command before execution, streams each test directly to the terminal, and prints each return code immediately afterward. It does not run inherited tests in hidden threads or suppress their output.

## Non-authority rule

Exact internal registry inspection is not surface-language interpretation. Registry membership is not occurrence selection. Action-root identity is not permission, capability, route, invocation, execution, proof, memory, rendering, or delivery.
