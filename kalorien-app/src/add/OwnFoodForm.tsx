import { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import type { Food } from '../foods';
import { kcalFromMacros, parseNum } from '../logic';
import { newId } from '../storage';
import { c } from '../theme';
import { Btn, NumField, s, TextField } from '../ui';

const str = (n: number | null | undefined) => (n === null || n === undefined ? '' : String(n).replace('.', ','));

/** Eigenes Lebensmittel mit Werten pro 100 g, z.B. von der Verpackung. */
export function OwnFoodForm({
  initial, onSave, onDelete, onBack,
}: {
  initial: Partial<Food>;
  onSave: (f: Food) => void;
  onDelete?: (id: string) => void;
  onBack: () => void;
}) {
  const [v, setV] = useState({
    name: initial.name ?? '', brand: initial.brand ?? '', barcode: initial.barcode ?? '',
    kcal: str(initial.kcal), protein: str(initial.protein), carbs: str(initial.carbs), fat: str(initial.fat),
    sugar: str(initial.sugar), fiber: str(initial.fiber), salt: str(initial.salt), satFat: str(initial.satFat),
    servingG: str(initial.servingG),
  });
  const set = (k: keyof typeof v) => (x: string) => setV((o) => ({ ...o, [k]: x }));
  const n = (k: keyof typeof v) => parseNum(v[k]);
  const p = n('protein'), ch = n('carbs'), f = n('fat');
  const fromMacros = kcalFromMacros(p ?? 0, ch ?? 0, f ?? 0);
  const kcal = n('kcal') ?? (fromMacros || null);
  const sumMacros = (p ?? 0) + (ch ?? 0) + (f ?? 0);
  const errors: string[] = [];
  if (!v.name.trim()) errors.push('Name fehlt');
  if (p === null || ch === null || f === null) errors.push('Protein, KH und Fett pro 100 g angeben');
  if (sumMacros > 100) errors.push('Mehr als 100 g Makros pro 100 g, Werte prüfen');
  if (!kcal) errors.push('Energie fehlt');

  const save = () => {
    if (errors.length) return;
    onSave({
      id: initial.id ?? `eigen:${newId()}`,
      source: 'eigen',
      name: v.name.trim(),
      brand: v.brand.trim() || undefined,
      barcode: v.barcode.replace(/\D/g, '') || undefined,
      kcal: Math.round(kcal!), protein: p!, carbs: ch!, fat: f!,
      sugar: n('sugar'), fiber: n('fiber'), salt: n('salt'), satFat: n('satFat'),
      servingG: n('servingG'),
    });
  };

  return (
    <View>
      <Pressable onPress={onBack} style={{ marginBottom: 10 }} hitSlop={10}>
        <Text style={{ color: c.muted }}>‹ Zurück</Text>
      </Pressable>
      <Text style={[s.h1, { marginBottom: 12 }]}>{initial.id ? 'Lebensmittel bearbeiten' : 'Eigenes Lebensmittel'}</Text>
      <View style={s.card}>
        <TextField label="Name" value={v.name} onChange={set('name')} placeholder="z.B. Proteinriegel Schoko" />
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <View style={{ flex: 1 }}><TextField label="Marke (optional)" value={v.brand} onChange={set('brand')} /></View>
          <NumField label="Barcode (optional)" value={v.barcode} onChange={set('barcode')} />
        </View>
      </View>
      <Text style={s.section}>Nährwerte pro 100 g (Verpackung)</Text>
      <View style={s.card}>
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <NumField label="Energie" value={v.kcal} onChange={set('kcal')} suffix="kcal" placeholder={fromMacros ? String(fromMacros) : ''} />
          <NumField label="Portion" value={v.servingG} onChange={set('servingG')} suffix="g" placeholder="optional" />
        </View>
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <NumField label="Protein" value={v.protein} onChange={set('protein')} suffix="g" />
          <NumField label="Kohlenhydrate" value={v.carbs} onChange={set('carbs')} suffix="g" />
          <NumField label="Fett" value={v.fat} onChange={set('fat')} suffix="g" />
        </View>
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <NumField label="davon Zucker" value={v.sugar} onChange={set('sugar')} suffix="g" />
          <NumField label="Ballaststoffe" value={v.fiber} onChange={set('fiber')} suffix="g" />
          <NumField label="Salz" value={v.salt} onChange={set('salt')} suffix="g" />
        </View>
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <NumField label="ges. Fettsäuren" value={v.satFat} onChange={set('satFat')} suffix="g" />
          <View style={{ flex: 2 }} />
        </View>
        {errors.length > 0 && <Text style={[s.label, { color: c.over, marginTop: 10 }]}>{errors.join(' · ')}</Text>}
      </View>
      <View style={{ flexDirection: 'row', gap: 10 }}>
        {onDelete && initial.id && <Btn title="Löschen" kind="danger" onPress={() => onDelete(initial.id!)} />}
        <Btn title="Speichern" disabled={errors.length > 0} onPress={save} />
      </View>
    </View>
  );
}
