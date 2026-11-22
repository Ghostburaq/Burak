import { useEffect, useMemo, useState } from 'react';
import { Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { recipeToFood, scale, type Food, type Recipe } from '../foods';
import { MEALS, type Entry, type EntryDraft, type Meal, type Template } from '../logic';
import { newId } from '../storage';
import { c } from '../theme';
import { Chip, s, Segmented } from '../ui';
import { AmountView } from './AmountView';
import { FoodSearch } from './FoodSearch';
import { ManualForm } from './ManualForm';
import { OwnFoodForm } from './OwnFoodForm';
import { RecipeEditor } from './RecipeEditor';
import { Scanner } from './Scanner';

type Tab = 'suche' | 'scan' | 'manuell' | 'rezepte';
type Screen =
  | { k: 'tabs' }
  | { k: 'amount'; food: Food; grams?: number; purpose: 'entry' | 'ingredient' }
  | { k: 'own'; initial: Partial<Food>; then: 'entry' | 'ingredient' }
  | { k: 'recipe' };

export interface AddModalProps {
  visible: boolean;
  editing: Entry | null;
  defaultMeal: Meal;
  entries: Entry[];
  templates: Template[];
  recentManual: Template[];
  myFoods: Food[];
  favorites: Food[];
  recipes: Recipe[];
  onClose: () => void;
  onSaveEntry: (draft: EntryDraft, template: Omit<Template, 'id'> | null) => void;
  onDeleteEntry: (id: string) => void;
  onDeleteTemplate: (id: string) => void;
  onUpsertFood: (f: Food) => void;
  onDeleteFood: (id: string) => void;
  onToggleFavorite: (f: Food) => void;
  onSaveRecipe: (r: Recipe) => void;
  onDeleteRecipe: (id: string) => void;
}

export function entryFromFood(food: Food, grams: number, meal: Meal): EntryDraft {
  const n = scale(food, grams);
  return {
    name: food.brand && food.source === 'off' ? `${food.name} (${food.brand})` : food.name,
    meal, grams, food,
    kcal: n.kcal, protein: n.protein, carbs: n.carbs, fat: n.fat,
    sugar: n.sugar, fiber: n.fiber, salt: n.salt,
  };
}

export function AddModal(p: AddModalProps) {
  const [tab, setTab] = useState<Tab>('suche');
  const [meal, setMeal] = useState<Meal>(p.defaultMeal);
  const [screen, setScreen] = useState<Screen>({ k: 'tabs' });
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [picking, setPicking] = useState(false); // Zutat für Rezept wählen

  useEffect(() => {
    if (!p.visible) return;
    setMeal(p.editing?.meal ?? p.defaultMeal);
    setRecipe(null);
    setPicking(false);
    if (p.editing?.food) {
      setScreen({ k: 'amount', food: p.editing.food, grams: p.editing.grams, purpose: 'entry' });
    } else {
      setScreen({ k: 'tabs' });
      setTab(p.editing ? 'manuell' : 'suche');
    }
  }, [p.visible, p.editing, p.defaultMeal]);

  const recentFoods = useMemo(() => {
    const seen = new Set<string>();
    const out: Food[] = [];
    for (const e of [...p.entries].sort((a, b) => b.createdAt - a.createdAt)) {
      if (!e.food || seen.has(e.food.id)) continue;
      seen.add(e.food.id);
      out.push(e.food);
      if (out.length >= 15) break;
    }
    return out;
  }, [p.entries]);

  const recipeFoods = useMemo(() => p.recipes.map(recipeToFood), [p.recipes]);
  const searchPool = useMemo(() => [...p.myFoods, ...recipeFoods], [p.myFoods, recipeFoods]);
  const isFav = (f: Food) => p.favorites.some((x) => x.id === f.id);

  const pick = (food: Food) => {
    // Online-Produkte lokal merken, damit sie offline und per Barcode sofort wieder da sind
    if (food.source === 'off' && !p.myFoods.some((f) => f.id === food.id)) p.onUpsertFood(food);
    setScreen({ k: 'amount', food, purpose: picking ? 'ingredient' : 'entry' });
  };

  const confirmAmount = (food: Food, grams: number, purpose: 'entry' | 'ingredient') => {
    if (purpose === 'ingredient' && recipe) {
      setRecipe({ ...recipe, items: [...recipe.items, { food, grams }] });
      setPicking(false);
      setScreen({ k: 'recipe' });
      return;
    }
    p.onSaveEntry(entryFromFood(food, grams, meal), null);
  };

  const startRecipe = (r?: Recipe) => {
    setRecipe(r ? { ...r, items: [...r.items] } : { id: newId(), name: '', items: [], portions: 1 });
    setScreen({ k: 'recipe' });
  };

  const title = p.editing ? 'Eintrag bearbeiten' : picking ? 'Zutat wählen' : 'Hinzufügen';
  const showMeal = !picking && (screen.k === 'tabs' || (screen.k === 'amount' && screen.purpose === 'entry'));

  let body: React.ReactNode;
  if (screen.k === 'amount') {
    const own = screen.food.source === 'eigen' ? p.myFoods.find((f) => f.id === screen.food.id) : undefined;
    body = (
      <AmountView
        food={screen.food}
        initialGrams={screen.grams}
        isFavorite={isFav(screen.food)}
        actionLabel={screen.purpose === 'ingredient' ? 'Zum Rezept hinzufügen' : p.editing ? 'Speichern' : 'Hinzufügen'}
        onToggleFavorite={() => p.onToggleFavorite(screen.food)}
        onConfirm={(g) => confirmAmount(screen.food, g, screen.purpose)}
        onDelete={p.editing ? () => p.onDeleteEntry(p.editing!.id) : undefined}
        onBack={p.editing ? undefined : () => setScreen({ k: 'tabs' })}
        onEditOwn={own ? () => setScreen({ k: 'own', initial: own, then: screen.purpose }) : undefined}
      />
    );
  } else if (screen.k === 'own') {
    body = (
      <OwnFoodForm
        initial={screen.initial}
        onBack={() => setScreen({ k: 'tabs' })}
        onDelete={(id) => { p.onDeleteFood(id); setScreen({ k: 'tabs' }); }}
        onSave={(f) => { p.onUpsertFood(f); setScreen({ k: 'amount', food: f, purpose: screen.then }); }}
      />
    );
  } else if (screen.k === 'recipe' && recipe) {
    const existing = p.recipes.some((r) => r.id === recipe.id);
    body = (
      <RecipeEditor
        recipe={recipe}
        onChange={setRecipe}
        onAddIngredient={() => { setPicking(true); setTab('suche'); setScreen({ k: 'tabs' }); }}
        onSave={() => { p.onSaveRecipe(recipe); setRecipe(null); setTab('rezepte'); setScreen({ k: 'tabs' }); }}
        onDelete={existing ? () => { p.onDeleteRecipe(recipe.id); setRecipe(null); setTab('rezepte'); setScreen({ k: 'tabs' }); } : undefined}
        onBack={() => { setRecipe(null); setTab('rezepte'); setScreen({ k: 'tabs' }); }}
      />
    );
  } else {
    const tabs: { key: Tab; label: string }[] = picking
      ? [{ key: 'suche', label: 'Suchen' }, { key: 'scan', label: 'Scannen' }]
      : [{ key: 'suche', label: 'Suchen' }, { key: 'scan', label: 'Scannen' }, { key: 'manuell', label: 'Schnell' }, { key: 'rezepte', label: 'Rezepte' }];
    body = (
      <>
        {!p.editing && <Segmented options={tabs} value={tab} onChange={setTab} />}
        {picking && (
          <Pressable onPress={() => { setPicking(false); setScreen({ k: 'recipe' }); }} style={{ marginTop: 10 }}>
            <Text style={{ color: c.muted }}>‹ Zurück zum Rezept</Text>
          </Pressable>
        )}
        <View style={{ height: 12 }} />
        {tab === 'suche' && (
          <FoodSearch
            ownFoods={searchPool}
            favorites={p.favorites}
            recent={recentFoods}
            onPick={pick}
            onCreateOwn={(name) => setScreen({ k: 'own', initial: { name }, then: picking ? 'ingredient' : 'entry' })}
          />
        )}
        {tab === 'scan' && (
          <Scanner
            localByBarcode={(code) => p.myFoods.find((f) => f.barcode === code)}
            onFound={pick}
            onNotFound={(code) => setScreen({ k: 'own', initial: { barcode: code }, then: picking ? 'ingredient' : 'entry' })}
          />
        )}
        {tab === 'manuell' && (
          <ManualForm
            meal={meal}
            editing={p.editing}
            templates={p.templates}
            recent={p.recentManual}
            onSave={p.onSaveEntry}
            onDelete={p.onDeleteEntry}
            onDeleteTemplate={p.onDeleteTemplate}
          />
        )}
        {tab === 'rezepte' && (
          <View>
            <View style={s.card}>
              <Pressable onPress={() => startRecipe()}>
                <Text style={{ color: c.accent, fontWeight: '600' }}>+ Neues Rezept</Text>
              </Pressable>
              <Text style={[s.label, { marginTop: 6 }]}>Zutaten aus der Datenbank, Portionen festlegen, danach mit einem Tipp eintragen.</Text>
            </View>
            {p.recipes.map((r) => {
              const f = recipeToFood(r);
              const portion = f.servingG ? scale(f, f.servingG) : null;
              return (
                <View key={r.id} style={s.card}>
                  <Pressable onPress={() => setScreen({ k: 'amount', food: f, purpose: 'entry' })}>
                    <View style={s.row}>
                      <Text style={[s.h2, { flex: 1 }]}>{r.name}</Text>
                      <Text style={s.text}>{portion?.kcal ?? 0} kcal</Text>
                    </View>
                    <Text style={s.label}>
                      {r.items.length} Zutaten · {r.portions} Portionen · Portion {f.servingG} g · P {Math.round(portion?.protein ?? 0)} g
                    </Text>
                  </Pressable>
                  <Pressable onPress={() => startRecipe(r)} style={{ marginTop: 8 }}>
                    <Text style={{ color: c.muted, fontSize: 13 }}>Bearbeiten</Text>
                  </Pressable>
                </View>
              );
            })}
          </View>
        )}
      </>
    );
  }

  return (
    <Modal visible={p.visible} animationType="slide" onRequestClose={p.onClose} presentationStyle="pageSheet">
      <SafeAreaView style={{ flex: 1, backgroundColor: c.bg }}>
        <View style={[s.row, { padding: 16, paddingBottom: 8 }]}>
          <Text style={s.h1}>{title}</Text>
          <Pressable onPress={p.onClose} hitSlop={12}>
            <Text style={[s.text, { color: c.muted }]}>Schliessen</Text>
          </Pressable>
        </View>
        {showMeal && (
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 16 }}>
            {MEALS.map((m) => (
              <Chip key={m.key} title={m.label} active={meal === m.key} onPress={() => setMeal(m.key)} />
            ))}
          </View>
        )}
        <ScrollView contentContainerStyle={{ padding: 16, paddingTop: 4, paddingBottom: 60 }} keyboardShouldPersistTaps="handled">
          {body}
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
}
