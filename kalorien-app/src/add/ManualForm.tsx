import { useEffect, useState } from 'react';
import { Pressable, Text, TextInput, View } from 'react-native';
import { kcalFromMacros, parseNum, round1, type Entry, type EntryDraft, type Meal, type Template } from '../logic';
import { c } from '../theme';
import { Btn, Chip, NumField, s } from '../ui';

const str = (n: number | null | undefined) => (n ? String(round1(n)).replace('.', ',') : '');

/** Freie Eingabe ohne Datenbank: Name, Makros, optional kcal, Mengenfaktor, Vorlagen. */
export function ManualForm({
  meal, editing, templates, recent, onSave, onDelete, onDeleteTemplate,
}: {
  meal: Meal;
  editing: Entry | null;
  templates: Template[];
  recent: Template[];
  onSave: (draft: EntryDraft, template: Omit<Template, 'id'> | null) => void;
  onDelete: (id: string) => void;
  onDeleteTemplate: (id: string) => void;
}) {
  const [name, setName] = useState('');
  const [kcal, setKcal] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fat, setFat] = useState('');
  const [factor, setFactor] = useState('1');
  const [asTemplate, setAsTemplate] = useState(false);
  const [manage, setManage] = useState(false);

  useEffect(() => {
    setName(editing?.name ?? '');
    setKcal(str(editing?.kcal));
    setProtein(str(editing?.protein));
    setCarbs(str(editing?.carbs));
    setFat(str(editing?.fat));
    setFactor('1');
    setAsTemplate(false);
  }, [editing]);

  const p = parseNum(protein) ?? 0;
  const ch = parseNum(carbs) ?? 0;
  const f = parseNum(fat) ?? 0;
  const k = parseNum(kcal);
  const fromMacros = kcalFromMacros(p, ch, f);
  const mult = parseNum(factor) ?? 1;
  const finalKcal = (k ?? fromMacros) * mult;
  const mismatch = k !== null && fromMacros > 0 && Math.abs(k - fromMacros) / Math.max(k, 1) > 0.15;
  const canSave = name.trim() !== '' && finalKcal > 0;

  const apply = (t: Template) => {
    setName(t.name); setKcal(str(t.kcal)); setProtein(str(t.protein)); setCarbs(str(t.carbs)); setFat(str(t.fat)); setFactor('1');
  };

  const save = () => {
    if (!canSave) return;
    onSave(
      {
        name: name.trim(), meal,
        kcal: Math.round(finalKcal),
        protein: round1(p * mult), carbs: round1(ch * mult), fat: round1(f * mult),
      },
      asTemplate ? { name: name.trim(), kcal: Math.round(k ?? fromMacros), protein: round1(p), carbs: round1(ch), fat: round1(f) } : null,
    );
  };

  return (
    <View>
      {!editing && templates.length > 0 && (
        <View style={s.card}>
          <View style={s.row}>
            <Text style={s.h2}>Vorlagen</Text>
            <Pressable onPress={() => setManage((v) => !v)}>
              <Text style={s.label}>{manage ? 'Fertig' : 'Verwalten'}</Text>
            </Pressable>
          </View>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginTop: 10 }}>
            {templates.map((t) => (
              <Chip key={t.id} title={manage ? `✕ ${t.name}` : `${t.name} · ${Math.round(t.kcal)}`} onPress={() => (manage ? onDeleteTemplate(t.id) : apply(t))} />
            ))}
          </View>
        </View>
      )}
      {!editing && recent.length > 0 && (
        <View style={s.card}>
          <Text style={s.h2}>Zuletzt manuell erfasst</Text>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginTop: 10 }}>
            {recent.map((t) => (
              <Chip key={t.id} title={`${t.name} · ${Math.round(t.kcal)}`} onPress={() => apply(t)} />
            ))}
          </View>
        </View>
      )}

      <View style={s.card}>
        <Text style={s.fieldLabel}>Bezeichnung</Text>
        <View style={s.inputWrap}>
          <TextInput style={s.input} value={name} onChangeText={setName} placeholder="z.B. Kantinenmenü" placeholderTextColor={c.muted} />
        </View>
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <NumField label="Protein" value={protein} onChange={setProtein} suffix="g" />
          <NumField label="Kohlenhydrate" value={carbs} onChange={setCarbs} suffix="g" />
          <NumField label="Fett" value={fat} onChange={setFat} suffix="g" />
        </View>
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <NumField label="Energie (leer = aus Makros)" value={kcal} onChange={setKcal} suffix="kcal" placeholder={fromMacros > 0 ? String(fromMacros) : ''} />
          <NumField label="Menge" value={factor} onChange={setFactor} suffix="×" />
        </View>
        {mismatch && (
          <Text style={[s.label, { color: c.warn, marginTop: 8 }]}>Makros ergeben {fromMacros} kcal, eingetragen sind {k}. Werte prüfen.</Text>
        )}
        <Text style={[s.label, { marginTop: 10 }]}>
          Gespeichert werden: <Text style={{ color: c.text }}>{Math.round(finalKcal)} kcal</Text> · P {round1(p * mult)} g · KH {round1(ch * mult)} g · F {round1(f * mult)} g
        </Text>
        {!editing && (
          <Pressable onPress={() => setAsTemplate((v) => !v)} style={[s.row, { marginTop: 14, justifyContent: 'flex-start' }]}>
            <View style={{ width: 20, height: 20, borderRadius: 5, borderWidth: 1.5, borderColor: asTemplate ? c.accent : c.muted, backgroundColor: asTemplate ? c.accent : 'transparent', marginRight: 10 }} />
            <Text style={s.text}>Als Vorlage speichern (Werte für Menge 1×)</Text>
          </Pressable>
        )}
      </View>

      <View style={{ flexDirection: 'row', gap: 10 }}>
        {editing && <Btn title="Löschen" kind="danger" onPress={() => onDelete(editing.id)} />}
        <Btn title={editing ? 'Speichern' : 'Hinzufügen'} onPress={save} disabled={!canSave} />
      </View>
    </View>
  );
}
