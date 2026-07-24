# AI.Web Forge Workshop Runtime-State and Launcher Repair — R2 Decision

## Decision

Preserve the accepted Forge workshop and its existing maker, simulator, approval,
audit, rollback, and operator-console capabilities. Repair source/runtime
separation before installing any deterministic language-core replacement bridge.

## Proven operational result

The first repair started the real Forge workshop through the launcher, opened port
7477, returned HTTP 200 from `/api/status`, returned HTTP 200 from
`forge-protoforge-status`, and stopped cleanly. No simulation and no LLM call were
requested.

## R2 correction

R2 closes the remaining historical write paths:

1. Patch 198 roadmap injection reads runtime state first and committed source only
   as fallback, then writes only below the local runtime root.
2. Patch 198 command-install auto-update writes only below the runtime root.
3. Patch 239 status, plan, approved-run, and result reports write only below the
   runtime root.
4. Operator-console report, trace, receipt, RMC-status, and object-viewer readers
   admit the bounded runtime report root and retain committed-source fallback.
5. The four exact runtime residue files produced by the first live test are
   preserved outside the repository before source-tree copies are restored or
   removed.

## Runtime root

`~/.local/state/aiweb-forge/legacy-workshop-v1/`

## Authority boundaries

- Forge remains the workshop where work is made.
- ProtoForge remains the controlled construction and simulation substrate.
- The simulator is preserved.
- Bridge 1 is not installed.
- Qwen/Ollama behavior is not changed by this repair.
- No simulation is executed by apply, rollback, verification, or collection.
- No LLM request is made by apply, rollback, verification, or collection.
- No source file is staged or committed by the external tools.
