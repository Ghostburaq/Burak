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

// Erinnerungs-Video: Bild + fallende Blätter + Lichtfunken + Musik.
// Bild:  public/katzen.png (quadratisch), Hintergrund: public/katzen_bg.jpg (vorgeblurrt)
// Musik: public/lied.wav  (erzeugt mit studio/musik/wiegenlied.py)

export type ErinnerungProps = { text: string };

const FPS = 30;
const DAUER = 44 * FPS;
const BILD = 1000;
const LEAF =
  "M50 5 L58 28 L75 18 L70 40 L92 38 L78 55 L88 62 L62 66 L64 82 L52 72 L50 95 L48 72 L36 82 L38 66 L12 62 L22 55 L8 38 L30 40 L25 18 L42 28 Z";
const FARBEN = ["#e8471c", "#f28a1c", "#f5b324", "#c4281c", "#ff9a2e"];

const Blatt: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const r = (k: string) => random(`${k}-${i}`);
  const size = 36 + r("s") * 64;
  const speed = 1.6 + r("v") * 2.2;
  const y = ((frame * speed + r("o") * 2300) % 2300) - 180;
  const x = r("x") * 1080 + Math.sin(frame / (35 + r("p") * 30) + r("ph") * 6) * 70;
  const rot = frame * (r("r") - 0.5) * 3 + r("r0") * 360;
  const flip = Math.cos(frame / (20 + r("f") * 25));
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
        opacity: 0.9,
        filter: size > 70 ? "blur(2px)" : undefined,
      }}
    >
      <path d={LEAF} fill={FARBEN[i % FARBEN.length]} />
      <path d="M50 30 L50 92" stroke="rgba(90,30,0,0.5)" strokeWidth={2} />
    </svg>
  );
};

const Funke: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const r = (k: string) => random(`f${k}-${i}`);
  // Funken um Heiligenschein und Flügel
  const x = 15 + r("x") * 70;
  const y = 5 + r("y") * 45;
  const tw = Math.max(0, Math.sin(frame / (12 + r("t") * 18) + r("p") * 6));
  const s = 4 + r("s") * 8;
  return (
    <div
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y - frame * 0.01}%`,
        width: s,
        height: s,
        borderRadius: "50%",
        background: "#fff2c4",
        boxShadow: `0 0 ${s * 2}px ${s}px rgba(255,200,90,0.8)`,
        opacity: tw * 0.9,
      }}
    />
  );
};

export const Erinnerung: React.FC<ErinnerungProps> = ({ text }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.16]);
  const bgZoom = interpolate(frame, [0, durationInFrames], [1.1, 1.25]);
  const halo = 0.45 + 0.3 * Math.sin(frame / 22);
  const rays = interpolate(Math.sin(frame / 60), [-1, 1], [0.08, 0.2]);
  const fade = interpolate(
    frame,
    [0, 45, durationInFrames - 75, durationInFrames - 5],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const textIn = interpolate(frame, [30 * FPS, 33 * FPS], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <AbsoluteFill style={{ opacity: fade }}>
        <Img
          src={staticFile("katzen_bg.jpg")}
          style={{
            position: "absolute",
            height: "100%",
            left: "50%",
            transform: `translateX(-50%) scale(${bgZoom})`,
          }}
        />

        {/* Lichtstrahlen */}
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(115deg, transparent 30%, rgba(255,200,110,1) 45%, transparent 60%)",
            opacity: rays,
            mixBlendMode: "screen",
          }}
        />

        {/* Hauptbild */}
        <div
          style={{
            position: "absolute",
            left: (1080 - BILD) / 2,
            top: 380,
            width: BILD,
            height: BILD,
            borderRadius: 36,
            overflow: "hidden",
            boxShadow: "0 0 90px 10px rgba(255,170,60,0.55)",
          }}
        >
          <div
            style={{
              width: "100%",
              height: "100%",
              position: "relative",
              transform: `scale(${zoom})`,
              transformOrigin: "54% 35%",
            }}
          >
            <Img
              src={staticFile("katzen.png")}
              style={{ width: "100%", height: "100%" }}
            />
            {/* Heiligenschein leuchtet */}
            <div
              style={{
                position: "absolute",
                left: "53.9%",
                top: "12.1%",
                width: 300,
                height: 150,
                transform: "translate(-50%, -50%)",
                borderRadius: "50%",
                background:
                  "radial-gradient(ellipse, rgba(255,230,150,0.95) 0%, rgba(255,190,80,0.4) 40%, transparent 70%)",
                opacity: halo,
                mixBlendMode: "screen",
              }}
            />
            {Array.from({ length: 34 }, (_, i) => (
              <Funke key={i} i={i} />
            ))}
          </div>
        </div>

        {Array.from({ length: 34 }, (_, i) => (
          <Blatt key={i} i={i} />
        ))}

        <div
          style={{
            position: "absolute",
            top: 1470,
            width: "100%",
            textAlign: "center",
            fontFamily: "Cormorant Garamond",
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 104,
            color: "#ffe0a0",
            textShadow: "0 0 30px rgba(255,170,60,0.9), 0 2px 6px rgba(0,0,0,0.6)",
            opacity: textIn,
            transform: `translateY(${(1 - textIn) * 25}px)`,
          }}
        >
          {text}
        </div>
      </AbsoluteFill>
      <Audio src={staticFile("lied.wav")} />
    </AbsoluteFill>
  );
};

export const ErinnerungComp = () => (
  <Composition
    id="Erinnerung"
    component={Erinnerung}
    durationInFrames={DAUER}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{ text: "Für immer bei uns." }}
  />
);
