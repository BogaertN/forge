# Patch 262C — RMC Cymatic Geometry / Browser Tone Preview Read-Only

Adds `GET /api/rmc/cymatic-preview`.

The endpoint derives deterministic SVG geometry and a browser-only tone plan from the already verified `GET /api/rmc/phase-preview` payload. It does not generate audio files, image files, shell commands, Chroma queries, ingestions, Identity Vault writes, or RMC live memory writes.

The frontend may render SVG in the browser and may play a short tone sequence only after the operator clicks the preview button. No generated artifact is persisted in this patch.
