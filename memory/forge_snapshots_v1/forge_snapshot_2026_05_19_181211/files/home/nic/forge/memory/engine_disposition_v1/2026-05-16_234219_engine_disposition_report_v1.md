# Engine Disposition Report — Patch 117

Created: `2026-05-16T23:42:19`
Status: `ENGINE_DISPOSITION_REPORT_READY`
Excluded total: `25`
Recommended next patch: `Patch 118 — Forge Master Status Report`

## Bucket Counts

- `agent_identity_deferred`: `3`
- `approved_hold_family_excluded`: `2`
- `authority_or_external_control_deferred`: `3`
- `deferred_hold_family`: `6`
- `general_deferred_review`: `3`
- `memory_archive_or_state_deferred`: `2`
- `runtime_wrapper_or_stack_deferred`: `6`

## Engines

- `admin_override_console` → `authority_or_external_control_deferred` | `DEFERRED` | `aiweb/engines/admin_override_console`
- `agents_stack` → `runtime_wrapper_or_stack_deferred` | `DEFERRED` | `aiweb/runtime_wrappers/agents_stack`
- `aiweb_os` → `deferred_hold_family` | `DEFERRED` | `aiweb/runtime_wrappers/aiweb_os_v1`
- `aiweb_os_engine` → `general_deferred_review` | `DEFERRED` | `aiweb/engines/aiweb_os_engine`
- `cold_archive_engine` → `approved_hold_family_excluded` | `APPROVED` | `aiweb/engines/cold_archive_engine_frozen_v1`
- `contribution_ledger_stack` → `runtime_wrapper_or_stack_deferred` | `DEFERRED` | `aiweb/runtime_wrappers/contribution_ledger_stack`
- `control_stack` → `runtime_wrapper_or_stack_deferred` | `DEFERRED` | `aiweb/runtime_wrappers/control_stack`
- `core_stack_breather` → `runtime_wrapper_or_stack_deferred` | `DEFERRED` | `aiweb/engines/core_stack_breather`
- `core_system_stack` → `runtime_wrapper_or_stack_deferred` | `DEFERRED` | `aiweb/runtime_wrappers/core_system_stack`
- `dream_state_engine` → `memory_archive_or_state_deferred` | `DEFERRED` | `aiweb/engines/dream_state_engine`
- `drift_arbitration_engine` → `approved_hold_family_excluded` | `APPROVED` | `aiweb/engines/drift_arbitration_engine`
- `external_feed_listener` → `authority_or_external_control_deferred` | `DEFERRED` | `aiweb/engines/external_feed_listener`
- `fluid_memory_engine` → `memory_archive_or_state_deferred` | `DEFERRED` | `aiweb/engines/fluid_memory_engine`
- `gilligan` → `agent_identity_deferred` | `DEFERRED` | `agents/gilligan`
- `gilligan_drift_correction_upgrade` → `general_deferred_review` | `DEFERRED` | `aiweb/engines/gilligan_drift_correction_upgrade`
- `goal_injection_engine` → `authority_or_external_control_deferred` | `DEFERRED` | `aiweb/engines/goal_injection_engine`
- `memory_stack_engine` → `deferred_hold_family` | `DEFERRED` | `aiweb/engines/memory_stack_engine`
- `memory_stack_engine_breathing` → `deferred_hold_family` | `DEFERRED` | `aiweb/engines/memory_stack_engine_breathing_v1`
- `memory_stack_stack` → `runtime_wrapper_or_stack_deferred` | `DEFERRED` | `aiweb/runtime_wrappers/memory_stack_stack`
- `naming_engine` → `general_deferred_review` | `DEFERRED` | `aiweb/engines/naming_engine`
- `neo` → `agent_identity_deferred` | `DEFERRED` | `agents/neo`
- `neo_engine` → `agent_identity_deferred` | `DEFERRED` | `aiweb/engines/neo_engine`
- `protoforge_dashboard_runtime` → `deferred_hold_family` | `DEFERRED` | `runtime_wrappers/protoforge_dashboard_runtime_v2.0`
- `saved_ideas` → `deferred_hold_family` | `DEFERRED` | `projects/recursive_lmm_grok1/engines/saved_ideas`
- `step_counter` → `deferred_hold_family` | `DEFERRED` | `projects/recursive_lmm_grok1/engines/step_counter_frozen_v1`

## Authority

Read-only disposition report. No engine writes, no ledger mutation, no quarantine, no delete.
