import { Easing, Interactive, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Headline } from "../elements/Headline";
import { Waveform } from "../elements/Waveform";
import { colors } from "../theme";

const HookSceneInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      <Waveform
        name="Sinus"
        color={colors.accent}
        harmonics={0}
        dipDepth={1}
        dipStart={100}
        dipLength={5}
        cyclesPerFrame={0.04}
        style={{
          position: "absolute",
          left: 80,
          top: 1180,
          opacity: interpolate(frame, [0, 0.4 * fps], [0, 0.5], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
      <Headline
        name="Hook 1"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 520,
          fontSize: 130,
          opacity: interpolate(frame, [0, 0.25 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [0, 0.4 * fps], ["0px 40px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Strom ist da.
      </Headline>
      <Headline
        name="Hook 2"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 720,
          fontSize: 110,
          color: colors.alert,
          opacity: interpolate(frame, [1.1 * fps, 1.35 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [1.1 * fps, 1.5 * fps], ["0px 40px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        Die Anlage fällt trotzdem aus.
      </Headline>
    </>
  );
};

export const HookScene = Interactive.create({
  Component: HookSceneInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
