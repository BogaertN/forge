import { useCallback, useEffect, useState } from 'react';
import { asText, boundaryClass } from '../api/format';
import { getIdentityVaultStatus, getOperatorOutputState, getProtoForgeReports } from '../api/forgeClient';
import type { IdentityVaultStatusResponse, OperatorOutputStateResponse, ProtoForgeReportsResponse } from '../api/types';

function field(source: Record<string, unknown> | undefined, key: string): unknown {
  return source && Object.prototype.hasOwnProperty.call(source, key) ? source[key] : undefined;
}

function safeStatus(value: unknown): string {
  return asText(value || 'UNKNOWN');
}

function BoundaryLine({ label, value, goodWhenFalse = false }: { label: string; value: unknown; goodWhenFalse?: boolean }) {
  return (
    <div className="runtime-boundary-line">
      <span>{label}</span>
      <strong className={boundaryClass(value, goodWhenFalse)}>{asText(value)}</strong>
    </div>
  );
}

function MiniMetric({ label, value, tone }: { label: string; value: unknown; tone?: string }) {
  return (
    <div className="runtime-mini-metric">
      <span>{label}</span>
      <strong className={tone}>{asText(value)}</strong>
    </div>
  );
}

export function RightAuditRail() {
  const [outputState, setOutputState] = useState<OperatorOutputStateResponse | null>(null);
  const [protoForge, setProtoForge] = useState<ProtoForgeReportsResponse | null>(null);
  const [identity, setIdentity] = useState<IdentityVaultStatusResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [lastRefresh, setLastRefresh] = useState<string>('not loaded');

  const load = useCallback(async () => {
    try {
      const [outputData, protoData, identityData] = await Promise.all([
        getOperatorOutputState(),
        getProtoForgeReports().catch(() => null),
        getIdentityVaultStatus().catch(() => null),
      ]);
      setOutputState(outputData);
      setProtoForge(protoData);
      setIdentity(identityData);
      setError('');
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLastRefresh(new Date().toLocaleTimeString());
    }
  }, []);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), 3000);
    return () => window.clearInterval(id);
  }, [load]);

  const forgeData = outputState?.forge_status?.data;
  const boundary = outputState?.boundary;
  const protoSummary = protoForge?.summary;
  const identitySummary = identity?.summary;

  return (
    <aside className="right-rail right-rail-runtime-live">
      <div className="rail-title">RUNTIME STATUS</div>
      <button className="right-rail-refresh" onClick={() => void load()}>Refresh Status</button>
      <div className="rail-refresh-note">live poll: 3s · last: {lastRefresh}</div>

      {error && <div className="right-rail-error">status error: {error}</div>}

      <div className="runtime-status-block">
        <div className="runtime-status-header">Forge Core</div>
        <MiniMetric label="Status" value={safeStatus(outputState?.status)} tone={outputState?.status === 'OK' ? 'good' : 'warn'} />
        <MiniMetric label="Trust" value={field(forgeData, 'trust')} />
        <MiniMetric label="Commands" value={field(forgeData, 'cmd_count')} />
        <MiniMetric label="Tools" value={field(forgeData, 'tool_count')} />
        <MiniMetric label="Session" value={field(forgeData, 'session_id')} />
        <MiniMetric label="Next" value={outputState?.summary?.next_patch} />
      </div>

      <div className="runtime-status-block runtime-count-grid">
        <MiniMetric label="Safe" value={outputState?.summary?.safe_browser_commands} />
        <MiniMetric label="Gated" value={outputState?.summary?.gated_browser_commands} />
        <MiniMetric label="Audit" value={outputState?.summary?.audit_lines} />
        <MiniMetric label="Slots" value={outputState?.summary?.output_slots} />
      </div>

      <div className="runtime-status-block">
        <div className="runtime-status-header">Authority Boundary</div>
        <BoundaryLine label="UI authority" value={boundary?.ui_is_authority} goodWhenFalse />
        <BoundaryLine label="Forge governs" value={boundary?.forge_governs} />
        <BoundaryLine label="Command bridge" value={boundary?.command_execution_enabled} />
        <BoundaryLine label="Frontend shell" value={boundary?.frontend_direct_shell} goodWhenFalse />
        <BoundaryLine label="Frontend files" value={boundary?.frontend_direct_file_write} goodWhenFalse />
        <BoundaryLine label="LLM shell" value={boundary?.llm_shell_enabled} goodWhenFalse />
        <BoundaryLine label="LLM file writes" value={boundary?.llm_file_write_enabled} goodWhenFalse />
        <BoundaryLine label="Identity write" value={outputState?.identity_vault_write} goodWhenFalse />
        <BoundaryLine label="RMC live write" value={outputState?.rmc_live_memory_write} goodWhenFalse />
        <BoundaryLine label="Left rail gated click" value={boundary?.left_rail_gated_actions_require_operator_click} />
        <BoundaryLine label="Right rail read-only" value={boundary?.right_rail_runtime_status_read_only} />
      </div>

      <div className="runtime-status-block">
        <div className="runtime-status-header">ProtoForge</div>
        <MiniMetric label="Status" value={protoForge?.status} tone={protoForge?.status === 'OK' ? 'good' : 'warn'} />
        <MiniMetric label="Service" value={protoSummary?.service_verdict} />
        <MiniMetric label="Latest run" value={protoSummary?.latest_run_id} />
        <MiniMetric label="Run OK" value={protoSummary?.latest_run_ok} />
        <MiniMetric label="Client" value={protoSummary?.client_mode} />
      </div>

      <div className="runtime-status-block">
        <div className="runtime-status-header">Identity Vault</div>
        <MiniMetric label="Status" value={identity?.status} tone={identity?.status === 'OK' ? 'good' : 'warn'} />
        <MiniMetric label="Agent dirs" value={identitySummary?.agent_dirs_found} />
        <MiniMetric label="Reports" value={identitySummary?.reports_found} />
        <BoundaryLine label="Secret reads" value={identity?.secret_reads} goodWhenFalse />
        <BoundaryLine label="Autonomous exec" value={identity?.autonomous_execution} goodWhenFalse />
      </div>

      <p className="rail-note">
        Patch 260: right rail reads live runtime state only. It polls Forge status APIs and does not execute commands, write files, touch Identity Vault, or mutate RMC live memory.
      </p>
    </aside>
  );
}
