/** Convert minutes-from-midnight to "HH:MM" (24h). */
export function fmtTime(min: number): string {
  const clamped = Math.max(0, Math.min(1440, Math.round(min)));
  const h = Math.floor(clamped / 60) % 24;
  const m = clamped % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

/** Convert "HH:MM" (24h) to minutes from midnight. Returns NaN on bad input. */
export function parseTime(value: string): number {
  const match = /^(\d{1,2}):(\d{2})$/.exec(value.trim());
  if (!match) return NaN;
  const h = Number(match[1]);
  const m = Number(match[2]);
  if (h < 0 || h > 23 || m < 0 || m > 59) return NaN;
  return h * 60 + m;
}

/** Current local time as "HH:MM". */
export function nowHHMM(): string {
  return fmtTime(new Date().getHours() * 60 + new Date().getMinutes());
}
