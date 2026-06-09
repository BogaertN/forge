// Patch 262-UI-MemoryPanel-P5
// Shared RMC Memory Panel view primitives. UI-only, no network, no writes, no authority.

import type { ReactNode } from 'react';
import type { RmcRouteManifest } from './rmc-api-client';

export type JsonValue = unknown;
export type JsonRecord = Record<string, any>;

export function asText(value: JsonValue): string {
  if (value === null || value === undefined || value === '') return '—';
  if (Array.isArray(value)) return value.length > 0 ? value.map(asText).join(', ') : '—';
  if (typeof value === 'boolean') return value ? 'True' : 'False';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export function jsonPreview(value: JsonValue, fallback = 'No data.'): string {
  if (value === null || value === undefined || value === '') return fallback;
  if (typeof value === 'string') return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function getPath(source: JsonRecord | null | undefined, path: Array<string | number>): JsonValue {
  let cursor: any = source;
  for (const key of path) {
    if (cursor === null || cursor === undefined) return undefined;
    cursor = cursor[key as keyof typeof cursor];
  }
  return cursor;
}

export function statusClass(value: JsonValue, goodWhenFalse = false): string {
  const boolValue = value === true;
  if (goodWhenFalse) return boolValue ? 'bad' : 'good';
  if (value === 'OK' || value === 'PASS' || boolValue) return 'good';
  if (value === 'BLOCKED' || value === 'SKIPPED') return 'warn';
  return 'warn';
}

export function Metric({ label, value, goodWhenFalse = false }: { label: string; value: JsonValue; goodWhenFalse?: boolean }) {
  return (
    <div className="status-badge">
      <span>{label}</span>
      <strong className={statusClass(value, goodWhenFalse)}>{asText(value)}</strong>
    </div>
  );
}

export function Section({ title, badge, children }: { title: string; badge?: JsonValue; children: ReactNode }) {
  return (
    <section className="panel-card wide rmc-memory-block">
      <div className="output-slot-header">
        <span>{title}</span>
        {badge !== undefined && <strong>{asText(badge)}</strong>}
      </div>
      {children}
    </section>
  );
}

export function JsonDetails({ title, value }: { title: string; value: JsonValue }) {
  return (
    <details className="audit-receipt-file-item">
      <summary>{title}</summary>
      <pre className="rmc-object-pre">{jsonPreview(value)}</pre>
    </details>
  );
}

export function DirectoryList({ directories }: { directories: JsonRecord | null }) {
  const entries = Object.entries(directories ?? {}).sort(([a], [b]) => a.localeCompare(b));
  if (entries.length === 0) {
    return <div className="muted small-note">No directory inventory reported by /api/rmc/memory-status.</div>;
  }
  return (
    <div className="rmc-count-list">
      {entries.map(([key, directory]) => {
        const record = directory as JsonRecord;
        return (
          <div key={key} className="runtime-mini-metric">
            <span>{record.label || key}</span>
            <strong>{record.exists ? `${record.files_found ?? 0} files` : 'missing'}</strong>
          </div>
        );
      })}
    </div>
  );
}

export function RouteAvailability({ manifest }: { manifest: RmcRouteManifest | null }) {
  const lookup = manifest?.lookup ?? {};
  const required = [
    ['memory_status', 'Context library status'],
    ['context_search_test', 'Context search test'],
    ['context_duplicates', 'Context duplicate status'],
    ['context_export_manifest', 'Context export manifest preview'],
    ['latest_memory_writes', 'Latest memory writes'],
    ['rmc_namespaces', 'RMC namespaces'],
    ['memory_recaller', 'Context search / recall'],
    ['chroma_status', 'Chroma retrieval boundary'],
    ['active_loop_state', 'Active loop state'],
    ['promotion_path_status', 'Promotion status'],
    ['promotion_path_preview', 'Promotion preview'],
    ['promotion_path_promote', 'Gated promotion'],
    ['glyph_renderer_status', 'Glyph renderer'],
    ['llm_renderer_status', 'Optional LLM renderer'],
    ['pipeline_summary', 'Pipeline summary'],
  ];
  const knownGaps = [
    ['context_search_history', 'Historical context-search-test run history is not a write-backed route yet; current endpoint is live read-only.'],
  ];
  return (
    <div className="rmc-object-grid">
      {required.map(([key, label]) => (
        <div className="runtime-mini-metric" key={key}>
          <span>{label}</span>
          <strong className={lookup[key] ? 'good' : 'warn'}>{lookup[key] || 'not exposed'}</strong>
        </div>
      ))}
      {knownGaps.map(([key, label]) => (
        <div className="runtime-mini-metric" key={key}>
          <span>{label}</span>
          <strong className="warn">backend route missing</strong>
        </div>
      ))}
    </div>
  );
}

export function ReviewQueueList({ promotionStatus, onPreview }: { promotionStatus: JsonRecord | null; onPreview: (candidateId: string) => void }) {
  const candidates = (promotionStatus?.review_queue_preview ?? []) as JsonRecord[];
  if (candidates.length === 0) {
    return <div className="muted small-note">No review_queue candidates reported.</div>;
  }
  return (
    <div className="audit-receipt-file-list">
      {candidates.map((candidate) => {
        const candidateId = String(candidate.candidate_id ?? '');
        return (
          <div className="audit-receipt-file-item" key={candidateId || JSON.stringify(candidate)}>
            <div className="output-slot-header">
              <span>{candidateId || 'unknown candidate'}</span>
              <strong className={candidate.circuit_breaker_triggered ? 'warn' : 'good'}>{asText(candidate.review_status)}</strong>
            </div>
            <div className="mini-report-path">{asText(candidate.path)}</div>
            <div className="rmc-object-grid">
              <Metric label="family" value={candidate.candidate_family} />
              <Metric label="target" value={candidate.candidate_target_dataset} />
              <Metric label="namespace" value={candidate.promotion_namespace} />
              <Metric label="circuit breaker" value={candidate.circuit_breaker_triggered} goodWhenFalse />
              <Metric label="promotable preview" value={candidate.promotable_preview} />
              <Metric label="missing fields" value={(candidate.missing_required_fields ?? []).length} goodWhenFalse />
            </div>
            <div className="action-row compact-actions">
              <button type="button" onClick={() => onPreview(candidateId)} disabled={!candidateId}>Preview promotion</button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
