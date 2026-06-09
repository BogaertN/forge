# Patch 238 — ProtoForge2 Discovery Scan

Purpose: begin Phase 11 by adding a read-only Forge command that discovers the real ProtoForge2 root and reports command candidates without running ProtoForge2.

## New commands

- `forge-protoforge2-discovery-scan`
- `forge-protoforge2-discovery-scan-report`

## Expected roots scanned

- `/home/nic/protoforge2`
- `/home/nic/ProtoForge2`
- `/home/nic/aiweb/protoforge2`
- `/home/nic/forge/protoforge2`

## Boundary

This patch is read-only discovery only.

It does not execute ProtoForge2.
It does not run startup, test, or health commands.
It does not update `/home/nic/aiweb/service_contracts/protoforge2.contract.json`.
It does not mutate Identity Vault.
It does not write RMC memory.
It does not write agent, long-term, private, or shared memory.
It does not read secret file contents. Dangerous files are listed by path only.
It does not grant autonomous execution.
It does not invoke EchoForge.

## Expected command surface

Patch 237 had `846/846` commands. Patch 238 adds two commands, so expected is `848/848`.

## Expected verdicts

If a ProtoForge2 root is found:

`PROTOFORGE2_DISCOVERY_SCAN_ROOT_FOUND`

If no expected root exists:

`PROTOFORGE2_DISCOVERY_SCAN_NO_ROOT_FOUND`

Both are valid read-only discovery outcomes.
