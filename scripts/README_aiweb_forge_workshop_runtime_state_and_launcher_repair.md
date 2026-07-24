# Forge Workshop Runtime-State and Launcher Repair R2

This payload completes the source/runtime separation discovered by the first real
launcher acceptance.

## Modified source files

- `main.py`
- `agents/forge/permissions.py`
- `scripts/aiweb_os_appctl.py`

Only `main.py` changes relative to the first applied repair. The permissions and
launcher files remain byte-identical to the first repair so the final accepted
payload stays one coherent 12-file unit.

## Applied state correction

The R2 apply tool:

1. verifies the exact failed-result repository state;
2. backs up repository and runtime destinations;
3. migrates the two Patch 198 and two Patch 239 runtime residue records;
4. restores the two tracked Patch 239 reports to committed bytes;
5. removes only the two exact untracked Patch 198 source-tree files;
6. applies the corrected 12-file payload;
7. stages and commits nothing.

## Real acceptance

The result collector runs the repair behavior test, verifier, inherited Slice 48
behavior and committed verifier, real launcher/API smoke test, source/runtime
post-check, and disposable rollback rehearsal.

Bridge 1 remains unapplied.
