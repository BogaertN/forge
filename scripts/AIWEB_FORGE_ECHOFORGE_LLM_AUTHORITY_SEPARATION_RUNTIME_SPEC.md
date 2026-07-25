# Forge / EchoForge LLM Authority Separation Runtime Specification

## Forge refusal

The first command token is normalized and compared with the immutable legacy
model-command registry in `agents/forge/llm_authority.py`. Arguments are not
retained in the refusal receipt.

Every refusal contains:

- schema and stable refusal code;
- command token;
- surface;
- session identity;
- UTC timestamp;
- the explicit EchoForge advisory command;
- false flags for Forge model authority, model call, tool dispatch, and
  protected-memory write.

The same boundary is enforced at:

- the interactive Forge CLI;
- Patch 199 orchestrator execution;
- Patch 201 `/api/command`;
- every named legacy command function;
- every remaining direct Ollama/Qwen provider function in `main.py`; and
- the `agents.forge.agent.ForgeAgent` compatibility object.

There is no environment-variable override.

## EchoForge request

Syntax:

`echoforge-advisory <role> :: <prompt>`

Roles:

`debate`, `reflection`, `journal`, `clarifier`, `proponent`, `opponent`,
`decider`, `auditor`, `specialist`, and `discussion`.

The prompt must be non-empty and no larger than 16,000 characters or 64,000
UTF-8 bytes.

## Provider boundary

The provider:

- uses only Python’s standard library;
- permits only `http://127.0.0.1`, `http://[::1]`, or `http://localhost`;
- requires the `/api/chat` path;
- disables proxies;
- rejects credentials, query strings, fragments, and redirects;
- defaults to `qwen3:8b`;
- sends no `tools` field;
- limits the timeout to 180 seconds;
- limits the response body to 1 MiB;
- limits parsed JSON depth;
- rejects malformed JSON, empty output, and any non-empty `tool_calls`; and
- performs no shell execution or filesystem write.

The environment may select a different loopback URL or model through
`ECHOFORGE_OLLAMA_URL` and `ECHOFORGE_OLLAMA_MODEL`. The same endpoint and model
validation applies. External providers and credentials remain prohibited.

## Response boundary

The response envelope always fixes:

- `advisory_only=true`
- `forge_authority=false`
- `tool_calls_allowed=false`
- `tool_calls_present=false`
- `forge_route_selected=false`
- `forge_permission_granted=false`
- `forge_action_executed=false`
- `protected_memory_written=false`
- `proof_claimed=false`

It includes provider/model metadata and a SHA-256 of the displayed output.
Forge audit receives only role, provider/model, stable error code, and output
hash. Prompt and response content are not written to the Forge audit chain.

## Failure and recovery

Invalid input, unavailable provider, timeout, malformed response, oversized
response, redirect, non-loopback endpoint, or returned tool call produces a
typed refusal. No fallback provider or legacy Forge agent is attempted.

Forge startup, status, deterministic workshop commands, and Bridges 1 through 5
do not probe Ollama and continue to operate when Ollama is unavailable.
