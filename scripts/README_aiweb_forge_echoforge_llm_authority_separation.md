# Forge / EchoForge LLM Authority Separation

This slice removes model, model-routing, model-tool, and model-derived artifact
authority from Forge while preserving an explicit advisory-only EchoForge
runtime.

## Operator use

Forge commands work normally without Ollama. Legacy Forge model commands now
print a governed refusal.

For optional deliberation, invoke:

```text
echoforge-advisory clarifier :: Explain the difference between an advisory proposal and accepted Forge authority.
```

The result is visibly marked advisory. Copying an EchoForge answer does not
admit it into Forge. Any future use must enter a separately designed and
authorized deterministic Forge admission path.

## Developer checks

Run from the repository root:

```text
python3 scripts/test_aiweb_forge_echoforge_llm_authority_separation.py
python3 scripts/aiweb_forge_echoforge_llm_authority_separation_verify.py --repo . --mode applied
```

The behavior test uses simulated local-provider responses and makes no model or
network call. The verifier reads source and Git metadata only.

Also run the accepted Bridge 5 test and verifier and the frozen-legacy
containment gates named by the controlling patch design. Developer checks do
not accept or lock the candidate.

## Apply and rollback

Do not copy files into a live repository until a separate independent
verification and apply authorization.

Before application:

1. Confirm branch `main`, baseline
   `1d7c4da0f524a5abad75962daa66d0eaa9a5bbce`, and a clean worktree.
2. Create and verify a Git bundle.
3. Back up `main.py` and `agents/forge/agent.py` with modes and SHA-256 hashes.
4. Confirm the ten created paths do not already exist.
5. Apply only the exact twelve approved paths.

Rollback restores the two backups and removes only the ten introduced paths.
It never removes unrelated files and never stages, commits, or pushes.
