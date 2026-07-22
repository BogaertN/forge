# AI.Web Slice 43C

This increment adds exact authorized-meaning and proposed-expression admission
to the accepted RMC Echo boundary. It admits only the exact accepted Slice 42
ancestry and rejects raw text, orphan expressions, fabricated or recomputed
identities, unsupported versions, missing links, delivered candidates, and
unauthorized candidates.

Admission is custody for later Slice 43D comparison. It is not comparison,
drift classification, Echo disposition, MSM integration, delivery, or action
authority.

## Runtime package

`aiweb_language_core_bootstrap.rmc_echo_runtime.authorized_source_admission`

## Visible behavior test

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/test_aiweb_slice43c_authorized_meaning_proposed_expression_admission.py \
  /home/nic/forge
```

## Independent verifier

Applied mode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  scripts/aiweb_slice43c_authorized_meaning_proposed_expression_admission_verify.py \
  /home/nic/forge --mode applied
```

Committed mode uses `--mode committed`. The verifier prints the current behavior
test and the inherited Slice 43B verifier directly. It uses no hidden workers or
output suppression.
