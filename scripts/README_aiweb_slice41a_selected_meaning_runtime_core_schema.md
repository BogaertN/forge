# Slice 41A — Selected Meaning Runtime Core Schema and Authority Contract

This increment adds immutable, frozen, slotted schema contracts only.

It preserves the exact candidate, gate, authority, alternative, unresolved,
limitation, trace, and receipt reference shapes needed by later Slice 41 work.
It does not evaluate eligibility, select or rank a candidate, discard an
alternative, resolve ambiguity, construct selected meaning, modify MSM-v1,
enable bootstrap integration, create outward meaning, or create any truth,
evidence, proof, permission, execution, route, tool, action, memory, rendering,
delivery, or external-resource authority.

## Package

`aiweb_language_core_bootstrap.selected_meaning_runtime`

## Files

- `identity.py`: stable package, accepted-parent, and record-schema identities.
- `authority.py`: closed custody-state vocabulary, deferred scope, and permanent
  non-authority boundaries.
- `schema.py`: frozen, slotted record contracts and schema-only enums.
- `__init__.py`: explicit public exports.

## Next increment

Slice 41B owns deterministic validation, identity calculation, canonical
serialization, version custody, duplicate and collision rejection, lifecycle
transitions, and cross-record consistency checks.  A valid Slice 41B record
will still not mean a candidate is eligible or selected.
