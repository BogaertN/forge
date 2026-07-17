# Slice 38D Participant-Role Identity Registry

This increment adds a closed Forge-owned participant-role identity registry on top of the committed Slice 38C action-root registry.

The implementation is additive. It does not modify Slice 38A, Slice 38B, or Slice 38C source files.

## Visible test command

```bash
/home/nic/forge/.venv/bin/python3 -B /home/nic/forge/scripts/aiweb_slice38d_participant_role_identity_registry_verify.py /home/nic/forge --mode applied
```

The verifier runs the Slice 38D behavior test and every inherited language-core behavior test sequentially. It prints each command, child output, duration, and return code directly to the terminal. It uses no background test workers and suppresses no child output.

## Scope

This slice proves role identity, lifecycle ancestry, dependencies, relationships, correction support, conflict support, exact read-only lookup, and authority separation. Predicate frames and occurrence role assignment remain absent.
