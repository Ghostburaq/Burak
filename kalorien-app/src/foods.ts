// Lebensmittel-Datenbank: Schweizer Nährwertdatenbank (offline), Open Food Facts (online),
// eigene Lebensmittel und Rezepte. Alle Werte pro 100 g.

import blvRaw from './data/blv.json';

export interface Nutr {
  kcal: number;
  protein: number;
  carbs: number;
  fat: number;
  sugar?: number | null;
  fiber?: number | null;
  salt?: number | null;
  satFat?: number | null;
}

export type FoodSource = 'blv' | 'off' | 'eigen' | 'rezept';

export interface Food extends Nutr {
  id: string; // 'blv:123', 'off:761...', 'eigen:abc', 'rezept:abc'
  name: string;
  brand?: string;
  category?: string;
  source: FoodSource;
  servingG?: number | null; // Portionsgrösse in g, falls bekannt
  barcode?: string;
}

export interface RecipeItem {
  food: Food; // Schnappschuss, damit das Rezept stabil bleibt
  grams: number;
}

export interface Recipe {
  id: string;
  name: string;
  items: RecipeItem[];
  portions: number;
}

export const BLV_SOURCE =
  'Schweizer Nährwertdatenbank V 7.1, Bundesamt für Lebensmittelsicherheit und Veterinärwesen (BLV), naehrwertdaten.ch';

export const SOURCE_LABEL: Record<FoodSource, string> = {
  blv: 'BLV',
  off: 'Open Food Facts',
  eigen: 'Eigenes',
  rezept: 'Rezept',
};

// ---------- BLV ----------

type BlvRow = [number, string, string, string, number, number, number, number, number, number | null, number | null, number | null, number | null];

let blvCache: Food[] | null = null;
export function blvFoods(): Food[] {
  if (blvCache) return blvCache;
  const rows = (blvRaw as unknown as { foods: BlvRow[] }).foods;
  blvCache = rows.map(([id, name, syn, cat, , kcal, protein, carbs, fat, sugar, fiber, salt, satFat]) => ({
    id: `blv:${id}`,
    name,
    brand: syn || undefined, // Synonyme nur für die Suche
    category: cat,
    source: 'blv',
    kcal, protein, carbs, fat, sugar, fiber, salt, satFat,
  }));
  return blvCache;
}

// ---------- Suche ----------

export function normalize(s: string): string {
  return s
    .toLowerCase()
    .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .replace(/[éèê]/g, 'e').replace(/[àâ]/g, 'a').replace(/[ç]/g, 'c')
    .replace(/[^a-z0-9 ]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Alle Suchwörter müssen vorkommen. Rang: Name beginnt mit Suchbegriff, dann Wortanfang,
 * dann irgendwo; bei Gleichstand kürzere Namen zuerst (generisch vor zusammengesetzt).
 */
export function searchFoods(foods: Food[], query: string, limit = 40): Food[] {
  const q = normalize(query);
  if (!q) return [];
  const tokens = q.split(' ');
  const scored: { f: Food; score: number }[] = [];
  for (const f of foods) {
    const name = normalize(f.name);
    const hay = name + ' ' + normalize(f.brand ?? '');
    if (!tokens.every((t) => hay.includes(t))) continue;
    let score = 0;
    if (name.startsWith(q)) score += 100;
    else if ((' ' + name).includes(' ' + tokens[0])) score += 50;
    if (name === q) score += 100;
    score -= name.length * 0.3;
    if (f.source === 'eigen' || f.source === 'rezept') score += 30; // eigene Sachen zuerst
    scored.push({ f, score });
  }
  return scored.sort((a, b) => b.score - a.score).slice(0, limit).map((x) => x.f);
}

// ---------- Mengen ----------

const r1 = (n: number) => Math.round(n * 10) / 10;
const opt = (v: number | null | undefined, k: number) => (v === null || v === undefined ? null : r1(v * k));

/** Nährwerte für eine Menge in g aus Werten pro 100 g. */
export function scale(n: Nutr, grams: number): Nutr {
  const k = grams / 100;
  return {
    kcal: Math.round(n.kcal * k),
    protein: r1(n.protein * k),
    carbs: r1(n.carbs * k),
    fat: r1(n.fat * k),
    sugar: opt(n.sugar, k),
    fiber: opt(n.fiber, k),
    salt: opt(n.salt, k),
    satFat: opt(n.satFat, k),
  };
}

/** Rezept als Lebensmittel: Werte pro 100 g des Gesamtgerichts, Portion = Gesamtgewicht / Portionen. */
export function recipeToFood(r: Recipe): Food {
  const totalG = r.items.reduce((a, i) => a + i.grams, 0);
  const sumK = (k: keyof Nutr) => {
    let anyNull = false;
    const s = r.items.reduce((a, i) => {
      const v = i.food[k];
      if (v === null || v === undefined) { anyNull = true; return a; }
      return a + (v * i.grams) / 100;
    }, 0);
    return { s, anyNull };
  };
  const per100 = (k: keyof Nutr) => {
    const { s, anyNull } = sumK(k);
    return totalG > 0 ? (anyNull && s === 0 ? null : (s / totalG) * 100) : 0;
  };
  return {
    id: `rezept:${r.id}`,
    name: r.name,
    source: 'rezept',
    kcal: per100('kcal') ?? 0,
    protein: per100('protein') ?? 0,
    carbs: per100('carbs') ?? 0,
    fat: per100('fat') ?? 0,
    sugar: per100('sugar'),
    fiber: per100('fiber'),
    salt: per100('salt'),
    satFat: per100('satFat'),
    servingG: totalG > 0 && r.portions > 0 ? Math.round(totalG / r.portions) : null,
  };
}

// ---------- Open Food Facts ----------

type OffNutriments = Record<string, number | string | undefined>;
interface OffProduct {
  code?: string;
  product_name?: string;
  product_name_de?: string;
  brands?: string | string[];
  serving_quantity?: number | string;
  nutriments?: OffNutriments;
}

const numOr = (v: unknown): number | null => {
  const n = typeof v === 'string' ? parseFloat(v) : typeof v === 'number' ? v : NaN;
  return Number.isFinite(n) ? n : null;
};

/** Wandelt ein Open-Food-Facts-Produkt um. Ohne kcal und Makros pro 100 g: null. */
export function mapOff(p: OffProduct): Food | null {
  const n = p.nutriments ?? {};
  let kcal = numOr(n['energy-kcal_100g']);
  if (kcal === null) {
    const kj = numOr(n['energy-kj_100g']) ?? numOr(n['energy_100g']);
    if (kj !== null) kcal = kj / 4.184;
  }
  const protein = numOr(n['proteins_100g']);
  const carbs = numOr(n['carbohydrates_100g']);
  const fat = numOr(n['fat_100g']);
  const name = (p.product_name_de || p.product_name || '').trim();
  if (kcal === null || protein === null || carbs === null || fat === null || !name || !p.code) return null;
  const brand = Array.isArray(p.brands) ? p.brands.join(', ') : p.brands;
  const serving = numOr(p.serving_quantity);
  return {
    id: `off:${p.code}`,
    name,
    brand: brand || undefined,
    source: 'off',
    barcode: p.code,
    kcal: Math.round(kcal),
    protein, carbs, fat,
    sugar: numOr(n['sugars_100g']),
    fiber: numOr(n['fiber_100g']),
    salt: numOr(n['salt_100g']),
    satFat: numOr(n['saturated-fat_100g']),
    servingG: serving && serving > 0 ? serving : null,
  };
}

const OFF_FIELDS = 'code,product_name,product_name_de,brands,serving_quantity,nutriments';

async function fetchJson(url: string, ms = 12000): Promise<unknown> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try {
    const res = await fetch(url, { signal: ctrl.signal, headers: { Accept: 'application/json' } });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

export type LookupResult = { ok: true; food: Food } | { ok: false; reason: 'not_found' | 'no_nutrition' | 'offline' };

export async function lookupBarcode(code: string): Promise<LookupResult> {
  const clean = code.replace(/\D/g, '');
  try {
    const d = (await fetchJson(`https://world.openfoodfacts.org/api/v2/product/${clean}.json?fields=${OFF_FIELDS}`)) as
      | { status?: number; product?: OffProduct }
      | null;
    if (!d || !d.product) return { ok: false, reason: 'not_found' };
    const f = mapOff({ ...d.product, code: d.product.code ?? clean });
    return f ? { ok: true, food: f } : { ok: false, reason: 'no_nutrition' };
  } catch {
    return { ok: false, reason: 'offline' };
  }
}

/** Textsuche bei Open Food Facts. Wirft bei Netzwerkfehler (z.B. im Browser wegen CORS). */
export async function searchOff(query: string): Promise<Food[]> {
  const url = `https://search.openfoodfacts.org/search?q=${encodeURIComponent(query)}&page_size=25&langs=de,fr,en&fields=${OFF_FIELDS}`;
  const d = (await fetchJson(url)) as { hits?: OffProduct[] } | null;
  return (d?.hits ?? []).map(mapOff).filter((f): f is Food => f !== null);
}
