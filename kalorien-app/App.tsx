import { StatusBar } from 'expo-status-bar';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { EntryModal, type EntryDraft } from './src/EntryModal';
import { toDateKey, type Entry, type Meal, type Template } from './src/logic';
import { calculate, currentTrend, DEFAULT_PROFILE } from './src/nutrition';
import { ProfileScreen } from './src/ProfileScreen';
import { DayScreen, WeekScreen } from './src/screens';
import { exportJson, loadAll, newId, parseBackup, persist, saveAll, type AppData } from './src/storage';
import { c } from './src/theme';
import { WeightScreen } from './src/WeightScreen';

type Tab = 'tag' | 'woche' | 'gewicht' | 'profil';
const TABS: { key: Tab; label: string }[] = [
  { key: 'tag', label: 'Tag' },
  { key: 'woche', label: 'Woche' },
  { key: 'gewicht', label: 'Gewicht' },
  { key: 'profil', label: 'Profil' },
];

/** Vorschlag der Mahlzeit nach Uhrzeit für den allgemeinen Plus-Button. */
function mealByTime(): Meal {
  const h = new Date().getHours();
  if (h < 10) return 'fruehstueck';
  if (h < 15) return 'mittag';
  if (h < 21) return 'abend';
  return 'snack';
}

const EMPTY: AppData = { entries: [], templates: [], profile: DEFAULT_PROFILE, weights: {}, water: {}, training: [] };

export default function App() {
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<Tab>('tag');
  const [date, setDate] = useState(toDateKey(new Date()));
  const [data, setData] = useState<AppData>(EMPTY);
  const [modal, setModal] = useState<{ open: boolean; meal: Meal; editing: Entry | null }>({
    open: false, meal: 'mittag', editing: null,
  });

  useEffect(() => {
    loadAll().then((d) => { setData(d); setReady(true); });
  }, []);

  /** Ändert einen Teil der Daten und speichert genau diesen Teil. */
  const update = useCallback(<K extends keyof AppData>(key: K, fn: (prev: AppData[K]) => AppData[K]) => {
    setData((prev) => {
      const next = { ...prev, [key]: fn(prev[key]) };
      (persist[key] as (v: AppData[K]) => void)(next[key]);
      return next;
    });
  }, []);

  const trend = useMemo(() => currentTrend(data.weights), [data.weights]);
  const calc = useMemo(() => calculate(data.profile, trend), [data.profile, trend]);
  const goalsFor = useCallback((d: string) => (data.training.includes(d) ? calc.training : calc.base), [data.training, calc]);

  // Zuletzt gegessen: eindeutige Namen, neueste zuerst
  const recent = useMemo<Template[]>(() => {
    const seen = new Set<string>();
    const out: Template[] = [];
    for (const e of [...data.entries].sort((a, b) => b.createdAt - a.createdAt)) {
      const k = e.name.toLowerCase();
      if (seen.has(k)) continue;
      seen.add(k);
      out.push({ id: 'r' + e.id, name: e.name, kcal: e.kcal, protein: e.protein, carbs: e.carbs, fat: e.fat });
      if (out.length >= 12) break;
    }
    return out;
  }, [data.entries]);

  const closeModal = () => setModal((m) => ({ ...m, open: false, editing: null }));

  const handleSave = (draft: EntryDraft, template: Omit<Template, 'id'> | null) => {
    const editing = modal.editing;
    if (editing) {
      update('entries', (prev) => prev.map((e) => (e.id === editing.id ? { ...e, ...draft } : e)));
    } else {
      update('entries', (prev) => [...prev, { ...draft, id: newId(), date, createdAt: Date.now() }]);
    }
    if (template) {
      update('templates', (prev) => [
        { ...template, id: newId() },
        ...prev.filter((t) => t.name.toLowerCase() !== template.name.toLowerCase()),
      ]);
    }
    closeModal();
  };

  const copyMeal = (meal: Meal, from: string) => {
    const now = Date.now();
    update('entries', (prev) => [
      ...prev,
      ...prev.filter((e) => e.date === from && e.meal === meal).map((e, i) => ({ ...e, id: newId(), date, createdAt: now + i })),
    ]);
  };

  if (!ready) {
    return (
      <View style={{ flex: 1, backgroundColor: c.bg, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator color={c.accent} />
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <SafeAreaView style={{ flex: 1, backgroundColor: c.bg }} edges={['top', 'left', 'right']}>
        <StatusBar style="light" />
        <View style={{ flex: 1 }}>
          {tab === 'tag' && (
            <DayScreen
              date={date}
              setDate={setDate}
              entries={data.entries}
              goals={goalsFor(date)}
              isTraining={data.training.includes(date)}
              onToggleTraining={() =>
                update('training', (prev) => (prev.includes(date) ? prev.filter((d) => d !== date) : [...prev, date]))
              }
              water={data.water[date] ?? 0}
              waterGoal={calc.waterMl}
              onWater={(delta) => update('water', (prev) => ({ ...prev, [date]: Math.max(0, (prev[date] ?? 0) + delta) }))}
              configured={data.profile.configured}
              onSetup={() => setTab('profil')}
              onAdd={(meal) => setModal({ open: true, meal, editing: null })}
              onEdit={(e) => setModal({ open: true, meal: e.meal, editing: e })}
              onCopyMeal={copyMeal}
            />
          )}
          {tab === 'woche' && (
            <WeekScreen entries={data.entries} goalsFor={goalsFor} onOpenDay={(d) => { setDate(d); setTab('tag'); }} />
          )}
          {tab === 'gewicht' && (
            <WeightScreen
              weights={data.weights}
              entries={data.entries}
              profile={data.profile}
              formulaTdee={calc.tdeeFormula}
              onSetWeight={(d, kg) => update('weights', (prev) => ({ ...prev, [d]: kg }))}
              onDeleteWeight={(d) => update('weights', (prev) => { const n = { ...prev }; delete n[d]; return n; })}
              onApplyTdee={(t) => update('profile', (p) => ({ ...p, tdeeOverride: t }))}
            />
          )}
          {tab === 'profil' && (
            <ProfileScreen
              profile={data.profile}
              trendWeight={trend}
              onSave={(p) => update('profile', () => p)}
              exportText={() => exportJson(data)}
              onImport={(text) => {
                const r = parseBackup(text);
                if (typeof r === 'string') return r;
                setData(r);
                saveAll(r);
                return null;
              }}
            />
          )}
        </View>

        {tab === 'tag' && (
          <Pressable
            onPress={() => setModal({ open: true, meal: mealByTime(), editing: null })}
            style={{
              position: 'absolute', right: 20, bottom: 90, width: 58, height: 58, borderRadius: 29,
              backgroundColor: c.accent, alignItems: 'center', justifyContent: 'center',
              shadowColor: '#000', shadowOpacity: 0.4, shadowRadius: 8, elevation: 6,
            }}
          >
            <Text style={{ fontSize: 30, color: '#0b0d10', marginTop: -2 }}>+</Text>
          </Pressable>
        )}

        <SafeAreaView edges={['bottom']} style={{ backgroundColor: c.card, borderTopWidth: 1, borderTopColor: c.border }}>
          <View style={{ flexDirection: 'row' }}>
            {TABS.map((t) => (
              <Pressable key={t.key} onPress={() => setTab(t.key)} style={{ flex: 1, paddingVertical: 16, alignItems: 'center' }}>
                <Text style={{ color: tab === t.key ? c.accent : c.muted, fontWeight: tab === t.key ? '700' : '500', fontSize: 15 }}>
                  {t.label}
                </Text>
              </Pressable>
            ))}
          </View>
        </SafeAreaView>

        <EntryModal
          visible={modal.open}
          editing={modal.editing}
          defaultMeal={modal.meal}
          templates={data.templates}
          recent={recent}
          onClose={closeModal}
          onSave={handleSave}
          onDelete={(id) => { update('entries', (prev) => prev.filter((e) => e.id !== id)); closeModal(); }}
          onDeleteTemplate={(id) => update('templates', (prev) => prev.filter((t) => t.id !== id))}
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}
