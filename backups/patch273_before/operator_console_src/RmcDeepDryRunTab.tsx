// Patch 272 — Deep Dry-Run UI Panel
// Read-only Operator Console surface for /api/rmc/deep-dry-run and adjacent deep-stack proofs.

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  fetchRouteManifest,
  getDeepDryRun,
  getDeepPipelinePreflight,
  getProtoForge2DriftPreview,
  getResurrectionPreview,
} from '../lib/rmc-api-client';
import {
  JsonDetails,
  Metric,
  Section,
  getPath,
  type JsonRecord,
} from '../lib/rmc-panel-primitives';

const DEFAULT_DRY_RUN_INPUT = 'Patch 272 UI dry-run: show the governed RMC deep stack without writing, projecting, echo-approving, or committing memory.';

type EndpointKey = 'routeManifest' | 'deepDryRun' | 'deepPipelinePreflight' | 'protoforge2DriftPreview' | 'resurrectionPreview';

type EndpointState = Record<EndpointKey, { ok: boolean; status: string; error: string | null }>;

const EMPTY_ENDPOINT_STATE: EndpointState = {
  routeManifest: { ok: false, status: 'not_loaded', error: null },
  deepDryRun: { ok: false, status: 'not_loaded', error: null },
  deepPipelinePreflight: { ok: false, status: 'not_loaded', error: null },
  protoforge2DriftPreview: { ok: false, status: 'not_loaded', error: null },
  resurrectionPreview: { ok: false, status: 'not_loaded', error: null },
};

function asArray(value: unknown): JsonRecord[] {
  return Array.isArray(value) ? value.filter((item): item is JsonRecord => typeof item === 'object' && item !== null) : [];
}

function asString(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'string') return value;
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'number') return String(value);
  return JSON.stringify(value);
}

function endpointMetric(state: EndpointState) {
  const values = Object.values(state);
  return {
    total: values.length,
    ok: values.filter((item) => item.ok).length,
    failed: values.filter((item) => !item.ok).length,
  };
}

function StageList({ stages }: { stages: JsonRecord[] }) {
  if (stages.length === 0) {
    return <div className="muted small-note">No dry-run stages reported yet.</div>;
  }
  return (
    <div className="rmc-stage-list deep-dry-run-stage-list">
      {stages.map((stage, index) => {
        const executed = stage.executed === true;
        const writesFiles = stage.writes_files === true;
        return (
          <div className="rmc-stage-card" key={`${stage.stage_id ?? 'stage'}-${index}`}>
            <div className="output-slot-header">
              <span>{index + 1}. {asString(stage.stage_id)}</span>
              <strong className={stage.status === 'OK' || stage.status === 'SKIPPED' ? 'good' : 'warn'}>{asString(stage.status)}</strong>
            </div>
            <div className="rmc-object-grid">
              <Metric label="executed" value={executed} />
              <Metric label="read-only" value={stage.read_only} />
              <Metric label="writes files" value={writesFiles} goodWhenFalse />
            </div>
            {stage.reason && <div className="muted small-note">{asString(stage.reason)}</div>}
            <JsonDetails title="stage summary" value={stage.summary ?? stage} />
          </div>
        );
      })}
    </div>
  );
}

function EndpointHealth({ endpointState }: { endpointState: EndpointState }) {
  const summary = endpointMetric(endpointState);
  return (
    <Section title="Deep Dry-Run Endpoint Health" badge={summary.failed === 0 ? 'OK' : 'DEGRADED'}>
      <div className="rmc-object-grid">
        <Metric label="endpoint total" value={summary.total} />
        <Metric label="endpoint OK" value={summary.ok} />
        <Metric label="endpoint failed" value={summary.failed} goodWhenFalse />
      </div>
      <div className="rmc-count-list">
        {Object.entries(endpointState).map(([key, item]) => (
          <div key={key} className="runtime-mini-metric">
            <span>{key}</span>
            <strong className={item.ok ? 'good' : 'bad'}>{item.status}</strong>
            {item.error && <small>{item.error}</small>}
          </div>
        ))}
      </div>
    </Section>
  );
}

function RouteProof({ routeManifest }: { routeManifest: JsonRecord | null }) {
  const lookup = (routeManifest?.lookup ?? {}) as JsonRecord;
  const routes = [
    ['deep_dry_run', '/api/rmc/deep-dry-run'],
    ['deep_pipeline_preflight', '/api/rmc/deep-pipeline-preflight'],
    ['protoforge2_drift_preview', '/api/rmc/protoforge2-drift-preview'],
    ['resurrection_preview', '/api/rmc/resurrection-preview'],
    ['containment_router', '/api/rmc/containment-router'],
    ['chi_correction_preview', '/api/rmc/chi-correction-preview'],
  ];
  return (
    <Section title="Canonical Route Proof" badge={routeManifest?.status}>
      <div className="rmc-object-grid">
        <Metric label="canonical route count" value={routeManifest?.canonical_route_count} />
        <Metric label="alias count" value={routeManifest?.alias_count} />
        {routes.map(([key, expected]) => (
          <Metric key={key} label={key} value={lookup[key] || expected} />
        ))}
      </div>
      <div className="muted small-note">
        The panel resolves endpoints through /api/rmc/route-manifest first and only falls back to hardcoded local routes if the manifest is unreachable.
      </div>
    </Section>
  );
}

function FinalRouteSection({ dryRun }: { dryRun: JsonRecord | null }) {
  const payload = (dryRun?.dry_run ?? dryRun) as JsonRecord | null;
  const finalRoute = (payload?.final_route ?? {}) as JsonRecord;
  const summary = (payload?.summary ?? {}) as JsonRecord;
  const violations = (payload?.forbidden_effect_violations ?? summary?.forbidden_effect_violations ?? []) as unknown[];
  const modules = (payload?.deep_stack_modules_exercised ?? {}) as JsonRecord;
  return (
    <Section title="Final Route / Forbidden-Effect Proof" badge={payload?.status}>
      <div className="rmc-object-grid">
        <Metric label="run id" value={payload?.run_id} />
        <Metric label="stage count" value={payload?.stage_count} />
        <Metric label="final route" value={finalRoute?.final_route ?? payload?.final_route} />
        <Metric label="projection allowed" value={finalRoute?.projection_allowed ?? payload?.projection_allowed} goodWhenFalse />
        <Metric label="manifest emitted" value={payload?.manifest_emitted} goodWhenFalse />
        <Metric label="memory committed" value={finalRoute?.memory_write_committed ?? payload?.memory_write_committed} goodWhenFalse />
        <Metric label="forbidden violations" value={violations.length} goodWhenFalse />
        <Metric label="deep modules exercised" value={Object.keys(modules).length || '—'} />
      </div>
      <JsonDetails title="Final route object" value={finalRoute} />
      <JsonDetails title="Forbidden effect violations" value={violations} />
      <JsonDetails title="Deep stack modules exercised" value={modules} />
    </Section>
  );
}

function DeepBoundarySection({ dryRun, preflight, pf2Preview, resurrection }: { dryRun: JsonRecord | null; preflight: JsonRecord | null; pf2Preview: JsonRecord | null; resurrection: JsonRecord | null }) {
  const dry = (dryRun?.dry_run ?? dryRun) as JsonRecord | null;
  const pre = (preflight?.preflight ?? preflight) as JsonRecord | null;
  const pf2 = (pf2Preview?.preview ?? pf2Preview) as JsonRecord | null;
  const res = (resurrection?.dry_run_evaluation ?? resurrection) as JsonRecord | null;
  return (
    <Section title="Boundary / Read-Only Contract" badge={pre?.activation_ready === true ? 'READY' : 'REVIEW'}>
      <div className="rmc-object-grid">
        <Metric label="preflight activation ready" value={pre?.activation_ready} />
        <Metric label="boundary verifications" value={pre?.boundary_verifications_passed} />
        <Metric label="boundary failures" value={(pre?.boundary_verification_failures ?? []).length} goodWhenFalse />
        <Metric label="PF2 adapter mode" value={pf2?.adapter_mode} />
        <Metric label="PF2 live" value={pf2?.live_drift_available} />
        <Metric label="PF2 normalized" value={getPath(pf2, ['normalized_result', 'normalized'])} />
        <Metric label="resurrection allowed" value={res?.resurrection_allowed} goodWhenFalse />
        <Metric label="resurrection projection" value={res?.projection_allowed} goodWhenFalse />
        <Metric label="dry-run writes files" value={dry?.writes_files} goodWhenFalse />
        <Metric label="dry-run calls LLM" value={dry?.calls_llm} goodWhenFalse />
      </div>
      <JsonDetails title="Deep pipeline preflight" value={pre} />
      <JsonDetails title="ProtoForge2 drift preview" value={pf2} />
      <JsonDetails title="Resurrection preview" value={res} />
    </Section>
  );
}

export function RmcDeepDryRunTab() {
  const [input, setInput] = useState(DEFAULT_DRY_RUN_INPUT);
  const [routeManifest, setRouteManifest] = useState<JsonRecord | null>(null);
  const [deepDryRun, setDeepDryRun] = useState<JsonRecord | null>(null);
  const [deepPreflight, setDeepPreflight] = useState<JsonRecord | null>(null);
  const [pf2Preview, setPf2Preview] = useState<JsonRecord | null>(null);
  const [resurrectionPreview, setResurrectionPreview] = useState<JsonRecord | null>(null);
  const [endpointState, setEndpointState] = useState<EndpointState>(EMPTY_ENDPOINT_STATE);
  const [loading, setLoading] = useState(true);
  const [lastLoadedAt, setLastLoadedAt] = useState<string | null>(null);

  const loadPanel = useCallback(async () => {
    setLoading(true);
    const nextState: EndpointState = { ...EMPTY_ENDPOINT_STATE };

    async function guarded<T>(key: EndpointKey, call: () => Promise<T>): Promise<T | null> {
      try {
        const value = await call();
        nextState[key] = { ok: true, status: 'OK', error: null };
        return value;
      } catch (err) {
        nextState[key] = { ok: false, status: 'ERROR', error: err instanceof Error ? err.message : String(err) };
        return null;
      }
    }

    const [manifest, dry, preflight, pf2, resurrection] = await Promise.all([
      guarded('routeManifest', () => fetchRouteManifest(true)),
      guarded('deepDryRun', () => getDeepDryRun({ input })),
      guarded('deepPipelinePreflight', () => getDeepPipelinePreflight()),
      guarded('protoforge2DriftPreview', () => getProtoForge2DriftPreview()),
      guarded('resurrectionPreview', () => getResurrectionPreview()),
    ]);

    setRouteManifest(manifest as JsonRecord | null);
    setDeepDryRun(dry as JsonRecord | null);
    setDeepPreflight(preflight as JsonRecord | null);
    setPf2Preview(pf2 as JsonRecord | null);
    setResurrectionPreview(resurrection as JsonRecord | null);
    setEndpointState(nextState);
    setLastLoadedAt(new Date().toISOString());
    setLoading(false);
  }, [input]);

  useEffect(() => {
    void loadPanel();
  }, [loadPanel]);

  const dryRunPayload = (deepDryRun?.dry_run ?? deepDryRun) as JsonRecord | null;
  const stages = useMemo(() => asArray(dryRunPayload?.stages), [dryRunPayload]);
  const endpointSummary = endpointMetric(endpointState);

  return (
    <div className="tab-stack rmc-deep-dry-run-panel">
      <div className="panel-card wide">
        <div className="output-slot-header">
          <span>RMC Deep Dry-Run Panel</span>
          <strong>{loading ? 'loading' : endpointSummary.failed === 0 ? 'live proof loaded' : 'partial load'}</strong>
        </div>
        <div className="muted small-note">
          Read-only control surface for Patch 271. This panel executes /api/rmc/deep-dry-run only as a dry-run proof. It does not write files, emit manifests, project output, echo-approve, commit memory, call an LLM, touch Identity Vault, or re-enter active runtime.
        </div>
        <div className="action-row compact-actions">
          <input value={input} onChange={(event) => setInput(event.target.value)} aria-label="Deep dry-run input" />
          <button type="button" onClick={() => void loadPanel()}>Run read-only dry-run</button>
        </div>
        <div className="rmc-object-grid">
          <Metric label="dry-run status" value={dryRunPayload?.status} />
          <Metric label="stage count" value={dryRunPayload?.stage_count} />
          <Metric label="last loaded" value={lastLoadedAt} />
          <Metric label="endpoint failures" value={endpointSummary.failed} goodWhenFalse />
          <Metric label="projection allowed" value={dryRunPayload?.projection_allowed} goodWhenFalse />
          <Metric label="memory committed" value={dryRunPayload?.memory_write_committed} goodWhenFalse />
        </div>
      </div>

      <EndpointHealth endpointState={endpointState} />
      <RouteProof routeManifest={routeManifest} />
      <FinalRouteSection dryRun={deepDryRun} />
      <DeepBoundarySection dryRun={deepDryRun} preflight={deepPreflight} pf2Preview={pf2Preview} resurrection={resurrectionPreview} />
      <Section title="16-Stage Dry-Run Trace" badge={dryRunPayload?.stage_count}>
        <StageList stages={stages} />
      </Section>
      <JsonDetails title="Full deep dry-run JSON" value={deepDryRun} />
    </div>
  );
}
