# Patch 208 — Missing RMC Modules Staged Rebuild

This staged patch rebuilds the three missing RMC modules identified by Patch 206 and frozen by Patch 207.

It does not modify live `~/aiweb/runtime_wrappers/` modules.
It does not wire Gilligan into Forge.
It does not move or delete the standalone `gilligan_agent` folder.

## Staged runtime import names

These names match the existing `rmc_orchestrator.py` imports:

- `phase_parser/phase_state_parser.py`
- `drift_detection/drift_detector.py`
- `echo_validator/echo_validator.py`

## Staged logical compatibility names

These wrappers match the architecture/report language:

- `phase_state_parser/phase_state_parser.py`
- `drift_arbitrator/drift_arbitrator.py`
- `echo_gate/echo_gate.py`

## Verification

Run:

```bash
cd ~/forge
source .venv/bin/activate
python scripts/rmc_stage208_verify.py
```

Expected verdict:

```text
Verdict: PASS
```

## Next step after PASS

Create a separate install patch that copies these staged modules into `~/aiweb/runtime_wrappers/`, then updates the RMC orchestrator to use numeric `phase_id`/`phase_number` when calling the manifest compiler.
