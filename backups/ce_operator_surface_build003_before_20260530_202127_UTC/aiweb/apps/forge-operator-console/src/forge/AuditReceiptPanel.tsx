import { useEffect, useState } from 'react';
import { getAuditReceipts } from '../api/forgeClient';
import type { AuditReceiptDirectorySummary, AuditReceiptsResponse } from '../api/types';

function ReceiptDirectoryBlock({ name, directory }: { name: string; directory: AuditReceiptDirectorySummary }) {
  return (
    <div className="audit-receipt-directory">
      <div className="output-slot-header">
        <span>{name}</span>
        <strong>{directory.exists ? `${directory.files_found} files` : 'missing'}</strong>
      </div>
      <div className="mini-report-path">{directory.path}</div>
      {directory.recent_files.length > 0 ? (
        <div className="audit-receipt-file-list">
          {directory.recent_files.slice(0, 5).map((file) => (
            <details key={`${name}-${file.relative_path || file.filename}`} className="audit-receipt-file-item">
              <summary>
                <span>{file.filename || 'unknown file'}</span>
                <small>{file.modified_at || '—'} · {file.size_bytes ?? 0} bytes</small>
              </summary>
              <div className="mini-report-path">{file.relative_path || file.directory || ''}</div>
              <pre>{file.preview || file.error || 'No preview.'}</pre>
            </details>
          ))}
        </div>
      ) : (
        <div className="muted small-note">No recent files found here.</div>
      )}
    </div>
  );
}

export function AuditReceiptPanel() {
  const [data, setData] = useState<AuditReceiptsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function reload() {
    setLoading(true);
    setError('');
    try {
      const response = await getAuditReceipts();
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  return (
    <div className="audit-receipt-panel">
      <div className="runner-header">
        <div>
          <div className="card-key">Audit / Receipt Full Panel</div>
          <p>Reads Forge audit tail, receipt directories, and proof previews through <code>/api/operator/audit-receipts</code>.</p>
        </div>
        <span className="runner-mode runner-safe">READ ONLY</span>
      </div>

      <div className="page-capture-row">
        <button disabled={loading} onClick={() => void reload()}>{loading ? 'Refreshing…' : 'Refresh Audit / Receipts'}</button>
        <span className="runner-hints">No command execution. No shell. No file writes from this panel.</span>
      </div>

      {error && <div className="error-panel">Audit / receipt panel error: {error}</div>}

      {data && (
        <>
          <div className="audit-receipt-summary">
            <div><span>Audit Lines</span><strong>{data.summary.audit_lines_total}</strong></div>
            <div><span>Tail Lines</span><strong>{data.summary.audit_tail_lines}</strong></div>
            <div><span>Receipt Files</span><strong>{data.summary.receipt_files_found}</strong></div>
            <div><span>Next</span><strong>{data.summary.next_patch}</strong></div>
          </div>

          <div className="audit-tail-full-panel">
            <div className="output-slot-header">
              <span>Audit Tail</span>
              <strong>{data.audit.exists ? `${data.audit.size_bytes} bytes` : 'missing'}</strong>
            </div>
            <div className="mini-report-path">{data.audit.path}</div>
            <div className="audit-lines audit-lines-large">
              {data.audit.tail.length > 0 ? data.audit.tail.map((line, index) => <div key={`${index}-${line}`}>{line}</div>) : '—'}
            </div>
          </div>

          <div className="audit-receipt-directory-grid">
            {Object.entries(data.receipt_directories).map(([name, directory]) => (
              <ReceiptDirectoryBlock key={name} name={name} directory={directory} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
