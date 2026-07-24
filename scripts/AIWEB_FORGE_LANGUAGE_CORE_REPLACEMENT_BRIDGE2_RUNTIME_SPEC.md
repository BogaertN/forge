# Bridge 2 Runtime Specification

- Bridge 1 routes continue to execute their fixed existing Forge commands.
- Unsupported ordinary requests return `UNSUPPORTED_HOLD`.
- Patch 199 returns an impossible/held plan without calling `_p187_call_ollama`.
- Operator Console reports `planner_called=false` and `ollama_fallback_used=false`.
- Explicit LLM-backed generation/review commands are untouched and remain visible for later replacement.
- No new execution, permission, file-write, memory-write, RMC-authority, or simulation authority is introduced.
