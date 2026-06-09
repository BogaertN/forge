export function StatusBadge({
  label,
  value,
  good = true,
}: {
  label: string;
  value: string | number | boolean | null | undefined;
  good?: boolean;
}) {
  return (
    <div className="status-badge">
      <span>{label}</span>
      <strong className={good ? 'good' : 'warn'}>{String(value ?? '—')}</strong>
    </div>
  );
}
