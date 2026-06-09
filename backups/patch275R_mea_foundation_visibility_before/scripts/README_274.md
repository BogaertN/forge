# Patch 274 — AI.Web Build Manifest Endpoint

Adds `/api/aiweb-os/build-manifest`, a read-only build-state source of truth for Forge/RMC/Operator Console state.

Also hardens the high-security Terminus HTML shell presentation: the original HTML shell is hidden by default and opens only inside an Operator Console overlay when the left rail `Open Terminus` control is clicked. The button no longer opens a separate browser tab.

Safety contract:

- no arbitrary browser shell
- no arbitrary command endpoint
- no RMC live memory write
- no Identity Vault write
- no Chroma write
- no LLM call
- build manifest is read-only
- Terminus overlay is operator-invoked and hidden by default
