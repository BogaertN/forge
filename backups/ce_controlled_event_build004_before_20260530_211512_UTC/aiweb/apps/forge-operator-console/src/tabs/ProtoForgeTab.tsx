import { useCallback } from 'react';
import { getProtoForgeReports } from '../api/forgeClient';
import type { ProtoForgeReportsResponse } from '../api/types';
import { asText, boundaryClass } from '../api/format';
import { useAsyncData } from '../api/useAsyncData';
import { ArtifactBrowser } from '../protoforge/ArtifactBrowser';
import { SimulationPlanner } from '../protoforge/SimulationPlanner';
import { SimulationResultPanel } from '../protoforge/SimulationResultPanel';
import { TraceReplay3D } from '../protoforge/TraceReplay3D';

function BoundaryCard({ report }: { report: ProtoForgeReportsResponse | null }) {
  const summary = report?.summary;

  return (
    <div className="panel-card">
      <div className="card-key">Authority Boundary</div>
      <div className="card-value">
        <div>
          endpoint read-only:{' '}
          <span className={boundaryClass(report?.read_only)}>{asText(report?.read_only)}</span>
        </div>
        <div>
          executes command:{' '}
          <span className={boundaryClass(report?.executes_command, true)}>
            {asText(report?.executes_command)}
          </span>
        </div>
        <div>
          executes simulation:{' '}
          <span className={boundaryClass(report?.executes_simulation, true)}>
            {asText(report?.executes_simulation)}
          </span>
        </div>
        <div>
          shell used:{' '}
          <span className={boundaryClass(summary?.shell_used, true)}>{asText(summary?.shell_used)}</span>
        </div>
        <div>
          Identity write:{' '}
          <span className={boundaryClass(summary?.identity_vault_written, true)}>
            {asText(summary?.identity_vault_written)}
          </span>
        </div>
        <div>
          RMC live write:{' '}
          <span className={boundaryClass(summary?.rmc_live_memory_written, true)}>
            {asText(summary?.rmc_live_memory_written)}
          </span>
        </div>
      </div>
    </div>
  );
}

function HashCard({ report }: { report: ProtoForgeReportsResponse | null }) {
  const summary = report?.summary;

  return (
    <div className="panel-card wide">
      <div className="card-key">Hashes</div>
      <div className="card-value hash-lines">
        <div>Result hash: {asText(summary?.result_hash)}</div>
        <div>Result file sha256: {asText(summary?.result_file_sha256)}</div>
      </div>
    </div>
  );
}

export function ProtoForgeTab() {
  const loader = useCallback(() => getProtoForgeReports(), []);
  const state = useAsyncData<ProtoForgeReportsResponse>(loader);
  const report = state.data;
  const summary = report?.summary ?? null;

  return (
    <section className="tab-page">
      <div className="eyebrow">PROTOFORGE</div>
      <h1>ProtoForge Simulations</h1>
      <p className="subtitle">
        Read-only production app panel using <code>/api/protoforge/reports</code>. This panel does not execute simulations.
      </p>

      <div className="action-row">
        <button onClick={state.reload}>Refresh ProtoForge Reports</button>
        <span className="muted">{state.loading ? 'loading…' : 'read-only'}</span>
      </div>

      {state.error && <div className="error-panel">ProtoForge report error: {state.error}</div>}

      <div className="status-grid">
        <div className="status-badge">
          <span>Status</span>
          <strong className={summary?.service_ok ? 'good' : 'warn'}>{asText(summary?.service_verdict)}</strong>
        </div>
        <div className="status-badge">
          <span>Contract</span>
          <strong>{asText(summary?.contract_version)}</strong>
        </div>
        <div className="status-badge">
          <span>Latest Run</span>
          <strong>{asText(summary?.latest_run_id)}</strong>
        </div>
        <div className="status-badge">
          <span>Substrate</span>
          <strong className="good">{asText(summary?.substrate_verdict)}</strong>
        </div>
      </div>

      <div className="card-grid">
        <div className="panel-card wide">
          <div className="card-key">Implementation Root</div>
          <div className="card-value">{asText(summary?.implementation_root)}</div>
        </div>

        <SimulationPlanner summary={summary} />
        <SimulationResultPanel summary={summary} />
        <BoundaryCard report={report} />
        <ArtifactBrowser summary={summary} />
        <HashCard report={report} />
        <TraceReplay3D summary={summary} />
      </div>
    </section>
  );
}
