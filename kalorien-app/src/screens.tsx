import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import {
  addDays, formatDate, isoWeek, MEALS, sum, sumMicros, toDateKey, weekdayShort, weekStats,
  type Entry, type Goals, type Meal,
} from './logic';
import { c } from './theme';
import { Bar, Btn, Chip, MacroLine, s } from './ui';

// ---------- Tag ----------

export function DayScreen({
  date, setDate, entries, goals, isTraining, onToggleTraining, water, waterGoal, onWater,
  configured, onSetup, onAdd, onEdit, onCopyMeal,
}: {
  date: string;
  setDate: (d: string) => void;
  entries: Entry[];
  goals: Goals;
  isTraining: boolean;
  onToggleTraining: () => void;
  water: number;
  waterGoal: number;
  onWater: (delta: number) => void;
  configured: boolean;
  onSetup: () => void;
  onAdd: (meal: Meal) => void;
  onEdit: (e: Entry) => void;
  onCopyMeal: (meal: Meal, from: string) => void;
}) {
  const today = toDateKey(new Date());
  const yesterday = addDays(date, -1);
  const dayEntries = entries.filter((e) => e.date === date);
  const t = sum(dayEntries);
  const micro = sumMicros(dayEntries);
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

      {!configured && (
        <View style={[s.card, { borderColor: c.accent }]}>
          <Text style={s.h2}>Profil einrichten</Text>
          <Text style={[s.label, { marginTop: 4, marginBottom: 12 }]}>
            Mit Grösse, Gewicht, Alter, Aktivität und Ziel berechnet die App deinen Bedarf und deine Makros.
          </Text>
          <View style={{ flexDirection: 'row' }}>
            <Btn title="Jetzt einrichten" onPress={onSetup} />
          </View>
        </View>
      )}

      <View style={s.card}>
        <View style={s.row}>
          <View>
            <Text style={s.label}>Gegessen</Text>
            <Text style={[s.h1, { fontSize: 30 }]}>{Math.round(t.kcal)}</Text>
          </View>
          <Chip title={isTraining ? 'Trainingstag ✓' : 'Trainingstag?'} active={isTraining} onPress={onToggleTraining} />
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={s.label}>{rest >= 0 ? 'Übrig' : 'Über Ziel'}</Text>
            <Text style={[s.h1, { fontSize: 30, color: rest >= 0 ? c.accent : c.over }]}>{Math.abs(Math.round(rest))}</Text>
          </View>
        </View>
        <MacroLine label="Energie" value={t.kcal} goal={goals.kcal} unit="kcal" color={c.accent} />
        <MacroLine label="Protein" value={t.protein} goal={goals.protein} unit="g" color={c.protein} min />
        <MacroLine label="Kohlenhydrate" value={t.carbs} goal={goals.carbs} unit="g" color={c.carbs} />
        <MacroLine label="Fett" value={t.fat} goal={goals.fat} unit="g" color={c.fat} />
        {dayEntries.length > 0 && (
          <View style={[s.row, { marginTop: 12, paddingTop: 10, borderTopWidth: 1, borderTopColor: c.border }]}>
            <MicroStat label="Ballaststoffe" v={micro.fiber} ref_="≥ 30" good={micro.fiber >= 30} />
            <MicroStat label="Zucker" v={micro.sugar} />
            <MicroStat label="Salz" v={micro.salt} ref_="≤ 5" bad={micro.salt > 5} />
          </View>
        )}
        {micro.missing > 0 && dayEntries.length > 0 && (
          <Text style={[s.label, { fontSize: 11, marginTop: 4 }]}>
            {micro.missing} {micro.missing === 1 ? 'Eintrag' : 'Einträge'} ohne Angaben zu Ballaststoffen, Zucker, Salz
          </Text>
        )}
      </View>

      {MEALS.map((m) => {
        const list = dayEntries.filter((e) => e.meal === m.key).sort((a, b) => a.createdAt - b.createdAt);
        const mt = sum(list);
        const canCopy = list.length === 0 && entries.some((e) => e.date === yesterday && e.meal === m.key);
        return (
          <View key={m.key} style={s.card}>
            <View style={s.row}>
              <Text style={s.h2}>{m.label}</Text>
              <Text style={s.label}>
                {Math.round(mt.kcal)} kcal{mt.protein > 0 ? ` · P ${Math.round(mt.protein)} g` : ''}
              </Text>
            </View>
            {list.map((e) => (
              <Pressable key={e.id} onPress={() => onEdit(e)} style={{ paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: c.border }}>
                <View style={s.row}>
                  <Text style={[s.text, { flex: 1, marginRight: 10 }]} numberOfLines={1}>{e.name}</Text>
                  <Text style={s.text}>{Math.round(e.kcal)}</Text>
                </View>
                <Text style={s.label}>
                  {e.grams ? `${e.grams} g · ` : ''}P {Math.round(e.protein)} · KH {Math.round(e.carbs)} · F {Math.round(e.fat)} g
                </Text>
              </Pressable>
            ))}
            <View style={[s.row, { paddingTop: 12 }]}>
              <Pressable onPress={() => onAdd(m.key)}>
                <Text style={{ color: c.accent, fontWeight: '600' }}>+ Hinzufügen</Text>
              </Pressable>
              {canCopy && (
                <Pressable onPress={() => onCopyMeal(m.key, yesterday)}>
                  <Text style={{ color: c.muted, fontWeight: '600' }}>↻ Wie gestern</Text>
                </Pressable>
              )}
            </View>
          </View>
        );
      })}

      <View style={s.card}>
        <View style={s.row}>
          <Text style={s.h2}>Wasser</Text>
          <Text style={s.label}>
            <Text style={{ color: c.text }}>{(water / 1000).toFixed(2).replace('.', ',')}</Text> / {(waterGoal / 1000).toFixed(1).replace('.', ',')} l
          </Text>
        </View>
        <Bar value={water} goal={waterGoal} color={c.water} />
        <View style={{ flexDirection: 'row', gap: 8, marginTop: 12 }}>
          <Btn title="− 250" kind="ghost" onPress={() => onWater(-250)} disabled={water <= 0} />
          <Btn title="+ 250 ml" kind="ghost" onPress={() => onWater(250)} />
          <Btn title="+ 500 ml" kind="ghost" onPress={() => onWater(500)} />
        </View>
      </View>
    </ScrollView>
  );
}

// ---------- Woche ----------

export function WeekScreen({
  entries, goalsFor, onOpenDay,
}: { entries: Entry[]; goalsFor: (date: string) => Goals; onOpenDay: (d: string) => void }) {
  const today = toDateKey(new Date());
  const [ref, setRef] = useState(today);
  const w = weekStats(entries, ref);
  const dayGoals = w.days.map((d) => goalsFor(d.date));
  const logged = w.days.map((d, i) => ({ ...d, goal: dayGoals[i] })).filter((d) => d.totals.kcal > 0);
  // Ziel-Schnitt über dieselben Tage wie der Ist-Schnitt, sonst verzerren Trainingstage den Vergleich
  const goalBase = logged.length ? logged.map((d) => d.goal) : dayGoals;
  const avgGoal = (k: keyof Goals) => Math.round(goalBase.reduce((a, g) => a + g[k], 0) / goalBase.length);
  const balance = logged.reduce((a, d) => a + d.totals.kcal - d.goal.kcal, 0);
  const max = Math.max(...dayGoals.map((g) => g.kcal * 1.25), ...w.days.map((d) => d.totals.kcal), 1);
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
        <Text style={s.label}>Energie pro Tag, Strich = Tagesziel. Tippen öffnet den Tag.</Text>
        <View style={{ height: BAR_H, flexDirection: 'row', alignItems: 'flex-end', marginTop: 14 }}>
          {w.days.map((d, i) => {
            const h = (d.totals.kcal / max) * BAR_H;
            const g = dayGoals[i].kcal;
            const over = d.totals.kcal > g;
            return (
              <Pressable key={d.date} onPress={() => onOpenDay(d.date)} style={{ flex: 1, alignItems: 'center', justifyContent: 'flex-end', height: '100%' }}>
                <View style={{ position: 'absolute', bottom: (g / max) * BAR_H, width: '80%', height: 2, backgroundColor: c.muted }} />
                <View style={{ width: '56%', height: Math.max(h, d.totals.kcal > 0 ? 3 : 0), backgroundColor: over ? c.over : c.accent, borderRadius: 4 }} />
              </Pressable>
            );
          })}
        </View>
        <View style={{ flexDirection: 'row', marginTop: 6 }}>
          {w.days.map((d) => (
            <View key={d.date} style={{ flex: 1, alignItems: 'center' }}>
              <Text style={[s.label, d.date === today && { color: c.text, fontWeight: '700' }]}>{weekdayShort(d.date)}</Text>
              <Text style={[s.label, { fontSize: 11 }]}>{d.totals.kcal ? Math.round(d.totals.kcal) : '·'}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={s.card}>
        <Text style={s.h2}>Schnitt pro erfasstem Tag</Text>
        <Text style={s.label}>{w.loggedDays} von 7 Tagen erfasst</Text>
        {w.loggedDays > 0 ? (
          <>
            <MacroLine label="Energie" value={w.avg.kcal} goal={avgGoal('kcal')} unit="kcal" color={c.accent} />
            <MacroLine label="Protein" value={w.avg.protein} goal={avgGoal('protein')} unit="g" color={c.protein} min />
            <MacroLine label="Kohlenhydrate" value={w.avg.carbs} goal={avgGoal('carbs')} unit="g" color={c.carbs} />
            <MacroLine label="Fett" value={w.avg.fat} goal={avgGoal('fat')} unit="g" color={c.fat} />
            <View style={[s.row, { marginTop: 14 }]}>
              <Text style={s.label}>Bilanz zum Ziel (erfasste Tage)</Text>
              <Text style={[s.text, { fontWeight: '700', color: balance > 0 ? c.over : c.accent }]}>
                {balance > 0 ? '+' : ''}{Math.round(balance)} kcal
              </Text>
            </View>
          </>
        ) : (
          <Text style={[s.text, { marginTop: 10, color: c.muted }]}>Noch keine Einträge in dieser Woche.</Text>
        )}
      </View>
    </ScrollView>
  );
}

function MicroStat({ label, v, ref_, good, bad }: { label: string; v: number; ref_?: string; good?: boolean; bad?: boolean }) {
  return (
    <View style={{ alignItems: 'center', flex: 1 }}>
      <Text style={[s.text, { fontWeight: '600', color: bad ? c.over : good ? c.accent : c.text }]}>
        {String(Math.round(v * 10) / 10).replace('.', ',')} g
      </Text>
      <Text style={[s.label, { fontSize: 11 }]}>{label}{ref_ ? ` (${ref_})` : ''}</Text>
    </View>
  );
}
