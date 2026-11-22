import { CameraView, useCameraPermissions } from 'expo-camera';
import { useRef, useState } from 'react';
import { ActivityIndicator, Platform, Text, View } from 'react-native';
import { lookupBarcode, type Food } from '../foods';
import { c } from '../theme';
import { Btn, NumField, s } from '../ui';

/** Barcode scannen oder eintippen, dann bei Open Food Facts nachschlagen. Lokale Produkte zuerst. */
export function Scanner({
  localByBarcode, onFound, onNotFound,
}: {
  localByBarcode: (code: string) => Food | undefined;
  onFound: (f: Food) => void;
  onNotFound: (code: string) => void;
}) {
  const [perm, requestPerm] = useCameraPermissions();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [manual, setManual] = useState('');
  const lock = useRef(false);
  const native = Platform.OS !== 'web';

  const handle = async (raw: string) => {
    const code = raw.replace(/\D/g, '');
    if (lock.current || code.length < 8) return;
    lock.current = true;
    setBusy(true); setMsg('');
    const local = localByBarcode(code);
    if (local) { onFound(local); return; }
    const r = await lookupBarcode(code);
    setBusy(false);
    if (r.ok) { onFound(r.food); return; }
    if (r.reason === 'offline') {
      setMsg('Keine Verbindung zu Open Food Facts. Später erneut versuchen.');
      lock.current = false;
      return;
    }
    setMsg(r.reason === 'no_nutrition' ? `Produkt ${code} gefunden, aber ohne Nährwerte.` : `Produkt ${code} nicht in der Datenbank.`);
    onNotFound(code);
  };

  return (
    <View>
      {native ? (
        !perm ? (
          <ActivityIndicator color={c.accent} />
        ) : !perm.granted ? (
          <View style={s.card}>
            <Text style={s.h2}>Kamera für Barcodes</Text>
            <Text style={[s.label, { marginVertical: 8 }]}>Die Kamera wird nur zum Lesen des Strichcodes genutzt, es werden keine Bilder gespeichert.</Text>
            <View style={{ flexDirection: 'row' }}>
              <Btn title="Kamera erlauben" onPress={requestPerm} />
            </View>
          </View>
        ) : (
          <View style={{ height: 300, borderRadius: 16, overflow: 'hidden', marginBottom: 12, backgroundColor: '#000' }}>
            <CameraView
              style={{ flex: 1 }}
              facing="back"
              barcodeScannerSettings={{ barcodeTypes: ['ean13', 'ean8', 'upc_a', 'upc_e'] }}
              onBarcodeScanned={busy ? undefined : (r) => handle(r.data)}
            />
            <View pointerEvents="none" style={{ position: 'absolute', left: '12%', right: '12%', top: '38%', height: '24%', borderWidth: 2, borderColor: c.accent, borderRadius: 12 }} />
          </View>
        )
      ) : (
        <View style={s.card}>
          <Text style={s.h2}>Scanner nur in der App</Text>
          <Text style={[s.label, { marginTop: 6 }]}>Im Browser kannst du die Nummer unter dem Strichcode eintippen.</Text>
        </View>
      )}

      {busy && <ActivityIndicator color={c.accent} style={{ marginVertical: 10 }} />}
      {msg ? <Text style={[s.label, { color: c.warn, marginBottom: 10 }]}>{msg}</Text> : null}

      <View style={s.card}>
        <View style={{ flexDirection: 'row', gap: 10, alignItems: 'flex-end' }}>
          <NumField label="Barcode eintippen (EAN)" value={manual} onChange={setManual} placeholder="7610..." />
          <View style={{ width: 110, flexDirection: 'row' }}>
            <Btn title="Suchen" disabled={manual.replace(/\D/g, '').length < 8 || busy} onPress={() => { lock.current = false; handle(manual); }} />
          </View>
        </View>
      </View>
      {lock.current && !busy && (
        <View style={{ flexDirection: 'row' }}>
          <Btn title="Nochmals scannen" kind="ghost" onPress={() => { lock.current = false; setMsg(''); setManual(''); }} />
        </View>
      )}
      <Text style={[s.label, { marginTop: 10 }]}>Produktdaten: Open Food Facts, offene Datenbank (ODbL).</Text>
    </View>
  );
}
