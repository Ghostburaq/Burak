import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { addDays, formatDate, parseNum, toDateKey, type Entry } from './logic';
import { adaptiveTdee, currentTrend, sortedWeights, trendAt, type Profile, type Weights } from './nutrition';
import { c } from './theme';
import { Btn, KV, NumField, s } from './ui';

const fmt = (n: number, d = 1) => n.toFixed(d).replace('.', ',');
const signed = (n: number) => (n > 0 ? '+' : n < 0 ? '−' : '±') + fmt(Math.abs(n));

export function WeightScreen({
  weights, entries, profile, formulaTdee, onSetWeight, onDeleteWeight, onApplyTdee,
}: {
  weights: Weights;
  entries: Entry[];
  profile: Profile;
  formulaTdee: number;
  onSetWeight: (date: string, kg: number) => void;
  onDeleteWeight: (date: string) => void;
  onApplyTdee: (tdee: number | null) => void;
}) {
  const today = toDateKey(new Date());
  const [input, setInput] = useState(weights[today] ? fmt(weights[today]) : '');
  const kg = parseNum(input);
  const list = sortedWeights(weights);
  const trend = currentTrend(weights);
  const last = list[list.length - 1];
  const delta = (days: number) => {
    if (!last) return null;
    const past = trendAt(weights, addDays(last.date, -days));
    return trend !== null && past !== null ? trend - past : null;
  };
  const d7 = delta(7);
  const d30 = delta(30);
  const ad = adaptiveTdee(entries, weights, today);

  // Diagramm: letzte 42 Tage
  const DAYS = 42;
  const H = 150;
  const start = addDays(today, -(DAYS - 1));
  const days = Array.from({ length: DAYS }, (_, i) => addDays(start, i));
  const pts = days.map((d) => ({ d, w: weights[d], t: trendAt(weights, d) }));
  const vals = pts.flatMap((p) => [p.w, p.t]).filter((v): v is number => typeof v === 'number');
  const lo = vals.length ? Math.min(...vals) - 0.5 : 0;
  const hi = vals.length ? Math.max(...vals) + 0.5 : 1;
  const y = (v: number) => ((v - lo) / (hi - lo)) * H;

  return (
    <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 40 }} keyboardShouldPersistTaps="handled">
      <Text style={[s.h1, { marginBottom: 14 }]}>Gewicht</Text>

      <View style={s.card}>
        <Text style={s.label}>Heute wiegen, am besten morgens nüchtern</Text>
        <View style={{ flexDirection: 'row', gap: 10, alignItems: 'flex-end', marginTop: 8 }}>
          <NumField label="" value={input} onChange={setInput} suffix="kg" placeholder={trend ? fmt(trend) : '80,0'} />
          <View style={{ width: 130, flexDirection: 'row' }}>
            <Btn title="Speichern" disabled={!kg || kg < 20 || kg > 400} onPress={() => kg && onSetWeight(today, Math.round(kg * 10) / 10)} />
          </View>
        </View>
      </View>

      <View style={s.card}>
        <View style={s.row}>
          <View>
            <Text style={s.label}>Trendgewicht (Ø 7 Tage)</Text>
            <Text style={[s.h1, { fontSize: 30 }]}>{trend ? `${fmt(trend)} kg` : '–'}</Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={s.label}>7 Tage: <Text style={{ color: c.text }}>{d7 !== null ? `${signed(d7)} kg` : '–'}</Text></Text>
            <Text style={s.label}>30 Tage: <Text style={{ color: c.text }}>{d30 !== null ? `${signed(d30)} kg` : '–'}</Text></Text>
          </View>
        </View>
        {vals.length > 0 ? (
          <View style={{ height: H, marginTop: 16, flexDirection: 'row', alignItems: 'flex-end' }}>
            {pts.map((p) => (
              <View key={p.d} style={{ flex: 1, height: H }}>
                {p.t !== null && (
                  <View style={{ position: 'absolute', bottom: y(p.t) - 1.5, left: 0, right: 0, height: 3, backgroundColor: c.accent, opacity: 0.85 }} />
                )}
                {p.w !== undefined && (
                  <View style={{ position: 'absolute', bottom: y(p.w) - 3, alignSelf: 'center', width: 6, height: 6, borderRadius: 3, backgroundColor: c.muted }} />
                )}
              </View>
            ))}
          </View>
        ) : (
          <Text style={[s.label, { marginTop: 12 }]}>Noch keine Wiegungen.</Text>
        )}
        {vals.length > 0 && (
          <Text style={[s.label, { marginTop: 8 }]}>
            Punkte = Wiegung, Linie = Trend. {fmt(lo + 0.5)} bis {fmt(hi - 0.5)} kg, letzte 6 Wochen.
          </Text>
        )}
      </View>

      <View style={s.card}>
        <Text style={s.h2}>Dein echter Verbrauch</Text>
        <Text style={[s.label, { marginTop: 4, marginBottom: 8 }]}>
          Aus Essensprotokoll und Gewichtsverlauf der letzten {ad.windowDays} Tage zurückgerechnet. Genauer als jede Formel, weil er deinen Stoffwechsel und deine Alltagsbewegung enthält.
        </Text>
        {ad.ok ? (
          <>
            <KV k="Ø Zufuhr (erfasste Tage)" v={`${ad.avgIntake} kcal`} />
            <KV k="Gewichtstrend" v={`${signed(ad.kgPerWeek!)} kg/Woche`} />
            <KV k="Formel (Profil)" v={`${Math.round(formulaTdee)} kcal`} />
            <KV k="Tatsächlicher Verbrauch" v={`${ad.tdee} kcal`} strong />
            <Text style={[s.label, { marginTop: 6 }]}>
              Basis: {ad.loggedDays} erfasste Tage, {ad.weighIns} Wiegungen. Unvollständig erfasste Tage drücken den Wert nach unten.
            </Text>
            <View style={{ flexDirection: 'row', marginTop: 12 }}>
              <Btn title={profile.tdeeOverride === ad.tdee ? 'Übernommen' : 'Als Verbrauch übernehmen'} onPress={() => onApplyTdee(ad.tdee!)} disabled={profile.mode === 'manual'} />
            </View>
          </>
        ) : (
          <Text style={[s.text, { color: c.muted }]}>{ad.reason}</Text>
        )}
        {profile.tdeeOverride !== null && (
          <Pressable onPress={() => onApplyTdee(null)} style={{ marginTop: 12 }}>
            <Text style={{ color: c.muted }}>Aktiv: {profile.tdeeOverride} kcal. Zurück zur Formel</Text>
          </Pressable>
        )}
      </View>

      {list.length > 0 && (
        <View style={s.card}>
          <Text style={[s.h2, { marginBottom: 6 }]}>Wiegungen</Text>
          {list.slice(-14).reverse().map((p) => (
            <View key={p.date} style={[s.row, { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: c.border }]}>
              <Text style={s.text}>{formatDate(p.date)}</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 16 }}>
                <Text style={s.text}>{fmt(p.kg)} kg</Text>
                <Pressable onPress={() => onDeleteWeight(p.date)} hitSlop={10}>
                  <Text style={{ color: c.muted }}>✕</Text>
                </Pressable>
              </View>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}
