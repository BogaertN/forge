# AI.Web Slice 48 — Local Runtime Service Boundary Runtime Specification

## Accepted base

- repository: `/home/nic/forge`
- branch: `main`
- parent HEAD: `1f9070065aad5df11627cbb16732430ca47ded11`
- parent tree: `2d18842fb938c99ce5616fc713577b7e9f2ea1ae`
- parent subject: `Slice 47 GP-014 status decision and Phase D closeout`

## Service boundary

Slice 48 installs a separate, disabled-by-default, owner-only local service. It does not import or launch `main.py`, the legacy Terminus server, the desktop orchestrator, the operator console, an LLM, a vector system, a resource loader, a tool router, an action path, a delivery path, or GP-014.

The service uses a Unix domain socket in the current user's state directory. It creates no TCP or UDP listener and has no HTTP route. The default state directory is outside the repository at `~/.local/state/aiweb-forge/local-runtime-service-v1`.

## Explicit commands

- `start`
- `stop`
- `status`
- `health`
- `version`
- `capabilities`

Every command supports `--format text` and `--format json`.

## Process ownership

A stop operation is permitted only when PID, Linux process-start ticks, exact command-line digest, entry-script identity, and service identity all agree. A reused PID or unrelated live process is never signaled. Shutdown first uses an owner-only control token over an owner-only AF_UNIX socket. SIGTERM is only a bounded fallback after exact process identity verification. SIGKILL is not used.

## State and permissions

- state directory: mode `0700`
- socket, token, identity, PID record, and lock files: mode `0600`
- JSON records: canonical serialization and atomic replacement
- repository writes: prohibited
- startup at boot: not installed
- systemd service: not installed

## Deferred work

Slice 49 may add the read-only language inspection API after a fresh source packet and dedicated acceptance. Slice 48 itself exposes no language records.
