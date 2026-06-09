# RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009

## Purpose

Build 009 adds the deterministic non-LLM rendering preview corridor downstream of
`MEA-TO-RMC-RENDER-GATE-ADAPTER-BUILD-008`.

The pipeline is:

```text
verified Build 008 MEA render-admission packet
→ controlled semantic lexicon
→ finite grammar sentence plan
→ deterministic surface realization
→ unapproved render preview awaiting Build 010 Echo Validator hardening
```

## Architectural boundary

MEA and RMC remain separate typed layers.

- MEA produces and seals the bounded problem-manifest result.
- Build 008 admits the sealed MEA result only under its existing epistemic limits.
- Build 009 maps the admitted limits into deterministic preview language.
- Build 010 must validate that rendered language faithfully echoes the admitted meaning
  before any approval is possible.

Build 009 does not merge the MEA problem-manifest schema into the RMC meaning-manifest
schema and does not compile a new RMC meaning manifest.

## Installed source

```text
forge/rmc_engine_v1/renderer/__init__.py
forge/rmc_engine_v1/renderer/semantic_lexicon.py
forge/rmc_engine_v1/renderer/grammar_templates.py
forge/rmc_engine_v1/renderer/surface_realizer.py
forge/rmc_engine_v1/renderer/renderer.py
forge/scripts/test_non_llm_renderer_lexicon_build009.py
forge/scripts/non_llm_renderer_lexicon_build009_verify.py
```

## Supported preview delivery modes

```text
explanation
decision
warning
verification_result
next_step
refusal
uncertain_result
```

These are delivery modes only. Every mode remains subordinate to:

```text
claim_status = hypothesis
required_next_action = test_required
proof_debt = 0.85
verified claim = blocked
empirical fact = blocked
discovery = blocked
```

## Hard boundaries

Build 009:

- generates deterministic preview text only;
- uses no LLM and no free-form text generation;
- adds no new evidence and cannot reduce proof debt;
- does not invoke the existing generic output renderer;
- does not invoke Echo Validator yet;
- does not approve or publish user-facing output;
- does not write MEA memory or RMC output memory;
- does not write Identity Vault, Contribution Economy, CT, or either ledger;
- does not touch Chroma;
- does not create API routes or UI components;
- requires no application restart.

## Test commands after installation

```bash
cd "$HOME/forge"

PYTHONDONTWRITEBYTECODE=1 "$HOME/forge/.venv/bin/python" scripts/test_non_llm_renderer_lexicon_build009.py   --forge-root "$HOME/forge"

PYTHONDONTWRITEBYTECODE=1 "$HOME/forge/.venv/bin/python" scripts/non_llm_renderer_lexicon_build009_verify.py   --forge-root "$HOME/forge"
```

Expected result:

```text
RESULT: RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009_BEHAVIOR PASS  Total:107 Passed:107 Failed:0
RESULT: RMC-NON-LLM-RENDERER-AND-SEMANTIC-LEXICON-BUILD-009_VERIFY PASS  Total:25 Passed:25 Failed:0
```
