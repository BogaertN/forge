# Forge Mode Registry — Patch 129

Status: `FORGE_MODE_REGISTRY_READY_NO_ENFORCEMENT`
Modes: `10`
Enforcement active: `False`

## Modes
- `READ_ONLY` — Read-only analysis: Inspect files, manifests, audit, status, search results, and reports without mutation.
- `CONTEXT_SEARCH` — Context and code search: Query document/context/code memory and display provenance-bound results.
- `PATCH_PLANNING` — Patch planning: Draft source-grounded patch plans and LLM planning packets under Forge-owned memory only.
- `SANDBOX` — Sandbox rehearsal: Apply proposed changes only inside Forge-owned sandbox copies and report the result.
- `TEST` — Allowlisted test mode: Run only safe, explicit, allowlisted tests with shell=False and bounded reporting.
- `APPLY` — Controlled live apply: Permit live writes only after proposal, preflight, sandbox, tests, rollback, and explicit token gates pass.
- `RECOVERY` — Recovery and rollback: Restore from approved rollback/snapshot paths with explicit recovery authority.
- `DASHBOARD` — Dashboard mode: Display read-only gauges and status artifacts before any UI write controls exist.
- `SELF_UPDATE` — Forge self-update lane: Prepare Forge self-update proposals, snapshots, and sandboxes before any future self-write authority.
- `INGESTION` — Corpus ingestion: Register, extract, dry-run, and explicitly ingest approved documents into the context library.
