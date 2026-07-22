# AI.Web Slice 43B

This increment adds deterministic validation, canonical serialization,
SHA-256 identities, exact version and predecessor custody, immutable lifecycle
successors, a closed transition law, and fail-closed rejection to the accepted
Slice 43A RMC Echo schema.

It is validation-only. A valid record is not source admission, meaning
preservation, an Echo decision, or delivery authority.

## Runtime package

`aiweb_language_core_bootstrap.rmc_echo_runtime.governed_lifecycle`

## Visible behavior test

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/test_aiweb_slice43b_deterministic_validation_identity_versioning_lifecycle.py \
  /home/nic/forge
```

## Independent verifier

Applied mode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/aiweb_slice43b_deterministic_validation_identity_versioning_lifecycle_verify.py \
  /home/nic/forge --mode applied
```

Committed mode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/aiweb_slice43b_deterministic_validation_identity_versioning_lifecycle_verify.py \
  /home/nic/forge --mode committed
```

The verifier runs the current Slice 43B behavior test and the complete accepted
Slice 43A verifier visibly from an exact temporary checkout. It does not use
hidden workers or suppress test output.
