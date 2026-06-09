// Patch 262-UI-MemoryPanel-P5
// RMC Memory Panel Phase 2 hardening: split reusable view primitives from the stateful panel.

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
  type RmcRouteManifest,
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
import {
  DirectoryList,
  JsonDetails,
  Metric,
  ReviewQueueList,
  RouteAvailability,
  Section,
  getPath,
  type JsonRecord,
} from '../lib/rmc-panel-primitives';

type PanelData = {
  routeManifest: RmcRouteManifest | null;
  memoryStatus: JsonRecord | null;
  contextSearchTest: JsonRecord | null;
  contextDuplicates: JsonRecord | null;
  contextExportManifest: JsonRecord | null;
  latestMemoryWrites: JsonRecord | null;
  rmcNamespaces: JsonRecord | null;
  chromaStatus: JsonRecord | null;
  activeLoop: JsonRecord | null;
  pipelineSummary: JsonRecord | null;
  promotionStatus: JsonRecord | null;
  glyphStatus: JsonRecord | null;
  llmStatus: JsonRecord | null;
  datasetGrowthStatus: JsonRecord | null;
  datasetGrowthCoverage: JsonRecord | null;
};

const DEFAULT_INPUT = 'correct projection before naming';
const PROMOTION_TOKEN = PROMOTION_TOKEN_FROM_GUARDS;
const LOCAL_MODEL_ENDPOINT = 'http://localhost:11434/api/generate';
const LOCAL_MODEL_NAME = 'qwen3:8b';

const emptyPanelData: PanelData = {
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
  const [data, setData] = useState<PanelData>(emptyPanelData);
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
    const nextData: PanelData = { ...emptyPanelData };
    const nextHealth: EndpointHealthMap = {};

    const calls: Array<[keyof PanelData, () => Promise<unknown>]> = [
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
        (nextData as JsonRecord)[key] = value;
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

  const promotionCounts = data.promotionStatus?.counts as JsonRecord | undefined;
  const memorySummary = data.memoryStatus?.summary as JsonRecord | undefined;
  const activeLoop = (data.activeLoop?.L_t ?? data.activeLoop) as JsonRecord | undefined;
  const routeCount = data.routeManifest?.canonical_route_count ?? '—';
  const endpointSummary = summarizeEndpointHealth(endpointHealth);
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
    <div className="tab-stack rmc-memory-panel phase2">
      <div className="panel-card wide">
        <div className="output-slot-header">
          <span>RMC Memory Panel Phase 2</span>
          <strong>{loading ? 'loading' : 'canonical routes loaded'}</strong>
        </div>
        <div className="muted small-note">
          This panel is a control surface only. It reads canonical RMC routes from /api/rmc/route-manifest, previews gated actions, and requires exact operator tokens before any write route is called.
        </div>
        {error && <div className="error-panel">RMC panel load error: {error}</div>}
        <div className="action-row compact-actions">
          <input value={input} onChange={(event) => setInput(event.target.value)} aria-label="RMC input" />
          <button type="button" onClick={() => void loadOverview()}>Reload RMC state</button>
        </div>
        <div className="rmc-object-grid">
          <Metric label="canonical routes" value={routeCount} />
          <Metric label="endpoint failures" value={endpointSummary.failed} goodWhenFalse />
          <Metric label="last refresh" value={lastLoadedAt} />
          <Metric label="memory status" value={data.memoryStatus?.status} />
          <Metric label="duplicate issues" value={getPath(data.contextDuplicates, ['summary', 'issue_total'])} goodWhenFalse />
          <Metric label="latest writes" value={data.latestMemoryWrites?.total_files_seen} />
          <Metric label="Chroma available" value={data.chromaStatus?.connector_available_for_query} />
          <Metric label="LLM default enabled" value={getPath(data.llmStatus, ['default_enabled'])} goodWhenFalse />
          <Metric label="glyph phases" value={data.glyphStatus?.phase_count} />
          <Metric label="review queue" value={promotionCounts?.review_queue} />
          <Metric label="stable memory" value={promotionCounts?.stable_memory} />
          <Metric label="retrieval index rows" value={promotionCounts?.retrieval_index_rows} />
        </div>
      </div>

      <Section title="UI Endpoint Health / Partial Load Guard" badge={endpointSummary.degraded ? 'DEGRADED' : 'OK'}>
        <div className="rmc-object-grid">
          <Metric label="endpoint total" value={endpointSummary.total} />
          <Metric label="endpoint OK" value={endpointSummary.ok} />
          <Metric label="endpoint failed" value={endpointSummary.failed} goodWhenFalse />
          <Metric label="partial load" value={endpointSummary.degraded} goodWhenFalse />
        </div>
        <div className="rmc-count-list">
          {Object.values(endpointHealth).map((health) => (
            <div key={health.key} className="runtime-mini-metric">
              <span>{health.key}</span>
              <strong className={health.ok ? 'good' : 'bad'}>{health.status}</strong>
              {!health.ok && <small>{health.error || 'endpoint failed'}</small>}
            </div>
          ))}
        </div>
        <div className="muted small-note">
          P4 isolates endpoint failures. One stale route can no longer blank the whole memory panel; failed sources are marked here while healthy sources still render.
        </div>
      </Section>

      <Section title="Canonical Route Manifest / API Truth" badge={data.routeManifest?.status}>
        <RouteAvailability manifest={data.routeManifest} />
        {routeWarnings.length > 0 && (
          <div className="muted small-note">Approval-gated routes: {routeWarnings.join(' | ')}</div>
        )}
      </Section>

      <Section title="Context Library / Memory Surface" badge={data.memoryStatus?.status}>
        <div className="rmc-object-grid">
          <Metric label="context library exists" value={memorySummary?.context_library_exists} />
          <Metric label="collection" value={memorySummary?.collection} />
          <Metric label="chunks" value={memorySummary?.collection_total_chunks} />
          <Metric label="ingestion receipts" value={memorySummary?.receipt_files} />
          <Metric label="export manifests" value={memorySummary?.manifest_files} />
          <Metric label="symbolic maps" value={memorySummary?.symbolic_map_files} />
          <Metric label="symbolic chunks" value={memorySummary?.symbolic_chunks_scanned} />
          <Metric label="legacy Chroma present" value={memorySummary?.legacy_chroma_db_present} goodWhenFalse />
          <Metric label="duplicate issues" value={getPath(data.contextDuplicates, ['summary', 'issue_total'])} goodWhenFalse />
          <Metric label="export receipt count" value={getPath(data.contextExportManifest, ['summary', 'receipt_count'])} />
          <Metric label="namespace count" value={data.rmcNamespaces?.namespace_count} />
          <Metric label="latest write files" value={data.latestMemoryWrites?.total_files_seen} />
        </div>
        <DirectoryList directories={(data.memoryStatus?.directories ?? null) as JsonRecord | null} />
        <JsonDetails title="Latest ingestion receipt" value={data.memoryStatus?.latest_receipt} />
        <JsonDetails title="Symbolic summary" value={data.memoryStatus?.symbolic_summary} />
        <JsonDetails title="Context search test" value={data.contextSearchTest} />
        <JsonDetails title="Context duplicate status" value={data.contextDuplicates} />
        <JsonDetails title="Context export manifest preview" value={data.contextExportManifest} />
        <JsonDetails title="RMC namespaces" value={data.rmcNamespaces} />
        <JsonDetails title="Latest memory writes" value={data.latestMemoryWrites} />
      </Section>

      <Section title="Active Loop State / Session Continuity" badge={data.activeLoop?.status}>
        <div className="rmc-object-grid">
          <Metric label="loop id" value={activeLoop?.current_loop_id} />
          <Metric label="current phase" value={activeLoop?.current_phase} />
          <Metric label="next step" value={activeLoop?.next_expected_step} />
          <Metric label="open issues" value={(activeLoop?.open_issues ?? []).length} goodWhenFalse />
          <Metric label="unresolved branches" value={(activeLoop?.unresolved_branches ?? []).length} goodWhenFalse />
          <Metric label="memory write status" value={activeLoop?.memory_write_status} />
        </div>
        <JsonDetails title="L_t active loop object" value={activeLoop} />
      </Section>

      <Section title="Promotion Path / Review Queue → Stable Memory → Retrieval Index" badge={data.promotionStatus?.status}>
        <div className="rmc-object-grid">
          <Metric label="review queue" value={promotionCounts?.review_queue} />
          <Metric label="stable memory" value={promotionCounts?.stable_memory} />
          <Metric label="approved promotions" value={promotionCounts?.approved_promotions} />
          <Metric label="retrieval rows" value={promotionCounts?.retrieval_index_rows} />
          <Metric label="writes on status" value={data.promotionStatus?.writes_files} goodWhenFalse />
          <Metric label="approval token" value={PROMOTION_TOKEN} />
        </div>
        <ReviewQueueList promotionStatus={data.promotionStatus} onPreview={(candidateId) => void previewPromotion(candidateId)} />
        <div className="panel-card wide">
          <div className="output-slot-header">
            <span>Gated promotion execution</span>
            <strong className={canPromote ? 'good' : 'warn'}>{canPromote ? 'armed' : 'locked'}</strong>
          </div>
          <div className="muted small-note">
            Promotion is a real write route. P3 requires a fresh preview, the exact approval token, and the exact confirmation fingerprint before the write route can be called.
          </div>
          <div className="rmc-object-grid">
            <Metric label="preview current" value={promotionArmState.previewCurrent} />
            <Metric label="preview allows promotion" value={promotionArmState.previewAllowsPromotion} />
            <Metric label="token exact" value={promotionArmState.tokenExact} />
            <Metric label="confirmation exact" value={promotionArmState.confirmationExact} />
            <Metric label="unsafe paths" value={promotionArmState.unsafePathCount} goodWhenFalse />
            <Metric label="duplicate" value={promotionArmState.duplicateDetected} goodWhenFalse />
          </div>
          {promotionArmState.reasonCodes.length > 0 && (
            <div className="muted small-note">Gate blockers: {promotionArmState.reasonCodes.join(' | ')}</div>
          )}
          <div className="action-row compact-actions">
            <input value={selectedCandidateId} onChange={(event) => setSelectedCandidateId(event.target.value)} placeholder="candidate_id" />
            <input value={promotionApproval} onChange={(event) => setPromotionApproval(event.target.value)} placeholder={PROMOTION_TOKEN} />
            <input
              value={promotionConfirmation}
              onChange={(event) => setPromotionConfirmation(event.target.value)}
              placeholder={expectedPromotionConfirmation || 'PROMOTE <candidate_id>'}
            />
            <button type="button" onClick={() => void runPromotion()} disabled={!canPromote}>Promote reviewed candidate</button>
          </div>
          <div className="muted small-note">
            Required confirmation: <code>{expectedPromotionConfirmation || 'select and preview a candidate first'}</code>
          </div>
          <JsonDetails title="Promotion preview" value={promotionPreview} />
          <JsonDetails title="Promotion arm state" value={promotionArmState} />
          <JsonDetails title="Promotion commit result" value={promotionCommitResult} />
        </div>
      </Section>

      <Section title="Renderer / Optional Local LLM Toggle" badge={data.llmStatus?.status}>
        <div className="rmc-object-grid">
          <Metric label="LLM default enabled" value={data.llmStatus?.default_enabled} goodWhenFalse />
          <Metric label="local only" value={getPath(data.llmStatus, ['boundary', 'approved_endpoint_policy'])} />
          <Metric label="echo required" value={getPath(data.llmStatus, ['boundary', 'echo_validation_required_after_llm_text'])} />
          <Metric label="LLM is authority" value={getPath(data.llmStatus, ['boundary', 'llm_output_is_not_authority']) === false} goodWhenFalse />
        </div>
        <div className="action-row compact-actions">
          <label>
            <input type="checkbox" checked={llmEnabled} onChange={(event) => setLlmEnabled(event.target.checked)} />
            Enable optional local LLM draft
          </label>
          <input value={modelEndpoint} onChange={(event) => setModelEndpoint(event.target.value)} disabled={!llmEnabled} />
          <input value={model} onChange={(event) => setModel(event.target.value)} disabled={!llmEnabled} />
          <button type="button" onClick={() => void runRenderer()} disabled={renderLoading}>{renderLoading ? 'rendering' : 'Preview renderer'}</button>
        </div>
        <div className="muted small-note">The LLM toggle only drafts text through the sentence plan. It does not approve output and does not write memory.</div>
        <JsonDetails title="Renderer result" value={renderResult} />
      </Section>

      <Section title="Chroma / Glyph / Dataset Growth Boundaries" badge="read-only">
        <div className="rmc-object-grid">
          <Metric label="Chroma path guard" value={data.chromaStatus?.chroma_path_guard_ok} />
          <Metric label="Chroma query available" value={data.chromaStatus?.connector_available_for_query} />
          <Metric label="Chroma writes" value={data.chromaStatus?.writes_chroma} goodWhenFalse />
          <Metric label="glyph renderer" value={data.glyphStatus?.mode} />
          <Metric label="image generation authority" value={data.glyphStatus?.image_generation_is_authority} goodWhenFalse />
          <Metric label="dataset growth status" value={data.datasetGrowthStatus?.status} />
        </div>
        <JsonDetails title="Dataset growth coverage" value={data.datasetGrowthCoverage} />
        <JsonDetails title="Pipeline summary" value={data.pipelineSummary} />
      </Section>
    </div>
  );
}
