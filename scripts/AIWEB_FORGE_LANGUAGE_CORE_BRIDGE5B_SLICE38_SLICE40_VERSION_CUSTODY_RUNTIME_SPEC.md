# Bridge 5B Runtime Specification

Bridge 5B adds a shared fail-closed predicate/frame version-custody helper
to the verbal-cognition gate runtime and connects it to the Slice 40C,
Slice 40D, Slice 40E, and Slice 40F validators.

## Accepted paths

### Frozen legacy path

The original Slice 40 fixture pair remains accepted exactly as before:

- predicate version `v1.0.0`
- frame version `v1.0.0`

This correction does not reinterpret or migrate those frozen records.

### Current registry path

Any non-legacy pair must resolve by exact ID in the closed read-only Slice
38 registries, must carry each exact registered version, and must preserve
the frame-to-predicate link recorded by the admitted frame.

The current real inspect branch proves:

- admitted predicate version `v1.3.0`
- admitted frame version `v1.1.0`

## Permanent non-authorities

Version compatibility is not candidate selection, gate authority,
requirement satisfaction, gate composition, gate pass, gate failure,
selected meaning, permission, route, execution, memory authority,
rendering, delivery, evidence validation, truth, or LLM authority.
