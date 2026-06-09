// Patch 262-UI-MemoryPanel-P6
// Domain section components for RMC Memory Panel Phase 2. UI-only, no network, no writes, no authority.

import type { ChangeEvent, ReactNode } from 'react';
import type { RmcRouteManifest } from './rmc-api-client';
import type { EndpointHealthMap } from './rmc-panel-health';
import { summarizeEndpointHealth } from './rmc-panel-health';
import {
  DirectoryList,
  JsonDetails,
  Metric,
  ReviewQueueList,
  RouteAvailability,
  Section,
  getPath,
  type JsonRecord,
} from './rmc-panel-primitives';
import type { PromotionArmState } from './rmc-ui-guards';

export type RmcPanelData = {
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

export type RmcPanelShellProps = {
  loading: boolean;
  error: string | null;
  input: string;
  onInputChange: (value: string) => void;
  onReload: () => void;
  children: ReactNode;
};

export function RmcPanelShell({ loading, error, input, onInputChange, onReload, children }: RmcPanelShellProps) {
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
          <input value={input} onChange={(event: ChangeEvent<HTMLInputElement>) => onInputChange(event.target.value)} aria-label="RMC input" />
          <button type="button" onClick={onReload}>Reload RMC state</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function RmcTopMetricsSection({ data, endpointHealth, lastLoadedAt }: { data: RmcPanelData; endpointHealth: EndpointHealthMap; lastLoadedAt: string | null }) {
  const promotionCounts = data.promotionStatus?.counts as JsonRecord | undefined;
  const routeCount = data.routeManifest?.canonical_route_count ?? '—';
  const endpointSummary = summarizeEndpointHealth(endpointHealth);
  return (
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
  );
}

export function RmcEndpointHealthSection({ endpointHealth }: { endpointHealth: EndpointHealthMap }) {
  const endpointSummary = summarizeEndpointHealth(endpointHealth);
  return (
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
  );
}

export function RmcRouteManifestSection({ manifest, routeWarnings }: { manifest: RmcRouteManifest | null; routeWarnings: string[] }) {
  return (
    <Section title="Canonical Route Manifest / API Truth" badge={manifest?.status}>
      <RouteAvailability manifest={manifest} />
      {routeWarnings.length > 0 && (
        <div className="muted small-note">Approval-gated routes: {routeWarnings.join(' | ')}</div>
      )}
    </Section>
  );
}

export function RmcContextLibrarySection({ data }: { data: RmcPanelData }) {
  const memorySummary = data.memoryStatus?.summary as JsonRecord | undefined;
  return (
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
  );
}

export function RmcActiveLoopSection({ activeLoopData }: { activeLoopData: JsonRecord | null }) {
  const activeLoop = (activeLoopData?.L_t ?? activeLoopData) as JsonRecord | undefined;
  return (
    <Section title="Active Loop State / Session Continuity" badge={activeLoopData?.status}>
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
  );
}

export type RmcPromotionSectionProps = {
  promotionStatus: JsonRecord | null;
  promotionPreview: JsonRecord | null;
  promotionCommitResult: JsonRecord | null;
  selectedCandidateId: string;
  promotionApproval: string;
  promotionConfirmation: string;
  expectedConfirmation: string;
  promotionToken: string;
  armState: PromotionArmState;
  canPromote: boolean;
  onPreview: (candidateId: string) => void;
  onPromote: () => void;
  onCandidateIdChange: (value: string) => void;
  onApprovalChange: (value: string) => void;
  onConfirmationChange: (value: string) => void;
};

export function RmcPromotionSection(props: RmcPromotionSectionProps) {
  const promotionCounts = props.promotionStatus?.counts as JsonRecord | undefined;
  return (
    <Section title="Promotion Path / Review Queue → Stable Memory → Retrieval Index" badge={props.promotionStatus?.status}>
      <div className="rmc-object-grid">
        <Metric label="review queue" value={promotionCounts?.review_queue} />
        <Metric label="stable memory" value={promotionCounts?.stable_memory} />
        <Metric label="approved promotions" value={promotionCounts?.approved_promotions} />
        <Metric label="retrieval rows" value={promotionCounts?.retrieval_index_rows} />
        <Metric label="writes on status" value={props.promotionStatus?.writes_files} goodWhenFalse />
        <Metric label="approval token" value={props.promotionToken} />
      </div>
      <ReviewQueueList promotionStatus={props.promotionStatus} onPreview={props.onPreview} />
      <div className="panel-card wide">
        <div className="output-slot-header">
          <span>Gated promotion execution</span>
          <strong className={props.canPromote ? 'good' : 'warn'}>{props.canPromote ? 'armed' : 'locked'}</strong>
        </div>
        <div className="muted small-note">
          Promotion is a real write route. P3 requires a fresh preview, the exact approval token, and the exact confirmation fingerprint before the write route can be called.
        </div>
        <div className="rmc-object-grid">
          <Metric label="preview current" value={props.armState.previewCurrent} />
          <Metric label="preview allows promotion" value={props.armState.previewAllowsPromotion} />
          <Metric label="token exact" value={props.armState.tokenExact} />
          <Metric label="confirmation exact" value={props.armState.confirmationExact} />
          <Metric label="unsafe paths" value={props.armState.unsafePathCount} goodWhenFalse />
          <Metric label="duplicate" value={props.armState.duplicateDetected} goodWhenFalse />
        </div>
        {props.armState.reasonCodes.length > 0 && (
          <div className="muted small-note">Gate blockers: {props.armState.reasonCodes.join(' | ')}</div>
        )}
        <div className="action-row compact-actions">
          <input value={props.selectedCandidateId} onChange={(event: ChangeEvent<HTMLInputElement>) => props.onCandidateIdChange(event.target.value)} placeholder="candidate_id" />
          <input value={props.promotionApproval} onChange={(event: ChangeEvent<HTMLInputElement>) => props.onApprovalChange(event.target.value)} placeholder={props.promotionToken} />
          <input
            value={props.promotionConfirmation}
            onChange={(event: ChangeEvent<HTMLInputElement>) => props.onConfirmationChange(event.target.value)}
            placeholder={props.expectedConfirmation || 'PROMOTE <candidate_id>'}
          />
          <button type="button" onClick={props.onPromote} disabled={!props.canPromote}>Promote reviewed candidate</button>
        </div>
        <div className="muted small-note">
          Required confirmation: <code>{props.expectedConfirmation || 'select and preview a candidate first'}</code>
        </div>
        <JsonDetails title="Promotion preview" value={props.promotionPreview} />
        <JsonDetails title="Promotion arm state" value={props.armState} />
        <JsonDetails title="Promotion commit result" value={props.promotionCommitResult} />
      </div>
    </Section>
  );
}

export type RmcRendererSectionProps = {
  llmStatus: JsonRecord | null;
  llmEnabled: boolean;
  modelEndpoint: string;
  model: string;
  renderLoading: boolean;
  renderResult: JsonRecord | null;
  onLlmEnabledChange: (value: boolean) => void;
  onModelEndpointChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onRender: () => void;
};

export function RmcRendererSection(props: RmcRendererSectionProps) {
  return (
    <Section title="Renderer / Optional Local LLM Toggle" badge={props.llmStatus?.status}>
      <div className="rmc-object-grid">
        <Metric label="LLM default enabled" value={props.llmStatus?.default_enabled} goodWhenFalse />
        <Metric label="local only" value={getPath(props.llmStatus, ['boundary', 'approved_endpoint_policy'])} />
        <Metric label="echo required" value={getPath(props.llmStatus, ['boundary', 'echo_validation_required_after_llm_text'])} />
        <Metric label="LLM is authority" value={getPath(props.llmStatus, ['boundary', 'llm_output_is_not_authority']) === false} goodWhenFalse />
      </div>
      <div className="action-row compact-actions">
        <label>
          <input type="checkbox" checked={props.llmEnabled} onChange={(event: ChangeEvent<HTMLInputElement>) => props.onLlmEnabledChange(event.target.checked)} />
          Enable optional local LLM draft
        </label>
        <input value={props.modelEndpoint} onChange={(event: ChangeEvent<HTMLInputElement>) => props.onModelEndpointChange(event.target.value)} disabled={!props.llmEnabled} />
        <input value={props.model} onChange={(event: ChangeEvent<HTMLInputElement>) => props.onModelChange(event.target.value)} disabled={!props.llmEnabled} />
        <button type="button" onClick={props.onRender} disabled={props.renderLoading}>{props.renderLoading ? 'rendering' : 'Preview renderer'}</button>
      </div>
      <div className="muted small-note">The LLM toggle only drafts text through the sentence plan. It does not approve output and does not write memory.</div>
      <JsonDetails title="Renderer result" value={props.renderResult} />
    </Section>
  );
}

export function RmcBoundarySection({ data }: { data: RmcPanelData }) {
  return (
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
  );
}
