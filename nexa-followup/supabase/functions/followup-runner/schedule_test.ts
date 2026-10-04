import { assertEquals } from "jsr:@std/assert";
import { dueAt, isInSendWindow, nextSendSlot } from "./schedule.ts";

const s = { timezone: "Europe/Zurich", send_window_start: "08:00", send_window_end: "17:00" };

Deno.test("Werktag 10:00 Zürich liegt im Fenster", () => {
  assertEquals(isInSendWindow(new Date("2026-10-06T08:00:00Z"), s), true); // Di 10:00 MESZ
});

Deno.test("Samstag liegt nicht im Fenster", () => {
  assertEquals(isInSendWindow(new Date("2026-10-10T08:00:00Z"), s), false);
});

Deno.test("Freitag 18:00 schiebt auf Montag 08:00 Zürich", () => {
  const slot = nextSendSlot(new Date("2026-10-09T16:00:00Z"), s); // Fr 18:00 MESZ
  assertEquals(slot.toISOString(), "2026-10-12T06:00:00.000Z");   // Mo 08:00 MESZ
});

Deno.test("Follow-up 1: Erstmail Do 14:00, +4 Tage = Mo 14:00", () => {
  const due = dueAt(new Date("2026-10-08T12:00:00Z"), 4, s, false);
  assertEquals(due.toISOString(), "2026-10-12T12:00:00.000Z");
});

Deno.test("Follow-up 2: Erstmail Mo 09:00, +9 Tage = Mi 08:00 (über Zeitumstellung)", () => {
  // Zeitumstellung CH: 25.10.2026. Mo 19.10. 09:00 MESZ = 07:00Z; Mi 28.10. 09:00 MEZ = 08:00Z.
  // Kalendertage x 24h ergibt 08:00 MEZ (07:00Z) und liegt damit im Fenster.
  const due = dueAt(new Date("2026-10-19T07:00:00Z"), 9, s, false);
  assertEquals(due.toISOString(), "2026-10-28T07:00:00.000Z");
});

Deno.test("Fälligkeit am Sonntag schiebt auf Montag", () => {
  const due = dueAt(new Date("2026-10-07T10:00:00Z"), 4, s, false); // Mi -> So
  assertEquals(due.toISOString(), "2026-10-12T06:00:00.000Z");
});

Deno.test("Testmodus komprimiert: 1 Tag = 5 Minuten", () => {
  const t = { ...s, test_day_minutes: 5 };
  const due = dueAt(new Date("2026-10-10T08:00:00Z"), 4, t, true);
  assertEquals(due.toISOString(), "2026-10-10T08:20:00.000Z");
});
