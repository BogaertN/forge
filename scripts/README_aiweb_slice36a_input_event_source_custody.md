# Slice 36A — Input Event and Source Custody

Slice 36A adds an isolated `aiweb_language_core_bootstrap.input_event_custody` package. It captures exact in-memory source text into immutable, versioned custody records before any tokenization or interpretation.

## New runtime files

- `input_event_custody/schema.py` — closed statuses, condition codes, immutable limits, event, condition, span, and result records.
- `input_event_custody/capture.py` — strict UTF-8 capture, exact SHA-256, code-point/byte boundaries, unsupported Unicode classification, typed rejection, source-span construction, and validators.
- `input_event_custody/__init__.py` — explicit package export surface only.

## Boundary

The bootstrap root is not modified and does not auto-import this package. The runtime is standard-library only and has no filesystem, network, environment, memory, route, tool, action, delivery, concept, interpretation, or tokenization authority.

## Verification

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/test_aiweb_slice36a_input_event_source_custody.py

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/aiweb_slice36a_input_event_source_custody_verify.py \
  /home/nic/forge --mode committed
```

The verifier also runs the accepted inherited source-behavior suite from Slice 24 through Slice 35E.
