export interface TracePoint {
  step: number;
  t: number;
  x: number;
  y: number;
  z: number;
}

function asNumber(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function extractPosition(frame: Record<string, unknown>): { x: number; y: number; z: number } {
  const position = frame.position;

  if (Array.isArray(position)) {
    return {
      x: asNumber(position[0], 0),
      y: asNumber(position[1], 0),
      z: asNumber(position[2], 0),
    };
  }

  if (position && typeof position === 'object') {
    const record = position as Record<string, unknown>;
    return {
      x: asNumber(record.x, 0),
      y: asNumber(record.y, 0),
      z: asNumber(record.z, 0),
    };
  }

  return {
    x: asNumber(frame.x, 0),
    y: asNumber(frame.y, 0),
    z: asNumber(frame.z, 0),
  };
}

export function normalizeTrace(raw: unknown): TracePoint[] {
  let frames: unknown[] = [];

  if (Array.isArray(raw)) {
    frames = raw;
  } else if (raw && typeof raw === 'object') {
    const record = raw as Record<string, unknown>;
    for (const key of ['steps', 'trace', 'state_trace', 'frames']) {
      const value = record[key];
      if (Array.isArray(value)) {
        frames = value;
        break;
      }
    }
  }

  return frames
    .filter((frame): frame is Record<string, unknown> => Boolean(frame) && typeof frame === 'object')
    .map((frame, index) => {
      const position = extractPosition(frame);
      return {
        step: asNumber(frame.step, index),
        t: asNumber(frame.t, asNumber(frame.time, index / 60)),
        x: position.x,
        y: position.y,
        z: position.z,
      };
    });
}
