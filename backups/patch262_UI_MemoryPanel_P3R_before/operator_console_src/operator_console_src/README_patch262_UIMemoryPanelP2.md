# Patch 262-UI-MemoryPanel-P2

RMC Memory Panel Phase 2 UI source drop.

This patch does not change backend authority. It stages React source files under `forge/operator_console_src/` so the operator can copy them into the React app intentionally.

Copy targets:

```bash
mkdir -p /home/nic/aiweb/apps/forge-operator-console/src/lib
cp ~/forge/operator_console_src/rmc-api-client.ts /home/nic/aiweb/apps/forge-operator-console/src/lib/rmc-api-client.ts
cp ~/forge/operator_console_src/RmcMemoryTab.tsx /home/nic/aiweb/apps/forge-operator-console/src/tabs/RmcMemoryTab.tsx
```

The panel uses `/api/rmc/route-manifest` as the endpoint source of truth. It does not use raw `/api/rmc/...` fetch calls inside the component.

Gated promotion remains locked unless the operator manually enters `APPROVE_RMC_PROMOTION`.

The optional LLM renderer is default-off. The checkbox only sends `llm_renderer=on` for renderer preview and does not approve output or write memory.
