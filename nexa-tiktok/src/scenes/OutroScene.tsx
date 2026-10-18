import { Interactive, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Headline } from "../elements/Headline";
import { colors, headFont } from "../theme";

const OutroSceneInner = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      <Headline
        name="Frage an Community"
        style={{
          position: "absolute",
          left: 80,
          right: 160,
          top: 560,
          fontSize: 96,
          opacity: interpolate(frame, [0, 0.3 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Was hat bei dir schon mal ohne Grund ausgelöst?
      </Headline>
      <div
        style={{
          position: "absolute",
          left: 80,
          top: 1120,
          fontFamily: headFont,
          fontWeight: 700,
          fontSize: 140,
          letterSpacing: "0.12em",
          color: colors.accent,
          opacity: interpolate(frame, [1 * fps, 1.4 * fps], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        NEXA
      </div>
    </>
  );
};

export const OutroScene = Interactive.create({
  Component: OutroSceneInner,
  layout: "absolute-fill",
  schema: { ...Interactive.backgroundSchema },
});
