export function asText(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—';
  }

  if (Array.isArray(value)) {
    return value.length > 0 ? value.map(asText).join(', ') : '—';
  }

  if (typeof value === 'boolean') {
    return value ? 'True' : 'False';
  }

  return String(value);
}

export function boundaryClass(value: unknown, goodWhenFalse = false): string {
  const boolValue = value === true;

  if (goodWhenFalse) {
    return boolValue ? 'bad' : 'good';
  }

  return boolValue ? 'good' : 'warn';
}
