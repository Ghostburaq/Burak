import AsyncStorage from '@react-native-async-storage/async-storage';
import type { Entry, Goals, Template } from './logic';
import type { Food, Recipe } from './foods';
import { DEFAULT_PROFILE, type Profile, type Weights } from './nutrition';

const KEYS = {
  entries: 'kal.entries.v1',
  templates: 'kal.templates.v1',
  goalsLegacy: 'kal.goals.v1',
  profile: 'kal.profile.v1',
  weights: 'kal.weights.v1',
  water: 'kal.water.v1',
  training: 'kal.training.v1',
  myFoods: 'kal.myfoods.v1',
  favorites: 'kal.favorites.v1',
  recipes: 'kal.recipes.v1',
};

export interface AppData {
  entries: Entry[];
  templates: Template[];
  profile: Profile;
  weights: Weights;
  water: Record<string, number>; // Datum -> ml
  training: string[]; // Daten mit Training
  myFoods: Food[]; // eigene Lebensmittel und genutzte Online-Produkte (Offline-Cache)
  favorites: Food[];
  recipes: Recipe[];
}

async function load<T>(key: string, fallback: T): Promise<T> {
  try {
    const raw = await AsyncStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

async function save(key: string, value: unknown): Promise<void> {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Speicher voll oder gesperrt (z.B. privater Browsermodus): Daten bleiben bis zum Schliessen im Speicher
  }
}

export async function loadAll(): Promise<AppData> {
  let profile = await load<Profile | null>(KEYS.profile, null);
  if (!profile) {
    // Migration: alte feste Ziele werden zum manuellen Modus
    const legacy = await load<Goals | null>(KEYS.goalsLegacy, null);
    profile = legacy ? { ...DEFAULT_PROFILE, configured: true, mode: 'manual', manual: legacy } : DEFAULT_PROFILE;
  }
  return {
    entries: await load<Entry[]>(KEYS.entries, []),
    templates: await load<Template[]>(KEYS.templates, []),
    profile: { ...DEFAULT_PROFILE, ...profile },
    weights: await load<Weights>(KEYS.weights, {}),
    water: await load<Record<string, number>>(KEYS.water, {}),
    training: await load<string[]>(KEYS.training, []),
    myFoods: await load<Food[]>(KEYS.myFoods, []),
    favorites: await load<Food[]>(KEYS.favorites, []),
    recipes: await load<Recipe[]>(KEYS.recipes, []),
  };
}

export const persist = {
  entries: (v: Entry[]) => save(KEYS.entries, v),
  templates: (v: Template[]) => save(KEYS.templates, v),
  profile: (v: Profile) => save(KEYS.profile, v),
  weights: (v: Weights) => save(KEYS.weights, v),
  water: (v: Record<string, number>) => save(KEYS.water, v),
  training: (v: string[]) => save(KEYS.training, v),
  myFoods: (v: Food[]) => save(KEYS.myFoods, v),
  favorites: (v: Food[]) => save(KEYS.favorites, v),
  recipes: (v: Recipe[]) => save(KEYS.recipes, v),
};

export async function saveAll(d: AppData): Promise<void> {
  await Promise.all([
    persist.entries(d.entries), persist.templates(d.templates), persist.profile(d.profile),
    persist.weights(d.weights), persist.water(d.water), persist.training(d.training),
    persist.myFoods(d.myFoods), persist.favorites(d.favorites), persist.recipes(d.recipes),
  ]);
}

export function exportJson(d: AppData): string {
  return JSON.stringify({ app: 'kalorien', version: 1, exportedAt: new Date().toISOString(), ...d });
}

/** Prüft ein Backup grob und gibt die Daten zurück, sonst eine Fehlermeldung. */
export function parseBackup(text: string): AppData | string {
  try {
    const o = JSON.parse(text);
    if (o?.app !== 'kalorien' || !Array.isArray(o.entries)) return 'Kein gültiges Kalorien-Backup.';
    return {
      entries: o.entries,
      templates: Array.isArray(o.templates) ? o.templates : [],
      profile: { ...DEFAULT_PROFILE, ...(o.profile ?? {}) },
      weights: o.weights ?? {},
      water: o.water ?? {},
      training: Array.isArray(o.training) ? o.training : [],
      myFoods: Array.isArray(o.myFoods) ? o.myFoods : [],
      favorites: Array.isArray(o.favorites) ? o.favorites : [],
      recipes: Array.isArray(o.recipes) ? o.recipes : [],
    };
  } catch {
    return 'Text ist kein gültiges JSON.';
  }
}

export function newId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}
