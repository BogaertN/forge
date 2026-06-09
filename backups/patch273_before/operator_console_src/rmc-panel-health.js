// Patch 262-UI-MemoryPanel-P4
// CommonJS compatibility copy of UI endpoint-health helpers for verifier execution.

function cleanKey(value) {
  return typeof value === 'string' && value.trim() ? value.trim() : 'unknown_endpoint';
}

function cleanError(value) {
  if (value === null || value === undefined || value === '') return null;
  return String(value).slice(0, 500);
}

function makeEndpointHealth(key, ok, error, checkedAtUtc) {
  return {
    key: cleanKey(key),
    ok: Boolean(ok),
    status: ok ? 'OK' : 'FAILED',
    error: ok ? null : cleanError(error),
    checked_at_utc: checkedAtUtc || new Date().toISOString(),
  };
}

function summarizeEndpointHealth(map) {
  const entries = Object.values(map || {});
  const total = entries.length;
  const failed = entries.filter((entry) => !entry.ok).length;
  const ok = total - failed;
  return {
    total,
    ok,
    failed,
    degraded: failed > 0,
    all_ok: total > 0 && failed === 0,
  };
}

module.exports = {
  makeEndpointHealth,
  summarizeEndpointHealth,
};
