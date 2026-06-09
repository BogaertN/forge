import type {
  AuditReceiptsResponse,
  AuditTailResponse,
  ForgeCommandResponse,
  ForgeStatusResponse,
  IdentityVaultStatusResponse,
  OperatorApiContract,
  OperatorCoreInventoryResponse,
  PageCaptureResponse,
  PatchWorkflowResponse,
  OperatorLlmRequestResponse,
  OperatorOutputStateResponse,
  ProtoForgeReportsResponse,
  SeenPageItem,
  ProtoForgeTraceResponse,
  RmcMemoryStatusResponse,
  RmcMemoryObjectResponse,
  RmcPhasePreviewResponse,
  RmcCymaticPreviewResponse,
  RmcResonanceOutputGateResponse,
  RmcCompilerContractResponse,
  RmcPhaseParserResponse,
  RmcDriftAnalyzerResponse,
  RmcCandidateConclusionResponse,
  RmcCoherenceGateResponse,
  RmcManifestCompilerResponse,
  RmcDatasetGrowthResponse,
  AiwebOsStatusResponse,
  AiwebOsLogsResponse,
  AiwebOsLifecycleManifestResponse,
  AiwebOsLifecyclePreviewResponse,
  AiwebOsLifecycleConfirmResponse,
  AiwebOsLifecycleAction,
  AiwebOsBuildManifestResponse,
} from './types';

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function getOperatorApiContract(): Promise<OperatorApiContract> {
  const response = await fetch('/api/operator/contract');
  return readJson<OperatorApiContract>(response);
}

export async function getForgeStatus(): Promise<ForgeStatusResponse> {
  const response = await fetch('/api/forge/status');
  return readJson<ForgeStatusResponse>(response);
}

export async function getAuditTail(): Promise<AuditTailResponse> {
  const response = await fetch('/api/audit/tail');
  return readJson<AuditTailResponse>(response);
}

export async function getProtoForgeReports(): Promise<ProtoForgeReportsResponse> {
  const response = await fetch('/api/protoforge/reports');
  return readJson<ProtoForgeReportsResponse>(response);
}

export async function runForgeCommand(command: string, gate?: string): Promise<ForgeCommandResponse> {
  const response = await fetch('/api/command', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command, gate }),
  });
  return readJson<ForgeCommandResponse>(response);
}

export interface AskForgeOperatorOptions {
  dataset_capture?: 'capture' | 'queue' | 'none';
  dataset_capture_approval?: 'CAPTURE_RMC_LLM_TURN' | '';
}

export async function askForgeOperator(request: string, options: AskForgeOperatorOptions = {}): Promise<OperatorLlmRequestResponse> {
  const response = await fetch('/api/operator/llm-request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request, ...options }),
  });
  return readJson<OperatorLlmRequestResponse>(response);
}

export async function getProtoForgeTraceLatest(): Promise<ProtoForgeTraceResponse> {
  const response = await fetch('/api/protoforge/trace/latest');
  return readJson<ProtoForgeTraceResponse>(response);
}

export async function getIdentityVaultStatus(): Promise<IdentityVaultStatusResponse> {
  const response = await fetch('/api/identity-vault/status');
  return readJson<IdentityVaultStatusResponse>(response);
}

export async function getOperatorCoreInventory(): Promise<OperatorCoreInventoryResponse> {
  const response = await fetch('/api/operator/core-inventory');
  return readJson<OperatorCoreInventoryResponse>(response);
}

export async function getOperatorOutputState(): Promise<OperatorOutputStateResponse> {
  const response = await fetch('/api/operator/output-state');
  return readJson<OperatorOutputStateResponse>(response);
}



export async function getRmcDatasetGrowthStatus(): Promise<RmcDatasetGrowthResponse> {
  const response = await fetch('/api/rmc/dataset-growth/status');
  return readJson<RmcDatasetGrowthResponse>(response);
}

export async function getRmcDatasetGrowthCoverage(): Promise<RmcDatasetGrowthResponse> {
  const response = await fetch('/api/rmc/dataset-growth/coverage');
  return readJson<RmcDatasetGrowthResponse>(response);
}

export async function previewRmcDatasetCapture(input: string): Promise<RmcDatasetGrowthResponse> {
  const params = new URLSearchParams({ input });
  const response = await fetch(`/api/rmc/dataset-growth/capture-preview?${params.toString()}`);
  return readJson<RmcDatasetGrowthResponse>(response);
}

export async function getSeenPages(): Promise<SeenPageItem[]> {
  const response = await fetch('/api/seen-pages');
  return readJson<SeenPageItem[]>(response);
}

export async function capturePage(url: string): Promise<PageCaptureResponse> {
  const response = await fetch('/api/read-page', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  return readJson<PageCaptureResponse>(response);
}


export async function getPatchWorkflow(): Promise<PatchWorkflowResponse> {
  const response = await fetch('/api/operator/patch-workflow');
  return readJson<PatchWorkflowResponse>(response);
}

export async function getAuditReceipts(): Promise<AuditReceiptsResponse> {
  const response = await fetch('/api/operator/audit-receipts');
  return readJson<AuditReceiptsResponse>(response);
}


export async function getRmcMemoryStatus(): Promise<RmcMemoryStatusResponse> {
  const response = await fetch('/api/rmc/memory-status');
  return readJson<RmcMemoryStatusResponse>(response);
}


export interface RmcMemoryObjectRequest {
  selector?: 'latest_manifest' | 'latest_receipt' | undefined;
  path?: string | undefined;
  source_file?: string | undefined;
  chunk_id?: string | undefined;
}

export async function getRmcMemoryObject(request: RmcMemoryObjectRequest = {}): Promise<RmcMemoryObjectResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/memory-object${query ? `?${query}` : ''}`);
  return readJson<RmcMemoryObjectResponse>(response);
}


export async function getRmcPhasePreview(request: RmcMemoryObjectRequest = {}): Promise<RmcPhasePreviewResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/phase-preview${query ? `?${query}` : ''}`);
  return readJson<RmcPhasePreviewResponse>(response);
}


export async function getRmcCymaticPreview(request: RmcMemoryObjectRequest = {}): Promise<RmcCymaticPreviewResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/cymatic-preview${query ? `?${query}` : ''}`);
  return readJson<RmcCymaticPreviewResponse>(response);
}


export async function getRmcResonanceOutputGate(request: RmcMemoryObjectRequest = {}): Promise<RmcResonanceOutputGateResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/resonance-output-gate${query ? `?${query}` : ''}`);
  return readJson<RmcResonanceOutputGateResponse>(response);
}


export async function getRmcPhaseParser(request: RmcMemoryObjectRequest & { input?: string; text?: string } = {}): Promise<RmcPhaseParserResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/phase-parser${query ? `?${query}` : ''}`);
  return readJson<RmcPhaseParserResponse>(response);
}


export async function getRmcDriftAnalyzer(request: RmcMemoryObjectRequest & { input?: string; text?: string } = {}): Promise<RmcDriftAnalyzerResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/drift-analyzer${query ? `?${query}` : ''}`);
  return readJson<RmcDriftAnalyzerResponse>(response);
}


export async function getRmcCompilerContract(): Promise<RmcCompilerContractResponse> {
  const response = await fetch('/api/rmc/compiler-contract');
  return readJson<RmcCompilerContractResponse>(response);
}


export async function getRmcCandidateConclusion(request: RmcMemoryObjectRequest & { input?: string; text?: string } = {}): Promise<RmcCandidateConclusionResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/candidate-conclusion${query ? `?${query}` : ''}`);
  return readJson<RmcCandidateConclusionResponse>(response);
}


export async function getRmcCoherenceGate(request: RmcMemoryObjectRequest & { input?: string; text?: string } = {}): Promise<RmcCoherenceGateResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/coherence-gate${query ? `?${query}` : ''}`);
  return readJson<RmcCoherenceGateResponse>(response);
}

export async function getRmcManifestCompiler(request: RmcMemoryObjectRequest & { input?: string; text?: string } = {}): Promise<RmcManifestCompilerResponse> {
  const params = new URLSearchParams();
  Object.entries(request).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).length > 0) {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  const response = await fetch(`/api/rmc/manifest-compiler${query ? `?${query}` : ''}`);
  return readJson<RmcManifestCompilerResponse>(response);
}



// Patch 274 — AI.Web OS build manifest endpoint. Read-only, no shell, no writes.

export async function getAiwebOsBuildManifest(): Promise<AiwebOsBuildManifestResponse> {
  const response = await fetch('/api/aiweb-os/build-manifest');
  return readJson<AiwebOsBuildManifestResponse>(response);
}

// Patch 263S — AI.Web OS lifecycle endpoints. These functions only call
// backend-owned lifecycle routes. They do not expose shell, arbitrary command
// text, file writes, model calls, or Identity Vault/RMC mutation to the browser.
export async function getAiwebOsLifecycleManifest(): Promise<AiwebOsLifecycleManifestResponse> {
  const response = await fetch('/api/aiweb-os/lifecycle-manifest');
  return readJson<AiwebOsLifecycleManifestResponse>(response);
}

export async function getAiwebOsStatus(): Promise<AiwebOsStatusResponse> {
  const response = await fetch('/api/aiweb-os/status');
  return readJson<AiwebOsStatusResponse>(response);
}

export async function getAiwebOsLogs(lines = 120): Promise<AiwebOsLogsResponse> {
  const params = new URLSearchParams({ lines: String(lines) });
  const response = await fetch(`/api/aiweb-os/logs?${params.toString()}`);
  return readJson<AiwebOsLogsResponse>(response);
}

function lifecyclePath(action: AiwebOsLifecycleAction, stage: 'preview' | 'confirm'): string {
  const slug = action === 'exit_window' ? 'exit-window' : action;
  return `/api/aiweb-os/${slug}-${stage}`;
}

export async function previewAiwebOsLifecycleAction(action: AiwebOsLifecycleAction): Promise<AiwebOsLifecyclePreviewResponse> {
  const response = await fetch(lifecyclePath(action, 'preview'));
  return readJson<AiwebOsLifecyclePreviewResponse>(response);
}

export async function confirmAiwebOsLifecycleAction(action: AiwebOsLifecycleAction, token: string): Promise<AiwebOsLifecycleConfirmResponse> {
  const params = new URLSearchParams({ token });
  const response = await fetch(`${lifecyclePath(action, 'confirm')}?${params.toString()}`);
  return readJson<AiwebOsLifecycleConfirmResponse>(response);
}
