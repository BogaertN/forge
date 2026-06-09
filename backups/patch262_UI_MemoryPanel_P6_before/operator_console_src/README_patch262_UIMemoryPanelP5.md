# Patch 262-UI-MemoryPanel-P5 — Memory Panel Component Boundary Split

Purpose: keep the RMC Memory Panel production-maintainable by splitting reusable UI primitives out of `RmcMemoryTab.tsx` while preserving all P2R/P3R/P4 behavior.

This patch is UI-only. It does not modify Forge backend routes, RMC engine modules, Chroma, Identity Vault, LLM renderer boundaries, promotion backend logic, or memory write logic.

New file:

- `operator_console_src/rmc-panel-primitives.tsx`

Updated file:

- `operator_console_src/RmcMemoryTab.tsx`

Preserved guardrails:

- React uses the canonical `rmc-api-client` route manifest client.
- Promotion still requires `APPROVE_RMC_PROMOTION` plus exact `PROMOTE <candidate_id>` confirmation.
- Partial endpoint load health remains isolated through `rmc-panel-health`.
- Optional LLM renderer remains default-off.
- The panel still contains no raw `/api/rmc` fetches, no shell execution, and no direct model authority claim.

Copy targets after install:

```bash
cp ~/forge/operator_console_src/rmc-api-client.ts \
   /home/nic/aiweb/apps/forge-operator-console/src/lib/rmc-api-client.ts

cp ~/forge/operator_console_src/rmc-ui-guards.ts \
   /home/nic/aiweb/apps/forge-operator-console/src/lib/rmc-ui-guards.ts

cp ~/forge/operator_console_src/rmc-panel-health.ts \
   /home/nic/aiweb/apps/forge-operator-console/src/lib/rmc-panel-health.ts

cp ~/forge/operator_console_src/rmc-panel-primitives.tsx \
   /home/nic/aiweb/apps/forge-operator-console/src/lib/rmc-panel-primitives.tsx

cp ~/forge/operator_console_src/RmcMemoryTab.tsx \
   /home/nic/aiweb/apps/forge-operator-console/src/tabs/RmcMemoryTab.tsx
```
