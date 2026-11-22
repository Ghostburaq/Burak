import AsyncStorage from '@react-native-async-storage/async-storage';
import type { Entry, Goals, Template } from './logic';

const KEYS = {
  entries: 'kal.entries.v1',
  templates: 'kal.templates.v1',
  goals: 'kal.goals.v1',
};

// Startwerte, sofort in den Zielen anpassbar. Keine Empfehlung.
export const DEFAULT_GOALS: Goals = { kcal: 2000, protein: 150, carbs: 200, fat: 70 };

async function load<T>(key: string, fallback: T): Promise<T> {
  try {
    const raw = await AsyncStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

async function save(key: string, value: unknown): Promise<void> {
  await AsyncStorage.setItem(key, JSON.stringify(value));
}

export const store = {
  loadAll: async () => ({
    entries: await load<Entry[]>(KEYS.entries, []),
    templates: await load<Template[]>(KEYS.templates, []),
    goals: await load<Goals>(KEYS.goals, DEFAULT_GOALS),
  }),
  saveEntries: (v: Entry[]) => save(KEYS.entries, v),
  saveTemplates: (v: Template[]) => save(KEYS.templates, v),
  saveGoals: (v: Goals) => save(KEYS.goals, v),
};

export function newId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}
