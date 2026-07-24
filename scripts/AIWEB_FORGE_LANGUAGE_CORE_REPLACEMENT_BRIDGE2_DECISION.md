# Forge Language Core Replacement Bridge 2 Decision

## Accepted scope

Bridge 2 removes Qwen/Ollama fallback from ordinary request interpretation on the current Forge workshop line.

It closes three fallthroughs:

1. the final interactive `agent.ask(user_input)` path;
2. the Patch 199 planner's unsupported-request Ollama call;
3. the Operator Console interpretation fallback claim and route.

Unsupported requests are preserved as explicit deterministic holds. No command, shell, simulation, source write, memory write, or permission grant is performed.

## Deliberately not replaced yet

Explicit generation and review commands remain separately governed, including command implementation, diagnostic output analysis, engine review, repair drafts/reviews, self-suggestion, and tool-wrapper generation. Their presence is visible and is not represented as completed replacement.

## Source authority

Parent commit: `65e3dac9b7891b9ac58ce29c1084b9a3bec7a327`

Bridge 1 and the workshop launcher repair remain preserved. `agents/forge/agent.py` is not modified.
