import { useEffect, useState } from 'react';
import { Modal, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { kcalFromMacros, MEALS, parseNum, round1, type Entry, type Meal, type Template } from './logic';
import { c } from './theme';
import { Btn, Chip, NumField, s } from './ui';

export interface EntryDraft {
  name: string;
  meal: Meal;
  kcal: number;
  protein: number;
  carbs: number;
  fat: number;
}

interface Props {
  visible: boolean;
  editing: Entry | null;
  defaultMeal: Meal;
  templates: Template[];
  onClose: () => void;
  onSave: (draft: EntryDraft, template: Omit<Template, 'id'> | null) => void;
  onDelete: (id: string) => void;
  onDeleteTemplate: (id: string) => void;
}

const str = (n: number) => (n ? String(round1(n)) : '');

export function EntryModal({ visible, editing, defaultMeal, templates, onClose, onSave, onDelete, onDeleteTemplate }: Props) {
  const [name, setName] = useState('');
  const [meal, setMeal] = useState<Meal>(defaultMeal);
  const [kcal, setKcal] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fat, setFat] = useState('');
  const [factor, setFactor] = useState('1');
  const [asTemplate, setAsTemplate] = useState(false);
  const [manageTemplates, setManageTemplates] = useState(false);

  useEffect(() => {
    if (!visible) return;
    setName(editing?.name ?? '');
    setMeal(editing?.meal ?? defaultMeal);
    setKcal(editing ? str(editing.kcal) : '');
    setProtein(editing ? str(editing.protein) : '');
    setCarbs(editing ? str(editing.carbs) : '');
    setFat(editing ? str(editing.fat) : '');
    setFactor('1');
    setAsTemplate(false);
    setManageTemplates(false);
  }, [visible, editing, defaultMeal]);

  const p = parseNum(protein) ?? 0;
  const ch = parseNum(carbs) ?? 0;
  const f = parseNum(fat) ?? 0;
  const k = parseNum(kcal);
  const fromMacros = kcalFromMacros(p, ch, f);
  const mult = parseNum(factor) ?? 1;
  const finalKcal = (k ?? fromMacros) * mult;
  // Hinweis, wenn eingetragene kcal stark von den Makros abweichen (Tippfehler, Ballaststoffe, Alkohol)
  const mismatch = k !== null && fromMacros > 0 && Math.abs(k - fromMacros) / Math.max(k, 1) > 0.15;
  const canSave = name.trim() !== '' && finalKcal > 0;

  const applyTemplate = (t: Template) => {
    setName(t.name);
    setKcal(str(t.kcal));
    setProtein(str(t.protein));
    setCarbs(str(t.carbs));
    setFat(str(t.fat));
    setFactor('1');
  };

  const save = () => {
    if (!canSave) return;
    onSave(
      {
        name: name.trim(),
        meal,
        kcal: Math.round(finalKcal),
        protein: round1(p * mult),
        carbs: round1(ch * mult),
        fat: round1(f * mult),
      },
      asTemplate
        ? { name: name.trim(), kcal: Math.round(k ?? fromMacros), protein: round1(p), carbs: round1(ch), fat: round1(f) }
        : null,
    );
  };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose} presentationStyle="pageSheet">
      <SafeAreaView style={{ flex: 1, backgroundColor: c.bg }}>
        <View style={[s.row, { padding: 16 }]}>
          <Text style={s.h1}>{editing ? 'Eintrag bearbeiten' : 'Neuer Eintrag'}</Text>
          <Pressable onPress={onClose} hitSlop={12}>
            <Text style={[s.text, { color: c.muted }]}>Schliessen</Text>
          </Pressable>
        </View>

        <ScrollView contentContainerStyle={{ padding: 16, paddingTop: 0 }} keyboardShouldPersistTaps="handled">
          {!editing && templates.length > 0 && (
            <View style={s.card}>
              <View style={s.row}>
                <Text style={s.h2}>Vorlagen</Text>
                <Pressable onPress={() => setManageTemplates((v) => !v)}>
                  <Text style={s.label}>{manageTemplates ? 'Fertig' : 'Verwalten'}</Text>
                </Pressable>
              </View>
              <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginTop: 10 }}>
                {templates.map((t) => (
                  <Chip
                    key={t.id}
                    title={manageTemplates ? `✕ ${t.name}` : `${t.name} · ${Math.round(t.kcal)}`}
                    onPress={() => (manageTemplates ? onDeleteTemplate(t.id) : applyTemplate(t))}
                  />
                ))}
              </View>
            </View>
          )}

          <View style={s.card}>
            <Text style={s.fieldLabel}>Bezeichnung</Text>
            <View style={s.inputWrap}>
              <TextInput
                style={s.input}
                value={name}
                onChangeText={setName}
                placeholder="z.B. Haferflocken mit Quark"
                placeholderTextColor={c.muted}
              />
            </View>

            <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginTop: 14 }}>
              {MEALS.map((m) => (
                <Chip key={m.key} title={m.label} active={meal === m.key} onPress={() => setMeal(m.key)} />
              ))}
            </View>

            <View style={{ flexDirection: 'row', gap: 10, marginTop: 6 }}>
              <NumField label="Protein" value={protein} onChange={setProtein} suffix="g" />
              <NumField label="Kohlenhydrate" value={carbs} onChange={setCarbs} suffix="g" />
              <NumField label="Fett" value={fat} onChange={setFat} suffix="g" />
            </View>
            <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
              <NumField
                label="Energie (leer = aus Makros)"
                value={kcal}
                onChange={setKcal}
                suffix="kcal"
                placeholder={fromMacros > 0 ? String(fromMacros) : ''}
              />
              <NumField label="Menge" value={factor} onChange={setFactor} suffix="×" />
            </View>

            {mismatch && (
              <Text style={[s.label, { color: c.carbs, marginTop: 8 }]}>
                Makros ergeben {fromMacros} kcal, eingetragen sind {k}. Werte prüfen.
              </Text>
            )}
            <Text style={[s.label, { marginTop: 10 }]}>
              Gespeichert werden: <Text style={{ color: c.text }}>{Math.round(finalKcal)} kcal</Text> · P{' '}
              {round1(p * mult)} g · KH {round1(ch * mult)} g · F {round1(f * mult)} g
            </Text>

            {!editing && (
              <Pressable onPress={() => setAsTemplate((v) => !v)} style={[s.row, { marginTop: 14, justifyContent: 'flex-start' }]}>
                <View
                  style={{
                    width: 20, height: 20, borderRadius: 5, borderWidth: 1.5, borderColor: asTemplate ? c.accent : c.muted,
                    backgroundColor: asTemplate ? c.accent : 'transparent', marginRight: 10,
                  }}
                />
                <Text style={s.text}>Als Vorlage speichern (Werte für Menge 1×)</Text>
              </Pressable>
            )}
          </View>

          <View style={{ flexDirection: 'row', gap: 10 }}>
            {editing && <Btn title="Löschen" kind="danger" onPress={() => onDelete(editing.id)} />}
            <Btn title="Speichern" onPress={save} disabled={!canSave} />
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
}
