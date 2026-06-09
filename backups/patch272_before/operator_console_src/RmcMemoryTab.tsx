// Patch 262-UI-MemoryPanel-P6
// RMC Memory Panel Phase 2 hardening: split domain sections from the stateful panel controller.

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  fetchRouteManifest,
  getActiveLoopState,
  getChromaStatus,
  getContextDuplicates,
  getContextExportManifest,
  getContextSearchTest,
  getDatasetGrowthCoverage,
  getDatasetGrowthStatus,
  getGlyphRendererStatus,
  getLlmRendererStatus,
  getLatestMemoryWrites,
  getMemoryStatus,
  getOutputRenderer,
  getPipelineSummary,
  getPromotionPreview,
  getPromotionPromote,
  getPromotionStatus,
  getRmcNamespaces,
} from '../lib/rmc-api-client';
import {
  PROMOTION_TOKEN as PROMOTION_TOKEN_FROM_GUARDS,
  buildPromotionConfirmationPhrase as buildGuardConfirmationPhrase,
  evaluatePromotionArmState as evaluateGuardPromotionArmState,
} from '../lib/rmc-ui-guards';
import {
  makeEndpointHealth,
  summarizeEndpointHealth,
  type EndpointHealthMap,
} from '../lib/rmc-panel-health';
import type { JsonRecord } from '../lib/rmc-panel-primitives';
import {
  RmcActiveLoopSection,
  RmcBoundarySection,
  RmcContextLibrarySection,
  RmcEndpointHealthSection,
  RmcPanelShell,
  RmcPromotionSection,
  RmcRendererSection,
  RmcRouteManifestSection,
  RmcTopMetricsSection,
  type RmcPanelData,
} from '../lib/rmc-memory-sections';

const DEFAULT_INPUT = 'correct projection before naming';
const PROMOTION_TOKEN = PROMOTION_TOKEN_FROM_GUARDS;
const LOCAL_MODEL_ENDPOINT = 'http://localhost:11434/api/generate';
const LOCAL_MODEL_NAME = 'qwen3:8b';

const emptyPanelData: RmcPanelData = {
  routeManifest: null,
  memoryStatus: null,
  contextSearchTest: null,
  contextDuplicates: null,
  contextExportManifest: null,
  latestMemoryWrites: null,
  rmcNamespaces: null,
  chromaStatus: null,
  activeLoop: null,
  pipelineSummary: null,
  promotionStatus: null,
  glyphStatus: null,
  llmStatus: null,
  datasetGrowthStatus: null,
  datasetGrowthCoverage: null,
};

export function RmcMemoryTab() {
  const [input, setInput] = useState(DEFAULT_INPUT);
  const [data, setData] = useState<RmcPanelData>(emptyPanelData);
  const [endpointHealth, setEndpointHealth] = useState<EndpointHealthMap>({});
  const [lastLoadedAt, setLastLoadedAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [promotionPreview, setPromotionPreview] = useState<JsonRecord | null>(null);
  const [promotionCommitResult, setPromotionCommitResult] = useState<JsonRecord | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState('');
  const [promotionApproval, setPromotionApproval] = useState('');
  const [promotionConfirmation, setPromotionConfirmation] = useState('');
  const [llmEnabled, setLlmEnabled] = useState(false);
  const [modelEndpoint, setModelEndpoint] = useState(LOCAL_MODEL_ENDPOINT);
  const [model, setModel] = useState(LOCAL_MODEL_NAME);
  const [renderResult, setRenderResult] = useState<JsonRecord | null>(null);
  const [renderLoading, setRenderLoading] = useState(false);

  const loadOverview = useCallback(async () => {
    setLoading(true);
    setError(null);
    const checkedAt = new Date().toISOString();
    const nextData: RmcPanelData = { ...emptyPanelData };
    const nextHealth: EndpointHealthMap = {};

    const calls: Array<[keyof RmcPanelData, () => Promise<unknown>]> = [
      ['routeManifest', () => fetchRouteManifest(true)],
      ['memoryStatus', () => getMemoryStatus()],
      ['contextSearchTest', () => getContextSearchTest({ query: input, limit: 8 })],
      ['contextDuplicates', () => getContextDuplicates()],
      ['contextExportManifest', () => getContextExportManifest()],
      ['latestMemoryWrites', () => getLatestMemoryWrites({ limit: 12 })],
      ['rmcNamespaces', () => getRmcNamespaces()],
      ['chromaStatus', () => getChromaStatus()],
      ['activeLoop', () => getActiveLoopState({ input })],
      ['pipelineSummary', () => getPipelineSummary({ input, include_full: '0' })],
      ['promotionStatus', () => getPromotionStatus()],
      ['glyphStatus', () => getGlyphRendererStatus()],
      ['llmStatus', () => getLlmRendererStatus()],
      ['datasetGrowthStatus', () => getDatasetGrowthStatus()],
      ['datasetGrowthCoverage', () => getDatasetGrowthCoverage()],
    ];

    await Promise.all(calls.map(async ([key, call]) => {
      try {
        const value = await call();
        nextData[key] = value as any;
        nextHealth[key] = makeEndpointHealth(key, true, null, checkedAt);
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        nextHealth[key] = makeEndpointHealth(key, false, message, checkedAt);
      }
    }));

    const summary = summarizeEndpointHealth(nextHealth);
    setData(nextData);
    setEndpointHealth(nextHealth);
    setLastLoadedAt(new Date().toISOString());
    setError(summary.failed > 0 ? `Partial RMC UI load: ${summary.failed} endpoint(s) failed; loaded data remains visible for the endpoints that passed.` : null);
    setLoading(false);
  }, [input]);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  const expectedPromotionConfirmation = buildGuardConfirmationPhrase(selectedCandidateId);
  const promotionArmState = evaluateGuardPromotionArmState({
    candidateId: selectedCandidateId,
    approvalToken: promotionApproval,
    confirmationPhrase: promotionConfirmation,
    preview: promotionPreview,
  });
  const canPromote = promotionArmState.armed;

  const previewPromotion = useCallback(async (candidateId: string) => {
    setSelectedCandidateId(candidateId);
    setPromotionApproval('');
    setPromotionConfirmation('');
    setPromotionCommitResult(null);
    setPromotionPreview(await getPromotionPreview(candidateId) as JsonRecord);
  }, []);

  const runPromotion = useCallback(async () => {
    if (!canPromote) return;
    setPromotionCommitResult(await getPromotionPromote(selectedCandidateId, promotionApproval) as JsonRecord);
    await loadOverview();
  }, [canPromote, loadOverview, promotionApproval, selectedCandidateId]);

  const runRenderer = useCallback(async () => {
    setRenderLoading(true);
    try {
      setRenderResult(await getOutputRenderer({
        input,
        mode: 'text',
        llm_renderer: llmEnabled ? 'on' : 'off',
        model_endpoint: llmEnabled ? modelEndpoint : undefined,
        model: llmEnabled ? model : undefined,
      }) as JsonRecord);
    } finally {
      setRenderLoading(false);
    }
  }, [input, llmEnabled, modelEndpoint, model]);

  const routeWarnings = useMemo(() => {
    const approvalRoutes = data.routeManifest?.approval_required ?? [];
    return approvalRoutes.map((route) => `${route.route_key}: ${route.approval_token ?? 'approval required'}`);
  }, [data.routeManifest]);

  return (
    <RmcPanelShell
      loading={loading}
      error={error}
      input={input}
      onInputChange={setInput}
      onReload={() => void loadOverview()}
    >
      <RmcTopMetricsSection data={data} endpointHealth={endpointHealth} lastLoadedAt={lastLoadedAt} />
      <RmcEndpointHealthSection endpointHealth={endpointHealth} />
      <RmcRouteManifestSection manifest={data.routeManifest} routeWarnings={routeWarnings} />
      <RmcContextLibrarySection data={data} />
      <RmcActiveLoopSection activeLoopData={data.activeLoop} />
      <RmcPromotionSection
        promotionStatus={data.promotionStatus}
        promotionPreview={promotionPreview}
        promotionCommitResult={promotionCommitResult}
        selectedCandidateId={selectedCandidateId}
        promotionApproval={promotionApproval}
        promotionConfirmation={promotionConfirmation}
        expectedConfirmation={expectedPromotionConfirmation}
        promotionToken={PROMOTION_TOKEN}
        armState={promotionArmState}
        canPromote={canPromote}
        onPreview={(candidateId) => void previewPromotion(candidateId)}
        onPromote={() => void runPromotion()}
        onCandidateIdChange={setSelectedCandidateId}
        onApprovalChange={setPromotionApproval}
        onConfirmationChange={setPromotionConfirmation}
      />
      <RmcRendererSection
        llmStatus={data.llmStatus}
        llmEnabled={llmEnabled}
        modelEndpoint={modelEndpoint}
        model={model}
        renderLoading={renderLoading}
        renderResult={renderResult}
        onLlmEnabledChange={setLlmEnabled}
        onModelEndpointChange={setModelEndpoint}
        onModelChange={setModel}
        onRender={() => void runRenderer()}
      />
      <RmcBoundarySection data={data} />
    </RmcPanelShell>
  );
}
