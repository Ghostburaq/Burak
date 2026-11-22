import { StatusBar } from 'expo-status-bar';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { EntryModal, type EntryDraft } from './src/EntryModal';
import { toDateKey, type Entry, type Goals, type Meal, type Template } from './src/logic';
import { DayScreen, GoalsScreen, WeekScreen } from './src/screens';
import { DEFAULT_GOALS, newId, store } from './src/storage';
import { c } from './src/theme';

type Tab = 'tag' | 'woche' | 'ziele';
const TABS: { key: Tab; label: string }[] = [
  { key: 'tag', label: 'Tag' },
  { key: 'woche', label: 'Woche' },
  { key: 'ziele', label: 'Ziele' },
];

/** Vorschlag der Mahlzeit nach Uhrzeit, wenn über den allgemeinen Plus-Button erfasst wird. */
function mealByTime(): Meal {
  const h = new Date().getHours();
  if (h < 10) return 'fruehstueck';
  if (h < 15) return 'mittag';
  if (h < 21) return 'abend';
  return 'snack';
}

export default function App() {
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<Tab>('tag');
  const [date, setDate] = useState(toDateKey(new Date()));
  const [entries, setEntries] = useState<Entry[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [goals, setGoals] = useState<Goals>(DEFAULT_GOALS);
  const [modal, setModal] = useState<{ open: boolean; meal: Meal; editing: Entry | null }>({
    open: false, meal: 'mittag', editing: null,
  });

  useEffect(() => {
    store.loadAll().then((d) => {
      setEntries(d.entries);
      setTemplates(d.templates);
      setGoals(d.goals);
      setReady(true);
    });
  }, []);

  const updateEntries = useCallback((fn: (prev: Entry[]) => Entry[]) => {
    setEntries((prev) => {
      const next = fn(prev);
      store.saveEntries(next);
      return next;
    });
  }, []);

  const updateTemplates = useCallback((fn: (prev: Template[]) => Template[]) => {
    setTemplates((prev) => {
      const next = fn(prev);
      store.saveTemplates(next);
      return next;
    });
  }, []);

  const closeModal = () => setModal((m) => ({ ...m, open: false, editing: null }));

  const handleSave = (draft: EntryDraft, template: Omit<Template, 'id'> | null) => {
    const editing = modal.editing;
    if (editing) {
      updateEntries((prev) => prev.map((e) => (e.id === editing.id ? { ...e, ...draft } : e)));
    } else {
      updateEntries((prev) => [...prev, { ...draft, id: newId(), date, createdAt: Date.now() }]);
    }
    if (template) {
      // Gleichnamige Vorlage wird ersetzt statt doppelt angelegt
      updateTemplates((prev) => [
        { ...template, id: newId() },
        ...prev.filter((t) => t.name.toLowerCase() !== template.name.toLowerCase()),
      ]);
    }
    closeModal();
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
              entries={entries}
              goals={goals}
              onAdd={(meal) => setModal({ open: true, meal, editing: null })}
              onEdit={(e) => setModal({ open: true, meal: e.meal, editing: e })}
            />
          )}
          {tab === 'woche' && (
            <WeekScreen entries={entries} goals={goals} onOpenDay={(d) => { setDate(d); setTab('tag'); }} />
          )}
          {tab === 'ziele' && (
            <GoalsScreen goals={goals} onSave={(g) => { setGoals(g); store.saveGoals(g); }} />
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
          templates={templates}
          onClose={closeModal}
          onSave={handleSave}
          onDelete={(id) => { updateEntries((prev) => prev.filter((e) => e.id !== id)); closeModal(); }}
          onDeleteTemplate={(id) => updateTemplates((prev) => prev.filter((t) => t.id !== id))}
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}
