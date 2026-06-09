import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  confirmAiwebOsLifecycleAction,
  getAiwebOsLifecycleManifest,
  getAiwebOsLogs,
  getAiwebOsStatus,
  previewAiwebOsLifecycleAction,
} from '../api/forgeClient';
import type {
  AiwebOsLifecycleAction,
  AiwebOsLifecycleConfirmResponse,
  AiwebOsLifecycleManifestResponse,
  AiwebOsLifecyclePreviewResponse,
  AiwebOsLogsResponse,
  AiwebOsStatusResponse,
} from '../api/types';
import { asText, boundaryClass } from '../api/format';

type PanelMode = 'closed' | 'status' | 'logs' | 'action';

type ActionSpec = {
  action: AiwebOsLifecycleAction;
  label: string;
  tone: 'safe' | 'warn' | 'danger';
  description: string;
};

const ACTIONS: ActionSpec[] = [
  {
    action: 'exit_window',
    label: 'Exit Window',
    tone: 'safe',
    description: 'Close only the visible Operator Console window. Forge backend remains running.',
  },
  {
    action: 'restart',
    label: 'Restart AI.Web OS',
    tone: 'warn',
    description: 'Restart the fixed AI.Web OS orchestrator wrapper. Connection may briefly drop.',
  },
  {
    action: 'shutdown',
    label: 'Shutdown AI.Web OS',
    tone: 'danger',
    description: 'Stop the fixed AI.Web OS orchestrator wrapper. Console will disconnect.',
  },
];

function statusTone(status: string | undefined): string {
  return status === 'OK' || status === 'PREVIEW_OK' || status === 'CONFIRMED' ? 'good' : status === 'REFUSED' ? 'warn' : 'muted';
}

function MiniProof({ label, value, goodWhenFalse = false }: { label: string; value: unknown; goodWhenFalse?: boolean }) {
  return (
    <div className="operator-life-proof-tile">
      <span>{label}</span>
      <strong className={boundaryClass(value, goodWhenFalse)}>{asText(value)}</strong>
    </div>
  );
}

function stdoutSummary(status: AiwebOsStatusResponse | null): string[] {
  const stdout = status?.appctl_status?.stdout || '';
  return stdout.split('\n').filter((line) => line.trim().length > 0).slice(0, 20);
}

export function OperatorLifecycleMenu() {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<PanelMode>('closed');
  const [manifest, setManifest] = useState<AiwebOsLifecycleManifestResponse | null>(null);
  const [status, setStatus] = useState<AiwebOsStatusResponse | null>(null);
  const [logs, setLogs] = useState<AiwebOsLogsResponse | null>(null);
  const [preview, setPreview] = useState<AiwebOsLifecyclePreviewResponse | null>(null);
  const [confirmResult, setConfirmResult] = useState<AiwebOsLifecycleConfirmResponse | null>(null);
  const [selectedAction, setSelectedAction] = useState<ActionSpec | null>(null);
  const [tokenInput, setTokenInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [lastLoaded, setLastLoaded] = useState('not loaded');

  const boundary = preview?.boundary || status?.boundary || manifest?.boundary;
  const tokenMatches = Boolean(preview?.confirmation_token && tokenInput === preview.confirmation_token);

  const loadBase = useCallback(async () => {
    setBusy(true);
    try {
      const [manifestData, statusData] = await Promise.all([
        getAiwebOsLifecycleManifest().catch(() => null),
        getAiwebOsStatus(),
      ]);
      setManifest(manifestData);
      setStatus(statusData);
      setLastLoaded(new Date().toLocaleTimeString());
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (!open) return;
    void loadBase();
  }, [open, loadBase]);

  const routeCount = useMemo(() => manifest?.routes?.length ?? 0, [manifest]);

  async function showStatus() {
    setMode('status');
    setOpen(true);
    setPreview(null);
    setConfirmResult(null);
    setSelectedAction(null);
    await loadBase();
  }

  async function showLogs() {
    setMode('logs');
    setOpen(true);
    setPreview(null);
    setConfirmResult(null);
    setSelectedAction(null);
    setBusy(true);
    try {
      const data = await getAiwebOsLogs(140);
      setLogs(data);
      setError('');
      setLastLoaded(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function beginAction(actionSpec: ActionSpec) {
    setMode('action');
    setOpen(true);
    setSelectedAction(actionSpec);
    setTokenInput('');
    setConfirmResult(null);
    setBusy(true);
    try {
      const data = await previewAiwebOsLifecycleAction(actionSpec.action);
      setPreview(data);
      setError('');
      setLastLoaded(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function confirmSelectedAction() {
    if (!selectedAction || !preview?.confirmation_token) return;
    setBusy(true);
    try {
      const result = await confirmAiwebOsLifecycleAction(selectedAction.action, tokenInput);
      setConfirmResult(result);
      setError('');
      setLastLoaded(new Date().toLocaleTimeString());
      if (result.status === 'CONFIRMED' && result.close_operator_window_in_browser) {
        window.setTimeout(() => window.close(), 350);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="operator-life-menu">
      <button
        className={open ? 'operator-life-trigger active' : 'operator-life-trigger'}
        onClick={() => {
          const next = !open;
          setOpen(next);
          setMode(next ? 'status' : 'closed');
        }}
        aria-expanded={open}
      >
        Operator Menu
      </button>

      {open && (
        <section className="operator-life-popover" aria-label="AI.Web OS lifecycle menu">
          <div className="operator-life-header">
            <div>
              <div className="operator-life-eyebrow">AI.Web OS Lifecycle</div>
              <h2>Operator Controls</h2>
            </div>
            <button className="operator-life-close" onClick={() => { setOpen(false); setMode('closed'); }}>×</button>
          </div>

          <div className="operator-life-command-row">
            <button onClick={() => void showStatus()} disabled={busy}>Status</button>
            <button onClick={() => void showLogs()} disabled={busy}>View Logs</button>
            {ACTIONS.map((item) => (
              <button
                key={item.action}
                className={`operator-life-action-${item.tone}`}
                onClick={() => void beginAction(item)}
                disabled={busy}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="operator-life-contract-grid">
            <MiniProof label="Routes" value={routeCount} />
            <MiniProof label="Forge governs" value={boundary?.forge_governs} />
            <MiniProof label="Browser shell" value={boundary?.browser_executes_shell} goodWhenFalse />
            <MiniProof label="Arbitrary command" value={boundary?.browser_executes_arbitrary_command} goodWhenFalse />
            <MiniProof label="Identity write" value={boundary?.identity_vault_write} goodWhenFalse />
            <MiniProof label="RMC write" value={boundary?.rmc_live_memory_write} goodWhenFalse />
          </div>

          {error && <div className="operator-life-error">{error}</div>}
          {busy && <div className="operator-life-loading">Loading controlled lifecycle surface…</div>}

          {mode === 'status' && (
            <div className="operator-life-body">
              <div className="operator-life-status-grid">
                <div className="operator-life-card">
                  <span>Status</span>
                  <strong className={statusTone(status?.status)}>{asText(status?.status)}</strong>
                </div>
                <div className="operator-life-card">
                  <span>Appctl</span>
                  <strong className={statusTone(status?.appctl_status?.status)}>{asText(status?.appctl_status?.status)}</strong>
                </div>
                <div className="operator-life-card">
                  <span>Mode</span>
                  <strong>{asText(status?.mode)}</strong>
                </div>
                <div className="operator-life-card">
                  <span>Last loaded</span>
                  <strong>{lastLoaded}</strong>
                </div>
              </div>
              <pre className="operator-life-pre">{stdoutSummary(status).join('\n') || 'No AI.Web OS status output loaded yet.'}</pre>
            </div>
          )}

          {mode === 'logs' && (
            <div className="operator-life-body operator-life-logs">
              <div className="operator-life-log-head">
                <span>Files: {logs?.file_count ?? 0}</span>
                <span>Read-only: {asText(logs?.read_only)}</span>
                <span>Executes command: {asText(logs?.executes_command)}</span>
              </div>
              {(logs?.files || []).map((file) => (
                <details key={file.path} className="operator-life-log-file">
                  <summary>{file.name} · {file.size_bytes} bytes</summary>
                  <pre>{file.tail_lines.join('\n') || 'No lines returned.'}</pre>
                </details>
              ))}
              {(logs?.files || []).length === 0 && <p className="operator-life-muted">No lifecycle logs found yet.</p>}
            </div>
          )}

          {mode === 'action' && selectedAction && (
            <div className="operator-life-body">
              <div className={`operator-life-danger-card operator-life-danger-${selectedAction.tone}`}>
                <span>{selectedAction.label}</span>
                <strong>{preview?.status ?? 'Preview loading'}</strong>
                <p>{selectedAction.description}</p>
              </div>
              <ul className="operator-life-effects">
                {(preview?.effects || []).map((effect) => <li key={effect}>{effect}</li>)}
              </ul>
              <label className="operator-life-token-label">
                Type exact confirmation token
                <code>{preview?.confirmation_token || 'TOKEN_NOT_LOADED'}</code>
                <input
                  value={tokenInput}
                  onChange={(event) => setTokenInput(event.target.value)}
                  placeholder="confirmation token"
                  spellCheck={false}
                />
              </label>
              <button
                className="operator-life-confirm-button"
                disabled={busy || !tokenMatches}
                onClick={() => void confirmSelectedAction()}
              >
                Confirm {selectedAction.label}
              </button>
              {confirmResult && (
                <div className="operator-life-confirm-result">
                  <strong className={statusTone(confirmResult.status)}>{confirmResult.status}</strong>
                  <span>{confirmResult.message || confirmResult.reason || 'No message returned.'}</span>
                  <pre>{JSON.stringify(confirmResult.scheduled_result || {}, null, 2)}</pre>
                </div>
              )}
            </div>
          )}

          <p className="operator-life-note">
            Patch 263S: final-product lifecycle controls are preview-first and token-gated. The browser receives no shell, no arbitrary command input, and no authority over Forge, RMC memory, Chroma, or Identity Vault.
          </p>
        </section>
      )}
    </div>
  );
}
