# Forge Language Core Bridge 5

Bridge 5 connects exact CandidateMeaning and predicate/frame nominations through the real Slice 40C–40H and Slice 41C runtime, then stops before selected-meaning construction.

Run the behavior test:

```text
python scripts/test_aiweb_forge_language_core_bridge5_exact_gate_eligibility_hold.py /home/nic/forge
```

Run the verifier:

```text
python scripts/aiweb_forge_language_core_bridge5_verify.py /home/nic/forge --mode applied
```

This bridge does not select meaning, route tools, execute actions, write memory, call an LLM from Forge, or remove EchoForge's isolated LLM deliberation capability.
