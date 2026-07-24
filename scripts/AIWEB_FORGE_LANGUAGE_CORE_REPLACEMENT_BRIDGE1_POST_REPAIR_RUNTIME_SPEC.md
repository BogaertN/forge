# Forge Language-Core Replacement Bridge 1 Runtime Specification

## Order of interpretation

1. Preserve exact input through accepted input-event custody.
2. Normalize a comparison copy deterministically.
3. Match only a fixed phrase or regular-expression family.
4. Produce a bounded route decision or explicit hold.
5. Produce a non-authoritative recursive-manifest preview.
6. In the CLI, execute only a fixed allowlist of existing Forge command
   functions.
7. In the Operator Console planner endpoint, return proposal metadata only.
8. Fall back to the historical model only when Bridge 1 reports unsupported.

## Covered routes

- `status`
- `audit`
- `forge-capabilities`
- `forge-protoforge-status`
- `forge-protoforge-simulation-plan`
- `forge-protoforge-result-show`

## Execution hold

Requests to run or execute a simulation return `APPROVAL_REQUIRED`.
The bridge does not call the run function. The existing Operator Console gate
remains `RUN-PROTOFORGE`.

## RMC boundary

Bridge 1 emits `preview_only_not_compiled_mu_t`. It writes no memory and claims
no selected-meaning, rendering, permission, or execution authority.
