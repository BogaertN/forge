import { useCallback } from 'react';
import { asText, boundaryClass } from '../api/format';
import { getContributionEconomyMeaPreview, getContributionEconomyStatus } from '../api/forgeClient';
import type { ContributionEconomyMeaPreviewResponse, ContributionEconomyStatusResponse } from '../api/types';
import { useAsyncData } from '../api/useAsyncData';
import { StatusBadge } from '../shell/StatusBadge';

function GateLine({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ce-gate-line">
      <span>{label}</span>
      <strong className={boundaryClass(value, true)}>{value === false ? 'BLOCKED' : asText(value)}</strong>
    </div>
  );
}

function CountCard({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ce-count-card">
      <span>{label}</span>
      <strong>{asText(value)}</strong>
    </div>
  );
}

function hashPreview(value: string | null | undefined): string {
  if (!value) return '—';
  return value.length > 22 ? `${value.slice(0, 14)}…${value.slice(-8)}` : value;
}

export function ContributionEconomyTab() {
  const statusLoader = useCallback(() => getContributionEconomyStatus(), []);
  const previewLoader = useCallback(() => getContributionEconomyMeaPreview(), []);
  const statusState = useAsyncData<ContributionEconomyStatusResponse>(statusLoader);
  const previewState = useAsyncData<ContributionEconomyMeaPreviewResponse>(previewLoader);

  const data = statusState.data;
  const preview = previewState.data?.preview;
  const coreCounts = data?.integrated_core?.row_counts ?? {};

  return (
    <section className="tab-page ce-operator-tab">
      <div className="eyebrow">CONTRIBUTION ECONOMY</div>
      <h1>Contribution Economy Operator Surface</h1>
      <p className="subtitle">
        Read-only integration view from <code>/api/contribution-economy/status</code> and the MEA capsule compatibility preview.
        Identity Vault authorizes; Forge governs; economic gates remain blocked.
      </p>

      <div className="action-row">
        <button onClick={statusState.reload}>Refresh Contribution Economy</button>
        <button onClick={previewState.reload}>Refresh MEA Preview</button>
        <span className="muted">
          {statusState.loading || previewState.loading ? 'loading…' : 'read-only · no write controls'}
        </span>
      </div>

      {(statusState.error || previewState.error || data?.error || previewState.data?.error) && (
        <div className="error-panel">
          {statusState.error && <div>Status error: {statusState.error}</div>}
          {previewState.error && <div>MEA preview error: {previewState.error}</div>}
          {data?.error && <div>Backend status error: {data.error}</div>}
          {previewState.data?.error && <div>Backend preview error: {previewState.data.error}</div>}
        </div>
      )}

      <div className="status-grid">
        <StatusBadge label="Subsystem" value={data?.status ?? '—'} good={data?.status === 'OK'} />
        <StatusBadge label="Principals" value={data?.identity_authority?.registered_principal_count ?? '—'} />
        <StatusBadge label="Contribution Events" value={coreCounts.contribution_events ?? '—'} />
        <StatusBadge label="Capsule Candidates" value={coreCounts.memory_capsule_candidates ?? '—'} />
        <StatusBadge label="CT Mint Events" value={coreCounts.ct_mint_events ?? '—'} />
        <StatusBadge label="UI Bridge" value={data?.operator_visibility?.read_only_routes_enabled ? 'READ-ONLY' : '—'} good={data?.operator_visibility?.read_only_routes_enabled === true} />
      </div>

      <div className="ce-panel-grid">
        <div className="panel-card">
          <div className="card-key">Identity Vault Authority</div>
          <div className="card-value">
            <div>multi-user schema: <span className={data?.identity_authority_schema?.verified ? 'good' : 'warn'}>{asText(data?.identity_authority_schema?.verified)}</span></div>
            <div>private-only principals: {asText(data?.identity_authority?.private_identity_vault_only_principal_count)}</div>
            <div>all principals private-only: <span className={data?.identity_authority?.all_principals_private_only ? 'good' : 'warn'}>{asText(data?.identity_authority?.all_principals_private_only)}</span></div>
            <div>public grants: {asText(data?.identity_authority?.public_display_authorization_event_count)}</div>
            <div>economic grants: {asText(data?.identity_authority?.economic_authorization_event_count)}</div>
            <div>raw identity exported: <span className={boundaryClass(data?.identity_authority?.raw_private_identity_exported, true)}>{asText(data?.identity_authority?.raw_private_identity_exported)}</span></div>
          </div>
        </div>

        <div className="panel-card">
          <div className="card-key">Economic Gates</div>
          <div className="card-value ce-gates">
            <GateLine label="Capsule finalization" value={data?.economic_gates?.capsule_finalization_enabled} />
            <GateLine label="CT minting" value={data?.economic_gates?.ct_minting_enabled} />
            <GateLine label="Influence write" value={data?.economic_gates?.influence_ledger_writes_enabled} />
            <GateLine label="Investment write" value={data?.economic_gates?.investment_ledger_writes_enabled} />
            <GateLine label="Money creates CT" value={data?.economic_gates?.money_creates_ct} />
          </div>
        </div>

        <div className="panel-card wide">
          <div className="card-key">Integrated Core — Persisted Record Counts</div>
          <div className="ce-count-grid">
            <CountCard label="Events" value={coreCounts.contribution_events} />
            <CountCard label="Capsule Candidates" value={coreCounts.memory_capsule_candidates} />
            <CountCard label="Validation Records" value={coreCounts.capsule_validation_records} />
            <CountCard label="Finalization Receipts" value={coreCounts.capsule_finalization_receipts} />
            <CountCard label="CT Mint Events" value={coreCounts.ct_mint_events} />
            <CountCard label="Corrections" value={coreCounts.nullification_correction_events} />
          </div>
          <div className="ce-core-boundary">
            <div>live event persistence: <span className={boundaryClass(data?.integrated_core?.live_event_persistence_enabled, true)}>{asText(data?.integrated_core?.live_event_persistence_enabled)}</span></div>
            <div>capsule finalization: <span className={boundaryClass(data?.integrated_core?.capsule_finalization_enabled, true)}>{asText(data?.integrated_core?.capsule_finalization_enabled)}</span></div>
            <div>CT minting: <span className={boundaryClass(data?.integrated_core?.ct_minting_enabled, true)}>{asText(data?.integrated_core?.ct_minting_enabled)}</span></div>
            <div>ledger writes: <span className={boundaryClass(data?.integrated_core?.ledger_write_enabled, true)}>{asText(data?.integrated_core?.ledger_write_enabled)}</span></div>
          </div>
        </div>

        <div className="panel-card">
          <div className="card-key">Influence Ledger</div>
          <div className="card-value">
            <div>total entries: <strong>{asText(data?.ledgers?.influence_total_entries)}</strong></div>
            {Object.entries(data?.ledgers?.influence_row_counts ?? {}).map(([key, value]) => (
              <div key={key}>{key}: {asText(value)}</div>
            ))}
          </div>
        </div>

        <div className="panel-card">
          <div className="card-key">Investment Ledger</div>
          <div className="card-value">
            <div>total entries: <strong>{asText(data?.ledgers?.investment_total_entries)}</strong></div>
            {Object.entries(data?.ledgers?.investment_row_counts ?? {}).map(([key, value]) => (
              <div key={key}>{key}: {asText(value)}</div>
            ))}
            <div>money creates CT: <span className={boundaryClass(data?.ledgers?.money_creates_ct, true)}>{asText(data?.ledgers?.money_creates_ct)}</span></div>
          </div>
        </div>

        <div className="panel-card wide ce-mea-preview">
          <div className="card-key">MEA → Memory Capsule Compatibility Preview</div>
          <div className="card-value">
            <div>status: <span className={preview?.capsule_status ? 'good' : 'muted'}>{asText(preview?.capsule_status)}</span></div>
            <div>claim status: <strong>{asText(preview?.claim_status)}</strong></div>
            <div>capsule finalized: <span className={boundaryClass(preview?.finalized, true)}>{asText(preview?.finalized)}</span></div>
            <div>contributors attached: {asText(preview?.contributors_count)}</div>
            <div>contributor proof: {asText(preview?.proof_hash)}</div>
            <div>CT status: <span className="warn">{asText(preview?.ct_minting_status)}</span></div>
            <div className="ce-hash-line">source proof: <code>{hashPreview(preview?.source_artifact_proof_hash)}</code></div>
            <div className="ce-hash-line">top-level hash: <code>{hashPreview(preview?.top_level_hash)}</code></div>
            <p className="ce-integrity-note">{asText(preview?.integrity_rule)}</p>
          </div>
        </div>

        <div className="panel-card wide">
          <div className="card-key">Operator Boundary</div>
          <div className="ce-boundary-grid">
            {Object.entries(data?.boundary ?? {}).map(([key, value]) => (
              <div key={key}>
                <span>{key}</span>
                <strong className={boundaryClass(value, key !== 'read_only' && key !== 'forge_governs' && key !== 'identity_vault_authorizes')}>
                  {asText(value)}
                </strong>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
