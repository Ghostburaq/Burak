import "@fontsource/bangers/400.css";
import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// NEXA Personal Training: Promo im Comic-Look.
// Bilder: public/pt/*.jpg (SD-Turbo, hochskaliert), Musik: public/pt/beat.wav (studio/showcase/power_beat.py)
// 100 BPM: 1 Schlag = 18 Frames, 1 Takt = 72 Frames. Drop bei Frame 144.

const FPS = 30;
const SCHLAG = 18;
const TAKT = 72;
const NACHT = "#0c1417";
const PETROL = "#33dcc0";
const ORANGE = "#ff8a2a";
const CREME = "#fff3d6";
const TINTE = "#0a0a0a";
const comic = "Bangers, Impact, sans-serif";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const pt = (p: string) => staticFile(`pt/${p}`);

const useSp = (delay = 0, damping = 12) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping } });
};

// Halbton-Raster über allem
const Raster: React.FC<{ farbe?: string; groesse?: number }> = ({ farbe = "rgba(255,255,255,0.06)", groesse = 16 }) => (
  <AbsoluteFill
    style={{ backgroundImage: `radial-gradient(${farbe} 2.5px, transparent 3px)`, backgroundSize: `${groesse}px ${groesse}px` }}
  />
);

const Speedlines: React.FC<{ farbe: string }> = ({ farbe }) => {
  const frame = useCurrentFrame();
  return (
    <svg viewBox="-540 -960 1080 1920" style={{ position: "absolute", inset: 0 }}>
      {Array.from({ length: 56 }, (_, i) => {
        const a = (i / 56) * Math.PI * 2 + frame * 0.004;
        const w = 0.012 + ((i * 13) % 7) * 0.004;
        return (
          <polygon
            key={i}
            points={`0,0 ${Math.cos(a - w) * 2300},${Math.sin(a - w) * 2300} ${Math.cos(a + w) * 2300},${Math.sin(a + w) * 2300}`}
            fill={farbe}
          />
        );
      })}
    </svg>
  );
};

// Explosions-Stern hinter grossen Wörtern
const Stern: React.FC<{ farbe: string; r: number; zacken?: number }> = ({ farbe, r, zacken = 14 }) => {
  const frame = useCurrentFrame();
  const pts = Array.from({ length: zacken * 2 }, (_, i) => {
    const a = (i / (zacken * 2)) * Math.PI * 2 + frame * 0.01;
    const rr = i % 2 ? r * 0.62 : r * (0.95 + 0.08 * Math.sin(i * 3.1));
    return `${Math.cos(a) * rr},${Math.sin(a) * rr}`;
  }).join(" ");
  return (
    <svg viewBox={`${-r - 20} ${-r - 20} ${2 * r + 40} ${2 * r + 40}`} width={2 * r + 40} height={2 * r + 40}>
      <polygon points={pts} fill={farbe} stroke={TINTE} strokeWidth={12} strokeLinejoin="round" />
    </svg>
  );
};

// Comic-Panel: knallt rein, leicht schräg, wippt im Takt
const Panel: React.FC<{ bild: string; dreh: number; top?: number }> = ({ bild, dreh, top = 470 }) => {
  const frame = useCurrentFrame();
  const rein = useSp(0, 11);
  const takt = 1 + 0.018 * Math.exp(-((frame % SCHLAG) / 4));
  const zoom = interpolate(frame, [0, 144], [1.04, 1.16]);
  return (
    <div
      style={{
        position: "absolute",
        left: 80,
        top,
        width: 920,
        height: 920,
        background: CREME,
        border: `14px solid ${TINTE}`,
        boxShadow: `22px 22px 0 ${TINTE}`,
        overflow: "hidden",
        transform: `rotate(${dreh}deg) scale(${(0.4 + 0.6 * rein) * takt})`,
        opacity: rein,
      }}
    >
      <Img src={pt(bild)} style={{ width: "100%", height: "100%", transform: `scale(${zoom})` }} />
      <Raster farbe="rgba(0,0,0,0.10)" groesse={12} />
    </div>
  );
};

const Wort: React.FC<{ text: string; farbe: string; size: number; top: number; delay?: number; dreh?: number }> = ({
  text,
  farbe,
  size,
  top,
  delay = 0,
  dreh = -4,
}) => {
  const s = useSp(delay, 9);
  return (
    <div
      style={{
        position: "absolute",
        top,
        width: "100%",
        textAlign: "center",
        fontFamily: comic,
        fontSize: size,
        lineHeight: 1,
        color: farbe,
        WebkitTextStroke: `${Math.max(6, size / 18)}px ${TINTE}`,
        paintOrder: "stroke fill",
        textShadow: `8px 8px 0 ${TINTE}`,
        letterSpacing: 3,
        transform: `rotate(${dreh}deg) scale(${0.3 + 0.7 * s})`,
        opacity: Math.min(1, s * 1.5),
      }}
    >
      {text}
    </div>
  );
};

// Erklär-Kasten unten (wie Comic-Erzählbox)
const Box: React.FC<{ text: string; delay?: number; farbe?: string }> = ({ text, delay = 10, farbe = CREME }) => {
  const s = useSp(delay, 13);
  return (
    <div
      style={{
        position: "absolute",
        left: 90,
        right: 90,
        top: 1500,
        padding: "26px 34px",
        background: farbe,
        border: `10px solid ${TINTE}`,
        boxShadow: `14px 14px 0 ${TINTE}`,
        fontFamily: comic,
        fontSize: 78,
        letterSpacing: 2,
        color: TINTE,
        textAlign: "center",
        transform: `translateY(${(1 - s) * 260}px) rotate(1.5deg)`,
      }}
    >
      {text}
    </div>
  );
};

const Flash: React.FC<{ farbe?: string }> = ({ farbe = "white" }) => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{ background: farbe, opacity: interpolate(frame, [0, 7], [0.85, 0], clamp) }} />;
};

const Kapitel: React.FC<{
  bild: string;
  wort: string;
  wortFarbe: string;
  sternFarbe: string;
  box: string;
  grund: string;
  linien: string;
  dreh: number;
}> = ({ bild, wort, wortFarbe, sternFarbe, box, grund, linien, dreh }) => (
  <AbsoluteFill style={{ background: grund }}>
    <Speedlines farbe={linien} />
    <Raster />
    <Panel bild={bild} dreh={dreh} top={430} />
    <div style={{ position: "absolute", top: 70, width: "100%", display: "flex", justifyContent: "center" }}>
      <Stern farbe={sternFarbe} r={230} />
    </div>
    <Wort text={wort} farbe={wortFarbe} size={190} top={190} />
    <Box text={box} />
    <Flash />
  </AbsoluteFill>
);

export const PTPromo: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  // Wackeln beim Drop
  const wackel = frame >= 144 && frame < 160 ? Math.sin(frame * 2.7) * (160 - frame) * 1.8 : 0;
  const ende = interpolate(frame, [durationInFrames - 20, durationInFrames], [1, 0], clamp);

  return (
    <AbsoluteFill style={{ background: NACHT, transform: `translate(${wackel}px, ${wackel * 0.5}px)` }}>
      <AbsoluteFill style={{ opacity: ende }}>
        {/* Hook: 0 - 144 */}
        <Sequence from={0} durationInFrames={144}>
          <AbsoluteFill style={{ background: NACHT }}>
            <Raster />
            <Panel bild="hook.jpg" dreh={-2} top={520} />
            <Wort text="DU TRAINIERST HART." farbe={CREME} size={112} top={200} delay={4} dreh={-3} />
            <Wort text="UND TRITTST AN ORT?" farbe={ORANGE} size={112} top={1530} delay={TAKT} dreh={2} />
          </AbsoluteFill>
        </Sequence>

        <Sequence from={144} durationInFrames={TAKT * 2}>
          <Kapitel
            bild="training.jpg"
            wort="TRAINING"
            wortFarbe={CREME}
            sternFarbe={ORANGE}
            box="EIN PLAN, DER ZU DIR PASST."
            grund="#0f2b2a"
            linien="rgba(51,220,192,0.16)"
            dreh={2}
          />
        </Sequence>

        <Sequence from={288} durationInFrames={TAKT * 2}>
          <Kapitel
            bild="mindset.jpg"
            wort="MINDSET"
            wortFarbe={CREME}
            sternFarbe={PETROL}
            box="KLARER KOPF. KLARE ZIELE."
            grund="#2e1608"
            linien="rgba(255,138,42,0.18)"
            dreh={-2}
          />
        </Sequence>

        <Sequence from={432} durationInFrames={TAKT * 2}>
          <Kapitel
            bild="beratung.jpg"
            wort="BERATUNG"
            wortFarbe={CREME}
            sternFarbe={ORANGE}
            box="TECHNIK. AUFBAU. FORTSCHRITT."
            grund="#0f2b2a"
            linien="rgba(51,220,192,0.16)"
            dreh={2}
          />
        </Sequence>

        {/* Endkarte: 576 - Schluss */}
        <Sequence from={576}>
          <Endkarte />
        </Sequence>
      </AbsoluteFill>
      <Audio src={pt("beat.wav")} />
    </AbsoluteFill>
  );
};

const Endkarte: React.FC = () => {
  const frame = useCurrentFrame();
  const knopf = useSp(40, 10);
  const puls = 1 + 0.03 * Math.sin(frame / 5);
  return (
    <AbsoluteFill style={{ background: NACHT }}>
      <Speedlines farbe="rgba(255,138,42,0.10)" />
      <Raster />
      <div style={{ position: "absolute", top: 330, width: "100%", display: "flex", justifyContent: "center" }}>
        <Stern farbe={PETROL} r={330} zacken={16} />
      </div>
      <Wort text="NEXA" farbe={CREME} size={300} top={560} delay={0} dreh={-5} />
      <Wort text="PERSONAL TRAINING" farbe={ORANGE} size={96} top={1120} delay={12} dreh={0} />
      <Wort text="MINDSET · BERATUNG" farbe={PETROL} size={80} top={1235} delay={20} dreh={0} />
      <div
        style={{
          position: "absolute",
          top: 1440,
          left: 140,
          right: 140,
          padding: "30px 0",
          textAlign: "center",
          background: ORANGE,
          border: `10px solid ${TINTE}`,
          boxShadow: `14px 14px 0 ${TINTE}`,
          borderRadius: 24,
          fontFamily: comic,
          fontSize: 70,
          letterSpacing: 2,
          color: TINTE,
          transform: `scale(${knopf * puls})`,
        }}
      >
        ERSTGESPRÄCH ANFRAGEN
      </div>
      <Wort text="LINK IN BIO" farbe={CREME} size={60} top={1660} delay={55} dreh={0} />
      <Flash farbe={PETROL} />
    </AbsoluteFill>
  );
};

export const PTPromoComp = () => (
  <Composition id="PTPromo" component={PTPromo} durationInFrames={25 * FPS} fps={FPS} width={1080} height={1920} />
);
