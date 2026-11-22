import { test } from 'node:test';
import assert from 'node:assert/strict';
import { blvFoods, mapOff, normalize, recipeToFood, scale, searchFoods, type Food } from './foods';

test('BLV-Datenbank geladen und plausibel', () => {
  const f = blvFoods();
  assert.ok(f.length > 1000);
  for (const x of f) {
    assert.ok(x.kcal >= 0 && x.kcal <= 900, `${x.name} kcal ${x.kcal}`);
    assert.ok(x.protein + x.carbs + x.fat <= 101, `${x.name} Makros > 100 g`);
  }
});

test('Suche findet generische Lebensmittel, Umlaute egal', () => {
  const f = blvFoods();
  const r = searchFoods(f, 'haferflocken');
  assert.ok(r.length > 0);
  assert.ok(normalize(r[0].name).startsWith('haferflocken'), r[0].name);
  const k = searchFoods(f, 'kase');
  const k2 = searchFoods(f, 'käse');
  assert.equal(k.length, 0); // "kase" ist nicht "kaese"
  assert.ok(k2.length > 0);
  const multi = searchFoods(f, 'reis gekocht');
  assert.ok(multi.every((x) => normalize(x.name + ' ' + (x.brand ?? '')).includes('reis')));
});

test('Mengen skalieren', () => {
  const n = scale({ kcal: 370, protein: 13, carbs: 59, fat: 7, fiber: 10, sugar: null }, 60);
  assert.deepEqual(n, { kcal: 222, protein: 7.8, carbs: 35.4, fat: 4.2, sugar: null, fiber: 6, salt: null, satFat: null });
});

test('Rezept: Werte pro 100 g und Portionsgrösse', () => {
  const a: Food = { id: 'a', name: 'A', source: 'eigen', kcal: 100, protein: 20, carbs: 0, fat: 2 };
  const b: Food = { id: 'b', name: 'B', source: 'eigen', kcal: 300, protein: 0, carbs: 70, fat: 1 };
  const f = recipeToFood({ id: 'r', name: 'R', portions: 2, items: [{ food: a, grams: 200 }, { food: b, grams: 200 }] });
  assert.equal(f.kcal, 200);
  assert.equal(f.protein, 10);
  assert.equal(f.carbs, 35);
  assert.equal(f.servingG, 200);
  const portion = scale(f, f.servingG!);
  assert.equal(portion.kcal, 400);
});

test('Open Food Facts Mapping', () => {
  const f = mapOff({
    code: '123', product_name: 'Skyr', brands: 'Emmi', serving_quantity: '150',
    nutriments: { 'energy-kcal_100g': 63, proteins_100g: 11, carbohydrates_100g: 4, fat_100g: 0.2, salt_100g: 0.1 },
  });
  assert.equal(f?.id, 'off:123');
  assert.equal(f?.servingG, 150);
  assert.equal(f?.fiber, null);
  // kJ-Fallback
  const g = mapOff({ code: '1', product_name: 'X', nutriments: { 'energy-kj_100g': 418.4, proteins_100g: 1, carbohydrates_100g: 1, fat_100g: 1 } });
  assert.equal(g?.kcal, 100);
  // ohne Makros: unbrauchbar
  assert.equal(mapOff({ code: '2', product_name: 'Y', nutriments: { 'energy-kcal_100g': 50 } }), null);
});
