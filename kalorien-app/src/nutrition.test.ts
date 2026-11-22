import { test } from 'node:test';
import assert from 'node:assert/strict';
import { addDays, type Entry } from './logic';
import {
  adaptiveTdee, bmrMifflin, calculate, currentTrend, DEFAULT_PROFILE, slopePerDay, trendAt,
} from './nutrition';

const now = new Date(2026, 10, 22);

test('Mifflin-St Jeor', () => {
  // Mann, 80 kg, 180 cm, 30 J: 800 + 1125 - 150 + 5 = 1780
  assert.equal(bmrMifflin('m', 80, 180, 30), 1780);
  assert.equal(bmrMifflin('w', 60, 165, 30), 600 + 1031.25 - 150 - 161);
});

test('Zielkalorien und Makros im Auto-Modus', () => {
  const p = { ...DEFAULT_PROFILE, birthYear: 1996, goal: 'lose' as const, ratePerWeek: 0.5, pal: 1.55, trainingBonus: 300 };
  const c = calculate(p, null, now);
  assert.equal(c.bmr, 1780);
  assert.equal(Math.round(c.tdee), 2759); // 1780 * 1.55
  assert.equal(Math.round(c.adjustment), -550); // 0.5 * 7700 / 7
  assert.equal(c.base.kcal, 2209);
  assert.equal(c.base.protein, 144); // 1.8 * 80
  assert.equal(c.base.fat, Math.round((2209 * 0.25) / 9));
  assert.equal(c.base.carbs, Math.round((2209 - 144 * 4 - c.base.fat * 9) / 4));
  assert.equal(c.training.kcal, 2509);
  assert.equal(c.training.protein, 144);
  assert.equal(c.warnings.length, 0);
});

test('Warnungen bei aggressivem Defizit', () => {
  const p = { ...DEFAULT_PROFILE, goal: 'lose' as const, ratePerWeek: 1.5, pal: 1.2 };
  const c = calculate(p, 70, now);
  assert.ok(c.warnings.some((w) => w.includes('Grundumsatz')));
  assert.ok(c.warnings.some((w) => w.includes('1 %')));
});

test('Manueller Modus und Override', () => {
  const p = { ...DEFAULT_PROFILE, mode: 'manual' as const, manual: { kcal: 2500, protein: 180, carbs: 250, fat: 80 }, trainingBonus: 200 };
  const c = calculate(p, null, now);
  assert.equal(c.base.kcal, 2500);
  assert.equal(c.training.kcal, 2700);
  assert.equal(c.training.carbs, 300);
  const o = calculate({ ...DEFAULT_PROFILE, tdeeOverride: 3000 }, null, now);
  assert.equal(o.tdee, 3000);
  assert.equal(o.tdeeSource, 'adaptiv');
});

test('Trendgewicht und Steigung', () => {
  const w = { '2026-11-01': 80, '2026-11-05': 81, '2026-11-07': 79, '2026-11-20': 78 };
  assert.equal(trendAt(w, '2026-11-07'), 80);
  assert.equal(trendAt(w, '2026-11-20'), 78);
  assert.equal(currentTrend(w), 78);
  const s = slopePerDay([{ date: '2026-11-01', kg: 80 }, { date: '2026-11-11', kg: 79 }]);
  assert.ok(Math.abs(s! + 0.1) < 1e-9);
});

test('Adaptiver Verbrauch', () => {
  const today = '2026-11-22';
  const entries: Entry[] = [];
  const weights: Record<string, number> = {};
  // 21 Tage je 2500 kcal, Gewicht fällt linear 0.05 kg/Tag -> 0.35 kg/Woche
  for (let i = 1; i <= 21; i++) {
    const d = addDays(today, -i);
    entries.push({ id: d, date: d, meal: 'mittag', name: 'x', createdAt: 0, kcal: 2500, protein: 0, carbs: 0, fat: 0 });
    weights[d] = 80 - (21 - i) * 0.05;
  }
  const a = adaptiveTdee(entries, weights, today);
  assert.ok(a.ok);
  assert.equal(a.avgIntake, 2500);
  assert.equal(a.tdee, Math.round(2500 + 0.05 * 7700)); // 2885
  const few = adaptiveTdee(entries.slice(0, 5), weights, today);
  assert.equal(few.ok, false);
});
