import type { ProtoForgeSummary } from '../api/types';
import { asText } from '../api/format';

export function SimulationPlanner({ summary }: { summary: ProtoForgeSummary | null }) {
  const allowedTypes = summary?.allowed_types ?? [];

  return (
    <div className="panel-card">
      <div className="card-key">Simulation Planner</div>
      <div className="card-value">
        <div>Allowed types:</div>
        <ul className="compact-list">
          {allowedTypes.length > 0
            ? allowedTypes.map((type) => <li key={type}>{type}</li>)
            : <li>—</li>}
        </ul>
        <div className="muted">Latest plan: {asText(summary?.latest_plan_id)}</div>
        <div className="muted">Plan type: {asText(summary?.latest_plan_type)}</div>
      </div>
    </div>
  );
}
