# AI.Web Slice 41B

This slice adds a validation-only governed-lifecycle companion under:

`aiweb_language_core_bootstrap/selected_meaning_runtime/governed_lifecycle/`

Run the visible behavior test from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge \
/usr/bin/python3 -B \
scripts/test_aiweb_slice41b_deterministic_validation_identity_versioning_lifecycle.py
```

Run the independent verifier in applied or committed mode:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge \
/usr/bin/python3 -B \
scripts/aiweb_slice41b_deterministic_validation_identity_versioning_lifecycle_verify.py \
--mode applied /home/nic/forge
```

The slice contains no selector, eligibility evaluator, MSM mutation, bootstrap
enablement, route, tool, action, memory write, rendering, delivery, LLM,
embedding, vector, RAG, or semantic-similarity authority.
