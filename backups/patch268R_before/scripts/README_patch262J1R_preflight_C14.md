# Patch 262J1R-Preflight-C14 — Real Glyph Renderer

Implements the deterministic FBSC glyph renderer for RMC.

## Scope

- Adds `forge/rmc_engine_v1/glyph_renderer.py`.
- Integrates `output_renderer.py` glyph packet mode with the real renderer.
- Registers `glyph_renderer` in `rmc_engine_v1/__init__.py`.
- Adds read-only glyph endpoint routes in `main.py`:
  - `/api/rmc/glyph-renderer`
  - `/api/rmc/glyph-renderer/status`
  - `/api/rmc/glyph-packet`
  - `/api/rmc/phase-glyph`

## Production boundary

Canonical glyphs are deterministic SVG/JSON packets from FBSC Phase Glyph Codex v2.5.
This patch does not use an image generator. Image generation may later expand a glyph packet visually, but generated images are not authoritative phase meaning.

No writes. No LLM. No image model. No Chroma. No DB reads. No shell. No Identity Vault. No RMC memory mutation.

## Verify

```bash
cd ~/forge
source .venv/bin/activate
python scripts/patch262J1R_preflight_C14_verify.py
python scripts/test_rmc_glyph_renderer_C14.py
python scripts/test_rmc_output_renderer_C5.py
python scripts/test_rmc_phase_codex_binding.py
```

Expected:

```text
RESULT: PATCH_262J1R_PREFLIGHT_C14_VERIFY_OK
RESULT: glyph_renderer_C14_behavior_tests_pass=True
RESULT: output_renderer_C5_behavior_tests_pass=True
RESULT: phase_codex_B3_behavior_tests_pass=True
```
