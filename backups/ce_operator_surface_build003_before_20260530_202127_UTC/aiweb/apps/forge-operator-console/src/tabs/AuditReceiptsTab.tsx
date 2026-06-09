export function AuditReceiptsTab() {
  return (
    <section className="tab-page">
      <div className="eyebrow">AUDIT</div>
      <h1>Audit / Receipts</h1>
      <p className="subtitle">Proof trail and rollback surface placeholder.</p>
      <div className="card-grid">
        <div className="panel-card">
          <div className="card-key">Mode</div>
          <div className="card-value">read-only first</div>
        </div>
        <div className="panel-card">
          <div className="card-key">Boundary</div>
          <div className="card-value">No direct writes. No bypassing Forge.</div>
        </div>
      </div>
    </section>
  );
}
