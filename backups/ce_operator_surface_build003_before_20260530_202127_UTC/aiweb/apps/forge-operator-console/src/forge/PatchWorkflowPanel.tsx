import { useEffect, useState } from 'react';
import { getPatchWorkflow } from '../api/forgeClient';
import type { PatchWorkflowCommandSpec, PatchWorkflowDirectorySummary, PatchWorkflowResponse } from '../api/types';

function commandMode(command: PatchWorkflowCommandSpec): string {
  if (command.browser_safe) return 'SAFE';
  if (command.browser_gated) return command.gate ? `GATED ${command.gate}` : 'GATED';
  return 'TERMINAL';
}

function DirectoryBlock({ name, directory }: { name: string; directory: PatchWorkflowDirectorySummary }) {
  return (
    <div className="patch-workflow-directory">
      <div className="output-slot-header">
        <span>{name}</span>
        <strong>{directory.exists ? `${directory.files_found} files` : 'missing'}</strong>
      </div>
      <div className="mini-report-path">{directory.path}</div>
      {directory.recent_files.length > 0 ? (
        <div className="patch-file-list">
          {directory.recent_files.slice(0, 5).map((file) => (
            <details key={`${name}-${file.relative_path || file.filename}`} className="patch-file-item">
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

export function PatchWorkflowPanel() {
  const [data, setData] = useState<PatchWorkflowResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function reload() {
    setLoading(true);
    setError('');
    try {
      const response = await getPatchWorkflow();
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
    <div className="patch-workflow-panel">
      <div className="runner-header">
        <div>
          <div className="card-key">Patch / Proposal Workflow</div>
          <p>Reads Forge proposal, apply-plan, rollback, and gate status through <code>/api/operator/patch-workflow</code>.</p>
        </div>
        <span className="runner-mode runner-safe">READ ONLY</span>
      </div>

      <div className="page-capture-row">
        <button disabled={loading} onClick={() => void reload()}>{loading ? 'Refreshing…' : 'Refresh Workflow'}</button>
        <span className="runner-hints">No command execution. No shell. No file writes from this panel.</span>
      </div>

      {error && <div className="error-panel">Patch workflow error: {error}</div>}

      {data && (
        <>
          <div className="patch-workflow-summary">
            <div><span>Proposals</span><strong>{data.summary.proposed_patches_found}</strong></div>
            <div><span>Apply Plans</span><strong>{data.summary.apply_plans_found}</strong></div>
            <div><span>Rollback Entries</span><strong>{data.summary.rollback_entries_found}</strong></div>
            <div><span>Next</span><strong>{data.summary.next_patch}</strong></div>
          </div>

          <div className="patch-command-groups">
            {data.command_groups.map((group) => (
              <div className="patch-command-group" key={group.group}>
                <div className="output-slot-header">
                  <span>{group.group}</span>
                  <strong>{group.commands.length} commands</strong>
                </div>
                <p>{group.description}</p>
                <div className="patch-command-list">
                  {group.commands.map((command) => (
                    <div className={`patch-command-item ${command.browser_gated ? 'gated' : ''}`} key={`${group.group}-${command.command}`}>
                      <code>{command.command}</code>
                      <span>{commandMode(command)}</span>
                      <small>{command.description || ''}</small>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="patch-directory-grid">
            {Object.entries(data.directories).map(([name, directory]) => (
              <DirectoryBlock key={name} name={name} directory={directory} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
