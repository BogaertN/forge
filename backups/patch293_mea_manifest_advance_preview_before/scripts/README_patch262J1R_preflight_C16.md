# Patch 262J1R-Preflight-C16 — Optional LLM Renderer Boundary

This patch adds a default-off optional LLM text renderer inside the RMC Output Renderer path.

## Production rules

- The deterministic template renderer remains the default.
- The LLM path can only run when explicitly toggled with `llm_renderer=on`, `use_llm=true`, or `llm=true`.
- The caller must supply `model_endpoint`.
- C16 approves only local HTTP loopback endpoints, such as `http://localhost:11434/api/generate`.
- Remote endpoints are refused.
- Non-text render modes do not use the LLM path.
- LLM text is bound to the existing sentence plan and is still checked for forbidden claims.
- LLM text is still subject to Echo Validator before memory write or projection.
- No files, Chroma writes, shell calls, Identity Vault writes, RMC memory writes, or canonical reference mutations are introduced.

## New endpoint

`/api/rmc/llm-renderer/status`

This status endpoint is read-only and does not call a model.

## Example default deterministic render

`/api/rmc/output-renderer?input=correct%20projection%20before%20naming&mode=text`

## Example optional LLM render

`/api/rmc/output-renderer?input=correct%20projection%20before%20naming&mode=text&llm_renderer=on&model_endpoint=http://localhost:11434/api/generate&model=qwen3:8b`

The output is not approved until Echo Validator passes.
