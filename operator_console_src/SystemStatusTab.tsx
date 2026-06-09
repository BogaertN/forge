import { useCallback } from 'react';
import { getAiwebOsBuildManifest, getForgeStatus, getOperatorApiContract } from '../api/forgeClient';
import type { ApiEndpointSpec, ForgeStatusResponse, OperatorApiContract, AiwebOsBuildManifestResponse } from '../api/types';
import { useAsyncData } from '../api/useAsyncData';
import { StatusBadge } from '../shell/StatusBadge';

function getNumber(data: Record<string, unknown> | undefined, key: string): number | string {
  const value = data?.[key];
  return typeof value === 'number' || typeof value === 'string' ? value : '—';
}

function getAuditTail(data: Record<string, unknown> | undefined): string[] {
  const value = data?.audit_tail;
  return Array.isArray(value) ? value.map(String).slice(-8) : [];
}

function BoundaryPanel({ status }: { status: ForgeStatusResponse | null }) {
  const boundary = status?.boundary;

  return (
    <div className="panel-card">
      <div className="card-key">Boundary</div>
      <div className="card-value">
        <div>executes command: {String(boundary?.executes_command ?? false)}</div>
        <div>executes simulation: {String(boundary?.executes_simulation ?? false)}</div>
        <div>Identity write: {String(boundary?.identity_vault_write ?? false)}</div>
        <div>RMC live write: {String(boundary?.rmc_live_memory_write ?? false)}</div>
      </div>
    </div>
  );
}

function ContractPanel({ contract }: { contract: OperatorApiContract | null }) {
  return (
    <div className="panel-card wide">
      <div className="card-key">API Contract</div>
      <div className="card-value">
        <div>{contract?.api_contract ?? '—'} · v{contract?.version ?? '—'}</div>
        <div>read-only contract: {String(contract?.read_only_contract ?? false)}</div>
        <div>adds Forge commands: false</div>
      </div>
    </div>
  );
}


function BuildManifestPanel({ manifest }: { manifest: AiwebOsBuildManifestResponse | null }) {
  return (
    <div className="panel-card wide">
      <div className="card-key">AI.Web Build Manifest</div>
      <div className="card-value">
        <div>current patch: <span className="good">{String(manifest?.current_patch ?? '—')}</span></div>
        <div>last successful: {String(manifest?.last_successful_patch ?? '—')}</div>
        <div>RMC canonical routes: {String(manifest?.counts?.rmc_canonical_routes ?? '—')}</div>
        <div>command surface expected: {String(manifest?.counts?.command_surface_expected ?? '—')}</div>
        <div>Terminus hidden by default: {String(manifest?.terminus_high_security_ui?.hidden_by_default ?? '—')}</div>
        <div>dirty-state warning: {String(manifest?.dirty_state?.warning ?? '—')}</div>
      </div>
    </div>
  );
}

export function SystemStatusTab() {
  const statusLoader = useCallback(() => getForgeStatus(), []);
  const contractLoader = useCallback(() => getOperatorApiContract(), []);
  const buildManifestLoader = useCallback(() => getAiwebOsBuildManifest(), []);
  const statusState = useAsyncData<ForgeStatusResponse>(statusLoader);
  const contractState = useAsyncData<OperatorApiContract>(contractLoader);
  const buildManifestState = useAsyncData<AiwebOsBuildManifestResponse>(buildManifestLoader);

  const status = statusState.data;
  const contract = contractState.data;
  const buildManifest = buildManifestState.data;
  const core = status?.data;
  const auditTail = getAuditTail(core);

  return (
    <section className="tab-page">
      <div className="eyebrow">SYSTEM</div>
      <h1>System Status</h1>
      <p className="subtitle">
        Read-only Forge runtime health from <code>/api/forge/status</code>. This panel does not execute commands.
      </p>

      <div className="action-row">
        <button onClick={statusState.reload}>Refresh Forge Status</button>
        <button onClick={contractState.reload}>Refresh API Contract</button>
        <button onClick={buildManifestState.reload}>Refresh Build Manifest</button>
        <span className="muted">
          {statusState.loading || contractState.loading || buildManifestState.loading ? 'loading…' : 'read-only'}
        </span>
      </div>

      {(statusState.error || contractState.error || buildManifestState.error) && (
        <div className="error-panel">
          {statusState.error && <div>Forge status error: {statusState.error}</div>}
          {contractState.error && <div>API contract error: {contractState.error}</div>}
          {buildManifestState.error && <div>Build manifest error: {buildManifestState.error}</div>}
        </div>
      )}

      <div className="status-grid">
        <StatusBadge label="Status" value={status?.status ?? '—'} good={status?.status === 'OK'} />
        <StatusBadge label="Trust" value={getNumber(core, 'trust')} />
        <StatusBadge label="Tools" value={getNumber(core, 'tool_count')} />
        <StatusBadge label="Commands" value={getNumber(core, 'cmd_count')} />
      </div>

      <div className="card-grid">
        <BuildManifestPanel manifest={buildManifest} />
        <ContractPanel contract={contract} />
        <BoundaryPanel status={status} />

        <div className="panel-card wide">
          <div className="card-key">Read-only endpoints</div>
          <div className="card-value">
            {(contract?.endpoints ?? []).map((endpoint: ApiEndpointSpec) => (
              <div key={`${endpoint.method}-${endpoint.path}`}>
                {endpoint.method} {endpoint.path} · {endpoint.mode}
              </div>
            ))}
          </div>
        </div>

        <div className="panel-card wide">
          <div className="card-key">Recent Audit Tail</div>
          <div className="audit-lines">
            {auditTail.length > 0 ? auditTail.map((line) => <div key={line}>{line}</div>) : '—'}
          </div>
        </div>
      </div>
    </section>
  );
}
