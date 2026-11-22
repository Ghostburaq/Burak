import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { c, radius } from './theme';

/** `min`: Mindestziel (z.B. Protein), darüber ist gut. Sonst Obergrenze, rot erst ab 5 % darüber. */
export function Bar({ value, goal, color, min }: { value: number; goal: number; color: string; min?: boolean }) {
  const pct = goal > 0 ? Math.min(value / goal, 1) : 0;
  const over = !min && goal > 0 && value > goal * 1.05;
  return (
    <View style={s.barTrack}>
      <View style={[s.barFill, { width: `${pct * 100}%`, backgroundColor: over ? c.over : color }]} />
    </View>
  );
}

export function MacroLine({
  label, value, goal, unit, color, min,
}: { label: string; value: number; goal: number; unit: string; color: string; min?: boolean }) {
  return (
    <View style={{ marginTop: 10 }}>
      <View style={s.row}>
        <Text style={s.label}>{label}</Text>
        <Text style={s.label}>
          <Text style={{ color: c.text }}>{Math.round(value)}</Text> / {goal} {unit}
        </Text>
      </View>
      <Bar value={value} goal={goal} color={color} min={min} />
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

export function Chip({ title, active, onPress, wide }: { title: string; active?: boolean; onPress: () => void; wide?: boolean }) {
  return (
    <Pressable onPress={onPress} style={[s.chip, wide && { maxWidth: '100%', alignSelf: 'flex-start' }, active && { backgroundColor: c.accent, borderColor: c.accent }]}>
      <Text style={[s.chipText, active && { color: '#0b0d10' }]} numberOfLines={1}>
        {title}
      </Text>
    </Pressable>
  );
}

export function Segmented<T extends string>({
  options, value, onChange,
}: { options: { key: T; label: string }[]; value: T; onChange: (v: T) => void }) {
  return (
    <View style={s.seg}>
      {options.map((o) => (
        <Pressable key={o.key} onPress={() => onChange(o.key)} style={[s.segItem, value === o.key && s.segActive]}>
          <Text style={[s.segText, value === o.key && { color: '#0b0d10', fontWeight: '700' }]}>{o.label}</Text>
        </Pressable>
      ))}
    </View>
  );
}

export function TextField({
  label, value, onChange, placeholder, multiline,
}: { label?: string; value: string; onChange: (v: string) => void; placeholder?: string; multiline?: boolean }) {
  return (
    <View>
      {label ? <Text style={s.fieldLabel}>{label}</Text> : null}
      <View style={s.inputWrap}>
        <TextInput
          style={[s.input, multiline && { minHeight: 90, textAlignVertical: 'top' }]}
          value={value}
          onChangeText={onChange}
          placeholder={placeholder}
          placeholderTextColor={c.muted}
          multiline={multiline}
        />
      </View>
    </View>
  );
}

export function KV({ k, v, strong }: { k: string; v: string; strong?: boolean }) {
  return (
    <View style={[s.row, { paddingVertical: 5 }]}>
      <Text style={s.label}>{k}</Text>
      <Text style={[s.text, strong && { fontWeight: '700', color: c.accent }]}>{v}</Text>
    </View>
  );
}

export const s = StyleSheet.create({
  seg: { flexDirection: 'row', backgroundColor: c.cardAlt, borderRadius: 10, padding: 3, borderWidth: 1, borderColor: c.border },
  segItem: { flex: 1, paddingVertical: 8, alignItems: 'center', borderRadius: 8 },
  segActive: { backgroundColor: c.accent },
  segText: { color: c.text, fontSize: 14 },
  section: { color: c.muted, fontSize: 12, fontWeight: '700', letterSpacing: 0.8, textTransform: 'uppercase', marginBottom: 8, marginTop: 6 },
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
