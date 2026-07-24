# Forge Workshop Runtime-State and Launcher Repair — R2 Runtime Specification

## Source/runtime split

Committed repository files are immutable baseline and implementation records.
Mutable local session state and generated operational reports belong under:

`~/.local/state/aiweb-forge/legacy-workshop-v1/`

## Configuration

- Runtime approvals: `config/approved_paths.json`
- Runtime session scope: `config/session_scope.json`
- Committed configuration remains fallback and architecture evidence.

## Build-sequence and Patch 198

- Runtime build-sequence directory:
  `memory/forge_build_sequence_v1/`
- Reads use runtime-first, committed-source fallback.
- Injection, append, mark, sync, and command-install auto-update write runtime
  state only.
- Startup must not create or modify a source-tree build-sequence record.

## ProtoForge connector and Patch 239

- Runtime report directory:
  `memory/aiweb_patch239_protoforge_connector_v1/`
- Status, plan, approved-run, and result reports write runtime state only.
- Per-file reads use runtime-first and committed-source fallback.
- Operator-console report, trace, receipts, RMC status, and object-viewer paths
  admit the runtime directory without broadening to arbitrary home-directory
  access.

## Launcher

- The literal `forge>` prompt is the readiness boundary for one-path and
  multiple-path startup.
- Missing browser openers are nonfatal; the backend remains available at
  `http://localhost:7477/operator-console`.
- Startup timeout cleanup removes only owned child and supervisor processes.

## Acceptance

- exact 12-file payload;
- exact Slice 48 parent identity;
- no staged paths;
- real launcher start and stop;
- HTTP 200 status and ProtoForge status;
- no simulation;
- no LLM request;
- source/runtime separation after the live test;
- inherited Slice 48 behavior and committed verifier;
- disposable apply/rollback rehearsal.
