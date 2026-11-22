import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { c, radius } from './theme';

export function Bar({ value, goal, color }: { value: number; goal: number; color: string }) {
  const pct = goal > 0 ? Math.min(value / goal, 1) : 0;
  const over = goal > 0 && value > goal;
  return (
    <View style={s.barTrack}>
      <View style={[s.barFill, { width: `${pct * 100}%`, backgroundColor: over ? c.over : color }]} />
    </View>
  );
}

export function MacroLine({
  label, value, goal, unit, color,
}: { label: string; value: number; goal: number; unit: string; color: string }) {
  return (
    <View style={{ marginTop: 10 }}>
      <View style={s.row}>
        <Text style={s.label}>{label}</Text>
        <Text style={s.label}>
          <Text style={{ color: c.text }}>{Math.round(value)}</Text> / {goal} {unit}
        </Text>
      </View>
      <Bar value={value} goal={goal} color={color} />
    </View>
  );
}

export function NumField({
  label, value, onChange, placeholder, suffix,
}: { label: string; value: string; onChange: (v: string) => void; placeholder?: string; suffix?: string }) {
  return (
    <View style={{ flex: 1 }}>
      <Text style={s.fieldLabel}>{label}</Text>
      <View style={s.inputWrap}>
        <TextInput
          style={s.input}
          value={value}
          onChangeText={onChange}
          keyboardType="decimal-pad"
          placeholder={placeholder}
          placeholderTextColor={c.muted}
          selectTextOnFocus
        />
        {suffix ? <Text style={s.suffix}>{suffix}</Text> : null}
      </View>
    </View>
  );
}

export function Btn({
  title, onPress, kind = 'primary', disabled,
}: { title: string; onPress: () => void; kind?: 'primary' | 'ghost' | 'danger'; disabled?: boolean }) {
  const bg = kind === 'primary' ? c.accent : 'transparent';
  const fg = kind === 'primary' ? '#0b0d10' : kind === 'danger' ? c.over : c.text;
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        s.btn,
        { backgroundColor: bg, opacity: disabled ? 0.4 : pressed ? 0.7 : 1 },
        kind !== 'primary' && { borderWidth: 1, borderColor: kind === 'danger' ? c.over : c.border },
      ]}
    >
      <Text style={[s.btnText, { color: fg }]}>{title}</Text>
    </Pressable>
  );
}

export function Chip({ title, active, onPress }: { title: string; active?: boolean; onPress: () => void }) {
  return (
    <Pressable onPress={onPress} style={[s.chip, active && { backgroundColor: c.accent, borderColor: c.accent }]}>
      <Text style={[s.chipText, active && { color: '#0b0d10' }]} numberOfLines={1}>
        {title}
      </Text>
    </Pressable>
  );
}

export const s = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  card: { backgroundColor: c.card, borderRadius: radius, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: c.border },
  h1: { color: c.text, fontSize: 22, fontWeight: '700' },
  h2: { color: c.text, fontSize: 16, fontWeight: '600' },
  label: { color: c.muted, fontSize: 13 },
  text: { color: c.text, fontSize: 15 },
  barTrack: { height: 8, backgroundColor: c.cardAlt, borderRadius: 4, overflow: 'hidden', marginTop: 6 },
  barFill: { height: 8, borderRadius: 4 },
  fieldLabel: { color: c.muted, fontSize: 12, marginBottom: 4 },
  inputWrap: { flexDirection: 'row', alignItems: 'center', backgroundColor: c.cardAlt, borderRadius: 10, borderWidth: 1, borderColor: c.border },
  input: { flex: 1, color: c.text, fontSize: 16, paddingHorizontal: 12, paddingVertical: 10, minWidth: 0 },
  suffix: { color: c.muted, paddingRight: 10, fontSize: 13 },
  btn: { borderRadius: 12, paddingVertical: 13, paddingHorizontal: 16, alignItems: 'center', flex: 1 },
  btnText: { fontSize: 15, fontWeight: '600' },
  chip: { borderWidth: 1, borderColor: c.border, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 7, marginRight: 8, marginBottom: 8, maxWidth: 200 },
  chipText: { color: c.text, fontSize: 13 },
});
