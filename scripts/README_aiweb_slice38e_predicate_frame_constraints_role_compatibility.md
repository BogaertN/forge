# Slice 38E

This slice adds the closed predicate-frame constraint registry.

Run the behavior test:

```bash
/home/nic/forge/.venv/bin/python3 -B scripts/test_aiweb_slice38e_predicate_frame_constraints_role_compatibility.py /home/nic/forge
```

Run the visible verifier:

```bash
/home/nic/forge/.venv/bin/python3 -B scripts/aiweb_slice38e_predicate_frame_constraints_role_compatibility_verify.py /home/nic/forge --mode applied
```

The verifier prints every child test sequentially. It uses no hidden workers and suppresses no test output.
