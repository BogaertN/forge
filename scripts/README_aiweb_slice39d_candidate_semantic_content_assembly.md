# Slice 39D Candidate Semantic Content Assembly

This increment adds the isolated package:

`aiweb_language_core_bootstrap.candidate_meaning_construction.candidate_semantic_content`

The public entry point is:

`assemble_candidate_semantic_content(...)`

It requires exact accepted Slice 39C predecessor custody plus the exact supporting Slice 36, 37, and 38 result records. It returns a typed assembled, no-candidate, or rejected result. All failures are preserved as deterministic issues; no exception path is used to create authority.

The package is intentionally candidate-only. A role layout is not a participant assignment. A relation reference is not a relation fact. Missing information is not a clarification decision. A requested act is not permission or execution.

Run the visible behavior test with:

```text
python3 -B scripts/test_aiweb_slice39d_candidate_semantic_content_assembly.py /home/nic/forge
```

Run the visible independent verifier with:

```text
python3 -B scripts/aiweb_slice39d_candidate_semantic_content_assembly_verify.py /home/nic/forge --mode applied
```
