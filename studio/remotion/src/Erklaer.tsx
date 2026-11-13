import {
  AbsoluteFill,
  Audio,
  Composition,
  Loop,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { GESAMT, PLAN } from "./erklaer-zeitplan";

// NEXA-Erklärvideo. Zeitplan und Texte kommen aus studio/erklaer/bauen.py.
// Ton: public/erklaer/ton.wav (Stimme + geduckte Musik).

const FPS = 30;
const GELB = "#f5c400";
const ORANGE = "#ff9a2e";
const ROT = "#ff5a3c";
const GRUND = "#0b0f14";
const GRAU = "#6b7684";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const font = "Inter, sans-serif";

const useSpring = (delay = 0, damping = 14) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping } });
};

// Welle: Grundschwingung + 5. + 7. Harmonische
const Welle: React.FC<{
  a5: number;
  a7: number;
  farbe: string;
  breite?: number;
  hoehe?: number;
  zeichnen?: number;
  freq?: number;
  dicke?: number;
}> = ({ a5, a7, farbe, breite = 900, hoehe = 420, zeichnen = 1, freq = 1, dicke = 9 }) => {
  const frame = useCurrentFrame();
  const n = 400;
  const pts: string[] = [];
  for (let i = 0; i <= n; i++) {
    const x = (i / n) * 4 * Math.PI;
    const ph = frame * 0.06;
    const y = Math.sin(freq * x - ph) + a5 * Math.sin(5 * x - 5 * ph) + a7 * Math.sin(7 * x - 7 * ph);
    pts.push(`${(i / n) * breite},${hoehe / 2 - (y * hoehe) / 3.4}`);
  }
  const d = `M${pts.join(" L")}`;
  return (
    <svg width={breite} height={hoehe} style={{ overflow: "visible" }}>
      <line x1={0} y1={hoehe / 2} x2={breite} y2={hoehe / 2} stroke={GRAU} strokeWidth={2} strokeDasharray="8 10" />
      <path
        d={d}
        fill="none"
        stroke={farbe}
        strokeWidth={dicke}
        strokeLinejoin="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - zeichnen}
        style={{ filter: `drop-shadow(0 0 14px ${farbe}88)` }}
      />
    </svg>
  );
};

const Chip: React.FC<{ text: string; delay: number; farbe?: string }> = ({ text, delay, farbe = GELB }) => {
  const s = useSpring(delay, 12);
  return (
    <div
      style={{
        fontFamily: font,
        fontWeight: 800,
        fontSize: 54,
        color: GRUND,
        background: farbe,
        padding: "18px 36px",
        borderRadius: 999,
        transform: `scale(${s}) translateY(${(1 - s) * 40}px)`,
        opacity: s,
      }}
    >
      {text}
    </div>
  );
};

const Mitte: React.FC<{ children: React.ReactNode; top?: number }> = ({ children, top = 330 }) => (
  <div
    style={{
      position: "absolute",
      top,
      left: 0,
      right: 0,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 40,
    }}
  >
    {children}
  </div>
);

const Label: React.FC<{ text: string; farbe?: string; size?: number }> = ({ text, farbe = "white", size = 64 }) => (
  <div style={{ fontFamily: font, fontWeight: 800, fontSize: size, color: farbe, textAlign: "center" }}>{text}</div>
);

// ---------------------------------------------------------------- Szenen
const Sauber: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Mitte>
      <Label text="Sauberer Sinus" />
      <Welle a5={0} a7={0} farbe={GELB} zeichnen={interpolate(frame, [0, 40], [0, 1], clamp)} />
      <Label text="50 Hz" farbe={GELB} size={56} />
    </Mitte>
  );
};

const Lasten: React.FC = () => {
  const frame = useCurrentFrame();
  const k = interpolate(frame, [20, 120], [0, 1], clamp);
  return (
    <Mitte>
      <Welle a5={0.25 * k} a7={0.15 * k} farbe={k > 0.5 ? ORANGE : GELB} />
      <div style={{ display: "flex", flexWrap: "wrap", gap: 24, justifyContent: "center", padding: "0 60px" }}>
        <Chip text="Frequenz-Umrichter" delay={5} />
        <Chip text="Netzteile" delay={35} />
        <Chip text="LED-Treiber" delay={65} />
      </div>
    </Mitte>
  );
};

const Harmonische: React.FC = () => {
  const s1 = useSpring(10);
  const s2 = useSpring(45);
  const s3 = useSpring(80);
  const zeile = (s: number, label: string, farbe: string, freq: number, amp: number) => (
    <div style={{ display: "flex", alignItems: "center", gap: 30, opacity: s, transform: `translateX(${(1 - s) * -80}px)` }}>
      <div style={{ width: 230, fontFamily: font, fontWeight: 800, fontSize: 52, color: farbe, textAlign: "right" }}>{label}</div>
      <svg width={640} height={150}>
        <Welle a5={0} a7={0} farbe={farbe} breite={640} hoehe={150 * amp} freq={freq} dicke={6} />
      </svg>
    </div>
  );
  return (
    <Mitte top={300}>
      <Welle a5={0.25} a7={0.15} farbe={ROT} breite={900} hoehe={360} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {zeile(s1, "50 Hz", GELB, 1, 1)}
        {zeile(s2, "250 Hz", ORANGE, 5, 0.55)}
        {zeile(s3, "350 Hz", ROT, 7, 0.4)}
      </div>
    </Mitte>
  );
};

const Karte: React.FC<{ titel: string; icon: React.ReactNode; delay: number }> = ({ titel, icon, delay }) => {
  const s = useSpring(delay, 13);
  return (
    <div
      style={{
        width: 860,
        display: "flex",
        alignItems: "center",
        gap: 40,
        padding: "34px 44px",
        background: "#151b22",
        border: `4px solid ${ROT}`,
        borderRadius: 28,
        opacity: s,
        transform: `translateX(${(1 - s) * 120}px)`,
      }}
    >
      <svg width={110} height={110} viewBox="0 0 100 100">
        {icon}
      </svg>
      <div style={{ fontFamily: font, fontWeight: 800, fontSize: 58, color: "white" }}>{titel}</div>
    </div>
  );
};

const Folgen: React.FC = () => (
  <Mitte top={360}>
    <Karte
      titel="Erwärmung"
      delay={20}
      icon={
        <g fill="none" stroke={ROT} strokeWidth={7} strokeLinecap="round">
          <rect x={40} y={8} width={20} height={58} rx={10} />
          <circle cx={50} cy={78} r={15} fill={ROT} />
          <line x1={50} y1={30} x2={50} y2={70} />
        </g>
      }
    />
    <Karte
      titel="Fehlauslösungen"
      delay={55}
      icon={<polygon points="58,5 22,55 46,55 38,95 78,40 54,40" fill={ROT} />}
    />
    <Karte
      titel="Resonanzen"
      delay={95}
      icon={
        <path d="M5 85 C 30 85, 38 80, 45 40 S 50 5, 55 40 S 70 85, 95 85" fill="none" stroke={ROT} strokeWidth={7} strokeLinecap="round" />
      }
    />
  </Mitte>
);

const Norm: React.FC = () => {
  const frame = useCurrentFrame();
  const s = useSpring(10);
  const max = 12;
  const breite = 860;
  const xGrenze = (8 / max) * breite;
  const zeiger = interpolate(Math.sin(frame / 9), [-1, 1], [2, 11]);
  return (
    <Mitte top={380}>
      <Label text="EN 50160" farbe={GELB} size={96} />
      <Label text="Gesamtverzerrung der Spannung (THDu)" size={44} />
      <div style={{ position: "relative", width: breite, height: 260, marginTop: 30, opacity: s }}>
        <div style={{ position: "absolute", top: 90, width: xGrenze, height: 70, background: "#1e3a24", borderRadius: "16px 0 0 16px" }} />
        <div style={{ position: "absolute", top: 90, left: xGrenze, width: breite - xGrenze, height: 70, background: "#4a1a14", borderRadius: "0 16px 16px 0" }} />
        <div style={{ position: "absolute", top: 60, left: xGrenze - 4, width: 8, height: 130, background: GELB }} />
        <div style={{ position: "absolute", top: 0, left: xGrenze - 150, width: 300, textAlign: "center", fontFamily: font, fontWeight: 800, fontSize: 46, color: GELB }}>
          max. 8 %
        </div>
        {[0, 4, 8, 12].map((v) => (
          <div
            key={v}
            style={{ position: "absolute", top: 200, left: (v / max) * breite - 60, width: 120, textAlign: "center", fontFamily: font, fontSize: 36, color: GRAU }}
          >
            {v} %
          </div>
        ))}
        <div
          style={{
            position: "absolute",
            top: 72,
            left: (zeiger / max) * breite - 26,
            width: 52,
            height: 106,
            borderRadius: 12,
            background: "white",
            display: "grid",
            placeItems: "center",
            fontFamily: font,
            fontWeight: 900,
            fontSize: 48,
            color: GRUND,
          }}
        >
          ?
        </div>
      </div>
      <Label text="Wo liegst du?" size={60} />
    </Mitte>
  );
};

const Messen: React.FC = () => {
  const frame = useCurrentFrame();
  const puls = 0.5 + 0.5 * Math.sin(frame / 6);
  const tage = Math.min(7, Math.floor(interpolate(frame, [20, 170], [0, 7.99], clamp)));
  return (
    <Mitte top={360}>
      <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <div style={{ width: 44, height: 44, borderRadius: "50%", background: ROT, opacity: 0.4 + 0.6 * puls }} />
        <Label text="Messung läuft" size={70} />
      </div>
      <Label text="IEC 61000-4-30" farbe={GELB} size={92} />
      <Label text="Klasse A" farbe={GELB} size={70} />
      <div style={{ display: "flex", gap: 16, marginTop: 30 }}>
        {["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"].map((t, i) => (
          <div
            key={t}
            style={{
              width: 104,
              height: 104,
              borderRadius: 18,
              display: "grid",
              placeItems: "center",
              fontFamily: font,
              fontWeight: 800,
              fontSize: 38,
              background: i < tage ? GELB : "#1a2129",
              color: i < tage ? GRUND : GRAU,
            }}
          >
            {t}
          </div>
        ))}
      </div>
      <Label text="Bewertung über 1 Woche" size={44} farbe={GRAU} />
    </Mitte>
  );
};

const Ende: React.FC = () => {
  const s = useSpring(0, 11);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "absolute", top: 330, left: 260, width: 560, height: 560 }}>
        <Loop durationInFrames={90}>
          <OffthreadVideo src={staticFile("erklaer/blitz.mp4")} muted style={{ width: "100%", height: "100%", mixBlendMode: "lighten" }} />
        </Loop>
      </div>
      <div style={{ position: "absolute", top: 1000, width: "100%", transform: `scale(${0.7 + 0.3 * s})`, opacity: s }}>
        <Label text="MESSEN" size={150} farbe={GELB} />
        <Label text="STATT RATEN." size={110} />
      </div>
    </AbsoluteFill>
  );
};

const SZENEN: Record<string, React.FC> = {
  sauber: Sauber,
  lasten: Lasten,
  harmonische: Harmonische,
  folgen: Folgen,
  norm: Norm,
  messen: Messen,
  ende: Ende,
};

// Untertitel: Satz blendet ein, Wörter werden der Reihe nach hell
const Untertitel: React.FC<{ text: string; dauer: number }> = ({ text, dauer }) => {
  const frame = useCurrentFrame();
  const woerter = text.split(" ");
  const fortschritt = interpolate(frame, [0, dauer * FPS], [0, woerter.length], clamp);
  const ein = interpolate(frame, [0, 6], [0, 1], clamp);
  return (
    <div
      style={{
        position: "absolute",
        top: 1470,
        left: 60,
        right: 60,
        textAlign: "center",
        fontFamily: font,
        fontWeight: 800,
        fontSize: 54,
        lineHeight: 1.25,
        opacity: ein,
      }}
    >
      {woerter.map((w, i) => (
        <span key={i} style={{ color: i < fortschritt ? "white" : "#5d6773" }}>
          {w}{" "}
        </span>
      ))}
    </div>
  );
};

export const Erklaer: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const fade = interpolate(frame, [0, 12, durationInFrames - 20, durationInFrames], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill style={{ background: GRUND }}>
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(#ffffff08 2px, transparent 2px), linear-gradient(90deg, #ffffff08 2px, transparent 2px)",
          backgroundSize: "60px 60px",
        }}
      />
      <AbsoluteFill style={{ opacity: fade }}>
        <div style={{ position: "absolute", top: 120, width: "100%", textAlign: "center", fontFamily: font, fontWeight: 800, fontSize: 40, letterSpacing: 6, color: GELB }}>
          NEXA · NETZQUALITÄT
        </div>
        {PLAN.map((p, i) => {
          const von = Math.round(p.start * FPS) - (i === 0 ? Math.round(p.start * FPS) : 6);
          const bis = i + 1 < PLAN.length ? Math.round(PLAN[i + 1].start * FPS) - 6 : durationInFrames;
          const Szene = SZENEN[p.szene];
          return (
            <Sequence key={i} from={von} durationInFrames={bis - von}>
              <Szene />
            </Sequence>
          );
        })}
        {PLAN.map((p, i) => (
          <Sequence key={`u${i}`} from={Math.round(p.start * FPS)} durationInFrames={Math.round((p.dauer + 0.4) * FPS)}>
            <Untertitel text={p.text} dauer={p.dauer} />
          </Sequence>
        ))}
      </AbsoluteFill>
      <Audio src={staticFile("erklaer/ton.wav")} />
    </AbsoluteFill>
  );
};

export const ErklaerComp = () => (
  <Composition id="Erklaer" component={Erklaer} durationInFrames={Math.ceil(GESAMT * FPS)} fps={FPS} width={1080} height={1920} />
);
