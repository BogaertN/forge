# Patch 262-UI-MemoryPanel-P4 — Partial Load Guard + Endpoint Health Surface

This patch hardens the RMC Memory Panel Phase 2 React surface after P3R.

It adds a UI-only endpoint health helper module and updates `RmcMemoryTab.tsx` so route failures are isolated per endpoint. One stale or unavailable backend route can no longer blank the whole panel. Healthy RMC surfaces still render, failed endpoints are marked in a dedicated `UI Endpoint Health / Partial Load Guard` section, and the panel records the last refresh time.

Safety boundary:
- UI source only.
- No backend authority changes.
- No writes.
- No shell execution.
- No LLM calls.
- No Chroma writes.
- No Identity Vault writes.
- No promotion call unless P3R guard remains armed by exact token and confirmation.
