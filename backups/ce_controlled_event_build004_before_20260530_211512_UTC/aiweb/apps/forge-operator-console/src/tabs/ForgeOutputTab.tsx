import { useCallback, useState } from 'react';
import { asText, boundaryClass } from '../api/format';
import { getOperatorOutputState } from '../api/forgeClient';
import type { ForgeCommandRunRecord, ForgeLlmRequestRecord, OperatorOutputSlot, OperatorOutputStateResponse } from '../api/types';
import { useAsyncData } from '../api/useAsyncData';
import { AskForgeRequest } from '../forge/AskForgeRequest';
import { AuditReceiptPanel } from '../forge/AuditReceiptPanel';
import { PageCapturePanel } from '../forge/PageCapturePanel';
import { PatchWorkflowPanel } from '../forge/PatchWorkflowPanel';
import { SafeCommandRunner } from '../forge/SafeCommandRunner';

function OutputSlotCard({ slot }: { slot: OperatorOutputSlot }) {
  return (
    <div className="output-slot">
      <div className="output-slot-header">
        <span>{slot.title}</span>
        <strong>{slot.status}</strong>
      </div>
      <pre>{slot.body}</pre>
    </div>
  );
}

function CommandResultCard({ record }: { record: ForgeCommandRunRecord }) {
  return (
    <div className="output-slot command-result-card">
      <div className="output-slot-header">
        <span>{record.command}</span>
        <strong>{record.status}</strong>
      </div>
      <div className="mini-report-path">
        {record.created_at} · {record.safe_mode}{record.gate ? ` · gate: ${record.gate}` : ''}
      </div>
      <pre>{record.output}</pre>
    </div>
  );
}

function LlmResultCard({ record }: { record: ForgeLlmRequestRecord }) {
  return (
    <div className="output-slot llm-result-card">
      <div className="output-slot-header">
        <span>Ask Forge: {record.request}</span>
        <strong>{record.status}</strong>
      </div>
      <div className="mini-report-path">
        {record.created_at} · {record.kind}
      </div>
      {record.dataset_growth_capture && (
        <div className="mini-report-path dataset-capture-line">
          dataset: {String(record.dataset_growth_capture.status ?? 'UNKNOWN')} · canonical write: {String(record.dataset_growth_capture.canonical_reference_write_allowed ?? false)}
        </div>
      )}
      <pre>{record.response_text}</pre>
    </div>
  );
}

export function ForgeOutputTab() {
  const loader = useCallback(() => getOperatorOutputState(), []);
  const state = useAsyncData<OperatorOutputStateResponse>(loader);
  const [commandHistory, setCommandHistory] = useState<ForgeCommandRunRecord[]>([]);
  const [llmHistory, setLlmHistory] = useState<ForgeLlmRequestRecord[]>([]);
  const data = state.data;
  const forgeData = data?.forge_status?.data;
  const visibleOutputSlots = (data?.output_slots ?? []).filter((slot) => slot.id !== 'rmc_dataset_growth_slot');
  const auditLines = data?.audit_tail?.lines ?? [];

  function handleCommandResult(record: ForgeCommandRunRecord) {
    setCommandHistory((existing) => [record, ...existing].slice(0, 20));
    state.reload();
  }

  function handleLlmResult(record: ForgeLlmRequestRecord) {
    setLlmHistory((existing) => [record, ...existing].slice(0, 10));
    state.reload();
  }

  return (
    <section className="tab-page">
      <div className="eyebrow">FORGE</div>
      <h1>Forge Output</h1>
      <p className="subtitle">
        Live output cockpit. Safe/gated commands and natural-language planning now route through Forge-governed bridges.
      </p>

      <div className="action-row">
        <button onClick={state.reload}>Refresh Forge Output State</button>
        <span className="muted">{state.loading ? 'loading…' : 'operator output live'}</span>
      </div>

      {state.error && <div className="error-panel">Forge output state error: {state.error}</div>}

      <div className="status-grid">
        <div className="status-badge">
          <span>Status</span>
          <strong className={data?.status === 'OK' ? 'good' : 'warn'}>{asText(data?.status)}</strong>
        </div>
        <div className="status-badge">
          <span>Trust</span>
          <strong>{asText(forgeData?.trust)}</strong>
        </div>
        <div className="status-badge">
          <span>Commands</span>
          <strong>{asText(forgeData?.cmd_count)}</strong>
        </div>
        <div className="status-badge">
          <span>Next</span>
          <strong>{asText(data?.summary.next_patch)}</strong>
        </div>
      </div>

      <div className="forge-output-layout">
        <div className="panel-card output-main">
          <SafeCommandRunner bridge={data?.browser_command_bridge} onResult={handleCommandResult} />
          <AskForgeRequest onResult={handleLlmResult} />
          <PageCapturePanel />
          <PatchWorkflowPanel />
          <AuditReceiptPanel />

          <div className="card-key command-history-title">LLM / Natural-Language Results</div>
          <div className="output-slot-list llm-history-list">
            {llmHistory.length > 0
              ? llmHistory.map((record) => <LlmResultCard key={record.id} record={record} />)
              : <OutputSlotCard slot={{ id: 'llm-empty', kind: 'llm_result', title: 'LLM / Natural-Language Result Slot', status: 'WAITING_FOR_REQUEST', body: 'Ask Forge for a proposal-only plan. The model cannot execute shell commands or write files from this panel.' }} />}
          </div>

          <div className="card-key command-history-title">Command Results</div>
          <div className="output-slot-list">
            {commandHistory.length > 0
              ? commandHistory.map((record) => <CommandResultCard key={record.id} record={record} />)
              : visibleOutputSlots.map((slot) => <OutputSlotCard key={slot.id} slot={slot} />)}
          </div>
        </div>

        <div className="panel-card output-side">
          <div className="card-key">Authority Boundary</div>
          <div className="card-value">
            <div>read-only state: <span className={boundaryClass(data?.read_only)}>{asText(data?.read_only)}</span></div>
            <div>backend command bridge: <span className="good">existing /api/command only</span></div>
            <div>calls LLM: <span className={boundaryClass(data?.calls_llm, true)}>{asText(data?.calls_llm)}</span></div>
            <div>writes files: <span className={boundaryClass(data?.writes_files, true)}>{asText(data?.writes_files)}</span></div>
            <div>command execution enabled: <span className={boundaryClass(data?.boundary.command_execution_enabled)}>{asText(data?.boundary.command_execution_enabled)}</span></div>
            <div>LLM execution enabled: <span className={boundaryClass(data?.boundary.llm_execution_enabled, true)}>{asText(data?.boundary.llm_execution_enabled)}</span></div>
            <div>LLM request bridge: <span className={boundaryClass(data?.boundary.llm_request_bridge_enabled)}>{asText(data?.boundary.llm_request_bridge_enabled)}</span></div>
            <div>LLM direct tools: <span className={boundaryClass(data?.boundary.llm_direct_tool_execution_enabled, true)}>{asText(data?.boundary.llm_direct_tool_execution_enabled)}</span></div>
            <div>LLM shell: <span className={boundaryClass(data?.boundary.llm_shell_enabled, true)}>{asText(data?.boundary.llm_shell_enabled)}</span></div>
            <div>LLM file writes: <span className={boundaryClass(data?.boundary.llm_file_write_enabled, true)}>{asText(data?.boundary.llm_file_write_enabled)}</span></div>
            <div>page capture: <span className={boundaryClass(data?.boundary.page_capture_enabled)}>{asText(data?.boundary.page_capture_enabled)}</span></div>
            <div>capture write scope: <span className="good">{asText(data?.boundary.page_capture_write_scope)}</span></div>
            <div>capture → Identity Vault: <span className={boundaryClass(data?.boundary.page_capture_identity_vault_write, true)}>{asText(data?.boundary.page_capture_identity_vault_write)}</span></div>
            <div>capture → RMC live memory: <span className={boundaryClass(data?.boundary.page_capture_rmc_live_memory_write, true)}>{asText(data?.boundary.page_capture_rmc_live_memory_write)}</span></div>
            <div>patch workflow: <span className={boundaryClass(data?.boundary.patch_workflow_enabled)}>{asText(data?.boundary.patch_workflow_enabled)}</span></div>
            <div>patch workflow read-only: <span className={boundaryClass(data?.boundary.patch_workflow_read_only)}>{asText(data?.boundary.patch_workflow_read_only)}</span></div>
            <div>patch workflow executes command: <span className={boundaryClass(data?.boundary.patch_workflow_executes_command, true)}>{asText(data?.boundary.patch_workflow_executes_command)}</span></div>
            <div>patch workflow writes files: <span className={boundaryClass(data?.boundary.patch_workflow_writes_files, true)}>{asText(data?.boundary.patch_workflow_writes_files)}</span></div>
            <div>audit receipts: <span className={boundaryClass(data?.boundary.audit_receipts_enabled)}>{asText(data?.boundary.audit_receipts_enabled)}</span></div>
            <div>audit receipts read-only: <span className={boundaryClass(data?.boundary.audit_receipts_read_only)}>{asText(data?.boundary.audit_receipts_read_only)}</span></div>
            <div>audit receipts executes command: <span className={boundaryClass(data?.boundary.audit_receipts_executes_command, true)}>{asText(data?.boundary.audit_receipts_executes_command)}</span></div>
            <div>audit receipts writes files: <span className={boundaryClass(data?.boundary.audit_receipts_writes_files, true)}>{asText(data?.boundary.audit_receipts_writes_files)}</span></div>
          </div>
        </div>

        <div className="panel-card output-side">
          <div className="card-key">Command Bridge Inventory</div>
          <div className="card-value">
            <div>safe commands: {asText(data?.summary.safe_browser_commands)}</div>
            <div>gated commands: {asText(data?.summary.gated_browser_commands)}</div>
            <div>output slots: {asText(data?.summary.output_slots)}</div>
          </div>
        </div>

        <div className="panel-card output-wide">
          <div className="card-key">Recent Audit Tail</div>
          <div className="audit-lines">
            {auditLines.length > 0 ? auditLines.map((line) => <div key={line}>{line}</div>) : '—'}
          </div>
        </div>

        <div className="panel-card output-wide">
          <div className="card-key">Recommended Sequence</div>
          <div className="card-value">
            <ol className="compact-list">
              {(data?.recommended_sequence ?? []).map((item) => <li key={item}>{item}</li>)}
            </ol>
          </div>
        </div>
      </div>
    </section>
  );
}
