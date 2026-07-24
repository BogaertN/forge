# Bridge 5 Remaining LLM Lanes and EchoForge Boundary

## Forge

Ordinary Forge language interpretation does not fall through to Qwen/Ollama. Bridge 5 also performs no LLM call.

The following explicit legacy maker lanes may still contain model-dependent implementation or review behavior and must be addressed by the subsequent Forge/EchoForge authority-separation cutover:

- diagnostic-output analysis;
- Forge command implementation generation;
- Forge self-suggestion generation;
- engine review generation;
- generic repair draft generation;
- generic repair candidate review;
- LLM tool-wrapper generation; and
- LLM tool suggestion generation.

These lanes are not granted meaning-selection, permission, routing, or execution authority by Bridge 5.

## EchoForge

LLM use is intentionally preserved inside the explicit EchoForge deliberation, debate, reflection, and journaling boundary. EchoForge output is advisory material. It is not accepted Forge meaning, proof, permission, tool routing, patch authority, or execution authority.

The next cutover must remove or isolate model access from Forge while preserving the bounded EchoForge LLM route.
