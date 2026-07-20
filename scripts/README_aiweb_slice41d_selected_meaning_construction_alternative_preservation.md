# Slice 41D — Selected Meaning Construction and Alternative Preservation

This additive package implements deterministic selected-meaning construction after Slice 41C.

## Package

`aiweb_language_core_bootstrap.selected_meaning_runtime.selected_meaning_construction`

## Main API

```python
construct_selected_meaning_package(construction_input)
```

The constructor requires an exact successful Slice 41C eligibility result. It returns an immutable selected-meaning package and never modifies MSM-v1.

## Verification

```bash
/usr/bin/python3 -B scripts/test_aiweb_slice41d_selected_meaning_construction_alternative_preservation.py /home/nic/forge
/usr/bin/python3 -B scripts/aiweb_slice41d_selected_meaning_construction_alternative_preservation_verify.py --mode applied /home/nic/forge
```

Use `--mode committed` only after the exact Slice 41D commit exists.

## Boundary

Selected meaning is semantic custody only. It is not truth, evidence, permission, execution, outward answer, rendering, or delivery. Alternatives remain preserved.
