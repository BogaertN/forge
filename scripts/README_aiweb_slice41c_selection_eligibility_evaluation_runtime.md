# Slice 41C Selection Eligibility Evaluation Runtime

This additive package implements deterministic candidate-specific selection-eligibility evaluation.

## Runtime package

`aiweb_language_core_bootstrap.selected_meaning_runtime.eligibility_evaluation`

## Verification

Run the visible behavior test:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge /usr/bin/python3 -B /home/nic/forge/scripts/test_aiweb_slice41c_selection_eligibility_evaluation_runtime.py /home/nic/forge
```

Run source verification:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge /usr/bin/python3 -B /home/nic/forge/scripts/aiweb_slice41c_selection_eligibility_evaluation_runtime_verify.py --mode source /home/nic/forge
```

Applied and committed modes additionally run the current test plus all 54 inherited accepted language-core tests visibly.

## Authority boundary

A positive eligibility result authorizes only later Slice 41D construction review. It is not selected meaning, MSM mutation, permission, execution, evidence, truth, memory, rendering or delivery authority.
