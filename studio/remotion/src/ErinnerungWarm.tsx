import "@fontsource/cormorant-garamond/500-italic.css";
import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Wärmere, ruhigere Version des Erinnerungs-Videos.
// Bild: public/katzen.png, Hintergrund: public/katzen_bg.jpg
// Musik: public/trauerlied.wav (studio/musik/trauerlied.py)

export type WarmProps = { zeile1: string; zeile2: string };

const FPS = 30;
const DAUER = 61 * FPS;
const BILD = 1000;
const TOP = 400;
const LEAF =
  "M50 5 L58 28 L75 18 L70 40 L92 38 L78 55 L88 62 L62 66 L64 82 L52 72 L50 95 L48 72 L36 82 L38 66 L12 62 L22 55 L8 38 L30 40 L25 18 L42 28 Z";
const FARBEN = ["#e8571c", "#f28a1c", "#f5b324", "#d2401c", "#ffa733"];
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const Blatt: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const r = (k: string) => random(`w${k}-${i}`);
  const size = 34 + r("s") * 60;
  const speed = 1.0 + r("v") * 1.5;
  const y = ((frame * speed + r("o") * 2300) % 2300) - 180;
  const x = r("x") * 1080 + Math.sin(frame / (45 + r("p") * 35) + r("ph") * 6) * 90;
  const rot = frame * (r("r") - 0.5) * 1.8 + r("r0") * 360;
  const flip = Math.cos(frame / (28 + r("f") * 30));
  return (
    <svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `rotate(${rot}deg) scaleX(${flip})`,
        opacity: 0.85,
        filter: size > 75 ? "blur(2.5px)" : "drop-shadow(0 0 6px rgba(255,150,40,0.6))",
      }}
    >
      <path d={LEAF} fill={FARBEN[i % FARBEN.length]} />
      <path d="M50 30 L50 92" stroke="rgba(90,30,0,0.5)" strokeWidth={2} />
    </svg>
  );
};

// Warme Lichtkugeln (Bokeh), steigen langsam auf
const Bokeh: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const r = (k: string) => random(`b${k}-${i}`);
  const s = 40 + r("s") * 140;
  const y = 2000 - ((frame * (0.4 + r("v") * 0.8) + r("o") * 2200) % 2200);
  const x = r("x") * 1080 + Math.sin(frame / 90 + r("p") * 6) * 40;
  const glow = 0.25 + 0.2 * Math.sin(frame / (30 + r("t") * 40) + r("q") * 6);
  return (
    <div
      style={{
        position: "absolute",
        left: x - s / 2,
        top: y,
        width: s,
        height: s,
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(255,210,130,0.9) 0%, rgba(255,160,60,0.35) 45%, transparent 70%)",
        filter: "blur(6px)",
        opacity: glow,
        mixBlendMode: "screen",
      }}
    />
  );
};

const Funke: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const r = (k: string) => random(`wf${k}-${i}`);
  const x = 12 + r("x") * 76;
  const y = 4 + r("y") * 50;
  const tw = Math.max(0, Math.sin(frame / (16 + r("t") * 22) + r("p") * 6));
  const s = 4 + r("s") * 8;
  return (
    <div
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y - frame * 0.008}%`,
        width: s,
        height: s,
        borderRadius: "50%",
        background: "#fff2c4",
        boxShadow: `0 0 ${s * 2.5}px ${s}px rgba(255,190,80,0.85)`,
        opacity: tw * 0.9,
      }}
    />
  );
};

const Zeile: React.FC<{ text: string; von: number; bis: number; size: number }> = ({ text, von, bis, size }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [von * FPS, (von + 3) * FPS, bis * FPS - 60, bis * FPS], [0, 1, 1, 0], clamp);
  return (
    <div
      style={{
        position: "absolute",
        top: TOP + BILD + 110,
        width: "100%",
        padding: "0 70px",
        textAlign: "center",
        fontFamily: "Cormorant Garamond",
        fontStyle: "italic",
        fontWeight: 500,
        fontSize: size,
        lineHeight: 1.15,
        whiteSpace: "pre-line",
        color: "#ffe2a8",
        textShadow: "0 0 34px rgba(255,160,50,0.95), 0 2px 8px rgba(0,0,0,0.6)",
        opacity: o,
        transform: `translateY(${(1 - o) * 20}px)`,
      }}
    >
      {text}
    </div>
  );
};

export const ErinnerungWarm: React.FC<WarmProps> = ({ zeile1, zeile2 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames: D } = useVideoConfig();

  const zoom = interpolate(frame, [0, D], [1, 1.22]);
  const bgZoom = interpolate(frame, [0, D], [1.1, 1.3]);
  const halo = 0.5 + 0.3 * Math.sin(frame / 26);
  // Herzschlag der Pfote im Baum: doppelter Puls
  const beat = (frame % 48) / 48;
  const herz = 0.35 + 0.65 * (Math.exp(-((beat - 0.1) ** 2) / 0.002) + 0.7 * Math.exp(-((beat - 0.28) ** 2) / 0.002));
  const leak = interpolate(frame, [0, D], [-500, 1300]);
  const fade = interpolate(frame, [0, 75, D - 120, D - 10], [0, 1, 1, 0], clamp);
  const waerme = interpolate(frame, [0, D * 0.7, D], [0.18, 0.3, 0.38], clamp);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AbsoluteFill style={{ opacity: fade }}>
        <Img
          src={staticFile("katzen_bg.jpg")}
          style={{ position: "absolute", height: "100%", left: "50%", transform: `translateX(-50%) scale(${bgZoom})` }}
        />
        {Array.from({ length: 16 }, (_, i) => (
          <Bokeh key={i} i={i} />
        ))}

        <div
          style={{
            position: "absolute",
            left: (1080 - BILD) / 2,
            top: TOP,
            width: BILD,
            height: BILD,
            borderRadius: 40,
            overflow: "hidden",
            boxShadow: "0 0 120px 20px rgba(255,160,50,0.6)",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              transform: `scale(${zoom})`,
              transformOrigin: "54% 30%",
            }}
          >
            <Img src={staticFile("katzen.png")} style={{ width: "100%", height: "100%", filter: "saturate(1.08) sepia(0.12)" }} />
            <div
              style={{
                position: "absolute",
                left: "53.9%",
                top: "12.1%",
                width: 330,
                height: 170,
                transform: "translate(-50%, -50%)",
                borderRadius: "50%",
                background: "radial-gradient(ellipse, rgba(255,235,160,1) 0%, rgba(255,190,80,0.45) 40%, transparent 70%)",
                opacity: halo,
                mixBlendMode: "screen",
              }}
            />
            <div
              style={{
                position: "absolute",
                left: "11.4%",
                top: "21.5%",
                width: 210,
                height: 210,
                transform: `translate(-50%, -50%) scale(${0.9 + 0.12 * herz})`,
                borderRadius: "50%",
                background: "radial-gradient(circle, rgba(255,200,90,0.95) 0%, rgba(255,140,40,0.35) 45%, transparent 70%)",
                opacity: herz * 0.8,
                mixBlendMode: "screen",
              }}
            />
            {Array.from({ length: 40 }, (_, i) => (
              <Funke key={i} i={i} />
            ))}
          </div>
        </div>

        {/* Lichtschleier, der langsam durchs Bild wandert */}
        <div
          style={{
            position: "absolute",
            left: leak,
            top: 200,
            width: 700,
            height: 1500,
            background: "radial-gradient(ellipse, rgba(255,190,100,0.55) 0%, transparent 65%)",
            transform: "rotate(25deg)",
            mixBlendMode: "screen",
            filter: "blur(30px)",
          }}
        />

        {Array.from({ length: 26 }, (_, i) => (
          <Blatt key={i} i={i} />
        ))}

        {/* Warmer Farbfilter und Vignette */}
        <AbsoluteFill style={{ background: "rgba(255,140,40,1)", opacity: waerme * 0.35, mixBlendMode: "soft-light" }} />
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, transparent 45%, rgba(20,6,0,0.75) 100%)" }} />

        <Zeile text={zeile1} von={18} bis={34} size={74} />
        <Zeile text={zeile2} von={42} bis={62} size={108} />
      </AbsoluteFill>
      <Audio src={staticFile("trauerlied.wav")} />
    </AbsoluteFill>
  );
};

export const ErinnerungWarmComp = () => (
  <Composition
    id="ErinnerungWarm"
    component={ErinnerungWarm}
    durationInFrames={DAUER}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{ zeile1: "In jedem Herbst.\nIn jedem Sonnenstrahl.", zeile2: "Für immer bei uns." }}
  />
);
