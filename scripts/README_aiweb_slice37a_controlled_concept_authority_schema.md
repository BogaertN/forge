# AI.Web Slice 37A Controlled Concept-Authority Schema

This increment adds ten files and modifies no predecessor file.

The package contains immutable schema records, exact non-authority declarations, a disabled authority profile, an empty registry contract, deterministic identity helpers and structural validators.

It contains no built-in vocabulary and no lookup engine.

Run the behavior test:

```bash
/usr/bin/python3 -B scripts/test_aiweb_slice37a_controlled_concept_authority_schema.py /home/nic/forge
```

Run the independent verifier before commit:

```bash
/usr/bin/python3 -B scripts/aiweb_slice37a_controlled_concept_authority_schema_verify.py /home/nic/forge --mode precommit
```

Run the independent verifier after commit:

```bash
/usr/bin/python3 -B scripts/aiweb_slice37a_controlled_concept_authority_schema_verify.py /home/nic/forge --mode committed
```
