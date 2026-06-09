import type { ProtoForgeSummary } from '../api/types';
import { asText } from '../api/format';

export function ArtifactBrowser({ summary }: { summary: ProtoForgeSummary | null }) {
  const files = summary?.artifact_files ?? [];

  return (
    <div className="panel-card wide">
      <div className="card-key">Artifact Browser</div>
      <div className="card-value">
        <div>Manifest version: {asText(summary?.artifact_manifest_version)}</div>
        <ul className="compact-list">
          {files.length > 0
            ? files.map((file) => <li key={file}>{file}</li>)
            : <li>No artifact list loaded yet.</li>}
        </ul>
      </div>
    </div>
  );
}
