import { useCallback } from 'react';
import { asText, boundaryClass } from '../api/format';
import { getIdentityVaultStatus } from '../api/forgeClient';
import type { IdentityVaultReportSummary, IdentityVaultStatusResponse } from '../api/types';
import { useAsyncData } from '../api/useAsyncData';

function ReportSummary({ report }: { report: IdentityVaultReportSummary }) {
  const summary = report.summary ?? {};

  return (
    <div className="mini-report">
      <div className="mini-report-title">{asText(report.filename ?? report.kind ?? report.path)}</div>
      <div className="mini-report-path">{asText(report.path)}</div>
      {Object.keys(summary).length > 0 && (
        <div className="mini-report-fields">
          {Object.entries(summary).map(([key, value]) => (
            <div key={key}>{key}: {asText(value)}</div>
          ))}
        </div>
      )}
    </div>
  );
}

export function IdentityVaultTab() {
  const loader = useCallback(() => getIdentityVaultStatus(), []);
  const state = useAsyncData<IdentityVaultStatusResponse>(loader);
  const data = state.data;

  return (
    <section className="tab-page">
      <div className="eyebrow">IDENTITY</div>
      <h1>Identity Vault</h1>
      <p className="subtitle">
        Read-only identity posture from <code>/api/identity-vault/status</code>. This panel does not activate agents, read secrets, or write the Identity Vault.
      </p>

      <div className="action-row">
        <button onClick={state.reload}>Refresh Identity Vault Status</button>
        <span className="muted">{state.loading ? 'loading…' : 'read-only'}</span>
      </div>

      {state.error && <div className="error-panel">Identity Vault status error: {state.error}</div>}

      <div className="status-grid">
        <div className="status-badge">
          <span>Status</span>
          <strong className={data?.status === 'OK' ? 'good' : 'warn'}>{asText(data?.status)}</strong>
        </div>
        <div className="status-badge">
          <span>Agents</span>
          <strong>{asText(data?.summary.agent_dirs_found)}</strong>
        </div>
        <div className="status-badge">
          <span>Reports</span>
          <strong>{asText(data?.summary.reports_found)}</strong>
        </div>
        <div className="status-badge">
          <span>Commands checked</span>
          <strong>{asText(data?.summary.commands_checked)}</strong>
        </div>
      </div>

      <div className="card-grid">
        <div className="panel-card">
          <div className="card-key">Authority Boundary</div>
          <div className="card-value">
            <div>read-only: <span className={boundaryClass(data?.read_only)}>{asText(data?.read_only)}</span></div>
            <div>executes command: <span className={boundaryClass(data?.executes_command, true)}>{asText(data?.executes_command)}</span></div>
            <div>Identity write: <span className={boundaryClass(data?.identity_vault_write, true)}>{asText(data?.identity_vault_write)}</span></div>
            <div>Identity DB write: <span className={boundaryClass(data?.identity_db_write, true)}>{asText(data?.identity_db_write)}</span></div>
            <div>secret reads: <span className={boundaryClass(data?.secret_reads, true)}>{asText(data?.secret_reads)}</span></div>
            <div>autonomous execution: <span className={boundaryClass(data?.autonomous_execution, true)}>{asText(data?.autonomous_execution)}</span></div>
            <div>RMC live write: <span className={boundaryClass(data?.rmc_live_memory_write, true)}>{asText(data?.rmc_live_memory_write)}</span></div>
          </div>
        </div>

        <div className="panel-card wide">
          <div className="card-key">Candidate Roots</div>
          <div className="card-value">
            {(data?.roots ?? []).map((root) => (
              <div key={root.path}>
                <span className={root.exists ? 'good' : 'muted'}>{root.exists ? 'exists' : 'missing'}</span> · {root.path}
              </div>
            ))}
          </div>
        </div>

        <div className="panel-card wide">
          <div className="card-key">Agent Namespaces</div>
          <div className="card-value">
            {(data?.agents ?? []).length > 0
              ? (data?.agents ?? []).map((agent) => (
                  <div key={agent.path} className="mini-report">
                    <div className="mini-report-title">{agent.agent_id}</div>
                    <div className="mini-report-path">{agent.path}</div>
                    <div>profile.json: {asText(agent.has_profile_json)}</div>
                    <div>state.json: {asText(agent.has_state_json)}</div>
                    <div>permissions.json: {asText(agent.has_permissions_json)}</div>
                  </div>
                ))
              : 'No agent namespace directories found at the scanned roots.'}
          </div>
        </div>

        <div className="panel-card wide">
          <div className="card-key">Known Identity Commands Present</div>
          <div className="card-value">
            {(data?.commands ?? []).map((command) => (
              <div key={command.command}>
                <span className={command.present_in_main ? 'good' : 'muted'}>{command.present_in_main ? 'present' : 'not found'}</span> · {command.command}
              </div>
            ))}
          </div>
        </div>

        <div className="panel-card wide">
          <div className="card-key">Recent Identity / Agent Reports</div>
          <div className="card-value report-list">
            {(data?.reports ?? []).length > 0
              ? (data?.reports ?? []).map((report, index) => <ReportSummary key={`${report.path}-${index}`} report={report} />)
              : 'No identity report files found in Forge memory patterns yet.'}
          </div>
        </div>
      </div>
    </section>
  );
}
