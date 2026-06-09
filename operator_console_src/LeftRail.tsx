import { useEffect, useMemo, useState } from 'react';
import { getOperatorOutputState, runForgeCommand } from '../api/forgeClient';
import { DatasetGrowthRail } from '../forge/DatasetGrowthRail';
import type { ForgeCommandResponse, OperatorOutputStateResponse, OperatorTabId } from '../api/types';

type RailActionStatus = 'IDLE' | 'OK' | 'ERROR' | 'NEEDS_GATE' | 'CANCELLED';

interface RailActionResult {
  title: string;
  status: RailActionStatus;
  body: string;
}

function commandOutput(response: ForgeCommandResponse): string {
  return String(response.output || response.status || 'No output returned.');
}

function compactOutput(value: string): string {
  return value.length > 1100 ? `${value.slice(0, 1100)}\n…[trimmed in left rail; full command output remains available through Forge]` : value;
}

export function LeftRail({
  activeTab,
  onTabChange,
}: {
  activeTab: OperatorTabId;
  onTabChange: (tab: OperatorTabId) => void;
}) {
  const [state, setState] = useState<OperatorOutputStateResponse | null>(null);
  const [loadingAction, setLoadingAction] = useState<string>('');
  const [result, setResult] = useState<RailActionResult | null>(null);

  async function reloadState() {
    try {
      const data = await getOperatorOutputState();
      setState(data);
    } catch (err) {
      setResult({
        title: 'Left rail state check',
        status: 'ERROR',
        body: err instanceof Error ? err.message : String(err),
      });
    }
  }

  useEffect(() => {
    void reloadState();
  }, []);

  const safeCommands = useMemo(() => new Set(state?.browser_command_bridge?.safe ?? []), [state]);
  const gatedCommands = useMemo(() => new Set(state?.browser_command_bridge?.gated ?? []), [state]);

  function canRun(command: string): boolean {
    if (!state) return true;
    return safeCommands.has(command) || gatedCommands.has(command);
  }

  async function runRailCommand(title: string, command: string, gate?: string) {
    setLoadingAction(title);
    setResult(null);
    try {
      const response = await runForgeCommand(command, gate);
      setResult({
        title,
        status: (response.status as RailActionStatus) || 'OK',
        body: compactOutput(commandOutput(response)),
      });
      await reloadState();
    } catch (err) {
      setResult({
        title,
        status: 'ERROR',
        body: err instanceof Error ? err.message : String(err),
      });
    } finally {
      setLoadingAction('');
    }
  }

  function openTerminus() {
    window.dispatchEvent(new CustomEvent('aiweb-open-terminus'));
    setResult({
      title: 'Open Terminus',
      status: 'OK',
      body: 'Opened the Terminus high-security HTML shell inside the Operator Console overlay. No new browser tab was opened and no Forge command was executed.',
    });
  }


  function focusAskForgeDatasetCapture() {
    onTabChange('forge_output');
    window.setTimeout(() => {
      window.dispatchEvent(new CustomEvent('forge-dataset-growth-focus-ask', { detail: { enableCapture: true } }));
      const block = document.getElementById('ask-forge-block');
      block?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      const input = document.getElementById('ask-forge-request-textarea') as HTMLTextAreaElement | null;
      input?.focus();
    }, 220);
    setResult({
      title: 'Ask Forge Dataset Capture',
      status: 'OK',
      body: 'Focused Ask Forge and requested dataset review capture mode. The capture still requires the Ask Forge submit action and only writes to the growth dataset, never canonical reference files.',
    });
  }

  function focusPageCapture() {
    onTabChange('forge_output');
    window.setTimeout(() => {
      const input = document.getElementById('page-capture-url') as HTMLInputElement | null;
      input?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      input?.focus();
    }, 180);
    setResult({
      title: 'Capture Page',
      status: 'OK',
      body: 'Focused the Forge Output page-capture panel. Capture still routes through /api/read-page and writes only to Forge browser memory.',
    });
  }

  async function runApprovedSimulation() {
    const approved = window.confirm('Run the latest approved ProtoForge simulation through the Forge-gated bridge? This uses gate RUN-PROTOFORGE.');
    if (!approved) {
      setResult({
        title: 'Run Approved Sim',
        status: 'CANCELLED',
        body: 'Operator cancelled gated ProtoForge simulation run. No command was sent.',
      });
      return;
    }
    onTabChange('protoforge_simulations');
    await runRailCommand('Run Approved Sim', 'forge-protoforge-simulation-run-approved', 'RUN-PROTOFORGE');
  }

  const busy = Boolean(loadingAction);

  return (
    <aside className="left-rail left-rail-live">
      <div className="rail-title">FORGE</div>
      <button onClick={openTerminus} disabled={busy}>Open Terminus</button>
      <button onClick={focusPageCapture} disabled={busy}>Capture Page</button>

      <DatasetGrowthRail onFocusAskForge={focusAskForgeDatasetCapture} />

      <div className="rail-title">PROTOFORGE</div>
      <button
        disabled={busy || !canRun('forge-protoforge-status')}
        onClick={() => {
          onTabChange('protoforge_simulations');
          void runRailCommand('ProtoForge Status', 'forge-protoforge-status');
        }}
      >
        Status
      </button>
      <button
        disabled={busy || !canRun('forge-protoforge-simulation-plan')}
        onClick={() => {
          onTabChange('protoforge_simulations');
          void runRailCommand('Plan Cube Sim', 'forge-protoforge-simulation-plan pybullet_fixed_falling_cube');
        }}
      >
        Plan Cube Sim
      </button>
      <button
        className="rail-gated-button"
        disabled={busy || !canRun('forge-protoforge-simulation-run-approved')}
        onClick={() => void runApprovedSimulation()}
      >
        Run Approved Sim
      </button>
      <button
        disabled={busy || !canRun('forge-protoforge-result-show')}
        onClick={() => {
          onTabChange('protoforge_simulations');
          void runRailCommand('Latest Result', 'forge-protoforge-result-show');
        }}
      >
        Latest Result
      </button>

      <div className="rail-title">STATE</div>
      <div className="rail-mini-state">
        <div>tab: <span>{activeTab}</span></div>
        <div>safe: <span>{state?.summary?.safe_browser_commands ?? '—'}</span></div>
        <div>gated: <span>{state?.summary?.gated_browser_commands ?? '—'}</span></div>
      </div>
      <button className="rail-secondary" disabled={busy} onClick={() => void reloadState()}>Refresh Rail State</button>

      {loadingAction && <p className="rail-note">Running through Forge bridge: {loadingAction}</p>}
      {result && (
        <div className={`rail-result rail-result-${result.status.toLowerCase()}`}>
          <div className="rail-result-header">
            <span>{result.title}</span>
            <strong>{result.status}</strong>
          </div>
          <pre>{result.body}</pre>
        </div>
      )}

      <p className="rail-note">
        Patch 259: left rail buttons route only through existing UI surfaces or Forge's safe/gated <code>/api/command</code> bridge. No shell or direct writes are granted here.
      </p>
    </aside>
  );
}
