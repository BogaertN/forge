# Patch 255 — LLM / Natural-Language Request Bridge v1

Adds a Forge-governed, proposal-only natural-language request bridge for the production Operator Console.

Expected verifier output:

```text
PATCH255_LLM_REQUEST_BRIDGE_VERIFY_PASS
endpoint=/api/operator/llm-request
mode=forge_governed_plan_only
adds_forge_commands=False
executes_command=False
executes_shell=False
writes_files=False
identity_vault_write=False
rmc_live_memory_write=False
returns_proposal_only=True
```
