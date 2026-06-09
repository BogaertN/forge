# Patch 262C1 — Audible Browser Tone + FBSC Glyph Codex Alignment

This is a small hotfix/upgrade on top of Patch 262C.

It keeps `/api/rmc/cymatic-preview` read-only while improving two things:

1. Browser audio audibility: symbolic 16–144 Hz phase frequencies remain preserved in the trace, but browser playback uses `playback_frequency_hz` transposed upward by three octaves so normal speakers can actually reproduce the tones.
2. FBSC glyph codex alignment: each phase geometry node includes glyph, phase color, code identifier, function hook, and motion tag from the FBSC Phase Glyph Codex.

Boundary:

- No new Forge commands.
- No shell.
- No LLM call.
- No Chroma query.
- No DB reads.
- No ingestion.
- No resurrection.
- No audio file writes.
- No image file writes.
- No Identity Vault write.
- No RMC live memory write.

The sound still only plays after an operator click in the browser.
