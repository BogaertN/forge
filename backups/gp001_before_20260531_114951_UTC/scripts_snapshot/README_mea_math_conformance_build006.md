# MEA-DISCOVERY-KERNEL-MATH-CONFORMANCE-BUILD-006

## Purpose

Build 006 installs the first deterministic mathematical conformance contract for the
existing MEA / Forge Discovery Kernel after the controlled Build 005 MEA memory write.

It is intentionally read-only. It does **not** rewrite the sealed `144hz_substrate_status`
history or the Build 005 JSONL memory record.

## Why this build exists

The final MEA / Forge Discovery Kernel document requires:

```text
Score(c_i) = αR + βP + γU + δN + ηI + κΩ + ρA - λD - μB - νK
I(c_i) = ΔF + ΔQ + ΔX
```

with:
- replay required for sealing;
- positive information gain required for discovery;
- proof debt constraining claim status;
- the 144 Hz harmonic path remaining `hypothesis`, not `verified_claim`;
- RMC rendering only after MEA has sealed and classified a manifest.

The live historic Patch 275–299 path was built before the final reconciliation
document. Build 006 therefore implements the corrected forward contract and audits
the already-installed preview path instead of pretending it already conforms.

## New modules

```text
forge/rmc_engine_v1/mea/fixed_point_math_contract.py
forge/rmc_engine_v1/mea/evidence_tier_contract.py
forge/rmc_engine_v1/mea/fbsc_operator_crosswalk.py
forge/rmc_engine_v1/mea/math_conformance.py
```

It also updates only the package export surface:

```text
forge/rmc_engine_v1/mea/__init__.py
```

and adds verifier/test scripts:

```text
forge/scripts/test_mea_math_conformance_build006.py
forge/scripts/mea_math_conformance_build006_verify.py
```

## Deterministic fixed-point contract

Future conformed scoring uses integer micro-units only:

```text
0         = 0.000000
1,000,000 = 1.000000
```

and integer basis-point weights:

```text
10,000 = coefficient 1.0000
```

New governed term vectors reject binary floating-point inputs. Historical float preview
records remain preserved as historical artifacts and may be converted only for read-only
audit comparison.

## Information-gain correction

Build 006 uses:

```text
I(c_i) = ΔF + ΔQ + ΔX
```

where:

```text
ΔF = verified fact gain
ΔQ = uncertainty-vector reduction or bounded narrowing
ΔX = contradiction resolution
K  = operator cost only
```

This removes the prior notation collision where `K` represented both knowledge gain and
operator cost.

## Claim-state correction

The canonical 144 Hz path is represented as:

```text
epistemic_claim_status: hypothesis
required_next_action:   test_required
```

The system no longer needs to force `hypothesis` and `test_required` into one conflicting
claim-status axis.

## Evidence-tier law

Build 006 enforces:

```text
Internal FBSC / AI.Web ancestry may support bounded structural hypothesis review.
Internal ancestry alone cannot authorize an external empirical verified claim.
Replay proves reproducibility, not scientific truth.
```

For the canonical 144 Hz test contract:

```text
aggregate_support_micro: 450000
proof_debt_micro:        550000
verified_empirical_claim_permitted: false
```

## FBSC operator crosswalk

Build 006 maps the FBSC operator family into MEA runtime contracts:

```text
⧒  Recursive Amplification        -> hypothesize / expand / simulate
⧀  Symbolic Discharge / Collapse  -> rejected / cold storage / containment
⧧  Resonance Severance            -> split / reject
⧜  Recursive Integration / Memory -> Build 005 controlled MEA JSONL memory write
⧙  Recursive Lock / Fusion        -> Patch 297 controlled seal transition
⟁  Resonance Merge                -> merge / bridge
ΔΦ  Phase Differential             -> phase-state and gate validation
```

Only the already implemented current-corridor bindings are claimed live. Future merge,
bridge, split, and simulation activation is not overclaimed.

## Honest live-path audit finding

Build 006 executes the actual installed measurement kernel over the existing
`cg_hypothesis_001` preview and detects that the historical active scorer path is not yet
ready to be declared conformant:

```text
information_gain_zero_blocks_discovery
measured_drift_exceeds_theta_D
legacy_proof_debt_exceeds_hypothesis_limit
no_measured_memory_ancestry_resonance_bound
operator_cost_not_bound_to_executed_hypothesize_operator
legacy_coherence_uses_fallback_R_P_U_N
```

Therefore:

```text
active_legacy_pipeline_declared_conformant: false
migration_decision:
  BLOCK_ACTIVE_SCORER_MIGRATION_UNTIL_LIVE_TERMS_CONFORM
```

This is not a rollback of the historic sealed hypothesis. The Build 005 record remains a
lawfully bounded historical hypothesis with `proof_debt = 0.85` and renderer blocked.
It is not rewritten.

## Forbidden effects

Build 006 performs no:

```text
file write during runtime evaluation
MEA memory write
MEA runtime-state write
Identity Vault write
Contribution Economy write
CT minting
ledger write
Chroma access
LLM call
renderer activation
HTTP route addition
UI modification
```

## Next engineering boundary

The next build must migrate future candidate/seal scoring through the new conformance
contract and prove, without rewriting historical records, that a newly evaluated
144 Hz case produces:

```text
epistemic_claim_status: hypothesis
required_next_action: test_required
verified_empirical_claim_permitted: false
```

Only after the measured scoring path conforms should Forge proceed into the downstream
RMC semantic lexicon and non-LLM rendering corridor.
