import { useState } from 'react';
import { asText, boundaryClass } from '../api/format';
import { getRmcDatasetGrowthCoverage, getRmcDatasetGrowthStatus } from '../api/forgeClient';
import type { RmcDatasetGrowthResponse } from '../api/types';

function compactCounts(counts?: Record<string, number>) {
  if (!counts) return '—';
  return Object.entries(counts)
    .slice(0, 4)
    .map(([key, value]) => `${key.replace(/_examples|_reference|_v1|\.jsonl/g, '')}: ${value}`)
    .join('\n');
}

export function DatasetGrowthRail({ onFocusAskForge }: { onFocusAskForge: () => void }) {
  const [loading, setLoading] = useState<string>('');
  const [status, setStatus] = useState<RmcDatasetGrowthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load(kind: 'status' | 'coverage') {
    setLoading(kind);
    setError(null);
    try {
      const data = kind === 'status' ? await getRmcDatasetGrowthStatus() : await getRmcDatasetGrowthCoverage();
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading('');
    }
  }

  const growthCounts = status?.growth_counts ?? status?.counts;
  const canonicalCounts = status?.canonical_reference_counts;
  const writesCanonical = Boolean(status?.boundary?.canonical_reference_write_allowed);

  return (
    <div className="rail-dataset-growth" id="left-rail-dataset-growth">
      <div className="rail-title">RMC DATASET</div>
      <button disabled={Boolean(loading)} onClick={() => void load('status')}>Dataset Status</button>
      <button disabled={Boolean(loading)} onClick={() => void load('coverage')}>Coverage Report</button>
      <button className="rail-secondary" disabled={Boolean(loading)} onClick={onFocusAskForge}>Ask Forge + Queue</button>

      {loading && <p className="rail-note">Loading dataset {loading}…</p>}
      {error && <div className="rail-result rail-result-error"><pre>{error}</pre></div>}
      {status && (
        <div className="rail-mini-state rail-dataset-summary">
          <div>status: <span className={status.status === 'OK' ? 'good' : 'warn'}>{asText(status.status)}</span></div>
          <div>root: <span>{asText(status.dataset_root ?? status.boundary?.growth_root)}</span></div>
          <div>canonical write: <span className={boundaryClass(writesCanonical, true)}>{asText(writesCanonical)}</span></div>
          <div className="rail-dataset-counts">
            <strong>growth</strong>
            <pre>{compactCounts(growthCounts)}</pre>
          </div>
          <div className="rail-dataset-counts">
            <strong>reference</strong>
            <pre>{compactCounts(canonicalCounts)}</pre>
          </div>
        </div>
      )}
      <p className="rail-note">Growth captures go to <code>memory/rmc_dataset_v1</code>. Gold/reference files stay patch-only.</p>
    </div>
  );
}
