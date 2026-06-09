import { useEffect, useState } from 'react';
import { askForgeOperator } from '../api/forgeClient';
import type { ForgeLlmRequestRecord } from '../api/types';

export function AskForgeRequest({
  onResult,
}: {
  onResult: (record: ForgeLlmRequestRecord) => void;
}) {
  const [request, setRequest] = useState('What should we wire next in the Operator Console?');
  const [running, setRunning] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [captureDataset, setCaptureDataset] = useState(false);

  useEffect(() => {
    function handleFocus(event: Event) {
      const detail = (event as CustomEvent<{ enableCapture?: boolean }>).detail;
      if (detail?.enableCapture) setCaptureDataset(true);
      window.setTimeout(() => {
        document.getElementById('ask-forge-block')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        (document.getElementById('ask-forge-request-textarea') as HTMLTextAreaElement | null)?.focus();
      }, 60);
    }
    window.addEventListener('forge-dataset-growth-focus-ask', handleFocus as EventListener);
    return () => window.removeEventListener('forge-dataset-growth-focus-ask', handleFocus as EventListener);
  }, []);

  async function submit() {
    const trimmed = request.trim();
    const requestId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;

    setLocalError(null);

    if (!trimmed) {
      setLocalError('Enter a Forge request first.');
      return;
    }

    setRunning(true);

    try {
      const response = await askForgeOperator(trimmed, captureDataset ? {
        dataset_capture: 'capture',
        dataset_capture_approval: 'CAPTURE_RMC_LLM_TURN',
      } : {});
      onResult({
        id: requestId,
        request: trimmed,
        status: response.status,
        kind: response.kind ?? 'unknown',
        response_text: response.response_text ?? JSON.stringify(response, null, 2),
        created_at: new Date().toISOString(),
        boundary: response.boundary,
        dataset_growth_capture: response.dataset_growth_capture,
      });
    } catch (error) {
      onResult({
        id: requestId,
        request: trimmed,
        status: 'CLIENT_ERROR',
        kind: 'client_error',
        response_text: error instanceof Error ? error.message : String(error),
        created_at: new Date().toISOString(),
      });
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="ask-forge-runner" id="ask-forge-block">
      <div className="runner-header">
        <div>
          <div className="card-key">Ask Forge</div>
          <p>
            Uses the Forge-governed <code>/api/operator/llm-request</code> bridge. The model returns a plan/proposal only.
          </p>
        </div>
        <div className="runner-mode runner-safe">plan only</div>
      </div>

      <label>
        Natural-language request
        <textarea
          value={request}
          onChange={(event) => {
            setRequest(event.target.value);
            setLocalError(null);
          }}
          placeholder="Ask Forge for a plan. It will not execute commands."
          rows={4}
          id="ask-forge-request-textarea"
        />
      </label>

      <label className="ask-forge-dataset-capture">
        <input
          id="ask-forge-dataset-capture"
          type="checkbox"
          checked={captureDataset}
          onChange={(event) => setCaptureDataset(event.target.checked)}
        />
        Queue this Ask Forge turn for RMC dataset review
      </label>

      {localError && <div className="error-panel">{localError}</div>}

      <div className="action-row compact-actions">
        <button onClick={submit} disabled={running}>
          {running ? 'Asking Forge…' : captureDataset ? 'Ask Forge + Queue Dataset Review' : 'Ask Forge for Plan'}
        </button>
        <span className="muted">proposal only · no shell · canonical reference stays patch-only</span>
      </div>

      <div className="runner-hints">
        Good requests: <code>plan the next Operator Console patch</code>, <code>how should we verify page capture?</code>
      </div>
    </div>
  );
}
