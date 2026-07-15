# Slice 36F — Scope, Attachment, and Reference Operator Constraints

This package adds the first bounded scope-and-reference constraint layer after Slice 36E.

## Package

`aiweb_language_core_bootstrap.scope_attachment_reference_constraints`

## Public entry point

`apply_scope_attachment_reference_constraints(...)`

Required predecessors:

- Slice 36B projection result;
- Slice 36D binding result;
- Slice 36E phase-trail result.

Optional input:

- immutable explicit ActiveContextRegistry;
- a tuple naming prohibited context dependencies requested by a caller;
- explicit policy and limit records.

## Important behavior

The package preserves every lawful attachment candidate and every exact context match.

It never selects an attachment or resolves a reference.

It never searches external context.

It never mutates a Slice 36E trail.

## Verification

Run:

```bash
/usr/bin/python3 -B scripts/test_aiweb_slice36f_scope_attachment_reference_constraints.py
```

Then run the independent verifier in the requested precommit or committed mode.

## Boundaries

- reference candidate is not reference resolution;
- reference resolution is not concept meaning;
- concept authority belongs to Slice 37;
- predicate and participant-role authority belong to Slice 38;
- recognized capability is not authorized capability;
- verified claim is not world truth;
- private is not releasable;
- quoted instruction is not active instruction.
