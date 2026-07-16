# Slice 37C — Minimal Built-In Concept Registry

This increment adds one isolated subpackage:

`aiweb_language_core_bootstrap.controlled_concept_sense_registry.built_in_registry`

It leaves the parent package unchanged and does not auto-import or activate the registry.

## Exact population

- one internal namespace;
- four current admitted concepts;
- five provenance records;
- fifteen immutable resource versions;
- ten authority records;
- ten lifecycle transitions;
- one closed read-only manifest.

## Exact lookup boundary

Only exact stable-ID and exact internal namespace/key lookup are available. Unknown IDs or keys raise `KeyError`; wrong argument types fail deterministically. No text is normalized or interpreted.

## Verification

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B scripts/test_aiweb_slice37c_minimal_built_in_concept_registry.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B scripts/aiweb_slice37c_minimal_built_in_concept_registry_verify.py /home/nic/forge --mode precommit
```

The verifier protects 189 predecessor files and runs 22 inherited tests on the complete live repository.
