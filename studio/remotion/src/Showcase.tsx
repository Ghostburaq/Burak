import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  Loop,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Showcase: KI-Zeichnung + Manim + Blender-3D + Remotion-Titel + eigene Musik.
// Assets in public/showcase/ (erzeugt mit studio/showcase/*.py und studio/bild/bild.py)
// Schnitte liegen auf den Takten der Musik (120 BPM, 1 Takt = 2 s = 60 Frames).

const FPS = 30;
const GELB = "#f5c400";
const GRUND = "#0b0f14";
const f = (p: string) => staticFile(`showcase/${p}`);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const Titel: React.FC<{ text: string; farbe?: string; size?: number; top: number; delay?: number }> = ({
  text,
  farbe = "white",
  size = 96,
  top,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 13 } });
  return (
    <div
      style={{
        position: "absolute",
        top,
        width: "100%",
        padding: "0 70px",
        textAlign: "center",
        fontFamily: "Inter, sans-serif",
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1.05,
        color: farbe,
        textTransform: "uppercase",
        letterSpacing: 2,
        WebkitTextStroke: farbe === "white" ? "3px black" : undefined,
        textShadow: "6px 6px 0 #000",
        transform: `scale(${0.6 + 0.4 * s}) rotate(${(1 - s) * -6}deg)`,
        opacity: s,
      }}
    >
      {text}
    </div>
  );
};

// Comic-Panel mit dicker Kontur, leicht schräg, Ken-Burns-Zoom
const Panel: React.FC<{ src: string; dreh: number }> = ({ src, dreh }) => {
  const frame = useCurrentFrame();
  const z = interpolate(frame, [0, 120], [1.05, 1.2]);
  const rein = interpolate(frame, [0, 10], [1.4, 1], clamp);
  return (
    <div
      style={{
        position: "absolute",
        left: 70,
        top: 520,
        width: 940,
        height: 940,
        border: "14px solid white",
        outline: "8px solid black",
        overflow: "hidden",
        transform: `rotate(${dreh}deg) scale(${rein})`,
        boxShadow: "18px 18px 0 #000",
      }}
    >
      <Img src={src} style={{ width: "100%", height: "100%", transform: `scale(${z})` }} />
    </div>
  );
};

// Speedlines im Manga-Stil (Strahlen aus der Mitte)
const Speedlines: React.FC<{ farbe?: string }> = ({ farbe = "rgba(245,196,0,0.18)" }) => {
  const frame = useCurrentFrame();
  const n = 48;
  return (
    <svg viewBox="-540 -960 1080 1920" style={{ position: "absolute", inset: 0 }}>
      {Array.from({ length: n }, (_, i) => {
        const a = (i / n) * Math.PI * 2 + frame * 0.01;
        const w = 0.02 + ((i * 7) % 5) * 0.006;
        return (
          <polygon
            key={i}
            points={`0,0 ${Math.cos(a - w) * 2200},${Math.sin(a - w) * 2200} ${Math.cos(a + w) * 2200},${Math.sin(a + w) * 2200}`}
            fill={farbe}
          />
        );
      })}
    </svg>
  );
};

const Blitz: React.FC = () => {
  // Weisser Flash auf dem Schnitt
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{ background: "white", opacity: interpolate(frame, [0, 6], [0.9, 0], clamp) }} />;
};

const Raster: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundImage: "radial-gradient(rgba(255,255,255,0.07) 2px, transparent 2.5px)",
      backgroundSize: "14px 14px",
    }}
  />
);

export const Showcase: React.FC = () => {
  const frame = useCurrentFrame();
  // Kamera-Wackeln beim Drop (8 s)
  const shake = frame >= 240 && frame < 252 ? Math.sin(frame * 3) * (252 - frame) * 1.6 : 0;
  const ende = interpolate(frame, [570, 600], [1, 0], clamp);

  return (
    <AbsoluteFill style={{ background: GRUND, transform: `translate(${shake}px, ${shake * 0.6}px)` }}>
      <AbsoluteFill style={{ opacity: ende }}>
        {/* 0-4 s: Manga-Zeichnung, Hook */}
        <Sequence from={0} durationInFrames={120}>
          <Raster />
          <Panel src={f("manga1.png")} dreh={-2} />
          <Titel text="Strom fällt aus." top={170} />
          <Titel text="Und dann?" farbe={GELB} top={1560} delay={30} />
        </Sequence>

        {/* 4-8 s: Manim, Netzqualität */}
        <Sequence from={120} durationInFrames={120}>
          <OffthreadVideo src={f("welle.mp4")} muted />
          <Blitz />
        </Sequence>

        {/* 8-12 s: Drop, 3D-Blitz aus Blender */}
        <Sequence from={240} durationInFrames={120}>
          <Speedlines />
          <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
            <div style={{ width: 1000, height: 1000 }}>
              <Loop durationInFrames={90}>
                <OffthreadVideo src={f("blitz.mp4")} muted style={{ width: "100%", height: "100%", mixBlendMode: "lighten" }} />
              </Loop>
            </div>
          </AbsoluteFill>
          <Titel text="Energie" top={220} size={150} farbe={GELB} />
          <Titel text="die liefert." top={1560} delay={20} />
          <Blitz />
        </Sequence>

        {/* 12-16 s: zweite Zeichnung mit Sprechblase */}
        <Sequence from={360} durationInFrames={120}>
          <Raster />
          <Panel src={f("manga2.png")} dreh={2} />
          <Sprechblase />
          <Blitz />
        </Sequence>

        {/* 16-20 s: Logo */}
        <Sequence from={480} durationInFrames={120}>
          <Speedlines farbe="rgba(245,196,0,0.08)" />
          <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
            <div style={{ width: 520, height: 520, marginTop: -420 }}>
              <OffthreadVideo src={f("blitz.mp4")} muted style={{ width: "100%", height: "100%", mixBlendMode: "lighten" }} />
            </div>
          </AbsoluteFill>
          <Titel text="NEXA" top={1000} size={230} farbe={GELB} />
          <Titel text="Strom. Technik. Klartext." top={1290} size={58} delay={20} />
          <Blitz />
        </Sequence>
      </AbsoluteFill>
      <Audio src={f("beat.wav")} />
    </AbsoluteFill>
  );
};

const Sprechblase: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - 12, fps, config: { damping: 10 } });
  return (
    <div
      style={{
        position: "absolute",
        left: 120,
        top: 180,
        transform: `scale(${s})`,
        transformOrigin: "30% 100%",
      }}
    >
      <div
        style={{
          background: "white",
          border: "8px solid black",
          borderRadius: "50%",
          padding: "70px 90px",
          fontFamily: "Inter, sans-serif",
          fontWeight: 900,
          fontSize: 78,
          color: "black",
          textAlign: "center",
          boxShadow: "12px 12px 0 #000",
        }}
      >
        Messen.
        <br />
        Nicht raten.
      </div>
      <svg width="140" height="150" style={{ position: "absolute", left: 300, top: "100%", marginTop: -14 }}>
        <polygon points="0,0 90,0 40,140" fill="white" stroke="black" strokeWidth="8" />
        <rect x="6" y="0" width="80" height="12" fill="white" />
      </svg>
    </div>
  );
};

export const ShowcaseComp = () => (
  <Composition id="Showcase" component={Showcase} durationInFrames={20 * FPS} fps={FPS} width={1080} height={1920} />
);
