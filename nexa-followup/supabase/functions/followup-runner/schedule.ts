// Reine Zeitlogik, ohne Abhängigkeiten (testbar mit `deno test`).

export interface WindowSettings {
  timezone: string;          // z.B. "Europe/Zurich"
  send_window_start: string; // "08:00" oder "08:00:00"
  send_window_end: string;   // "17:00"
  test_day_minutes?: number | null;
}

const DAY_MS = 86_400_000;
const STEP_MS = 5 * 60_000;

function toMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + (m || 0);
}

function localParts(d: Date, tz: string): { weekday: number; minutes: number } {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: tz, weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  }).formatToParts(d);
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? "";
  const weekday = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(get("weekday"));
  return { weekday, minutes: Number(get("hour")) * 60 + Number(get("minute")) };
}

/** Werktag (Mo–Fr) und innerhalb des Sendefensters, in der lokalen Zeitzone. */
export function isInSendWindow(d: Date, s: WindowSettings): boolean {
  const { weekday, minutes } = localParts(d, s.timezone);
  if (weekday === 0 || weekday === 6) return false;
  return minutes >= toMinutes(s.send_window_start) && minutes < toMinutes(s.send_window_end);
}

/** Nächster erlaubter Sendezeitpunkt ab `d` (inklusive). DST-sicher durch Iteration. */
export function nextSendSlot(d: Date, s: WindowSettings): Date {
  // Auf 5-Minuten-Raster aufrunden, damit Slots sauber auf Fensterbeginn landen.
  let t = new Date(Math.ceil(d.getTime() / STEP_MS) * STEP_MS);
  for (let i = 0; i < (8 * DAY_MS) / STEP_MS; i++) {
    if (isInSendWindow(t, s)) return t;
    t = new Date(t.getTime() + STEP_MS);
  }
  throw new Error("Kein Sendefenster innerhalb von 8 Tagen gefunden. Einstellungen prüfen.");
}

/** Länge eines "Tages" in ms. Im Testmodus komprimierbar (z.B. 1 Tag = 5 Minuten). */
export function dayMs(s: WindowSettings, dryRun: boolean): number {
  return dryRun && s.test_day_minutes ? s.test_day_minutes * 60_000 : DAY_MS;
}

/**
 * Fälligkeit eines Schritts: Erstmail + offset_days Kalendertage, dann ins nächste
 * Sendefenster geschoben. Im komprimierten Testmodus wird das Fenster ignoriert.
 */
export function dueAt(startedAt: Date, offsetDays: number, s: WindowSettings, dryRun: boolean): Date {
  const raw = new Date(startedAt.getTime() + offsetDays * dayMs(s, dryRun));
  if (dryRun && s.test_day_minutes) return raw;
  return nextSendSlot(raw, s);
}
