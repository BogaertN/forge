# Patch 262A — RMC Memory Object Viewer / Manifest Trace View

Adds a read-only RMC object inspection endpoint:

- `GET /api/rmc/memory-object`

The endpoint can inspect allowlisted Forge memory/report files and returns a compact object summary plus a `manifest_trace`.

Supported selectors:

- `?selector=latest_manifest`
- `?selector=latest_receipt`
- `?path=memory/context_library_v1/...`
- `?source_file=<symbolic_map_file>&chunk_id=<chunk_id>`

Authority boundary:

- No Forge commands added.
- No shell.
- No LLM call.
- No Chroma query.
- No DB file reads.
- No ingestion.
- No resurrection.
- No cymatic generation.
- No Identity Vault write.
- No RMC live memory write.
