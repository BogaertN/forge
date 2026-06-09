# CANONICAL_ENGINE_RELATIONSHIP_MAP_V1

Status: `CANONICAL_ENGINE_RELATIONSHIP_MAP_READY`

Read-only relationship map for final canonical engines using imports, source text references, shared runtime terms, and latest safe-test status. No project files are modified.

## Counts
- canonical_engines: 54
- relationship_rows: 54
- total_detected_edges: 86
- high_risk_neighbors: 0
- medium_risk_neighbors: 5
- engines_with_test_issues: 0
- engines_without_test_result: 5

## Canonical Relationship Rows
### activity_log
- canonical_path: `projects/recursive_lmm_grok1/engines/activity_log`
- resolved_path: `/home/nic/aiweb/projects/recursive_lmm_grok1/engines/activity_log`
- relationship_count: 0
- risk_level: `MEDIUM`
- test_status: `NO_TEST_RESULT`

### agent_reflection_engine
- canonical_path: `aiweb/engines/agent_reflection_engine`
- resolved_path: `/home/nic/aiweb/engines/agent_reflection_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### ascii_interpreter_engine
- canonical_path: `aiweb/engines/ascii_interpreter_engine`
- resolved_path: `/home/nic/aiweb/engines/ascii_interpreter_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### athena
- canonical_path: `agents/athena`
- resolved_path: `/home/nic/aiweb/agents/athena`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### athena_engine
- canonical_path: `aiweb/engines/athena_engine`
- resolved_path: `/home/nic/aiweb/engines/athena_engine`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - athena — source_text_reference (medium)

### christping_listener
- canonical_path: `aiweb/engines/christping_listener`
- resolved_path: `/home/nic/aiweb/engines/christping_listener`
- relationship_count: 1
- risk_level: `MEDIUM`
- test_status: `NO_TEST_RESULT`
- neighbors:
  - control_panel_ui_engine — source_text_reference (medium)

### christping_validator_engine
- canonical_path: `aiweb/engines/christping_validator_engine`
- resolved_path: `/home/nic/aiweb/engines/christping_validator_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### collapse_prevention_engine
- canonical_path: `aiweb/engines/collapse_prevention_engine`
- resolved_path: `/home/nic/aiweb/engines/collapse_prevention_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### compute_contribution_engine
- canonical_path: `aiweb/engines/compute_contribution_engine`
- resolved_path: `/home/nic/aiweb/engines/compute_contribution_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### confusion_checker
- canonical_path: `projects/recursive_lmm_grok1/engines/confusion_checker`
- resolved_path: `/home/nic/aiweb/projects/recursive_lmm_grok1/engines/confusion_checker`
- relationship_count: 0
- risk_level: `MEDIUM`
- test_status: `NO_TEST_RESULT`

### contribution_dashboard_engine
- canonical_path: `aiweb/engines/contribution_dashboard_engine`
- resolved_path: `/home/nic/aiweb/engines/contribution_dashboard_engine`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - compute_contribution_engine — source_text_reference (medium)

### control_panel_ui_engine
- canonical_path: `aiweb/engines/control_panel_ui_engine_v1.02`
- resolved_path: `/home/nic/aiweb/engines/control_panel_ui_engine_v1.02`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - protoforge — source_text_reference (medium)

### document_output_formatter
- canonical_path: `aiweb/engines/document_output_formatter`
- resolved_path: `/home/nic/aiweb/engines/document_output_formatter`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### drift_analyzer_tool
- canonical_path: `aiweb/engines/drift_analyzer_tool`
- resolved_path: `/home/nic/aiweb/engines/drift_analyzer_tool`
- relationship_count: 2
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - drift_signature_logger — shared_runtime_term:drift (weak)
  - symbolic_drift_visualizer — shared_runtime_term:drift (weak)

### drift_signature_logger
- canonical_path: `aiweb/engines/drift_signature_logger`
- resolved_path: `/home/nic/aiweb/engines/drift_signature_logger`
- relationship_count: 2
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - drift_analyzer_tool — shared_runtime_term:drift (weak)
  - symbolic_drift_visualizer — shared_runtime_term:drift (weak)

### echo_trace_visualizer
- canonical_path: `aiweb/engines/echo_trace_visualizer`
- resolved_path: `/home/nic/aiweb/engines/echo_trace_visualizer`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### entropy_monitor_engine
- canonical_path: `aiweb/engines/entropy_monitor_engine`
- resolved_path: `/home/nic/aiweb/engines/entropy_monitor_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### failsafe_manager
- canonical_path: `aiweb/engines/failsafe_manager`
- resolved_path: `/home/nic/aiweb/engines/failsafe_manager`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### field_resonance_mapper
- canonical_path: `aiweb/engines/field_resonance_mapper`
- resolved_path: `/home/nic/aiweb/engines/field_resonance_mapper`
- relationship_count: 6
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - recursive_field_breather — shared_runtime_term:field (weak)
  - recursive_field_engine — shared_runtime_term:field (weak)
  - recursive_field_stack — shared_runtime_term:field (weak)
  - resonance_charge_meter — shared_runtime_term:resonance (weak)
  - resonance_display — shared_runtime_term:resonance (weak)
  - resonance_visualizer_engine — shared_runtime_term:resonance (weak)

### glyph_engine
- canonical_path: `aiweb/engines/glyph_engine`
- resolved_path: `/home/nic/aiweb/engines/glyph_engine`
- relationship_count: 2
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - glyph_ui_overlay — shared_runtime_term:glyph (weak)
  - symbolic_glyph_engine — shared_runtime_term:glyph (weak)

### glyph_ui_overlay
- canonical_path: `aiweb/symbolic_layers/glyph_ui_overlay`
- resolved_path: `/home/nic/aiweb/symbolic_layers/glyph_ui_overlay`
- relationship_count: 2
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - glyph_engine — shared_runtime_term:glyph (weak)
  - symbolic_glyph_engine — shared_runtime_term:glyph (weak)

### install_onboarding_engine
- canonical_path: `aiweb/engines/install_onboarding_engine`
- resolved_path: `/home/nic/aiweb/engines/install_onboarding_engine`
- relationship_count: 7
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - compute_contribution_engine — source_text_reference (medium)
  - contribution_dashboard_engine — source_text_reference (medium)
  - loop_resurrection_engine — source_text_reference (medium)
  - peer_communication_engine — source_text_reference (medium)
  - resonance_charge_meter — source_text_reference (medium)
  - symbolic_capacitor_engine — source_text_reference (medium)
  - tone_engine — source_text_reference (medium)

### loop_resurrection_engine
- canonical_path: `aiweb/engines/loop_resurrection_engine`
- resolved_path: `/home/nic/aiweb/engines/loop_resurrection_engine`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - symbolic_feedback_loop_engine — shared_runtime_term:loop (weak)

### peer_communication_engine
- canonical_path: `aiweb/engines/peer_communication_engine`
- resolved_path: `/home/nic/aiweb/engines/peer_communication_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### phase_engine
- canonical_path: `aiweb/engines/phase_engine`
- resolved_path: `/home/nic/aiweb/engines/phase_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### plugin_engine
- canonical_path: `aiweb/engines/plugin_engine`
- resolved_path: `/home/nic/aiweb/engines/plugin_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### project_brain
- canonical_path: `projects/recursive_lmm_grok1/engines/project_brain`
- resolved_path: `/home/nic/aiweb/projects/recursive_lmm_grok1/engines/project_brain`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - recursive_field_engine — source_text_reference (medium)

### project_memory
- canonical_path: `projects/recursive_lmm_grok1/engines/project_memory`
- resolved_path: `/home/nic/aiweb/projects/recursive_lmm_grok1/engines/project_memory`
- relationship_count: 1
- risk_level: `MEDIUM`
- test_status: `NO_TEST_RESULT`
- neighbors:
  - spc_memory_migrator — shared_runtime_term:memory (weak)

### protoforge
- canonical_path: `aiweb/runtime_wrappers/protoforge_v1.04_db_enabled`
- resolved_path: `/home/nic/aiweb/runtime_wrappers/protoforge_v1.04_db_enabled`
- relationship_count: 6
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - control_panel_ui_engine — source_text_reference (medium)
  - phase_engine — source_text_reference (medium)
  - plugin_engine — source_text_reference (medium)
  - recursive_field_engine — source_text_reference (medium)
  - system_log_engine — source_text_reference (medium)
  - tier_enforcer — source_text_reference (medium)

### recursion_mapper
- canonical_path: `aiweb/symbolic_layers/recursion_mapper`
- resolved_path: `/home/nic/aiweb/symbolic_layers/recursion_mapper`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### recursive_agent_kernel
- canonical_path: `aiweb/engines/recursive_agent_kernel`
- resolved_path: `/home/nic/aiweb/engines/recursive_agent_kernel`
- relationship_count: 4
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - recursive_field_breather — shared_runtime_term:recursive (weak)
  - recursive_field_engine — shared_runtime_term:recursive (weak)
  - recursive_field_stack — shared_runtime_term:recursive (weak)
  - recursive_verification_engine — shared_runtime_term:recursive (weak)

### recursive_field_breather
- canonical_path: `aiweb/engines/recursive_field_breather`
- resolved_path: `/home/nic/aiweb/engines/recursive_field_breather`
- relationship_count: 6
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - protoforge — source_text_reference (medium)
  - field_resonance_mapper — shared_runtime_term:field (weak)
  - recursive_agent_kernel — shared_runtime_term:recursive (weak)
  - recursive_field_engine — shared_runtime_terms:field,recursive (weak)
  - recursive_field_stack — shared_runtime_terms:field,recursive (weak)
  - recursive_verification_engine — shared_runtime_term:recursive (weak)

### recursive_field_engine
- canonical_path: `aiweb/engines/recursive_field_engine`
- resolved_path: `/home/nic/aiweb/engines/recursive_field_engine`
- relationship_count: 5
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - field_resonance_mapper — shared_runtime_term:field (weak)
  - recursive_agent_kernel — shared_runtime_term:recursive (weak)
  - recursive_field_breather — shared_runtime_terms:field,recursive (weak)
  - recursive_field_stack — shared_runtime_terms:field,recursive (weak)
  - recursive_verification_engine — shared_runtime_term:recursive (weak)

### recursive_field_stack
- canonical_path: `aiweb/runtime_wrappers/recursive_field_stack`
- resolved_path: `/home/nic/aiweb/runtime_wrappers/recursive_field_stack`
- relationship_count: 5
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - recursive_field_engine — source_text_reference (medium)
  - field_resonance_mapper — shared_runtime_term:field (weak)
  - recursive_agent_kernel — shared_runtime_term:recursive (weak)
  - recursive_field_breather — shared_runtime_terms:field,recursive (weak)
  - recursive_verification_engine — shared_runtime_term:recursive (weak)

### recursive_verification_engine
- canonical_path: `engines/recursive_verification_engine`
- resolved_path: `/home/nic/aiweb/engines/recursive_verification_engine`
- relationship_count: 5
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - protoforge — source_text_reference (medium)
  - recursive_agent_kernel — shared_runtime_term:recursive (weak)
  - recursive_field_breather — shared_runtime_term:recursive (weak)
  - recursive_field_engine — shared_runtime_term:recursive (weak)
  - recursive_field_stack — shared_runtime_term:recursive (weak)

### resonance_charge_meter
- canonical_path: `aiweb/engines/resonance_charge_meter`
- resolved_path: `/home/nic/aiweb/engines/resonance_charge_meter`
- relationship_count: 3
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - field_resonance_mapper — shared_runtime_term:resonance (weak)
  - resonance_display — shared_runtime_term:resonance (weak)
  - resonance_visualizer_engine — shared_runtime_term:resonance (weak)

### resonance_display
- canonical_path: `aiweb/symbolic_layers/resonance_display`
- resolved_path: `/home/nic/aiweb/symbolic_layers/resonance_display`
- relationship_count: 3
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - field_resonance_mapper — shared_runtime_term:resonance (weak)
  - resonance_charge_meter — shared_runtime_term:resonance (weak)
  - resonance_visualizer_engine — shared_runtime_term:resonance (weak)

### resonance_visualizer_engine
- canonical_path: `aiweb/engines/resonance_visualizer_engine`
- resolved_path: `/home/nic/aiweb/engines/resonance_visualizer_engine`
- relationship_count: 3
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - field_resonance_mapper — shared_runtime_term:resonance (weak)
  - resonance_charge_meter — shared_runtime_term:resonance (weak)
  - resonance_display — shared_runtime_term:resonance (weak)

### resurrection_planner
- canonical_path: `aiweb/engines/resurrection_planner`
- resolved_path: `/home/nic/aiweb/engines/resurrection_planner`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### revisit_previous_tasks
- canonical_path: `projects/recursive_lmm_grok1/engines/revisit_previous_tasks`
- resolved_path: `/home/nic/aiweb/projects/recursive_lmm_grok1/engines/revisit_previous_tasks`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - loop_resurrection_engine — source_text_reference (medium)

### seed_manager
- canonical_path: `aiweb/engines/seed_manager`
- resolved_path: `/home/nic/aiweb/engines/seed_manager`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### spc_memory_migrator
- canonical_path: `aiweb/engines/spc_memory_migrator`
- resolved_path: `/home/nic/aiweb/engines/spc_memory_migrator`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - project_memory — shared_runtime_term:memory (weak)

### stack_breather_phase2
- canonical_path: `aiweb/runtime_wrappers/stack_breather_phase2`
- resolved_path: `/home/nic/aiweb/runtime_wrappers/stack_breather_phase2`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### symbolic_capacitor_engine
- canonical_path: `aiweb/engines/symbolic_capacitor_engine`
- resolved_path: `/home/nic/aiweb/engines/symbolic_capacitor_engine`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - control_panel_ui_engine — source_text_reference (medium)

### symbolic_cognition_stack
- canonical_path: `aiweb/runtime_wrappers/symbolic_cognition_stack`
- resolved_path: `/home/nic/aiweb/runtime_wrappers/symbolic_cognition_stack`
- relationship_count: 3
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - loop_resurrection_engine — source_text_reference (medium)
  - resonance_charge_meter — source_text_reference (medium)
  - symbolic_feedback_loop_engine — source_text_reference (medium)

### symbolic_drift_visualizer
- canonical_path: `aiweb/engines/symbolic_drift_visualizer`
- resolved_path: `/home/nic/aiweb/engines/symbolic_drift_visualizer`
- relationship_count: 2
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - drift_analyzer_tool — shared_runtime_term:drift (weak)
  - drift_signature_logger — shared_runtime_term:drift (weak)

### symbolic_feedback_loop_engine
- canonical_path: `aiweb/engines/symbolic_feedback_loop_engine`
- resolved_path: `/home/nic/aiweb/engines/symbolic_feedback_loop_engine`
- relationship_count: 1
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - loop_resurrection_engine — shared_runtime_term:loop (weak)

### symbolic_glyph_engine
- canonical_path: `aiweb/engines/symbolic_glyph_engine`
- resolved_path: `/home/nic/aiweb/engines/symbolic_glyph_engine`
- relationship_count: 3
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - protoforge — source_text_reference (medium)
  - glyph_engine — shared_runtime_term:glyph (weak)
  - glyph_ui_overlay — shared_runtime_term:glyph (weak)

### symbolic_layers_stack
- canonical_path: `aiweb/runtime_wrappers/symbolic_layers_stack`
- resolved_path: `/home/nic/aiweb/runtime_wrappers/symbolic_layers_stack`
- relationship_count: 3
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - glyph_ui_overlay — source_text_reference (medium)
  - recursion_mapper — source_text_reference (medium)
  - resonance_display — source_text_reference (medium)

### symbolic_policy_engine
- canonical_path: `aiweb/engines/symbolic_policy_engine`
- resolved_path: `/home/nic/aiweb/engines/symbolic_policy_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### system_log_engine
- canonical_path: `aiweb/engines/system_log_engine`
- resolved_path: `/home/nic/aiweb/engines/system_log_engine`
- relationship_count: 3
- risk_level: `LOW`
- test_status: `PASS`
- neighbors:
  - phase_engine — source_text_reference (medium)
  - plugin_engine — source_text_reference (medium)
  - tier_enforcer — source_text_reference (medium)

### tier_enforcer
- canonical_path: `aiweb/engines/tier_enforcer`
- resolved_path: `/home/nic/aiweb/engines/tier_enforcer`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### tone_engine
- canonical_path: `aiweb/engines/tone_engine`
- resolved_path: `/home/nic/aiweb/engines/tone_engine`
- relationship_count: 0
- risk_level: `LOW`
- test_status: `PASS`

### trust_guard
- canonical_path: `projects/recursive_lmm_grok1/engines/trust_guard`
- resolved_path: `/home/nic/aiweb/projects/recursive_lmm_grok1/engines/trust_guard`
- relationship_count: 0
- risk_level: `MEDIUM`
- test_status: `NO_TEST_RESULT`

## Risk Neighbors
- christping_listener: MEDIUM — test_status=NO_TEST_RESULT; relationship_count=1
- project_memory: MEDIUM — test_status=NO_TEST_RESULT; relationship_count=1
- activity_log: MEDIUM — test_status=NO_TEST_RESULT; relationship_count=0
- confusion_checker: MEDIUM — test_status=NO_TEST_RESULT; relationship_count=0
- trust_guard: MEDIUM — test_status=NO_TEST_RESULT; relationship_count=0

## Authority
- read_only_analysis: True
- engine_file_write_authority: False
- project_file_write_authority: False
- patch_apply_authority: False
- shell_execution_authority: False
- ledger_mutation: False
- relationship_map_authority_only: True
