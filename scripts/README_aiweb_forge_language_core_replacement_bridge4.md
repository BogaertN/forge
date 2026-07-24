# Forge Language Bridge 4

Bridge 4 exposes real CandidateMeaning and MSM-v1 candidate custody through explicit read-only previews. Exact candidate nomination is recorded only as a validated held boundary because gate custody and selection eligibility are not yet connected.

It changes `main.py`, adds `forge_language_bridge_v4`, and includes its own behavior test and verifier. It does not modify `agents/forge/agent.py`, ProtoForge, RMC, launcher repair files, or prior bridge modules.
