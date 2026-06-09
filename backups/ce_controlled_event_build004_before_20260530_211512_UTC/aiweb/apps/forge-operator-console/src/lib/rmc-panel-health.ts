// Patch 262-UI-MemoryPanel-P4
// UI endpoint-health helpers for partial-load-safe RMC Memory Panel rendering.
// This module is UI-only. It performs no network calls, writes, shell execution, or authority decisions.

export type EndpointHealth = {
  key: string;
  ok: boolean;
  status: 'OK' | 'FAILED';
  error: string | null;
  checked_at_utc: string;
};

export type EndpointHealthMap = Record<string, EndpointHealth>;

function cleanKey(value: unknown): string {
  return typeof value === 'string' && value.trim() ? value.trim() : 'unknown_endpoint';
}

function cleanError(value: unknown): string | null {
  if (value === null || value === undefined || value === '') return null;
  return String(value).slice(0, 500);
}

export function makeEndpointHealth(key: string, ok: boolean, error: unknown = null, checkedAtUtc?: string): EndpointHealth {
  return {
    key: cleanKey(key),
    ok: Boolean(ok),
    status: ok ? 'OK' : 'FAILED',
    error: ok ? null : cleanError(error),
    checked_at_utc: checkedAtUtc || new Date().toISOString(),
  };
}

export function summarizeEndpointHealth(map: EndpointHealthMap | null | undefined) {
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
