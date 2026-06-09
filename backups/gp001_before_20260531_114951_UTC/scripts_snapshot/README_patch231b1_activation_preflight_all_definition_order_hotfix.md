# Patch 231B.1 — Activation Preflight-All Definition Order Hotfix

## Purpose

Patch 231B installed the router entries for `forge-agent-activation-preflight-all` and
`forge-agent-activation-preflight-all-report`, but placed the supporting function definitions
below the `if __name__ == "__main__": main()` runtime call. Python compiles that layout, but
when Forge starts, `main()` runs before those definitions are executed. The result is a runtime
`NameError` when the command is called.

This hotfix moves the Patch 231B command definitions above the runtime entrypoint so the router
can call them safely.

## Boundary

This is a narrow route/definition-order hotfix only.

It does not install manual activation.
It does not activate any agent.
It does not write RMC memory.
It does not write Identity Vault database rows.
It does not create new RMC namespace folders.

## Expected command surface

After this hotfix, Forge should report:

`Expected: 800   Found: 800   Missing: 0`

## Expected command result

`forge-agent-activation-preflight-all` should run and return either:

`ALL_TARGET_AGENTS_READY_FOR_MANUAL_ACTIVATION`

or:

`BLOCKED_ACTIVATION_PREFLIGHT_ALL_TARGETS`

Both are valid depending on the real state of Athena and Neo.
