import { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { recipeToFood, scale, type Recipe, type RecipeItem } from '../foods';
import { parseNum } from '../logic';
import { c } from '../theme';
import { Btn, KV, NumField, s, TextField } from '../ui';

const dec = (n: number) => String(Math.round(n * 10) / 10).replace('.', ',');

/** Rezept bearbeiten. Zutaten kommen über die normale Suche (onAddIngredient). */
export function RecipeEditor({
  recipe, onChange, onAddIngredient, onSave, onDelete, onBack,
}: {
  recipe: Recipe;
  onChange: (r: Recipe) => void;
  onAddIngredient: () => void;
  onSave: () => void;
  onDelete?: () => void;
  onBack: () => void;
}) {
  const [portions, setPortions] = useState(String(recipe.portions));
  const food = recipeToFood(recipe);
  const totalG = recipe.items.reduce((a, i) => a + i.grams, 0);
  const portion = food.servingG ? scale(food, food.servingG) : null;
  const canSave = recipe.name.trim() !== '' && recipe.items.length > 0 && recipe.portions > 0;

  const setItem = (idx: number, it: RecipeItem | null) => {
    const items = [...recipe.items];
    if (it) items[idx] = it; else items.splice(idx, 1);
    onChange({ ...recipe, items });
  };

  return (
    <View>
      <Pressable onPress={onBack} style={{ marginBottom: 10 }} hitSlop={10}>
        <Text style={{ color: c.muted }}>‹ Zurück</Text>
      </Pressable>
      <View style={s.card}>
        <View style={{ flexDirection: 'row', gap: 10, alignItems: 'flex-end' }}>
          <View style={{ flex: 2 }}>
            <TextField label="Rezeptname" value={recipe.name} onChange={(name) => onChange({ ...recipe, name })} placeholder="z.B. Overnight Oats" />
          </View>
          <NumField label="Portionen" value={portions} onChange={(v) => { setPortions(v); const n = parseNum(v); if (n && n > 0) onChange({ ...recipe, portions: n }); }} />
        </View>
      </View>

      <View style={s.card}>
        <View style={s.row}>
          <Text style={s.h2}>Zutaten</Text>
          <Text style={s.label}>{totalG} g gesamt</Text>
        </View>
        {recipe.items.map((it, i) => (
          <View key={i} style={{ flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: c.border }}>
            <View style={{ flex: 1 }}>
              <Text style={s.text} numberOfLines={1}>{it.food.name}</Text>
              <Text style={s.label}>{scale(it.food, it.grams).kcal} kcal</Text>
            </View>
            <View style={{ width: 90 }}>
              <NumField label="" value={String(it.grams)} onChange={(v) => { const g = parseNum(v); if (g !== null) setItem(i, { ...it, grams: g }); }} suffix="g" />
            </View>
            <Pressable onPress={() => setItem(i, null)} hitSlop={10}>
              <Text style={{ color: c.muted, fontSize: 16 }}>✕</Text>
            </Pressable>
          </View>
        ))}
        <Pressable onPress={onAddIngredient} style={{ paddingTop: 12 }}>
          <Text style={{ color: c.accent, fontWeight: '600' }}>+ Zutat hinzufügen</Text>
        </Pressable>
      </View>

      {portion && (
        <View style={[s.card, { borderColor: c.accent }]}>
          <KV k={`Pro Portion (${food.servingG} g)`} v={`${portion.kcal} kcal`} strong />
          <Text style={s.label}>P {dec(portion.protein)} g · KH {dec(portion.carbs)} g · F {dec(portion.fat)} g</Text>
          <KV k="Ganzes Rezept" v={`${scale(food, totalG).kcal} kcal`} />
        </View>
      )}

      <View style={{ flexDirection: 'row', gap: 10 }}>
        {onDelete && <Btn title="Löschen" kind="danger" onPress={onDelete} />}
        <Btn title="Rezept speichern" disabled={!canSave} onPress={onSave} />
      </View>
    </View>
  );
}
