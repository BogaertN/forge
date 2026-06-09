# Symbolic Runtime Map — Patch 59

Generated: 2026-05-12T17:55:50
Read-only: True
Engines scanned: 425
Runtime roles: 12
Required role gaps: none

This is a map only. It does not clean, move, rename, promote, freeze, or delete engine files.

## phase_logic — Phase Logic / Φ-State Engine
Status: MAPPED  Required: True  Candidates: 68
Phases: Φ1, Φ2, Φ3, Φ4, Φ5, Φ6, Φ7, Φ8, Φ9
Operators: ∆Φ
Tracks FBSC phase state, phase transitions, phase validation, and structured progression.

- aiweb/engines/phase_engine — score=37 canonical=122 tags=active_or_unfrozen
- engines/phase_engine — score=33 canonical=82 tags=active_or_unfrozen
- aiweb/engines/phase_engine_frozen_v1 — score=29 canonical=111 tags=frozen
- aiweb/engines/tier_enforcer — score=27 canonical=123 tags=active_or_unfrozen
- engines/phase_engine_frozen_v1 — score=25 canonical=71 tags=frozen
- projects/recursive_lmm_grok1/engines/phase_engine_frozen_v1 — score=24 canonical=61 tags=frozen
- projects/recursive_lmm_grok1/engines/step_counter_frozen_v1 — score=24 canonical=61 tags=frozen
- projects/recursive_lmm_grok1_phase2/engines/step_counter_frozen_v1 — score=24 canonical=61 tags=frozen

## memory_persistence — Memory Persistence / Active Stack
Status: MAPPED  Required: True  Candidates: 35
Phases: Φ1, Φ2, Φ6, Φ7, Φ9
Operators: ΦM, MRN
Stores active memory, receipts, context state, runtime continuity, and durable recall surfaces.

- aiweb/engines/memory_stack_engine_breathing_v1 — score=49 canonical=126 tags=active_or_unfrozen
- engines/memory_stack_engine_breathing_v1 — score=45 canonical=86 tags=active_or_unfrozen
- aiweb/engines/memory_stack_engine — score=42 canonical=126 tags=frozen
- aiweb/engines/memory_stack_engine_breathing_v1_frozen_v1-0.01 — score=40 canonical=106 tags=frozen
- aiweb/engines/memory_stack_engine_breathing_v1_frozen_v1-0.02 — score=40 canonical=106 tags=frozen
- aiweb/engines/memory_stack_engine_frozen_v1 — score=40 canonical=103 tags=frozen
- aiweb/runtime_wrappers/memory_stack_stack — score=40 canonical=34 tags=active_or_unfrozen
- runtime_wrappers/memory_stack_stack — score=40 canonical=34 tags=active_or_unfrozen

## echo_validation — Echo Validation / Provenance Return
Status: MAPPED  Required: True  Candidates: 24
Phases: Φ2, Φ6, Φ7, Φ9
Operators: echo, χ(t)
Confirms outputs against origin, receipt, citation, trace, and echo-return requirements.

- aiweb/engines/christping_validator_engine — score=37 canonical=126 tags=active_or_unfrozen
- engines/christping_validator_engine — score=33 canonical=86 tags=active_or_unfrozen
- aiweb/engines/christping_validator_engine_frozen_v1-0.01 — score=28 canonical=106 tags=frozen
- aiweb/engines/echo_trace_visualizer — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/engines/symbolic_feedback_loop_engine — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/engines/agent_reflection_engine — score=26 canonical=119 tags=active_or_unfrozen
- engines/christping_validator_engine_frozen_v1-0.01 — score=24 canonical=66 tags=frozen
- engines/echo_trace_visualizer — score=23 canonical=80 tags=active_or_unfrozen

## drift_collapse — Drift / Collapse / Firewall Arbitration
Status: MAPPED  Required: True  Candidates: 38
Phases: Φ4, Φ5, Φ6
Operators: ε(t,Φ), ∆Φ, χ(t)
Detects phase drift, unsafe skips, contradiction, collapse risk, and firewall intervention points.

- aiweb/engines/drift_arbitration_engine — score=42 canonical=122 tags=frozen
- aiweb/engines/drift_arbitration_engine_frozen_v1-0.02 — score=41 canonical=117 tags=frozen
- aiweb/engines/drift_signature_logger — score=40 canonical=132 tags=active_or_unfrozen
- aiweb/engines/drift_arbitration_engine_frozen_v1-0.01 — score=40 canonical=108 tags=frozen
- aiweb/engines/drift_arbitration_engine_frozen_v1 — score=40 canonical=102 tags=frozen
- aiweb/engines/gilligan_drift_correction_upgrade — score=39 canonical=121 tags=active_or_unfrozen
- aiweb/engines/symbolic_drift_visualizer — score=39 canonical=121 tags=active_or_unfrozen
- aiweb/engines/drift_analyzer_tool — score=39 canonical=120 tags=active_or_unfrozen

## christping_correction — χ(t) / ChristPing Correction Layer
Status: MAPPED  Required: True  Candidates: 23
Phases: Φ5, Φ6, Φ7
Operators: χ(t)
Handles lawful correction after collapse, silence, grace pulse, and reentry gating.

- aiweb/engines/christping_listener — score=59 canonical=120 tags=active_or_unfrozen
- engines/christping_listener — score=55 canonical=80 tags=active_or_unfrozen
- projects/recursive_lmm_grok1/engines/christping_listener — score=54 canonical=75 tags=active_or_unfrozen
- projects/recursive_lmm_grok1_phase2/engines/christping_listener — score=54 canonical=70 tags=active_or_unfrozen
- aiweb/engines/christping_listener_frozen_v1 — score=50 canonical=100 tags=frozen
- aiweb/engines/christping_validator_engine — score=49 canonical=126 tags=active_or_unfrozen
- engines/christping_listener_frozen_v1 — score=46 canonical=60 tags=frozen
- engines/christping_validator_engine — score=45 canonical=86 tags=active_or_unfrozen

## spc_cold_storage — SPC / Cold Storage / Archive Containment
Status: MAPPED  Required: True  Candidates: 31
Phases: Φ5, Φ6, Φ8, Φ9
Operators: SPC, RPM
Keeps unresolved loops in non-destructive cold storage until lawful retrieval or resurrection.

- aiweb/engines/symbolic_capacitor_engine — score=49 canonical=125 tags=active_or_unfrozen
- engines/symbolic_capacitor_engine — score=45 canonical=85 tags=active_or_unfrozen
- projects/recursive_lmm_grok1/engines/symbolic_capacitor_engine — score=45 canonical=85 tags=active_or_unfrozen
- projects/recursive_lmm_grok1_phase2/engines/symbolic_capacitor_engine — score=44 canonical=75 tags=active_or_unfrozen
- aiweb/engines/symbolic_capacitor_engine_frozen_v1-0.01 — score=40 canonical=105 tags=frozen
- aiweb/engines/symbolic_capacitor_engine_frozen_v1 — score=39 canonical=99 tags=frozen
- aiweb/engines/cold_archive_engine — score=39 canonical=70 tags=backup_or_archive
- aiweb/engines/cold_archive_engine_frozen_v1 — score=37 canonical=79 tags=frozen,backup_or_archive

## loop_resurrection — Loop Resurrection / Lawful Return
Status: MAPPED  Required: True  Candidates: 15
Phases: Φ6, Φ7, Φ8, Φ9
Operators: χ(t), RPM
Maps engines responsible for returning sealed loops through echo-confirmed restoration.

- aiweb/engines/loop_resurrection_engine — score=49 canonical=120 tags=active_or_unfrozen
- engines/loop_resurrection_engine — score=45 canonical=80 tags=active_or_unfrozen
- projects/recursive_lmm_grok1/engines/loop_resurrection_engine — score=44 canonical=70 tags=active_or_unfrozen
- aiweb/engines/loop_resurrection_engine_frozen_v1 — score=40 canonical=104 tags=frozen
- aiweb/engines/loop_resurrection_engine_frozen_v1.01 — score=40 canonical=104 tags=frozen
- aiweb/engines/resurrection_planner — score=39 canonical=120 tags=active_or_unfrozen
- engines/loop_resurrection_engine_frozen_v1 — score=36 canonical=64 tags=frozen
- engines/loop_resurrection_engine_frozen_v1.01 — score=36 canonical=64 tags=frozen

## agent_kernel — Agent Kernel / Gilligan Neo Athena Runtime
Status: MAPPED  Required: True  Candidates: 57
Phases: Φ7, Φ8, Φ9
Operators: ψ, χ(t)
Coordinates named agents, reflection, command authority, and inter-agent symbolic behavior.

- aiweb/engines/recursive_agent_kernel — score=37 canonical=120 tags=active_or_unfrozen
- aiweb/engines/agent_reflection_engine — score=36 canonical=119 tags=active_or_unfrozen
- engines/recursive_agent_kernel — score=33 canonical=80 tags=active_or_unfrozen
- engines/agent_reflection_engine — score=32 canonical=79 tags=active_or_unfrozen
- projects/recursive_lmm_grok1/engines/recursive_agent_kernel — score=32 canonical=76 tags=active_or_unfrozen
- projects/recursive_lmm_grok1/engines/agent_reflection_engine — score=32 canonical=74 tags=active_or_unfrozen
- projects/recursive_lmm_grok1_phase2/engines/recursive_agent_kernel — score=32 canonical=70 tags=active_or_unfrozen
- projects/recursive_lmm_grok1_phase2/engines/agent_reflection_engine — score=31 canonical=69 tags=active_or_unfrozen

## ui_control_panel — UI / Control Panel / Runtime Dashboard
Status: MAPPED  Required: False  Candidates: 71
Phases: Φ7, Φ8, Φ9
Operators: display, overlay
Exposes system state, phase state, control surfaces, overlays, dashboard logic, and user-facing instrumentation.

- aiweb/engines/control_panel_ui_engine_v1.02 — score=43 canonical=134 tags=active_or_unfrozen
- aiweb/engines/control_panel_ui_engine — score=42 canonical=123 tags=active_or_unfrozen
- engines/control_panel_ui_engine_v1.02 — score=39 canonical=94 tags=active_or_unfrozen
- engines/control_panel_ui_engine — score=38 canonical=83 tags=active_or_unfrozen
- aiweb/symbolic_layers/glyph_ui_overlay — score=38 canonical=38 tags=active_or_unfrozen
- symbolic_layers/glyph_ui_overlay — score=38 canonical=38 tags=active_or_unfrozen
- aiweb/engines/control_panel_ui_engine_frozen_v1.02 — score=34 canonical=114 tags=frozen
- aiweb/engines/control_panel_ui_engine_frozen_v1.01 — score=33 canonical=103 tags=frozen

## ledger_provenance — Ledger / Contribution / Provenance Economy
Status: MAPPED  Required: False  Candidates: 16
Phases: Φ1, Φ6, Φ7, Φ8, Φ9
Operators: proof_hash, ledger
Tracks proof, contribution, tokenization, receipts, audit trails, and source-bound ownership logic.

- aiweb/engines/compute_contribution_engine — score=36 canonical=119 tags=active_or_unfrozen
- engines/compute_contribution_engine — score=32 canonical=79 tags=active_or_unfrozen
- projects/recursive_lmm_grok1/engines/compute_contribution_engine — score=32 canonical=74 tags=active_or_unfrozen
- projects/recursive_lmm_grok1_phase2/engines/compute_contribution_engine — score=31 canonical=69 tags=active_or_unfrozen
- aiweb/runtime_wrappers/contribution_ledger_stack — score=28 canonical=37 tags=active_or_unfrozen
- runtime_wrappers/contribution_ledger_stack — score=28 canonical=37 tags=active_or_unfrozen
- aiweb/engines/contribution_dashboard_engine — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/engines/compute_contribution_engine_frozen_v1 — score=27 canonical=99 tags=frozen

## policy_failsafe — Policy / Failsafe / Access Boundary
Status: MAPPED  Required: True  Candidates: 24
Phases: Φ4, Φ5, Φ6, Φ7
Operators: policy, failsafe
Defines runtime law, access boundaries, safety refusal, naming policy, and non-destructive enforcement.

- projects/recursive_lmm_grok1/engines/trust_guard — score=31 canonical=66 tags=active_or_unfrozen
- projects/recursive_lmm_grok1_phase2/engines/trust_guard — score=31 canonical=66 tags=active_or_unfrozen
- aiweb/engines/admin_override_console — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/engines/failsafe_manager — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/engines/symbolic_policy_engine — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/engines/naming_engine — score=26 canonical=119 tags=active_or_unfrozen
- engines/admin_override_console — score=23 canonical=80 tags=active_or_unfrozen
- engines/failsafe_manager — score=23 canonical=80 tags=active_or_unfrozen

## runtime_wrapper — Runtime Wrapper / Integration Harness
Status: MAPPED  Required: False  Candidates: 68
Phases: Φ1, Φ7, Φ8, Φ9
Operators: wrapper
Wraps engines into executable demos, dashboards, protoforge runtime folders, test harnesses, and launch surfaces.

- runtime_wrappers/protoforge — score=28 canonical=36 tags=active_or_unfrozen
- aiweb/runtime_wrappers/protoforge — score=28 canonical=35 tags=active_or_unfrozen
- aiweb/engines/core_stack_breather — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/engines/install_onboarding_engine — score=27 canonical=120 tags=active_or_unfrozen
- aiweb/runtime_wrappers/protoforge_v1.04_db_enabled — score=26 canonical=60 tags=active_or_unfrozen
- runtime_wrappers/Protoforge_v2.01 — score=26 canonical=60 tags=active_or_unfrozen
- runtime_wrappers/protoforge_v1.04_db_enabled — score=26 canonical=60 tags=active_or_unfrozen
- runtime_wrappers/protoforge_dashboard_runtime_v2.0 — score=25 canonical=54 tags=active_or_unfrozen
