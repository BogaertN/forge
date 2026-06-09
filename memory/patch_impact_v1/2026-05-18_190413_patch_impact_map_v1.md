# PATCH_IMPACT_MAP_V1

Status: PATCH_IMPACT_MAP_READY
Created: 2026-05-18T19:04:13

Target: all

## Summary

- targets_requested: all
- matches: 54
- high_risk: 0
- medium_risk: 17
- low_risk: 37
- test_issues: 0
- no_test_result: 5

## Plain English

Read-only patch impact analysis. It maps a requested engine/path to canonical role, relationship neighbors, latest safe-test status, and rollback needs. It does not write project files or apply patches.

## Rows

- activity_log: risk=MEDIUM score=45 tests=NO_TEST_RESULT
- agent_reflection_engine: risk=LOW score=20 tests=PASS
- ascii_interpreter_engine: risk=LOW score=15 tests=PASS
- athena: risk=LOW score=20 tests=PASS
- athena_engine: risk=LOW score=28 tests=PASS
- christping_listener: risk=MEDIUM score=58 tests=NO_TEST_RESULT
- christping_validator_engine: risk=LOW score=15 tests=PASS
- collapse_prevention_engine: risk=LOW score=15 tests=PASS
- compute_contribution_engine: risk=LOW score=20 tests=PASS
- confusion_checker: risk=MEDIUM score=45 tests=NO_TEST_RESULT
- contribution_dashboard_engine: risk=LOW score=28 tests=PASS
- control_panel_ui_engine: risk=LOW score=33 tests=PASS
- document_output_formatter: risk=LOW score=20 tests=PASS
- drift_analyzer_tool: risk=LOW score=30 tests=PASS
- drift_signature_logger: risk=MEDIUM score=35 tests=PASS
- echo_trace_visualizer: risk=LOW score=15 tests=PASS
- entropy_monitor_engine: risk=LOW score=15 tests=PASS
- failsafe_manager: risk=LOW score=25 tests=PASS
- field_resonance_mapper: risk=MEDIUM score=40 tests=PASS
- glyph_engine: risk=LOW score=30 tests=PASS
- glyph_ui_overlay: risk=LOW score=30 tests=PASS
- install_onboarding_engine: risk=MEDIUM score=40 tests=PASS
- loop_resurrection_engine: risk=LOW score=33 tests=PASS
- peer_communication_engine: risk=LOW score=20 tests=PASS
- phase_engine: risk=LOW score=20 tests=PASS
- plugin_engine: risk=LOW score=25 tests=PASS
- project_brain: risk=LOW score=28 tests=PASS
- project_memory: risk=MEDIUM score=53 tests=NO_TEST_RESULT
- protoforge: risk=MEDIUM score=50 tests=PASS
- recursion_mapper: risk=LOW score=15 tests=PASS
- recursive_agent_kernel: risk=MEDIUM score=40 tests=PASS
- recursive_field_breather: risk=MEDIUM score=40 tests=PASS
- recursive_field_engine: risk=MEDIUM score=45 tests=PASS
- recursive_field_stack: risk=MEDIUM score=40 tests=PASS
- recursive_verification_engine: risk=MEDIUM score=45 tests=PASS
- resonance_charge_meter: risk=MEDIUM score=40 tests=PASS
- resonance_display: risk=LOW score=30 tests=PASS
- resonance_visualizer_engine: risk=MEDIUM score=35 tests=PASS
- resurrection_planner: risk=LOW score=15 tests=PASS
- revisit_previous_tasks: risk=LOW score=28 tests=PASS
- seed_manager: risk=LOW score=20 tests=PASS
- spc_memory_migrator: risk=LOW score=23 tests=PASS
- stack_breather_phase2: risk=LOW score=25 tests=PASS
- symbolic_capacitor_engine: risk=LOW score=33 tests=PASS
- symbolic_cognition_stack: risk=LOW score=30 tests=PASS
- symbolic_drift_visualizer: risk=LOW score=30 tests=PASS
- symbolic_feedback_loop_engine: risk=LOW score=33 tests=PASS
- symbolic_glyph_engine: risk=LOW score=30 tests=PASS
- symbolic_layers_stack: risk=LOW score=30 tests=PASS
- symbolic_policy_engine: risk=LOW score=25 tests=PASS
- system_log_engine: risk=MEDIUM score=40 tests=PASS
- tier_enforcer: risk=LOW score=20 tests=PASS
- tone_engine: risk=LOW score=20 tests=PASS
- trust_guard: risk=MEDIUM score=45 tests=NO_TEST_RESULT

## Authority

- read_only_analysis: True
- project_file_write_authority: False
- engine_file_write_authority: False
- patch_apply_authority: False
- shell_execution_authority: False
- ledger_mutation: False
- chroma_write_authority: False
