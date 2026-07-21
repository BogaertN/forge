# AI.Web Slice 42B

This increment adds deterministic validation, canonical serialization,
SHA-256 identity, exact version and predecessor custody, immutable lifecycle
successors, a closed transition law, and fail-closed rejection to the Slice 42A
outward-expression schema.

It is validation-only. A valid record is not expression authority.

## Runtime package

`aiweb_language_core_bootstrap.outward_expression_runtime.governed_lifecycle`

## Visible test

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/test_aiweb_slice42b_deterministic_validation_identity_versioning_lifecycle.py \
  /home/nic/forge
```

## Independent verifier

Applied mode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/aiweb_slice42b_deterministic_validation_identity_versioning_lifecycle_verify.py \
  /home/nic/forge --mode applied
```

Committed mode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/aiweb_slice42b_deterministic_validation_identity_versioning_lifecycle_verify.py \
  /home/nic/forge --mode committed
```

The verifier runs the current Slice 42B test and the complete accepted Slice
42A verifier visibly from an exact temporary checkout. It does not use hidden
workers or suppress test output.
