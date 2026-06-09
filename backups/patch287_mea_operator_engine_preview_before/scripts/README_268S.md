# Patch 268S — ProtoForge2 Drift Candidate Adapter

## Why 268S

Patch 268R found the ProtoForge2 substrate root but returned SKIPPED because
only MANIFEST.sha256 and README.md were present. A wider audit found the real
drift candidates. This patch expands the connector to discover, classify, and
safely call them.

## Audit findings

| Path | Classification | SHA256 prefix |
|---|---|---|
| `.../laws/aiweb_rmc_drift_detector_reference.py` | `rmc_safe_arbitrator` | 648a35b3 |
| `.../protoforge_sandbox/drift_bridge.py` | `sandbox_drift_bridge` | e376b274 |
| `.../laws/protoforge_memory_drift_reference.py` | `full_doctrine_reference` | 5488f672 |
| `/home/nic/protoforge/src/protoforge/memory/drift.py` | `live_protoforge_package_copy` | 5488f672 |
| `/home/nic/protoforge/backend/drift.py` | `legacy_runtime_rejected` | d128249b |

The two full-engine copies are hash-identical (same 550-line implementation).

## Call order

1. `DriftArbitrator.evaluate()` from `aiweb_rmc_drift_detector_reference.py` (rank 1)
2. `DriftBridge.evaluate()` from `drift_bridge.py` (rank 2)
3. `DriftMonitor` — detected but **NOT called by default** (creates `storage/logs/drift.log`)
4. Legacy `backend/drift.py` — **REJECTED** (random entropy + log writes)

## Corrected boundary language (replaces 268R no_arbitrary_exec)

```
no_shell: true
no_subprocess: true
no_browser_selected_import_path: true
controlled_local_import_only: true
default_http_preview_read_only: true
full_drift_monitor_not_called_by_default: true
```

Note: `exec_module()` is used internally by Python's importlib. This is disclosed.

## RMC drift schema output

Preview endpoint normalizes to: `epsilon_s`, `entropy`, `verdict`, `drift_detected`,
`events`, `phase_deviation`, `transition_validity`, `correction_recommended`,
`chi_t_required`, `circuit_breaker_open`, `projection_ready`, `recommended_action`,
`source_adapter`, `source_candidate_sha256`, `normalized: true`.

## Tests: 373/373 pass across all five suites. Verifier: 37/37.

## Install

```bash
cd /home/nic && tar -xzf ~/patch268S_protoforge2_drift_candidate_adapter.tar.gz
python3 -m py_compile forge/rmc_engine_v1/protoforge2_drift_connector.py && echo OK
python3 -m py_compile forge/main.py && echo OK
python3 forge/scripts/patch268S_verify.py
# RESULT: PATCH_268S_VERIFY_OK
# Then verify on the running system:
curl http://localhost:7477/api/rmc/protoforge2-drift-status | python3 -m json.tool | head -30
```

## Does NOT modify

- `rmc_engine_v1/drift_engine.py` (structural RMC drift engine unchanged)
- Any existing routes (all 54 preserved)
- Identity Vault, Chroma, or any active memory
