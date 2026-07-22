# Slice 43D — Meaning-Preservation Comparison

This additive package creates deterministic findings for the 13 required
meaning-preservation dimensions.

The runtime accepts only the exact accepted Slice 43C admission result together
with its exact accepted Slice 42 ancestry. It does not inspect arbitrary raw
text.

## Public entry points

- `build_comparison_request(...)`
- `compare_meaning_preservation(...)`
- `make_dimension_snapshot(...)`
- `build_dimension_finding(...)`
- `validate_comparison_inputs(...)`
- `validate_snapshot(...)`
- `validate_finding(...)`
- `validate_package(...)`
- `validate_result(...)`

## Findings, not disposition

A finding outcome may be preserved, changed, missing, unsupported, conflicted,
or indeterminate. Slice 43D does not combine those findings into PASS, REJECTED,
or CONTAINED.

## Live verification

Run the delivered behavior test and verifier on `/home/nic/forge`, then run the
result collector. Do not stage or commit until the applied-result packet has
been reviewed and accepted.
