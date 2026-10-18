import { Easing, Interactive, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Headline } from "../elements/Headline";
import { Waveform } from "../elements/Waveform";
import { colors, monoFont } from "../theme";

const DipSceneInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      <Headline
        name="Titel"
        style={{ position: "absolute", left: 80, right: 160, top: 240, fontSize: 104, color: colors.alert }}
      >
        Spannungseinbruch
      </Headline>
      {/* 5 Perioden bei 50 Hz = 100 ms auf 30 % Restspannung */}
      <Waveform
        name="Einbruch laeuft durch"
        color={colors.accent}
        harmonics={0}
        dipDepth={0.3}
        dipStart={6}
        dipLength={5}
        cyclesPerFrame={0.06}
        style={{ position: "absolute", left: 80, top: 420 }}
      />
      <div
        style={{
          position: "absolute",
          left: 80,
          top: 900,
          fontFamily: monoFont,
          fontWeight: 700,
          fontSize: 180,
          color: colors.fg,
          opacity: interpolate(frame, [1.2 * fps, 1.5 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          scale: interpolate(frame, [1.2 * fps, 1.7 * fps], [0.85, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.spring({ damping: 200 }),
            output: "perceptual-scale",
          }),
          transformOrigin: "left center",
        }}
      >
        100 ms
      </div>
      <Headline
        name="Wirkung"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 1140,
          fontSize: 64,
          fontWeight: 500,
          opacity: interpolate(frame, [2 * fps, 2.4 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Das Licht zuckt kaum. Eine SPS oder ein Umrichter kann trotzdem aussteigen.
      </Headline>
      <Headline
        name="Norm"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 1440,
          fontSize: 72,
          color: colors.warn,
          opacity: interpolate(frame, [4 * fps, 4.4 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        EN 50160 begrenzt Einbrüche nicht. Sie zählt sie nur.
      </Headline>
    </>
  );
};

export const DipScene = Interactive.create({
  Component: DipSceneInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
