# Patch 262-RewireUI-R1 — Canonical Route Manifest + React API Client

Purpose: repair the three-way mismatch between the backend API contract, the actual `do_GET` route surface, and React component URL wiring.

Changes:

1. `forge/main.py`
   - Adds `_p262z_rmc_route_manifest_entries_v1()`.
   - Adds `_p262z_rmc_route_manifest_v1()`.
   - Adds `GET /api/rmc/route-manifest`.
   - Updates `_p245_api_contract_v1()` to draw its RMC endpoint table from the canonical manifest entries.
   - Preserves C16 optional LLM renderer routes, C14 glyph renderer routes, and C12 promotion routes.

2. `forge/operator_console_src/rmc-api-client.ts`
   - Canonical React client.
   - Fetches `/api/rmc/route-manifest` once and caches route lookup.
   - Provides one named function per important RMC endpoint.
   - Includes optional LLM renderer toggles while keeping LLM output non-authoritative.
   - Includes promotion preview/status helpers using `APPROVE_RMC_PROMOTION` as the backend token source.

3. `forge/operator_console_src/rmc-api-client.js`
   - JavaScript compatibility staging copy.

Boundary:

- No shell execution.
- No LLM calls.
- No Chroma query.
- No file writes at runtime.
- No Identity Vault writes.
- No RMC memory writes.
- UI is not authority.

Install note for React source:

After applying this patch, copy the TypeScript client into the React app when ready:

```bash
mkdir -p /home/nic/aiweb/apps/forge-operator-console/src/lib
cp ~/forge/operator_console_src/rmc-api-client.ts    /home/nic/aiweb/apps/forge-operator-console/src/lib/rmc-api-client.ts
```

Then React components should import named functions from `../lib/rmc-api-client` instead of hardcoding `/api/rmc/...` paths.
