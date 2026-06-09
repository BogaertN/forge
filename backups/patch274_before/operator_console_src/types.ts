export type OperatorTabId =
  | 'forge_output'
  | 'protoforge_simulations'
  | 'identity_vault'
  | 'echoforge'
  | 'rmc_memory'
  | 'rmc_deep_dry_run'
  | 'context_library'
  | 'audit_receipts'
  | 'system_status';

export interface ForgeCommandResponse {
  status: string;
  cmd?: string;
  output?: string;
}

export interface OperatorLlmBoundary {
  ui_is_authority?: boolean;
  forge_governs?: boolean;
  frontend_direct_model_access?: boolean;
  frontend_direct_shell?: boolean;
  frontend_direct_file_write?: boolean;
  executes_command?: boolean;
  executes_shell?: boolean;
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  returns_proposal_only?: boolean;
  approval_required_for_actions?: boolean;
}

export interface OperatorLlmRequestResponse {
  status: string;
  kind?: string;
  api_contract?: 'forge_operator_console_api_v1';
  endpoint?: '/api/operator/llm-request';
  request_id?: string;
  request?: string;
  created_at?: string;
  planner_called?: boolean;
  model_route?: string;
  response_text?: string;
  plan?: unknown;
  plan_validation?: unknown;
  error?: string;
  boundary?: OperatorLlmBoundary;
  dataset_growth_capture?: Record<string, unknown>;
}

export interface SeenPageItem {
  url: string;
  title?: string;
  fetched_at?: string;
  file?: string;
}

export interface PageCaptureBoundary {
  ui_is_authority?: boolean;
  forge_governs?: boolean;
  executes_command?: boolean;
  executes_shell?: boolean;
  calls_llm?: boolean;
  writes_files?: boolean;
  write_scope?: string;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
}

export interface PageCaptureResponse {
  status: string;
  endpoint?: '/api/read-page';
  url?: string;
  title?: string;
  text_preview?: string;
  text_length?: number;
  fetched_at?: string;
  file?: string;
  error?: string;
  boundary?: PageCaptureBoundary;
}

export interface PageCaptureRecord {
  id: string;
  url: string;
  status: string;
  title?: string;
  text_preview?: string;
  fetched_at?: string;
  file?: string;
  error?: string;
}

export interface PatchWorkflowFileSummary {
  filename?: string;
  relative_path?: string;
  directory?: string;
  modified_at?: string;
  size_bytes?: number;
  kind?: string;
  preview?: string;
  error?: string;
}

export interface PatchWorkflowDirectorySummary {
  path: string;
  exists: boolean;
  files_found: number;
  recent_files: PatchWorkflowFileSummary[];
  error?: string;
}

export interface PatchWorkflowCommandSpec {
  command: string;
  browser_safe: boolean;
  browser_gated: boolean;
  available_in_browser_bridge: boolean;
  description?: string;
  gate?: string;
}

export interface PatchWorkflowCommandGroup {
  group: string;
  description: string;
  commands: PatchWorkflowCommandSpec[];
}

export interface PatchWorkflowResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  endpoint: '/api/operator/patch-workflow';
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  calls_llm: boolean;
  writes_files: boolean;
  identity_vault_write: boolean;
  rmc_live_memory_write: boolean;
  summary: {
    proposed_patches_found: number;
    apply_plans_found: number;
    rollback_entries_found: number;
    command_groups: number;
    next_patch: string;
  };
  directories: Record<string, PatchWorkflowDirectorySummary>;
  command_groups: PatchWorkflowCommandGroup[];
  recommended_sequence: string[];
  boundary: {
    ui_is_authority: boolean;
    forge_governs: boolean;
    read_only_inventory: boolean;
    executes_command: boolean;
    executes_shell: boolean;
    calls_llm: boolean;
    writes_files: boolean;
    identity_vault_write: boolean;
    rmc_live_memory_write: boolean;
    approval_required_for_actions: boolean;
  };
}

export interface AuditReceiptFileSummary {
  filename?: string;
  relative_path?: string;
  directory?: string;
  modified_at?: string;
  size_bytes?: number;
  kind?: string;
  preview?: string;
  error?: string;
}

export interface AuditReceiptDirectorySummary {
  path: string;
  exists: boolean;
  files_found: number;
  recent_files: AuditReceiptFileSummary[];
  error?: string;
}

export interface AuditReceiptsResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  endpoint: '/api/operator/audit-receipts';
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  calls_llm: boolean;
  writes_files: boolean;
  identity_vault_write: boolean;
  rmc_live_memory_write: boolean;
  summary: {
    audit_log_exists: boolean;
    audit_lines_total: number;
    audit_tail_lines: number;
    audit_size_bytes: number;
    receipt_directories: number;
    receipt_files_found: number;
    next_patch: string;
  };
  audit: {
    path: string;
    exists: boolean;
    size_bytes: number;
    line_count: number;
    tail: string[];
  };
  receipt_directories: Record<string, AuditReceiptDirectorySummary>;
  recommended_sequence: string[];
  boundary: {
    ui_is_authority: boolean;
    forge_governs: boolean;
    read_only_inventory: boolean;
    executes_command: boolean;
    executes_shell: boolean;
    calls_llm: boolean;
    writes_files: boolean;
    identity_vault_write: boolean;
    rmc_live_memory_write: boolean;
    approval_required_for_actions: boolean;
  };
}

export interface ApiBoundary {
  executes_command?: boolean;
  executes_simulation?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  adds_forge_commands?: boolean;
}

export interface ApiEndpointSpec {
  method: 'GET' | 'POST';
  path: string;
  mode: string;
}

export interface OperatorApiContract {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  version: string;
  read_only_contract: boolean;
  endpoints: ApiEndpointSpec[];
  forbidden: string[];
}

export interface ForgeStatusResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  read_only: boolean;
  source: string;
  data: Record<string, unknown>;
  boundary: ApiBoundary;
}

export interface AuditTailResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  read_only: boolean;
  audit_log: string;
  max_lines: number;
  lines: string[];
  boundary: ApiBoundary;
}

export interface ProtoForgeSummary {
  service_verdict?: string;
  service_ok?: boolean;
  contract_path?: string;
  contract_version?: string;
  implementation_root?: string;
  allowed_types?: string[];
  latest_plan_id?: string;
  latest_plan_type?: string;
  latest_run_id?: string;
  latest_run_ok?: boolean;
  approved_execution_only?: boolean;
  substrate_verdict?: string;
  client_mode?: string;
  steps_recorded?: number | string;
  steps_requested?: number | string;
  fell_downward?: boolean | string;
  initial_z?: number | string;
  final_z?: number | string;
  artifact_files?: string[];
  artifact_manifest_version?: string;
  result_hash?: string;
  result_file_sha256?: string;
  identity_vault_written?: boolean;
  rmc_live_memory_written?: boolean;
  shell_used?: boolean;
}

export interface ProtoForgeReportsResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  identity_vault_write: boolean;
  rmc_live_memory_write: boolean;
  report_dir: string;
  summary: ProtoForgeSummary;
  reports: Record<string, unknown>;
}

export interface ProtoForgeTraceSummary {
  run_id?: string;
  artifact_manifest_version?: string;
  result_hash?: string;
  result_file_sha256?: string;
  client_mode?: string;
  steps_recorded?: number | string;
  steps_requested?: number | string;
  initial_z?: number | string;
  final_z?: number | string;
  fell_downward?: boolean | string;
  trace_step_count?: number;
  artifact_files?: string[];
}

export interface ProtoForgeTraceArtifact {
  ok: boolean;
  exists: boolean;
  path: string;
  data?: unknown;
  error?: string;
}

export interface ProtoForgeTraceArtifacts {
  state_trace?: ProtoForgeTraceArtifact;
  scenario?: ProtoForgeTraceArtifact;
  metrics?: ProtoForgeTraceArtifact;
  result?: ProtoForgeTraceArtifact;
}

export interface ProtoForgeTraceResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  endpoint: '/api/protoforge/trace/latest';
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  identity_vault_write: boolean;
  rmc_live_memory_write: boolean;
  summary: ProtoForgeTraceSummary;
  artifacts: ProtoForgeTraceArtifacts;
}

export interface IdentityVaultRootStatus {
  path: string;
  exists: boolean;
  is_dir: boolean;
}

export interface IdentityVaultAgentSummary {
  agent_id: string;
  path: string;
  has_profile_json: boolean;
  has_state_json: boolean;
  has_permissions_json: boolean;
}

export interface IdentityVaultCommandStatus {
  command: string;
  present_in_main: boolean;
}

export interface IdentityVaultReportSummary {
  ok: boolean;
  exists?: boolean;
  path?: string;
  filename?: string;
  mtime?: number;
  kind?: string;
  error?: string;
  summary?: Record<string, unknown>;
}

export interface IdentityVaultStatusResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  endpoint: '/api/identity-vault/status';
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  identity_vault_write: boolean;
  identity_db_write: boolean;
  secret_reads: boolean;
  autonomous_execution: boolean;
  rmc_live_memory_write: boolean;
  summary: {
    candidate_roots_checked: number;
    agent_dirs_found: number;
    reports_found: number;
    commands_checked: number;
  };
  roots: IdentityVaultRootStatus[];
  agents: IdentityVaultAgentSummary[];
  commands: IdentityVaultCommandStatus[];
  reports: IdentityVaultReportSummary[];
  boundary: {
    ui_is_authority: boolean;
    forge_governs: boolean;
    identity_vault_authorizes: boolean;
    frontend_direct_write: boolean;
  };
}

export interface CoreFeatureInventoryItem {
  id: string;
  label: string;
  original_source: string;
  production_target: string;
  current_status: string;
  needed: string[];
  safe_next_patch: string;
}

export interface ProductionPanelInventoryItem {
  tab: string;
  status: string;
  priority: string;
}

export interface BrowserCommandBridgeInventory {
  safe: string[];
  gated: string[];
  safe_count: number;
  gated_count: number;
  error?: string;
}

export interface OperatorCoreInventoryResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  endpoint: '/api/operator/core-inventory';
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  calls_llm: boolean;
  writes_files: boolean;
  identity_vault_write: boolean;
  rmc_live_memory_write: boolean;
  summary: {
    safe_browser_commands: number;
    gated_browser_commands: number;
    features_tracked: number;
    production_panels_tracked: number;
    next_patch: string;
  };
  browser_command_bridge: BrowserCommandBridgeInventory;
  original_terminus_features: CoreFeatureInventoryItem[];
  production_panels: ProductionPanelInventoryItem[];
  recommended_sequence: string[];
  boundary: {
    ui_is_authority: boolean;
    forge_governs: boolean;
    model_can_reason_but_forge_verifies: boolean;
    frontend_direct_shell: boolean;
    frontend_direct_file_write: boolean;
  };
}

export interface OperatorOutputSlot {
  id: string;
  kind: string;
  title: string;
  status: string;
  body: string;
}

export interface OperatorOutputStateResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  endpoint: '/api/operator/output-state';
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  calls_llm: boolean;
  writes_files: boolean;
  identity_vault_write: boolean;
  rmc_live_memory_write: boolean;
  summary: {
    safe_browser_commands: number;
    gated_browser_commands: number;
    audit_lines: number;
    output_slots: number;
    next_patch: string;
  };
  forge_status: ForgeStatusResponse;
  audit_tail: AuditTailResponse;
  browser_command_bridge: BrowserCommandBridgeInventory;
  output_slots: OperatorOutputSlot[];
  core_inventory_summary: Record<string, unknown>;
  recommended_sequence: string[];
  boundary: {
    ui_is_authority: boolean;
    forge_governs: boolean;
    model_can_reason_but_forge_verifies: boolean;
    frontend_direct_shell: boolean;
    frontend_direct_file_write: boolean;
    command_execution_enabled: boolean;
    llm_execution_enabled: boolean;
    llm_request_bridge_enabled?: boolean;
    llm_direct_tool_execution_enabled?: boolean;
    llm_shell_enabled?: boolean;
    llm_file_write_enabled?: boolean;
    page_capture_enabled?: boolean;
    page_capture_write_scope?: string;
    page_capture_identity_vault_write?: boolean;
    page_capture_rmc_live_memory_write?: boolean;
    patch_workflow_enabled?: boolean;
    patch_workflow_read_only?: boolean;
    patch_workflow_executes_command?: boolean;
    patch_workflow_writes_files?: boolean;
    patch_workflow_identity_vault_write?: boolean;
    patch_workflow_rmc_live_memory_write?: boolean;
    audit_receipts_enabled?: boolean;
    audit_receipts_read_only?: boolean;
    audit_receipts_executes_command?: boolean;
    audit_receipts_writes_files?: boolean;
    audit_receipts_identity_vault_write?: boolean;
    audit_receipts_rmc_live_memory_write?: boolean;
    left_rail_command_launcher_enabled?: boolean;
    left_rail_uses_existing_command_bridge?: boolean;
    left_rail_direct_shell?: boolean;
    left_rail_direct_file_write?: boolean;
    left_rail_identity_vault_write?: boolean;
    left_rail_rmc_live_memory_write?: boolean;
    left_rail_gated_actions_require_operator_click?: boolean;

    right_rail_runtime_status_enabled?: boolean;
    right_rail_runtime_status_read_only?: boolean;
    right_rail_uses_existing_read_only_apis?: boolean;
    right_rail_executes_command?: boolean;
    right_rail_direct_shell?: boolean;
    right_rail_direct_file_write?: boolean;
    right_rail_identity_vault_write?: boolean;
    right_rail_rmc_live_memory_write?: boolean;
  };
}

export interface ForgeCommandRunRecord {
  id: string;
  command: string;
  gate?: string;
  status: string;
  output: string;
  created_at: string;
  safe_mode: 'safe' | 'gated' | 'unknown';
}

export interface ForgeLlmRequestRecord {
  id: string;
  request: string;
  status: string;
  kind: string;
  response_text: string;
  created_at: string;
  boundary?: OperatorLlmBoundary;
  dataset_growth_capture?: Record<string, unknown>;
}


export interface RmcDatasetGrowthResponse {
  status: string;
  api_contract?: 'forge_operator_console_api_v1';
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  current_patch?: string;
  next_patch?: string;
  dataset_root?: string;
  counts?: Record<string, number>;
  growth_counts?: Record<string, number>;
  canonical_reference_counts?: Record<string, number>;
  readiness?: Record<string, unknown>;
  coverage_checks?: Record<string, unknown>;
  growth_law?: Record<string, unknown>;
  boundary?: Record<string, unknown>;
  writes_files?: boolean;
  approved_output?: boolean;
  error?: string;
}


export interface RmcMemoryFileSummary {
  filename?: string;
  relative_path?: string;
  directory?: string;
  modified_at?: string;
  size_bytes?: number;
  kind?: string;
  preview?: string;
  error?: string;
}

export interface RmcMemoryDirectorySummary {
  label: string;
  path: string;
  exists: boolean;
  is_dir: boolean;
  files_found: number;
  recent_files: RmcMemoryFileSummary[];
}

export interface RmcMemorySymbolicEntry {
  source_file?: string;
  chunk_id?: string;
  corpus_id?: string;
  rpmc_phase_tags?: string;
  symbolic_operators?: string;
  memory_role?: string;
  symbolic_signature?: string;
  chunk_preview?: string;
}

export interface RmcMemoryReceiptRecord {
  receipt_id?: string;
  timestamp?: string;
  corpus_id?: string;
  filename?: string;
  source_filename?: string;
  corpus_folder?: string;
  chunk_count_verified?: number | string;
  collection?: string;
  verification_ok?: boolean | null;
  symbolic_map_path?: string;
  collection_manifest_path?: string;
}

export interface RmcMemoryStatusResponse {
  status: string;
  api_contract: 'forge_operator_console_api_v1';
  endpoint: '/api/rmc/memory-status';
  mode: string;
  read_only: boolean;
  executes_command: boolean;
  executes_simulation: boolean;
  calls_llm: boolean;
  writes_files: boolean;
  identity_vault_write: boolean;
  rmc_live_memory_write: boolean;
  summary: {
    context_library_exists: boolean;
    collection: string;
    collection_total_chunks: number | string;
    receipt_files: number;
    manifest_files: number;
    symbolic_map_files: number;
    symbolic_chunks_scanned: number;
    unique_corpus_ids_scanned: number;
    chroma_db_present: boolean;
    legacy_chroma_db_present: boolean;
    legacy_chroma_db_policy: string;
    next_patch: string;
  };
  directories: Record<string, RmcMemoryDirectorySummary>;
  latest_manifest: Record<string, unknown>;
  latest_receipt: RmcMemoryReceiptRecord;
  receipt_summary: {
    receipts_scanned: number;
    unique_corpus_ids: number;
    corpus_ids_recent_first: string[];
    chunk_total_verified_scanned: number;
    verification_failures_scanned: number;
    latest_receipts: RmcMemoryReceiptRecord[];
  };
  symbolic_summary: {
    maps_scanned: number;
    chunks_scanned: number;
    phase_counts: Record<string, number>;
    operator_counts: Record<string, number>;
    memory_role_counts: Record<string, number>;
    signal_counts: Record<string, number>;
    recent_symbolic_entries: RmcMemorySymbolicEntry[];
  };
  doctrine_model: {
    runtime_name: string;
    memory_unit: string;
    active_store: string;
    cold_store: string;
    phase_stack: string[];
    operators_tracked: string[];
    future_output_modalities: string[];
  };
  recommended_sequence: string[];
  boundary: {
    ui_is_authority: boolean;
    forge_governs: boolean;
    read_only_inventory: boolean;
    executes_command: boolean;
    executes_shell: boolean;
    calls_llm: boolean;
    writes_files: boolean;
    identity_vault_write: boolean;
    rmc_live_memory_write: boolean;
    queries_chroma_db: boolean;
    reads_db_files: boolean;
    ingests_documents: boolean;
    resurrects_memory: boolean;
    generates_cymatics: boolean;
    approval_required_for_actions: boolean;
  };
}


export interface RmcMemoryObjectResponse {
  status: string;
  api_contract?: 'forge_operator_console_api_v1';
  endpoint: '/api/rmc/memory-object';
  mode?: string;
  read_only: boolean;
  object_kind?: string;
  error?: string;
  request?: Record<string, string>;
  selector_note?: string;
  file?: {
    filename?: string;
    relative_path?: string;
    absolute_path?: string;
    size_bytes?: number;
    modified_at?: string;
    suffix?: string;
  };
  manifest_trace?: Record<string, unknown>;
  selected_symbolic_entry?: Record<string, unknown> | null;
  json_data?: unknown;
  text_preview?: string;
  recommended_sequence?: string[];
  glyph_codex_aligned?: boolean;
  audible_browser_transposition?: boolean;
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: {
    ui_is_authority?: boolean;
    forge_governs?: boolean;
    read_only_object_view?: boolean;
    executes_command?: boolean;
    executes_shell?: boolean;
    calls_llm?: boolean;
    writes_files?: boolean;
    identity_vault_write?: boolean;
    rmc_live_memory_write?: boolean;
    queries_chroma_db?: boolean;
    reads_db_files?: boolean;
    ingests_documents?: boolean;
    resurrects_memory?: boolean;
    generates_cymatics?: boolean;
  };
}


export interface RmcPhaseNode {
  phase: string;
  index: number;
  role: string;
  frequency_hz: number;
  frequency_model?: string;
  harmonic_signature?: string;
  observed_count: number;
  normalized_observation: number;
  display_amplitude: number;
  is_observed: boolean;
}

export interface RmcPhaseEdge {
  from: string;
  to: string;
  law: string;
}

export interface RmcPhasePreviewResponse {
  status: string;
  api_contract?: 'forge_operator_console_api_v1';
  endpoint: '/api/rmc/phase-preview';
  mode?: string;
  read_only: boolean;
  error?: string;
  source_endpoint?: string;
  source_object_kind?: string;
  source_file?: Record<string, unknown>;
  source_manifest_trace?: Record<string, unknown>;
  preview_seed?: Record<string, unknown>;
  phase_model?: {
    phase_stack?: string[];
    base_cycle_hz?: number;
    phase_step_hz?: number;
    model_note?: string;
    canonical_order_required?: boolean;
    no_phase_skip_policy?: boolean;
  };
  phase_counts?: Record<string, number>;
  phase_nodes?: RmcPhaseNode[];
  phase_edges?: RmcPhaseEdge[];
  frequency_preview?: {
    observed_total?: number;
    observed_phases?: string[];
    dominant_phase?: string;
    dormant_phases?: string[];
    audio_generated?: boolean;
    cymatic_geometry_generated?: boolean;
    render_policy?: string;
  };
  recommended_sequence?: string[];
  glyph_codex_aligned?: boolean;
  audible_browser_transposition?: boolean;
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: {
    ui_is_authority?: boolean;
    forge_governs?: boolean;
    read_only_phase_preview?: boolean;
    uses_verified_manifest_trace?: boolean;
    executes_command?: boolean;
    executes_shell?: boolean;
    calls_llm?: boolean;
    writes_files?: boolean;
    identity_vault_write?: boolean;
    rmc_live_memory_write?: boolean;
    queries_chroma_db?: boolean;
    reads_db_files?: boolean;
    ingests_documents?: boolean;
    resurrects_memory?: boolean;
    generates_audio?: boolean;
    generates_cymatics?: boolean;
  };
}


export interface RmcCymaticGeometryNode {
  phase: string;
  index: number;
  role?: string;
  harmonic_signature?: string;
  frequency_hz: number;
  observed_count?: number;
  normalized_observation?: number;
  amplitude: number;
  radius: number;
  angle_degrees: number;
  x: number;
  y: number;
  is_observed?: boolean;
  glyph?: string;
  color_hex?: string;
  code_identifier?: string;
  function_hook?: string;
  motion_tag?: string;
}

export interface RmcCymaticGeometryEdge {
  from: string;
  to: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  law?: string;
}

export interface RmcCymaticTone {
  phase: string;
  frequency_hz: number;
  symbolic_frequency_hz?: number;
  playback_frequency_hz?: number;
  playback_transpose_multiplier?: number;
  start_seconds: number;
  duration_seconds: number;
  gain: number;
  waveform: OscillatorType;
}

export interface RmcCymaticPreviewResponse {
  status: string;
  api_contract?: 'forge_operator_console_api_v1';
  endpoint: '/api/rmc/cymatic-preview';
  mode?: string;
  read_only: boolean;
  error?: string;
  source_endpoint?: string;
  source_object_kind?: string;
  source_file?: Record<string, unknown>;
  source_preview_seed?: Record<string, unknown>;
  source_phase_model?: Record<string, unknown>;
  source_frequency_preview?: Record<string, unknown>;
  geometry_model?: Record<string, unknown>;
  geometry_nodes?: RmcCymaticGeometryNode[];
  geometry_edges?: RmcCymaticGeometryEdge[];
  tone_plan?: {
    browser_audio_preview_available?: boolean;
    backend_audio_generated?: boolean;
    audio_file_written?: boolean;
    user_gesture_required?: boolean;
    audible_transposition_enabled?: boolean;
    playback_transpose_multiplier?: number;
    playback_note?: string;
    tone_sequence?: RmcCymaticTone[];
    tone_policy?: string;
  };
  recommended_sequence?: string[];
  glyph_codex_aligned?: boolean;
  audible_browser_transposition?: boolean;
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: {
    ui_is_authority?: boolean;
    forge_governs?: boolean;
    read_only_cymatic_preview?: boolean;
    uses_verified_phase_preview?: boolean;
    executes_command?: boolean;
    executes_shell?: boolean;
    calls_llm?: boolean;
    writes_files?: boolean;
    identity_vault_write?: boolean;
    rmc_live_memory_write?: boolean;
    queries_chroma_db?: boolean;
    reads_db_files?: boolean;
    ingests_documents?: boolean;
    resurrects_memory?: boolean;
    generates_audio_file?: boolean;
    generates_image_file?: boolean;
    renders_svg_in_browser?: boolean;
    browser_audio_preview_only?: boolean;
    audible_browser_transposition?: boolean;
    glyph_codex_aligned?: boolean;
  };
}


export interface RmcResonanceOutputGateResponse {
  status: string;
  api_contract?: 'forge_operator_console_api_v1';
  endpoint: '/api/rmc/resonance-output-gate';
  mode?: string;
  read_only: boolean;
  error?: string;
  source_endpoint?: string;
  source_object_kind?: string;
  source_file?: Record<string, unknown>;
  source_preview_seed?: Record<string, unknown>;
  glyph_codex_aligned?: boolean;
  audible_browser_transposition?: boolean;
  output_gate?: {
    gate_name?: string;
    gate_state?: string;
    write_enabled?: boolean;
    export_enabled?: boolean;
    receipt_write_enabled?: boolean;
    persistent_output_allowed?: boolean;
    operator_approval_required?: boolean;
  };
  receipt_preview?: Record<string, unknown>;
  artifact_plan?: Record<string, unknown>;
  recommended_sequence?: string[];
  receipt_written?: boolean;
  artifact_exported?: boolean;
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: {
    ui_is_authority?: boolean;
    forge_governs?: boolean;
    read_only_gate_preview?: boolean;
    uses_verified_cymatic_preview?: boolean;
    executes_command?: boolean;
    executes_shell?: boolean;
    calls_llm?: boolean;
    writes_files?: boolean;
    identity_vault_write?: boolean;
    rmc_live_memory_write?: boolean;
    generates_audio_file?: boolean;
    generates_image_file?: boolean;
    exports_artifact?: boolean;
    writes_receipt?: boolean;
    approval_required_for_persistent_output?: boolean;
  };
}


export interface RmcPhaseParserResponse {
  status: string;
  api_contract?: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  current_patch?: string;
  next_patch?: string;
  input_event?: Record<string, unknown>;
  phase_state?: {
    phase_primary?: string;
    phase_primary_role?: string;
    phase_secondary?: string[];
    phase_path_hypothesis?: string[];
    confidence?: number;
    phase_candidates?: Array<Record<string, unknown>>;
    transition_warnings?: Array<Record<string, unknown>>;
    routing?: string[];
    projection_warning?: string;
  };
  drift_foundation_anchor?: Record<string, unknown>;
  recommended_sequence?: string[];
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: Record<string, unknown>;
  error?: string;
}


export interface RmcDriftClassRecord {
  drift_key?: string;
  drift_type?: string;
  plain_meaning?: string;
  score?: number;
  severity?: string;
  evidence?: string[];
  projection_rule?: string;
  correction_required?: boolean;
}

export interface RmcDriftAnalyzerResponse {
  status: string;
  api_contract?: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  current_patch?: string;
  next_patch?: string;
  drift_report_id?: string;
  source_phase_parser?: RmcPhaseParserResponse | Record<string, unknown>;
  drift_taxonomy_anchor?: Record<string, unknown>;
  drift_classes?: RmcDriftClassRecord[];
  epsilon_s?: Record<string, unknown>;
  phase_drift?: Record<string, unknown>;
  chi_t?: Record<string, unknown>;
  circuit_breaker?: Record<string, unknown>;
  projection_status?: string;
  recommended_action?: string;
  recommended_sequence?: string[];
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: Record<string, unknown>;
  error?: string;
}


export interface RmcCandidateRecord {
  candidate_id?: string;
  title?: string;
  candidate_type?: string;
  meaning_state?: string;
  phase_target?: string;
  drift_posture?: string;
  confidence?: number;
  allowed_to_continue_to_scoring?: boolean;
  projection_allowed?: boolean;
  memory_write_allowed?: boolean;
  reason?: string;
  required_limitations?: string[];
  next_required_gate?: string;
}

export interface RmcCandidateConclusionResponse {
  status: string;
  api_contract?: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  current_patch?: string;
  next_patch?: string;
  candidate_set_id?: string;
  source_drift_report?: RmcDriftAnalyzerResponse | Record<string, unknown>;
  candidate_generation_status?: Record<string, unknown>;
  candidate_set?: RmcCandidateRecord[];
  selected_candidate_preview?: RmcCandidateRecord | null;
  dry_run_trace?: Record<string, unknown>;
  recommended_sequence?: string[];
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: Record<string, unknown>;
  error?: string;
}


export interface RmcCoherenceCandidateScore {
  candidate_id?: string;
  title?: string;
  candidate_type?: string;
  phase_target?: string;
  drift_posture?: string;
  input_confidence?: number;
  epsilon_s?: number;
  coherence_score?: number;
  status?: string;
  allowed_to_continue_to_manifest_dry_run?: boolean;
  projection_allowed?: boolean;
  final_language_allowed?: boolean;
  memory_write_allowed?: boolean;
  correction_gate?: Record<string, unknown>;
  naming_gate?: Record<string, unknown>;
  projection_gate?: Record<string, unknown>;
  cold_storage_gate?: Record<string, unknown>;
  manifest_gate?: Record<string, unknown>;
  required_limitations?: string[];
  score_components?: Record<string, unknown>;
  math_terms?: Record<string, unknown>;
  formal_math_binding?: string;
}

export interface RmcCoherenceGateResponse {
  status: string;
  api_contract?: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  current_patch?: string;
  next_patch?: string;
  coherence_run_id?: string;
  source_candidate_conclusion?: RmcCandidateConclusionResponse | Record<string, unknown>;
  candidate_scores?: RmcCoherenceCandidateScore[];
  selected_scored_candidate_preview?: RmcCoherenceCandidateScore | null;
  formal_math_binding?: Record<string, unknown>;
  gate_summary?: Record<string, unknown>;
  correction_naming_contract?: Record<string, unknown>;
  recommended_sequence?: string[];
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: Record<string, unknown>;
  error?: string;
}


export interface RmcManifestCompilerResponse {
  status: string;
  api_contract?: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  current_patch?: string;
  next_patch?: string;
  manifest_run_id?: string;
  source_coherence_gate?: RmcCoherenceGateResponse | Record<string, unknown>;
  engine_boundary?: Record<string, unknown>;
  manifest_schema_contract?: Record<string, unknown>;
  manifest_preflight?: Record<string, unknown>;
  manifest_packet?: Record<string, unknown> | null;
  manifest_compilation_allowed?: boolean;
  approved_output?: boolean;
  projection_allowed?: boolean;
  final_language_allowed?: boolean;
  memory_write_allowed?: boolean;
  recommended_sequence?: string[];
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: Record<string, unknown>;
  error?: string;
}


export interface RmcCompilerStageStatus {
  stage: string;
  implemented: boolean;
  status: string;
  evidence: string;
  next_action: string;
}

export interface RmcCompilerContractResponse {
  status: string;
  api_contract?: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  current_patch?: string;
  next_patch?: string;
  schema_fields?: Record<string, string[]>;
  compiler_contract?: Record<string, unknown>;
  compiler_stages?: RmcCompilerStageStatus[];
  summary?: Record<string, unknown>;
  source_surface_status?: Record<string, boolean>;
  recommended_sequence?: string[];
  writes_files?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  boundary?: Record<string, unknown>;
  error?: string;
}

export type AiwebOsLifecycleAction = 'exit_window' | 'restart' | 'shutdown';

export interface AiwebOsLifecycleBoundary {
  ui_is_authority?: boolean;
  forge_governs?: boolean;
  browser_executes_shell?: boolean;
  browser_executes_arbitrary_command?: boolean;
  backend_uses_fixed_allowlist?: boolean;
  requires_preview_before_confirm?: boolean;
  requires_exact_confirmation_token?: boolean;
  identity_vault_write?: boolean;
  rmc_live_memory_write?: boolean;
  chroma_write?: boolean;
  llm_call?: boolean;
  arbitrary_shell?: boolean;
}

export interface AiwebOsStatusResponse {
  status: string;
  endpoint?: string;
  mode?: string;
  created_at_utc?: string;
  read_only?: boolean;
  appctl_status?: {
    ok?: boolean;
    status?: string;
    returncode?: number;
    stdout?: string;
    stderr?: string;
    error?: string;
    path?: string;
    command_class?: string;
  };
  summary?: Record<string, unknown>;
  paths?: Record<string, string>;
  boundary?: AiwebOsLifecycleBoundary;
}

export interface AiwebOsLogFile {
  name: string;
  path: string;
  size_bytes: number;
  tail_lines: string[];
}

export interface AiwebOsLogsResponse {
  status: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  writes_files?: boolean;
  executes_command?: boolean;
  root?: string;
  max_lines?: number;
  file_count?: number;
  files?: AiwebOsLogFile[];
  boundary?: AiwebOsLifecycleBoundary;
}

export interface AiwebOsLifecycleManifestRoute {
  route_key: string;
  method: 'GET';
  path: string;
  action: string;
  requires_confirmation: boolean;
  confirmation_token?: string;
}

export interface AiwebOsLifecycleManifestResponse {
  status: string;
  endpoint?: string;
  mode?: string;
  read_only?: boolean;
  routes?: AiwebOsLifecycleManifestRoute[];
  boundary?: AiwebOsLifecycleBoundary;
}

export interface AiwebOsLifecyclePreviewResponse {
  status: string;
  endpoint?: string;
  mode?: string;
  action?: AiwebOsLifecycleAction;
  label?: string;
  requires_confirmation?: boolean;
  confirmation_token?: string;
  executes_now?: boolean;
  effects?: string[];
  boundary?: AiwebOsLifecycleBoundary;
}

export interface AiwebOsLifecycleConfirmResponse {
  status: string;
  endpoint?: string;
  mode?: string;
  action?: AiwebOsLifecycleAction;
  reason?: string;
  expected_token?: string;
  supplied_token_present?: boolean;
  executed?: boolean;
  close_operator_window_in_browser?: boolean;
  scheduled_result?: Record<string, unknown>;
  message?: string;
  boundary?: AiwebOsLifecycleBoundary;
}
