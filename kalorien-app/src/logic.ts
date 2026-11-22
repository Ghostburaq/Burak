// Reine Rechenlogik ohne React, damit sie direkt mit Node testbar ist.
import type { Food } from './foods';

export type Meal = 'fruehstueck' | 'mittag' | 'abend' | 'snack';

export const MEALS: { key: Meal; label: string }[] = [
  { key: 'fruehstueck', label: 'Frühstück' },
  { key: 'mittag', label: 'Mittagessen' },
  { key: 'abend', label: 'Abendessen' },
  { key: 'snack', label: 'Snacks' },
];

export interface Macros {
  kcal: number;
  protein: number; // g
  carbs: number; // g
  fat: number; // g
}

export interface Entry extends Macros {
  id: string;
  date: string; // YYYY-MM-DD, lokale Zeit
  meal: Meal;
  name: string;
  createdAt: number;
  // Optional, wenn aus der Datenbank erfasst
  grams?: number;
  food?: Food; // Schnappschuss pro 100 g, damit spätere Änderungen alte Einträge nicht verändern
  sugar?: number | null;
  fiber?: number | null;
  salt?: number | null;
}

export type EntryDraft = Omit<Entry, 'id' | 'date' | 'createdAt'>;

export interface Micros {
  sugar: number;
  fiber: number;
  salt: number;
  /** Anzahl Einträge ohne Angabe, damit die Summe als unvollständig erkennbar ist */
  missing: number;
}

export function sumMicros(items: Entry[]): Micros {
  const m: Micros = { sugar: 0, fiber: 0, salt: 0, missing: 0 };
  for (const e of items) {
    if (e.fiber == null && e.sugar == null && e.salt == null) { m.missing++; continue; }
    m.sugar += e.sugar ?? 0;
    m.fiber += e.fiber ?? 0;
    m.salt += e.salt ?? 0;
  }
  return m;
}

export interface Template extends Macros {
  id: string;
  name: string;
}

export type Goals = Macros;

export const ZERO: Macros = { kcal: 0, protein: 0, carbs: 0, fat: 0 };

/** Energie aus Makros nach Atwater-Faktoren: 4 / 4 / 9 kcal pro g. */
export function kcalFromMacros(protein: number, carbs: number, fat: number): number {
  return Math.round(protein * 4 + carbs * 4 + fat * 9);
}

export function sum(items: Macros[]): Macros {
  return items.reduce(
    (acc, e) => ({
      kcal: acc.kcal + e.kcal,
      protein: acc.protein + e.protein,
      carbs: acc.carbs + e.carbs,
      fat: acc.fat + e.fat,
    }),
    { ...ZERO },
  );
}

export function toDateKey(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export function fromDateKey(key: string): Date {
  const [y, m, d] = key.split('-').map(Number);
  return new Date(y, m - 1, d);
}

export function addDays(key: string, n: number): string {
  const d = fromDateKey(key);
  d.setDate(d.getDate() + n);
  return toDateKey(d);
}

/** 22.11.2026 */
export function formatDate(key: string): string {
  const [y, m, d] = key.split('-');
  return `${d}.${m}.${y}`;
}

const WEEKDAYS = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'];
export function weekdayShort(key: string): string {
  return WEEKDAYS[fromDateKey(key).getDay()];
}

/** ISO-8601-Kalenderwoche (Woche beginnt Montag, KW 1 enthält den ersten Donnerstag). */
export function isoWeek(key: string): number {
  const d = fromDateKey(key);
  const day = (d.getDay() + 6) % 7; // Mo = 0
  d.setDate(d.getDate() - day + 3); // Donnerstag dieser Woche
  const firstThursday = new Date(d.getFullYear(), 0, 4);
  const diff = (d.getTime() - firstThursday.getTime()) / 86400000;
  return 1 + Math.round((diff - 3 + ((firstThursday.getDay() + 6) % 7)) / 7);
}

/** Montag bis Sonntag der Woche, in der `key` liegt. */
export function weekDays(key: string): string[] {
  const day = (fromDateKey(key).getDay() + 6) % 7;
  const monday = addDays(key, -day);
  return Array.from({ length: 7 }, (_, i) => addDays(monday, i));
}

export interface WeekStats {
  days: { date: string; totals: Macros }[];
  loggedDays: number;
  /** Durchschnitt nur über Tage mit Einträgen, leere Tage verfälschen sonst den Schnitt. */
  avg: Macros;
}

export function weekStats(entries: Entry[], key: string): WeekStats {
  const days = weekDays(key).map((date) => ({
    date,
    totals: sum(entries.filter((e) => e.date === date)),
  }));
  const logged = days.filter((d) => d.totals.kcal > 0 || d.totals.protein > 0);
  const total = sum(logged.map((d) => d.totals));
  const n = logged.length || 1;
  return {
    days,
    loggedDays: logged.length,
    avg: {
      kcal: Math.round(total.kcal / n),
      protein: Math.round(total.protein / n),
      carbs: Math.round(total.carbs / n),
      fat: Math.round(total.fat / n),
    },
  };
}

/** Zahl aus Eingabefeld, akzeptiert Komma als Dezimaltrenner. Leer oder ungültig = null. */
export function parseNum(s: string): number | null {
  const t = s.trim().replace(',', '.');
  if (t === '') return null;
  const n = Number(t);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

export function round1(n: number): number {
  return Math.round(n * 10) / 10;
}
