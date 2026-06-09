import type { ProtoForgeSummary } from '../api/types';
import { asText, boundaryClass } from '../api/format';

export function SimulationResultPanel({ summary }: { summary: ProtoForgeSummary | null }) {
  return (
    <div className="panel-card">
      <div className="card-key">Latest Result</div>
      <div className="card-value">
        <div>Run ID: {asText(summary?.latest_run_id)}</div>
        <div>
          Run OK:{' '}
          <span className={boundaryClass(summary?.latest_run_ok)}>
            {asText(summary?.latest_run_ok)}
          </span>
        </div>
        <div>Verdict: {asText(summary?.substrate_verdict)}</div>
        <div>Client mode: {asText(summary?.client_mode)}</div>
        <div>Steps: {asText(summary?.steps_recorded)} / {asText(summary?.steps_requested)}</div>
        <div>Fell downward: {asText(summary?.fell_downward)}</div>
      </div>
    </div>
  );
}
