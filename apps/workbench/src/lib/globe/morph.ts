export type GlobeMorphPayload = {
  image: string;
  focusX: number;
  focusY: number;
};

const KEY = 'fc-globe-morph';

export function saveGlobeMorph(payload: GlobeMorphPayload): void {
  try {
    window.sessionStorage.setItem(KEY, JSON.stringify(payload));
  } catch {
    // A blocked storage API only removes the transition; navigation still works.
  }
}

export function takeGlobeMorph(): GlobeMorphPayload | null {
  try {
    const stored = window.sessionStorage.getItem(KEY);
    if (!stored) return null;
    window.sessionStorage.removeItem(KEY);
    const parsed = JSON.parse(stored) as Partial<GlobeMorphPayload>;
    if (typeof parsed.image !== 'string' || !parsed.image.startsWith('data:image/')) return null;
    const clamp = (value: number) => Math.min(1, Math.max(0, value));
    return {
      image: parsed.image,
      focusX: typeof parsed.focusX === 'number' ? clamp(parsed.focusX) : 0.5,
      focusY: typeof parsed.focusY === 'number' ? clamp(parsed.focusY) : 0.5,
    };
  } catch {
    return null;
  }
}
