import { Easing, Interactive, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Headline } from "../elements/Headline";
import { Waveform } from "../elements/Waveform";
import { colors, monoFont } from "../theme";

const MultimeterSceneInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      <Headline
        name="Frage"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 260,
          fontSize: 84,
          opacity: interpolate(frame, [0, 0.3 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Das Multimeter sagt:
      </Headline>
      <div
        style={{
          position: "absolute",
          left: 80,
          top: 400,
          fontFamily: monoFont,
          fontWeight: 700,
          fontSize: 260,
          color: colors.accent,
          scale: interpolate(frame, [0.3 * fps, 0.8 * fps], [0.8, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.spring({ damping: 200 }),
            output: "perceptual-scale",
          }),
          transformOrigin: "left center",
          opacity: interpolate(frame, [0.3 * fps, 0.6 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        230 V
      </div>
      <Waveform
        name="Verzerrte Kurve"
        color={colors.warn}
        harmonics={0.35}
        dipDepth={1}
        dipStart={100}
        dipLength={5}
        cyclesPerFrame={0.04}
        style={{
          position: "absolute",
          left: 80,
          top: 820,
          opacity: interpolate(frame, [2 * fps, 2.4 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
      <Headline
        name="Erklaerung"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 1340,
          fontSize: 64,
          fontWeight: 500,
          color: colors.fg,
          opacity: interpolate(frame, [2.6 * fps, 3 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Der Effektivwert stimmt. Die Kurve dahinter siehst du nicht.
      </Headline>
    </>
  );
};

export const MultimeterScene = Interactive.create({
  Component: MultimeterSceneInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
