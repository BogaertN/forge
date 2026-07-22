# AI.Web Slice 43E — Drift Finding, Materiality and Classification

This additive package classifies deterministic drift and materiality from the
exact validated Slice 43D findings.

## Runtime package

`aiweb_language_core_bootstrap.rmc_echo_runtime.drift_materiality_classification`

## Main entry points

- `build_classification_request(comparison_result)`
- `classify_drift_and_materiality(request, comparison_result)`
- `validate_classification_inputs(...)`
- `validate_finding(...)`
- `validate_package(...)`
- `validate_result(...)`

## Expected accepted fixture

The exact accepted Slice 43D fixture contains 13 preserved findings. Slice 43E
therefore creates 13 explicit no-drift records, zero drift-kind findings and
13 `not_applicable` materiality findings.

## Adversarial coverage

The behavior test constructs valid Slice 43D variants and proves all 17
admitted drift kinds, material, non-material, unsupported, conflicted and
indeterminate handling, multiple drift kinds, ancestry mismatch, exact custody,
immutable identities and all permanent authority-zero boundaries.

## Prohibited

No Echo disposition, rejection, containment, repair, rewriting, MSM mutation,
delivery, tool, action, memory write, model authority or GP-014 supersession.
