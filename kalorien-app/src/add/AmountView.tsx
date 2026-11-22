import { useEffect, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { scale, SOURCE_LABEL, type Food } from '../foods';
import { parseNum } from '../logic';
import { c } from '../theme';
import { Btn, Chip, KV, NumField, s } from '../ui';

const f1 = (n: number | null | undefined) => (n === null || n === undefined ? '–' : String(Math.round(n * 10) / 10).replace('.', ','));

/** Menge in g wählen, Nährwerte live. Für Tagebuch-Eintrag oder Rezeptzutat. */
export function AmountView({
  food, initialGrams, isFavorite, actionLabel, onToggleFavorite, onConfirm, onDelete, onBack, onEditOwn,
}: {
  food: Food;
  initialGrams?: number;
  isFavorite: boolean;
  actionLabel: string;
  onToggleFavorite: () => void;
  onConfirm: (grams: number) => void;
  onDelete?: () => void;
  onBack?: () => void;
  onEditOwn?: () => void;
}) {
  const start = initialGrams ?? food.servingG ?? 100;
  const [g, setG] = useState(String(start));
  useEffect(() => setG(String(initialGrams ?? food.servingG ?? 100)), [food.id, initialGrams, food.servingG]);
  const grams = parseNum(g) ?? 0;
  const n = scale(food, grams);
  const presets = [50, 100, 150, 200, 250];

  return (
    <View>
      {onBack && (
        <Pressable onPress={onBack} style={{ marginBottom: 10 }} hitSlop={10}>
          <Text style={{ color: c.muted }}>‹ Zurück</Text>
        </Pressable>
      )}
      <View style={s.card}>
        <View style={[s.row, { alignItems: 'flex-start' }]}>
          <View style={{ flex: 1, marginRight: 10 }}>
            <Text style={s.h2}>{food.name}</Text>
            <Text style={s.label}>
              {[food.source !== 'blv' ? food.brand : food.category, SOURCE_LABEL[food.source]].filter(Boolean).join(' · ')}
            </Text>
          </View>
          <Pressable onPress={onToggleFavorite} hitSlop={12}>
            <Text style={{ fontSize: 24, color: isFavorite ? c.warn : c.muted }}>{isFavorite ? '★' : '☆'}</Text>
          </Pressable>
        </View>
        <Text style={[s.label, { marginTop: 8 }]}>
          Pro 100 g: {Math.round(food.kcal)} kcal · P {f1(food.protein)} · KH {f1(food.carbs)} · F {f1(food.fat)} g
        </Text>
        {onEditOwn && (
          <Pressable onPress={onEditOwn} style={{ marginTop: 6 }}>
            <Text style={{ color: c.muted, fontSize: 13 }}>Lebensmittel bearbeiten</Text>
          </Pressable>
        )}
      </View>

      <View style={s.card}>
        <NumField label="Menge" value={g} onChange={setG} suffix="g" />
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginTop: 10 }}>
          {food.servingG ? (
            <>
              <Chip title={`1 Portion (${food.servingG} g)`} active={grams === food.servingG} onPress={() => setG(String(food.servingG))} />
              <Chip title={`½ Portion`} active={grams === food.servingG / 2} onPress={() => setG(String(food.servingG! / 2))} />
              <Chip title={`2 Portionen`} active={grams === food.servingG * 2} onPress={() => setG(String(food.servingG! * 2))} />
            </>
          ) : null}
          {presets.map((p) => (
            <Chip key={p} title={`${p} g`} active={grams === p} onPress={() => setG(String(p))} />
          ))}
        </View>
      </View>

      <View style={[s.card, { borderColor: c.accent }]}>
        <View style={s.row}>
          <Text style={s.h2}>{grams} g</Text>
          <Text style={[s.h1, { color: c.accent }]}>{n.kcal} kcal</Text>
        </View>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 10 }}>
          <Macro label="Protein" v={n.protein} color={c.protein} />
          <Macro label="Kohlenh." v={n.carbs} color={c.carbs} />
          <Macro label="Fett" v={n.fat} color={c.fat} />
        </View>
        <View style={{ marginTop: 10 }}>
          <KV k="davon Zucker" v={`${f1(n.sugar)} g`} />
          <KV k="Ballaststoffe" v={`${f1(n.fiber)} g`} />
          <KV k="Salz" v={`${f1(n.salt)} g`} />
          <KV k="Gesättigte Fettsäuren" v={`${f1(n.satFat)} g`} />
        </View>
      </View>

      <View style={{ flexDirection: 'row', gap: 10 }}>
        {onDelete && <Btn title="Löschen" kind="danger" onPress={onDelete} />}
        <Btn title={actionLabel} disabled={grams <= 0} onPress={() => onConfirm(grams)} />
      </View>
    </View>
  );
}

function Macro({ label, v, color }: { label: string; v: number; color: string }) {
  return (
    <View style={{ alignItems: 'center', flex: 1 }}>
      <Text style={[s.h2, { color }]}>{f1(v)} g</Text>
      <Text style={s.label}>{label}</Text>
    </View>
  );
}
