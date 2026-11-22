import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  addDays,
  formatDate,
  isoWeek,
  kcalFromMacros,
  parseNum,
  weekDays,
  weekStats,
  type Entry,
} from './logic.ts';

test('kcal aus Makros nach Atwater', () => {
  assert.equal(kcalFromMacros(30, 50, 10), 30 * 4 + 50 * 4 + 10 * 9);
});

test('ISO-Kalenderwochen inkl. Jahreswechsel', () => {
  assert.equal(isoWeek('2026-11-22'), 47); // Sonntag
  assert.equal(isoWeek('2026-11-23'), 48); // Montag
  assert.equal(isoWeek('2026-01-01'), 1); // Donnerstag
  assert.equal(isoWeek('2027-01-01'), 53); // Freitag, gehört zu KW 53/2026
  assert.equal(isoWeek('2024-12-30'), 1); // Montag, KW 1/2025
});

test('Datumshelfer', () => {
  assert.equal(addDays('2026-02-28', 1), '2026-03-01');
  assert.equal(formatDate('2026-07-04'), '04.07.2026');
  const w = weekDays('2026-11-22');
  assert.equal(w[0], '2026-11-16');
  assert.equal(w[6], '2026-11-22');
});

test('Wochenschnitt zählt nur Tage mit Einträgen', () => {
  const e = (date: string, kcal: number, protein: number): Entry => ({
    id: date + kcal, date, meal: 'mittag', name: 'x', createdAt: 0,
    kcal, protein, carbs: 0, fat: 0,
  });
  const s = weekStats([e('2026-11-16', 2000, 150), e('2026-11-17', 2400, 170), e('2026-11-17', 0, 10)], '2026-11-20');
  assert.equal(s.loggedDays, 2);
  assert.equal(s.avg.kcal, 2200);
  assert.equal(s.avg.protein, 165);
});

test('Zahleneingabe mit Komma', () => {
  assert.equal(parseNum('12,5'), 12.5);
  assert.equal(parseNum(''), null);
  assert.equal(parseNum('abc'), null);
  assert.equal(parseNum('-3'), null);
});
