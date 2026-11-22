// Bedarfsrechnung, Makroverteilung, Gewichtstrend und adaptiver Verbrauch.
// Reine Funktionen ohne React, getestet in nutrition.test.ts.

import { addDays, fromDateKey, type Entry, type Macros } from './logic';

export type Sex = 'm' | 'w';
export type GoalType = 'lose' | 'maintain' | 'gain';

export interface Profile {
  configured: boolean;
  sex: Sex;
  birthYear: number;
  heightCm: number;
  weightKg: number; // Startgewicht, wird durch Trendgewicht ersetzt, sobald Wiegungen vorliegen
  pal: number; // Aktivitätsfaktor
  goal: GoalType;
  ratePerWeek: number; // kg pro Woche, Betrag
  proteinPerKg: number; // g pro kg Körpergewicht
  fatPct: number; // Anteil Fett an kcal in %
  trainingBonus: number; // kcal Zuschlag an Trainingstagen, geht komplett auf KH
  tdeeOverride: number | null; // übernommener adaptiver Verbrauch
  mode: 'auto' | 'manual';
  manual: Macros;
  waterMl: number | null; // null = Faustregel 35 ml pro kg
}

export const DEFAULT_PROFILE: Profile = {
  configured: false,
  sex: 'm',
  birthYear: 1995,
  heightCm: 180,
  weightKg: 80,
  pal: 1.55,
  goal: 'maintain',
  ratePerWeek: 0.5,
  proteinPerKg: 1.8,
  fatPct: 25,
  trainingBonus: 0,
  tdeeOverride: null,
  mode: 'auto',
  manual: { kcal: 2000, protein: 150, carbs: 200, fat: 70 },
  waterMl: null,
};

// Aktivitätsfaktoren nach der üblichen Harris-Benedict-Staffelung
export const PAL_LEVELS: { value: number; label: string; hint: string }[] = [
  { value: 1.2, label: 'Sitzend', hint: 'Büro, kaum Bewegung' },
  { value: 1.375, label: 'Leicht aktiv', hint: '1–3× Training pro Woche' },
  { value: 1.55, label: 'Mässig aktiv', hint: '3–5× Training pro Woche' },
  { value: 1.725, label: 'Sehr aktiv', hint: '6–7× Training oder körperliche Arbeit' },
  { value: 1.9, label: 'Extrem aktiv', hint: 'Harte körperliche Arbeit plus Training' },
];

/** Näherung: 1 kg Körpergewichtsänderung entspricht rund 7700 kcal. */
export const KCAL_PER_KG = 7700;

export function ageFromBirthYear(birthYear: number, now = new Date()): number {
  return now.getFullYear() - birthYear;
}

/** Grundumsatz nach Mifflin-St Jeor (1990). */
export function bmrMifflin(sex: Sex, weightKg: number, heightCm: number, age: number): number {
  return 10 * weightKg + 6.25 * heightCm - 5 * age + (sex === 'm' ? 5 : -161);
}

export interface Calc {
  weightUsed: number;
  bmr: number;
  tdeeFormula: number;
  tdee: number; // verwendet: Override oder Formel
  tdeeSource: 'formel' | 'adaptiv';
  adjustment: number; // kcal pro Tag aus Ziel
  base: Macros; // Ruhetag
  training: Macros; // Trainingstag
  waterMl: number;
  warnings: string[];
}

export function calculate(p: Profile, currentWeight: number | null, now = new Date()): Calc {
  const w = currentWeight ?? p.weightKg;
  const age = ageFromBirthYear(p.birthYear, now);
  const bmr = bmrMifflin(p.sex, w, p.heightCm, age);
  const tdeeFormula = bmr * p.pal;
  const tdee = p.tdeeOverride ?? tdeeFormula;
  const sign = p.goal === 'lose' ? -1 : p.goal === 'gain' ? 1 : 0;
  const adjustment = (sign * p.ratePerWeek * KCAL_PER_KG) / 7;
  const warnings: string[] = [];
  const waterMl = p.waterMl ?? Math.round((w * 35) / 250) * 250;

  if (p.mode === 'manual') {
    const base = p.manual;
    const training = { ...base, kcal: base.kcal + p.trainingBonus, carbs: base.carbs + p.trainingBonus / 4 };
    return { weightUsed: w, bmr, tdeeFormula, tdee, tdeeSource: p.tdeeOverride ? 'adaptiv' : 'formel', adjustment, base, training, waterMl, warnings };
  }

  const kcal = Math.round(tdee + adjustment);
  const split = (k: number): Macros => {
    const protein = Math.round(p.proteinPerKg * w);
    const fat = Math.round((k * p.fatPct) / 100 / 9);
    const carbs = Math.max(0, Math.round((k - protein * 4 - fat * 9) / 4));
    return { kcal: k, protein, carbs, fat };
  };
  const base = split(kcal);
  const training = split(kcal + p.trainingBonus);

  if (kcal < bmr) warnings.push(`Ziel (${kcal} kcal) liegt unter deinem Grundumsatz (${Math.round(bmr)} kcal).`);
  if (p.goal === 'lose' && p.ratePerWeek > w * 0.01)
    warnings.push(`Mehr als 1 % Körpergewicht pro Woche (${(w * 0.01).toFixed(1)} kg) ist sehr aggressiv, Muskelverlust wahrscheinlich.`);
  if (p.goal === 'gain' && p.ratePerWeek > 0.5)
    warnings.push('Mehr als 0,5 kg pro Woche Zunahme ist überwiegend Fett, nicht Muskel.');
  if (base.protein * 4 + base.fat * 9 > kcal) warnings.push('Protein und Fett allein übersteigen das Kalorienziel. Protein oder Fettanteil senken.');
  if (p.fatPct < 20) warnings.push('Fettanteil unter 20 % ist auf Dauer knapp (Hormonhaushalt, fettlösliche Vitamine).');

  return { weightUsed: w, bmr, tdeeFormula, tdee, tdeeSource: p.tdeeOverride ? 'adaptiv' : 'formel', adjustment, base, training, waterMl, warnings };
}

// ---------- Gewicht ----------

export type Weights = Record<string, number>; // Datum -> kg

export function sortedWeights(w: Weights): { date: string; kg: number }[] {
  return Object.entries(w)
    .map(([date, kg]) => ({ date, kg }))
    .sort((a, b) => (a.date < b.date ? -1 : 1));
}

/** Trendgewicht: Mittel aller Wiegungen der 7 Tage bis einschliesslich `date`. */
export function trendAt(w: Weights, date: string): number | null {
  const from = addDays(date, -6);
  const vals = Object.entries(w).filter(([d]) => d >= from && d <= date).map(([, kg]) => kg);
  if (!vals.length) return null;
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

/** Aktuellstes Trendgewicht, bezogen auf die letzte Wiegung. */
export function currentTrend(w: Weights): number | null {
  const s = sortedWeights(w);
  return s.length ? trendAt(w, s[s.length - 1].date) : null;
}

const dayIndex = (d: string) => Math.round(fromDateKey(d).getTime() / 86400000);

/** Steigung in kg pro Tag per linearer Regression. */
export function slopePerDay(points: { date: string; kg: number }[]): number | null {
  if (points.length < 2) return null;
  const xs = points.map((p) => dayIndex(p.date));
  const ys = points.map((p) => p.kg);
  const mx = xs.reduce((a, b) => a + b, 0) / xs.length;
  const my = ys.reduce((a, b) => a + b, 0) / ys.length;
  let num = 0, den = 0;
  for (let i = 0; i < xs.length; i++) {
    num += (xs[i] - mx) * (ys[i] - my);
    den += (xs[i] - mx) ** 2;
  }
  return den === 0 ? null : num / den;
}

export interface Adaptive {
  ok: boolean;
  reason?: string;
  tdee?: number;
  avgIntake?: number;
  kgPerWeek?: number;
  loggedDays: number;
  weighIns: number;
  windowDays: number;
}

/**
 * Tatsächlicher Verbrauch aus deinen Daten: Durchschnittszufuhr minus Energie,
 * die in Gewichtsänderung geflossen ist. Fenster endet gestern, weil heute noch läuft.
 */
export function adaptiveTdee(entries: Entry[], weights: Weights, today: string, windowDays = 21): Adaptive {
  const end = addDays(today, -1);
  const start = addDays(end, -(windowDays - 1));
  const perDay = new Map<string, number>();
  for (const e of entries) {
    if (e.date >= start && e.date <= end) perDay.set(e.date, (perDay.get(e.date) ?? 0) + e.kcal);
  }
  const logged = [...perDay.values()].filter((k) => k > 0);
  const pts = sortedWeights(weights).filter((p) => p.date >= start && p.date <= end);
  const base = { loggedDays: logged.length, weighIns: pts.length, windowDays };

  if (logged.length < 10) return { ...base, ok: false, reason: `Mindestens 10 erfasste Tage in den letzten ${windowDays} Tagen nötig (aktuell ${logged.length}).` };
  if (pts.length < 4) return { ...base, ok: false, reason: `Mindestens 4 Wiegungen in den letzten ${windowDays} Tagen nötig (aktuell ${pts.length}).` };
  const span = dayIndex(pts[pts.length - 1].date) - dayIndex(pts[0].date);
  if (span < 10) return { ...base, ok: false, reason: 'Wiegungen müssen mindestens 10 Tage auseinanderliegen.' };

  const slope = slopePerDay(pts)!;
  const avgIntake = logged.reduce((a, b) => a + b, 0) / logged.length;
  const tdee = avgIntake - slope * KCAL_PER_KG;
  return { ...base, ok: true, tdee: Math.round(tdee), avgIntake: Math.round(avgIntake), kgPerWeek: slope * 7 };
}
