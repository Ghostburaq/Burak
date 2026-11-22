import { useEffect, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import {
  addDays, formatDate, isoWeek, MEALS, parseNum, sum, toDateKey, weekdayShort, weekStats,
  type Entry, type Goals, type Meal,
} from './logic';
import { c } from './theme';
import { Btn, MacroLine, NumField, s } from './ui';

// ---------- Heute / Tag ----------

export function DayScreen({
  date, setDate, entries, goals, onAdd, onEdit,
}: {
  date: string;
  setDate: (d: string) => void;
  entries: Entry[];
  goals: Goals;
  onAdd: (meal: Meal) => void;
  onEdit: (e: Entry) => void;
}) {
  const today = toDateKey(new Date());
  const dayEntries = entries.filter((e) => e.date === date);
  const t = sum(dayEntries);
  const rest = goals.kcal - t.kcal;

  return (
    <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 110 }}>
      <View style={[s.row, { marginBottom: 14 }]}>
        <Pressable onPress={() => setDate(addDays(date, -1))} hitSlop={12}>
          <Text style={[s.h1, { color: c.muted }]}>‹</Text>
        </Pressable>
        <Pressable onPress={() => setDate(today)} style={{ alignItems: 'center' }}>
          <Text style={s.h2}>{date === today ? 'Heute' : `${weekdayShort(date)}, ${formatDate(date)}`}</Text>
          <Text style={s.label}>KW {isoWeek(date)}{date !== today ? ' · tippen für heute' : ''}</Text>
        </Pressable>
        <Pressable onPress={() => setDate(addDays(date, 1))} hitSlop={12} disabled={date >= today}>
          <Text style={[s.h1, { color: date >= today ? c.border : c.muted }]}>›</Text>
        </Pressable>
      </View>

      <View style={s.card}>
        <View style={s.row}>
          <View>
            <Text style={s.label}>Gegessen</Text>
            <Text style={[s.h1, { fontSize: 30 }]}>{Math.round(t.kcal)}</Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={s.label}>{rest >= 0 ? 'Übrig' : 'Über Ziel'}</Text>
            <Text style={[s.h1, { fontSize: 30, color: rest >= 0 ? c.accent : c.over }]}>{Math.abs(Math.round(rest))}</Text>
          </View>
        </View>
        <MacroLine label="Energie" value={t.kcal} goal={goals.kcal} unit="kcal" color={c.accent} />
        <MacroLine label="Protein" value={t.protein} goal={goals.protein} unit="g" color={c.protein} />
        <MacroLine label="Kohlenhydrate" value={t.carbs} goal={goals.carbs} unit="g" color={c.carbs} />
        <MacroLine label="Fett" value={t.fat} goal={goals.fat} unit="g" color={c.fat} />
      </View>

      {MEALS.map((m) => {
        const list = dayEntries.filter((e) => e.meal === m.key).sort((a, b) => a.createdAt - b.createdAt);
        const mt = sum(list);
        return (
          <View key={m.key} style={s.card}>
            <View style={s.row}>
              <Text style={s.h2}>{m.label}</Text>
              <Text style={s.label}>{Math.round(mt.kcal)} kcal</Text>
            </View>
            {list.map((e) => (
              <Pressable key={e.id} onPress={() => onEdit(e)} style={{ paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: c.border }}>
                <View style={s.row}>
                  <Text style={[s.text, { flex: 1, marginRight: 10 }]} numberOfLines={1}>{e.name}</Text>
                  <Text style={s.text}>{Math.round(e.kcal)}</Text>
                </View>
                <Text style={s.label}>
                  P {Math.round(e.protein)} · KH {Math.round(e.carbs)} · F {Math.round(e.fat)} g
                </Text>
              </Pressable>
            ))}
            <Pressable onPress={() => onAdd(m.key)} style={{ paddingTop: 12 }}>
              <Text style={{ color: c.accent, fontWeight: '600' }}>+ Hinzufügen</Text>
            </Pressable>
          </View>
        );
      })}
    </ScrollView>
  );
}

// ---------- Woche ----------

export function WeekScreen({
  entries, goals, onOpenDay,
}: { entries: Entry[]; goals: Goals; onOpenDay: (d: string) => void }) {
  const today = toDateKey(new Date());
  const [ref, setRef] = useState(today);
  const w = weekStats(entries, ref);
  const max = Math.max(goals.kcal * 1.25, ...w.days.map((d) => d.totals.kcal), 1);
  const goalPos = goals.kcal / max;
  const BAR_H = 160;

  return (
    <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
      <View style={[s.row, { marginBottom: 14 }]}>
        <Pressable onPress={() => setRef(addDays(ref, -7))} hitSlop={12}>
          <Text style={[s.h1, { color: c.muted }]}>‹</Text>
        </Pressable>
        <View style={{ alignItems: 'center' }}>
          <Text style={s.h2}>KW {isoWeek(ref)}</Text>
          <Text style={s.label}>{formatDate(w.days[0].date)} bis {formatDate(w.days[6].date)}</Text>
        </View>
        <Pressable onPress={() => setRef(addDays(ref, 7))} hitSlop={12} disabled={w.days[6].date >= today}>
          <Text style={[s.h1, { color: w.days[6].date >= today ? c.border : c.muted }]}>›</Text>
        </Pressable>
      </View>

      <View style={s.card}>
        <Text style={s.label}>Energie pro Tag, Linie = Ziel {goals.kcal} kcal</Text>
        <View style={{ height: BAR_H, flexDirection: 'row', alignItems: 'flex-end', marginTop: 14 }}>
          <View style={{ position: 'absolute', left: 0, right: 0, bottom: goalPos * BAR_H, height: 1, backgroundColor: c.muted, opacity: 0.6 }} />
          {w.days.map((d) => {
            const h = (d.totals.kcal / max) * BAR_H;
            const over = d.totals.kcal > goals.kcal;
            return (
              <Pressable key={d.date} onPress={() => onOpenDay(d.date)} style={{ flex: 1, alignItems: 'center', justifyContent: 'flex-end', height: '100%' }}>
                <View style={{ width: '60%', height: Math.max(h, d.totals.kcal > 0 ? 3 : 0), backgroundColor: over ? c.over : c.accent, borderRadius: 4 }} />
              </Pressable>
            );
          })}
        </View>
        <View style={{ flexDirection: 'row', marginTop: 6 }}>
          {w.days.map((d) => (
            <View key={d.date} style={{ flex: 1, alignItems: 'center' }}>
              <Text style={[s.label, d.date === today && { color: c.text, fontWeight: '700' }]}>{weekdayShort(d.date)}</Text>
              <Text style={[s.label, { fontSize: 11 }]}>{d.totals.kcal ? Math.round(d.totals.kcal) : '–'}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={s.card}>
        <Text style={s.h2}>Schnitt pro erfasstem Tag</Text>
        <Text style={s.label}>{w.loggedDays} von 7 Tagen erfasst</Text>
        {w.loggedDays > 0 ? (
          <>
            <MacroLine label="Energie" value={w.avg.kcal} goal={goals.kcal} unit="kcal" color={c.accent} />
            <MacroLine label="Protein" value={w.avg.protein} goal={goals.protein} unit="g" color={c.protein} />
            <MacroLine label="Kohlenhydrate" value={w.avg.carbs} goal={goals.carbs} unit="g" color={c.carbs} />
            <MacroLine label="Fett" value={w.avg.fat} goal={goals.fat} unit="g" color={c.fat} />
          </>
        ) : (
          <Text style={[s.text, { marginTop: 10, color: c.muted }]}>Noch keine Einträge in dieser Woche.</Text>
        )}
      </View>
    </ScrollView>
  );
}

// ---------- Ziele ----------

export function GoalsScreen({ goals, onSave }: { goals: Goals; onSave: (g: Goals) => void }) {
  const [kcal, setKcal] = useState(String(goals.kcal));
  const [protein, setProtein] = useState(String(goals.protein));
  const [carbs, setCarbs] = useState(String(goals.carbs));
  const [fat, setFat] = useState(String(goals.fat));
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setKcal(String(goals.kcal)); setProtein(String(goals.protein)); setCarbs(String(goals.carbs)); setFat(String(goals.fat));
  }, [goals]);

  const vals = [kcal, protein, carbs, fat].map(parseNum);
  const valid = vals.every((v) => v !== null) && (vals[0] ?? 0) > 0;
  const macroKcal = Math.round((vals[1] ?? 0) * 4 + (vals[2] ?? 0) * 4 + (vals[3] ?? 0) * 9);

  return (
    <ScrollView contentContainerStyle={{ padding: 16 }} keyboardShouldPersistTaps="handled">
      <Text style={[s.h1, { marginBottom: 14 }]}>Tagesziele</Text>
      <View style={s.card}>
        <NumField label="Energie" value={kcal} onChange={(v) => { setKcal(v); setSaved(false); }} suffix="kcal" />
        <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
          <NumField label="Protein" value={protein} onChange={(v) => { setProtein(v); setSaved(false); }} suffix="g" />
          <NumField label="Kohlenhydrate" value={carbs} onChange={(v) => { setCarbs(v); setSaved(false); }} suffix="g" />
          <NumField label="Fett" value={fat} onChange={(v) => { setFat(v); setSaved(false); }} suffix="g" />
        </View>
        <Text style={[s.label, { marginTop: 12 }]}>
          Makroziele ergeben {macroKcal} kcal
          {valid && Math.abs(macroKcal - (vals[0] ?? 0)) > 50 ? ` (Abweichung ${macroKcal - (vals[0] ?? 0)} kcal zum Energieziel)` : ''}
        </Text>
      </View>
      <View style={{ flexDirection: 'row' }}>
        <Btn
          title={saved ? 'Gespeichert' : 'Ziele speichern'}
          disabled={!valid}
          onPress={() => {
            onSave({ kcal: vals[0]!, protein: vals[1]!, carbs: vals[2]!, fat: vals[3]! });
            setSaved(true);
          }}
        />
      </View>
      <Text style={[s.label, { marginTop: 16 }]}>Alle Daten bleiben lokal auf diesem Gerät.</Text>
    </ScrollView>
  );
}
