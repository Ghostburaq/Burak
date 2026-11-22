import { useEffect, useMemo, useState } from 'react';
import { Platform, ScrollView, Share, Text, View } from 'react-native';
import { BLV_SOURCE } from './foods';
import { parseNum } from './logic';
import { calculate, PAL_LEVELS, type GoalType, type Profile, type Sex } from './nutrition';
import { c } from './theme';
import { Btn, Chip, KV, NumField, s, Segmented, TextField } from './ui';

type Draft = Record<
  'birthYear' | 'heightCm' | 'weightKg' | 'proteinPerKg' | 'fatPct' | 'trainingBonus' | 'waterMl' | 'mKcal' | 'mProtein' | 'mCarbs' | 'mFat',
  string
>;

const toStr = (n: number | null) => (n === null ? '' : String(n).replace('.', ','));

function draftFrom(p: Profile): Draft {
  return {
    birthYear: toStr(p.birthYear), heightCm: toStr(p.heightCm), weightKg: toStr(p.weightKg),
    proteinPerKg: toStr(p.proteinPerKg), fatPct: toStr(p.fatPct), trainingBonus: toStr(p.trainingBonus),
    waterMl: toStr(p.waterMl), mKcal: toStr(p.manual.kcal), mProtein: toStr(p.manual.protein),
    mCarbs: toStr(p.manual.carbs), mFat: toStr(p.manual.fat),
  };
}

const RATES = [0.25, 0.5, 0.75, 1];

export function ProfileScreen({
  profile, trendWeight, onSave, exportText, onImport,
}: {
  profile: Profile;
  trendWeight: number | null;
  onSave: (p: Profile) => void;
  exportText: () => string;
  onImport: (text: string) => string | null; // Fehlermeldung oder null
}) {
  const [sex, setSex] = useState<Sex>(profile.sex);
  const [goal, setGoal] = useState<GoalType>(profile.goal);
  const [pal, setPal] = useState(profile.pal);
  const [rate, setRate] = useState(profile.ratePerWeek);
  const [mode, setMode] = useState(profile.mode);
  const [d, setD] = useState<Draft>(draftFrom(profile));
  const [saved, setSaved] = useState(false);
  const [importText, setImportText] = useState('');
  const [importMsg, setImportMsg] = useState('');
  const [confirmImport, setConfirmImport] = useState(false);

  useEffect(() => {
    setSex(profile.sex); setGoal(profile.goal); setPal(profile.pal); setRate(profile.ratePerWeek);
    setMode(profile.mode); setD(draftFrom(profile));
  }, [profile]);

  const set = (k: keyof Draft) => (v: string) => { setD((x) => ({ ...x, [k]: v })); setSaved(false); };
  const touch = <T,>(fn: (v: T) => void) => (v: T) => { fn(v); setSaved(false); };

  const num = (k: keyof Draft) => parseNum(d[k]);
  const thisYear = new Date().getFullYear();
  const errors: string[] = [];
  const by = num('birthYear'), h = num('heightCm'), w = num('weightKg');
  if (mode === 'auto') {
    if (!by || by < thisYear - 100 || by > thisYear - 14) errors.push('Geburtsjahr prüfen');
    if (!h || h < 120 || h > 230) errors.push('Grösse in cm prüfen');
    if (!w || w < 30 || w > 300) errors.push('Gewicht in kg prüfen');
    if (num('proteinPerKg') === null || num('proteinPerKg')! > 4) errors.push('Protein g/kg prüfen');
    const fp = num('fatPct');
    if (fp === null || fp < 10 || fp > 60) errors.push('Fettanteil 10 bis 60 %');
  } else if (!num('mKcal')) errors.push('Kalorienziel fehlt');

  const candidate: Profile = useMemo(() => ({
    ...profile,
    configured: true,
    sex, goal, pal, ratePerWeek: rate, mode,
    birthYear: by ?? profile.birthYear,
    heightCm: h ?? profile.heightCm,
    weightKg: w ?? profile.weightKg,
    proteinPerKg: num('proteinPerKg') ?? profile.proteinPerKg,
    fatPct: num('fatPct') ?? profile.fatPct,
    trainingBonus: num('trainingBonus') ?? 0,
    waterMl: num('waterMl'),
    manual: {
      kcal: num('mKcal') ?? profile.manual.kcal,
      protein: num('mProtein') ?? 0,
      carbs: num('mCarbs') ?? 0,
      fat: num('mFat') ?? 0,
    },
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }), [d, sex, goal, pal, rate, mode, profile]);

  const calc = calculate(candidate, trendWeight);

  const doExport = async () => {
    const text = exportText();
    const name = `kalorien-backup-${new Date().toISOString().slice(0, 10)}.json`;
    if (Platform.OS === 'web') {
      const blob = new Blob([text], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = name;
      a.click();
      URL.revokeObjectURL(a.href);
    } else {
      await Share.share({ message: text, title: name });
    }
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 40 }} keyboardShouldPersistTaps="handled">
      <Text style={[s.h1, { marginBottom: 14 }]}>Profil & Ziele</Text>

      <Segmented
        options={[{ key: 'auto', label: 'Berechnen' }, { key: 'manual', label: 'Manuell' }]}
        value={mode}
        onChange={touch(setMode)}
      />
      <View style={{ height: 12 }} />

      {mode === 'auto' ? (
        <>
          <Text style={s.section}>Körper</Text>
          <View style={s.card}>
            <Segmented options={[{ key: 'm', label: 'Mann' }, { key: 'w', label: 'Frau' }]} value={sex} onChange={touch(setSex)} />
            <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
              <NumField label="Geburtsjahr" value={d.birthYear} onChange={set('birthYear')} />
              <NumField label="Grösse" value={d.heightCm} onChange={set('heightCm')} suffix="cm" />
              <NumField label="Gewicht" value={d.weightKg} onChange={set('weightKg')} suffix="kg" />
            </View>
            {trendWeight !== null && (
              <Text style={[s.label, { marginTop: 8 }]}>
                Gerechnet wird mit deinem Trendgewicht {trendWeight.toFixed(1).replace('.', ',')} kg aus dem Gewichtsverlauf.
              </Text>
            )}
          </View>

          <Text style={s.section}>Alltag & Training</Text>
          <View style={s.card}>
            {PAL_LEVELS.map((l) => (
              <Chip wide key={l.value} active={pal === l.value} onPress={() => touch(setPal)(l.value)} title={`${l.label} · ${l.hint}`} />
            ))}
            <Text style={s.label}>Faktor {pal.toString().replace('.', ',')} auf den Grundumsatz. Im Zweifel eine Stufe tiefer, die meisten überschätzen sich.</Text>
          </View>

          <Text style={s.section}>Ziel</Text>
          <View style={s.card}>
            <Segmented
              options={[{ key: 'lose', label: 'Abnehmen' }, { key: 'maintain', label: 'Halten' }, { key: 'gain', label: 'Aufbauen' }]}
              value={goal}
              onChange={touch(setGoal)}
            />
            {goal !== 'maintain' && (
              <>
                <Text style={[s.fieldLabel, { marginTop: 12 }]}>Tempo pro Woche</Text>
                <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
                  {RATES.map((r) => (
                    <Chip key={r} title={`${r.toString().replace('.', ',')} kg`} active={rate === r} onPress={() => touch(setRate)(r)} />
                  ))}
                </View>
              </>
            )}
          </View>

          <Text style={s.section}>Makros</Text>
          <View style={s.card}>
            <View style={{ flexDirection: 'row', gap: 10 }}>
              <NumField label="Protein" value={d.proteinPerKg} onChange={set('proteinPerKg')} suffix="g/kg" />
              <NumField label="Fett" value={d.fatPct} onChange={set('fatPct')} suffix="% kcal" />
            </View>
            <Text style={[s.label, { marginTop: 8 }]}>
              Kohlenhydrate füllen den Rest. Protein im Kraftsport üblich 1,6 bis 2,2 g/kg, in der Diät eher oben.
            </Text>
          </View>
        </>
      ) : (
        <>
          <Text style={s.section}>Feste Ziele</Text>
          <View style={s.card}>
            <NumField label="Energie" value={d.mKcal} onChange={set('mKcal')} suffix="kcal" />
            <View style={{ flexDirection: 'row', gap: 10, marginTop: 12 }}>
              <NumField label="Protein" value={d.mProtein} onChange={set('mProtein')} suffix="g" />
              <NumField label="KH" value={d.mCarbs} onChange={set('mCarbs')} suffix="g" />
              <NumField label="Fett" value={d.mFat} onChange={set('mFat')} suffix="g" />
            </View>
          </View>
        </>
      )}

      <Text style={s.section}>Trainingstage & Wasser</Text>
      <View style={s.card}>
        <View style={{ flexDirection: 'row', gap: 10 }}>
          <NumField label="Zuschlag Trainingstag" value={d.trainingBonus} onChange={set('trainingBonus')} suffix="kcal" placeholder="0" />
          <NumField label="Wasserziel" value={d.waterMl} onChange={set('waterMl')} suffix="ml" placeholder={String(calc.waterMl)} />
        </View>
        <Text style={[s.label, { marginTop: 8 }]}>
          Zuschlag geht komplett auf Kohlenhydrate. Trainingstag markierst du in der Tagesansicht. Wasser leer = Faustregel 35 ml pro kg.
        </Text>
      </View>

      <Text style={s.section}>Ergebnis</Text>
      <View style={[s.card, { borderColor: c.accent }]}>
        {mode === 'auto' && (
          <>
            <KV k="Grundumsatz (Mifflin-St Jeor)" v={`${Math.round(calc.bmr)} kcal`} />
            <KV k={`Gesamtumsatz (${calc.tdeeSource === 'adaptiv' ? 'aus deinen Daten' : `× ${pal.toString().replace('.', ',')}`})`} v={`${Math.round(calc.tdee)} kcal`} />
            {goal !== 'maintain' && <KV k={`Ziel ${goal === 'lose' ? 'Defizit' : 'Überschuss'}`} v={`${calc.adjustment > 0 ? '+' : '−'}${Math.abs(Math.round(calc.adjustment))} kcal`} />}
          </>
        )}
        <KV k="Ruhetag" v={`${calc.base.kcal} kcal`} strong />
        <Text style={s.label}>P {Math.round(calc.base.protein)} g · KH {Math.round(calc.base.carbs)} g · F {Math.round(calc.base.fat)} g</Text>
        {calc.training.kcal !== calc.base.kcal && (
          <>
            <KV k="Trainingstag" v={`${calc.training.kcal} kcal`} strong />
            <Text style={s.label}>P {Math.round(calc.training.protein)} g · KH {Math.round(calc.training.carbs)} g · F {Math.round(calc.training.fat)} g</Text>
          </>
        )}
        {calc.warnings.map((wn) => (
          <Text key={wn} style={[s.label, { color: c.warn, marginTop: 8 }]}>{wn}</Text>
        ))}
        {errors.length > 0 && <Text style={[s.label, { color: c.over, marginTop: 8 }]}>{errors.join(' · ')}</Text>}
      </View>

      <View style={{ flexDirection: 'row' }}>
        <Btn
          title={saved ? 'Gespeichert' : 'Speichern'}
          disabled={errors.length > 0}
          onPress={() => { onSave(candidate); setSaved(true); }}
        />
      </View>

      <Text style={[s.section, { marginTop: 24 }]}>Backup</Text>
      <View style={s.card}>
        <Text style={[s.label, { marginBottom: 10 }]}>
          Alle Daten liegen nur auf diesem Gerät. Regelmässig exportieren, damit nichts verloren geht.
        </Text>
        <View style={{ flexDirection: 'row' }}>
          <Btn title="Daten exportieren (JSON)" kind="ghost" onPress={doExport} />
        </View>
        <View style={{ height: 14 }} />
        <TextField label="Backup einfügen" value={importText} onChange={(v) => { setImportText(v); setConfirmImport(false); setImportMsg(''); }} multiline placeholder='{"app":"kalorien", ...}' />
        <View style={{ flexDirection: 'row', marginTop: 10 }}>
          <Btn
            title={confirmImport ? 'Wirklich alles ersetzen?' : 'Importieren'}
            kind={confirmImport ? 'danger' : 'ghost'}
            disabled={!importText.trim()}
            onPress={() => {
              if (!confirmImport) { setConfirmImport(true); return; }
              const err = onImport(importText);
              setImportMsg(err ?? 'Import erfolgreich.');
              setConfirmImport(false);
              if (!err) setImportText('');
            }}
          />
        </View>
        {importMsg ? <Text style={[s.label, { marginTop: 8 }]}>{importMsg}</Text> : null}
      </View>

      <Text style={[s.label, { marginTop: 8 }]}>
        Rechenbasis: Mifflin-St Jeor (1990), 7700 kcal pro kg als Näherung, 4/4/9 kcal pro g Protein/KH/Fett.{'\n\n'}Lebensmitteldaten: {BLV_SOURCE}. Markenprodukte: Open Food Facts (openfoodfacts.org), Lizenz ODbL.
      </Text>
    </ScrollView>
  );
}
