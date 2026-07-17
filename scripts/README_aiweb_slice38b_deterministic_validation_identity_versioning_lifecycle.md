# Slice 38B — Deterministic Validation, Identity, Versioning, and Lifecycle

This slice adds a disabled, pure, standard-library-only governance layer around
the accepted Slice 38A schema records.

It validates exact immutable records, provenance, stable lineage, compatible
version advancement, scope/non-scope preservation, explicit human-approved
lifecycle transitions, exact boolean review gates, duplicates, references,
current dependency versions, quarantine release requirements, rejection and
reopening custody, and ancestry. Malformed exact-record fields fail closed as
validation reports rather than escaping as Python exceptions.

Unknown or unsupported action-like material is never converted into a nearest
known action root, predicate, capability, route, tool, or inferred intent.

The slice adds no registry population, surface-word matching, predicate
selection, role assignment, frame completion, CandidateMeaning, selected
meaning, capability route, tool activation, action, evidence authority, memory
access, rendering, or delivery.

Run the behavior test:

```text
python3 -B scripts/test_aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle.py /home/nic/forge
```

Run the independent verifier in the repository state appropriate to the phase:

```text
python3 -B scripts/aiweb_slice38b_deterministic_validation_identity_versioning_lifecycle_verify.py /home/nic/forge --mode applied
```

The live-machine result remains subject to packet inspection before staging or
commit.
