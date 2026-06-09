# RMC Deep Architecture Roadmap v1

**Status as of Patches 265–268**
Not a spec doc. A navigation reference.

---

## WHAT IS BUILT (Patches 265–268)

### Containment Router (Patch 265)
`forge/rmc_engine_v1/containment_router.py`
The safety organ that sits after coherence scoring and before manifest compilation.
Six routes. Sealed routes cannot project, compile manifests, echo-validate, or write memory.
74 behavior tests. 21 verifier checks.

### SPC Cold Storage (Patch 266)
`forge/rmc_engine_v1/spc_cold_storage.py`
Three-tier Symbolic Phase Capacitor: WARM (Purgatory), COLD (Archive), DEEP (Hell).
Collapse idempotence law: ϊ(⊙) = ⊙. Collapse is forensic preservation, not deletion.
Preview mode + gated commit. Idempotence key enforces no-duplicate collapse.

### Drift Archive (Patch 266)
`forge/rmc_engine_v1/drift_archive.py`
Append-only diagnostic archive for unclassifiable / fallback candidates.
Cannot support truth claims. No resurrection path.

### Dream State Quarantine (Patch 266)
`forge/rmc_engine_v1/dream_state_quarantine.py`
Speculative candidates that are not wrong but not ready.
Future arbitration required. No projection. No stable memory.

### Ghost Loop Containment (Patch 266)
`forge/rmc_engine_v1/ghost_loop_containment.py`
Gate 7 (system capacity) failures. The loop is not wrong — the system cannot close it.
Preserved for future runtime generations. Cannot re-enter active runtime.

### χ(t) Correction Gate Preview (Patch 267)
`forge/rmc_engine_v1/chi_correction_gate.py`
χ(t) = Φ₁·α + Σ(Δψ / t)
Models correction attempts, residue accumulation, drift spiral detection.
All thresholds named: intervention (0.35), circuit_breaker (0.72), Babel Cutoff (0.78, RPMC doctrine).
Settle window: 3.33s (Harmonic Runtime Codex). Residue decay: 0.30 (χ(t) doctrine).

### ProtoForge2 Drift Connector Preflight (Patch 268)
`forge/rmc_engine_v1/protoforge2_drift_connector.py`
Safe importlib-based inspection of the real ProtoForge2 drift module.
Three modes: LIVE / SKIPPED / FALLBACK. Never modifies ProtoForge2.
Normalizes PF2 output to canonical RMC drift schema.

---

## IMMEDIATE NEXT WORK

### ChristPing 7-Gate Resurrection Protocol
`forge/rmc_engine_v1/resurrection_engine.py`

Connect SPC warm storage to the 7-gate ChristPing protocol.
At each Φ9 window, check all 7 gates for warm-tier SPC records.

Gates (from Harmonic Runtime Codex):
1. Collapse signature is a valid hash
2. phase_at_collapse is a valid phase
3. Invariant core I_t is recoverable
4. resurrection_limit not exceeded (default 5)
5. System has sufficient phase resolution capacity
6. Resonance signature matches (harmonic comparator)
7. System operator capacity gate (final approval)

Outcomes:
- All 7 pass + MATCH → RESURRECTION → ψ′ returned to active runtime
- Any gate fails → deferred to next Φ9 window
- BREACH in comparator → seal to DEEP archive (permanent)
- resurrection_limit exceeded → LOCKED → DEEP archive
- Gate 7 fails → Ghost Loop containment (not SPC)

ψ′ = transformed identity constituted by collapse history (not restoration, not repair).

### Temporal FFT Drift Analysis
Connect temporal pattern analysis to drift_engine.py.
Track ε_s over a rolling window of 8–16 data points.
Use FFT-style decomposition to distinguish:
- Exploration drift: entropy signal with useful novelty; allow to develop
- Thrashing drift: stuck recursive collapse pattern; route to SPC immediately
The ProtoForge2 memory-drift.py has the EMA + FFT implementation to adapt.

### Drift Spiral Detector (standalone)
Isolate the drift_spiral_detected logic from chi_correction_gate.py into a
standalone module that watches ε_s over correction attempts.
If 2+ consecutive corrections increase ε_s by > drift_spiral_delta (0.02):
abort further correction attempts, route directly to SPC.

### Active Loop Real Persistence
The current active_loop_state is reconstructed read-only from pipeline reports.
Future: persist the real loop state object between sessions.
Required fields: loop_id, open/closed, current_unresolved_branches,
current_correction_queue, named_concepts_in_progress, source_trace_ref,
last_valid_manifest_id, last_valid_echo_score, active_memory_namespace,
continuation_cursor.
State transition: S_{t+1} = F(S_t, O_t) requires a real persisted state object.

### Wire χ(t) into correction_naming_engine.py
Replace the boolean chi_required flag with a call to evaluate_chi_t().
At ε_s ≥ 0.35: attempt χ(t) correction before proceeding to naming.
If correction fails: route to correction_queue or SPC per chi_correction_gate.py output.
This closes the loop between the gate (Patch 267) and the correction engine.

---

## MEDIUM-TERM WORK

### Identity Vault Activation Gates
gilligan.local, athena.local, neo.local exist as inactive draft profiles.
Build activation preflight: agent role contract, permission scope, memory namespace,
action request contract, tool request bridge.
Activation requires explicit operator approval.
Agents exchange manifests, not messages.

### Memory Economy — CT Minting Engine
Connect the promotion path to CT (Contribution Token) minting.
When a memory node is promoted to stable memory by an identified contributor,
mint CRT (Creator Token) for that contributor.
CT ledger: separate append-only structure, permanently firewalled from investment ledger.
No administrator can award CT manually. CT can only be minted from validated Memory Capsules.

### psi1_trace System
Every active agent registers a ψ₁_trace — their origin state.
Lives in Identity Vault.
χ(t) correction binds to ψ₁ when normal correction fails at 0.35 threshold.
CT is cryptographically anchored to ψ₁.
Losing ψ₁ = losing CT history.

### Genesis Node Network Layer
TCP 7342: dead path sync between nodes.
UDP 7341: node discovery.
Per-node attribution ledger with reconciliation.
Multi-node dead path sharing: failed loops on one node educate other nodes.
Full design in Genesis Node Documents 9–16.

### ProtoForge2 Full Connector Activation
Current: `IMPLEMENTATION_REGISTERED_NOT_FORGE_CONNECTOR` (preflight only).
Next: build the formal Forge connector contract.
Enables: drift engine live mode, code renderer sandbox testing, simulation runs.

### KBIC Tribal Path
Memory sovereignty namespace: `rmc/kbic`.
Offline-first configuration.
Field deployment form factor: ruggedized tablet, wearable chest/shoulder harness.
Tribal staff workflow documentation.
Data sovereignty enforcement layer.

---

## LONGER-TERM ARCHITECTURE

### RMC Patch Generation Through Manifests
The long-term milestone:
  user request
  → RMC trace
  → candidate implementation paths
  → selected patch manifest
  → code renderer
  → preflight
  → Forge proposal
  → sandbox test (ProtoForge)
  → operator approval
  → apply
  → verifier
  → receipt
  → memory writeback

### Security Shell / High-Security HTML Layer
The HTML layer at / and /operator-console becomes the security boundary.
Request filtering, auth headers, operator session state, route allowlist,
approval-token warning layer.
Build before serious agent power.

### Agent-to-Manifest Communication
When agents (Gilligan, Athena, Neo) communicate, they exchange manifest packets.
Not free text. Every agent message has: claim, phase path, operator path,
memory links, confidence, drift status, output permission.
GILIN Resonance Protocol provides the inter-agent heartbeat for this.

### Memory Supersession / Correction History
When a memory is corrected or superseded, the old record is marked, not deleted.
Fields: superseded_by, correction_reason, supersession_timestamp, newer_version_id.
Without this, old wrong memories become undead — retrieved without warning.

### Stable Memory Retrieval Dominance Rules
stable > review_queue > speculative.
Source-backed > inferred.
User-confirmed > generated.
Newer correction supersedes older drifted memory.
Blocked-pattern memory warns but does not support claims.

---

## LAW SUMMARY (all modules must uphold these)

1. The model can reason. Forge must verify.
2. Forge governs. The UI is not authority.
3. RMC is trace-first. Language renders from a manifest, not generated first.
4. LLM is optional renderer/input support, not the center.
5. Cold storage is silence and forensic preservation, not deletion.
6. Ghost loops are not wrong. The current system lacks capacity to close them.
7. Collapse cannot compound: ϊ(⊙) = ⊙.
8. No route becomes authority just because it exists.
9. No output is real without trace.
10. No memory is real without gated writeback.
