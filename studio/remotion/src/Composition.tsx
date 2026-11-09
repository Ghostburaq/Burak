import {
  AbsoluteFill,
  Composition,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// NEXA Hook-Clip: Hochformat 1080x1920 fuer TikTok, Reels, Shorts.
// Texte per --props aendern, z.B.:
// npx remotion render NexaHook out/hook.mp4 --props='{"hook":"...","sub":"..."}'

export type HookProps = {
  hook: string;
  sub: string;
  bg: string;
  accent: string;
};

export const defaultHook: HookProps = {
  hook: "Hier steht dein Hook in einer Zeile.",
  sub: "Und hier die Auflösung.",
  bg: "#0b0f14",
  accent: "#f5c400",
};

export const NexaHook: React.FC<HookProps> = ({ hook, sub, bg, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({ frame, fps, config: { damping: 12 } });
  const subIn = interpolate(frame, [20, 35], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const bar = interpolate(frame, [0, 25], [0, 100], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: bg,
        justifyContent: "center",
        padding: 90,
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <div
        style={{
          width: `${bar}%`,
          height: 14,
          backgroundColor: accent,
          marginBottom: 50,
        }}
      />
      <div
        style={{
          color: "white",
          fontSize: 104,
          fontWeight: 800,
          lineHeight: 1.1,
          transform: `scale(${0.8 + 0.2 * pop})`,
          transformOrigin: "left center",
          opacity: pop,
        }}
      >
        {hook}
      </div>
      <div
        style={{
          color: accent,
          fontSize: 60,
          fontWeight: 600,
          marginTop: 50,
          opacity: subIn,
          transform: `translateY(${(1 - subIn) * 30}px)`,
        }}
      >
        {sub}
      </div>
    </AbsoluteFill>
  );
};

export const MyComposition = () => {
  return (
    <Composition
      id="NexaHook"
      component={NexaHook}
      durationInFrames={90}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={defaultHook}
    />
  );
};
