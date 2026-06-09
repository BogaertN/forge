# Patch 263R — AI.Web OS Desktop Orchestrator Single-Instance Hardening

Patch 263 made AI.Web OS launch like a product. Patch 263R hardens the lifecycle manager so repeated desktop clicks do not spawn duplicate operator windows.

## Behavior

- Keeps React as a static production build served through Forge.
- Keeps the clean Chrome app-mode operator window.
- Adds a single-instance lock around `start`, `stop`, and `restart`.
- Reuses/focuses the existing operator window when it is already open.
- Scans for an existing AI.Web OS app window if the PID file is stale or missing.
- Removes stale PID files safely.
- Reports lock path/state, operator window PID source, and log path in `status`.
- Still refuses to kill an externally owned Forge backend.

## Commands

```bash
~/forge/scripts/aiweb-os-start
~/forge/scripts/aiweb-os-status
~/forge/scripts/aiweb-os-stop
~/forge/scripts/aiweb-os-restart
```

## Boundary

This patch does not grant browser authority, does not write RMC memory, does not touch Identity Vault, does not query Chroma, does not call LLMs, and does not execute arbitrary shell commands. It is a desktop lifecycle supervisor only.

## Why this matters

A production desktop launcher must tolerate repeated clicks. Patch 263R makes start idempotent: if the backend and operator window are already running, start reuses the existing app instead of opening another window.
