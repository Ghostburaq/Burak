import { useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, Text, TextInput, View } from 'react-native';
import { blvFoods, searchFoods, searchOff, SOURCE_LABEL, type Food } from '../foods';
import { c } from '../theme';
import { s } from '../ui';

function Row({ f, onPress }: { f: Food; onPress: () => void }) {
  const sub = [f.source === 'blv' ? f.category : f.brand, SOURCE_LABEL[f.source]].filter(Boolean).join(' · ');
  return (
    <Pressable onPress={onPress} style={{ paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: c.border }}>
      <View style={s.row}>
        <Text style={[s.text, { flex: 1, marginRight: 10 }]} numberOfLines={2}>{f.name}</Text>
        <Text style={s.text}>{Math.round(f.kcal)}<Text style={s.label}> kcal</Text></Text>
      </View>
      <View style={s.row}>
        <Text style={[s.label, { flex: 1, marginRight: 8 }]} numberOfLines={1}>{sub}</Text>
        <Text style={s.label}>
          P {Math.round(f.protein)} · KH {Math.round(f.carbs)} · F {Math.round(f.fat)}{f.servingG ? ` · Portion ${f.servingG} g` : ' · pro 100 g'}
        </Text>
      </View>
    </Pressable>
  );
}

function Section({ title, foods, onPick, right }: { title: string; foods: Food[]; onPick: (f: Food) => void; right?: React.ReactNode }) {
  if (!foods.length) return null;
  return (
    <View style={s.card}>
      <View style={s.row}>
        <Text style={s.h2}>{title}</Text>
        {right}
      </View>
      {foods.map((f) => <Row key={f.id} f={f} onPress={() => onPick(f)} />)}
    </View>
  );
}

/** Suche über eigene Lebensmittel, Rezepte, Favoriten, BLV-Datenbank und optional Open Food Facts. */
export function FoodSearch({
  ownFoods, favorites, recent, onPick, onCreateOwn,
}: {
  ownFoods: Food[]; // eigene, gecachte Online-Produkte und Rezepte
  favorites: Food[];
  recent: Food[];
  onPick: (f: Food) => void;
  onCreateOwn: (name: string) => void;
}) {
  const [q, setQ] = useState('');
  const [online, setOnline] = useState<{ q: string; foods: Food[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const local = useMemo(() => {
    if (!q.trim()) return [];
    const seen = new Set<string>();
    const pool = [...ownFoods, ...favorites, ...blvFoods()].filter((f) => (seen.has(f.id) ? false : (seen.add(f.id), true)));
    return searchFoods(pool, q, 40);
  }, [q, ownFoods, favorites]);

  const goOnline = async () => {
    const query = q.trim();
    if (query.length < 2) return;
    setLoading(true); setError('');
    try {
      const foods = await searchOff(query);
      const localIds = new Set(local.map((f) => f.id));
      setOnline({ q: query, foods: foods.filter((f) => !localIds.has(f.id)) });
      if (!foods.length) setError('Keine Treffer mit Nährwerten bei Open Food Facts.');
    } catch {
      setOnline(null);
      setError('Online-Suche nicht erreichbar. Kein Netz, oder im Browser gesperrt: in der App auf dem Handy funktioniert sie.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      <View style={[s.inputWrap, { marginBottom: 12 }]}>
        <TextInput
          style={[s.input, { fontSize: 17 }]}
          value={q}
          onChangeText={(v) => { setQ(v); setError(''); }}
          placeholder="Lebensmittel suchen, z.B. Haferflocken"
          placeholderTextColor={c.muted}
          autoFocus
          returnKeyType="search"
          onSubmitEditing={goOnline}
        />
        {q ? (
          <Pressable onPress={() => { setQ(''); setOnline(null); }} hitSlop={10} style={{ paddingRight: 12 }}>
            <Text style={{ color: c.muted, fontSize: 16 }}>✕</Text>
          </Pressable>
        ) : null}
      </View>

      {!q.trim() ? (
        <>
          <Section title="Favoriten" foods={favorites} onPick={onPick} />
          <Section title="Zuletzt verwendet" foods={recent} onPick={onPick} />
          {!favorites.length && !recent.length && (
            <View style={s.card}>
              <Text style={s.h2}>Über 1200 Lebensmittel offline</Text>
              <Text style={[s.label, { marginTop: 6 }]}>
                Schweizer Nährwertdatenbank des BLV, dazu Millionen Markenprodukte online über Open Food Facts und den Barcode-Scanner. Mit ☆ markierte Lebensmittel erscheinen hier als Favoriten.
              </Text>
            </View>
          )}
        </>
      ) : (
        <>
          <Section title={`Treffer (${local.length}${local.length === 40 ? '+' : ''})`} foods={local} onPick={onPick} />
          {!local.length && <Text style={[s.label, { marginBottom: 12 }]}>Nichts in der Offline-Datenbank gefunden.</Text>}
          {online && online.q === q.trim() && <Section title="Open Food Facts" foods={online.foods} onPick={onPick} />}
          <View style={s.card}>
            {loading ? (
              <ActivityIndicator color={c.accent} />
            ) : (
              <Pressable onPress={goOnline}>
                <Text style={{ color: c.accent, fontWeight: '600' }}>Online suchen bei Open Food Facts (Markenprodukte)</Text>
              </Pressable>
            )}
            {error ? <Text style={[s.label, { marginTop: 8, color: c.warn }]}>{error}</Text> : null}
            <Pressable onPress={() => onCreateOwn(q.trim())} style={{ marginTop: 14 }}>
              <Text style={{ color: c.muted, fontWeight: '600' }}>+ „{q.trim()}“ als eigenes Lebensmittel anlegen</Text>
            </Pressable>
          </View>
        </>
      )}
    </View>
  );
}
