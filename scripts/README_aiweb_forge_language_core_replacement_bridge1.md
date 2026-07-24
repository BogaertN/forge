# Forge Language-Core Replacement Bridge 1

This patch installs the first bounded deterministic interpretation bridge into
the existing Forge workshop. It does not replace Forge.

Covered requests are interpreted without Qwen/Ollama and mapped only to a
fixed allowlist of existing Forge commands:

- Forge status
- audit-chain verification
- Forge capability report
- ProtoForge status
- ProtoForge symbolic-frequency plan
- ProtoForge falling-cube plan
- ProtoForge result display

A natural-language request to run a simulation is held and reports the existing
`RUN-PROTOFORGE` approval gate. No simulation is executed by the bridge.

Unsupported requests continue to use the historical Qwen/Ollama fallback.
That fallback remains temporary and visible in `forge-language-core-status`.

Commands added:

- `forge-language-core-status`
- `forge-language-preview <request>`

The preview command never executes the selected route.
