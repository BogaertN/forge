import { useCallback } from 'react';
import type { ProtoForgeSummary, ProtoForgeTraceResponse } from '../api/types';
import { asText } from '../api/format';
import { getProtoForgeTraceLatest } from '../api/forgeClient';
import { useAsyncData } from '../api/useAsyncData';
import { CubeTraceReplay } from '../three/CubeTraceReplay';

export function TraceReplay3D({ summary }: { summary: ProtoForgeSummary | null }) {
  const loader = useCallback(() => getProtoForgeTraceLatest(), []);
  const state = useAsyncData<ProtoForgeTraceResponse>(loader);
  const trace = state.data?.artifacts?.state_trace?.data;

  return (
    <div className="panel-card wide">
      <div className="card-key">3D Trace Replay</div>
      <div className="card-value trace-summary">
        <div>Run ID: {asText(state.data?.summary?.run_id ?? summary?.latest_run_id)}</div>
        <div>Trace steps: {asText(state.data?.summary?.trace_step_count)}</div>
        <div>Initial z: {asText(state.data?.summary?.initial_z ?? summary?.initial_z)}</div>
        <div>Final z: {asText(state.data?.summary?.final_z ?? summary?.final_z)}</div>
        <div>Mode: verified state_trace.json replay only. No browser-side physics.</div>
      </div>

      <div className="action-row compact-actions">
        <button onClick={state.reload}>Reload Trace</button>
        <span className="muted">{state.loading ? 'loading trace…' : 'read-only replay'}</span>
      </div>

      {state.error && <div className="error-panel">Trace replay error: {state.error}</div>}

      <CubeTraceReplay rawTrace={trace} />
    </div>
  );
}
