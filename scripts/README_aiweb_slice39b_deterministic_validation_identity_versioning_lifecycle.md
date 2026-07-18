# AI.Web Slice 39B

This increment adds deterministic validation, canonical identity and digest
generation, exact version custody, cross-record integrity, and a closed
candidate-construction lifecycle around the committed Slice 39A schema.

## New package

```text
aiweb_language_core_bootstrap/candidate_meaning_construction/governed_lifecycle/
```

The parent Slice 39A package remains unchanged and does not auto-import Slice
39B.

## Run the behavior test

```bash
/home/nic/forge/.venv/bin/python3 -B   /home/nic/forge/scripts/test_aiweb_slice39b_deterministic_validation_identity_versioning_lifecycle.py   /home/nic/forge
```

## Run the verifier after application

```bash
/home/nic/forge/.venv/bin/python3 -B   /home/nic/forge/scripts/aiweb_slice39b_deterministic_validation_identity_versioning_lifecycle_verify.py   /home/nic/forge   --mode applied
```

The verifier runs the Slice 39B behavior test plus the inherited Slice 30
through Slice 39A behavior chain. It does not stage, commit, or push.
