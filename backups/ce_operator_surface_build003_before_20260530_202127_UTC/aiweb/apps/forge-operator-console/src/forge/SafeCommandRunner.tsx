import { useMemo, useState } from 'react';
import { runForgeCommand } from '../api/forgeClient';
import type { BrowserCommandBridgeInventory, ForgeCommandRunRecord } from '../api/types';

function classifyCommand(command: string, bridge: BrowserCommandBridgeInventory | undefined): 'safe' | 'gated' | 'unknown' {
  const root = command.trim().split(/\s+/)[0] ?? '';

  if (bridge?.safe?.includes(root)) {
    return 'safe';
  }

  if (bridge?.gated?.includes(root)) {
    return 'gated';
  }

  return 'unknown';
}

function requiredGate(command: string): string {
  const root = command.trim().split(/\s+/)[0] ?? '';

  if (root.includes('protoforge') || root.includes('sim')) {
    return 'RUN-PROTOFORGE';
  }

  if (root.includes('install') || root.includes('apply')) {
    return 'APPLY';
  }

  if (root.includes('restart')) {
    return 'RESTART';
  }

  return '';
}

export function SafeCommandRunner({
  bridge,
  onResult,
}: {
  bridge: BrowserCommandBridgeInventory | undefined;
  onResult: (record: ForgeCommandRunRecord) => void;
}) {
  const [command, setCommand] = useState('forge-command-surface');
  const [gate, setGate] = useState('');
  const [running, setRunning] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const mode = useMemo(() => classifyCommand(command, bridge), [command, bridge]);
  const suggestedGate = useMemo(() => requiredGate(command), [command]);

  async function submit() {
    const trimmed = command.trim();
    const root = trimmed.split(/\s+/)[0] ?? '';
    const commandId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;

    setLocalError(null);

    if (!trimmed) {
      setLocalError('Enter a Forge command first.');
      return;
    }

    if (mode === 'unknown') {
      setLocalError(`Blocked by UI: "${root}" is not listed as browser-safe or gated.`);
      return;
    }

    if (mode === 'gated' && !gate.trim()) {
      setLocalError(`Gate required for "${root}". Suggested gate: ${suggestedGate || 'check Forge output'}.`);
      return;
    }

    setRunning(true);

    try {
      const response = await runForgeCommand(trimmed, gate.trim() || undefined);
      onResult({
        id: commandId,
        command: trimmed,
        gate: gate.trim() || undefined,
        status: response.status,
        output: response.output ?? JSON.stringify(response, null, 2),
        created_at: new Date().toISOString(),
        safe_mode: mode,
      });
    } catch (error) {
      onResult({
        id: commandId,
        command: trimmed,
        gate: gate.trim() || undefined,
        status: 'CLIENT_ERROR',
        output: error instanceof Error ? error.message : String(error),
        created_at: new Date().toISOString(),
        safe_mode: mode,
      });
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="safe-command-runner">
      <div className="runner-header">
        <div>
          <div className="card-key">Safe Command Runner</div>
          <p>
            Uses the existing Forge <code>/api/command</code> bridge. Unknown commands are blocked in the UI.
          </p>
        </div>
        <div className={`runner-mode runner-${mode}`}>{mode}</div>
      </div>

      <label>
        Command
        <input
          value={command}
          onChange={(event) => {
            setCommand(event.target.value);
            setLocalError(null);
          }}
          placeholder="forge-command-surface"
        />
      </label>

      {mode === 'gated' && (
        <label>
          Gate
          <input
            value={gate}
            onChange={(event) => setGate(event.target.value)}
            placeholder={suggestedGate || 'required gate'}
          />
        </label>
      )}

      {localError && <div className="error-panel">{localError}</div>}

      <div className="action-row compact-actions">
        <button onClick={submit} disabled={running || mode === 'unknown'}>
          {running ? 'Running…' : 'Run through Forge'}
        </button>
        <span className="muted">
          safe: {bridge?.safe_count ?? bridge?.safe?.length ?? 0} · gated: {bridge?.gated_count ?? bridge?.gated?.length ?? 0}
        </span>
      </div>

      <div className="runner-hints">
        Try safe commands first: <code>forge-command-surface</code>, <code>forge-protoforge-status</code>, <code>audit</code>.
      </div>
    </div>
  );
}
