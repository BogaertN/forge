# Forge / EchoForge LLM Authority Separation Decision

Status: implemented candidate; independent verification required  
Baseline: `1d7c4da0f524a5abad75962daa66d0eaa9a5bbce`  
Risk: HIGH

## Decision

Forge has no LLM authority. It does not use a model to interpret input, select
meaning, choose a route, grant permission, select or dispatch a tool, construct
or progress a patch, validate proof, execute an action, or write protected
memory.

Legacy Forge model commands fail closed with:

`FORGE_LLM_AUTHORITY_REMOVED_USE_EXPLICIT_ECHOFORGE`

The old `ForgeAgent` import remains only as a fail-closed compatibility
boundary. Its provider, tool-dispatch, and `ask()` methods all raise the same
governed refusal.

EchoForge owns the single explicit model-enabled command:

`echoforge-advisory <role> :: <prompt>`

EchoForge output is advisory text. It is not Forge meaning, permission, routing,
action, patch authority, proof, validation, or protected memory. EchoForge
sends no tools, rejects returned tool calls, and has no automatic route back
into Forge.

## Preserved boundaries

- The deterministic Forge workshop remains available.
- Language Bridges 1 through 5 remain deterministic and LLM-free.
- Bridge 5 remains held before selected-meaning construction.
- Existing read-only historical records may still describe former model lanes.
- No dependency, service, schema, privilege, or external provider was added.
- No EchoForge-to-Forge admission path is created by this change.

## Recovery decision

Application requires a verified backup of the two modified files and proof that
the ten created paths were absent. Rollback restores those two exact files and
removes only the ten introduced paths. Rollback must not touch unrelated files,
stage, commit, or push automatically.

This record does not accept, lock, install, commit, push, or release the
candidate.
